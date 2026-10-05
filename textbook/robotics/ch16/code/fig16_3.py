"""16.3 节的示意图。

图 16.3.1：平面 2R 臂的奇异：(a) θ = (30°, 0) 伸直：末端只能沿切向运动（可达方向），沿手臂的径向运动失去，
           沿手臂的力 F 不需要关节力矩；零空间的关节运动 θ̇ ∝ (1, −2.084) 使末端瞬时不动；
           (b) 末端沿径向以 0.1 m/s 运动所需的关节速度与 J 的最小奇异值随 θ₂ 的变化。
图 16.3.2：UR5e 的三类奇异位形（算例 16.3.2）：肘部奇异（θ₃ = 0），手腕奇异（θ₅ = 0，轴 2、3、4、6 平行），
           肩部奇异（手腕点在过基座轴线、垂直于手臂平面的竖直平面内）；画出关节轴和由结构承受的力。
图 16.3.3：接近奇异时 J 的最小奇异值与三个因子 |sin θ₃|、|sin θ₅|、|r| 成正比（对数坐标）。
"""
import math

import numpy as np

from _fig16 import C, arm_pts, arrow2, axes3d, base_mark, draw_arm, draw_chain, equal3d, floor3d, logaxis, plane, ur_chain
from _jac import (D4, L1, L2, TH_STAR, UR_Q, UR_S, UR_W, act, exp6, jac_2r, rotz, svals, ur_js, ur_shoulder_r, ur_wrist_point)
from bookout import T, figure, style

plt = style()
LL = (0.425, 0.392)

# ---------------------------------------------------------------- 图 16.3.1
fig, axs = plt.subplots(1, 2, figsize=(11.4, 4.4), gridspec_kw={"width_ratios": [1.15, 1.0]})
ax = axs[0]
plane(ax, (-0.12, 0.98), (-0.12, 0.62))
th = np.radians([30, 0])
pts = arm_pts(th, LL)
base_mark(ax)
draw_arm(ax, pts, C["z"], lw=6)
p = pts[-1]
u = np.array([math.cos(th[0]), math.sin(th[0])])
n = np.array([-u[1], u[0]])
arrow2(ax, p - 0.13 * n, p + 0.13 * n, C["y"], lw=2.0)
arrow2(ax, p + 0.13 * n, p - 0.13 * n, C["y"], lw=2.0)
ax.text(*(p + 0.15 * n + np.array([-0.06, 0.01])), T("能动：切向", "can move: tangential"), fontsize=9.5, color=C["y"])
ax.plot(*np.array([p - 0.12 * u, p + 0.14 * u]).T, color=C["x"], lw=1.6, ls="--")
ax.text(*(p + 0.16 * u + np.array([0.0, 0.02])), T("失去：径向", "lost: radial"), fontsize=9.5, color=C["x"])
arrow2(ax, p + 0.02 * u, p + 0.12 * u + 0.0 * n, C["accent"], lw=2.4, ms=13)
ax.text(*(p + 0.10 * u - 0.12 * n), T("力 F 沿手臂：", "force F along the arm: ") + r"$\tau = J^{T}F = 0$", fontsize=9.5, color=C["accent"])
for k, (c, txt) in enumerate(((C["x"], "+1"), (C["muted"], "−2.08"))):
    q = pts[k]
    t0 = th[0] + (0 if k == 0 else th[1])
    a0, a1 = (t0 + 0.6, t0 + 1.5) if k == 0 else (t0 - 0.6, t0 - 1.5)
    tt = np.linspace(a0, a1, 30)
    rr = 0.07
    ax.plot(q[0] + rr * np.cos(tt), q[1] + rr * np.sin(tt), color=C["ink"], lw=1.0)
    end = q + rr * np.array([math.cos(a1), math.sin(a1)])
    d = np.sign(a1 - a0) * np.array([-math.sin(a1), math.cos(a1)])
    ax.annotate("", xy=end + 0.003 * d, xytext=end - 0.02 * d, arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=1.0, mutation_scale=8))
