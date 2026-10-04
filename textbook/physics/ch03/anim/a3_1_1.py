"""动画 3.1.1（配图 3.1.1）：割线变切线。AGV 起步时 x = 0.25t²（算例 3.1.1）。取 t = 2 s 和 t + Δt 两点连一条割线，
它的斜率是这段时间的平均速度；Δt 越来越小，割线绕 t = 2 s 的点转动，趋于切线，斜率趋于瞬时速度 1 m/s。"""
from manim import *
from wq_anim import *
import numpy as np

x_of = lambda t: 0.25 * t * t
T0 = 2.0


class Lesson(Base):
    def construct(self):
        self.title("3.1", "割线变切线", "From secant to tangent")
        ax = Axes(x_range=[0, 4.2, 1], y_range=[0, 4.4, 1], x_length=6.8, y_length=4.0, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 24}).shift(LEFT * 2.0 + UP * 0.3)
        xl = ax.get_x_axis_label(MathTex(r"t/\mathrm s", font_size=28), edge=RIGHT, direction=DOWN)
        yl = ax.get_y_axis_label(MathTex(r"x/\mathrm m", font_size=28), edge=UP, direction=LEFT)
        curve = ax.plot(x_of, x_range=[0, 4.15], color=BLUE, stroke_width=4)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(Create(curve))
        self.caption("AGV 起步：x = 0.25t²，x–t 曲线越来越陡", "An AGV starting off: x = 0.25t²; the x–t curve gets steeper", wait=1.0)
        dt = ValueTracker(2.0)
        P = Dot(ax.c2p(T0, x_of(T0)), color=YELLOW, radius=0.09)
        Q = always_redraw(lambda: Dot(ax.c2p(T0 + dt.get_value(), x_of(T0 + dt.get_value())), color=ORANGE, radius=0.08))

        def secant():
            d = dt.get_value(); m = (x_of(T0 + d) - x_of(T0)) / d
            return ax.plot(lambda t: x_of(T0) + m * (t - T0), x_range=[0.3, 4.15], color=ORANGE, stroke_width=3)
        sec = always_redraw(secant)
        self.play(FadeIn(P), FadeIn(Q), Create(sec))
        lab = VGroup(MathTex(r"\Delta t =", font_size=34), DecimalNumber(2.0, num_decimal_places=3, font_size=34),
                     MathTex(r"\mathrm s", font_size=34)).arrange(RIGHT, buff=0.12)
        lab2 = VGroup(MathTex(r"\bar v = \frac{\Delta x}{\Delta t} =", font_size=34), DecimalNumber(1.5, num_decimal_places=3, font_size=34, color=ORANGE),
                      MathTex(r"\mathrm{m/s}", font_size=34)).arrange(RIGHT, buff=0.12)
        box = VGroup(lab, lab2).arrange(DOWN, aligned_edge=LEFT, buff=0.35).to_edge(RIGHT, buff=0.6).shift(UP * 0.9)
        lab[1].add_updater(lambda m: m.set_value(dt.get_value()))
        lab2[1].add_updater(lambda m: m.set_value((x_of(T0 + dt.get_value()) - x_of(T0)) / dt.get_value()))
        self.play(FadeIn(box))
        self.caption("割线连接 t = 2 s 和 t + Δt 两点，斜率是这段时间的平均速度", "The secant joins t = 2 s and t + Δt; its slope is the average velocity", wait=1.0)
        self.caption("让 Δt 越来越小……", "Now let Δt shrink...", wait=0)
        self.play(dt.animate.set_value(0.5), run_time=2.5, rate_func=smooth)
        self.play(dt.animate.set_value(0.1), run_time=2.0, rate_func=smooth)
        self.play(dt.animate.set_value(0.01), run_time=2.0, rate_func=smooth)
        tan = ax.plot(lambda t: x_of(T0) + 1.0 * (t - T0), x_range=[0.3, 4.15], color=RED, stroke_width=4)
        self.play(Create(tan))
        res = MathTex(r"v = \lim_{\Delta t\to 0}\frac{\Delta x}{\Delta t} = 1\ \mathrm{m/s}", font_size=32, color=RED).next_to(box, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(Write(res))
        self.caption("割线绕这一点转动，趋于切线：切线的斜率就是瞬时速度", "The secant pivots into the tangent, whose slope is the instantaneous velocity", wait=2.0)
        self.card([["割线变切线", "From secant to tangent"],
                   ["割线的斜率 = 平均速度 Δx/Δt", "Slope of the secant = average velocity Δx/Δt"],
                   ["Δt → 0：割线趋于切线，斜率趋于导数 dx/dt", "Δt → 0: the secant tends to the tangent, the slope to dx/dt"]])
