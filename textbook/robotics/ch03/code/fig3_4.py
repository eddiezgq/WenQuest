"""3.4 节的示意图。

图 3.4.1：(a) 二阶张量是线性算子：把单位圆上的每个矢量 u 变成 A u，单位圆变成椭圆，A u 一般不与 u 平行；
          (b) 同一个张量在 {a}、{b} 中的分量矩阵不同，椭圆（张量本身）不变。
图 3.4.2：算例 3.4.1：倾斜表面上的速度投影（侧视，y–z 平面）：正确的投影与误用分量矩阵的结果。
图 3.4.3：(a) 算例 3.4.2：夹爪中倾斜的板绕工具 z 轴转动，角动量 L 与 ω 不平行；(b) 应力张量：截面法线 n 与截面上的应力矢量 t = σ n。
"""
import math

import numpy as np

from _vec import C, arc2, arrow2, arrow3, d, frame3, rot_x, sub3d
from bookout import T, figure, style

plt = style()
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402


def R2(t):
    return np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])


A = R2(d(25)) @ np.diag([1.6, 0.6]) @ R2(d(25)).T       # 示意用的二维对称张量（在 {a} 中的分量）

# ---------------------------------------------------------------- 图 3.4.1
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.0, 4.6))
for ax in (ax1, ax2):
    ax.set_aspect("equal")
    ax.axis("off")
t = np.linspace(0, 2 * math.pi, 200)
U = np.vstack([np.cos(t), np.sin(t)])
E = A @ U
ax1.plot(*U, color=C["muted"], lw=1, ls="--")
ax1.plot(*E, color=C["accent"], lw=1.6)
for k, ang in enumerate((d(80), d(150), d(-20))):
    u = np.array([math.cos(ang), math.sin(ang)])
    arrow2(ax1, (0, 0), u, C["ink"], 1.4)
    arrow2(ax1, (0, 0), A @ u, C["x"], 1.8)
    ax1.text(*(u * 1.1 + [-0.05, 0.0]), rf"$\boldsymbol{{u}}_{k + 1}$", fontsize=12)
    ax1.text(*(A @ u * 1.08 + [0.02, -0.12]), rf"$\boldsymbol{{A}}\boldsymbol{{u}}_{k + 1}$", fontsize=12, color=C["x"])
ev = R2(d(25))
for j, lam in enumerate((1.6, 0.6)):
    e = ev[:, j] * lam
    ax1.plot([-e[0], e[0]], [-e[1], e[1]], color=C["z"], lw=1, ls=":")
ax1.text(1.25, 0.95, T("主轴", "principal axis"), fontsize=9.5, color=C["z"])
ax1.text(-1.75, 1.75, T("(a) 线性算子：单位圆 → 椭圆，Au 一般不平行于 u", "(a) A linear operator: unit circle → ellipse; Au is generally not parallel to u"), fontsize=10)
ax1.text(-1.0, -1.3, T("虚线：单位圆", "dashed: unit circle"), fontsize=9, color=C["muted"])
ax1.set_xlim(-1.8, 1.9)
ax1.set_ylim(-1.45, 1.9)

beta = d(55)
Rb = R2(beta)
A_b = Rb.T @ A @ Rb
ax2.plot(*E, color=C["accent"], lw=1.6)
for (ang, sub, alpha) in ((0.0, "a", 0.55), (beta, "b", 1.0)):
    xb, yb = R2(ang)[:, 0], R2(ang)[:, 1]
    arrow2(ax2, (0, 0), 1.75 * xb, C["x"], 1.4, alpha=alpha)
    arrow2(ax2, (0, 0), 1.45 * yb, C["y"], 1.4, alpha=alpha)
    ax2.text(*(1.83 * xb + [-0.02, -0.06]), rf"$\hat{{\boldsymbol{{x}}}}_{sub}$", color=C["x"], fontsize=12, alpha=alpha)
    ax2.text(*(1.53 * yb + [-0.1, 0.0]), rf"$\hat{{\boldsymbol{{y}}}}_{sub}$", color=C["y"], fontsize=12, alpha=alpha)
arc2(ax2, (0, 0), 0.5, 0, beta, C["ink"], 0.9)
ax2.text(0.52, 0.25, r"$55^\circ$", fontsize=10)


