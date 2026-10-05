"""52.10 节：算例 52.10.1——V 形块磨损多少就该换？由接触几何（第 51 章 v_block_contact）求一个工作面磨损与键槽对称度的关系，
结合仿真车间的对称度分布（sim/errors.py），定出更换界限和检查周期；并说明问题情景“键槽夹具定位元件磨损”相当于磨损多少；画图 52.10.3。"""
import math
import sys

import _mfg as M
import numpy as np

from bookout import T, figure, out, style

TL = M.tol()
sys.path.insert(0, str(M.REPO / "factory" / "digital"))
from sim import errors as SE  # noqa: E402

# 一个工作面磨损 w：轴心水平偏移 cx(w)，对称度公差带占用 2·cx
w0 = 0.01
cx, _ = TL.v_block_contact(None, 90, wear_left=w0, radius=40.3 / 2)
k = TL.offset_to_zone(abs(cx)) / w0                     # 每 1 mm 磨损占用的对称度
# 仿真车间里正常的对称度：均值 0.006、标准差 0.002（sim/errors.py 的模型参数，代表对刀、铣刀偏摆等其他误差）
src = (M.REPO / "factory" / "digital" / "sim" / "errors.py").read_text(encoding="utf-8")
assert "sym_mean, sym_sd = 0.006, 0.002" in src
mu, sd, T_sym = 0.006, 0.002, 0.02
w_limit = (T_sym - (mu + 3 * sd)) / k                   # 均值 + 3σ 碰到公差时的磨损量
cpk_new = (T_sym - mu) / (3 * sd)                        # 对称度只有上限
# 问题情景注入的对称度均值增量相当于多大磨损
inj = SE.PROBLEMS["locator_worn"]["default"]
w_inj = inj / k
# 磨损速度（教学假设）：20Cr 渗碳淬火的 V 形块，每装卸 1000 件磨损约 0.5 µm
rate = 0.0005 / 1000
life = w_limit / rate
check_every = 500

# 图 52.10.3：(a) 一个工作面磨损后轴心的偏移（磨损放大画出）；(b) 磨损随装卸件数增加，对称度的均值 + 3σ 碰到公差时更换
plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.9), gridspec_kw={"width_ratios": [1, 1.5]})
r = 40.3 / 2
wv = 2.0                                                  # 示意：磨损放大到 2 mm
s45 = math.sin(math.pi / 4)
zc0 = r / s45
a1.plot([0, 30], [0, 30], color=M.INK, lw=1.0)
# 左工作面后退 wv（沿法向），新面：平行于原面
nx, nz = -s45, -s45                                        # 左面磨损后沿外法向（离开轴心）后退
a1.plot([-30 + wv * nx, 0 + wv * nx], [30 + wv * nz, 0 + wv * nz], color="#c0504d", lw=1.2)
a1.plot([-30, 0], [30, 0], color=M.INK, lw=0.6, ls=":")
cx_v, cz_v = TL.v_block_contact(None, 90, wear_left=wv, radius=r)
c0 = plt.Circle((0, zc0), r, fc="none", ec=M.MUTED, lw=0.8, ls="--")
c1 = plt.Circle((cx_v, cz_v), r, fc="none", ec=M.INK, lw=1.0)
a1.add_patch(c0); a1.add_patch(c1)
a1.plot([0], [zc0], "+", color=M.MUTED); a1.plot([cx_v], [cz_v], "+", color=M.INK)
a1.annotate("", xy=(cx_v, zc0 + 8), xytext=(0, zc0 + 8), arrowprops=dict(arrowstyle="->", lw=0.8))
a1.text(cx_v / 2, zc0 + 10, T(f"偏移 {abs(cx_v):.2f}", f"shift {abs(cx_v):.2f}"), ha="center", fontsize=7.5)
a1.text(-34, 4, T(f"左面磨损 {wv:g}\n（放大画出）", f"left face worn {wv:g}\n(exaggerated)"), fontsize=7.5, color="#c0504d")
a1.set_aspect("equal"); a1.axis("off")
a1.set_title(T("(a) 轴心向磨损的一侧偏移", "(a) the axis moves toward the worn face"), fontsize=8.5)
n = np.linspace(0, 1.25 * life, 400)
mean = mu + k * rate * n
a2.fill_between(n / 1000, (mean - 3 * sd) * 1000, (mean + 3 * sd) * 1000, color="#4f7fb8", alpha=0.18, lw=0)
a2.plot(n / 1000, mean * 1000, color="#4f7fb8", lw=1.2, label=T("均值", "mean"))
a2.plot(n / 1000, (mean + 3 * sd) * 1000, color="#4f7fb8", lw=0.8, ls="--", label=T("均值 + 3σ", "mean + 3σ"))
a2.axhline(T_sym * 1000, color="#c0504d", lw=1.0)
a2.text(1.25 * life / 1000 * 0.98, T_sym * 1000 + 0.5, ha="right", s= T("公差 0.020", "tolerance 0.020"), color="#c0504d", fontsize=7.5)
a2.axvline(life / 1000, color=M.INK, lw=0.8, ls=":")
a2.text(life / 1000, 4, T(f" 更换（约 {life / 1000:.0f} 千件）", f" replace (≈{life / 1000:.0f}k parts)"), fontsize=7.5)
for c in np.arange(check_every, 1.25 * life, check_every):
    a2.plot([c / 1000], [3.0], "|", color=M.MUTED, ms=4)
a2.text(0.2, 1.6, T(f"每 {check_every} 件检验棒检查一次", f"check with the test bar every {check_every} parts"), fontsize=7, color=M.MUTED)
a2.set_xlabel(T("装卸件数 / 千件", "parts loaded / thousand"), fontsize=8)
a2.set_ylabel(T("键槽对称度 / µm", "keyway symmetry / µm"), fontsize=8)
a2.set_ylim(0, 24); a2.set_xlim(0, 1.25 * life / 1000)
a2.legend(fontsize=7, loc="upper left", frameon=False, bbox_to_anchor=(0.0, 0.8))
a2.set_title(T("(b) 磨损使对称度均值逐渐上移", "(b) wear drifts the symmetry upward"), fontsize=8.5)
fig.tight_layout()
figure(fig, "fig52_10_3")

out(w0=w0, cx=abs(cx), k=k, mu=mu, sd=sd, w_limit=w_limit, w_limit_um=w_limit * 1000, cpk_new=cpk_new, inj=inj, w_inj=w_inj * 1000,
    rate_um=rate * 1000 * 1000, life=life, check_every=check_every, checks=life / check_every)
