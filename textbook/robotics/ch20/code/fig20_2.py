"""20.2 节的示意图。

图 20.2.1：浮动基座：四只脚踩在地上不动（{s} 中位置不变），机身改变位姿（算例 20.2.1），各腿的关节角随之改变。
          斜二测投影：站立姿态（淡色）与改变后的姿态（实色），{s}、{b} 两个坐标系，足端在 {b} 中的位置矢量 p_i。
图 20.2.2：(a) 只有对角两只脚着地时，腿的运动学测不出机身绕两脚连线的转动（俯视）；
          (b) 右后脚打滑时，四条腿的最小二乘残差（算例 20.2.3）。
"""
import math

import numpy as np

from _fig20 import C, arrow, plane
from _leg import GO2, GO2_FOOT_R, LEGS, TH_REST, Tm, fk_links, go2_q, leg_fk, rpy, stance_ik
from bookout import T, figure, style

plt = style()
h0 = -leg_fk("FL", TH_REST)[2] + GO2_FOOT_R
feet = {leg: leg_fk(leg, TH_REST) + np.array([0, 0, h0]) for leg in LEGS}


def proj(p):
    """斜二测：x 向右、y（机身左侧）向左上、z 向上；单位 m。"""
    x, y, z = p
    return np.array([x - 0.35 * y, z + 0.55 * y])


def draw_go2(ax, T_sb, th, color, alpha=1.0, lw=3.0, z=3, axes=False):
    q = go2_q(th)
    Tl = fk_links(GO2, q, T_sb)
    # 机身：四个髋点连成的矩形
    hips = [Tl[f"{l}_hip"][:3, 3] for l in ("FL", "FR", "RR", "RL")]
    P = np.array([proj(p) for p in hips + [hips[0]]])
    ax.fill(P[:, 0], P[:, 1], color=color, alpha=0.18 * alpha, zorder=z - 1, lw=0)
    ax.plot(P[:, 0], P[:, 1], color=color, lw=1.6, alpha=alpha, zorder=z)
    for l in LEGS:
        a = Tl[f"{l}_hip"][:3, 3]
        b = Tl[f"{l}_thigh"][:3, 3]
        c = Tl[f"{l}_calf"][:3, 3]
        f = (Tl[f"{l}_calf"] @ np.r_[0, 0, -0.213, 1])[:3]
        Q = np.array([proj(p) for p in (a, b, c, f)])
        ax.plot(Q[:, 0], Q[:, 1], color=color, lw=lw, alpha=alpha, zorder=z, solid_capstyle="round", solid_joinstyle="round")
        ax.plot(*Q[3], "o", ms=6, color="#3a3a3a", alpha=alpha, zorder=z + 1)
    if axes:
        o = T_sb[:3, 3]
        for k, col in enumerate((C["x"], C["y"], C["z"])):
            arrow(ax, proj(o), proj(o + 0.12 * T_sb[:3, k]), col, 1.4, 9, z=8)
    return Tl


fig, ax = plt.subplots(figsize=(9.6, 6.2))
T0 = Tm(np.eye(3), (0, 0, h0))
draw_go2(ax, T0, np.tile(TH_REST, 4), C["steel"], alpha=0.55, lw=2.2)
T1 = Tm(rpy(math.radians(8), math.radians(-12), math.radians(10)), np.array([0.03, -0.02, h0 - 0.05]))
th1 = stance_ik(T1, feet)
Tl = draw_go2(ax, T1, th1, C["thigh"], lw=3.0, z=5, axes=True)
o1 = T1[:3, 3]
ax.text(*(proj(o1) + [-0.11, 0.05]), "{b}", fontsize=12, color=C["thigh"])
for l in ("FL", "RR"):
    f = feet[l]
    arrow(ax, proj(o1), proj(f), C["orange"], 1.3, 9, z=7, ls="--")
pm = 0.25 * proj(o1) + 0.75 * proj(feet["RR"])
ax.text(pm[0] + 0.015, pm[1] - 0.005, "$p_{b,\\mathrm{RR}}$", color=C["orange"], fontsize=12)
pm = (proj(o1) + proj(feet["FL"])) / 2
ax.text(pm[0] + 0.012, pm[1] + 0.02, "$p_{b,\\mathrm{FL}}$", color=C["orange"], fontsize=12)
# 地面坐标系 {s}
os_ = np.array([-0.48, -0.34, 0.0])
for k, col, lab in ((0, C["x"], "$x_s$"), (1, C["y"], "$y_s$"), (2, C["z"], "$z_s$")):
    e = np.zeros(3)
    e[k] = 0.12
    arrow(ax, proj(os_), proj(os_ + e), col, 1.4, 9, z=8)
    ax.text(*(proj(os_ + 1.25 * e) + [-0.01, -0.01]), lab, color=col, fontsize=11)
ax.text(*(proj(os_) + [-0.06, -0.03]), "{s}", fontsize=12)
# 地面：四只脚所在的平面
G = np.array([proj(p) for p in ([0.36, 0.26, 0], [0.36, -0.26, 0], [-0.36, -0.26, 0], [-0.36, 0.26, 0], [0.36, 0.26, 0])])
ax.fill(G[:, 0], G[:, 1], color=C["fill"], zorder=0)
ax.plot(G[:, 0], G[:, 1], color=C["light"], lw=0.8, zorder=0)
for l in LEGS:
    ax.text(*(proj(feet[l]) + [0.02, -0.035]), l, fontsize=10, color=C["dark"])
