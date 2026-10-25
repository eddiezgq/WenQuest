"""27.1 节的示意图。

图 27.1.1：三种法向接触模型的力-间隙关系：(a) 刚性接触（互补条件，φ ≥ 0，λ ≥ 0，φλ = 0），λ 轴上的竖线表示“压不进去”；
          (b) 罚函数（线性弹簧 λ = kδ）与赫兹接触 λ = Kδ^{3/2}（Ø10 mm 钢球压钢板，同一载荷 19.4 N 下取同一压入量）；
          (c) 横放在 V 形块中的毛坯：接触线上的赫兹压强分布（半宽 a，椭圆分布，最大压强 p₀）。
图 27.1.2：MuJoCo 中静止在地面上的球的穿透量随 solref 时间常数 τ 的变化：仿真（1、10、100 kg 三种质量重合）与式 (27.1.7)。
"""
import math

import numpy as np

from _ch27 import ball_xml, e_star, hertz_line, hertz_sphere, mj_rest, mj_rest_penetration, sh301_blank, G0
from bookout import COLORS as C, T, figure, style

plt = style()
fig, axs = plt.subplots(1, 3, figsize=(12.6, 3.7))
# (a) 刚性接触
ax = axs[0]
ax.plot([0, 3], [0, 0], color=C["z"], lw=2.4)
ax.plot([0, 0], [0, 3], color=C["z"], lw=2.4)
ax.annotate(T("分离：φ > 0，λ = 0", "apart: φ > 0, λ = 0"), (1.6, 0.05), (1.0, 0.8), fontsize=9.5, color=C["ink"],
            arrowprops=dict(arrowstyle="->", color=C["muted"]))
ax.annotate(T("接触：φ = 0，λ ≥ 0", "touching: φ = 0, λ ≥ 0"), (0.03, 2.0), (0.5, 2.4), fontsize=9.5, color=C["ink"],
            arrowprops=dict(arrowstyle="->", color=C["muted"]))
ax.set_xlim(-1, 3)
ax.set_ylim(-0.3, 3)
ax.axvspan(-1, 0, color=C["x"], alpha=0.07)
ax.text(-0.5, 1.3, T("穿透\n（不允许）", "penetration\n(not allowed)"), ha="center", fontsize=9, color=C["x"])
ax.set_xlabel(T("间隙 φ", "gap φ"))
ax.set_ylabel(T("法向接触力 λ", "normal contact force λ"))
ax.set_title(T("(a) 刚性接触：互补条件", "(a) rigid contact: complementarity"), fontsize=11)
ax.set_xticks([])
ax.set_yticks([])
# (b) 罚函数与赫兹
ax = axs[1]
m_b, r_b, L_b = sh301_blank()
N_line = m_b * G0 / (2 * math.cos(math.radians(45)))
d1, _, _ = hertz_sphere(N_line, 0.005)
dd = np.linspace(0, 1.6 * d1, 200)
K = 4 / 3 * e_star() * math.sqrt(0.005)
ax.plot(dd * 1e6, K * dd ** 1.5, color=C["z"], lw=2, label=T(r"赫兹：$\lambda = K\delta^{3/2}$", r"Hertz: $\lambda = K\delta^{3/2}$"))
ax.plot(dd * 1e6, N_line / d1 * dd, color=C["accent"], lw=1.6, ls="--", label=T(r"线性弹簧（割线）：$\lambda = k\delta$", r"linear spring (secant): $\lambda = k\delta$"))
ax.plot([d1 * 1e6], [N_line], "o", color=C["x"], ms=6)
ax.annotate(f"{N_line:.1f} N, {d1 * 1e6:.2f} µm", (d1 * 1e6, N_line), (0.15 * d1 * 1e6, 1.25 * N_line), fontsize=9, color=C["ink"],
            arrowprops=dict(arrowstyle="->", color=C["muted"]))
ax.set_xlabel(T("压入量 δ / µm", "indentation δ / µm"))
ax.set_ylabel(T("λ / N", "λ / N"))
ax.set_title(T("(b) Ø10 mm 钢球压钢板", "(b) Ø10 mm steel ball on a steel plate"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
# (c) 线接触的压强分布
ax = axs[2]
b, p0 = hertz_line(N_line / L_b, r_b)
x = np.linspace(-b, b, 300)
ax.fill_between(x * 1e6, p0 * np.sqrt(1 - (x / b) ** 2) / 1e6, color=C["z"], alpha=0.25)
ax.plot(x * 1e6, p0 * np.sqrt(1 - (x / b) ** 2) / 1e6, color=C["z"], lw=2)
ax.set_xlim(-1.6 * b * 1e6, 1.6 * b * 1e6)
ax.set_xlabel(T("离接触线的距离 / µm", "distance across the contact line / µm"))
ax.set_ylabel(T("压强 / MPa", "pressure / MPa"))
ax.text(0, p0 / 1e6 * 1.04, rf"$p_0$ = {p0 / 1e6:.1f} MPa", ha="center", fontsize=9.5)
ax.annotate("", (b * 1e6, 0.3), (-b * 1e6, 0.3), arrowprops=dict(arrowstyle="<->", color=C["ink"]))
ax.text(0, 0.9, f"2a = {2 * b * 1e6:.1f} µm", ha="center", fontsize=9.5)
ax.set_ylim(0, p0 / 1e6 * 1.18)
ax.set_title(T("(c) 毛坯在 V 形块上的线接触", "(c) line contact of the blank in a V-block"), fontsize=11)
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig27_1_1")

# ---------------------------------------------------------------- 图 27.1.2
fig, ax = plt.subplots(figsize=(6.4, 3.8))
tt = np.linspace(0.004, 0.05, 120)
ax.plot(tt * 1e3, [mj_rest_penetration(t) * 1e3 for t in tt], color=C["z"], lw=1.8, label=T("式 (27.1.7)", "Eq. (27.1.7)"))
mk = {1.0: "o", 10.0: "s", 100.0: "^"}
for m in (1.0, 10.0, 100.0):
    pts = []
    for tau in (0.005, 0.01, 0.02, 0.03, 0.04):
        dt = min(0.001, tau / 4)
        _, d = mj_rest(ball_xml(m=m, solref=f"{tau} 1", dt=dt), steps=int(4 / dt))
        pts.append((tau, -d.contact[0].dist))
    pts = np.array(pts)
    ax.plot(pts[:, 0] * 1e3, pts[:, 1] * 1e3, mk[m], mfc="none", color=C["x"] if m == 1 else (C["y"] if m == 10 else C["accent"]),
            ms=7 if m == 1 else 5, label=T(f"MuJoCo，{m:g} kg", f"MuJoCo, {m:g} kg"))
ax.axhline(1.0, color=C["muted"], lw=0.8, ls=":")
ax.text(5, 1.03, T("solimp 的过渡宽度 1 mm", "solimp transition width 1 mm"), fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("solref 的时间常数 τ / ms（阻尼比 1）", "solref time constant τ / ms (damping ratio 1)"))
ax.set_ylabel(T("静止时的穿透量 / mm", "penetration at rest / mm"))
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig27_1_2")
