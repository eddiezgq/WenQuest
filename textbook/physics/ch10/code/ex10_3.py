"""10.3 节的计算：

算例 10.3.2  双稳态柔性机构（如断电也能保持开、合两个位置的夹爪、阀门）的势能 U(x) = U0[(x/x0)² − 1]²，
            x0 = 2.0 mm，U0 = 5.0 mJ。求力 F(x)，平衡位置及其稳定性，阱底的等效劲度，切换所需的最大推力；
            能量 E = 2.0 mJ 与 8.0 mJ（从阱底量起）时运动的范围（转折点）（图 10.3.2）。
算例 10.3.1  机器人腕部的柔顺装置：x、y 两个方向的劲度 k_x = 200 N/m、k_y = 800 N/m，U = ½(k_x x² + k_y y²)。
            末端偏离到 (5.0, 5.0) mm 时恢复力多大、指向哪里？与指向原点的方向差多少度（图 10.3.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 10.3.1
x0, U0 = 2.0e-3, 5.0e-3
U = lambda x: U0 * ((x / x0) ** 2 - 1) ** 2
F = lambda x: -4 * U0 / x0 ** 2 * x * ((x / x0) ** 2 - 1)
xs = np.linspace(-3.2e-3, 3.2e-3, 2001)
Fnum = -np.gradient(U(xs), xs)
assert np.max(np.abs(Fnum[5:-5] - F(xs)[5:-5])) < 1e-3          # F = −dU/dx（数值核对）
k_well = 8 * U0 / x0 ** 2
x_pk = x0 / math.sqrt(3)
F_pk = 8 * U0 / (3 * math.sqrt(3) * x0)
assert abs(abs(F(x_pk)) - F_pk) < 1e-12
E1, E2 = 2.0e-3, 8.0e-3
tp1 = (x0 * math.sqrt(1 - math.sqrt(E1 / U0)), x0 * math.sqrt(1 + math.sqrt(E1 / U0)))
tp2 = x0 * math.sqrt(1 + math.sqrt(E2 / U0))
assert abs(U(tp1[0]) - E1) < 1e-12 and abs(U(tp1[1]) - E1) < 1e-12 and abs(U(tp2) - E2) < 1e-12
out(x0_mm=x0 * 1e3, U0_mJ=U0 * 1e3, k_well=k_well, x_pk_mm=x_pk * 1e3, F_pk=F_pk, E1_mJ=E1 * 1e3, E2_mJ=E2 * 1e3,
    tp1a=tp1[0] * 1e3, tp1b=tp1[1] * 1e3, tp2=tp2 * 1e3, F_at_1mm=abs(F(1.0e-3)), U_at_0=U(0.0) * 1e3)

# ---- 算例 10.3.2
kx, ky = 200.0, 800.0
p = np.array([5.0e-3, 5.0e-3])
Fp = -np.array([kx * p[0], ky * p[1]])
ang = math.degrees(math.acos(np.dot(Fp, -p) / (np.linalg.norm(Fp) * np.linalg.norm(p))))
out(kx=kx, ky=ky, Fx=abs(Fp[0]), Fy=abs(Fp[1]), Fmag=float(np.linalg.norm(Fp)), ang=ang, Up_mJ=0.5 * (kx * p[0] ** 2 + ky * p[1] ** 2) * 1e3)

plt = style()
# ---- 图 10.3.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
mm = xs * 1e3
a1.plot(mm, U(xs) * 1e3, color=d.INK, lw=2)
for E, col, lab in ((E1, d.VA, "E = 2 mJ"), (E2, d.VR, "E = 8 mJ")):
    inside = U(xs) <= E
    a1.plot(mm[inside & (xs > 0)] if E < U0 else mm[inside], np.full((inside & (xs > 0)).sum() if E < U0 else inside.sum(), E * 1e3),
            color=col, lw=1.6)
    a1.text(3.25, E * 1e3, lab, color=col, fontsize=8.5, va="center")
for xp in (-x0, x0):
    a1.plot(xp * 1e3, 0, "o", color=d.VB, ms=6)
a1.plot(0, U0 * 1e3, "o", color=d.VR, ms=6, mfc="white")
a1.text(-0.2, U0 * 1e3 + 0.7, T("不稳定", "unstable"), fontsize=8.5, ha="center", color=d.VR)
a1.text(-2.0, -1.1, T("稳定", "stable"), fontsize=8.5, ha="center", color=d.VB)
a1.text(2.0, -1.1, T("稳定", "stable"), fontsize=8.5, ha="center", color=d.VB)
a1.set_xlabel("x / mm"); a1.set_ylabel(T("势能 U / mJ", "potential energy U / mJ")); a1.set_ylim(-1.8, 14); a1.set_xlim(-3.3, 4.0); d.spines(a1)
a1.set_title(T("(a) 势能曲线与两个能量", "(a) potential curve and two energies"), fontsize=9.5)
a2.plot(mm, F(xs), color=d.VR, lw=2)
a2.axhline(0, color=d.MUTED, lw=0.6)
for xp, c in ((-x0, d.VB), (0.0, d.VR), (x0, d.VB)):
    a2.plot(xp * 1e3, 0, "o", color=c, ms=6, mfc="white" if xp == 0 else c)
a2.plot(x_pk * 1e3, F(x_pk), "s", color=d.INK, ms=5)
a2.text(x_pk * 1e3 + 0.15, F(x_pk) - 0.4, T(f"{F_pk:.2f} N", f"{F_pk:.2f} N"), fontsize=8.5)
a2.set_xlabel("x / mm"); a2.set_ylabel(T("力 F = −dU/dx / N", "force F = −dU/dx / N")); a2.set_xlim(-3.3, 3.3); a2.set_ylim(-12, 12); d.spines(a2)
a2.set_title(T("(b) 力：U 下降的方向", "(b) force points downhill in U"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig10_3_2")

# ---- 图 10.3.2：二维势能的等势线与力
fig, ax = plt.subplots(figsize=(3.6, 3.3))
gx, gy = np.meshgrid(np.linspace(-8, 8, 200), np.linspace(-8, 8, 200))
Ug = 0.5 * (kx * (gx * 1e-3) ** 2 + ky * (gy * 1e-3) ** 2) * 1e3
ax.contour(gx, gy, Ug, levels=[1, 2, 4, 6, 8, 12, 16, 20], colors=d.MUTED, linewidths=0.8)
P = p * 1e3
d.arrow(ax, P, P + Fp * 1.0, d.VR, lw=2, label=T("恢复力", "restoring force"), off=(1.6, -0.9), fs=9)
d.arrow(ax, P, P - P / np.linalg.norm(P) * 4.12, d.MUTED, lw=1.0, ms=9)
ax.text(0.3, 3.4, T("指向原点", "toward origin"), fontsize=8, color=d.MUTED)
ax.plot(*P, "o", color=d.INK, ms=5); ax.plot(0, 0, "+", color=d.INK, ms=9)
ax.set_xlabel("x / mm"); ax.set_ylabel("y / mm"); ax.set_aspect("equal"); ax.set_xlim(-8, 8); ax.set_ylim(-8, 8); d.spines(ax)
figure(fig, "fig10_3_1")
