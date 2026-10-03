"""动画 1.1.2（配图 1.1.1）：y = x² 在 [0, 1] 下方的面积。右端点矩形从上方盖住区域、左端点矩形从下方填进区域，
n = 4、8、16、64 时两组面积之和 R_n、L_n 互相靠拢，夹住 1/3。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("1.1", "面积：矩形越分越细", "Area: thinner and thinner boxes")
        ax = Axes(x_range=[0, 1.2, 0.25], y_range=[0, 1.2, 0.25], x_length=6, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(LEFT * 2 + UP * 0.1)
        f = lambda x: x * x
        curve = ax.plot(f, x_range=[0, 1.1], color=WHITE, stroke_width=4)
        region = ax.get_area(ax.plot(f, x_range=[0, 1]), x_range=[0, 1], color=YELLOW, opacity=0.25)
        self.play(Create(ax), Create(curve), FadeIn(region))
        self.caption("曲线 y = x² 下方、0 到 1 之间的面积是多少？", "How much area lies under y = x² between 0 and 1?")

        def boxes(n, right, color):
            g = VGroup()
            for k in range(n):
                xk = k / n
                hgt = f((k + 1) / n) if right else f(k / n)
                if hgt <= 0:
                    continue
                g.add(Polygon(ax.c2p(xk, 0), ax.c2p(xk + 1 / n, 0), ax.c2p(xk + 1 / n, hgt), ax.c2p(xk, hgt),
                              color=color, stroke_width=1.5, fill_color=color, fill_opacity=0.25))
            return g

        def sums(n):
            R = (n + 1) * (2 * n + 1) / (6 * n * n)
            L = (n - 1) * (2 * n - 1) / (6 * n * n)
            return VGroup(zh("n = %d" % n, 28, INK), zh("上方：R = %.5f" % R, 26, STEEL), zh("下方：L = %.5f" % L, 26, GREEN)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.9)

        up, low, lab = boxes(4, True, STEEL), boxes(4, False, GREEN), sums(4)
        self.play(FadeIn(up), FadeIn(lab))
        self.caption("右端点作高：矩形从上方盖住区域，面积偏大", "Right-end heights: boxes cover the region, too big")
        self.play(FadeIn(low))
        self.caption("左端点作高：矩形落在区域里面，面积偏小", "Left-end heights: boxes sit inside, too small")
        for n in (8, 16, 64):
            self.play(Transform(up, boxes(n, True, STEEL)), Transform(low, boxes(n, False, GREEN)), Transform(lab, sums(n)), run_time=1.8)
            self.wait(0.8)
        self.caption("两组和互相靠拢，夹住同一个数 1/3", "The two sums close in on the same number, 1/3")
        self.card([["面积是矩形面积之和的极限", "Area is the limit of sums of boxes"],
                   MathTex(r"L_n<A<R_n,\qquad R_n-L_n=\frac1n\to 0,\qquad A=\frac13", font_size=46)])
