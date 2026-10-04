"""2.1 节的计算：

算例 2.1.1  车间地面坐标中，AGV 从装货点 A(2, 1) m 沿通道先向东 12 m、再向北 5 m 到达 B。求路程、位移的大小和方向；
            另一辆 AGV 从 C(4, 8) m 出发，位移与它相同，求终点（图 2.1.1：同一个位移矢量，平移后仍是同一个矢量）。
算例 2.1.2  有限转动不是矢量：把一个盒子先绕 x 轴转 90°、再绕 y 轴转 90°，与先绕 y、再绕 x 比较，结果不同
            （图 2.1.2）；两次都只转 1° 时，两种顺序的差别只有约 0.017°，小转动近似可以交换（第 12 章的角速度矢量）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 2.1.1
A = np.array([2.0, 1.0])
legs = [np.array([12.0, 0.0]), np.array([0.0, 5.0])]
B = A + sum(legs)
path = sum(np.linalg.norm(v) for v in legs)
disp = B - A
dmag = float(np.linalg.norm(disp))
dang = math.degrees(math.atan2(disp[1], disp[0]))          # 从东向北量的角
C = np.array([4.0, 8.0])
Dp = C + disp
assert abs(dmag - 13.0) < 1e-12
out(A=f"({A[0]:.0f}, {A[1]:.0f})", B=f"({B[0]:.0f}, {B[1]:.0f})", path=path, dmag=dmag, dang=dang,
    C=f"({C[0]:.0f}, {C[1]:.0f})", Dp=f"({Dp[0]:.0f}, {Dp[1]:.0f})")


# ---- 算例 2.1.2：有限转动的顺序
def Rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def angle_between(R1, R2):
    """两个姿态之间相差的转角（把 R1 转到 R2 需要转多少度）。"""
    c = (np.trace(R1.T @ R2) - 1) / 2
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


q = math.radians(90)
R_xy = Ry(q) @ Rx(q)            # 先绕 x 转，再绕（固定的）y 转
R_yx = Rx(q) @ Ry(q)            # 先绕 y 转，再绕 x 转
big = angle_between(R_xy, R_yx)
s1 = math.radians(1)
small = angle_between(Ry(s1) @ Rx(s1), Rx(s1) @ Ry(s1))
assert big > 100 and small < 0.02
# 盒子上“封面法线”（开始时沿 z）在两种顺序下最后指向哪里
n0 = np.array([0, 0, 1.0])
n_xy, n_yx = R_xy @ n0, R_yx @ n0
dirname = {(1, 0, 0): "+x", (-1, 0, 0): "−x", (0, 1, 0): "+y", (0, -1, 0): "−y", (0, 0, 1): "+z", (0, 0, -1): "−z"}
nm = lambda v: dirname[tuple(int(round(c)) for c in v)]
out(big=big, small=small, small_rad=math.radians(small), small_pred=math.degrees(s1 * s1), n_xy=nm(n_xy), n_yx=nm(n_yx),
    s1_rad=s1)

plt = style()
# ---- 图 2.1.1：路程与位移；平移后的同一个矢量
fig, ax = plt.subplots(figsize=(5.4, 3.4))
for x in range(0, 21, 2):
    ax.plot([x, x], [0, 14], color="#eef1f2", lw=0.8, zorder=0)
for y in range(0, 15, 2):
    ax.plot([0, 20], [y, y], color="#eef1f2", lw=0.8, zorder=0)
P1 = A + legs[0]
ax.plot([A[0], P1[0], B[0]], [A[1], P1[1], B[1]], color=d.MUTED, lw=1.6, ls="--", zorder=1)
ax.text(8, 0.2, T("实际路线（路程 17 m）", "route (path length 17 m)"), color=d.MUTED, fontsize=9, ha="center")
d.arrow(ax, A, B, d.VR, lw=2.2, label=r"$\Delta\boldsymbol{r}$", off=(-0.6, 0.7))
d.arrow(ax, C, Dp, d.VR, lw=2.2, label=r"$\Delta\boldsymbol{r}$", off=(-0.6, 0.7))
for p, n in ((A, "A"), (B, "B"), (C, "C"), (Dp, "D")):
    ax.plot(*p, "o", color=d.INK, ms=4, zorder=4)
    ax.text(p[0] + 0.3, p[1] - 0.7, n, fontsize=10)
ax.text(19.6, 0.4, T("东 x", "east x"), ha="right", fontsize=9, color=d.MUTED)
ax.text(0.3, 13.3, T("北 y", "north y"), fontsize=9, color=d.MUTED)
ax.set_xlim(0, 20); ax.set_ylim(0, 14); ax.set_aspect("equal"); ax.set_xticks(range(0, 21, 4)); ax.set_yticks(range(0, 15, 2))
ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig2_1_1")

# ---- 图 2.1.2：转动的顺序不同，结果不同
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

box = np.array([[x, y, z] for x in (-1.2, 1.2) for y in (-0.8, 0.8) for z in (-0.25, 0.25)])
faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
top = 3                                   # 顶面（+z 一面）的编号：z = +0.25 的四个点 1, 3, 7, 5 → faces[5]


def draw_box(ax, R, title):
    P = box @ R.T
    polys = [[P[i] for i in f] for f in faces]
    cols = ["#d9dee1"] * 6
    cols[5] = "#e8b04a"                   # 封面（开始时朝上）涂成橙色
    cols[3] = "#9fb8d9"                   # 书脊（开始时朝 +y）涂成蓝色
    ax.add_collection3d(Poly3DCollection(polys, facecolors=cols, edgecolors=d.INK, linewidths=0.6, alpha=0.95))
    for v, c, n in ((np.array([1.9, 0, 0]), d.X_, "x"), (np.array([0, 1.9, 0]), d.Y_, "y"), (np.array([0, 0, 1.9]), d.Z_, "z")):
        ax.quiver(0, 0, 0, *v, color=c, lw=1.2, arrow_length_ratio=0.12)
        ax.text(*(v * 1.12), n, color=c, fontsize=9)
    nv = R @ np.array([0, 0, 1.0])                     # 封面的法线：橙色面朝向哪里
    ax.quiver(0, 0, 0, *(1.5 * nv), color="#c0392b", lw=2.2, arrow_length_ratio=0.18)
    lab = dirname[tuple(int(round(c)) for c in nv)]
    ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.set_zlim(-1.6, 1.6)
    ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=22, azim=-58); ax.set_axis_off()
    ax.set_title(title + T("\n封面朝 ", "\ncover faces ") + lab, fontsize=9)


fig = plt.figure(figsize=(7.6, 4.4))
rows = [(T("先绕 x 转 90°", "90° about x first"), Rx(q), T("再绕 y 转 90°", "then 90° about y"), R_xy),
        (T("先绕 y 转 90°", "90° about y first"), Ry(q), T("再绕 x 转 90°", "then 90° about x"), R_yx)]
k = 1
for t1, R1, t2, R2 in rows:
    draw_box(fig.add_subplot(2, 3, k, projection="3d"), np.eye(3), T("开始", "start"))
    draw_box(fig.add_subplot(2, 3, k + 1, projection="3d"), R1, t1)
    draw_box(fig.add_subplot(2, 3, k + 2, projection="3d"), R2, t2)
    k += 3
fig.subplots_adjust(wspace=0.0, hspace=0.15)
figure(fig, "fig2_1_2")
