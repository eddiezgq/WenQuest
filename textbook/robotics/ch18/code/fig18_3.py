"""18.3 节的示意图。

图 18.3.1：(a) Stewart 平台在位姿 X1 处（算例 18.3.1），六条腿按编号着色；(b) 5 s 多轴正弦运动中六条腿长随时间的变化，
           虚线为电动缸行程 0.55～0.85 m。
图 18.3.2：正解的牛顿法：从原点位姿出发求 X1 时各步的最大腿长残差（对数坐标），与“残差平方”的参考线对照。
图 18.3.3：X1 的腿长下，机架平面上方的四个实数解（装配模式）；第一个就是 X1。
"""
import math

import numpy as np

from _ch18 import (ST_A, ST_HOME, ST_LMAX, ST_LMIN, distinct_poses, pose, random_rotations, rpy, st_fk, st_fk_batch, st_ik,
                   st_points)
from _fig18 import BLUE2, C, GREY, axes3d, draw_stewart, equal3d, label3d
from bookout import T, figure, style

plt = style()
plt.rcParams["axes.unicode_minus"] = True
rad = math.radians
LEGC = ["#d62728", "#e8a33d", "#2ca02c", "#17becf", "#1f77b4", "#9467bd"]
X1 = pose(rpy(rad(6), rad(-8), rad(12)), [0.05, -0.03, 0.62])

# ---------------------------------------------------------------- 图 18.3.1
fig = plt.figure(figsize=(10.8, 4.6))
fig, ax = axes3d(plt, fig=fig, pos=121, elev=18, azim=-62)
q = draw_stewart(ax, X1, legs_cmap=LEGC, lw=2.6)
for i in range(6):
    off = np.array([0, 0, -0.03]) if i not in (2, 3) else np.array([0, 0, -0.09])    # 后面两点的标号放低一些，免得被腿挡住
    label3d(ax, ST_A[i] * 1.12 + off, str(i + 1), LEGC[i], fs=10, zorder=20)
ax.quiver(0, 0, 0, 0.18, 0, 0, color=C["x"], lw=1.4, arrow_length_ratio=0.15)
ax.quiver(0, 0, 0, 0, 0.18, 0, color=C["y"], lw=1.4, arrow_length_ratio=0.15)
ax.quiver(0, 0, 0, 0, 0, 0.18, color=C["z"], lw=1.4, arrow_length_ratio=0.15)
label3d(ax, [0.2, 0, 0], "x", C["x"])
label3d(ax, [0, 0.2, 0], "y", C["y"])
label3d(ax, [0, 0, 0.2], "z", C["z"])
pc = X1[:3, 3]
R = X1[:3, :3]
for k, col in enumerate((C["x"], C["y"], C["z"])):
    ax.quiver(*pc, *(0.12 * R[:, k]), color=col, lw=1.4, arrow_length_ratio=0.2)
label3d(ax, pc + np.array([-0.05, 0, 0.17]), T("动平台 {b}", "platform {b}"), C["z"], fs=9, zorder=20)
label3d(ax, np.array([0.3, -0.55, 0.0]), T("机架 {s}", "base {s}"), C["muted"], fs=9)
equal3d(ax, np.vstack([ST_A, q, [[0, 0, 0.75]]]), pad=0.02, zoom=1.2)
ax.text2D(0.0, 1.0, T("(a) 位姿 X1 处的 Stewart 平台", "(a) the Stewart platform at pose X1"), transform=ax.transAxes, fontsize=10)


def motion(t):
    return pose(rpy(rad(8) * math.sin(2 * math.pi * 0.5 * t), rad(6) * math.sin(2 * math.pi * 0.7 * t + 1.0),
                    rad(10) * math.sin(2 * math.pi * 0.3 * t)),
                [0.04 * math.sin(2 * math.pi * 0.4 * t), 0.03 * math.sin(2 * math.pi * 0.6 * t + 0.5), 0.6 + 0.05 * math.sin(2 * math.pi * 0.8 * t)])


ts = np.linspace(0, 5, 501)
Ls = np.array([st_ik(motion(t)) for t in ts])
a2 = fig.add_subplot(122)
for i in range(6):
    a2.plot(ts, Ls[:, i], color=LEGC[i], lw=1.6, label=T(f"腿 {i + 1}", f"leg {i + 1}"))
