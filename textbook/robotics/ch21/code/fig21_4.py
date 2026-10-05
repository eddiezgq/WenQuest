"""21.4 节的示意图。

图 21.4.1：四旋翼的微分平坦：由平坦输出 (p, ψ) 及其导数依次求出总推力与 z_b、姿态 R、物体角速度、物体角加速度，
          再由动力学（28.3 节）求力矩和四个推力。
图 21.4.2：数字工厂巡检的最小 snap 轨迹（算例 21.4.2）：(a) 车间俯视，航点、折线与轨迹（颜色表示速度）；(b) 高度与速度随时间的变化。
图 21.4.3：(a)(b) 同一组航点和时间下 k = 2、3、4 的物体角速度 ω_x 与角加速度的大小（算例 21.4.3）；
          (c)(d) 时间缩放后最快的最小 snap 轨迹：倾角、总推力与物体角速度（倾角达到 30° 的限制）。
"""
import math

import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from _fig21 import C, arrow
from _uav import flat, min_deriv_spline, spline_eval, x2
from bookout import T, figure, style
import ex21_4 as E

plt = style()
m = x2()["m"]

# ---------------------------------------------------------------- 图 21.4.1
fig, ax = plt.subplots(figsize=(12.0, 4.6))
ax.axis("off")
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.6)


def box(x, y, w, h, txt, fc, fs=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.12", fc=fc, ec=C["dark"], lw=1.0))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs)


box(0.2, 1.6, 1.9, 1.4, T("平坦输出\n$p(t)$，$\\psi(t)$", "flat outputs\n$p(t)$, $\\psi(t)$"), "#e8f1fa", 11.5)
rows = [(3.55, T(r"$\ddot p$", r"$\ddot p$"), T("总推力 $f$、$z_b$\n式 (21.2.3)", "thrust $f$, $z_b$\nEq. (21.2.3)")),
        (2.55, r"$+\ \psi$", T("姿态 $R$\n式 (21.2.5)", "attitude $R$\nEq. (21.2.5)")),
        (1.55, r"$\dddot p,\ \dot\psi$", T("物体角速度 $\\omega_b$\n式 (21.4.2)、(21.4.3)", "body rate $\\omega_b$\nEqs. (21.4.2), (21.4.3)")),
        (0.55, r"$p^{(4)},\ \ddot\psi$", T("物体角加速度 $\\dot\\omega_b$\n式 (21.4.4)", "body acceleration $\\dot\\omega_b$\nEq. (21.4.4)"))]
for y, der, txt in rows:
    box(4.0, y - 0.35, 2.9, 0.75, txt, "#f5f7f8", 10)
    arrow(ax, (2.15, 2.3), (3.95, y), C["muted"], 0.8, 9)
    ax.text(3.88, y + 0.1, der, fontsize=11, color=C["blue"], ha="right", va="bottom")
box(8.0, 0.25, 1.7, 1.0, T("力矩 $m_b$\n（28.3 节）", "moments $m_b$\n(Section 28.3)"), "#fdf3e1", 10)
box(10.2, 0.25, 1.6, 1.0, T("四个推力\n式 (21.1.8)", "four thrusts\nEq. (21.1.8)"), "#fdf3e1", 10)
arrow(ax, (6.95, 0.6), (7.95, 0.7), C["muted"], 1.0, 9)
arrow(ax, (9.75, 0.75), (10.15, 0.75), C["muted"], 1.0, 9)
arrow(ax, (6.95, 3.55), (10.6, 1.3), C["muted"], 0.8, 8, ls="--")
ax.text(8.9, 2.75, T("总推力直接给出推力之和", "the collective thrust is the sum"), fontsize=9, color=C["muted"], rotation=-31)
ax.text(8.0, 4.15, T("不需要积分任何微分方程：只要求导和代数运算", "no differential equation is integrated: only derivatives and algebra"),
        fontsize=10, color=C["accent"], ha="center")
figure(fig, "fig21_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.4.2
LAYOUT = {"store-01": (3, 4, 4, 5), "saw-01": (10, 4, 4, 2.5), "cnc-l01-a": (17, 4, 4, 2.2), "cnc-l01-b": (24, 4, 4, 2.2),
          "key-01": (31, 4, 3, 2.2), "ht-01": (17, 13, 5, 4), "grd-01": (31, 13, 4.5, 2.2), "qc-01": (38, 13, 4, 3),
          "vmc-01": (10, 22, 3.5, 3), "hmc-01": (17, 22, 4.5, 3.5), "hob-01": (24, 22, 3.5, 2.5), "asm-01": (31, 22, 5, 3),
          "test-01": (38, 22, 3.5, 2.5), "store-02": (45, 22, 4, 5)}          # 与 factory/digital/wqbus/layout.py 相同
fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.2, 4.9), gridspec_kw={"width_ratios": [1.55, 1.0]})
a1.set_aspect("equal")
for k, (x, yf, w, d) in LAYOUT.items():
    y = 28 - yf
    a1.add_patch(Rectangle((x - w / 2, y - d / 2), w, d, fc=C["light"] if k not in ("ht-01", "grd-01", "qc-01") else "#f3e2b3",
                           ec=C["dark"], lw=0.6))
    a1.text(x, y, k, fontsize=7, ha="center", va="center", color=C["dark"])
