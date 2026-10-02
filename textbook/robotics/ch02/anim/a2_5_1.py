"""动画 2.5.1（配图 2.5.2 左）：点 x·a 沿直线滑动，b 到它的残差随之变化；残差最短时恰好垂直于直线，此时的 x 就是最小二乘解。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.5", "最小二乘：垂直的残差最短", "Least squares: the perpendicular residual is shortest")
        U = 1.6
        O = np.array([-3.4, -1.6, 0])
        a = np.array([2.0, 0.6])
        b = np.array([1.0, 1.6])
        xh = float(a @ b / (a @ a))

        def P(v):
            return O + U * np.array([v[0], v[1], 0])

        line = Line(P(-0.4 * a), P(1.5 * a), color=BLUE, stroke_width=3)
        rng = bi(["A 的值域", "range of A"], 24, BLUE).next_to(P(1.5 * a), UP, buff=0.1)
        va = Arrow(P([0, 0]), P(a), buff=0, color=BLUE, stroke_width=6)
        la = MathTex("a", color=BLUE, font_size=36).next_to(P(a), DOWN, buff=0.15)
        vb = Arrow(P([0, 0]), P(b), buff=0, color=WHITE, stroke_width=6)
        lb = MathTex("b", font_size=36).next_to(P(b), UP, buff=0.1)
        self.play(Create(line), GrowArrow(va), FadeIn(la), FadeIn(rng), run_time=1.2)
        self.play(GrowArrow(vb), FadeIn(lb), run_time=0.8)
        x = ValueTracker(0.2)

        def moving():
            t = x.get_value()
            p = t * a
            g = VGroup(Dot(P(p), color=YELLOW, radius=0.08), DashedLine(P(p), P(b), color=RED, stroke_width=4))
            if abs(t - xh) < 0.01:
                u = a / np.linalg.norm(a)
                n = (b - p) / np.linalg.norm(b - p)
                c = 0.09
                g.add(VMobject(color=WHITE, stroke_width=2).set_points_as_corners([P(p + c * u), P(p + c * u + c * n), P(p + c * n)]))
            return g

        def panel():
            t = x.get_value()
            r = float(np.linalg.norm(b - t * a))
            return VGroup(MathTex(r"x = %.2f" % t, color=YELLOW, font_size=38),
                          MathTex(r"\|b - x a\| = %.3f" % r, color=RED, font_size=38)).arrange(DOWN, buff=0.3).move_to(np.array([4.2, 0.8, 0]))

        mv = always_redraw(moving)
        pn = always_redraw(panel)
        self.add(mv, pn)
        self.caption("点 x·a 沿直线滑动，红色虚线是残差 b − x·a", "The point x·a slides along the line; the red dashes are the residual b − x·a", wait=0)
        self.play(x.animate.set_value(1.25), run_time=3, rate_func=there_and_back_with_pause)
        self.caption("残差最短的位置：残差垂直于直线", "The residual is shortest where it is perpendicular to the line", wait=0)
        self.play(x.animate.set_value(xh), run_time=2)
        self.wait(1.2)
        eq = MathTex(r"a^{\mathsf T}(b - \hat x a) = 0", r"\;\Rightarrow\;", r"\hat x = \frac{a^{\mathsf T} b}{a^{\mathsf T} a}", font_size=40).move_to(np.array([3.2, -0.8, 0]))
        self.caption("垂直的条件就是正规方程", "The perpendicularity condition is the normal equation", wait=0)
        self.play(Write(eq), run_time=1.8)
        self.wait(1.0)
        self.caption("偏离这一点，残差的平方按勾股定理增加", "Move away and the squared residual grows by Pythagoras", wait=0)
        self.play(x.animate.set_value(xh + 0.4), run_time=1.5)
        self.play(x.animate.set_value(xh), run_time=1.2)
        self.wait(0.8)
        self.card([["最小二乘解", "The least-squares solution"],
                   MathTex(r"A^{\mathsf T}A\,\hat x = A^{\mathsf T} b", font_size=48),
                   ["残差 b − A x̂ 垂直于 A 的每一列", "the residual b − A x̂ is perpendicular to every column of A"]])
