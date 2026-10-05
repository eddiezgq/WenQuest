"""图 14.6.1：主轴与主应力。(a) L 形手爪支架（俯视）：质心与惯量主轴，主轴相对板的长边倾斜约 17°；
(b) 平面应力 σx = 50、σy = −20、τxy = 30 MPa 的莫尔圆：圆与横轴的两个交点就是 xy 平面内的两个主应力（2×2 对称矩阵的特征值；σz = 10 MPa 是中间主应力 σ₂，所以这两个是 σ₁ 与 σ₃）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.5))
a1.add_patch(plt.Rectangle((-150, -30), 300, 60, fc=BLUE, alpha=0.25, ec=BLUE))
a1.add_patch(plt.Rectangle((130 - 20, 80 - 50), 40, 100, fc=GREEN, alpha=0.3, ec=GREEN))
c = np.array([43.3, 26.7])
a1.plot(*c, "o", color=INK, ms=6)
a1.text(c[0] + 6, c[1] - 14, T("质心", "centre of mass"), fontsize=10)
th = np.radians(16.9)
for ang, col, lab in ((th, RED, T("主轴 1（最小主惯量）", "axis 1 (smallest)")), (th + np.pi / 2, ACC, T("主轴 2", "axis 2"))):
    d = np.array([np.cos(ang), np.sin(ang)])
    a1.plot([c[0] - 170 * d[0], c[0] + 170 * d[0]], [c[1] - 170 * d[1], c[1] + 170 * d[1]], "--", color=col, lw=1.4)
    a1.text(c[0] + 150 * d[0] + 4, c[1] + 150 * d[1], lab, color=col, fontsize=9)
a1.set_aspect("equal"); a1.set_xlim(-170, 230); a1.set_ylim(-110, 190)
a1.set_xlabel("x / mm"); a1.set_ylabel("y / mm")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) L 形支架的惯量主轴（俯视）", "(a) Principal axes of an L bracket (top view)"), fontsize=11)
sx, sy, txy = 50.0, -20.0, 30.0
cen, R = (sx + sy) / 2, np.hypot((sx - sy) / 2, txy)
t = np.linspace(0, 2 * np.pi, 300)
a2.plot(cen + R * np.cos(t), R * np.sin(t), color=ACC, lw=2)
a2.plot([sx, sy], [txy, -txy], "o-", color=INK, lw=1)
a2.text(sx + 2, txy + 3, "(σx, τxy)", fontsize=10); a2.text(sy - 18, -txy - 7, "(σy, −τxy)", fontsize=10)
for v, lab in ((cen + R, "σ₁"), (cen - R, "σ₃")):
    a2.plot(v, 0, "s", color=RED, ms=8)
    a2.text(v - 4, 5, f"{lab} = {v:.1f}", color=RED, fontsize=10, ha="center")
a2.axhline(0, color=MUTED, lw=0.8); a2.axvline(0, color=MUTED, lw=0.6)
a2.set_aspect("equal"); a2.set_xlabel(T("正应力 / MPa", "normal stress / MPa")); a2.set_ylabel(T("剪应力 / MPa", "shear stress / MPa"))
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 莫尔圆：主应力是特征值", "(b) Mohr's circle: principal stresses are eigenvalues"), fontsize=11)
fig.tight_layout()
figure(fig, "fig14_6_1")