for yy in (28 - 9.0, 28 - 18.5):
    a1.axhspan(yy - 1, yy + 1, color="#eef2f4", zorder=0)
C4, Ts = E.C_f, E.Ts_fast
tt = np.linspace(0, Ts.sum(), 1500)
P_ = np.array([spline_eval(C4, Ts, t) for t in tt])
V_ = np.array([np.linalg.norm(spline_eval(C4, Ts, t, 1)) for t in tt])
a1.plot(E.WP[:, 0], E.WP[:, 1], color=C["muted"], lw=0.9, ls="--", zorder=2)
sc = a1.scatter(P_[:, 0], P_[:, 1], c=V_, cmap="viridis", s=4, zorder=3)
for nm, w in zip(E.NAMES, E.WP):
    a1.plot(w[0], w[1], "o", ms=6, mfc="white", mec=C["red"], mew=1.5, zorder=4)
    left = nm == "W0"                                   # W0 的标注放在左侧，免得与 W1 的重叠
    a1.text(w[0] + (-0.4 if left else 0.4), w[1] + 0.5, f"{nm}  {w[2]:g} m", fontsize=8.5, color=C["red"], zorder=6,
            ha="right" if left else "left",
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
cb = fig.colorbar(sc, ax=a1, fraction=0.03, pad=0.02)
cb.set_label(T("速度 / (m/s)", "speed / (m/s)"))
a1.set_xlim(0, 50)
a1.set_ylim(0, 28)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("(a) 车间俯视：航点（旁注高度）、折线（虚线）与最小 snap 轨迹", "(a) workshop from above: waypoints (with heights), polyline, minimum-snap path"),
             fontsize=10.5)
a2.plot(tt, P_[:, 2], color=C["blue"], lw=1.8, label=T("高度 z / m", "height z / m"))
a2.plot(tt, V_, color=C["orange"], lw=1.6, label=T("速度 / (m/s)", "speed / (m/s)"))
tw = np.cumsum(np.r_[0, Ts])
for t_, nm in zip(tw, E.NAMES):
    a2.axvline(t_, color=C["muted"], lw=0.5, ls=":")
    a2.text(t_, 6.3, nm, fontsize=8, ha="center", color=C["red"])
