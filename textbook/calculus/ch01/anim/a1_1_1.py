"""动画 1.1.1（配图 1.1.1）：抛物线 y = x² 上，Q 沿曲线滑向 P(1, 1)，割线绕 P 转动，斜率读数 2 + h 趋于 2；
再从左侧滑近；最后放大 P 附近，曲线与切线几乎重合。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("1.1", "切线：割线的极限位置", "The tangent: the limit of secants")
        ax = Axes(x_range=[-0.5, 2.3, 0.5], y_range=[-0.5, 4.5, 1], x_length=7, y_length=5, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(LEFT * 1.5 + DOWN * 0.4)
        f = lambda x: x * x
        curve = ax.plot(f, x_range=[-0.5, 2.1], color=WHITE, stroke_width=4)
        P = ax.c2p(1, 1)
        dotP = Dot(P, color=YELLOW, radius=0.08)
        nameP = zh("P(1, 1)", 24, YELLOW).next_to(dotP, DR, buff=0.08)
        self.play(Create(ax), Create(curve), run_time=1.5)
        self.play(FadeIn(dotP), FadeIn(nameP))
        h = ValueTracker(1.0)
        sec = always_redraw(lambda: ax.plot(lambda x: 1 + (2 + h.get_value()) * (x - 1), x_range=[0.0, 2.2], color=STEEL, stroke_width=3))
        dotQ = always_redraw(lambda: Dot(ax.c2p(1 + h.get_value(), f(1 + h.get_value())), color=STEEL, radius=0.07))
        read = always_redraw(lambda: VGroup(zh("h = %.3f" % h.get_value(), 26, INK),
                                            zh("割线斜率 2 + h = %.3f" % (2 + h.get_value()), 26, STEEL)
                                            ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.9))
        self.play(Create(sec), FadeIn(dotQ), FadeIn(read))
        self.caption("Q 沿抛物线滑向 P，割线绕 P 转动", "Q slides towards P; the secant turns about P", wait=0.3)
        self.play(h.animate.set_value(0.01), run_time=5, rate_func=smooth)
        tan = ax.plot(lambda x: 2 * x - 1, x_range=[0.0, 2.2], color=RED, stroke_width=4)
        self.play(Create(tan))
        self.caption("斜率趋于 2：切线 y = 2x − 1", "The slope tends to 2: tangent y = 2x − 1")
        self.caption("从左侧滑近，斜率同样趋于 2", "From the left the slope also tends to 2", wait=0.3)
        self.play(h.animate.set_value(-0.9), run_time=1.2)
        self.play(h.animate.set_value(-0.01), run_time=4, rate_func=smooth)
        self.play(FadeOut(sec), FadeOut(dotQ), FadeOut(read))
        self.caption("放大 P 附近", "Zoom in around P", wait=0.3)
        self.play(FadeOut(nameP), VGroup(ax, curve, tan).animate.scale(6, about_point=P).shift(ORIGIN - P), dotP.animate.move_to(ORIGIN), run_time=3)
        self.caption("放大后，曲线和切线几乎分不出来", "Magnified, the curve and its tangent look the same")
        self.card([["切线是割线的极限位置", "The tangent is the limit of the secants"],
                   MathTex(r"\lim_{h\to 0}\frac{(1+h)^2-1}{h}=\lim_{h\to 0}(2+h)=2", font_size=46),
                   ["先约去 h，再让 h 趋于零", "Cancel h first, then let h go to zero"]])
