"""14.6 节的示意图。

图 14.6.1：SCARA（俯视）。(a) 算例 14.6.1 的右手、左手两种构型，工具都到达同一点、同一朝向；
           (b) 考虑关节限位（关节 1 ±140°、关节 2 ±145°）后，水平工作区内两种构型都能用的区域和只有一种能用的区域。
图 14.6.2：Delta。(a) 支链 1 在静止位置的两个解：主动臂端点绕铰点轴转动走一个圆，到 P′₁ 的距离为 Lb 的点有两个；
           阴影是关节限位 −40°～90°，肘部朝内的解在限位以外；(b) 动平台沿拾取路径（半径 0.12 m 的水平圆）走一圈时三根主动臂的转角。
"""
import math

import numpy as np

from _fig14 import BLUE2, C, PALE, arm_pts, base_mark, draw_arm, plane
from _ik import DELTA, SC, delta_leg_sp3, ik2r, scara_ik
from bookout import T, figure, style

plt = style()
L1s, L2s = SC["L1"], SC["L2"]
lim1, lim2 = math.radians(140), math.radians(145)

# ---------------------------------------------------------------- 图 14.6.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.8))
plane(a1, (-0.25, 0.68), (-0.42, 0.62))
tgt = (0.40, 0.20, 0.15, math.radians(30))
for s in scara_ik(*tgt, 0.242):
    col = C["z"] if s[1] > 0 else C["accent"]
    pts = arm_pts(s[:2], (L1s, L2s))
    draw_arm(a1, pts, col, lw=6)
    e = pts[1]
    a1.text(e[0] + (0.02 if s[1] > 0 else -0.2), e[1] + (-0.06 if s[1] > 0 else 0.03),
            T("右手构型（θ₂ > 0）", "right-handed (θ₂ > 0)") if s[1] > 0 else T("左手构型（θ₂ < 0）", "left-handed (θ₂ < 0)"), fontsize=9.5, color=col)
base_mark(a1)
a1.plot(tgt[0], tgt[1], "o", color=C["x"], ms=7, zorder=9)
d = np.array([math.cos(tgt[3]), math.sin(tgt[3])])
a1.annotate("", xy=np.array(tgt[:2]) + 0.12 * d, xytext=tgt[:2], arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.4))
a1.text(tgt[0] + 0.1, tgt[1] + 0.09, r"$\varphi = 30^\circ$", fontsize=10, color=C["x"])
a1.plot([0, tgt[0]], [0, tgt[1]], color=C["muted"], lw=0.8, ls=":")
a1.text(-0.24, 0.57, T("(a) 同一目标的两种构型（俯视）", "(a) two configurations for one target (top view)"), fontsize=10)
# (b)
plane(a2, (-0.68, 0.68), (-0.68, 0.68))
h = 0.005
g = np.arange(-0.62, 0.62 + h / 2, h)
img = np.zeros((len(g), len(g)))
for i, y in enumerate(g):
    for j, x in enumerate(g):
        ss = ik2r(x, y, L1s, L2s)
        okr = any(t[1] > 0 and abs(t[0]) <= lim1 and abs(t[1]) <= lim2 for t in ss)
        okl = any(t[1] < 0 and abs(t[0]) <= lim1 and abs(t[1]) <= lim2 for t in ss)
        img[i, j] = 3 if (okr and okl) else (1 if okr else (2 if okl else 0))
from matplotlib.colors import ListedColormap
cmap = ListedColormap(["#ffffff", "#9ecae1", "#f2cf8a", "#dfe7d3"])
a2.imshow(img, origin="lower", extent=(g[0] - h / 2, g[-1] + h / 2, g[0] - h / 2, g[-1] + h / 2), cmap=cmap, vmin=0, vmax=3, interpolation="nearest")
base_mark(a2, s=0.025)
a2.plot(-0.30, 0.35, "o", color=C["x"], ms=6)
a2.text(-0.29, 0.38, "Q", fontsize=11, color=C["x"])
for col, name, y in (("#dfe7d3", T("两种构型都可用", "both usable"), -0.5), ("#9ecae1", T("只有右手构型", "right-handed only"), -0.57),
                     ("#f2cf8a", T("只有左手构型", "left-handed only"), -0.64)):
    a2.add_patch(plt.Rectangle((0.28, y - 0.018), 0.04, 0.036, facecolor=col, edgecolor=C["muted"], lw=0.5))
    a2.text(0.34, y - 0.012, name, fontsize=9)