a2.set_ylim(0, 6.6)
a2.set_xlabel(T("时间 / s", "time / s"))
a2.legend(fontsize=9, frameon=False, loc="lower center")
a2.grid(alpha=0.25)
a2.set_title(T(f"(b) 高度与速度（总时间 {E.T_fast:.2f} s）", f"(b) height and speed (total {E.T_fast:.2f} s)"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig21_4_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 21.4.3
fig, axs = plt.subplots(2, 2, figsize=(12.0, 7.2))
Tso = E.Ts_opt
tt = np.linspace(0, Tso.sum(), 2400)
cols = {2: C["red"], 3: C["green"], 4: C["blue"]}
names = {2: T("k = 2（最小加速度）", "k = 2 (min. acceleration)"), 3: T("k = 3（最小加加速度）", "k = 3 (min. jerk)"),
         4: T("k = 4（最小 snap）", "k = 4 (min. snap)")}
for k in (2, 3, 4):
    Ck, _ = min_deriv_spline(E.WP, Tso, k)
    wx, dw = [], []
    for t in tt:
        F = flat([spline_eval(Ck, Tso, t, r) for r in range(5)], 0.0, 0.0, 0.0, m)
        wx.append(F["w"][0])
        dw.append(np.linalg.norm(F["dw"]))
    axs[0, 0].plot(tt, wx, color=cols[k], lw=1.4, label=names[k])
    if k > 2:
        axs[0, 1].plot(tt, dw, color=cols[k], lw=1.4, label=names[k])
for t_ in np.cumsum(np.r_[0, Tso])[1:-1]:
    for a_ in axs[0]:
        a_.axvline(t_, color=C["muted"], lw=0.5, ls=":")
axs[0, 0].set_ylabel(T(r"$\omega_x$ / (rad/s)", r"$\omega_x$ / (rad/s)"))
axs[0, 0].set_title(T("(a) 横滚角速度：k = 2 时在航点处跳变", "(a) roll rate: jumps at the waypoints for k = 2"), fontsize=10.5)
axs[0, 0].legend(fontsize=8.5, frameon=False)
axs[0, 1].set_ylabel(T(r"$\|\dot\omega_b\|$ / (rad/s²)", r"$\|\dot\omega_b\|$ / (rad/s²)"))
axs[0, 1].set_title(T("(b) 角加速度：k = 3、4 都连续（k = 2 在航点处为冲击）", "(b) angular acceleration: continuous for k = 3, 4 (k = 2: impulses)"),
                    fontsize=10.5)
axs[0, 1].legend(fontsize=8.5, frameon=False)
S = E.S_f
axs[1, 0].plot(S["t"], np.degrees(S["tilt"]), color=C["blue"], lw=1.5, label=T("倾角 / (°)", "tilt / (°)"))
axs[1, 0].axhline(30, color=C["blue"], lw=0.8, ls="--")
axs[1, 0].plot(S["t"], S["f"], color=C["orange"], lw=1.5, label=T("总推力 / N", "thrust / N"))
axs[1, 0].axhline(39, color=C["orange"], lw=0.8, ls="--")
axs[1, 0].legend(fontsize=8.5, frameon=False, loc="upper left", ncol=2)
axs[1, 0].set_ylim(0, 50)
axs[1, 0].set_title(T("(c) 最快的轨迹：倾角碰到 30° 的限制（虚线为限制）", "(c) fastest trajectory: the tilt reaches its 30° limit (dashed: limits)"), fontsize=10.5)
axs[1, 1].plot(S["t"], S["w"], color=C["purple"], lw=1.5, label=T(r"$\|\omega_b\|$ / (rad/s)", r"$\|\omega_b\|$ / (rad/s)"))
axs[1, 1].plot(S["t"], S["v"], color=C["green"], lw=1.5, label=T("速度 / (m/s)", "speed / (m/s)"))
axs[1, 1].axhline(2, color=C["purple"], lw=0.8, ls="--")
axs[1, 1].legend(fontsize=8.5, frameon=False, loc="upper right")
axs[1, 1].set_title(T("(d) 最快的轨迹：角速度与速度", "(d) fastest trajectory: body rate and speed"), fontsize=10.5)
for a_ in axs.flat:
    a_.set_xlabel(T("时间 / s", "time / s"))
    a_.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig21_4_3")
plt.close(fig)
