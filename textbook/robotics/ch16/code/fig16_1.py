"""16.1 节的示意图。

图 16.1.1：(a) 平面 3R 臂（UR5e 侧视尺寸）：末端速度是各关节贡献 θ̇_i ẑ × (p − p_i) 之和（首尾相接）；
           (b) UR5e 在 θ* 时六根关节轴此刻的位置（J_s 的六列）、基座坐标系与法兰盘坐标系。
图 16.1.2：算例 16.1.2 的三种点动：(a) 俯视的法兰盘中心路径；(b) 沿 x_s 直线点动时六个关节的转速。
"""
import math

import numpy as np

from _fig16 import C, arrow2, axes3d, base_mark, draw_arm, draw_chain, equal3d, floor3d, frame2d, plane
from _fig16 import arm_pts, ur_chain
from _jac import PL, TH_STAR, UR_B, UR_Q, UR_S, UR_W, act, exp6, jacobian_body, jacobian_space, ur_fk
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 16.1.1
fig = plt.figure(figsize=(11.6, 4.9))
ax = fig.add_subplot(121)
th = np.radians([35, -50, -60])
dth = np.radians([25, 35, 50])
pts = arm_pts(th, PL)
p = pts[-1]
plane(ax, (-0.08, 1.05), (-0.1, 0.72))
base_mark(ax)
draw_arm(ax, pts, C["z"], lw=6)
cols = [C["x"], C["y"], C["accent"]]
cur = p.copy()
for i in range(3):
    d = p - pts[i]
    v = dth[i] * np.array([-d[1], d[0]])
    arrow2(ax, cur, cur + v, cols[i], lw=1.8, ms=12)
    mid = cur + v / 2
    lab = r"$\dot\theta_%d\,\hat z\times(p - p_%d)$" % (i + 1, i + 1)
    at = (mid + np.array([0.075, 0.0])) if i < 2 else (cur + v + np.array([0.03, -0.01]))
    ax.text(at[0], at[1], T(f"关节 {i + 1}：", f"joint {i + 1}: ") + lab, fontsize=9.5, color=cols[i], va="center")
    cur = cur + v
    ax.plot(*pts[i], "o", ms=6, mfc="white", mec=cols[i], mew=1.6, zorder=8)
    ax.text(pts[i][0] + (-0.075 if i == 2 else -0.02), pts[i][1] + (-0.01 if i == 2 else -0.065), f"$p_{i + 1}$", fontsize=11, color=cols[i])
arrow2(ax, p, cur, C["ink"], lw=2.2, ms=14)
ax.text(cur[0] - 0.36, cur[1] - 0.01, T("末端速度 $\\dot p$（三者之和）", "tip velocity $\\dot p$ (the sum)"), fontsize=10, color=C["ink"], ha="left")
ax.text(p[0] + 0.02, p[1] - 0.05, "$p$", fontsize=12, color=C["ink"])
ax.text(-0.07, 0.69, T("(a) 平面 3R 臂：各关节的贡献首尾相接", "(a) Planar 3R arm: joint contributions head to tail"), fontsize=10.5)
ax.text(-0.07, 0.64, "θ = (35°, −50°, −60°),   " + r"$\dot\theta$" + " = (25, 35, 50) °/s", fontsize=10, color=C["muted"])

_, ax = axes3d(plt, fig=fig, pos=122, elev=18, azim=-125)
th = TH_STAR
Pc = ur_chain(th)
draw_chain(ax, Pc, "#9aa6ad", lw=6, js=10)
E = np.eye(4)
allp = [Pc]
for i in range(6):
    w = E[:3, :3] @ UR_W[i]
    q = act(E, UR_Q[i])
    ax.quiver(*(q - 0.07 * w), *(0.2 * w), color=C["accent"], lw=2.0, arrow_length_ratio=0.25)
    ax.scatter(*q, color=C["ink"], s=12, depthshade=False)
    off = {0: (0.03, 0.0, 0.03), 1: (0.0, 0.03, 0.05), 2: (0.0, 0.0, 0.05), 3: (-0.12, 0.0, 0.1), 4: (0.14, 0.1, -0.02), 5: (0.03, -0.02, -0.07)}[i]
    ax.text(*(q + 0.13 * w + np.array(off)), T(f"轴{i + 1}", f"axis {i + 1}"), fontsize=9.5, color=C["accent"], weight="bold")
    allp.append([q + 0.13 * w])
    E = E @ exp6(UR_S[i], th[i])
Tb = ur_fk(th)
for k, c in enumerate((C["x"], C["y"], C["z"])):
    ax.quiver(*Tb[:3, 3], *(0.12 * Tb[:3, k]), color=c, lw=1.6, arrow_length_ratio=0.25)
    ax.quiver(0, 0, 0, *(0.15 * np.eye(3)[k]), color=c, lw=1.6, arrow_length_ratio=0.25)
