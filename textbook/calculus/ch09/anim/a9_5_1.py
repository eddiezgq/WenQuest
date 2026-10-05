"""动画 9.5.1（配图 9.5.1）：泰勒多项式——sin x 的 1、3、5、7、9、11 次泰勒多项式一个个出现，贴合的范围越来越宽；
在 x = 2 处，误差与拉格朗日余项的上界同步缩小。"""
from manim import *
from wq_anim import *
import numpy as np
from math import factorial


def sci(v):
    m, e = f"{v:.1e}".split("e")
    return m if int(e) == 0 else r"%s\times 10^{%d}" % (m, int(e))


class Lesson(Base):
    def construct(self):
        self.title("9.5", "泰勒公式", "Taylor's formula")
        ax = Axes(x_range=[-7, 7, 1], y_range=[-2.2, 2.2, 1], x_length=11, y_length=4.0, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.5)
        g = ax.plot(np.sin, x_range=[-7, 7], color=WHITE, stroke_width=4)
        self.play(Create(ax), Create(g))
        self.caption("用多项式去贴合 sin x：在 0 处，函数值和各阶导数都相同", "Match sin x by polynomials: same value and derivatives at 0", wait=0.3)
        P = lambda n: (lambda x: sum((-1) ** k * x ** (2 * k + 1) / factorial(2 * k + 1) for k in range((n + 1) // 2)))
        cur = None
        lab = None
        colors = [STEEL, GREEN, YELLOW, ORANGE, RED, PURPLE]
        for n, c in zip((1, 3, 5, 7, 9, 11), colors):
            p = P(n)
            xm = 0.0
            while xm < 7 and abs(p(xm + 0.01)) <= 2.2:
                xm += 0.01
            curve = ax.plot(p, x_range=[-xm, xm, 0.02], color=c, stroke_width=3)
            err = abs(np.sin(2.0) - p(2.0))
            bound = 2.0 ** (n + 2) / factorial(n + 2)
            new_lab = MathTex(r"P_{%d}:\ |\sin 2-P_{%d}(2)|=%s\le\frac{2^{%d}}{%d!}=%s" % (n, n, sci(err), n + 2, n + 2, sci(bound)),
                              font_size=32, color=c).next_to(ax, UP, buff=0.25)
            if cur is None:
                self.play(Create(curve), Write(new_lab), run_time=1.2)
            else:
                self.play(ReplacementTransform(cur, curve), ReplacementTransform(lab, new_lab), run_time=1.2)
            cur, lab = curve, new_lab
            self.wait(0.5)
        self.caption("次数越高，贴合的范围越宽；误差不超过拉格朗日余项的上界", "Higher degree fits a wider range; the error stays below the Lagrange bound", wait=0.6)
        self.play(*[FadeOut(m) for m in (ax, g, cur, lab)])
        self.card([["泰勒公式", "Taylor's formula"],
                   MathTex(r"f(x)=\sum_{k=0}^{n}\frac{f^{(k)}(x_0)}{k!}(x-x_0)^k+\frac{f^{(n+1)}(\xi)}{(n+1)!}(x-x_0)^{n+1}", font_size=40),
                   ["n 次多项式的误差至多与 (x − x₀)ⁿ⁺¹ 同阶", "The error of degree n is at most of order (x − x₀)ⁿ⁺¹"]])
