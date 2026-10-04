"""动画 2.5.2（配图 2.5.3）：复合函数像流水线，x 经 g 变为 u，u 经 f 变为 y，复合函数的图像一点一点画出；
反函数把箭头倒过来，eˣ 的图像沿 y = x 翻折成 ln x。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.5", "复合函数与反函数", "Composition and inverse functions")
        # 流水线：x → g → u → f → y，g(x) = x²，f(u) = sin u
        bx = RoundedRectangle(width=1.8, height=1.0, corner_radius=0.15, color=STEEL).shift(LEFT * 2.3 + UP * 2.3)
        fx = RoundedRectangle(width=1.8, height=1.0, corner_radius=0.15, color=ORANGE).shift(RIGHT * 2.3 + UP * 2.3)
        gl = MathTex(r"g(x) = x^2", font_size=30, color=STEEL).move_to(bx)
        fl = MathTex(r"f(u) = \sin u", font_size=30, color=ORANGE).move_to(fx)
        a1 = Arrow(LEFT * 5.6 + UP * 2.3, bx.get_left(), buff=0.1, color=GREY_B)
        a2 = Arrow(bx.get_right(), fx.get_left(), buff=0.1, color=GREY_B)
        a3 = Arrow(fx.get_right(), RIGHT * 5.6 + UP * 2.3, buff=0.1, color=GREY_B)
        self.play(*[Create(m) for m in (bx, fx, a1, a2, a3)], FadeIn(gl), FadeIn(fl))
        x = ValueTracker(0.0)
        vals = always_redraw(lambda: VGroup(
            MathTex(r"x = %.2f" % x.get_value(), font_size=30).next_to(a1, DOWN, buff=0.1),
            MathTex(r"u = %.2f" % (x.get_value() ** 2), font_size=30, color=STEEL).next_to(a2, DOWN, buff=0.1),
            MathTex(r"y = %.2f" % math.sin(x.get_value() ** 2), font_size=30, color=ORANGE).next_to(a3, DOWN, buff=0.1)))
        self.play(FadeIn(vals))
        ax = Axes(x_range=[0, 3, 0.5], y_range=[-1.2, 1.2, 0.5], x_length=9, y_length=2.8, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(DOWN * 0.6)
        self.play(Create(ax))
        trace = always_redraw(lambda: ax.plot(lambda t: math.sin(t * t), x_range=[0, max(x.get_value(), 0.001)], color=YELLOW, stroke_width=4))
        dot = always_redraw(lambda: Dot(ax.c2p(x.get_value(), math.sin(x.get_value() ** 2)), color=YELLOW))
        self.add(trace, dot)
        self.caption("先算 u = g(x)，再算 y = f(u)：复合函数 f(g(x)) = sin x²", "First u = g(x), then y = f(u): the composite f(g(x)) = sin x²", wait=0.3)
        self.play(x.animate.set_value(3.0), run_time=6, rate_func=linear)
        self.caption("顺序不能交换：g(f(x)) = sin²x 是另一个函数", "The order matters: g(f(x)) = sin²x is a different function", wait=0.3)
        other = ax.plot(lambda t: math.sin(t) ** 2, x_range=[0, 3], color=GREEN, stroke_width=3)
        self.play(Create(other), run_time=1.5)
        self.wait(1)
        self.play(*[FadeOut(m) for m in (bx, fx, gl, fl, a1, a2, a3, vals, ax, trace, dot, other)])
        # 反函数：沿 y = x 翻折
        ax2 = Axes(x_range=[-3, 4.5, 1], y_range=[-3, 4.5, 1], x_length=5.2, y_length=5.2, tips=False,
                   axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(UP * 0.1 + LEFT * 2)
        diag = DashedLine(ax2.c2p(-3, -3), ax2.c2p(4.5, 4.5), color=GREY_B)
        ex = ax2.plot(np.exp, x_range=[-3, 1.5], color=RED, stroke_width=5)
        lex = MathTex(r"y = e^x", color=RED, font_size=34).next_to(ax2.c2p(1.4, 4.2), RIGHT)
        self.play(Create(ax2), Create(diag), Create(ex), FadeIn(lex))
        p = Dot(ax2.c2p(1, math.e), color=YELLOW)
        pl = MathTex(r"(1, e)", font_size=28, color=YELLOW).next_to(p, LEFT)
        self.play(FadeIn(p), FadeIn(pl))
        self.caption("反函数把对应倒过来：(a, b) 变成 (b, a)", "The inverse reverses the rule: (a, b) becomes (b, a)", wait=0.3)
        mirror = ex.copy()
        q = Dot(ax2.c2p(math.e, 1), color=YELLOW)
        ql = MathTex(r"(e, 1)", font_size=28, color=YELLOW).next_to(q, DOWN)
        pc = p.copy()
        self.play(Rotate(VGroup(mirror, pc), PI, axis=np.array([1.0, 1.0, 0.0]), about_point=ax2.c2p(0, 0)), run_time=3)
        self.play(mirror.animate.set_color(STEEL), FadeIn(q))
        self.play(FadeIn(ql), FadeIn(MathTex(r"y = \ln x", color=STEEL, font_size=34).next_to(ax2.c2p(4.3, 1.5), UP)))
        self.caption("两条曲线关于 y = x 对称", "The two curves are mirror images in y = x")
        self.card([["反函数", "Inverse function"],
                   MathTex(r"f^{-1}(f(x)) = x,\qquad f(f^{-1}(y)) = y", font_size=44),
                   ["单调函数一定有反函数；图像关于 y = x 对称", "A monotonic function has an inverse; graphs mirror in y = x"]])
