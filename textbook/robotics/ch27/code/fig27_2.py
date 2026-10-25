"""27.2 节的示意图。

图 27.2.1：(a) 摩擦锥的截面（法向力取 1）：圆是库仑摩擦允许的切向力范围，半径 μ；内接的正方形是 4 条母线的棱锥（MuJoCo 的 pyramidal），
              对角方向只有 μ cos 45°；正八边形是 8 条母线。(b) 平口夹爪与 90° V 形夹爪夹 Ø50 mm 毛坯的截面：接触点、法向力，
              V 形夹爪每个指有两条接触线，法向力是夹紧力的 1/(2 cos γ)。
图 27.2.2：(a) MuJoCo 中竖直提起毛坯（静止）：夹紧力与毛坯相对夹爪的滑移量，竖线为公式给出的最小夹紧力；
          (b) 四种情况下所需的最小夹紧力：平口 / V 形 × 竖直（A 点）/ 水平（B 点），公式与 MuJoCo 的值。
"""
import math

import numpy as np

from _ch27 import G0, GRIP_TOP, MU_JAW, PAD_HALF, V_HALF, lift_test, mj_threshold, sh301_blank
from bookout import COLORS as C, T, figure, style

plt = style()
from matplotlib.patches import Circle, Polygon, Rectangle   # noqa: E402

fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.4))
ax = axs[0]
th = np.linspace(0, 2 * math.pi, 400)
ax.plot(MU_JAW * np.cos(th), MU_JAW * np.sin(th), color=C["z"], lw=2, label=T("摩擦锥（圆）", "friction cone (circle)"))
for k, col, ls in ((4, C["x"], "-"), (8, C["accent"], "--")):
    a = 2 * math.pi * np.arange(k + 1) / k
    ax.plot(MU_JAW * np.cos(a), MU_JAW * np.sin(a), color=col, lw=1.5, ls=ls,
            label=T(f"{k} 条母线的棱锥", f"pyramid with {k} edges"))
ax.annotate("", (MU_JAW / 2, MU_JAW / 2), (0, 0), arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.6))
ax.text(0.055, 0.115, r"$\mu\cos 45^\circ$", color=C["x"], fontsize=10)
ax.annotate("", (MU_JAW, 0), (0, 0), arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.6))
ax.text(0.10, -0.022, r"$\mu$", color=C["z"], fontsize=11)
ax.set_aspect("equal")
ax.set_xlim(-0.27, 0.27)
ax.set_ylim(-0.27, 0.27)
ax.set_xlabel(T(r"切向力 $f_{t1}/f_n$", r"tangential force $f_{t1}/f_n$"))
ax.set_ylabel(T(r"切向力 $f_{t2}/f_n$", r"tangential force $f_{t2}/f_n$"))
ax.set_title(T(f"(a) 摩擦锥的截面（μ = {MU_JAW}）", f"(a) cross-section of the friction cone (μ = {MU_JAW})"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="lower left")
ax.grid(alpha=0.25)
# (b) 两种夹爪
ax = axs[1]
r = 25.0
for cx, name in ((-60, T("平口夹爪", "flat jaws")), (60, T("V 形夹爪（90°）", "V-jaws (90°)"))):
    ax.add_patch(Circle((cx, 0), r, fc="#d9dde1", ec=C["ink"], lw=1.2))
    if cx < 0:
        for s in (1, -1):
            ax.add_patch(Rectangle((cx + s * r if s > 0 else cx - r - 8, -14), 8, 28, fc="#6b7680", ec=C["ink"]))
            ax.annotate("", (cx + s * (r - 12), 0), (cx + s * r, 0), arrowprops=dict(arrowstyle="->", color=C["x"], lw=2))
            ax.annotate("", (cx + s * (r + 8), 0), (cx + s * (r + 24), 0), arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1.5))
        ax.text(cx + r + 14, 4, "F", fontsize=11)
        ax.text(cx + 3, 5, "N = F", fontsize=9.5, color=C["x"])
    else:
        g = V_HALF
        for s in (1, -1):
            for sg in (1, -1):
                ang = sg * g if s > 0 else math.pi - sg * g
                p = np.array([cx + r * math.cos(ang), r * math.sin(ang)])
                n = -np.array([math.cos(ang), math.sin(ang)])
                apex = np.array([cx + s * r / math.cos(g), 0.0])
                u = (apex - p) / np.linalg.norm(apex - p)
                quad = [p - 12 * u, apex, apex - 6 * n * 1.4, p - 12 * u - 6 * n]
                ax.add_patch(Polygon(quad, fc="#6b7680", ec=C["ink"]))
                ax.annotate("", p + 12 * n, p, arrowprops=dict(arrowstyle="->", color=C["x"], lw=2))
            ax.annotate("", (cx + s * (r / math.cos(g) + 4), 0), (cx + s * (r / math.cos(g) + 20), 0), arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1.5))
        ax.text(cx + r / math.cos(g) + 10, 4, "F", fontsize=11)
        ax.text(cx - 14, -44, r"$N = F/(2\cos\gamma)$", fontsize=10, color=C["x"])
        ax.plot([cx, cx + 34 * math.cos(g)], [0, 34 * math.sin(g)], color=C["muted"], lw=0.8, ls=":")
        ax.plot([cx, cx + 34], [0, 0], color=C["muted"], lw=0.8, ls=":")
        ax.text(cx + 11, 3, "γ", fontsize=10, color=C["muted"])
    ax.text(cx, 34, name, ha="center", fontsize=10)