for v in (ST_LMIN, ST_LMAX):
    a2.axhline(v, color=C["muted"], lw=1.2, ls="--")
a2.text(0.05, ST_LMAX + 0.008, T("行程上限 0.85 m", "stroke limit 0.85 m"), fontsize=9, color=C["muted"])
a2.text(0.05, ST_LMIN + 0.008, T("行程下限 0.55 m", "stroke limit 0.55 m"), fontsize=9, color=C["muted"])
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("腿长 / m", "leg length / m"))
a2.set_ylim(0.52, 0.9)
a2.set_xlim(0, 5)
a2.grid(alpha=0.3)
a2.legend(fontsize=8, ncol=3, loc="upper right", frameon=False, bbox_to_anchor=(1.0, 0.94))
a2.set_title(T("(b) 多轴正弦运动中的六条腿长", "(b) the six leg lengths during a multi-axis sine motion"), fontsize=10, loc="left")
figure(fig, "fig18_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 18.3.2
L1 = st_ik(X1)
hist = []
st_fk(L1, ST_HOME, tol=1e-15, hist=hist)
hist = [h for h in hist if h > 0]
fig, ax = plt.subplots(figsize=(6.4, 3.9))
k = np.arange(len(hist))
ax.semilogy(k, hist, "o-", color=C["z"], lw=1.8, ms=6, label=T("最大腿长残差", "largest leg-length residual"))
ref = [hist[1]]
for _ in range(len(hist) - 2):
    ref.append(ref[-1] ** 2)
ax.semilogy(k[1:], ref, ":", color=C["accent"], lw=1.4, label=T("每步平方的参考线", "squared at every step (reference)"))
ax.axhline(2.2e-16, color=C["muted"], lw=0.8, ls="--")
ax.text(0.05, 5e-16, T("双精度舍入误差", "double-precision round-off"), fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("迭代次数 k", "iteration k"))
ax.set_ylabel(T("残差 / m", "residual / m"))
ax.set_xticks(k)
ax.grid(alpha=0.3, which="both")
ax.legend(fontsize=9, frameon=False)
ax.set_title(T("从原点位姿出发求 X1：牛顿法二次收敛", "Solving for X1 from the home pose: quadratic convergence"), fontsize=10, loc="left")
figure(fig, "fig18_3_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 18.3.3
rng = np.random.default_rng(183)
N = 4000
T0 = np.zeros((N, 4, 4))
T0[:, :3, :3] = random_rotations(N, rng)
T0[:, :3, 3] = rng.uniform([-0.8, -0.8, -0.9], [0.8, 0.8, 0.9], (N, 3))
T0[:, 3, 3] = 1
Tb, okb = st_fk_batch(L1, T0, itmax=80)
sols = [S for S in distinct_poses(Tb[okb]) if S[2, 3] > 0]
sols.sort(key=lambda S: -S[2, 3])
fig = plt.figure(figsize=(11.0, 3.4))
for j, S in enumerate(sols[:4]):
    fig, ax = axes3d(plt, fig=fig, pos=141 + j, elev=14, azim=-60)
    qq = draw_stewart(ax, S, legs_cmap=LEGC, lw=1.8, plat_color=BLUE2 if j == 0 else "#f2cf8a", alpha=0.45)
    equal3d(ax, np.vstack([ST_A, qq, [[0, 0, 0.0], [0, 0, 0.75]]]), pad=0.02, zoom=1.15)
    tilt = math.degrees(math.acos(max(-1.0, min(1.0, S[2, 2]))))
    ax.text2D(0.02, 0.93, (T("解 1：就是 X1", "solution 1: X1 itself") if j == 0 else T(f"解 {j + 1}", f"solution {j + 1}")),
              transform=ax.transAxes, fontsize=9.5)
    ax.text2D(0.02, 0.83, T(f"中心高 {S[2, 3]:.3f} m，倾斜 {tilt:.1f}°", f"centre {S[2, 3]:.3f} m, tilt {tilt:.1f}°"), transform=ax.transAxes,
              fontsize=8.5, color=C["muted"])
figure(fig, "fig18_3_3")
plt.close(fig)
