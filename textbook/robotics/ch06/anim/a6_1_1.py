"""动画 6.1.1（配图 6.1.1）：零件从输送带到夹具的位移，等价于一次螺旋运动：绕轴转 θ，同时沿轴移 d。
先演示“先转后移”和“先移后转”两种分步做法到达同一位姿，再演示两者同时进行的螺旋运动，零件中心画出螺旋线。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([0.5, -1.0, 0])
SC = 8.0
Q = np.array([0.1, 0.0, 0.0])          # 螺旋轴上的一点 (m)
P1 = np.array([0.5, -0.2, 0.1])        # 零件中心的起始位置 (m)
TH = math.pi / 2                       # 转角
DD = 0.15                              # 沿轴的平移 (m)


def rz(t):
    return np.array([[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]])


def P(x):
    return proj3(x, O, SC)


def part(a, z, color=STEEL, op=0.35):
    """零件：绕轴转过 a、沿轴升高 z 之后的长方体。"""
    hx, hy, hz = 0.07, 0.045, 0.03
    R = rz(a)
    c = Q + R @ (P1 - Q) + np.array([0, 0, z])
    V = [c + R @ np.array([x, y, w]) for x in (-hx, hx) for y in (-hy, hy) for w in (-hz, hz)]
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    g = VGroup(*[Polygon(*[P(V[i]) for i in f], color=color, fill_color=NAVY, fill_opacity=op, stroke_width=2) for f in faces])
    top = Line(P(V[1]), P(V[5]), color=YELLOW, stroke_width=5)      # 一条棱着色，看出朝向
    return VGroup(g, top)


def center(a, z):
    return Q + rz(a) @ (P1 - Q) + np.array([0, 0, z])


class Lesson(Base):
    def construct(self):
        self.title("6.1", "沙勒定理：任何刚体位移都是螺旋运动", "Chasles: every rigid displacement is a screw motion")
        floor = VGroup(*[Line(P([x, -0.35, 0]), P([x, 0.55, 0]), color=GREY_D, stroke_width=1) for x in np.arange(-0.1, 0.71, 0.1)],
                       *[Line(P([-0.1, y, 0]), P([0.7, y, 0]), color=GREY_D, stroke_width=1) for y in np.arange(-0.35, 0.56, 0.1)])
        self.add(floor)
        start = part(0, 0)
        goal = part(TH, DD, GREY_B, 0.1).set_opacity(0.45)
        self.play(FadeIn(start), FadeIn(goal))
        self.caption("零件要从输送带（蓝）搬到夹具（灰）：转了 90°，还升高了 0.15 m",
                     "Move the part from the conveyor (blue) to the fixture (grey): turned 90° and raised 0.15 m")
        axis = DashedLine(P(Q + [0, 0, -0.05]), P(Q + [0, 0, 0.42]), color=YELLOW, stroke_width=4)
        lab = MathTex(r"\hat s", color=YELLOW, font_size=36).next_to(axis.get_end(), UP, buff=0.1)
        qd = Dot(P(Q), color=YELLOW)
        ql = MathTex("q", color=YELLOW, font_size=32).next_to(qd, LEFT, buff=0.12)
        self.play(Create(axis), FadeIn(lab), FadeIn(qd), FadeIn(ql))
        self.caption("存在一根竖直的轴：绕它转 90°，再沿它移 0.15 m", "There is a vertical axis: turn 90° about it, then slide 0.15 m along it")
        t = ValueTracker(0.0)
        start.add_updater(lambda m: m.become(part(TH * min(1, t.get_value()), DD * max(0, t.get_value() - 1))))
        self.play(t.animate.set_value(1), run_time=2)
        self.play(t.animate.set_value(2), run_time=1.3)
        start.clear_updaters()
        self.caption("先转后移、先移后转，结果相同：两步都绕着、沿着同一根轴", "Turn-then-slide equals slide-then-turn: both steps share one axis")
        u = ValueTracker(0.0)
        start.add_updater(lambda m: m.become(part(TH * max(0, u.get_value() - 1), DD * min(1, u.get_value()))))
        self.play(u.animate.set_value(1), run_time=1.3)
        self.play(u.animate.set_value(2), run_time=2)
        start.clear_updaters()
        self.caption("同时转和移：螺旋运动。零件中心走一段螺旋线", "Turning and sliding together: a screw motion. The centre traces a helix")
        w = ValueTracker(0.0)
        trace = always_redraw(lambda: VMobject(color=ORANGE, stroke_width=4).set_points_as_corners(
            [P(center(TH * s, DD * s)) for s in np.linspace(0, max(w.get_value(), 1e-3), 40)]))
        start.add_updater(lambda m: m.become(part(TH * w.get_value(), DD * w.get_value())))
        self.add(trace)
        self.play(w.animate.set_value(1), run_time=3.5, rate_func=linear)
        start.clear_updaters()
        self.caption("节距 h = d/θ：每转 1 弧度沿轴前进的距离", "Pitch h = d/θ: distance advanced along the axis per radian")
        self.wait(1.0)
        self.card([["沙勒定理（1830）", "Chasles' theorem (1830)"],
                   ["任何刚体位移都是绕某一根轴的螺旋运动", "Every rigid displacement is a screw motion about some axis"],
                   MathTex(r"x' = q + e^{[\hat s]\theta}(x - q) + h\theta\,\hat s", font_size=44)])
