"""动画 15.3.1（配图 15.3.1）：三种方法对奇异值的增益 g(σ)（对数坐标）。
牛顿法 1/σ，雅可比转置法 ασ（α = 1），阻尼最小二乘 σ/(σ² + λ²)；λ 从 0.003 增大到 0.5，峰值 1/(2λ) 在 σ = λ 处。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("15.3", "阻尼最小二乘：给 1/σ 加一个“阻尼”", "Damped least squares: damping 1/σ")
        ax = Axes(x_range=[-3, 0.5, 1], y_range=[-3, 3, 1], x_length=8.5, y_length=4.0, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 0, "include_ticks": False}).shift(UP * 0.1 + LEFT * 0.6)
        frame = VGroup(Line(ax.c2p(-3, -3), ax.c2p(0.5, -3), color=GREY_B, stroke_width=2),
                       Line(ax.c2p(-3, -3), ax.c2p(-3, 3), color=GREY_B, stroke_width=2),
                       *[DashedLine(ax.c2p(-3, k), ax.c2p(0.5, k), color=GREY_D, stroke_width=1) for k in (-2, -1, 0, 1, 2)])
        xl = VGroup(*[MathTex(r"10^{%d}" % k, font_size=24, color=GREY_B).next_to(ax.c2p(k, -3), DOWN, buff=0.15) for k in (-3, -2, -1, 0)])
        yl = VGroup(*[MathTex(r"10^{%d}" % k, font_size=24, color=GREY_B).next_to(ax.c2p(-3, k), LEFT, buff=0.15) for k in (-3, -2, -1, 0, 1, 2, 3)])
        xn = MathTex(r"\sigma", font_size=32).next_to(ax.c2p(0.5, -3), RIGHT, buff=0.2)
        yn = MathTex(r"g(\sigma)", font_size=32).next_to(ax.c2p(-3, 3), UP, buff=0.15)
        self.add(ax)
        self.play(Create(frame), FadeIn(xl), FadeIn(yl), Write(xn), Write(yn), run_time=1.5)

        newton = ax.plot(lambda x: -x, x_range=[-3, 0.5], color=RED, stroke_width=4)
        jt = ax.plot(lambda x: x, x_range=[-3, 0.5], color=ORANGE, stroke_width=4)
        ln = zh("牛顿法 1/σ", 22, RED).next_to(ax.c2p(-2.6, 2.6), RIGHT, buff=0.1)
        lj = zh("雅可比转置 ασ", 22, ORANGE).next_to(ax.c2p(-0.9, -1.4), RIGHT, buff=0.1)
        self.play(Create(newton), FadeIn(ln))
        self.caption("牛顿法：σ 越小，增益越大，奇异附近一步走得极远",
                     "Newton: the smaller σ, the larger the gain; near a singularity one step goes very far")
        self.play(Create(jt), FadeIn(lj))
        self.caption("雅可比转置：σ 越小，增益越小，从不失控，却走不动",
                     "Jacobian transpose: the smaller σ, the smaller the gain; never runs away, but hardly moves")
        lam = ValueTracker(0.003)

        def dls():
            l = lam.get_value()
            c = ax.plot(lambda x: math.log10(10 ** x / (10 ** (2 * x) + l * l)), x_range=[-3, 0.5, 0.02], color=BLUE, stroke_width=5)
            pk = Dot(ax.c2p(math.log10(l), math.log10(1 / (2 * l))), radius=0.08, color=BLUE_B)
            return VGroup(c, pk)

        def lab():
            l = lam.get_value()
            return VGroup(Text("λ = %.3f" % l, font=LATIN, font_size=26, color=BLUE_B),
                          Text("1/(2λ) = %.1f" % (1 / (2 * l)), font=LATIN, font_size=24, color=BLUE_B)
                          ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).shift(DOWN * 0.9)

        d, lb = always_redraw(dls), always_redraw(lab)
        self.play(FadeIn(d), FadeIn(lb))
        self.caption("阻尼最小二乘 σ/(σ² + λ²)：σ ≫ λ 时贴着牛顿法，σ ≪ λ 时贴着雅可比转置",
                     "Damped least squares σ/(σ² + λ²): Newton for σ ≫ λ, Jacobian transpose for σ ≪ λ", wait=1.0)
        self.play(lam.animate.set_value(0.05), run_time=4.0, rate_func=smooth)
        self.caption("峰值 1/(2λ) 在 σ = λ 处：一步的长度有了上限",
                     "The peak 1/(2λ) at σ = λ: a ceiling on the step length", wait=1.5)
        self.play(lam.animate.set_value(0.5), run_time=4.0, rate_func=smooth)
        self.caption("λ 太大：处处都打了折扣，变成慢吞吞的雅可比转置",
                     "λ too large: everything is discounted, it becomes a slow Jacobian transpose", wait=1.5)
        self.play(lam.animate.set_value(0.05), run_time=1.2, rate_func=smooth)
        self.card([["阻尼最小二乘", "Damped least squares"],
                   MathTex(r"\Delta\theta = J^{\mathsf T}\big(JJ^{\mathsf T} + \lambda^2 I\big)^{-1}e", font_size=40),
                   MathTex(r"\|\Delta\theta\| \le \frac{\|e\|}{2\lambda}", font_size=40),
                   ["远离奇异像牛顿法，接近奇异像雅可比转置", "Newton away from singularities, Jacobian transpose near them"]])
