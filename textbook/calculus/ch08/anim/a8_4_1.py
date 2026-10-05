"""动画 8.4.1（配图 8.4.1）：牛顿法——在 t₀ 处作切线，走到与横轴的交点 t₁，再作切线……；
误差的有效数字每步约翻一番；最后看 arctan x 从 1.5 出发，切线把迭代越抛越远。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("8.4", "牛顿法：沿切线找根", "Newton's method: follow the tangent")
        z, wn = 0.6, 10.0
        wd = wn * np.sqrt(1 - z * z)
        c = z / np.sqrt(1 - z * z)
        f = lambda t: 1 - np.exp(-z * wn * t) * (np.cos(wd * t) + c * np.sin(wd * t)) - 0.95
        df = lambda t: np.exp(-z * wn * t) * (wn ** 2 / wd) * np.sin(wd * t)
        ax = Axes(x_range=[0.1, 0.35, 0.05], y_range=[-0.6, 0.15, 0.15], x_length=10, y_length=5, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 18}).shift(DOWN * 0.4)
        g = ax.plot(f, x_range=[0.1, 0.35], color=WHITE, stroke_width=3)
        self.play(Create(ax), Create(g))
        self.caption("求 q(t) − 0.95 = 0 的根 t₉₅", "Solve q(t) − 0.95 = 0 for t₉₅", wait=0.2)
        t = 0.2
        errs = []
        drawn = []
        for k in range(3):
            tn = t - f(t) / df(t)
            p = Dot(ax.c2p(t, f(t)), color=RED)
            tl = Line(ax.c2p(t, f(t)), ax.c2p(tn, 0), color=RED)
            v = DashedLine(ax.c2p(t, 0), ax.c2p(t, f(t)), color=GREY_B)
            self.play(Create(v), FadeIn(p), run_time=0.5)
            self.play(Create(tl), run_time=0.8)
            lab = MathTex(f"t_{k + 1}", font_size=30, color=RED).next_to(ax.c2p(tn, 0), UP + RIGHT * 0.2, buff=0.1)
            self.play(FadeIn(lab), run_time=0.4)
            drawn += [p, tl, v, lab]
            t = tn
            errs.append(abs(tn - 0.2537398611108357))
        self.caption("每一步：用切线代替曲线，走到切线与横轴的交点", "Each step: replace the curve by its tangent and go to its intercept", wait=0.4)
        tab = VGroup(*[MathTex(r"e_%d \approx %s" % (k + 1, ("%.0e" % e).replace("e-0", r"\times10^{-").replace("e-", r"\times10^{-") + "}"), font_size=34)
                       for k, e in enumerate(errs)]).arrange(DOWN, aligned_edge=LEFT).move_to(ax.c2p(0.3, -0.35))
        self.play(FadeIn(tab))
        self.caption("误差的指数每步约翻一番：二次收敛", "The exponent of the error roughly doubles each step: quadratic convergence", wait=0.6)
        self.play(*[FadeOut(m) for m in [ax, g, tab] + drawn])
        ax2 = Axes(x_range=[-6, 6, 2], y_range=[-1.6, 1.6, 0.8], x_length=10, y_length=5, tips=False,
                   axis_config={"color": GREY_B, "include_numbers": True, "font_size": 18}).shift(DOWN * 0.4)
        g2 = ax2.plot(np.arctan, x_range=[-6, 6], color=WHITE, stroke_width=3)
        self.play(Create(ax2), Create(g2))
        x = 1.5
        for k in range(3):
            xn = x - np.arctan(x) * (1 + x * x)
            self.play(Create(DashedLine(ax2.c2p(x, 0), ax2.c2p(x, np.arctan(x)), color=GREY_B)), run_time=0.4)
            self.play(Create(Line(ax2.c2p(x, np.arctan(x)), ax2.c2p(max(xn, -6), np.arctan(x) - (x - max(xn, -6)) / (1 + x * x)), color=RED)), run_time=0.8)
            x = xn
        self.caption("arctan x 从 1.5 出发：远处切线太平，迭代越跳越远", "arctan x from 1.5: the tangent is too flat far out, and the iterates run away")
        self.card([["牛顿法", "Newton's method"],
                   MathTex(r"x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)},\qquad |e_{k+1}|\le C\,e_k^2", font_size=42),
                   ["离根近时二次收敛；离根远时可能发散", "Quadratic near a root; may diverge from far away"]])