ax.text(-0.10, 0.11, r"$\dot\theta_1 = 1$", fontsize=10)
ax.text(pts[1][0] - 0.06, pts[1][1] - 0.13, r"$\dot\theta_2 = -2.08$", fontsize=10)
ax.text(-0.10, 0.59, T("(a) 2R 臂伸直：θ = (30°, 0)", "(a) 2R arm straight: θ = (30°, 0)"), fontsize=10.5)
ax.text(-0.10, 0.54, T("零空间：", "null space: ") + r"$\dot\theta \propto (1, -2.08)$" + T(" 时末端瞬时不动", " leaves the tip still"), fontsize=9, color=C["muted"])
ax = axs[1]
t2 = np.radians(np.logspace(-1, np.log10(60), 200))
need, smin = [], []
for x in t2:
    Jt = jac_2r([th[0], x], LL)
    pp = np.array([LL[0] * math.cos(th[0]) + LL[1] * math.cos(th[0] + x), LL[0] * math.sin(th[0]) + LL[1] * math.sin(th[0] + x)])
    need.append(np.linalg.norm(np.degrees(np.linalg.solve(Jt, 0.1 * pp / np.linalg.norm(pp)))))
    smin.append(svals(Jt)[-1])
ax.plot(np.degrees(t2), need, color=C["x"], lw=1.8, label=T("径向 0.1 m/s 所需关节速度 ", "joint speed for 0.1 m/s radially ") + r"$\|\dot\theta\|$" + " / (°/s)")
ax.plot(np.degrees(t2), np.array(smin) * 1000, color=C["z"], lw=1.8, label=T("J 的最小奇异值 σ₂ × 1000 / m", "smallest singular value σ₂ × 1000 / m"))
ax.axhline(180, color=C["muted"], lw=0.8, ls=":")
ax.text(0.12, 200, T("UR5e 关节速度上限 180°/s", "UR5e joint speed limit 180°/s"), fontsize=8.5, color=C["muted"])
ax.set_xscale("log")
logaxis(ax)
ax.set_xlabel(T("θ₂ / (°)（离伸直的角度）", "θ₂ / (°) (angle from straight)"))
ax.legend(fontsize=8.6, frameon=False, loc="upper right")
ax.set_ylim(1, 3e4)
ax.set_title(T("(b) 接近奇异：所需关节速度 ∝ 1/sin θ₂", "(b) Near the singularity: joint speed ∝ 1/sin θ₂"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig16_3_1")
plt.close(fig)


# ---------------------------------------------------------------- 图 16.3.2
def bisect(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = (a + b) / 2
        if fa * f(m) <= 0:
            b = m
        else:
            a, fa = m, f(m)
    return (a + b) / 2


q_el = TH_STAR.copy()
q_el[2] = 0.0
q_wr = TH_STAR.copy()
q_wr[4] = 0.0
q_sh = TH_STAR.copy()
q_sh[1] = bisect(lambda t: ur_shoulder_r(np.r_[TH_STAR[0], t, TH_STAR[2:]]), math.radians(-170), math.radians(-100))


def axes_now(q):
    E, out = np.eye(4), []
    for i in range(6):
        out.append((E[:3, :3] @ UR_W[i], act(E, UR_Q[i])))
        E = E @ exp6(UR_S[i], q[i])
    return out


fig = plt.figure(figsize=(12.6, 4.6))
titles = (T("(a) 肘部奇异：θ₃ = 0，大臂与小臂成一直线", "(a) Elbow: θ₃ = 0, upper arm and forearm in line"),
          T("(b) 手腕奇异：θ₅ = 0，轴 2、3、4、6 平行", "(b) Wrist: θ₅ = 0, axes 2, 3, 4, 6 parallel"),
          T("(c) 肩部奇异：手腕点在过基座轴线的平面内", "(c) Shoulder: wrist point in the plane through the base axis"))
for k, q in enumerate((q_el, q_wr, q_sh)):
    _, ax = axes3d(plt, fig=fig, pos=131 + k, elev=16, azim=12)
    P = ur_chain(q)
    draw_chain(ax, P, "#9aa6ad", lw=5, js=9)
    ax.plot([0, 0], [0, 0], [-0.05, 1.05], color=C["muted"], lw=0.9, ls=":")
    A = axes_now(q)
    show = {0: [1, 2, 3], 1: [1, 2, 3, 5], 2: [0, 4, 5]}[k]
    for i in show:
        w, c = A[i]
        ax.quiver(*(c - 0.08 * w), *(0.2 * w), color=C["accent"], lw=1.8, arrow_length_ratio=0.25)
        ax.text(*(c + 0.14 * w + np.array([0, 0, 0.03])), f"{i + 1}", fontsize=10, color=C["accent"], weight="bold")
    pw = ur_wrist_point(q)
    ax.scatter(*pw, s=22, color=C["x"], depthshade=False)
    y1 = rotz(q[0]) @ np.array([0, -1.0, 0])
    if k == 2:
        L = np.array([pw - 0.25 * y1, pw + 0.45 * y1])
        ax.plot(*L.T, color=C["x"], lw=1.8)
        ax.quiver(*(pw + 0.15 * y1), *(0.2 * y1), color=C["x"], lw=2.0, arrow_length_ratio=0.3)
        ax.scatter(0, 0, pw[2], s=18, color=C["x"], depthshade=False)
        ax.text(*(pw + 0.3 * y1 + np.array([0, 0, 0.21])), T("力 F：经过手腕点和基座轴线", "force F: through the wrist point\nand the base axis"), fontsize=8.5, color=C["x"])
    if k == 1:
        w5, c5 = A[4]
        L5 = np.array([c5 - 0.75 * w5, c5 + 0.25 * w5])
        ax.plot(*L5.T, color=C["accent"], lw=1.0, ls="--")
        ax.text(*(c5 - 0.95 * w5 + np.array([0, 0, -0.07])), T("轴 5 的延长线", "axis 5 extended"), fontsize=8.5, color=C["accent"])
        c0 = np.array([0, 0, pw[2]])
        hit = c0 + D4 * y1
        ax.scatter(*hit, s=18, color=C["x"], depthshade=False)
        ax.scatter(*c0, s=18, color=C["x"], depthshade=False)
        L = np.array([c0 - 0.3 * y1, c0 + 0.9 * y1])
        ax.plot(*L.T, color=C["x"], lw=1.8)
        ax.text(*(c0 + 0.9 * y1 + np.array([0, 0, 0.04])), T("力 F ∥ 轴 2、3、4、6", "force F ∥ axes 2, 3, 4, 6"), fontsize=8.5, color=C["x"])
    if k == 0:
        ax.text(*(P[4] + np.array([0, 0, 0.08])), T("轴 2 到轴 4 的距离 = L₁ + L₂（最大）", "distance from axis 2 to axis 4 = L₁ + L₂ (maximum)"), fontsize=8.5, color=C["x"])
    floor3d(ax, half=0.5)
    equal3d(ax, np.vstack([P, [[0.4, 0.4, 0], [-0.6, -0.6, 0], [0, 0, 1.0]]]), pad=0.0, zoom=1.35)
    ax.text2D(0.0, 0.97, titles[k], transform=ax.transAxes, fontsize=9.8)
fig.tight_layout()
figure(fig, "fig16_3_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 16.3.3
fig, ax = plt.subplots(figsize=(6.6, 4.2))
es = np.logspace(-4, -0.3, 30)
x1, y1_, x2, y2, x3, y3 = [], [], [], [], [], []
for e in es:
    q = TH_STAR.copy()
    q[2] = e
    x1.append(abs(math.sin(e)))
    y1_.append(svals(ur_js(q))[-1])
    q = TH_STAR.copy()
    q[4] = e
    x2.append(abs(math.sin(e)))
    y2.append(svals(ur_js(q))[-1])
    q = q_sh.copy()
    q[1] += e
    x3.append(abs(ur_shoulder_r(q)) / 0.1)
    y3.append(svals(ur_js(q))[-1])
ax.plot(x1, y1_, color=C["z"], lw=1.8, marker="o", ms=3, label=T("肘部：横轴 |sin θ₃|", "elbow: |sin θ₃| on the axis"))
ax.plot(x2, y2, color=C["accent"], lw=1.8, marker="s", ms=3, label=T("手腕：横轴 |sin θ₅|", "wrist: |sin θ₅| on the axis"))
ax.plot(x3, y3, color=C["x"], lw=1.8, marker="^", ms=3, label=T("肩部：横轴 |r| / (0.1 m)", "shoulder: |r| / (0.1 m) on the axis"))
ax.plot([1e-4, 1], [1e-4 * 0.5, 0.5], color=C["muted"], lw=0.8, ls=":")
ax.text(2e-3, 3e-3, T("斜率 1", "slope 1"), fontsize=9, color=C["muted"])
ax.set_xscale("log")
logaxis(ax)
ax.set_xlabel(T("离奇异的程度（各自的因子）", "distance from the singularity (its own factor)"))
ax.set_ylabel(T("J$_s$ 的最小奇异值", "smallest singular value of J$_s$"))
ax.legend(fontsize=8.8, frameon=False, loc="upper left")
fig.tight_layout()
figure(fig, "fig16_3_3")
plt.close(fig)
