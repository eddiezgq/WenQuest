"""11.2 节的示意图。

图 11.2.1：五个平面机构及其计数：四杆机构、曲柄滑块机构、五杆机构、平行四边形加一根曲柄、剪叉式升降台。
图 11.2.2：三个空间机构：Delta（一条支链的平行四边形）、Stewart 平台 6-UPS、本内特机构（尺寸与程序 11.2.1 相同）。
"""
import math

import numpy as np

from _fig11 import C, bar, circ_int, clean3d, ground, pin, plane
from bookout import T, figure, style

plt = style()


def slider(ax, p, w=0.09, h=0.05, color=None):
    import matplotlib.patches as mp
    ax.add_patch(mp.Rectangle((p[0] - w / 2, p[1] - h / 2), w, h, facecolor=C["fill"], edgecolor=color or C["ink"], lw=1.3, zorder=5))


def rail(ax, x0, x1, y):
    ax.plot([x0, x1], [y, y], color=C["dark"], lw=1.2, zorder=2)
    for xx in np.arange(x0, x1, 0.04):
        ax.plot([xx, xx - 0.02], [y, y - 0.025], color=C["dark"], lw=0.7, zorder=2)


fig, axs = plt.subplots(1, 5, figsize=(11.5, 3.3))
lab = dict(fontsize=9.5, color=C["ink"], ha="center")
# (a) 四杆机构
ax = axs[0]
A, D = np.array([0.0, 0]), np.array([0.40, 0])
B = 0.15 * np.array([math.cos(1.05), math.sin(1.05)])
Cc = circ_int(B, 0.35, D, 0.30, 1)
for p, q, col in ((A, B, C["z"]), (B, Cc, C["accent"]), (Cc, D, C["z"])):
    bar(ax, p, q, col)
bar(ax, A, D, C["muted"], lw=1.2, ls="--")
for p in (A, D):
    ground(ax, p, 0.08)
for p in (A, B, Cc, D):
    pin(ax, p, 0.016)
plane(ax, (-0.12, 0.52), (-0.16, 0.5))
ax.text(0.2, 0.44, T("(a) 四杆机构", "(a) four-bar"), **lab)
ax.text(0.2, -0.2, "N = 4, J = 4\n$M = 3\\cdot 3 - 2\\cdot 4 = 1$", **lab)
# (b) 曲柄滑块
ax = axs[1]
B = 0.1 * np.array([math.cos(1.05), math.sin(1.05)])
xs = B[0] + math.sqrt(0.09 - B[1] ** 2)
rail(ax, 0.15, 0.45, -0.025)
bar(ax, A, B, C["z"])
bar(ax, B, (xs, 0), C["accent"])
slider(ax, (xs, 0))
ground(ax, A, 0.08)
for p in (A, B, (xs, 0)):
    pin(ax, p, 0.016)
plane(ax, (-0.12, 0.5), (-0.16, 0.5))
ax.text(0.19, 0.44, T("(b) 曲柄滑块机构", "(b) slider-crank"), **lab)
ax.text(0.19, -0.2, "N = 4, J = 4 (3R + P)\n$M = 1$", **lab)
# (c) 五杆机构
ax = axs[2]
A5, E5 = np.array([0.0, 0]), np.array([0.30, 0])
B5 = 0.2 * np.array([math.cos(math.radians(110)), math.sin(math.radians(110))])
D5 = E5 + 0.2 * np.array([math.cos(math.radians(70)), math.sin(math.radians(70))])
C5 = circ_int(B5, 0.3, D5, 0.3, -1)
for p, q, col in ((A5, B5, C["z"]), (B5, C5, C["accent"]), (C5, D5, C["accent"]), (D5, E5, C["z"])):
    bar(ax, p, q, col)
for p in (A5, E5):
    ground(ax, p, 0.08)
for p in (A5, B5, C5, D5, E5):
    pin(ax, p, 0.016)
ax.plot(*C5, "o", color=C["x"], ms=5, zorder=8)
plane(ax, (-0.17, 0.47), (-0.16, 0.5))
ax.text(0.15, 0.44, T("(c) 五杆机构", "(c) five-bar"), **lab)
ax.text(0.15, -0.2, "N = 5, J = 5\n$M = 3\\cdot 4 - 2\\cdot 5 = 2$", **lab)
# (d) 平行四边形加一根曲柄
ax = axs[3]
e = 0.25 * np.array([math.cos(1.05), math.sin(1.05)])
G = [np.array([0.0, 0]), np.array([0.3, 0]), np.array([0.6, 0])]
bar(ax, G[0] + e, G[2] + e, C["accent"])
for k, g in enumerate(G):
    bar(ax, g, g + e, C["x"] if k == 1 else C["z"])
    ground(ax, g, 0.08)
    pin(ax, g, 0.016)
    pin(ax, g + e, 0.016)
