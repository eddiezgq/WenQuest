"""6.7 节的示意图。

图 6.7.1：(a) 差速 AGV 依次“前进 ε、左转 ε、后退 ε、右转 ε”（图中 ε = 0.4，便于看清），回到原来的朝向，
          却向右平移了约 ε²：这就是 ε²[V_f, V_r]。(b) 侧移量 |y| 与 ε 的关系（对数坐标），与 ε² 的直线对照。
"""
import math

import numpy as np

from _screw import C
from bookout import T, figure, style

plt = style()


def run(e, n=40):
    """返回车体中心的轨迹和四个阶段结束时的位姿 (x, y, θ)。"""
    x, y, th = 0.0, 0.0, 0.0
    path, poses = [(x, y)], [(x, y, th)]
    for kind, sgn in (("f", 1), ("r", 1), ("f", -1), ("r", -1)):
        for _ in range(n):
            if kind == "f":
                x += sgn * e / n * math.cos(th)
                y += sgn * e / n * math.sin(th)
            else:
                th += sgn * e / n
            path.append((x, y))
        poses.append((x, y, th))
    return np.array(path), poses


def agv(ax, x, y, th, color, alpha=1.0, ls="-"):
    L, W = 0.12, 0.09
    P = np.array([[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2], [-L / 2, -W / 2]])
    R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
    Q = (R @ P.T).T + [x, y]
    ax.plot(Q[:, 0], Q[:, 1], color=color, lw=1.4, alpha=alpha, ls=ls)
    nose = R @ np.array([L / 2 + 0.05, 0]) + [x, y]
    ax.annotate("", xy=nose, xytext=(x, y), arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, alpha=alpha))


fig, (ax, bx) = plt.subplots(1, 2, figsize=(9.0, 3.8), gridspec_kw=dict(width_ratios=[1.25, 1]))
e = 0.4
path, poses = run(e)
ax.set_aspect("equal")
ax.axis("off")
agv(ax, *poses[0], C["muted"], 0.9, "--")
agv(ax, *poses[-1], C["accent"])
ax.plot(path[:, 0], path[:, 1], color=C["x"], lw=1.6)
labels = [T("① 前进 ε", "① forward ε"), T("② 左转 ε", "② turn left ε"), T("③ 后退 ε", "③ back ε"), T("④ 右转 ε", "④ turn right ε")]
spots = [(0.12, 0.04), (0.42, 0.04), (0.16, -0.16), (-0.12, -0.24)]
for lab, o in zip(labels, spots):
    ax.text(*o, lab, fontsize=9.5, color=C["ink"])
ax.annotate("", xy=poses[-1][:2], xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["z"], lw=1.8))
ax.text(-0.30, -0.10, T("净位移 ≈ ε²\n（向右平移）", "net ≈ ε²\n(a shift to the right)"), fontsize=9.5, color=C["z"])
ax.text(-0.30, 0.16, T("(a) ε = 0.4（m 与 rad）", "(a) ε = 0.4 (m and rad)"), fontsize=10)
ax.text(-0.30, 0.10, T("虚线：起点；金色：终点", "dashed: start; gold: end"), fontsize=9, color=C["muted"])
ax.set_xlim(-0.32, 0.62)
ax.set_ylim(-0.30, 0.20)

es = np.geomspace(0.02, 0.6, 30)
ys = [abs(run(x, 200)[1][-1][1]) for x in es]
bx.loglog(es, ys, "o", ms=3.5, color=C["x"], label=T("实际侧移 |y|", "actual side shift |y|"))
bx.loglog(es, es ** 2, color=C["z"], lw=1.2, label="ε²")
bx.set_xlabel(T("ε（前进的距离 m，转过的角度 rad）", "ε (distance in m, angle in rad)"))
bx.set_ylabel(T("|y| / m", "|y| / m"))
bx.set_title(T("(b) 侧移与 ε² 成正比", "(b) the side shift grows as ε²"), fontsize=10)
bx.legend(frameon=False, fontsize=9)
bx.grid(True, which="both", lw=0.3, alpha=0.5)
fig.tight_layout()
figure(fig, "fig6_7_1")
plt.close(fig)
