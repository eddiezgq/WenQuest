"""3.7 节的计算：

算例 3.7.1  巡检机器人在一座小土丘上，地面高度 H(x, y) = 3.0 − 0.02x² − 0.05y²（m）。在点 (5, 3) m 处求偏导数和梯度、
            最陡的坡度；机器人朝方位角 φ 行驶时感到的坡度是方向导数 ∇H·û。机器人最多能爬 15° 的坡，哪些方向能直接开上去？
            （图 3.7.1）
算例 3.7.2  1.6 节的最小二乘：残差平方和 S(a, b) 取极小时，∂S/∂a = 0、∂S/∂b = 0。由这两个方程（正规方程）解出 a、b，
            与式 (1.6.3) 和 numpy.polyfit 核对。数据用一组弹簧的拉力—伸长（习题 1.6.4）。
算例 3.7.3  人工势场导航：AGV 要去目标 g，途中有一根立柱。设势函数 U = ½k_a|r − g|² + 立柱附近的斥力项，AGV 每一步沿
            −∇U 的方向走一小段（梯度下降），看它怎样绕过立柱到达目标（图 3.7.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 3.7.1
h = lambda x, y: 3.0 - 0.02 * x ** 2 - 0.05 * y ** 2
P = np.array([5.0, 3.0])
grad = np.array([-0.04 * P[0], -0.10 * P[1]])
eps = 1e-6
gnum = np.array([(h(P[0] + eps, P[1]) - h(P[0] - eps, P[1])) / (2 * eps), (h(P[0], P[1] + eps) - h(P[0], P[1] - eps)) / (2 * eps)])
assert np.allclose(grad, gnum, atol=1e-8)
gmag = float(np.linalg.norm(grad))
up = math.degrees(math.atan2(grad[1], grad[0]))
smax = math.tan(math.radians(15))
# 方向导数 D(φ) = |∇H| cos(φ − φ_up)；能爬的方向：|D| ≤ tan 15°
c = smax / gmag
half = math.degrees(math.acos(c))                     # 与最陡上坡方向夹角超过 half 才不超过 15°
phi_e = 0.0                                           # 朝正东行驶
D_e = float(grad @ np.array([1.0, 0.0]))
out(gx=grad[0], gy=grad[1], gmag=gmag, half_c=180 - half, top=math.degrees(math.atan2(-P[1], -P[0])), gdeg=math.degrees(math.atan(gmag)), up=up, smax=smax, half=half,
    D_e=D_e, D_edeg=math.degrees(math.atan(abs(D_e))), hP=h(*P))

# ---- 算例 3.7.2：正规方程
F = np.array([1, 2, 3, 4, 5], float)
X = np.array([0.62, 1.19, 1.83, 2.41, 3.02])
n = F.size
# ∂S/∂a = −2Σ(y − a − bx) = 0，∂S/∂b = −2Σx(y − a − bx) = 0
A = np.array([[n, F.sum()], [F.sum(), (F * F).sum()]])
rhs = np.array([X.sum(), (F * X).sum()])
a_, b_ = np.linalg.solve(A, rhs)
assert np.allclose(np.polyfit(F, X, 1), [b_, a_])
out(a=a_, b=b_, k=1 / (b_ / 100), Sx=F.sum(), Sxx=(F * F).sum(), Sy=X.sum(), Sxy=(F * X).sum())

# ---- 算例 3.7.3：人工势场
g = np.array([9.0, 1.0])
obs, rho0, ka, kr = np.array([5.0, 2.4]), 1.5, 1.0, 1.2
start = np.array([1.0, 4.0])


def U(p):
    r = np.linalg.norm(p - obs)
    rep = 0.5 * kr * (1 / r - 1 / rho0) ** 2 if r < rho0 else 0.0
    return 0.5 * ka * np.sum((p - g) ** 2) + rep


def gradU(p, e=1e-6):
    return np.array([(U(p + [e, 0]) - U(p - [e, 0])) / (2 * e), (U(p + [0, e]) - U(p - [0, e])) / (2 * e)])


path = [start.copy()]
p = start.copy()
step = 0.05                                            # 每一步沿 −∇U 方向走 0.05 m
for _ in range(1000):
    gU = gradU(p)
    if np.linalg.norm(p - g) < 0.05:
        break
    p = p - step * gU / np.linalg.norm(gU)
    path.append(p.copy())
path = np.array(path)
dmin = float(np.min(np.linalg.norm(path - obs, axis=1)))
plen = float(np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1)))
assert np.linalg.norm(path[-1] - g) < 0.06 and dmin > 0.3
out(steps=len(path) - 1, plen=plen, straight=float(np.linalg.norm(g - start)), dmin=dmin, rho0=rho0)

plt = style()
# ---- 图 3.7.1：等高线与梯度
fig, ax = plt.subplots(figsize=(5.2, 4.0))
xs, ys = np.meshgrid(np.linspace(-8, 8, 200), np.linspace(-6, 6, 160))
cs = ax.contour(xs, ys, h(xs, ys), levels=np.arange(0.0, 3.01, 0.25), colors=d.MUTED, linewidths=0.7)
ax.clabel(cs, fmt="%.2f", fontsize=7)
for qx in range(-6, 7, 3):
    for qy in range(-4, 5, 2):
        gq = np.array([-0.04 * qx, -0.10 * qy])
        if np.linalg.norm(gq) > 1e-9:
            d.arrow(ax, (qx, qy), (qx + 3 * gq[0], qy + 3 * gq[1]), d.VB, lw=1.2, ms=8)
d.arrow(ax, tuple(P), tuple(P + 6 * grad), d.VR, lw=2.4)
ax.plot(*P, "o", color=d.INK, ms=5)
ax.text(P[0] + 0.2, P[1] + 0.35, T("机器人 (5, 3)", "robot (5, 3)"), fontsize=9)
ax.text(P[0] + 4 * grad[0] + 0.5, P[1] + 4 * grad[1] - 0.2, r"$\nabla H$", color=d.VR, fontsize=12)
ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
ax.set_title(T("等高线（高度 / m）与梯度：梯度垂直于等高线，指向上坡", "contours (height / m) and gradients: perpendicular to contours, uphill"), fontsize=8.5)
figure(fig, "fig3_7_1")

# ---- 图 3.7.2：势场导航
fig, ax = plt.subplots(figsize=(5.2, 3.4))
xs, ys = np.meshgrid(np.linspace(0, 10, 240), np.linspace(0, 5, 120))
UU = np.vectorize(lambda x, y: U(np.array([x, y])))(xs, ys)
ax.contour(xs, ys, np.log(UU + 0.05), levels=18, colors="#c7ced2", linewidths=0.6)
ax.add_patch(plt.Circle(tuple(obs), 0.25, fc=d.INK))
ax.add_patch(plt.Circle(tuple(obs), rho0, fill=False, ls="--", ec=d.MUTED, lw=0.8))
ax.text(obs[0], obs[1] + rho0 + 0.12, T("斥力作用范围", "repulsion range"), ha="center", fontsize=8, color=d.MUTED)
ax.plot(path[:, 0], path[:, 1], color=d.VR, lw=2)
ax.plot(*start, "o", color=d.VA, ms=6); ax.text(start[0], start[1] + 0.25, T("起点", "start"), ha="center", fontsize=9)
ax.plot(*g, "*", color=d.VB, ms=12); ax.text(g[0], g[1] - 0.45, T("目标", "goal"), ha="center", fontsize=9)
ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig3_7_2")
