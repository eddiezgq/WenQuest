"""动画 3.3.1（配图 3.3.1）：数列 (−1)ⁿ/n 的点一个个画出；给出 ε 带，找到 N，此后的点都在带内；
ε 缩小，N 后移；最后对 (−1)ⁿ，ε = 0.5 时无论 N 取多大总有点跳出带外。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("3.3", "ε–N：数列落进误差带", "ε–N: the terms fall into the band")
        ax = Axes(x_range=[0, 60, 10], y_range=[-1.1, 1.1, 0.5], x_length=11, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(DOWN * 0.5)
        self.play(Create(ax))
        a = lambda n: (-1) ** n / n
        dots = VGroup(*[Dot(ax.c2p(n, a(n)), radius=0.045, color=STEEL) for n in range(1, 61)])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.08), run_time=4)
        self.caption("(−1)ⁿ/n：在 0 的两侧跳动，离 0 越来越近", "(−1)ⁿ/n jumps around 0, getting closer", wait=0.3)
        for eps in (0.2, 0.05, 0.02):
            N = math.ceil(1 / eps)
            band = Rectangle(width=ax.c2p(60, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, eps)[1] - ax.c2p(0, -eps)[1],
                             stroke_width=0, fill_color=RED, fill_opacity=0.2).move_to(ax.c2p(30, 0))
            lab = MathTex(r"\varepsilon = %g" % eps, font_size=34, color=RED).next_to(ax.c2p(60, eps), UR, buff=0.1)
            self.play(FadeIn(band), FadeIn(lab))
            line = DashedLine(ax.c2p(N, -1.1), ax.c2p(N, 1.1), color=YELLOW)
            nl = MathTex(r"N = %d" % N, font_size=34, color=YELLOW).next_to(ax.c2p(N, 1.1), UP, buff=0.05)
            self.play(Create(line), FadeIn(nl))
            self.play(*[d.animate.set_color(GREEN) for n, d in zip(range(1, 61), dots) if n > N], run_time=1)
            self.caption("第 N 项以后，全部落在带内", "After the N-th term, every term lies in the band", wait=0.6)
            self.play(FadeOut(band), FadeOut(lab), FadeOut(line), FadeOut(nl), *[d.animate.set_color(STEEL) for d in dots], run_time=0.6)
        self.caption("对手缩小 ε，我们总能找到 N：数列收敛于 0", "However small ε, an N exists: the limit is 0", wait=0.3)
        self.play(FadeOut(dots))
        b = lambda n: (-1) ** n
        dots2 = VGroup(*[Dot(ax.c2p(n, b(n)), radius=0.045, color=STEEL) for n in range(1, 61)])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots2], lag_ratio=0.05), run_time=2.5)
        band = Rectangle(width=ax.c2p(60, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, 0.5)[1] - ax.c2p(0, -0.5)[1],
                         stroke_width=0, fill_color=RED, fill_opacity=0.2).move_to(ax.c2p(30, 1))
        self.play(FadeIn(band))
        self.caption("(−1)ⁿ：带放在 1 附近，奇数项总在带外", "(−1)ⁿ: a band around 1 always misses the odd terms", wait=0.3)
        self.play(*[d.animate.set_color(RED) for n, d in zip(range(1, 61), dots2) if n % 2 == 1])
        self.play(band.animate.move_to(ax.c2p(30, -1)), *[d.animate.set_color(RED) for n, d in zip(range(1, 61), dots2) if n % 2 == 0],
                  *[d.animate.set_color(STEEL) for n, d in zip(range(1, 61), dots2) if n % 2 == 1], run_time=1.5)
        self.caption("放到哪里都不行：(−1)ⁿ 发散", "Wherever the band goes, terms escape: (−1)ⁿ diverges")
        self.play(*[FadeOut(m) for m in (band, dots2, ax)])
        self.card([["数列极限的定义", "The limit of a sequence"],
                   MathTex(r"\forall\varepsilon>0,\ \exists N,\ n>N\ \Rightarrow\ |a_n-L|<\varepsilon", font_size=46),
                   ["ε 是给定的误差带，N 是“从哪一项起”", "ε: the given band; N: from which term on"]])