plane(ax, (-0.1, 0.8), (-0.16, 0.5))
ax.text(0.35, 0.44, T("(d) 平行四边形加一根曲柄（红）", "(d) parallelogram + extra crank (red)"), **lab)
ax.text(0.35, -0.2, T("N = 5, J = 6\n公式 M = 0，实际能动，M = 1", "N = 5, J = 6\nformula M = 0, yet it moves: M = 1"), **lab)
# (e) 剪叉式升降台
ax = axs[4]
a, phi = 0.2, math.radians(35)
c, s = math.cos(phi), math.sin(phi)
P0, P1, P2, P3 = np.array([0, 0.0]), np.array([2 * a * c, 0]), np.array([0, 2 * a * s]), np.array([2 * a * c, 2 * a * s])
rail(ax, -0.05, 0.42, -0.025)
bar(ax, P0, P3, C["z"])
bar(ax, P1, P2, C["accent"])
ax.plot([-0.05, 0.42], [2 * a * s + 0.03] * 2, color=C["dark"], lw=6, solid_capstyle="butt", zorder=2)
slider(ax, P1)
slider(ax, P3)
ground(ax, P0, 0.08)
for p in (P0, P1, P2, P3, (P0 + P3) / 2):
    pin(ax, p, 0.016)
plane(ax, (-0.12, 0.48), (-0.16, 0.5))
ax.text(0.18, 0.44, T("(e) 剪叉式升降台", "(e) scissor lift"), **lab)
ax.text(0.18, -0.2, "N = 6, J = 7 (5R + 2P)\n$M = 3\\cdot 5 - 2\\cdot 7 = 1$", **lab)
fig.subplots_adjust(wspace=0.05, left=0.0, right=1.0, top=1.0, bottom=0.0)
figure(fig, "fig11_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 11.2.2
fig = plt.figure(figsize=(11.0, 4.2))
# (a) Delta：三条支链，平行四边形（数据同程序 11.2.1）
ax = fig.add_subplot(1, 3, 1, projection="3d")
clean3d(ax, 0.42, elev=14, azim=-50, zoom=1.35)
Rb, Rp, La, Lb, w, th = 0.15, 0.04, 0.22, 0.5, 0.06, 0.18752297743898505
p = np.array([0, 0, -0.42])
tri = np.array([[Rb * math.cos(t), Rb * math.sin(t), 0] for t in np.radians([0, 120, 240, 0])]) * 1.35
ax.plot(*tri.T, color=C["dark"], lw=2)
ptri = np.array([[Rp * math.cos(t), Rp * math.sin(t), 0] for t in np.radians([0, 120, 240, 0])]) * 1.6 + p
ax.plot(*ptri.T, color=C["accent"], lw=2.5)
for k in range(3):
    ph = 2 * math.pi * k / 3
    er, et = np.array([math.cos(ph), math.sin(ph), 0]), np.array([-math.sin(ph), math.cos(ph), 0])
    B = Rb * er
    E = B + La * (math.cos(th) * er - math.sin(th) * np.array([0, 0, 1]))
    P = p + Rp * er
    ax.plot(*np.array([B, E]).T, color=C["z"], lw=4)
    ax.plot(*np.array([E - w / 2 * et, E + w / 2 * et]).T, color=C["z"], lw=2)
    for sgn in (1, -1):
        ax.plot(*np.array([E + sgn * w / 2 * et, P + sgn * w / 2 * et]).T, color=C["muted"], lw=1.5)
        ax.scatter(*(E + sgn * w / 2 * et), color=C["x"], s=10)
        ax.scatter(*(P + sgn * w / 2 * et), color=C["x"], s=10)
    ax.scatter(*B, color=C["ink"], s=14)
ax.text(0.0, 0.0, 0.08, T("主动臂（R）", "upper arms (R)"), fontsize=9, color=C["z"])
ax.text2D(0.6, 0.14, T("← 动平台", "← platform"), transform=ax.transAxes, fontsize=9, color=C["accent"])
ax.text2D(0.02, 0.02, T("红点为球关节；平行四边形使动平台只平移", "red dots: ball joints; the parallelograms keep the platform from turning"),
          transform=ax.transAxes, fontsize=8.5)
ax.set_title(T("(a) Delta：3 × (R + 两根 S–S 杆)", "(a) Delta: 3 × (R + two S–S rods)"), fontsize=10, pad=-6)
# (b) Stewart 6-UPS
ax = fig.add_subplot(1, 3, 2, projection="3d")
clean3d(ax, 0.5, elev=16, azim=-60, zoom=1.35)
ra, rb = 0.5, 0.3
aa = np.array([ra * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-10, 10, 110, 130, 230, 250])]) - np.array([0, 0, 0.3])
bb = np.array([rb * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-50, 50, 70, 170, 190, 290])]) + np.array([0, 0, 0.3])
ax.plot(*np.vstack([aa, aa[:1]]).T, color=C["dark"], lw=2)
ax.plot(*np.vstack([bb, bb[:1]]).T, color=C["accent"], lw=2.5)
for i in range(6):
    m = aa[i] + 0.45 * (bb[i] - aa[i])
    ax.plot(*np.array([aa[i], m]).T, color=C["z"], lw=4)
    ax.plot(*np.array([m - 0.05 * (bb[i] - aa[i]), bb[i]]).T, color=C["muted"], lw=2)
    ax.scatter(*aa[i], color=C["y"], s=14)
    ax.scatter(*bb[i], color=C["x"], s=14)
