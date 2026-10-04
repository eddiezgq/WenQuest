"""2.5 节的计算：

算例 2.5.1  UR5e 夹着 5 kg 的负载。以肩关节中心为原点（z 竖直向上），负载质心的位置矢量 r = (0.60, 0.25, 0.20) m。
            重力 F = (0, 0, −mg)。求重力对肩关节中心的力矩 M = r × F（分量式与“力臂”两种算法，图 2.5.2）。
算例 2.5.2  接着算例 2.4.2：目标 1 在机器人朝向的左边还是右边？用叉积的 z 分量判断。
算例 2.5.3  激光雷达测出仓库一块存放区的五个角点 (0, 0)、(8, 0)、(9, 5)、(4, 7)、(−1, 4) m。用叉积求它的面积
            （把多边形分成以第一个角点为公共顶点的三角形，图 2.5.3），并与鞋带公式核对。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

rad = math.radians
# ---- 算例 2.5.1
m = 5.0
r = np.array([0.60, 0.25, 0.20])
F = np.array([0.0, 0.0, -m * g])
M = np.cross(r, F)
Mmag = float(np.linalg.norm(M))
arm = math.hypot(r[0], r[1])                       # 力臂：r 在水平面内的投影长度
assert abs(Mmag - arm * m * g) < 1e-9 and abs(M @ r) < 1e-9 and abs(M @ F) < 1e-9
# 行列式展开的各项
out(m=m, mg=m * g, Mx=M[0], My=M[1], Mz=M[2], Mmag=Mmag, arm=arm,
    Mmax=0.85 * m * g)                             # 水平伸直到 0.85 m 时（习题 1.7.2）

# ---- 用随机矢量核对反交换律、分配律和混合积的轮换（习题 2.5.6）
rng = np.random.default_rng(25)
for _ in range(100):
    A_, B_, C_ = rng.normal(size=(3, 3))
    assert np.allclose(np.cross(B_, A_), -np.cross(A_, B_))
    assert np.allclose(np.cross(A_, B_ + C_), np.cross(A_, B_) + np.cross(A_, C_))
    assert np.isclose(A_ @ np.cross(B_, C_), np.cross(A_, B_) @ C_)
    assert abs(A_ @ np.cross(A_, B_)) < 1e-12

# ---- 算例 2.5.2：左还是右
head = 30.0
u = np.array([math.cos(rad(head)), math.sin(rad(head)), 0.0])
t = np.array([6.0, 5.0, 0.0])
cz = float(np.cross(u, t)[2])
t3 = np.array([7.0, 2.0, 0.0])
cz3 = float(np.cross(u, t3)[2])
assert cz > 0 and cz3 < 0
out(cz=cz, cz3=cz3)

# ---- 算例 2.5.3：多边形面积
P = np.array([[0, 0], [8, 0], [9, 5], [4, 7], [-1, 4]], float)
tri = []
for i in range(1, len(P) - 1):
    a3 = np.append(P[i] - P[0], 0); b3 = np.append(P[i + 1] - P[0], 0)
    tri.append(0.5 * np.cross(a3, b3)[2])
area = sum(tri)
x, y = P[:, 0], P[:, 1]
shoelace = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
assert abs(area - shoelace) < 1e-12
out(tri1=tri[0], tri2=tri[1], tri3=tri[2], area=area)

plt = style()
# ---- 图 2.5.1：叉积的大小是平行四边形的面积，方向按右手定则（动画 2.5.1 的静态图）
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig = plt.figure(figsize=(7.4, 3.6))
for k, (ang, ttl) in enumerate(((75, T(r"$\boldsymbol{A}\times\boldsymbol{B}$ 向上", r"$\boldsymbol{A}\times\boldsymbol{B}$ points up")),
                                (75, T(r"$\boldsymbol{B}\times\boldsymbol{A}$ 向下", r"$\boldsymbol{B}\times\boldsymbol{A}$ points down")))):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    A = np.array([2.0, 0.0, 0.0]); B = 1.7 * np.array([math.cos(rad(ang)), math.sin(rad(ang)), 0.0])
    C = np.cross(A, B) if k == 0 else np.cross(B, A)
    Cn = C / np.linalg.norm(C) * 1.9
    ax.add_collection3d(Poly3DCollection([[np.zeros(3), A, A + B, B]], facecolors="#f3d9a4", edgecolors="#c9a050", alpha=0.6))
    ax.quiver(0, 0, 0, *A, color=d.VA, lw=2.2, arrow_length_ratio=0.1); ax.text(*(A * 1.08), r"$\boldsymbol{A}$", color=d.VA, fontsize=12)
    ax.quiver(0, 0, 0, *B, color=d.VB, lw=2.2, arrow_length_ratio=0.12); ax.text(*(B * 1.12), r"$\boldsymbol{B}$", color=d.VB, fontsize=12)
    ax.quiver(0, 0, 0, *Cn, color=d.VR, lw=2.4, arrow_length_ratio=0.12)
    ax.text(*(Cn * 1.08 + np.array([0.1, 0, 0])), r"$\boldsymbol{A}\times\boldsymbol{B}$" if k == 0 else r"$\boldsymbol{B}\times\boldsymbol{A}$",
            color=d.VR, fontsize=11)
    ax.text(*((A + B) * 0.45), T("面积 ", "area ") + r"$AB\sin\theta$", fontsize=9, color="#8a6a20", ha="center")
    ax.set_xlim(-0.5, 2.5); ax.set_ylim(-0.5, 2.0); ax.set_zlim(-2.0, 2.0)
    ax.view_init(elev=42, azim=-70); ax.set_axis_off(); ax.set_box_aspect((1.2, 1, 1.4)); ax.set_title(ttl, fontsize=9)
figure(fig, "fig2_5_1")

# ---- 图 2.5.2：重力对肩关节的力矩
fig = plt.figure(figsize=(5.2, 4.0))
ax = fig.add_subplot(projection="3d")
ax.plot([0, 0], [0, 0], [-0.45, 0], color="#9aa5ab", lw=8)               # 底座示意
ax.plot([0, r[0]], [0, r[1]], [0, r[2]], color="#bfc7cc", lw=6)            # 手臂示意（直线代替）
ax.quiver(0, 0, 0, *r, color=d.VA, lw=2.2, arrow_length_ratio=0.08); ax.text(*(r * 0.55 + np.array([0.02, 0, -0.09])), r"$\boldsymbol{r}$", color=d.VA, fontsize=12)
fs = 0.004
_e = r + F * fs; ax.plot([r[0], _e[0]], [r[1], _e[1]], [r[2], _e[2]], color=d.VB, lw=2.4); ax.plot([_e[0]], [_e[1]], [_e[2]], marker="v", color=d.VB, ms=9); ax.text(*(r + F * fs * 0.6 + np.array([0.06, 0, 0])), r"$\boldsymbol{F}=m\boldsymbol{g}$", color=d.VB, fontsize=11)
ms = 0.015
ax.quiver(0, 0, 0, *(M * ms), color=d.VR, lw=2.4, arrow_length_ratio=0.1); ax.text(*(M * ms + np.array([-0.3, 0.05, 0.06])), r"$\boldsymbol{M}=\boldsymbol{r}\times\boldsymbol{F}$", color=d.VR, fontsize=11)
ax.plot([r[0], r[0]], [r[1], r[1]], [r[2], -0.45], color=d.MUTED, lw=0.8, ls=":")
ax.plot([0, r[0]], [0, r[1]], [-0.45, -0.45], color=d.MUTED, lw=1.0, ls="--")
ax.text(r[0] / 2, r[1] / 2 - 0.05, -0.5, T(f"力臂 {arm:.2f} m", f"lever arm {arm:.2f} m"), fontsize=9, color=d.MUTED)
for v, c, n in ((np.array([0.8, 0, 0]), d.X_, "x"), (np.array([0, 0.75, 0]), d.Y_, "y"), (np.array([0, 0, 0.5]), d.Z_, "z")):
    ax.quiver(0, 0, 0, *v, color=c, lw=1, arrow_length_ratio=0.08); ax.text(*(v * 1.07), n, color=c)
ax.set_xlim(-0.3, 0.8); ax.set_ylim(-0.6, 0.7); ax.set_zlim(-0.5, 0.6)
ax.view_init(elev=24, azim=-38); ax.set_axis_off(); ax.set_box_aspect((1.1, 1.3, 1.1))
figure(fig, "fig2_5_2")

# ---- 图 2.5.3：多边形面积 = 三角形面积之和
fig, ax = plt.subplots(figsize=(4.6, 3.6))
cols = ["#d6e6f5", "#d9efdf", "#f3e0d0"]
for i in range(1, len(P) - 1):
    ax.fill([P[0, 0], P[i, 0], P[i + 1, 0]], [P[0, 1], P[i, 1], P[i + 1, 1]], color=cols[i - 1], ec=d.MUTED, lw=0.8)
    cx, cy = (P[0] + P[i] + P[i + 1]) / 3
    ax.text(cx, cy, f"{tri[i - 1]:.1f} m²", ha="center", va="center", fontsize=9)
ax.plot(*np.vstack([P, P[:1]]).T, color=d.INK, lw=1.6)
for i, p in enumerate(P):
    ax.plot(*p, "o", color=d.INK, ms=4); ax.text(p[0] + 0.2, p[1] + 0.2, f"$P_{i + 1}$", fontsize=10)
ax.set_xlim(-2, 10.5); ax.set_ylim(-1, 8); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig2_5_3")
