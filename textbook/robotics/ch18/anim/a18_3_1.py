"""动画 18.3.1（配图 18.3.1）：Stewart 平台（几何同算例 11.5.4：万向节在半径 0.5 m 的圆上，方位角 ±10°、110°、130°、230°、250°；
球关节在半径 0.3 m 的圆上，方位角 ±50°、70°、170°、190°、290°；原点位姿平台中心高 0.6 m）。
平台依次作升降、前后、横滚、俯仰、偏航和多轴组合运动；右边六根柱条是逆解 l_i = |p + R b_i − a_i| 给出的腿长，
虚线是电动缸行程 0.55～0.85 m。"""
from manim import *
from wq_anim import *
import numpy as np
import math

RA, RB = 0.5, 0.3
A_DEG = [-10, 10, 110, 130, 230, 250]
B_DEG = [-50, 50, 70, 170, 190, 290]
AA = [np.array([RA * math.cos(math.radians(t)), RA * math.sin(math.radians(t)), 0.0]) for t in A_DEG]
BB = [np.array([RB * math.cos(math.radians(t)), RB * math.sin(math.radians(t)), 0.0]) for t in B_DEG]
COLS = ["#d62728", "#e8a33d", "#2ca02c", "#17becf", "#1f77b4", "#9467bd"]
SC = 5.2
ORG = np.array([-2.9, -2.0, 0.0])
LMIN, LMAX = 0.55, 0.85


AZ, EL = math.radians(-55), math.radians(17)          # 视线的方位角与仰角（正交投影）
RIGHT_ = np.array([-math.sin(AZ), math.cos(AZ), 0.0])
UP_ = np.array([-math.sin(EL) * math.cos(AZ), -math.sin(EL) * math.sin(AZ), math.cos(EL)])


def P(v):
    v = np.asarray(v, dtype=float)
    return ORG + SC * np.array([v @ RIGHT_, v @ UP_, 0.0])


def pose_at(u):
    """u ∈ [0, 6]：0–1 升降，1–2 前后，2–3 横滚，3–4 俯仰，4–5 偏航，5–6 组合。返回 (R, p)。"""
    s = math.sin(2 * math.pi * (u % 1.0))
    x = y = 0.0
    z = 0.6
    r = pt = yw = 0.0
    k = int(min(u, 5.999))
    if k == 0:
        z += 0.07 * s
    elif k == 1:
        x += 0.06 * s
    elif k == 2:
        r = math.radians(15) * s
    elif k == 3:
        pt = math.radians(15) * s
    elif k == 4:
        yw = math.radians(25) * s
    else:
        t = 2 * math.pi * (u - 5.0)
        r, pt, yw = math.radians(8) * math.sin(t), math.radians(6) * math.sin(2 * t + 1), math.radians(10) * math.sin(t + 0.5)
        x, y, z = 0.03 * math.sin(2 * t), 0.03 * math.sin(t + 0.3), 0.6 + 0.04 * math.sin(3 * t)
    R = rot_z(math.degrees(yw)) @ rot_y(math.degrees(pt)) @ rot_x(math.degrees(r))
    return R, np.array([x, y, z])


def hexagon(pts):
    c = sum(pts) / len(pts)
    order = sorted(range(len(pts)), key=lambda i: math.atan2(pts[i][1] - c[1], pts[i][0] - c[0]))
    return [pts[i] for i in order]