ax.text2D(0.02, 0.02, T("绿：万向节 U；蓝灰之间：移动关节 P；红：球关节 S", "green: U joints; blue/grey: P joints; red: S joints"),
          transform=ax.transAxes, fontsize=8.5)
ax.set_title(T("(b) Stewart 平台 6-UPS", "(b) Stewart platform 6-UPS"), fontsize=10, pad=-6)
# (c) 本内特机构
ax = fig.add_subplot(1, 3, 3, projection="3d")
aB, alB, beB = 0.3, math.radians(30), math.radians(60)
bB = aB * math.sin(beB) / math.sin(alB)
KB = math.sin((beB + alB) / 2) / math.sin((beB - alB) / 2)


def dhA(t, a_, al):
    ct, st, ca, sa = math.cos(t), math.sin(t), math.cos(al), math.sin(al)
    return np.array([[ct, -st * ca, st * sa, a_ * ct], [st, ct * ca, -ct * sa, a_ * st], [0, sa, ca, 0], [0, 0, 0, 1]])


def bennett_frames(t1):
    t2 = 2 * math.atan(KB / math.tan(t1 / 2))
    th4 = [t1, t2, -t1, -t2]
    Tc, fr = np.eye(4), []
    for k in range(4):
        fr.append(Tc.copy())
        Tc = Tc @ dhA(th4[k], [aB, bB][k % 2], [alB, beB][k % 2])
    return fr


for t1, alpha in ((1.0, 1.0), (1.6, 0.3), (0.6, 0.3)):
    fr = bennett_frames(t1)
    pts = [f[:3, 3] for f in fr] + [fr[0][:3, 3]]
    # 连杆是相邻两轴的公垂线：从轴 k 上的原点沿 x 到轴 k+1
    for k in range(4):
        q0 = fr[k][:3, 3]
        q1 = fr[(k + 1) % 4][:3, 3]
        ax.plot(*np.array([q0, q1]).T, color=C["z"] if k % 2 == 0 else C["accent"], lw=3.5 if alpha == 1 else 1.5, alpha=alpha)
    if alpha == 1:
        for k in range(4):
            zk, qk = fr[k][:3, 2], fr[k][:3, 3]
            ax.plot(*np.array([qk - 0.12 * zk, qk + 0.12 * zk]).T, color=C["x"], lw=2)
            sk = -1 if k == 3 else 1                              # R4 的标注放在轴的另一端，免得与 R3 重叠
            ax.text(*(qk + sk * 0.17 * zk), f"$R_{k + 1}$", fontsize=10, color=C["x"])
allp = np.array([f[:3, 3] for f in bennett_frames(1.0)])
c0 = allp.mean(0)
L0 = 0.5
ax.set_xlim(c0[0] - L0, c0[0] + L0)
ax.set_ylim(c0[1] - L0, c0[1] + L0)
ax.set_zlim(c0[2] - L0, c0[2] + L0)
ax.set_box_aspect((1, 1, 1), zoom=1.35)
ax.view_init(elev=22, azim=-35)
ax.set_axis_off()
ax.text2D(0.02, 0.02, T("a = 0.3 m, α = 30°；b = a sinβ/sinα，β = 60°；淡色为另外两个位置",
                        "a = 0.3 m, α = 30°; b = a sinβ/sinα, β = 60°; faint: two other positions"), transform=ax.transAxes, fontsize=8.5)
ax.set_title(T("(c) 本内特机构：公式 −2，实际 1", "(c) Bennett linkage: formula −2, actually 1"), fontsize=10, pad=-6)
fig.subplots_adjust(wspace=0.0, left=0.0, right=1.0, top=0.95, bottom=0.02)
figure(fig, "fig11_2_2")
plt.close(fig)
