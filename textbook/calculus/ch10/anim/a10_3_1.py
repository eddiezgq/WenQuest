"""动画 10.3.1（配图 10.3.1）：f、f′、f″ 三幅图联动——f(x) = x³ − 3x。一条竖线从左向右扫过：
f′ > 0 时 f 上升、f′ < 0 时下降，f′ = 0 处是极值；f″ > 0 时 f 向上弯、f″ < 0 时向下弯，f″ = 0 处是拐点。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("10.3", "f、f′、f″ 联动", "f, f′ and f″ together")
        f = lambda x: x ** 3 - 3 * x
        f1 = lambda x: 3 * x ** 2 - 3
        f2 = lambda x: 6 * x
        cfg = dict(x_range=[-2.2, 2.2, 1], x_length=8, tips=False, axis_config={"color": GREY_B})
        A = Axes(y_range=[-4.5, 4.5, 1.5], y_length=1.9, **cfg).shift(UP * 1.95)
        B = Axes(y_range=[-4, 12, 4], y_length=1.6, **cfg).shift(DOWN * 0.25)
        C = Axes(y_range=[-14, 14, 7], y_length=1.6, **cfg).shift(DOWN * 2.2)
        labs = VGroup(MathTex("f", font_size=34).next_to(A, LEFT), MathTex("f'", font_size=34, color=STEEL).next_to(B, LEFT),
                      MathTex("f''", font_size=34, color=ORANGE).next_to(C, LEFT))
        gA = A.plot(f, x_range=[-2.2, 2.2], color=WHITE, stroke_width=3)
        gB = B.plot(f1, x_range=[-2.2, 2.2], color=STEEL, stroke_width=3)
        gC = C.plot(f2, x_range=[-2.2, 2.2], color=ORANGE, stroke_width=3)
        self.play(Create(A), Create(B), Create(C), FadeIn(labs))
        self.play(Create(gA), Create(gB), Create(gC), run_time=2)
        x = ValueTracker(-2.2)
        line = always_redraw(lambda: DashedLine(A.c2p(x.get_value(), 4.5), C.c2p(x.get_value(), -14), color=GREY_B, stroke_width=1.5))
        dA = always_redraw(lambda: Dot(A.c2p(x.get_value(), f(x.get_value())), color=GREEN if f1(x.get_value()) > 0 else RED, radius=0.08))
        dB = always_redraw(lambda: Dot(B.c2p(x.get_value(), f1(x.get_value())), color=STEEL, radius=0.07))
        dC = always_redraw(lambda: Dot(C.c2p(x.get_value(), f2(x.get_value())), color=ORANGE, radius=0.07))
        tan = always_redraw(lambda: A.plot(lambda t: f(x.get_value()) + f1(x.get_value()) * (t - x.get_value()),
                                            x_range=[max(-2.2, x.get_value() - 0.45), min(2.2, x.get_value() + 0.45)],
                                            color=GREEN if f1(x.get_value()) > 0 else RED, stroke_width=2.5))
        self.play(FadeIn(line), FadeIn(dA), FadeIn(dB), FadeIn(dC), FadeIn(tan))
        self.caption("f′ > 0（绿）时 f 上升，f′ < 0（红）时 f 下降", "f rises where f′ > 0 (green), falls where f′ < 0 (red)", wait=0.2)
        self.play(x.animate.set_value(-1), run_time=2.5)
        self.caption("f′ = 0、由正变负：极大值", "f′ = 0, changing from + to −: a local maximum", wait=0.6)
        self.play(x.animate.set_value(0), run_time=2)
        self.caption("f″ = 0、变号：拐点，弯曲方向由向下变为向上", "f″ = 0 and changes sign: inflection, bending turns from down to up", wait=0.6)
        self.play(x.animate.set_value(1), run_time=2)
        self.caption("f′ = 0、由负变正，f″ > 0：极小值", "f′ = 0 from − to +, f″ > 0: a local minimum", wait=0.6)
        self.play(x.animate.set_value(2.2), run_time=2)
        for m in (line, dA, dB, dC, tan):
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in (A, B, C, labs, gA, gB, gC, line, dA, dB, dC, tan)])
        self.card([["一阶导数管升降，二阶导数管弯曲", "f′ for rising and falling, f″ for bending"],
                   MathTex(r"f'>0\ \Rightarrow\ \nearrow,\qquad f''>0\ \Rightarrow\ \smile", font_size=44),
                   ["极值：f′ 变号；拐点：f″ 变号", "Extremum: f′ changes sign; inflection: f″ changes sign"]])