class Lesson(Base):
    def construct(self):
        self.title("18.3", "Stewart 平台：给定位姿，六条腿各伸多长", "Stewart platform: leg lengths for a given pose")
        u = ValueTracker(0.0)
        base = Polygon(*[P(a) for a in hexagon(AA)], color=GREY_B, fill_color=GREY_E, fill_opacity=0.8, stroke_width=2)
        self.add(base)

        def platform():
            R, p = pose_at(u.get_value())
            q = [p + R @ b for b in BB]
            g = VGroup()
            for i in range(6):
                g.add(Line(P(AA[i]), P(q[i]), color=COLS[i], stroke_width=7))
            g.add(Polygon(*[P(v) for v in hexagon(q)], color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.55, stroke_width=3))
            for i in range(6):
                g.add(Dot(P(AA[i]), radius=0.05, color=GREY_A), Dot(P(q[i]), radius=0.06, color=WHITE))
            for k, col in enumerate((RED, GREEN, BLUE)):
                g.add(Line(P(p), P(p + 0.12 * R[:, k]), color=col, stroke_width=4))
            return g

        plat = always_redraw(platform)
        self.add(plat)

        # 右边：腿长柱条
        X0, Y0, H = 2.6, -2.2, 3.6                 # 柱条区域：y 从 Y0（0.55 m）到 Y0 + H（0.85 m）

        def ymap(L):
            return Y0 + H * (L - LMIN) / (LMAX - LMIN)

        frame_ = VGroup(DashedLine([X0 - 0.4, ymap(LMIN), 0], [X0 + 3.4, ymap(LMIN), 0], color=GREY_B),
                        DashedLine([X0 - 0.4, ymap(LMAX), 0], [X0 + 3.4, ymap(LMAX), 0], color=GREY_B),
                        Text("0.55 m", font=LATIN, font_size=18, color=GREY_B).next_to([X0 - 0.4, ymap(LMIN), 0], LEFT, buff=0.1),
                        Text("0.85 m", font=LATIN, font_size=18, color=GREY_B).next_to([X0 - 0.4, ymap(LMAX), 0], LEFT, buff=0.1))
        labs = VGroup(*[Text(str(i + 1), font=LATIN, font_size=20, color=COLS[i]).move_to([X0 + 0.55 * i, Y0 - 0.3, 0]) for i in range(6)])
        head = bi(["腿长（逆解）", "leg lengths (inverse kinematics)"], 22).move_to([X0 + 1.4, ymap(LMAX) + 0.5, 0])
        self.add(frame_, labs, head)

        def bars():
            R, p = pose_at(u.get_value())
            g = VGroup()
            for i in range(6):
                L = float(np.linalg.norm(p + R @ BB[i] - AA[i]))
                top = ymap(L)
                r = Rectangle(width=0.36, height=max(top - (Y0 - 0.05), 0.02), color=COLS[i], fill_opacity=0.85, stroke_width=0)
                r.move_to([X0 + 0.55 * i, (top + Y0 - 0.05) / 2, 0])
                g.add(r)
            return g

        bg = always_redraw(bars)
        self.add(bg)
        steps = [("升降：六条腿同时伸缩", "Heave: all six legs extend together"),
                 ("前后：一侧伸长，另一侧缩短", "Surge: one side extends, the other shortens"),
                 ("横滚：绕 x 轴转 ±15°", "Roll: ±15° about x"),
                 ("俯仰：绕 y 轴转 ±15°", "Pitch: ±15° about y"),
                 ("偏航：绕 z 轴转 ±25°，腿长成对地交替变化", "Yaw: ±25° about z; the legs change in alternating pairs"),
                 ("组合运动：控制器每个周期都在做这样的逆解", "Combined motion: the controller solves this every cycle")]
        for k, (zh_, en_) in enumerate(steps):
            self.caption(zh_, en_, wait=0)
            self.play(u.animate.set_value(k + 1.0), run_time=2.9 if k < 5 else 4.0, rate_func=linear)
        self.wait(0.5)
        self.card([["逆解：一步算出六条腿长", "Inverse kinematics: six leg lengths in one step"],
                   MathTex(r"l_i = \| p + R\,b_i - a_i \|,\quad i = 1,\ldots,6", font_size=42),
                   ["正解：由六条腿长求位姿，要用牛顿法", "Forward kinematics: the pose from six lengths needs Newton's method"]])
