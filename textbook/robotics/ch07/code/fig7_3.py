"""7.3 节的示意图。

图 7.3.1：(a) 牛顿法：沿切线走到与横轴的交点；(b) 二分法与牛顿法的误差随迭代次数的变化。
图 7.3.2：2R 臂逆运动学的牛顿迭代：从初值 (0, 1) rad 出发，各次迭代的手臂形态逐步逼近目标。
图 7.3.3：初值平面上的“吸引域”：(a) 纯牛顿法；(b) 加回溯线搜索。
"""
import math

import numpy as np
from matplotlib.colors import ListedColormap

from _ode import G, L1, L2, LINK, fk2, ik2_analytic, jac2, link_params, newton2_batch, newton2_batch_ls, wrap
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
box = dict(fc="white", ec="none", pad=1.0, alpha=0.9)


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


Jo, lc, wn2 = link_params()
mgl = LINK["mk"] * G * lc
k_s, th_s = 10.0, math.pi / 3
f = lambda t: k_s * (th_s - t) - mgl * np.cos(t)
df = lambda t: -k_s + mgl * np.sin(t)

# ---------------------------------------------------------------- 图 7.3.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw=dict(wspace=0.3))
tt = np.linspace(-0.05, 1.1, 300)
a1.plot(tt, f(tt), color=C["ink"], lw=1.6)
a1.axhline(0, color=C["muted"], lw=0.8)
t = 0.0
cols = [C["x"], C["z"], C["y"]]
for i in range(3):
    t1 = t - f(t) / df(t)
    a1.plot([t, t], [0, f(t)], color=C["muted"], lw=0.8, ls=":")
    a1.plot([t], [f(t)], "o", color=cols[i], ms=4.5, zorder=5)
    a1.plot([t, t1], [f(t), 0], color=cols[i], lw=1.3)
    a1.plot([t1], [0], "o", mfc="white", mec=cols[i], ms=5, zorder=5)
    a1.text(t, -0.55 if i != 1 else -0.9, f"$\\theta_{i}$", color=cols[i], fontsize=11, ha="center")
    t = t1
a1.text(0.5, 4.3, T("在 $\\theta_k$ 处作切线，\n它与横轴的交点就是 $\\theta_{k+1}$", "draw the tangent at $\\theta_k$;\nit meets the axis at $\\theta_{k+1}$"),
        fontsize=9.5, bbox=box)
a1.set_xlabel(T("连杆角 θ / rad", "link angle θ / rad"))
a1.set_ylabel(T("f(θ) / (N·m)", "f(θ) / (N·m)"))
a1.set_title(T("(a) 牛顿法的几何意义", "(a) Newton's method, geometrically"), fontsize=10.5)
a1.set_xlim(-0.05, 1.1)
clean(a1)
from scipy.optimize import brentq
root = brentq(lambda x: float(f(x)), 0, th_s, xtol=1e-15)
a, b = 0.0, th_s
eb = []
while b - a > 1e-14 and len(eb) < 46:
    c = (a + b) / 2
    a, b = (a, c) if f(a) * f(c) <= 0 else (c, b)
    eb.append(abs((a + b) / 2 - root))
t, en = 0.0, [abs(root)]
for _ in range(5):
    t = t - f(t) / df(t)
    en.append(max(abs(t - root), 1e-17))