ax2.text(-1.95, -1.25, r"$A_a$", fontsize=13)
ax2.text(-1.95, -1.6, r"$A_b$", fontsize=13)
ax2.text(-1.6, -1.25, "= [%.3f  %.3f;  %.3f  %.3f]" % (A[0, 0], A[0, 1], A[1, 0], A[1, 1]), fontsize=11)
ax2.text(-1.6, -1.6, "= [%.3f  %.3f;  %.3f  %.3f]" % (A_b[0, 0], A_b[0, 1], A_b[1, 0], A_b[1, 1]), fontsize=11)
ax2.text(-1.95, -1.95, T("迹都是 %.1f，行列式都是 %.2f" % (np.trace(A), np.linalg.det(A)),
                         "trace %.1f and determinant %.2f in both" % (np.trace(A), np.linalg.det(A))), fontsize=10, color=C["muted"])
ax2.text(-1.95, 1.75, T("(b) 同一个椭圆，两套分量矩阵", "(b) One ellipse, two component matrices"), fontsize=10)
ax2.set_xlim(-2.0, 2.0)
ax2.set_ylim(-2.1, 1.9)
fig.subplots_adjust(wspace=0.05)
figure(fig, "fig3_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.4.2
th = d(20)
n = np.array([-math.sin(th), math.cos(th)])          # (y, z) 平面内的法线
s = np.array([math.cos(th), math.sin(th)])           # 沿表面
vc = np.array([0.10, 0.0])
v = vc - (vc @ n) * n
fig, ax = plt.subplots(figsize=(7.4, 4.4))
ax.set_aspect("equal")
ax.axis("off")
K = 10.0
L0 = np.array([-0.4, 0.0])
pts = np.array([L0 - 1.2 * s, L0 + 1.7 * s]) * 1.0
ax.fill([pts[0][0], pts[1][0], pts[1][0], pts[0][0]], [pts[0][1], pts[1][1], -0.9, -0.9], color="#e8edf1")
ax.plot(pts[:, 0], pts[:, 1], color=C["muted"], lw=2)
ax.text(-1.35, -0.3, T("工件表面（倾斜 20°）", "work surface (tilted 20°)"), fontsize=10, color=C["muted"], rotation=20)
O = np.array([0.0, 0.0]) + L0 + 0.55 * s
arrow2(ax, O, O + 0.45 * n, C["z"], 1.8)
ax.text(*(O + 0.5 * n + [-0.05, 0.02]), r"$\hat{\boldsymbol{n}}$", fontsize=13, color=C["z"])
arrow2(ax, O, O + K * vc, C["x"], 2.0)
ax.text(*(O + K * vc + [0.04, -0.06]), r"$\boldsymbol{v}_{\rm cmd}$", fontsize=12, color=C["x"])
arrow2(ax, O, O + K * v, C["y"], 2.4)
ax.text(*(O + K * v + [-0.15, 0.08]), r"$\boldsymbol{P}\boldsymbol{v}_{\rm cmd}$", fontsize=12, color=C["y"])
ax.plot(*np.column_stack([O + K * vc, O + K * v]), ":", color=C["muted"], lw=1.2)
ax.text(*(O + K * vc + [0.06, 0.18]), T("沿法线的部分被去掉", "the normal part is removed"), fontsize=9, color=C["muted"])
ax.text(-1.55, -0.62, T(r"错误：把 diag(1, 1, 0) 直接用在 {a} 中，速度仍是水平的 $\boldsymbol{v}_{\rm cmd}$，", r"Wrong: using diag(1, 1, 0) in {a} leaves $\boldsymbol{v}_{\rm cmd}$ horizontal,"), fontsize=9.5, color=C["x"])
dig = -(vc @ n) * 1000
ax.text(-1.55, -0.75, T(f"工具每秒扎进表面 {dig:.0f} mm", f"and the tool digs into the surface at {dig:.0f} mm/s"), fontsize=9.5, color=C["x"])
arc2(ax, L0, 0.5, 0, th, C["ink"], 0.9)
ax.plot([L0[0], L0[0] + 0.7], [L0[1], L0[1]], color=C["muted"], lw=0.8, ls="--")
ax.text(L0[0] + 0.52, L0[1] + 0.05, r"$20^\circ$", fontsize=10)
ax.text(-1.55, 0.95, T("侧视：y 向右，z 向上；x 分量垂直于纸面，投影时不变", "Side view: y right, z up; the x part is normal to the page and unchanged"), fontsize=9.5)
ax.set_xlim(-1.6, 2.0)
ax.set_ylim(-0.9, 1.05)
figure(fig, "fig3_4_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.4.3
fig = plt.figure(figsize=(10.0, 4.6))
ax = sub3d(fig, 121, elev=10, azim=-12, lim=0.24, zoom=1.25, center=(0, 0, 0.04))
a_, b_, c_ = 0.30, 0.20, 0.02
R_tb = rot_x(d(30))
V = np.array([[x, y, z] for x in (-a_ / 2, a_ / 2) for y in (-b_ / 2, b_ / 2) for z in (-c_ / 2, c_ / 2)]) @ R_tb.T
faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
ax.add_collection3d(Poly3DCollection([V[f] for f in faces], facecolor="#f3e2b3", edgecolor=C["accent"], lw=0.6, alpha=0.75))
frame3(ax, np.eye(3), length=0.13, sub="t", lw=1.2, fs=10, alpha=0.8)
I_b = 2.0 / 12 * np.diag([b_ * b_ + c_ * c_, a_ * a_ + c_ * c_, a_ * a_ + b_ * b_])
I_t = R_tb @ I_b @ R_tb.T
w = np.array([0, 0, 1.0])
L = I_t @ w
arrow3(ax, np.zeros(3), w * 0.24, C["ink"], 2.4)
ax.text(0.0, 0.03, 0.25, r"$\boldsymbol{\omega}$", fontsize=14)
Lh = L / np.linalg.norm(L) * 0.24
arrow3(ax, np.zeros(3), Lh, C["x"], 2.4)
ax.text(*(Lh + [0, -0.1, 0.0]), r"$\boldsymbol{L}=\boldsymbol{I}\boldsymbol{\omega}$", fontsize=13, color=C["x"])
ax.text(0, 0.12, -0.12, T("板面相对工具 xy 平面倾斜 30°", "plate tilted 30° from the tool xy plane"), fontsize=9.5, color=C["accent"])
ax.text2D(0.0, 0.96, T("(a) 倾斜 30° 的板绕工具 z 轴转动：L 偏离 ω", "(a) A plate tilted 30° spinning about the tool z axis: L leans away from ω"),
          transform=ax.transAxes, fontsize=10)

ax = sub3d(fig, 122, elev=20, azim=-55, lim=0.9, zoom=1.2, center=(0.3, 0.3, 0.3))
cube = np.array([[x, y, z] for x in (0, 0.6) for y in (0, 0.6) for z in (0, 0.6)])
ax.add_collection3d(Poly3DCollection([cube[f] for f in faces], facecolor="#dbe7f3", edgecolor=C["muted"], lw=0.6, alpha=0.35))
sig = np.array([[1.0, 0.4, 0.0], [0.4, -0.5, 0.3], [0.0, 0.3, 0.6]])        # 示意用的应力分量
for k, (pc, nn) in enumerate((((0.6, 0.3, 0.3), (1, 0, 0)), ((0.3, 0.6, 0.3), (0, 1, 0)), ((0.3, 0.3, 0.6), (0, 0, 1)))):
    pc, nn = np.array(pc), np.array(nn, float)
    arrow3(ax, pc, 0.35 * nn, C["muted"], 1.2, ls="--")
    tt = sig @ nn
    arrow3(ax, pc, 0.45 * tt / np.linalg.norm(tt), C["x"], 2.2)
ax.text(1.0, 0.3, 0.42, r"$\hat{\boldsymbol{n}}$", fontsize=12, color=C["muted"])
ax.text(1.02, 0.55, 0.35, r"$\boldsymbol{t}=\boldsymbol{\sigma}\hat{\boldsymbol{n}}$", fontsize=12, color=C["x"])
ax.text2D(0.0, 0.96, T("(b) 应力：每个截面上的应力矢量 t 由法线 n 线性决定", "(b) Stress: the stress vector t on a cut depends linearly on its normal n"),
          transform=ax.transAxes, fontsize=10)
fig.subplots_adjust(wspace=0.05)
figure(fig, "fig3_4_3")
plt.close(fig)