ax.set_xlim(-110, 120)
ax.set_ylim(-50, 46)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("(b) 夹爪截面：法向力 N 与夹紧力 F", "(b) jaw cross-sections: normal force N and grip force F"), fontsize=11)
fig.tight_layout()
figure(fig, "fig27_2_1")

# ---------------------------------------------------------------- 图 27.2.2
m_b, r_b, L_b = sh301_blank()
W = m_b * G0
Ff = W / (2 * MU_JAW)
Fv = W * math.cos(V_HALF) / (2 * MU_JAW)
d = L_b / 2 - GRIP_TOP
Ffh = W * (0.5 + d / (2 * PAD_HALF)) / MU_JAW
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.0))
ax = axs[0]
for jaw, F0, col, lab in (("flat", Ff, C["z"], T("平口", "flat")), ("V", Fv, C["accent"], T("V 形", "V"))):
    Fs = np.linspace(0.7 * F0, 1.3 * F0, 13)
    sl = [max(lift_test(jaw, "v", F)[0], 1e-3) for F in Fs]
    ax.semilogy(Fs, sl, "o-", color=col, ms=4, lw=1.3, label=T(f"{lab}夹爪（MuJoCo）", f"{lab} jaws (MuJoCo)"))
    ax.axvline(F0, color=col, lw=1, ls="--")
ax.set_xlabel(T("夹紧力 F / N", "grip force F / N"))
ax.set_ylabel(T("毛坯相对夹爪的滑移 / mm", "slip of the blank in the jaws / mm"))
ax.set_title(T("(a) 竖直提起：滑与不滑（虚线为公式）", "(a) vertical lift: slip or hold (dashed: formula)"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
ax.grid(alpha=0.25, which="both")
ax = axs[1]
vals = [("flat", "v", Ff), ("V", "v", Fv), ("flat", "h", Ffh), ("V", "h", None)]
labels = [T("平口\n竖直", "flat\nvertical"), T("V 形\n竖直", "V\nvertical"), T("平口\n水平", "flat\nhorizontal"), T("V 形\n水平", "V\nhorizontal")]
mjv = [mj_threshold(j, o, 0.0, lo=5.0, hi=400.0, tol=0.5) for j, o, _ in vals]
x = np.arange(4)
ax.bar(x - 0.18, [v[2] if v[2] else 0 for v in vals], width=0.34, color=C["z"], label=T("公式", "formula"))
ax.bar(x + 0.18, mjv, width=0.34, color=C["accent"], label="MuJoCo")
for i, v in enumerate(mjv):
    ax.text(i + 0.18, v + 4, f"{v:.0f}", ha="center", fontsize=9)
    if vals[i][2]:
        ax.text(i - 0.18, vals[i][2] + 4, f"{vals[i][2]:.0f}", ha="center", fontsize=9)
ax.text(3 - 0.18, 6, T("见\n27.4 节", "see\n§27.4"), ha="center", fontsize=8, color=C["muted"])
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=9.5)
ax.set_ylabel(T("最小夹紧力 / N", "minimum grip force / N"))
ax.set_title(T("(b) 静止时所需的最小夹紧力（μ = 0.2）", "(b) minimum grip force at rest (μ = 0.2)"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25, axis="y")
fig.tight_layout()
figure(fig, "fig27_2_2")
