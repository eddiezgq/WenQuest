"""动画 5.3.1（配图 5.3.1）：匀速圆周运动中 Δv 指向圆心。质点沿圆周匀速运动，速度沿切线；把相隔 Δt 的两个速度平移到同一起点，
Δv 是它们终点的连线。Δt 由大变小，Δv 越来越接近指向圆心，|Δv|/Δt 趋于 v²/R。"""
from manim import *
from wq_anim import *
import numpy as np

R, V = 2.0, 1.6                                  # 画面中的半径与速度长度
C = np.array([-3.2, -0.6, 0])                    # 圆心
Q0 = np.array([3.0, -0.6, 0])                    # 速度三角形的公共起点


def pos(th):
    return C + R * np.array([np.cos(th), np.sin(th), 0])


def vel(th):
    return V * np.array([-np.sin(th), np.cos(th), 0])


class Lesson(Base):
    def construct(self):
        self.title("5.3", "匀速圆周运动：Δv 指向圆心", "Uniform circular motion: Δv points to the centre")
        circ = Circle(radius=R, color=GREY_B).move_to(C)
        cen = Dot(C, color=WHITE, radius=0.06)
        self.play(Create(circ), FadeIn(cen))
        th = ValueTracker(0.3)
        dot = always_redraw(lambda: Dot(pos(th.get_value()), color=WHITE, radius=0.08))
        varr = always_redraw(lambda: Arrow(pos(th.get_value()), pos(th.get_value()) + vel(th.get_value()), buff=0, color=BLUE, stroke_width=5))
        self.add(dot, varr)
        self.caption("速率不变，速度的方向沿切线不断转动", "Constant speed, but the velocity keeps turning along the tangent", wait=0)
        self.play(th.animate.set_value(0.3 + 2 * PI), run_time=4, rate_func=linear)
        th1 = 0.6
        dth = ValueTracker(1.2)
        v1 = always_redraw(lambda: Arrow(pos(th1), pos(th1) + vel(th1), buff=0, color=BLUE, stroke_width=5))
        v2 = always_redraw(lambda: Arrow(pos(th1 + dth.get_value()), pos(th1 + dth.get_value()) + vel(th1 + dth.get_value()), buff=0, color=TEAL, stroke_width=5))
        w1 = always_redraw(lambda: Arrow(Q0, Q0 + vel(th1), buff=0, color=BLUE, stroke_width=5))
        w2 = always_redraw(lambda: Arrow(Q0, Q0 + vel(th1 + dth.get_value()), buff=0, color=TEAL, stroke_width=5))
        dv = always_redraw(lambda: Arrow(Q0 + vel(th1), Q0 + vel(th1 + dth.get_value()), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.35))
        tocen = always_redraw(lambda: DashedLine(pos(th1 + dth.get_value() / 2), C, color=RED, stroke_opacity=0.6))
        lab = always_redraw(lambda: MathTex(r"\Delta\theta = %.2f\ \mathrm{rad}" % dth.get_value(), font_size=30).move_to(Q0 + np.array([0, -1.9, 0])))
        self.play(FadeOut(varr), FadeOut(dot), FadeIn(v1), FadeIn(v2))
        self.caption("取相隔 Δt 的两个速度，把它们平移到同一起点", "Take two velocities Δt apart and move them to a common start", wait=0)
        self.play(TransformFromCopy(v1, w1), TransformFromCopy(v2, w2), run_time=1.5)
        self.add(w1, w2)
        self.play(GrowArrow(dv), FadeIn(lab), Create(tocen))
        self.caption("Δv 从 v₁ 的终点指向 v₂ 的终点", "Δv runs from the tip of v₁ to the tip of v₂", wait=1.0)
        self.caption("Δt 越来越小……", "Let Δt shrink...", wait=0)
        self.play(dth.animate.set_value(0.15), run_time=4, rate_func=smooth)
        self.caption("Δv 垂直于速度，指向圆心：加速度 v²/R 指向圆心", "Δv becomes perpendicular to v and points to the centre: a = v²/R inward", wait=2.0)
        self.card([["匀速圆周运动的加速度", "Acceleration in uniform circular motion"],
                   ["速率不变，方向在变，所以有加速度", "Speed constant, direction changing: there is an acceleration"],
                   ["指向圆心，大小 v²/R = ω²R", "Towards the centre, magnitude v²/R = ω²R"]])
