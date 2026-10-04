"""2.3 节的计算：

算例 2.3.1  AGV 的路线分三段：12.0 m 朝 0°（正东），8.0 m 朝 60°，5.0 m 朝 160°（角度从 x 轴逆时针量）。用分量求
            总位移的大小和方向（图 2.3.2）；并说明为什么方向角要用 atan2 而不是 arctan。
算例 2.3.2  载货 AGV 总质量 500 kg，停在倾角 5° 的坡道上。重力在“水平—竖直”坐标系中的分量是 (0, −mg)；
            在“沿坡—垂直坡面”坐标系中是多少？用坐标系旋转的公式计算，并核对两组分量算出的大小相同（图 2.3.3）。
算例 2.3.3  四旋翼从起飞点飞到 (30, −20, 15) m（x 东、y 北、z 上）。求位移的大小、方向余弦和仰角。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

rad, deg = math.radians, math.degrees
# ---- 算例 2.3.1
legs = [(12.0, 0.0), (8.0, 60.0), (5.0, 160.0)]
comp = [(L * math.cos(rad(t)), L * math.sin(rad(t))) for L, t in legs]
Rx_, Ry_ = sum(c[0] for c in comp), sum(c[1] for c in comp)
Rm = math.hypot(Rx_, Ry_)
Ra = deg(math.atan2(Ry_, Rx_))
rows = "；".join(f"第 {i + 1} 段 ({c[0]:.2f}, {c[1]:.2f}) m" for i, c in enumerate(comp))
# atan2 与 arctan 的区别：反方向的位移
back_atan = deg(math.atan(-Ry_ / -Rx_))
back_atan2 = deg(math.atan2(-Ry_, -Rx_))
out(c1x=comp[0][0], c1y=comp[0][1], c2x=comp[1][0], c2y=comp[1][1], c3x=comp[2][0], c3y=comp[2][1],
    Rx=Rx_, Ry=Ry_, Rm=Rm, Ra=Ra, back_atan=back_atan, back_atan2=back_atan2)

# ---- 算例 2.3.2：同一个重力，两套坐标
m, alpha = 500.0, 5.0
W = np.array([0.0, -m * g])
ca, sa = math.cos(rad(alpha)), math.sin(rad(alpha))
# 新坐标轴 x' 沿坡向上、y' 垂直坡面向上，由 x、y 轴逆时针转过 α 得到：
# 分量变换  x' = x cos α + y sin α，  y' = −x sin α + y cos α
Wp = np.array([W[0] * ca + W[1] * sa, -W[0] * sa + W[1] * ca])
assert abs(np.linalg.norm(W) - np.linalg.norm(Wp)) < 1e-9
grade = 100 * math.tan(rad(alpha))
out(m=m, alpha=alpha, W=m * g, Wxp=Wp[0], Wyp=Wp[1], Wpar=-Wp[0], grade=grade)

# ---- 算例 2.3.3：三维位移、方向余弦
D = np.array([30.0, -20.0, 15.0])
Dm = float(np.linalg.norm(D))
cosa = D / Dm
elev = deg(math.asin(D[2] / Dm))
angs = [deg(math.acos(c)) for c in cosa]
assert abs(sum(cosa ** 2) - 1) < 1e-12
out(Dm=Dm, ca=cosa[0], cb=cosa[1], cg=cosa[2], aa=angs[0], ab=angs[1], ag=angs[2], elev=elev, horiz=math.hypot(D[0], D[1]))

plt = style()
# ---- 图 2.3.1：分量与单位矢量（平面与空间）
fig = plt.figure(figsize=(7.4, 3.3))
ax = fig.add_subplot(1, 2, 1)
A = np.array([3.0, 2.0])
ax.plot([0, A[0]], [A[1], A[1]], color=d.MUTED, lw=0.8, ls="--"); ax.plot([A[0], A[0]], [0, A[1]], color=d.MUTED, lw=0.8, ls="--")
d.arrow(ax, (0, 0), (A[0], 0), d.X_, lw=1.6, label=r"$A_x\boldsymbol{i}$", off=(0, -0.3))
d.arrow(ax, (0, 0), (0, A[1]), d.Y_, lw=1.6, label=r"$A_y\boldsymbol{j}$", off=(-0.45, 0))
d.arrow(ax, (0, 0), A, d.VR, label=r"$\boldsymbol{A}$", off=(-0.15, 0.3))
d.arrow(ax, (0, 0), (1, 0), d.INK, lw=2.6, ms=10); d.arrow(ax, (0, 0), (0, 1), d.INK, lw=2.6, ms=10)
ax.text(0.9, 0.18, r"$\boldsymbol{i}$", fontsize=11); ax.text(0.12, 0.85, r"$\boldsymbol{j}$", fontsize=11)
from matplotlib.patches import Arc
ax.add_patch(Arc((0, 0), 2.8, 2.8, theta1=0, theta2=math.degrees(math.atan2(2, 3)), color=d.MUTED, lw=1))
ax.text(1.55, 0.35, r"$\theta$", fontsize=11, color=d.MUTED)
ax.set_xlim(-0.8, 3.8); ax.set_ylim(-0.6, 2.8); ax.set_aspect("equal"); ax.set_xlabel("x"); ax.set_ylabel("y"); d.spines(ax)
ax.set_title(T("平面", "plane") + r"：$\boldsymbol{A}=A_x\boldsymbol{i}+A_y\boldsymbol{j}$", fontsize=9)
ax = fig.add_subplot(1, 2, 2, projection="3d")
B = np.array([2.0, 3.0, 2.2])
for v, c, n in ((np.array([4, 0, 0]), d.X_, "x"), (np.array([0, 4, 0]), d.Y_, "y"), (np.array([0, 0, 3]), d.Z_, "z")):
    ax.quiver(0, 0, 0, *v, color=c, lw=1, arrow_length_ratio=0.06); ax.text(*(v * 1.06), n, color=c)
ax.quiver(0, 0, 0, *B, color=d.VR, lw=2.2, arrow_length_ratio=0.1)
ax.text(*(B * 1.05), r"$\boldsymbol{A}$", color=d.VR, fontsize=12)
for P, Q in (((B[0], 0, 0), (B[0], B[1], 0)), ((0, B[1], 0), (B[0], B[1], 0)), ((B[0], B[1], 0), tuple(B))):
    ax.plot(*zip(P, Q), color=d.MUTED, lw=0.8, ls="--")
for v, n in ((np.array([1, 0, 0]), "i"), (np.array([0, 1, 0]), "j"), (np.array([0, 0, 1]), "k")):
    ax.quiver(0, 0, 0, *v, color=d.INK, lw=2.2, arrow_length_ratio=0.3)
    ax.text(*(v * 1.15 + np.array([0.15, -0.25, 0.0]) * (n == "j") + np.array([0, 0, 0.05])), rf"$\boldsymbol{{{n}}}$", fontsize=11)
ax.set_xlim(0, 4); ax.set_ylim(0, 4); ax.set_zlim(0, 3)
ax.view_init(elev=20, azim=-55); ax.set_axis_off(); ax.set_box_aspect((1, 1, 0.75))
ax.set_title(T("空间", "space") + r"：$\boldsymbol{A}=A_x\boldsymbol{i}+A_y\boldsymbol{j}+A_z\boldsymbol{k}$", fontsize=9)
figure(fig, "fig2_3_1")

# ---- 图 2.3.2：三段路线的分量相加
fig, ax = plt.subplots(figsize=(5.4, 3.4))
p = np.zeros(2)
cols = [d.VA, d.VB, "#8e44ad"]
for i, c in enumerate(comp):
    q = p + np.array(c)
    d.arrow(ax, p, q, cols[i], label=f"{legs[i][0]:.0f} m, {legs[i][1]:.0f}°", off=[(0, 0.6), (1.4, -0.3), (0.3, 0.6)][i], fs=9)
    p = q
d.arrow(ax, (0, 0), p, d.VR, lw=2.4, label=r"$\Delta\boldsymbol{r}$", off=(0.3, -0.7))
ax.plot([0, p[0]], [p[1], p[1]], color=d.MUTED, lw=0.8, ls=":"); ax.plot([p[0], p[0]], [0, p[1]], color=d.MUTED, lw=0.8, ls=":")
ax.text(p[0] / 2, -0.9, rf"$\Delta x$ = {Rx_:.2f} m", ha="center", fontsize=9, color=d.MUTED)
ax.text(p[0] - 0.3, p[1] / 2, rf"$\Delta y$ = {Ry_:.2f} m", fontsize=9, color=d.MUTED, ha="right")
ax.set_xlim(-1, 19); ax.set_ylim(-1.5, 10); ax.set_xticks(range(0, 19, 3)); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig2_3_2")

# ---- 图 2.3.3：同一个重力，两套坐标（动画 2.3.1 的静态图）
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.5))
s_ = 1.0 / (m * g) * 1.9
w = W * s_
th = rad(alpha) * 4          # 示意图中把坡度放大 4 倍，便于看清
ex, ey = np.array([math.cos(th), math.sin(th)]), np.array([-math.sin(th), math.cos(th)])
for k, ax in enumerate(axs):
    base = -0.35 * ey                                  # 坡面经过车底
    xs = np.array([-2.7, 2.7])
    ys = base[1] + (xs - base[0]) * math.tan(th)
    ax.fill([xs[0], xs[1], xs[1], xs[0]], [ys[0], ys[1], -2.4, -2.4], color="#e6eaec", zorder=0)
    corners = [(-0.6, -0.35), (0.6, -0.35), (0.6, 0.3), (-0.6, 0.3)]
    ax.fill(*zip(*[tuple(c[0] * ex + c[1] * ey) for c in corners]), color="#c8d0d4", ec=d.INK, lw=0.8, zorder=1)
    ax.text(2.6, -2.25, T("坡度在图中放大了", "slope exaggerated"), ha="right", fontsize=8, color=d.MUTED)
    if k == 0:
        d.arrow(ax, (0, 0), (2.0, 0), d.X_, lw=1.2); ax.text(2.1, -0.05, "x", color=d.X_)
        d.arrow(ax, (0, 0), (0, 1.5), d.Y_, lw=1.2); ax.text(0.08, 1.45, "y", color=d.Y_)
        d.arrow(ax, (0, 0), w, d.VR, lw=2.4); ax.text(w[0] + 0.12, w[1] + 0.3, r"$\boldsymbol{F}_\mathrm{g}$", color=d.VR, fontsize=12)
        ax.set_title(T("水平—竖直坐标：", "level axes: ") + r"$(0,\ -mg)$", fontsize=9)
    else:
        d.arrow(ax, (0, 0), 2.0 * ex, d.X_, lw=1.2); ax.text(*(2.1 * ex), "x′", color=d.X_)
        d.arrow(ax, (0, 0), 1.5 * ey, d.Y_, lw=1.2); ax.text(*(1.5 * ey + np.array([0.08, 0])), "y′", color=d.Y_)
        px, py = (w @ ex) * ex, (w @ ey) * ey
        ax.plot([px[0], w[0]], [px[1], w[1]], color=d.MUTED, lw=0.8, ls="--"); ax.plot([py[0], w[0]], [py[1], w[1]], color=d.MUTED, lw=0.8, ls="--")
        d.arrow(ax, (0, 0), w, d.VR, lw=2.4); ax.text(w[0] - 0.12, w[1] + 0.25, r"$\boldsymbol{F}_\mathrm{g}$", color=d.VR, fontsize=12, ha="right")
        d.arrow(ax, (0, 0), px, d.X_, lw=2.2); ax.text(px[0] - 0.15, px[1] + 0.2, r"$F_{\mathrm{g},x'}$", color=d.X_, fontsize=11, ha="right")
        d.arrow(ax, (0, 0), py, d.Y_, lw=2.2); ax.text(py[0] + 0.15, py[1] + 0.35, r"$F_{\mathrm{g},y'}$", color=d.Y_, fontsize=11, ha="left")
        ax.set_title(T("沿坡—垂直坡面坐标：", "slope axes: ") + r"$(-mg\sin\alpha,\ -mg\cos\alpha)$", fontsize=9)
    ax.set_xlim(-2.7, 2.7); ax.set_ylim(-2.4, 1.9); ax.set_aspect("equal"); d.clean(ax)
figure(fig, "fig2_3_3")
