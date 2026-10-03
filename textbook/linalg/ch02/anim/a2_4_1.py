"""动画 2.4.1（配图 2.4.1）：a = (4, 3) 所在的直线；b 的终点绕原点转动，投影 p = (a·b / a·a) a 在直线上滑动，
误差 e = b − p 始终垂直于直线；b ⟂ a 时投影为零，b 沿 a 时误差为零。最后回到 AGV 的数据 b = (3, 3.1)。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.4", "向一条直线投影", "Projection onto a line")
        k = 0.62
        O = np.array([-0.8, -0.5, 0.0])
        a = np.array([4.0, 3.0])

        def P(v):
            return O + k * np.array([v[0], v[1], 0.0])

        line = Line(P(-1.1 * a), P(1.5 * a), color=GREY_B, stroke_width=2)
        aa = Arrow(P([0, 0]), P(a / 2.5), buff=0, color=WHITE, stroke_width=6, max_tip_length_to_length_ratio=0.3)
        la = MathTex(r"\boldsymbol a", font_size=36).next_to(P(a / 2.5), DOWN + RIGHT, buff=0.05)
        self.play(Create(line), GrowArrow(aa), FadeIn(la))
        ang = ValueTracker(math.atan2(3.1, 3.0))
        R = math.hypot(3.0, 3.1)

        def scene():
            t = ang.get_value()
            b = R * np.array([math.cos(t), math.sin(t)])
            p = (a @ b) / (a @ a) * a
            g = VGroup(Arrow(P([0, 0]), P(b), buff=0, color=GREEN, stroke_width=6, max_tip_length_to_length_ratio=0.15))
            if np.linalg.norm(p) > 0.05:
                g.add(Arrow(P([0, 0]), P(p), buff=0, color=BLUE, stroke_width=7, max_tip_length_to_length_ratio=0.15))
            if np.linalg.norm(b - p) > 0.05:
                g.add(Arrow(P(p), P(b), buff=0, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.18))
                d = 0.18 * a / np.linalg.norm(a)
                n = 0.18 * (b - p) / np.linalg.norm(b - p)
                g.add(VMobject(stroke_color=WHITE, stroke_width=1.5).set_points_as_corners([P(p - d), P(p - d + n), P(p + n)]))
            g.add(MathTex(r"\boldsymbol b", color=GREEN, font_size=34).next_to(P(b), UP, buff=0.08))
            return g

        sc = always_redraw(scene)
        self.play(FadeIn(sc))
        self.caption("绿色 b 向直线投影：蓝色 p 在直线上，红色误差 e 垂直于直线",
                     "Project green b onto the line: blue p lies on it, red error e is perpendicular")
        rd = always_redraw(lambda: MathTex(r"\hat x = \frac{\boldsymbol a\cdot\boldsymbol b}{\boldsymbol a\cdot\boldsymbol a} = %.2f" %
                                           ((a @ (R * np.array([math.cos(ang.get_value()), math.sin(ang.get_value())]))) / 25), font_size=36)
                           .to_corner(UR, buff=0.5).shift(DOWN * 0.8))
        self.add(rd)
        self.play(ang.animate.set_value(math.atan2(3, 4) + math.pi / 2), run_time=2.5)
        self.caption("b 垂直于 a：投影缩成零", "b perpendicular to a: the projection shrinks to zero", wait=1.0)
        self.play(ang.animate.set_value(math.atan2(3, 4) + math.pi), run_time=2.0)
        self.caption("b 与 a 反向：误差为零，投影系数为负", "b opposite to a: zero error, negative coefficient", wait=1.0)
        self.play(ang.animate.set_value(math.atan2(3, 4) + 2 * math.pi), run_time=3.0)
        self.caption("b 沿 a 方向：b 就是它自己的投影", "b along a: b is its own projection", wait=1.0)
        self.play(ang.animate.set_value(math.atan2(3.1, 3.0) + 2 * math.pi), run_time=1.0)
        note = bi(["AGV：b = (3, 3.1)，沿通道 4.26 m，偏离 0.68 m", "AGV: b = (3, 3.1), 4.26 m along the aisle, 0.68 m off"], 26, YELLOW).to_edge(LEFT, buff=0.4).shift(UP * 2.2)
        self.play(FadeIn(note))
        self.caption("回到 AGV：误差 e 的长度就是偏离通道中心线的距离", "Back to the AGV: the length of e is the distance off the centre line", wait=1.2)
        self.card([["投影：误差与直线垂直", "Projection: the error is perpendicular"],
                   MathTex(r"\boldsymbol p = \frac{\boldsymbol a\cdot\boldsymbol b}{\boldsymbol a\cdot\boldsymbol a}\,\boldsymbol a,\qquad (\boldsymbol b - \boldsymbol p)\perp\boldsymbol a", font_size=44),
                   ["p 是直线上离 b 最近的点", "p is the point of the line closest to b"]])
