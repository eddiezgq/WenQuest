"""10.4 节的计算：

算例 10.4.1  过山车的竖直圆环：车（看成质点，500 kg）从高 h 处由静止滑下，进入半径 R = 6.0 m 的圆环，不计摩擦。
            要通过环顶，h 至少多高？h = 18 m 时，环顶的速度和乘客受的支持力（以 mg 计），环底呢？
            沿轨道画出动能、势能和机械能（图 10.4.1）。
算例 10.4.2  弹跳机器人：质量 1.0 kg，腿里的弹簧 k = 2400 N/m，压缩 80 mm 后释放，竖直起跳。
            不计损耗，能跳多高（从起跳时腿伸直的位置量起）？弹簧的能量只有 70% 变成机械能时呢？
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 10.4.1
mc, R, h = 500.0, 6.0, 18.0
h_min = 2.5 * R
v_top = math.sqrt(2 * g * (h - 2 * R))
N_top = mc * (v_top ** 2 / R - g)
v_bot = math.sqrt(2 * g * h)
N_bot = mc * (g + v_bot ** 2 / R)
assert abs(math.sqrt(2 * g * (h_min - 2 * R)) - math.sqrt(g * R)) < 1e-12
out(mc=mc, R=R, h=h, h_min=h_min, v_top=v_top, N_top_g=N_top / (mc * g), v_bot=v_bot, N_bot_g=N_bot / (mc * g),
    v_top_min=math.sqrt(g * R), N_bot_hmin_g=1 + 2 * h_min / R)

# ---- 算例 10.4.2
mr, k, x = 1.0, 2400.0, 0.080
Es = 0.5 * k * x * x
H_ideal = Es / (mr * g) - x
H_70 = 0.7 * Es / (mr * g) - x
v_take = math.sqrt(2 * (Es - mr * g * x) / mr)
out(mr=mr, k=k, x_mm=x * 1000, Es=Es, H_ideal=H_ideal, H_70=H_70, v_take=v_take)

# ---- 图 10.4.1：轨道与能量
L = 30.0
segs = []
xs = np.linspace(0, L, 400); segs.append(np.c_[xs, h / 2 * (1 + np.cos(math.pi * xs / L))])
segs.append(np.c_[np.linspace(L, L + 6, 60), np.zeros(60)])
th = np.linspace(-math.pi / 2, 1.5 * math.pi, 600); segs.append(np.c_[L + 6 + R * np.cos(th), R + R * np.sin(th)])
segs.append(np.c_[np.linspace(L + 6, L + 16, 80), np.zeros(80)])
P = np.vstack(segs)
s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
Ug = mc * g * P[:, 1] / 1000
K = mc * g * (h - P[:, 1]) / 1000
plt = style()
fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.4, 4.6), gridspec_kw={"height_ratios": [1.1, 1]})
a1.plot(P[:, 0], P[:, 1], color=d.INK, lw=2)
a1.axhline(h, color=d.MUTED, lw=0.7, ls="--"); a1.text(1, h + 0.6, T(f"出发高度 h = {h:.0f} m", f"start height h = {h:.0f} m"), fontsize=8.5, color=d.MUTED)
a1.axhline(2 * R, color=d.MUTED, lw=0.5, ls=":")
a1.plot(0, h, "o", color=d.VR, ms=7)
a1.plot(L + 6, 2 * R, "o", color=d.VA, ms=6); a1.text(L + 6, 2 * R + 1.0, T("环顶", "top of loop"), fontsize=8.5, ha="center", color=d.VA)
a1.plot(L + 6, 0, "o", color=d.VA, ms=6); a1.text(L + 3.2, -2.2, T("环底", "bottom"), fontsize=8.5, color=d.VA)
a1.set_aspect("equal"); a1.set_xlim(-1, L + 17); a1.set_ylim(-3, h + 3); a1.set_xlabel("x / m"); a1.set_ylabel("y / m"); d.spines(a1)
a2.fill_between(s, 0, Ug, color=d.VA, alpha=0.35, lw=0, label=T("势能 mgy", "potential energy mgy"))
a2.fill_between(s, Ug, Ug + K, color=d.VR, alpha=0.3, lw=0, label=T("动能 ½mv²", "kinetic energy ½mv²"))
a2.plot(s, Ug + K, color=d.INK, lw=1.6, label=T("机械能（不变）", "mechanical energy (constant)"))
a2.set_xlabel(T("沿轨道走过的路程 / m", "distance along the track / m")); a2.set_ylabel(T("能量 / kJ", "energy / kJ"))
a2.set_xlim(0, s[-1]); a2.set_ylim(0, mc * g * h / 1000 * 1.25); a2.legend(frameon=False, fontsize=8, loc="upper right", ncol=3); d.spines(a2)
fig.tight_layout()
figure(fig, "fig10_4_1")