ax.text(-0.62, 0.62, T("淡色：站立姿态；实色：机身横滚 8°、俯仰 −12°、偏航 10°，平移 (0.03, −0.02, −0.05) m",
                      "light: standing; solid: body rolled 8°, pitched −12°, yawed 10°, moved (0.03, −0.02, −0.05) m"),
        fontsize=9.5, color=C["muted"])
ax.text(-0.62, 0.585, T("四只脚的位置（黑点）在 {s} 中不变", "the four feet (black dots) stay put in {s}"), fontsize=9.5, color=C["muted"])
plane(ax, (-0.62, 0.62), (-0.25, 0.65))
figure(fig, "fig20_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 20.2.2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.6), gridspec_kw={"width_ratios": [1.1, 1.0]})
F = {l: leg_fk(l, TH_REST)[:2] for l in LEGS}
B = np.array([F["FL"], F["FR"], F["RR"], F["RL"], F["FL"]])
a1.plot(B[:, 0], B[:, 1], color=C["light"], lw=1.0, ls="--")
a1.add_patch(plt.Rectangle((-0.24, -0.10), 0.48, 0.20, facecolor=C["body"], edgecolor=C["dark"], lw=1.0, zorder=1))
for l in LEGS:
    on = l in ("FL", "RR")
    a1.plot(*F[l], "o", ms=11 if on else 9, color="#3a3a3a" if on else "white", mec="#3a3a3a", zorder=4)
    a1.text(F[l][0] + (0.02 if F[l][0] > 0 else -0.06), F[l][1] + (0.025 if F[l][1] > 0 else -0.045),
            l + T("（着地）" if on else "（腾空）", " (down)" if on else " (up)"), fontsize=9.5)
a1.plot([F["FL"][0] * 1.35, F["RR"][0] * 1.35], [F["FL"][1] * 1.35, F["RR"][1] * 1.35], color=C["red"], lw=1.4, zorder=3)
ang = math.atan2(F["FL"][1] - F["RR"][1], F["FL"][0] - F["RR"][0])
e = np.array([math.cos(ang), math.sin(ang)])
c = 0.5 * F["FL"]
n = np.array([-e[1], e[0]])
t = np.linspace(-2.4, 2.4, 50)
ell = np.array([c + 0.025 * math.cos(tt) * e + 0.06 * math.sin(tt) * n for tt in t])
a1.plot(ell[:, 0], ell[:, 1], color=C["red"], lw=1.2)
arrow(a1, ell[-2], ell[-1], C["red"], 1.2, 9)
a1.text(0.12, 0.25, T("绕两脚连线的转动：\n关节都不动，两脚也不动", "rotation about the line through the feet:\nno joint moves, neither foot moves"),
        fontsize=9.5, color=C["red"])
arrow(a1, (-0.33, -0.22), (-0.25, -0.22), C["x"], 1.2, 9)
arrow(a1, (-0.33, -0.22), (-0.33, -0.14), C["y"], 1.2, 9)
a1.text(-0.245, -0.235, "$x_b$", color=C["x"], fontsize=10)
a1.text(-0.355, -0.125, "$y_b$", color=C["y"], fontsize=10)
a1.set_title(T("(a) 对角两只脚着地（俯视）：秩为 5", "(a) two diagonal feet down (top view): rank 5"), fontsize=11)
plane(a1, (-0.36, 0.40), (-0.26, 0.33))
# (b) 残差：由程序 20.2.1 的同一计算重做（右后脚沿 x_s 打滑 0.05 m/s）
from _leg import Tinv, leg_jac, skew
roll, pitch, yaw = math.radians(8), math.radians(-12), math.radians(10)
T1 = Tm(rpy(roll, pitch, yaw), np.array([0.03, -0.02, h0 - 0.05]))
th1 = stance_ik(T1, feet)
pb = {l: (Tinv(T1) @ np.r_[feet[l], 1])[:3] for l in LEGS}
w_b, v_b = np.array([0.2, -0.3, 0.1]), np.array([0.05, 0.02, -0.04])
A = np.vstack([np.hstack([skew(pb[l]), -np.eye(3)]) for l in LEGS])
y = np.concatenate([skew(pb[l]) @ w_b - v_b for l in LEGS])
y[9:12] += T1[:3, :3].T @ np.array([0.05, 0, 0])
V, *_ = np.linalg.lstsq(A, y, rcond=None)
res = A @ V - y
rl = [np.linalg.norm(res[3 * k:3 * k + 3]) * 1000 for k in range(4)]
cols = [C["steel"]] * 3 + [C["red"]]
a2.bar(LEGS, rl, color=cols, width=0.55)
for k, v in enumerate(rl):
    a2.text(k, v + 0.6, f"{v:.1f}", ha="center", fontsize=10)
a2.set_ylabel(T("残差 / (mm/s)", "residual / (mm/s)"))
a2.set_ylim(0, max(rl) * 1.25)
a2.grid(axis="y", alpha=0.25)
a2.set_title(T("(b) 右后脚打滑 0.05 m/s：各腿的残差", "(b) rear-right foot slipping at 0.05 m/s: residual per leg"), fontsize=11)
fig.tight_layout()
figure(fig, "fig20_2_2")
plt.close(fig)
