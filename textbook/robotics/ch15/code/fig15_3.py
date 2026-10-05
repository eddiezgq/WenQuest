"""15.3 节的示意图。

图 15.3.1：三种方法都是对奇异值的“滤波”：沿第 i 个奇异方向，修正量是误差分量的 g(σᵢ) 倍。
           牛顿法 g = 1/σ；雅可比转置法 g = ασ；阻尼最小二乘 g = σ/(σ² + λ²)，最大值 1/(2λ) 在 σ = λ 处。
图 15.3.2：算例 15.3.2，UR5e 沿直线经过手腕奇异附近：(a) θ5；(b) 关节 4、6 的转速；(c) 跟踪误差。
"""
import math

import numpy as np

from _fig15 import C, logaxis
from _nik import WristPath
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 15.3.1
fig, ax = plt.subplots(figsize=(6.6, 4.3))
s = np.logspace(-3, 0.5, 400)
ax.plot(s, 1 / s, color=C["x"], lw=1.8, label=T("牛顿法：1/σ", "Newton: 1/σ"))
for lam, c in ((0.05, C["z"]), (0.2, "#6baed6")):
    g = s / (s ** 2 + lam ** 2)
    ax.plot(s, g, color=c, lw=1.8, label=T(f"阻尼最小二乘：σ/(σ² + λ²)，λ = {lam}", f"damped least squares: σ/(σ² + λ²), λ = {lam}"))
    ax.plot([lam], [1 / (2 * lam)], "o", color=c, ms=5)
    ax.annotate(T(f"最大 1/(2λ) = {1 / (2 * lam):.1f}", f"max 1/(2λ) = {1 / (2 * lam):.1f}"), xy=(lam, 1 / (2 * lam)),
                xytext=(lam * 1.6, 1 / (2 * lam) * 2.4), fontsize=9, color=c, arrowprops=dict(arrowstyle="-", color=c, lw=0.8))
ax.plot(s, 1.0 * s, color=C["accent"], lw=1.8, label=T("雅可比转置：ασ（α = 1）", "Jacobian transpose: ασ (α = 1)"))
ax.set_xscale("log")
logaxis(ax)
ax.set_ylim(1e-3, 1e3)
ax.set_xlabel(T("奇异值 σ", "singular value σ"))
ax.set_ylabel(T("增益 g(σ)：修正量 / 误差分量", "gain g(σ): correction / error component"))
ax.legend(fontsize=8.5, frameon=False, loc="lower left")
ax.axvspan(1e-3, 2e-2, color="#f6e7e7", zorder=0)
ax.text(1.2e-3, 400, T("接近奇异", "near singular"), fontsize=9, color=C["x"])
fig.tight_layout()
figure(fig, "fig15_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 15.3.2
P = WristPath()
ana = P.analytic()
runs = [(P.run("exact"), C["x"], T("精确求逆", "exact inverse")),
        (P.run("fixed", lam=0.01), C["z"], T("固定阻尼 λ = 0.01 m", "fixed damping λ = 0.01 m")),
        (P.run("var", lam=0.02, eps=0.01), C["accent"], T("可变阻尼", "variable damping"))]
t = np.arange(P.N) * P.dt
fig, axs = plt.subplots(1, 3, figsize=(11.2, 3.6))
ax = axs[0]
for H, c, lab in runs:
    ax.plot(t, np.degrees(H["th"][:, 4]), color=c, lw=1.5, label=lab)
ax.axhline(0, color=C["muted"], lw=0.8, ls=":")
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel("θ₅ / (°)")
ax.set_title(T("(a) 关节 5：手腕离奇异多远", "(a) Joint 5: distance from the wrist singularity"), fontsize=10, loc="left")
ax.legend(fontsize=8, frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax = axs[1]
for H, c, lab in runs:
    ax.plot(t, np.degrees(np.abs(H["dth"][:, 3])), color=c, lw=1.4)
    ax.plot(t, np.degrees(np.abs(H["dth"][:, 5])), color=c, lw=1.0, ls="--")
ax.axhline(180, color=C["ink"], lw=1.0, ls=":")
ax.text(0.05, 200, T("UR5e 关节速度上限 180°/s", "UR5e joint speed limit 180°/s"), fontsize=8.5)
logaxis(ax)
ax.set_ylim(0.1, 2000)
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("转速 / (°/s)", "speed / (°/s)"))
ax.set_title(T("(b) 关节 4（实线）、关节 6（虚线）", "(b) Joint 4 (solid), joint 6 (dashed)"), fontsize=10, loc="left")
ax = axs[2]
for H, c, lab in runs:
    ax.plot(t, H["ep"] * 1000, color=c, lw=1.4)
    ax.plot(t, np.degrees(H["eo"]), color=c, lw=1.0, ls="--")
logaxis(ax)
ax.set_ylim(1e-5, 10)
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("位置误差 / mm（实线）；姿态误差 / (°)（虚线）", "position error / mm (solid); orientation / (°) (dashed)"), fontsize=9)
ax.set_title(T("(c) 跟踪误差", "(c) Tracking error"), fontsize=10, loc="left")
fig.tight_layout()
figure(fig, "fig15_3_2")
plt.close(fig)
