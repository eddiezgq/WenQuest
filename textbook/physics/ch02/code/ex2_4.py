"""2.4 节的计算：

算例 2.4.1  AGV 用牵引杆拖一辆料车沿直线前进 20 m，牵引杆对料车的拉力 300 N，方向斜向上、与前进方向成 25°。
            拉力沿前进方向的分量是多少？拉力做的功 W = F·s 是多少（第 9 章）？用 F s cos θ 和分量 FxSx + FySy 各算一次。
算例 2.4.2  巡检机器人朝向 30°（从 x 轴量起），相机的水平视场角 70°（左右各 35°）。目标在机器人前方的位置矢量为
            (6.0, 5.0) m。用点积求目标方向与朝向的夹角，判断目标是否在视场内（图 2.4.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

rad, deg = math.radians, math.degrees
# ---- 算例 2.4.1
F, th, s = 300.0, 25.0, 20.0
Fv = np.array([F * math.cos(rad(th)), F * math.sin(rad(th))])
sv = np.array([s, 0.0])
W1 = F * s * math.cos(rad(th))
W2 = float(Fv @ sv)
assert abs(W1 - W2) < 1e-9
out(F=F, th=th, s=s, Fpar=Fv[0], Fperp=Fv[1], Wk=W1 / 1000, W=W1)

# ---- 算例 2.4.2
head, half = 30.0, 35.0
u = np.array([math.cos(rad(head)), math.sin(rad(head))])
t = np.array([6.0, 5.0])
cosang = float(u @ t / np.linalg.norm(t))
ang = deg(math.acos(cosang))
inside = cosang > math.cos(rad(half))
# 偏向一侧的另一个目标 (2.0, 6.5)
t2 = np.array([2.0, 6.5])
cos2 = float(u @ t2 / np.linalg.norm(t2))
ang2 = deg(math.acos(cos2))
assert inside and cos2 < math.cos(rad(half))
out(head=head, half=half, tmag=float(np.linalg.norm(t)), udott=float(u @ t), cosang=cosang, ang=ang, cos_half=math.cos(rad(half)),
    cos2=cos2, ang2=ang2, tiny=deg(math.acos(1 - 1e-8)))

plt = style()
# ---- 图 2.4.1：点积是投影；夹角决定正负
fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.7))
B = np.array([2.6, 0.0])
for ax, a_deg, lab in zip(axs, (35, 90, 135), (T("锐角：", "acute: ") + r"$\boldsymbol{A}\cdot\boldsymbol{B}>0$", T("直角：", "right angle: ") + r"$\boldsymbol{A}\cdot\boldsymbol{B}=0$",
                                                 T("钝角：", "obtuse: ") + r"$\boldsymbol{A}\cdot\boldsymbol{B}<0$")):
    A = 2.0 * np.array([math.cos(rad(a_deg)), math.sin(rad(a_deg))])
    ax.plot([-1.8, 3.0], [0, 0], color="#e3e7e9", lw=0.8)
    d.arrow(ax, (0, 0), B, d.VB, label=r"$\boldsymbol{B}$", off=(0.95, -0.25))
    d.arrow(ax, (0, 0), A, d.VA, label=r"$\boldsymbol{A}$", off=(-0.25, 0.1))
    ax.plot([A[0], A[0]], [A[1], 0], color=d.MUTED, lw=0.8, ls="--")
    if abs(A[0]) > 1e-9:
        ax.plot([0, A[0]], [-0.12, -0.12], color=d.VR, lw=4, solid_capstyle="butt", alpha=0.8)
        ax.text(A[0] / 2, -0.42, r"$A\cos\theta$", color=d.VR, ha="center", fontsize=10)
    from matplotlib.patches import Arc
    ax.add_patch(Arc((0, 0), 0.9, 0.9, theta1=0, theta2=a_deg, color=d.MUTED))
    ax.text(0.6 * math.cos(rad(a_deg / 2)), 0.6 * math.sin(rad(a_deg / 2)), r"$\theta$", fontsize=10, color=d.MUTED)
    ax.set_title(lab, fontsize=9); ax.set_xlim(-1.8, 3.0); ax.set_ylim(-0.7, 2.2); ax.set_aspect("equal"); d.clean(ax)
figure(fig, "fig2_4_1")

# ---- 图 2.4.2：视场判断
fig, ax = plt.subplots(figsize=(4.6, 3.6))
from matplotlib.patches import Wedge
ax.add_patch(Wedge((0, 0), 8.5, head - half, head + half, fc="#fbeec9", ec="#e0c070", lw=0.8))
ax.text(7.2 * math.cos(rad(head)), 7.2 * math.sin(rad(head)) - 0.3, T("视场 ±35°", "field of view ±35°"), fontsize=8.5,
        color="#a07a10", ha="center", rotation=head)
d.arrow(ax, (0, 0), 2.5 * u, d.INK, lw=2.4, label=r"$\hat{\boldsymbol{u}}$", off=(0.2, -0.5))
for P, name, col in ((t, T("目标 1", "target 1"), d.VR), (t2, T("目标 2", "target 2"), d.VA)):
    d.arrow(ax, (0, 0), P, col, lw=1.6)
    ax.plot(*P, "o", color=col, ms=5); ax.text(P[0] + 0.2, P[1] + 0.1, name, fontsize=9, color=col)
ax.add_patch(plt.Rectangle((-0.5, -0.35), 1.0, 0.7, fc="#c8d0d4", ec=d.INK, zorder=4))
ax.set_xlim(-1, 9); ax.set_ylim(-1, 9); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig2_4_2")
