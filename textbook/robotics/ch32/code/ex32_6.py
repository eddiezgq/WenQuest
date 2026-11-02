"""32.6 节的计算：背隙、刚度与效率。

(1) 算例 32.6.1：每个关节的背隙让 TCP 走多远：手臂水平伸直、工具朝下，关节 j 转一个小角度 δ，TCP 移动 |z_j × (p − o_j)|·δ；
    背隙取机器人厂关节测试台的名义值（清单 factory/plants/wenquest-robot.yaml 的 joint_backlash）。最坏（全部同向）与均方根。
(2) 算例 32.6.2：重力预紧：负载跑合台的标准动作里，各关节的力矩改变方向几次（第 29 章的逆动力学）；J1 的轴竖直，重力帮不上忙。
(3) 算例 32.6.3：关节测试台的背隙散布：名义值、标准差、上限取清单；错误注入“谐波减速器来料批次背隙偏大”在背隙上加的量取
    仿真车间 factory/digital/sim/errors.py；各抽 2000 台，超上限的比例。图 32.6.1。
(4) 拖动示教：用手推 TCP 让关节转动，要克服关节的空载摩擦力矩（清单 joint_friction 的名义值）：TCP 处的力 = 摩擦力矩 / 力臂。
"""
import math

import numpy as np
import yaml

from _ch32 import ARCMIN, DIGITAL, ROOT, runin_series, wqcr5
from bookout import COLORS as C, T, figure, out, style

W = wqcr5()
P = yaml.safe_load((ROOT / "factory" / "plants" / "wenquest-robot.yaml").read_text(encoding="utf-8"))
chars = {m["item"]: {c["code"]: c for c in m["chars"]} for m in P["measurements"]}
mod_item = {"L": "WQJ-L", "M": "WQJ-M", "S": "WQJ-S"}
# ---------------------------------------------------------------- (1) 背隙 → TCP
q = np.radians(W.OUTSTRETCHED_DEG)
Tw = W.link_world(q)
p = (Tw[5] @ np.append(W.tcp_local(), 1.0))[:3]
lever = np.array([np.linalg.norm(np.cross(Tw[j][:3, 2], p - Tw[j][:3, 3])) for j in range(6)])
bl = np.array([chars[mod_item[s]]["joint_backlash"]["nominal"] for s in W.JOINT_MODULE])
dx = bl * ARCMIN * lever * 1000
rep = chars["WQ-CR5"]["cr_repeat"]["hi"]
out(**{f"lev{j + 1}": lever[j] for j in range(6)}, **{f"bl{j + 1}": bl[j] for j in range(6)}, **{f"dx{j + 1}": dx[j] for j in range(6)},
    dx_sum=dx.sum(), dx_rss=math.sqrt((dx ** 2).sum()), rep=rep, sum_ratio=dx.sum() / rep)
assert dx.sum() > 3 * rep

# ---------------------------------------------------------------- (2) 力矩换向
t, tau, qd = runin_series(5.0)
flips = []
for j in range(6):
    s = np.sign(tau[:, j])
    s = s[np.abs(tau[:, j]) > 0.05 * np.abs(tau[:, j]).max()]
    flips.append(int(np.sum(s[1:] != s[:-1])))
out(**{f"flip{j + 1}": flips[j] for j in range(6)})
assert flips[1] == 0 and flips[0] > 0                        # J2 一直被重力压向一边；J1 每次起停都换向

# ---------------------------------------------------------------- (3) 测试台的散布
import sys  # noqa: E402
sys.path.insert(0, str(DIGITAL))
from sim import errors as ER  # noqa: E402
shift = ER.PROBLEMS["hd_lot"]["default"]
c = chars["WQJ-L"]["joint_backlash"]
rng = np.random.default_rng(32)
good = rng.normal(c["nominal"], c["sigma"], 2000)
bad = rng.normal(c["nominal"] + shift, c["sigma"], 2000)
out(bl_nom=c["nominal"], bl_sig=c["sigma"], bl_hi=c["hi"], shift=shift, rej_good=float(np.mean(good > c["hi"]) * 100),
    rej_bad=float(np.mean(bad > c["hi"]) * 100), z_good=(c["hi"] - c["nominal"]) / c["sigma"])
assert np.mean(good > c["hi"]) < 0.001 < 0.3 < np.mean(bad > c["hi"])

# ---------------------------------------------------------------- (4) 拖动示教
fr = np.array([chars[mod_item[s]]["joint_friction"]["nominal"] for s in W.JOINT_MODULE])
push = fr / lever
out(**{f"fr{j + 1}": fr[j] for j in range(3)}, **{f"push{j + 1}": push[j] for j in range(3)})

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(11.6, 3.9))
ax = axs[0]
bins = np.linspace(0.3, 1.4, 45)
ax.hist(good, bins=bins, color=C["z"], alpha=0.7, label=T("正常批次", "normal lots"))
ax.hist(bad, bins=bins, color=C["x"], alpha=0.6, label=T(f"背隙偏大的批次（+{shift:.2f}′）", f"bad lot (+{shift:.2f}′)"))
ax.axvline(c["hi"], color=C["ink"], lw=1.2, ls="--")
ax.set_xlabel(T("关节测试台测得的背隙 / 角分（大模组）", "backlash on the joint test bench / arcmin (large module)"))
ax.set_ylabel(T("台数（各抽 2000 台）", "count (2000 of each)"))
ax.text(c["hi"] + 0.02, ax.get_ylim()[1] * 0.92, T("上限 1.0′", "limit 1.0′"), fontsize=8)
ax.legend(fontsize=8, frameon=False, loc="upper left")
ax.set_title(T("(a) 测试台上的背隙散布", "(a) backlash on the test bench"), fontsize=11)
ax = axs[1]
ax.bar(np.arange(6), dx, color=[C["x"], C["x"], "#ff9896", C["z"], C["z"], C["z"]])
ax.axhline(rep, color=C["ink"], lw=1, ls="--")
ax.text(5.4, dx.max() * 0.97, T("虚线：重复定位精度 ±0.03 mm", "dashed: repeatability ±0.03 mm"), fontsize=8, ha="right")
ax.set_xticks(np.arange(6), [f"J{j + 1}\n{bl[j]:.1f}′" for j in range(6)])
ax.set_ylabel(T("背隙让 TCP 走的距离 / mm", "TCP play from backlash / mm"))
ax.set_title(T("(b) 每个关节的背隙乘力臂（伸直、工具朝下）", "(b) each joint's backlash times its lever (outstretched)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig32_6_1")