a2.semilogy(range(1, len(eb) + 1), eb, "o-", color=C["muted"], ms=3, lw=1.0, label=T("二分法", "bisection"))
a2.semilogy(range(len(en)), en, "s-", color=C["x"], ms=4.5, lw=1.4, label=T("牛顿法", "Newton's method"))
a2.axhline(1e-15, color=C["muted"], lw=0.6, ls="--")
a2.text(46, 2.5e-17, T("双精度的舍入误差", "double-precision round-off"), fontsize=8.5, color=C["muted"], ha="right")
a2.set_xlabel(T("迭代次数 k", "iteration k"))
a2.set_ylabel(T("误差 |θ_k − θ*| / rad", "error |θ_k − θ*| / rad").replace("θ_k", "$\\theta_k$").replace("θ*", "$\\theta^*$"))
a2.set_title(T("(b) 误差随迭代的变化", "(b) error versus iteration"), fontsize=10.5)
a2.set_ylim(1e-17, 3)
a2.legend(frameon=False, fontsize=9.5)
a2.grid(True, which="major", lw=0.3, alpha=0.5)
clean(a2)
figure(fig, "fig7_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.3.2
p_d = np.array([0.45, 0.35])
th = np.array([0.0, 1.0])
hist = [th.copy()]
for _ in range(4):
    th = th - np.linalg.solve(jac2(th), fk2(th) - p_d)
    hist.append(th.copy())
fig, ax = plt.subplots(figsize=(5.6, 4.6))
ax.set_aspect("equal")
reach = L1 + L2
ang = np.linspace(0, 2 * math.pi, 300)
ax.plot(reach * np.cos(ang), reach * np.sin(ang), color=C["muted"], lw=0.7, ls="--")
ax.text(-0.62, 0.57, T("够得着的边界", "edge of reach"), fontsize=9, color=C["muted"])
alphas = [0.35, 0.5, 0.7, 0.85, 1.0]
cmap = [C["muted"], "#e67e22", C["y"], C["z"], C["x"]]
for i, (thk, al) in enumerate(zip(hist, alphas)):
    p1 = np.array([L1 * math.cos(thk[0]), L1 * math.sin(thk[0])])
    p2 = fk2(thk)
    ax.plot([0, p1[0], p2[0]], [0, p1[1], p2[1]], color=cmap[i], lw=3.5 if i == 4 else 2.2, alpha=al, solid_capstyle="round")
    ax.plot([p1[0]], [p1[1]], "o", color=cmap[i], ms=4, alpha=al)
    ax.plot([p2[0]], [p2[1]], "o", color=cmap[i], ms=4)
    ax.plot([], [], color=cmap[i], lw=2.2, label=T(f"第 {i} 次迭代", f"iteration {i}") if i < 4 else T("第 4 次：已到达目标", "iteration 4: on target"))
ax.plot([p_d[0]], [p_d[1]], marker="*", color=C["x"], ms=14, zorder=6)
ax.text(p_d[0] - 0.05, p_d[1] + 0.06, T("目标 $p_d$", "target $p_d$"), fontsize=10, color=C["x"], ha="right", bbox=box)
ax.legend(loc="upper right", frameon=False, fontsize=9)
ax.plot([0], [0], "s", color=C["ink"], ms=7)
ax.set_xlim(-0.7, 1.15)
ax.set_ylim(-0.25, 0.9)
ax.set_xlabel("x / m")
ax.set_ylabel("y / m")
clean(ax)
figure(fig, "fig7_3_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.3.3
N = 241
g = np.linspace(-math.pi, math.pi, N)
T1, T2 = np.meshgrid(g, g)
th0 = np.column_stack([T1.ravel(), T2.ravel()])
cm = ListedColormap(["#d9d9d9", "#9ecae1", "#fdae6b"])
fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.4), gridspec_kw=dict(wspace=0.25))
sols = ik2_analytic(p_d)
for ax, fn, title in ((axs[0], newton2_batch, T("(a) 纯牛顿法", "(a) plain Newton")),
                      (axs[1], newton2_batch_ls, T("(b) 加回溯线搜索", "(b) with backtracking line search"))):
    thf, ok, _ = fn(th0, p_d)
    cls = np.where(~ok, 0, np.where(wrap(thf[:, 1]) > 0, 1, 2)).reshape(N, N)
    ax.imshow(cls, origin="lower", extent=[-math.pi, math.pi, -math.pi, math.pi], cmap=cm, vmin=0, vmax=2,
              interpolation="nearest", aspect="equal")
    for s_, mk in zip(sols, ("^", "v")):
        ax.plot([s_[0]], [s_[1]], marker=mk, color=C["ink"], ms=8, mec="white")
    ax.set_title(title, fontsize=10.5)
    ax.set_xlabel(r"$\theta_1^{(0)}$ / rad")
    ax.set_xticks([-math.pi, 0, math.pi])
    ax.set_xticklabels([r"$-\pi$", "0", r"$\pi$"])
    ax.set_yticks([-math.pi, 0, math.pi])
    ax.set_yticklabels([r"$-\pi$", "0", r"$\pi$"])
axs[0].set_ylabel(r"$\theta_2^{(0)}$ / rad")
from matplotlib.patches import Patch
handles = [Patch(color="#9ecae1", label=T("收敛到 θ₂ > 0 的解（▲）", "converges to the θ₂ > 0 solution (▲)")),
           Patch(color="#fdae6b", label=T("收敛到 θ₂ < 0 的解（▼）", "converges to the θ₂ < 0 solution (▼)")),
           Patch(color="#d9d9d9", label=T("40 步内不收敛", "no convergence in 40 steps"))]
fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, -0.1))
figure(fig, "fig7_3_3")
plt.close(fig)
