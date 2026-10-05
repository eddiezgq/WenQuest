"""7.3 节的计算：

算例 7.3.1  AGV 过弯：弯道半径 R = 1.20 m。三个限制——轮胎与地面不打滑（μ_s = 0.60）；货箱在车板上不滑（μ_s = 0.30）；
            高货箱不倾倒（重心高 h = 0.80 m，底面半宽 b = 0.20 m，要求 a_n ≤ gb/h，第 14 章）。求各自允许的最大速率，
            取最小者（图 7.3.1）。
算例 7.3.2  SCARA 机器人夹着 0.80 kg 的零件，末端离转轴 0.40 m，以 3.0 rad/s 匀速转动：零件做圆周运动所需的向心力多大，
            由谁提供？与夹住它所需的竖直摩擦力比较。两指沿切向夹紧、μ_s = 0.50 时，每指至少要多大的夹紧力？
生活中的例子  公路弯道的超高（横向坡度）：半径 300 m、横坡 6% 的弯道，不靠侧向摩擦时的“设计速度”。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 7.3.1
R = 1.20
lim = {"tyre": 0.60 * g, "cargo": 0.30 * g, "tip": g * 0.20 / 0.80}
vmax = {k: math.sqrt(a * R) for k, a in lim.items()}
k_min = min(vmax, key=vmax.get)
out(R=R, a_tyre=lim["tyre"], a_cargo=lim["cargo"], a_tip=lim["tip"], v_tyre=vmax["tyre"], v_cargo=vmax["cargo"], v_tip=vmax["tip"],
    v_ok=vmax[k_min])

# ---- 算例 7.3.2
m, w, rr = 0.80, 3.0, 0.40
Fc = m * w * w * rr
mu2 = 0.50
out(m=m, w=w, rr=rr, Fc=Fc, Fg=m * g, ratio=Fc / (m * g), mu2=mu2, FN_rot=math.hypot(m * g, Fc) / (2 * mu2), FN_still=m * g / (2 * mu2),
    w_rpm=w * 60 / (2 * math.pi))

# ---- 生活中的例子：超高
Rr, e = 300.0, 0.06
th = math.atan(e)
vdes = math.sqrt(g * Rr * math.tan(th))
out(Rr=Rr, e_pct=100 * e, vdes=vdes, vdes_kmh=3.6 * vdes)

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.2))
Rs = np.linspace(0.3, 4.0, 300)
for k, col, name in (("tyre", d.MUTED, T(r"轮胎不打滑（$\mu_\mathrm{s}$ = 0.60）", r"tyres grip ($\mu_\mathrm{s}$ = 0.60)")),
                     ("cargo", d.VA, T(r"货箱不滑（$\mu_\mathrm{s}$ = 0.30）", r"cargo does not slide ($\mu_\mathrm{s}$ = 0.30)")),
                     ("tip", d.VR, T(r"高货箱不倒（$gb/h$）", r"tall cargo does not tip ($gb/h$)"))):
    ax.plot(Rs, np.sqrt(lim[k] * Rs), color=col, lw=2, label=name)
ax.axvline(R, color=d.INK, lw=0.8, ls=":"); ax.text(R + 0.05, 0.25, f"R = {R:.1f} m", fontsize=8.5)
ax.set_xlabel(T("弯道半径 R / m", "bend radius R / m")); ax.set_ylabel(T("允许的最大速率 / (m/s)", "maximum speed / (m/s)"))
ax.set_ylim(0, 5); ax.legend(frameon=False, fontsize=8.5, loc="upper left"); d.spines(ax)
figure(fig, "fig7_3_1")
