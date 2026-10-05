"""第 20 章示意图共用：Go2 的侧视、正视、俯视简图，G1 的侧视简图，箭头与角度标注。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from _leg import AX, G1, G1_INERTIAL, G1_SOLE, LEGS, fk_links, leg_fk
from bookout import COLORS

C = dict(COLORS)
C.update(steel="#9aa6ad", dark="#5d6b73", light="#d5dbde", orange="#e8913a", purple="#8e6bbf", fill="#eef2f4",
         body="#dfe6ea", blue="#1f77b4", red="#d62728", green="#2ca02c", thigh="#4f7fb0", calf="#2f4f6f")
BODY_L, BODY_H, BODY_W = 0.48, 0.10, 0.20       # 示意：机身外形（长、高、宽）只为画图，取整数量级


def arrow(ax, p, q, color, lw=1.5, ms=10, z=5, ls="-"):
    ax.annotate("", xy=tuple(q), xytext=tuple(p),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms, linestyle=ls),
                zorder=z)


def dim(ax, p, q, text, off, color=None, fs=10, tpos=0.5, toff=(0, 0)):
    """尺寸线：p、q 之间的双向箭头，沿法向偏移 off，文字放在 tpos 处。"""
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = q - p
    n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-12) * off
    a, b = p + n, q + n
    col = color or C["ink"]
    ax.annotate("", xy=tuple(b), xytext=tuple(a), arrowprops=dict(arrowstyle="<->", color=col, lw=0.9, shrinkA=0, shrinkB=0), zorder=4)
    for e, f in ((p, a), (q, b)):
        ax.plot([e[0], f[0]], [e[1], f[1]], color=col, lw=0.5, zorder=3)
    m = a + tpos * (b - a)
    ax.text(m[0] + toff[0], m[1] + toff[1], text, color=col, fontsize=fs, ha="center", va="center", zorder=6)


def angle_arc(ax, c, r, a0, a1, color, text=None, fs=11, tr=1.35, lw=1.2):
    """从方向角 a0 到 a1（弧度）的圆弧，末端带箭头。"""
    t = np.linspace(a0, a1, 40)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw, zorder=6)
    e = np.array([c[0] + r * math.cos(a1), c[1] + r * math.sin(a1)])
    d = math.copysign(1, a1 - a0) * np.array([-math.sin(a1), math.cos(a1)])
    ax.annotate("", xy=tuple(e + 0.002 * d), xytext=tuple(e - 0.02 * r / 0.06 * d),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=9), zorder=6)
    if text:
        am = (a0 + a1) / 2
        ax.text(c[0] + tr * r * math.cos(am), c[1] + tr * r * math.sin(am), text, color=color, fontsize=fs, ha="center", va="center")


def plane(ax, xlim, ylim, axis=False):
    ax.set_aspect("equal")
    if not axis:
        ax.axis("off")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def leg_side_points(leg, th, base=(0.0, 0.0), pitch=0.0):
    """侧视（x–z）：大腿关节、膝（小腿关节）、足端中心，机身原点在 base，机身俯仰 pitch（弧度，绕 y 轴，正为低头）。"""
    t1, t2, t3 = th
    h = np.array([leg_fk(leg, (t1, 0, 0))[0], 0.0])
    k = h + 0.213 * np.array([-math.sin(t2), -math.cos(t2)])
    f = k + 0.213 * np.array([-math.sin(t2 + t3), -math.cos(t2 + t3)])
    R = np.array([[math.cos(pitch), math.sin(pitch)], [-math.sin(pitch), math.cos(pitch)]])
    return [R @ p + np.asarray(base) for p in (h, k, f)]


def draw_leg2(ax, pts, color_t=None, color_c=None, lw=5, alpha=1.0, z=4, foot_r=0.022, joints=True):
    h, k, f = pts
    ax.plot([h[0], k[0]], [h[1], k[1]], color=color_t or C["thigh"], lw=lw, solid_capstyle="round", alpha=alpha, zorder=z)
    ax.plot([k[0], f[0]], [k[1], f[1]], color=color_c or C["calf"], lw=lw * 0.75, solid_capstyle="round", alpha=alpha, zorder=z)
    import matplotlib.patches as mp
    if joints:
        for p in (h, k):
            ax.add_patch(mp.Circle(p, 0.011, facecolor="white", edgecolor=color_t or C["thigh"], lw=1.3, zorder=z + 1, alpha=alpha))
    ax.add_patch(mp.Circle(f, foot_r, facecolor="#3a3a3a", edgecolor="none", zorder=z + 1, alpha=alpha))


def body_side(ax, base=(0.0, 0.0), pitch=0.0, alpha=1.0, z=3):
    """侧视的机身（圆角矩形近似），原点在两髋连线的中点。"""
    import matplotlib.patches as mp
    R = np.array([[math.cos(pitch), math.sin(pitch)], [-math.sin(pitch), math.cos(pitch)]])
    c = np.array([[-BODY_L / 2, -BODY_H / 2], [BODY_L / 2, -BODY_H / 2], [BODY_L / 2 + 0.03, 0.0], [BODY_L / 2, BODY_H / 2],
                  [-BODY_L / 2, BODY_H / 2]])
    w = (R @ c.T).T + np.asarray(base)
    ax.add_patch(mp.Polygon(w, closed=True, facecolor=C["body"], edgecolor=C["dark"], lw=1.0, zorder=z, alpha=alpha))


def ground(ax, x0, x1, y=0.0, step=0.03):
    ax.plot([x0, x1], [y, y], color=C["dark"], lw=1.2, zorder=1)
    for x in np.arange(x0 + 0.01, x1, step):
        ax.plot([x, x - 0.015], [y, y - 0.015], color=C["steel"], lw=0.6, zorder=1)


# ---------------------------------------------------------------- G1 侧视简图
G1_CHAIN = {
    "leg_r": ["pelvis", "right_hip_pitch_link", "right_hip_roll_link", "right_knee_link", "right_ankle_pitch_link"],
    "leg_l": ["pelvis", "left_hip_pitch_link", "left_hip_roll_link", "left_knee_link", "left_ankle_pitch_link"],
    "trunk": ["pelvis", "waist_yaw_link", "torso_link"],
    "arm_r": ["right_shoulder_pitch_link", "right_elbow_link", "right_wrist_roll_link", "right_wrist_yaw_link"],
    "arm_l": ["left_shoulder_pitch_link", "left_elbow_link", "left_wrist_roll_link", "left_wrist_yaw_link"],
}


def g1_points(q, T_sb):
    """G1 主要连杆原点在 {s} 中的位置，以及头顶、手心、脚底前后端。"""
    Tl = fk_links(G1, q, T_sb)
    P = {k: Tl[k][:3, 3].copy() for k in Tl}
    P["head"] = (Tl["torso_link"] @ np.r_[0.0, 0, 0.45, 1])[:3]
    P["neck"] = (Tl["torso_link"] @ np.r_[0.0, 0, 0.30, 1])[:3]
    P["hand_r"] = (Tl["right_wrist_yaw_link"] @ np.r_[0.08, 0, 0, 1])[:3]
    P["hand_l"] = (Tl["left_wrist_yaw_link"] @ np.r_[0.08, 0, 0, 1])[:3]
    for s in ("left", "right"):
        T = Tl[f"{s}_ankle_roll_link"]
        P[f"toe_{s}"] = (T @ np.r_[G1_SOLE[2][0], 0, -0.035, 1])[:3]
        P[f"heel_{s}"] = (T @ np.r_[G1_SOLE[0][0], 0, -0.035, 1])[:3]
    return P


def draw_g1_side(ax, P, color="#4f7fb0", alpha=1.0, lw=4, z=4, far_alpha=0.45):
    """侧视（x–z）：远侧（左）肢体淡一些，近侧（右）肢体实线。"""
    def seg(names, a, w, col=color):
        pts = np.array([P[n][[0, 2]] for n in names])
        ax.plot(pts[:, 0], pts[:, 1], color=col, lw=w, alpha=a, solid_capstyle="round", solid_joinstyle="round", zorder=z)
    seg(["left_hip_roll_link", "left_knee_link", "left_ankle_pitch_link"], alpha * far_alpha, lw)
    seg(["heel_left", "toe_left"], alpha * far_alpha, lw * 0.8)
    seg(["left_shoulder_pitch_link", "left_elbow_link", "hand_l"], alpha * far_alpha, lw * 0.8)
    seg(["pelvis", "torso_link", "neck"], alpha, lw * 1.6)
    seg(["pelvis", "right_hip_roll_link", "right_knee_link", "right_ankle_pitch_link"], alpha, lw)
    seg(["heel_right", "toe_right"], alpha, lw * 0.8)
    seg(["neck", "right_shoulder_pitch_link", "right_elbow_link", "hand_r"], alpha, lw * 0.8)
    import matplotlib.patches as mp
    h = P["head"][[0, 2]]
    n = P["neck"][[0, 2]]
    ax.add_patch(mp.Circle(h, 0.07, facecolor="white", edgecolor=color, lw=1.5, alpha=alpha, zorder=z))
    ax.plot([n[0], h[0]], [n[1], h[1]], color=color, lw=lw * 0.8, alpha=alpha, zorder=z - 1)
