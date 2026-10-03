"""14.4 节的示意图。

图 14.4.1：球形手腕六轴臂（算例 14.4.1 的 θ*）：关节 4、5、6 的轴交于腕心 p_w；法兰中心沿接近方向 x_b 离腕心 D6。
           前三个关节决定腕心的位置，后三个关节只决定姿态。
图 14.4.2：两类有封闭解的六轴臂（零位，只画关节轴）：(a) 球形手腕，轴 4、5、6 交于一点；
           (b) UR5e，轴 2、3、4 互相平行（表 12.1.1）。
"""
import math

import numpy as np

from _fig14 import C, arrow3d, axes3d, draw_chain, equal3d, label3d, line3d, sw_chain, ur_chain
from _ik import SW, SW_M, SW_PW, SW_Q, SW_S, SW_W, UR_Q, UR_W, exp6, sw_fk
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 14.4.1
th = np.radians([30, 40, -70, 20, 50, -30])
fig, ax = axes3d(plt, size=(6.4, 4.6), elev=24, azim=-70)
P = sw_chain(th)
draw_chain(ax, P, "#8f9ba3", lw=6)
Es = [np.eye(4)]
for S, t in zip(SW_S, th):
    Es.append(Es[-1] @ exp6(S, t))
pw = P[3]
cols = [C["muted"], C["muted"], C["muted"], C["accent"], C["accent"], C["accent"]]
for i in range(6):
    w = Es[i][:3, :3] @ SW_W[i]                       # 关节 i 的轴（前面的关节转过以后）
    q = Es[i][:3, :3] @ SW_Q[i] + Es[i][:3, 3]
    if i >= 3:
        line3d(ax, q, w, -0.2, 0.2, cols[i], lw=2.0)
        end = {3: -0.27, 4: 0.23, 5: 0.27}[i]
        lift = np.array([0, 0, 0.07 if i == 5 else 0.012])
        label3d(ax, q + end * w + lift, T(f"轴 {i + 1}", f"axis {i + 1}"), cols[i], fs=9)
    else:
        line3d(ax, q, w, -0.1, 0.1, cols[i], lw=1.6)
Tb = sw_fk(th)
xb = Tb[:3, 0]
arrow3d(ax, Tb[:3, 3], 0.15 * xb, C["x"], lw=1.8)
label3d(ax, Tb[:3, 3] + 0.17 * xb, r"$x_b$", C["x"], fs=11)
ax.scatter(*pw, s=60, color=C["accent"], depthshade=False, zorder=10)
label3d(ax, pw + np.array([-0.1, 0.0, -0.09]), r"$p_w$", C["accent"], fs=12)
label3d(ax, (pw + Tb[:3, 3]) / 2 + np.array([0, 0, 0.04]), r"$D_6$", fs=11)
label3d(ax, P[1] + np.array([0.03, 0.0, 0.02]), T("肩", "shoulder"), fs=9)
label3d(ax, P[2] + np.array([0.03, 0.0, 0.03]), T("肘", "elbow"), fs=9)
ax.plot([0.0, 0.0], [0.0, 0.0], [0.0, 0.16], color=C["muted"], lw=8, alpha=0.5)
ax.text2D(0.0, 0.0, T(r"前三个关节把腕心 $p_w$ 送到位；后三个关节绕 $p_w$ 调整姿态", r"joints 1–3 place the wrist centre $p_w$; joints 4–6 turn the tool about it"),
          transform=ax.transAxes, fontsize=9, color=C["ink"])
equal3d(ax, np.vstack([P, P[-1] + 0.3 * sw_fk(th)[:3, 0]]), pad=0.06, zoom=1.25)
figure(fig, "fig14_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 14.4.2
from _ik import UR_S


def axes_now(Slist, Q, W, th):
    """当前形态下各关节轴：(轴上一点, 方向)。"""
    E, out = np.eye(4), []
    for S, q, w, t in zip(Slist, Q, W, th):
        out.append((E[:3, :3] @ q + E[:3, 3], E[:3, :3] @ w))
        E = E @ exp6(S, t)
    return out


fig = plt.figure(figsize=(9.8, 4.6))
cases = [(T("(a) 球形手腕：轴 4、5、6 交于腕心", "(a) spherical wrist: axes 4, 5, 6 meet at one point"),
          sw_chain, SW_S, SW_Q, SW_W, np.radians([0, 35, -75, 0, 55, 0]), (3, 4, 5), -60),
         (T("(b) UR5e：轴 2、3、4 互相平行", "(b) UR5e: axes 2, 3, 4 are parallel"),
          ur_chain, UR_S, UR_Q, UR_W, np.radians([0, -60, 80, -110, -90, 0]), (1, 2, 3), 35)]
for k, (title, chain_f, Sl, Q, W, th, hi, az) in enumerate(cases):
    _, ax = axes3d(plt, fig=fig, pos=121 + k, elev=22, azim=az)
    chain = chain_f(th)
    draw_chain(ax, chain, "#9aa6ad", lw=5)
    for i, (q, w) in enumerate(axes_now(Sl, Q, W, th)):
        col = C["accent"] if i in hi else C["muted"]
        line3d(ax, q, w, -0.16, 0.16, col, lw=2.4 if i in hi else 1.4)
        label3d(ax, q + 0.2 * w, str(i + 1), col, fs=11, weight="bold")
    ax.text2D(0.02, 0.97, title, transform=ax.transAxes, fontsize=10)
    equal3d(ax, chain, pad=0.1, zoom=1.35)
figure(fig, "fig14_4_2")
plt.close(fig)
