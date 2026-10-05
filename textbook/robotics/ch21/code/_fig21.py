"""第 21 章示意图共用：颜色、箭头、四旋翼 X2 的俯视与侧视简图。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = dict(COLORS)
C.update(steel="#9aa6ad", dark="#5d6b73", light="#d5dbde", orange="#e8913a", purple="#8e6bbf", fill="#eef2f4",
         body="#dfe6ea", blue="#1f77b4", red="#d62728", green="#2ca02c", rotor="#c9d3d8", up="#1f77b4", down="#d62728")
ROTOR_R = 0.13            # MJCF 中旋翼碰撞体（扁椭球）的半径，m；画图时用作桨盘半径
BODY_HALF = (0.16, 0.04)  # MJCF 中机身质量体（椭球）的半轴，m


def arrow(ax, p, q, color, lw=1.6, ms=11, z=5, ls="-"):
    ax.annotate("", xy=tuple(q), xytext=tuple(p),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms, linestyle=ls),
                zorder=z)


def spin(ax, c, r, ccw, color, lw=1.1):
    """桨盘边缘的一段带箭头圆弧，表示旋翼的转向（俯视）。"""
    a0, a1 = (math.radians(200), math.radians(320)) if ccw else (math.radians(320), math.radians(200))
    t = np.linspace(a0, a1, 40)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw, zorder=4)
    e = np.array([c[0] + r * math.cos(a1), c[1] + r * math.sin(a1)])
    d = (1 if ccw else -1) * np.array([-math.sin(a1), math.cos(a1)])
    arrow(ax, e - 0.02 * d, e + 0.004 * d, color, lw, 9)


def top_view(ax, r, sig, scale=1.0, thrust=None, numbers=True, spin_arrows=True, body=True, rotor_r=ROTOR_R):
    """X2 俯视简图：x_b 向右（机头），y_b 向上（左侧）。thrust：四个推力（N），按大小给桨盘着色。"""
    for i, ri in enumerate(r):
        x, y = ri[0], ri[1]
        ax.plot([0, x], [0, y], color=C["dark"], lw=3.0, zorder=2, solid_capstyle="round")
        fc = C["rotor"]
        if thrust is not None:
            d = thrust[i] - np.mean(thrust)
            fc = C["up"] if d > 1e-9 else C["down"] if d < -1e-9 else C["rotor"]
        circ = __import__("matplotlib").patches.Circle((x, y), rotor_r, fc=fc, ec=C["dark"], lw=0.8,
                                                      alpha=0.35 if thrust is not None else 0.6, zorder=3)
        ax.add_patch(circ)
        ax.plot(x, y, "o", color=C["ink"], ms=3, zorder=5)
        if spin_arrows:
            spin(ax, (x, y), rotor_r * 0.78, sig[i] < 0, C["purple"])
        if numbers:
            ax.text(x + 0.03 * np.sign(x), y + 0.035 * np.sign(y), str(i + 1), fontsize=12, color=C["ink"],
                    ha="center", va="center", zorder=6, fontweight="bold")
    if body:
        e = __import__("matplotlib").patches.Ellipse((0, 0), 2 * BODY_HALF[0], 2 * BODY_HALF[1], fc=C["body"], ec=C["dark"],
                                                     lw=0.9, zorder=3)
        ax.add_patch(e)
        ax.plot([BODY_HALF[0] - 0.02, BODY_HALF[0] + 0.01], [0, 0], color=C["accent"], lw=3, zorder=4)   # 机头相机


def frame2(ax, o, L, labels=("$x_b$", "$y_b$"), fs=12, lw=1.4, dx=(0.01, -0.012)):
    arrow(ax, o, (o[0] + L, o[1]), C["x"], lw, 10)
    arrow(ax, o, (o[0], o[1] + L), C["y"], lw, 10)
    ax.text(o[0] + L + dx[0], o[1] + dx[1], labels[0], color=C["x"], fontsize=fs, va="center")
    ax.text(o[0] - 0.012, o[1] + L + 0.02, labels[1], color=C["y"], fontsize=fs, ha="center")


def side_drone(ax, o, ang, s=1.0, color=None, arms=0.2, hub=0.05):
    """侧视的四旋翼简图：中心 o，机身转角 ang（弧度，逆时针为正，图中 x 向右、z 向上），尺度 s。返回机体 z 轴方向。"""
    col = color or C["dark"]
    R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    o = np.asarray(o, float)
    for sx in (-1, 1):
        a = o + R @ np.array([sx * arms * s, 0.0])
        ax.plot([o[0], a[0]], [o[1], a[1]], color=col, lw=3, zorder=3, solid_capstyle="round")
        p1 = a + R @ np.array([-0.07 * s, 0.025 * s])
        p2 = a + R @ np.array([0.07 * s, 0.025 * s])
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=col, lw=2.0, zorder=3)
        m = a + R @ np.array([0, 0.025 * s])
        ax.plot([a[0], m[0]], [a[1], m[1]], color=col, lw=1.5, zorder=3)
    b = __import__("matplotlib").patches.Ellipse(tuple(o), 2 * hub * s * 1.6, hub * s, angle=math.degrees(ang),
                                                 fc=C["body"], ec=col, lw=1.0, zorder=4)
    ax.add_patch(b)
    return R @ np.array([0.0, 1.0])
