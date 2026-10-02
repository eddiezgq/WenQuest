"""动画 7.1.1（配图 7.1.1）：AGV 位置曲线 x = 0.25t² 上，点 Q 沿曲线滑向 P(2, 1)，割线绕 P 转动，斜率读数 1 + 0.25h 趋于 1；
再让 Q 从左侧滑近；最后放大 P 附近，曲线与切线几乎重合。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("7.1", "割线变成切线", "The secant becomes the tangent")
        ax = Axes(x_range=[0, 4.5, 1], y_range=[0, 5, 1], x_length=7.2, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(LEFT * 1.6 + DOWN * 0.4)
        f = lambda t: 0.25 * t * t
        curve = ax.plot(f, x_range=[0, 4.3], color=WHITE, stroke_width=4)
        P = ax.c2p(2, 1)
        self.play(Create(ax), Create(curve), run_time=1.5)
        dotP = Dot(P, color=YELLOW, radius=0.08)
        nameP = zh("P", 26, YELLOW).next_to(dotP, DR, buff=0.08)
        self.play(FadeIn(dotP), FadeIn(nameP))
        h = ValueTracker(2.0)

        def secant():
            hv = h.get_value()
            m = (f(2 + hv) - 1) / hv
            return ax.plot(lambda t: 1 + m * (t - 2), x_range=[0.3, 4.4], color=STEEL, stroke_width=3)

        sec = always_redraw(secant)
        dotQ = always_redraw(lambda: Dot(ax.c2p(2 + h.get_value(), f(2 + h.get_value())), color=STEEL, radius=0.07))
        read = always_redraw(lambda: VGroup(
            zh("h = %.3f s" % h.get_value(), 26, INK),
            zh("割线斜率 = %.4f m/s" % ((f(2 + h.get_value()) - 1) / h.get_value()), 26, STEEL)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.9))
        self.play(Create(sec), FadeIn(dotQ), FadeIn(read))
        self.caption("Q 沿曲线滑向 P：割线绕 P 转动", "Q slides along the curve towards P; the secant turns about P", wait=0.3)
        self.play(h.animate.set_value(0.02), run_time=5, rate_func=smooth)
        self.caption("斜率 = 1 + 0.25h，趋于 1 m/s", "slope = 1 + 0.25h, tending to 1 m/s")
        tan = ax.plot(lambda t: 1 + (t - 2), x_range=[0.3, 4.4], color=RED, stroke_width=4)
        self.play(Create(tan))
        self.caption("现在让 Q 从左侧滑近", "Now let Q come in from the left", wait=0.3)
        self.play(h.animate.set_value(-1.8), run_time=1.2)
        self.play(h.animate.set_value(-0.02), run_time=4, rate_func=smooth)
        self.caption("从两侧趋于同一个斜率：这就是 t = 2 s 时的瞬时速度", "Both sides tend to the same slope: the speed at t = 2 s")
        self.play(FadeOut(sec), FadeOut(dotQ), FadeOut(read))
        grp = VGroup(ax, curve, tan)
        self.caption("把 P 附近放大", "Zoom in around P", wait=0.3)
        self.play(FadeOut(nameP), grp.animate.scale(6, about_point=P).shift(ORIGIN - P), dotP.animate.move_to(ORIGIN), run_time=3)
        self.caption("放大以后，曲线与切线几乎分不出来", "Magnified, the curve and the tangent can hardly be told apart")
        self.card([["切线是割线的极限位置", "The tangent is the limit of secants"],
                   MathTex(r"v(t_0)=\lim_{h\to 0}\frac{x(t_0+h)-x(t_0)}{h}", font_size=46),
                   ["平均速度的极限是瞬时速度", "The limit of average speeds is the instantaneous speed"]])
