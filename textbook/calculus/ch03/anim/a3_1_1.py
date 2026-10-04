"""动画 3.1.1（配图 3.1.1）：刘徽割圆。圆内接正多边形从 6 边起逐次加倍到 3072 边，面积数列逼近 π；
最后放大边界，3072 边形与圆几乎分不出来。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("3.1", "割之弥细，所失弥少", "Liu Hui: the finer the cut, the less is lost")
        R = 2.6
        c0 = LEFT * 2.2 + DOWN * 0.4
        circle = Circle(radius=R, color=WHITE, stroke_width=3).move_to(c0)
        self.play(Create(circle), run_time=1.2)

        def poly(n):
            pts = [c0 + R * np.array([math.cos(2 * math.pi * k / n + math.pi / 2), math.sin(2 * math.pi * k / n + math.pi / 2), 0]) for k in range(n)]
            return Polygon(*pts, color=STEEL, stroke_width=2.5, fill_color=STEEL, fill_opacity=0.25)

        area = lambda n: n / 2 * math.sin(2 * math.pi / n)

        def sci(v):
            m, e = ("%.2e" % v).split("e")
            return r"%s\times 10^{%d}" % (m, int(e))
        n = 6
        p = poly(n)
        read = VGroup(zh("边数 n = 6", 30, INK), MathTex(r"S_n = %.8f" % area(6), font_size=38, color=STEEL),
                      MathTex(r"\pi - S_n = " + sci(math.pi - area(6)), font_size=34, color=YELLOW)
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(RIGHT, buff=0.6).shift(UP * 0.5)
        self.play(DrawBorderThenFill(p), FadeIn(read))
        self.caption("正六边形：面积约 2.6，与圆相差一截", "The hexagon: area about 2.6, well short of the circle", wait=0.3)
        for n in (12, 24, 48, 96, 192, 384, 768, 1536, 3072):
            q = poly(n)
            new = VGroup(zh("边数 n = %d" % n, 30, INK), MathTex(r"S_n = %.8f" % area(n), font_size=38, color=STEEL),
                         MathTex(r"\pi - S_n = " + sci(math.pi - area(n)), font_size=34, color=YELLOW)
                         ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(read, aligned_edge=LEFT)
            rt = 1.2 if n <= 96 else 0.6
            self.play(Transform(p, q), Transform(read, new), run_time=rt)
            if n == 24:
                self.caption("边数每加倍一次，误差缩小到约四分之一", "Each doubling cuts the error to about a quarter", wait=0.3)
            if n == 192:
                self.caption("刘徽算到 192 边：π ≈ 3.14", "Liu Hui stopped at 192 sides: π ≈ 3.14", wait=0.3)
        self.caption("放大边界：3072 边形与圆几乎重合", "Zoom in at the edge: the 3072-gon hugs the circle", wait=0.3)
        top = c0 + UP * R
        self.play(VGroup(circle, p).animate.scale(40, about_point=top).shift(ORIGIN + DOWN * 0.5 - top), run_time=3)
        self.wait(1)
        self.play(FadeOut(VGroup(circle, p)), FadeOut(read))
        self.card([["割之又割，以至于不可割，则与圆周合体而无所失矣", "Cut and cut again until no more cutting is possible: then it merges with the circle"],
                   MathTex(r"\lim_{n\to\infty} S_n = \pi", font_size=52),
                   ["数列的极限：一个无限的过程", "The limit of a sequence: an infinite process"]])
