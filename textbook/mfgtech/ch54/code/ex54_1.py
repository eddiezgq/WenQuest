"""算例 54.1.1：误差敏感方向。SH-301 轴承位 Ø35（R = 17.5 mm），刀尖相对工件轴线偏移 δ = 0.01 mm：
沿法向（y）偏移时直径变化 Δd ≈ 2δ，沿切向（z）偏移时 Δd ≈ δ²/R，相差三个数量级以上；k6 公差 0.016 的十分之一允许切向偏移多少。
图 54.1.4：两个方向偏移的几何关系与 Δd–δ 曲线；图 54.1.5：车削与镗削的误差敏感方向。计算用 hub/accuracy.py 的 diameter_error。"""
import math

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
R, d = 17.5, 0.01
dn = A.diameter_error(R, dy=d)
dt = A.diameter_error(R, dz=d)
T6 = 0.016
dz_allow = math.sqrt((T6 / 10) * R)            # Δd ≈ dz²/R = T/10
assert abs(A.diameter_error(R, dz=dz_allow) - T6 / 10) < 1e-6

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.4), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axs[0]
th = [2 * math.pi * i / 200 for i in range(201)]
r0, e = 1.0, 0.25                              # 示意：偏移量放大
ax.plot([r0 * math.cos(t) for t in th], [r0 * math.sin(t) for t in th], color=M.MUTED, lw=1)
r1 = r0 + e
ax.plot([r1 * math.cos(t) for t in th], [r1 * math.sin(t) for t in th], color=M.RED, lw=1, ls="--")
r2 = math.hypot(r0, e)
ax.plot([r2 * math.cos(t) for t in th], [r2 * math.sin(t) for t in th], color=M.ACCENT, lw=1, ls=":")
ax.plot([0], [0], "k+", ms=8)
ax.plot([-r0], [0], "ko", ms=4)
ax.annotate("", xy=(-r1, 0), xytext=(-r0, 0), arrowprops=dict(arrowstyle="-|>", color=M.RED, lw=1.4))
ax.annotate("", xy=(-r0, e), xytext=(-r0, 0), arrowprops=dict(arrowstyle="-|>", color=M.ACCENT, lw=1.4))
ax.plot([0, -r0], [0, e], color=M.ACCENT, lw=0.8)
ax.text(-r1 - 0.05, -0.2, T("法向 δ：\n半径 R + δ", "normal δ:\nradius R + δ"), color=M.RED, fontsize=7.5, ha="right")
ax.text(-r0 + 0.05, e + 0.08, T("切向 δ：半径 √(R² + δ²)", "tangential δ: radius √(R² + δ²)"), color=M.ACCENT, fontsize=7.5)
ax.text(0.08, -0.15, T("工件轴线", "axis"), fontsize=7.5)
ax.set_aspect("equal")
ax.set_xlim(-1.75, 1.35); ax.set_ylim(-1.35, 1.45); ax.axis("off")
ax.set_title(T("(a) 刀尖偏移 δ（放大画）", "(a) tool tip moved by δ (exaggerated)"), fontsize=8.5)
ax = axs[1]
ds = [10 ** (-4 + 3 * i / 100) for i in range(101)]
ax.loglog([x * 1000 for x in ds], [A.diameter_error(R, dy=x) * 1000 for x in ds], color=M.RED, label=T("法向（y）：Δd ≈ 2δ", "normal (y): Δd ≈ 2δ"))
ax.loglog([x * 1000 for x in ds], [A.diameter_error(R, dz=x) * 1000 for x in ds], color=M.ACCENT, label=T("切向（z）：Δd ≈ δ²/R", "tangential (z): Δd ≈ δ²/R"))
ax.axhline(T6 * 1000, color=M.MUTED, ls="--", lw=0.8)
ax.text(0.12, T6 * 1000 * 1.25, T("k6 公差 16 µm", "k6 tolerance 16 µm"), fontsize=7.5, color=M.MUTED)
ax.plot([d * 1000], [dn * 1000], "o", color=M.RED, ms=4)
ax.plot([d * 1000], [dt * 1000], "o", color=M.ACCENT, ms=4)
ax.set_xlabel(T("刀尖偏移 δ / µm", "tool tip displacement δ / µm"))
ax.set_ylabel(T("直径变化 Δd / µm", "diameter change Δd / µm"))
ax.set_title(T("(b) Ø35 外圆（R = 17.5 mm）", "(b) Ø35 diameter (R = 17.5 mm)"), fontsize=8.5)
ax.legend(fontsize=7.5, loc="lower right")
ax.grid(True, which="both", lw=0.3, alpha=0.5)
figure(fig, "fig54_1_4")

# 图 54.1.5：车削（刀具不动、工件转）与镗削（刀具随镗杆转、工件不动）
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.3))
for ax, mode in zip(axs, ("turning", "boring")):
    ax.plot([math.cos(t) for t in th], [math.sin(t) for t in th], color=M.INK, lw=1.2)
    ax.plot([0], [0], "k+", ms=8)
    if mode == "turning":
        ax.plot([-1.6, -1.0], [0, 0], color=M.WARM, lw=3.5)
        ax.text(-1.3, 0.1, T("车刀", "tool"), color=M.WARM, fontsize=7.5, ha="center")
        ax.annotate("", xy=(-1.55, -0.14), xytext=(-1.05, -0.14), arrowprops=dict(arrowstyle="<->", color=M.RED, lw=1.2), annotation_clip=False)
        ax.text(-1.3, -0.45, T("敏感方向\n固定（y）", "sensitive\ndirection fixed"), color=M.RED, fontsize=7.5, ha="center")
        ax.annotate("", xy=(0.55, 0.55), xytext=(0.65, -0.35), arrowprops=dict(arrowstyle="-|>", color=M.MUTED, connectionstyle="arc3,rad=0.4"))
        ax.text(0.75, 0.0, T("工件转", "work turns"), fontsize=7.5, color=M.MUTED)
        ax.set_title(T("(a) 车削：刀具不动，工件转", "(a) turning: tool fixed, work turns"), fontsize=8.5)
    else:
        for k in range(8):
            t = 2 * math.pi * k / 8
            ax.annotate("", xy=(0.97 * math.cos(t), 0.97 * math.sin(t)), xytext=(0.55 * math.cos(t), 0.55 * math.sin(t)),
                        arrowprops=dict(arrowstyle="<->", color=M.RED, lw=0.9))
        ax.plot([0, 0.97], [0, 0], color=M.WARM, lw=3)
        ax.text(0.5, 0.1, T("镗刀", "bar"), color=M.WARM, fontsize=7.5, ha="center")
        ax.annotate("", xy=(-0.2, 0.42), xytext=(-0.42, -0.2), arrowprops=dict(arrowstyle="-|>", color=M.MUTED, connectionstyle="arc3,rad=-0.5"))
        ax.text(0, -1.3, T("敏感方向随镗刀转动", "sensitive direction turns with the bar"), color=M.RED, fontsize=7.5, ha="center")
        ax.set_title(T("(b) 镗削：镗刀随镗杆转，工件不动", "(b) boring: the bar turns, work fixed"), fontsize=8.5)
    ax.set_aspect("equal"); ax.set_xlim(-1.75, 1.35); ax.set_ylim(-1.45, 1.3); ax.axis("off")
figure(fig, "fig54_1_5")

out(R=R, delta_um=d * 1000, dn_um=dn * 1000, dt_um=dt * 1000, ratio=dn / dt, dz_allow=dz_allow)