a2.text(-0.66, 0.6, T("(b) 计入关节限位后的水平工作区", "(b) horizontal workspace with joint limits"), fontsize=10)
figure(fig, "fig14_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 14.6.2
D = DELTA
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.6), gridspec_kw={"width_ratios": [1.0, 1.15]})
plane(a1, (-0.12, 0.62), (-0.55, 0.32))
p0 = np.array([0, 0, -0.42])
sols = delta_leg_sp3(0, p0)
Bk = np.array([D["Rb"], 0.0])                                # 铰点（支链 1 平面内：横坐标沿 e1，纵坐标为 z）
Pk = np.array([D["Rp"], p0[2]])
t = np.linspace(0, 2 * math.pi, 300)
a1.plot(Bk[0] + D["La"] * np.cos(t), Bk[1] + D["La"] * np.sin(t), color=BLUE2, lw=1.2, ls="--")
a1.plot(Pk[0] + D["Lb"] * np.cos(t), Pk[1] + D["Lb"] * np.sin(t), color=C["muted"], lw=1.0, ls=":")
wedge = np.linspace(math.radians(40), math.radians(-90), 60)       # 限位 −40°～90°（向下为正）：方向角 = −θ
a1.fill(np.r_[Bk[0], Bk[0] + D["La"] * np.cos(wedge)], np.r_[Bk[1], Bk[1] + D["La"] * np.sin(wedge)], color=PALE, zorder=0)
for th in sols:
    E = Bk + D["La"] * np.array([math.cos(th), -math.sin(th)])
    ok = math.radians(-40) <= th <= math.radians(90)
    col = C["z"] if ok else C["accent"]
    a1.plot([Bk[0], E[0]], [Bk[1], E[1]], color=col, lw=5, solid_capstyle="round")
    a1.plot([E[0], Pk[0]], [E[1], Pk[1]], color=col, lw=2, ls="-" if ok else "--")
    a1.plot(*E, "o", color=col, ms=5)
    a1.text(E[0] + 0.02, E[1] + 0.02, T(f"θ₁ = {math.degrees(th):.1f}°", f"θ₁ = {math.degrees(th):.1f}°"), fontsize=9.5, color=col)
a1.plot([-0.1, 0.6], [0, 0], color=C["ink"], lw=1.0)
a1.plot(*Bk, "o", color=C["ink"], ms=5)
a1.text(Bk[0] - 0.02, Bk[1] + 0.03, T("铰点", "hinge"), fontsize=9)
a1.plot(*Pk, "s", color=C["x"], ms=6)
a1.text(Pk[0] + 0.02, Pk[1] - 0.04, "P′₁", fontsize=11, color=C["x"])
a1.text(-0.11, 0.27, T("(a) 支链 1 的竖直平面：两个解", "(a) leg 1, vertical plane: two solutions"), fontsize=10)
a1.text(0.28, -0.36, T("浅蓝阴影：关节限位以内", "shaded: within the joint limits"), fontsize=8.5, color=C["muted"])
# (b)
ang = np.arange(0, 361, 1.0)
TH = np.array([[math.degrees(min(delta_leg_sp3(k, np.array([0.12 * math.cos(math.radians(a)), 0.12 * math.sin(math.radians(a)), -0.42])),
                                  key=lambda x: abs(x - 0.2))) for k in range(3)] for a in ang])
for k, col in enumerate((C["x"], C["y"], C["z"])):
    a2.plot(ang, TH[:, k], color=col, lw=1.8, label=T(f"主动臂 {k + 1}", f"arm {k + 1}"))
a2.axhline(math.degrees(0.187523), color=C["muted"], lw=0.8, ls=":")
a2.set_xlim(0, 360)
a2.set_xticks(range(0, 361, 60))
a2.set_xlabel(T("路径上的方位角 / (°)", "position on the path / (°)"), fontsize=10)
a2.set_ylabel(T("主动臂转角 θₖ / (°)", "arm angle θₖ / (°)"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3)
a2.spines["top"].set_visible(False)
a2.spines["right"].set_visible(False)
a2.set_title(T("(b) 沿拾取路径一圈", "(b) once round the pick path"), fontsize=10, loc="left", pad=24)
figure(fig, "fig14_6_2")
plt.close(fig)