ax.text(*(Tb[:3, 3] + np.array([0.0, 0.12, -0.02])), "{b}", fontsize=10)
ax.text(0.03, -0.06, -0.06, "{s}", fontsize=10)
floor3d(ax, half=0.55)
equal3d(ax, np.vstack(allp + [[[0.2, 0.2, 0], [-0.6, -0.6, 0]]]), pad=0.0, zoom=1.45)
ax.text2D(0.0, 0.97, T("(b) UR5e，θ = θ*：J$_s$ 的第 i 列是轴 i 此刻的位置", "(b) UR5e at θ*: column i of J$_s$ is axis i where it is now"),
          transform=ax.transAxes, fontsize=10.5)
fig.tight_layout()
figure(fig, "fig16_1_1")
plt.close(fig)


# ---------------------------------------------------------------- 图 16.1.2
def rk4(f, y, dt):
    k1 = f(y)
    k2 = f(y + dt / 2 * k1)
    k3 = f(y + dt / 2 * k2)
    k4 = f(y + dt * k3)
    return y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def run(V, frame, dur=3.0, dt=2e-3):
    J = (lambda q: jacobian_space(UR_S, q)) if frame == "s" else (lambda q: jacobian_body(UR_B, q))
    f = lambda q: np.linalg.solve(J(q), V)
    q = TH_STAR.copy()
    P, S = [ur_fk(q)[:3, 3]], [f(q)]
    for _ in range(int(round(dur / dt))):
        q = rk4(f, q, dt)
        P.append(ur_fk(q)[:3, 3])
        S.append(f(q))
    return np.array(P), np.degrees(np.array(S))


om = math.radians(10)
Pa, Sa = run(np.r_[0, 0, 0, 0.05, 0, 0], "s")
Pb, _ = run(np.r_[0, 0, om, 0, 0, 0], "b")
Pc, _ = run(np.r_[0, 0, om, 0, 0, 0], "s", dur=36.0, dt=0.02)
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.3), gridspec_kw={"width_ratios": [1.0, 1.15]})
ax = axs[0]
ax.set_aspect("equal")
ax.plot(Pc[:, 0], Pc[:, 1], color=C["x"], lw=1.3, ls="--", label=T("(c) 误写 V$_s$ = (0, 0, ω, 0, 0, 0)：绕基座轴线画圆", "(c) wrong V$_s$ = (0, 0, ω, 0, 0, 0): a circle about the base axis"))
ax.plot(Pc[:151, 0], Pc[:151, 1], color=C["x"], lw=2.6)
ax.plot(Pa[:, 0], Pa[:, 1], color=C["z"], lw=2.6, label=T("(a) 基座坐标系沿 x$_s$ 平移 3 s", "(a) base-frame jog along x$_s$ for 3 s"))
ax.plot(*Pb[0, :2], "o", color=C["accent"], ms=8, label=T("(b) 工具坐标系绕 z$_b$ 转：法兰盘中心不动", "(b) tool-frame turn about z$_b$: flange centre stays"))
Pk = ur_chain(TH_STAR)
ax.plot(Pk[:, 0], Pk[:, 1], color="#9aa6ad", lw=5, solid_capstyle="round", zorder=0)
ax.plot(0, 0, "s", color=C["muted"], ms=8)
ax.text(0.02, 0.03, T("基座轴线", "base axis"), fontsize=9, color=C["muted"])
ax.annotate("", xy=(0.03, 0.0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.2))
ax.set_xlim(-0.85, 0.85)
ax.set_ylim(-0.8, 0.8)
ax.set_xlabel("x / m")
ax.set_ylabel("y / m")
ax.legend(fontsize=8.2, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=1)
ax.set_title(T("(a) 法兰盘中心的路径（俯视）", "(a) Path of the flange centre (top view)"), fontsize=10.5, loc="left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax = axs[1]
t = np.arange(len(Sa)) * 2e-3
for i, c in enumerate((C["x"], C["y"], C["z"], C["accent"], C["muted"], "#6baed6")):
    ax.plot(t, Sa[:, i], color=c, lw=1.6, ls="-" if i != 5 else "--", label=T(f"关节 {i + 1}", f"joint {i + 1}"))
ax.axhline(0, color=C["muted"], lw=0.6)
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("关节转速 / (°/s)", "joint speed / (°/s)"))
ax.legend(fontsize=8.5, frameon=False, ncol=3, loc="upper left")
ax.set_ylim(-11, 11)
ax.set_title(T("(b) 沿 x$_s$ 以 50 mm/s 点动时的关节转速", "(b) Joint speeds for the 50 mm/s jog along x$_s$"), fontsize=10.5, loc="left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
figure(fig, "fig16_1_2")
plt.close(fig)
