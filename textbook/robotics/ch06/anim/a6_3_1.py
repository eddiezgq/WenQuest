"""动画 6.3.1（配图 6.3.1）：刚体以一个运动旋量匀速运动。先画出刚体上若干点的速度 v + ω × x，
看起来杂乱无章；再找出速度与 ω 平行的那些点，它们排成一条直线，即瞬时螺旋轴（莫齐定理）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([0.0, -1.6, 0])
SC = 1.6
W = np.array([0.0, 0.0, 0.8])            # 角速度 rad/s（沿 z）
QA = np.array([0.6, -0.9, 0.0])          # 螺旋轴上的一点
H = 0.4                                  # 节距 m/rad
V = -np.cross(W, QA) + H * W             # 原点处那一点的速度


def vel(x):
    return V + np.cross(W, x)


def rot(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def moved(x, t):
    """点 x 在螺旋运动下 t 秒后的位置。"""
    return QA + rot(W[2] * t) @ (x - QA) + H * W * t


PTS = [np.array([x, y, z]) for x in (-0.6, 0.6) for y in (-0.6, 0.6) for z in (0.0, 0.8)] + [QA + np.array([0, 0, 0.0]), QA + np.array([0, 0, 0.8])]


def body(t):
    P = [proj3(moved(x, t), O, SC) for x in PTS[:8]]
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    return VGroup(*[Polygon(*[P[i] for i in f], color=STEEL, fill_color=NAVY, fill_opacity=0.12, stroke_width=2) for f in faces])


def arrows(t, axis_only=False):
    g = VGroup()
    for i, x in enumerate(PTS):
        if axis_only and i < 8:
            continue
        y = moved(x, t)
        on_axis = i >= 8
        g.add(Dot(proj3(y, O, SC), radius=0.05, color=YELLOW if on_axis else WHITE))
        g.add(Arrow(proj3(y, O, SC), proj3(y + 0.9 * vel(y), O, SC), buff=0, color=BLUE if on_axis else ORANGE,
                    stroke_width=5, max_tip_length_to_length_ratio=0.2))
    return g


class Lesson(Base):
    def construct(self):
        self.title("6.3", "运动旋量：刚体速度的螺旋结构", "Twists: the screw structure of rigid-body velocity")
        b = body(0)
        self.play(Create(b))
        a = arrows(0)
        self.play(FadeIn(a), run_time=1.2)
        self.caption("刚体上各点的速度 v + ω × x 各不相同", "Each point's velocity v + ω × x is different")
        t = ValueTracker(0.0)
        b.add_updater(lambda m: m.become(body(t.get_value())))
        a.add_updater(lambda m: m.become(arrows(t.get_value())))
        self.play(t.animate.set_value(1.5), run_time=3, rate_func=linear)
        self.caption("但有一条直线，其上各点的速度都与 ω 平行（蓝色）", "Yet on one line every velocity is parallel to ω (blue)")
        line = always_redraw(lambda: DashedLine(proj3(QA + [0, 0, -0.4], O, SC), proj3(QA + [0, 0, 2.6], O, SC), color=YELLOW, stroke_width=4))
        self.play(Create(line))
        self.play(t.animate.set_value(3.0), run_time=3, rate_func=linear)
        self.caption("这就是瞬时螺旋轴：绕它转动，同时沿它移动", "The instantaneous screw axis: turning about it while sliding along it")
        trace = always_redraw(lambda: VMobject(color=RED, stroke_width=3).set_points_as_corners(
            [proj3(moved(PTS[1], s), O, SC) for s in np.linspace(0, max(t.get_value(), 1e-3), 60)]))
        self.add(trace)
        self.play(t.animate.set_value(5.5), run_time=4, rate_func=linear)
        b.clear_updaters()
        a.clear_updaters()
        self.card([["莫齐定理（1763）", "Mozzi's theorem (1763)"],
                   ["刚体任一瞬间的运动都是绕某一根轴的螺旋运动", "At any instant a rigid body moves by a screw motion about some axis"],
                   MathTex(r"\mathcal V = (\omega,\ v) = (\hat s,\ -\hat s\times q + h\hat s)\,\dot\theta", font_size=44)])
