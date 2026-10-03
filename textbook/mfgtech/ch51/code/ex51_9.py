"""51.9 节：定位误差的仿真核对——蒙特卡罗抽样一批工件的直径，求 V 形块上工序基准的位置分散，与公式比较（图 51.9.1）；
心轴间隙定位：孔、轴尺寸和接触方向都随机时，孔心位移的最大值与 X_max 比较。"""
import math
import random

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

TL = M.tol()
p = M.plan()
fin = next(f for f in M.op(p, 40)["features"] if f["name"] == "齿轮位")
d0, es, ei = fin["size_mm"], fin["es_mm"], fin["ei_mm"]
Td = es - ei
mc = {m: TL.v_block_mc(d0, es, ei, 90, m, n=50_000) for m in ("center", "top", "bottom")}   # 按接触几何逐件求位置，不用公式
fm = {m: TL.v_block(Td, 90, m) for m in ("center", "top", "bottom")}
err = max(abs(mc[m] - fm[m]) / fm[m] for m in mc)
rng = random.Random(3)
hole, pin = (35, 0.025, 0.0), (35, -0.009, -0.025)
pts = []
for _ in range(20_000):
    D = rng.uniform(hole[0] + hole[2], hole[0] + hole[1])
    dd = rng.uniform(pin[0] + pin[2], pin[0] + pin[1])
    th = rng.uniform(0, 2 * math.pi)
    r = (D - dd) / 2                                # 孔靠在销上：孔心偏离销心 (D − d)/2，方向任意
    pts.append((r * math.cos(th), r * math.sin(th)))
span = max(x for x, _ in pts) - min(x for x, _ in pts)
Xmax = TL.pin_clearance(hole, pin, "any")
# 接触几何仿真（tolerance.v_block_contact）：公式反映不了的两种情况
# (1) V 形块一个工作面磨损 0.01 mm：轴心水平偏移，键槽对称度直接受影响
wear = 0.01
cx_w, _ = TL.v_block_contact(None, 90, wear_left=wear, radius=d0 / 2)
sym_wear = TL.offset_to_zone(abs(cx_w))
# (2) 定位外圆有三棱形圆度误差 0.01 mm（等直径多棱圆，两点法量直径看不出），转角随机
lobe_bottom = TL.v_block_mc(d0, es, ei, 90, "bottom", n=2000, lobes=3, roundness=0.01)
out(wear=wear, cx_w=abs(cx_w), sym_wear=sym_wear, lobe_bottom=lobe_bottom, lobe_ratio=lobe_bottom / fm["bottom"])
out(mc_center=mc["center"], mc_bottom=mc["bottom"], f_center=fm["center"], f_bottom=fm["bottom"], err_pct=100 * err,
    span=span, Xmax=Xmax, span_ratio=span / Xmax)

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.8))
s = math.sin(math.pi / 4)
d = np.random.default_rng(1).uniform(d0 + ei, d0 + es, 20_000)
for m, col, lab in (("center", M.ACCENT, T("轴心", "axis")), ("bottom", M.RED, T("下母线", "bottom generatrix"))):
    y = (d / 2) / s + (0 if m == "center" else -d / 2)
    axs[0].hist((y - y.mean()) * 1000, bins=60, color=col, alpha=0.55, label=lab)
axs[0].set_xlabel(T("工序基准的位置变动 / µm", "position of the operation datum / µm"), fontsize=8.5)
axs[0].legend(fontsize=8, frameon=False)
axs[0].set_yticks([])
xs, ys = zip(*pts)
axs[1].plot(np.array(xs) * 1000, np.array(ys) * 1000, ".", ms=1, color=M.ACCENT, alpha=0.4)
axs[1].set_aspect("equal")
axs[1].set_xlabel(T("孔心相对心轴中心 / µm", "bore centre relative to mandrel / µm"), fontsize=8.5)
for ax in axs:
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
figure(fig, "fig51_9_1")
