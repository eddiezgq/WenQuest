"""动画 14.6.1（配图 14.6.1）：SCARA（俯视，两臂 0.35 m、0.25 m）的工具点沿直线 x = 0.45 m 从 y = −0.3 m 走到 0.3 m。
右手构型（θ2 > 0，蓝）与左手构型（θ2 < 0，金）同时跟随，关于基座—工具连线对称。最后演示换手：必须经过手臂伸直的位置。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.35, 0.25
SC = 5.0
O = np.array([-2.6, -0.3, 0.0])


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


def ik(x, y, sg):
    r = math.hypot(x, y)
    c = (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    c = max(-1.0, min(1.0, c))
    t2 = math.atan2(sg * math.sqrt(max(0.0, 1 - c * c)), c)
    t1 = math.atan2(y, x) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    return t1, t2


def draw(x, y, sg, col):
    t1, t2 = ik(x, y, sg)
    e = S(L1 * math.cos(t1), L1 * math.sin(t1))
    tip = S(x, y)
    return VGroup(Line(O, e, color=col, stroke_width=14, stroke_opacity=0.9), Line(e, tip, color=col, stroke_width=10, stroke_opacity=0.9),
                  Dot(O, radius=0.11, color=WHITE), Dot(e, radius=0.1, color=WHITE))


class Lesson(Base):
    def construct(self):
        self.title("14.6", "SCARA：右手与左手", "SCARA: right-handed and left-handed")
        reach = Circle(radius=SC * (L1 + L2), color=BLUE_E, stroke_width=2).move_to(O)
        inner = Circle(radius=SC * (L1 - L2), color=BLUE_E, stroke_width=1).move_to(O)
        path = DashedLine(S(0.45, -0.3), S(0.45, 0.3), color=GREY_B, stroke_width=3)
        self.play(Create(reach), Create(inner), Create(path))
        y = ValueTracker(-0.3)
        mode = ValueTracker(0.0)          # 0：沿直线；1：换手演示

        def arms():
            if mode.get_value() < 0.5:
                yy = y.get_value()
                return VGroup(draw(0.45, yy, 1, BLUE), draw(0.45, yy, -1, ORANGE), Dot(S(0.45, yy), radius=0.09, color=RED))
            u = y.get_value()                                   # 换手：θ2 从正到负，工具沿径向外移到伸直位置再回来
            t1 = math.atan2(0.0, 0.45)
            t2 = 1.2 * (1 - 2 * u)
            e = S(L1 * math.cos(t1 - t2 / 2), L1 * math.sin(t1 - t2 / 2))
            a = t1 - t2 / 2
            tip = S(L1 * math.cos(a) + L2 * math.cos(a + t2), L1 * math.sin(a) + L2 * math.sin(a + t2))
            col = BLUE if t2 > 0 else ORANGE
            return VGroup(Line(O, e, color=col, stroke_width=14), Line(e, tip, color=col, stroke_width=10),
                          Dot(O, radius=0.11, color=WHITE), Dot(e, radius=0.1, color=WHITE), Dot(tip, radius=0.09, color=RED))

        g = always_redraw(arms)
        self.add(g)
        leg = VGroup(VGroup(Line(ORIGIN, RIGHT * 0.5, color=BLUE, stroke_width=8), zh("右手构型", 22, BLUE)).arrange(RIGHT, buff=0.15),
                     VGroup(Line(ORIGIN, RIGHT * 0.5, color=ORANGE, stroke_width=8), zh("左手构型", 22, ORANGE)).arrange(RIGHT, buff=0.15)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(leg))
        self.caption("工具点沿直线走：两种构型都能跟随，彼此关于基座—工具连线对称",
                     "The tool runs along a line: both configurations follow, mirror images about the base–tool line", wait=0)
        self.play(y.animate.set_value(0.3), run_time=5.0, rate_func=smooth)
        self.caption("途中不能换手：换手要让 θ₂ 经过零，也就是手臂伸直",
                     "No switching on the way: θ₂ would have to pass zero, the arm straight", wait=0.5)
        self.play(y.animate.set_value(-0.3), run_time=4.0, rate_func=smooth)
        y.set_value(0.0)
        mode.set_value(1.0)
        self.caption("专门的换手动作：手臂伸直到外边界，再折向另一侧",
                     "A dedicated change of hand: straighten to the outer edge, then fold to the other side", wait=0)
        self.play(y.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        self.wait(0.8)
        self.card([["SCARA：右手、左手两组解", "SCARA: right- and left-handed solutions"],
                   MathTex(r"\theta_3 = z_0 - z,\qquad \theta_4 = \varphi - \theta_1 - \theta_2", font_size=40),
                   ["点位带构型标志，运动中不换手", "Points carry a hand flag; the hand does not change on the way"]])
