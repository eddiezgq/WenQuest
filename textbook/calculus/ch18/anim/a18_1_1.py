"""动画 18.1.1（配图 18.1.1）：达布上和与下和——f(x) = x² 在 [0, 1] 上，分割加密时，外接矩形（上和）往下压、内接矩形（下和）往上长，
两者之差 1/n 趋于零，把面积 1/3 夹住；狄利克雷函数在每个小区间上的上确界是 1、下确界是 0，上和恒为 1、下和恒为 0，夹不住。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("18.1", "达布上和与下和", "Upper and lower Darboux sums")
        ax = Axes(x_range=[0, 1.05, 0.5], y_range=[0, 1.1, 0.5], x_length=6.0, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B}).shift(LEFT * 3.0 + DOWN * 0.4)
        g = ax.plot(lambda x: x * x, x_range=[0, 1], color=WHITE, stroke_width=3)
        self.play(Create(ax), Create(g))

        def rects(n, top):
            grp = VGroup()
            for k in range(n):
                xa, xb = k / n, (k + 1) / n
                h = (xb if top else xa) ** 2
                if h <= 0:
                    continue
                r = Polygon(ax.c2p(xa, 0), ax.c2p(xb, 0), ax.c2p(xb, h), ax.c2p(xa, h),
                            color=ORANGE if top else STEEL, fill_opacity=0.25 if top else 0.55, stroke_width=1)
                grp.add(r)
            return grp

        up, lo, lab = None, None, None
        for n in (2, 4, 8, 16, 32):
            U = sum(((k + 1) / n) ** 2 for k in range(n)) / n
            L = sum((k / n) ** 2 for k in range(n)) / n
            nu, nl = rects(n, True), rects(n, False)
            nlab = VGroup(MathTex(r"n=%d" % n, font_size=34),
                          MathTex(r"U=%.4f" % U, font_size=34, color=ORANGE),
                          MathTex(r"L=%.4f" % L, font_size=34, color=STEEL),
                          MathTex(r"U-L=%.4f" % (U - L), font_size=34)).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT, buff=0.8)
            if up is None:
                self.play(FadeIn(nu), FadeIn(nl), Write(nlab))
                self.caption("上和取每段的最大值，下和取最小值：面积被夹在中间", "Upper sum uses the max on each piece, lower the min", wait=0.6)
            else:
                self.play(ReplacementTransform(up, nu), ReplacementTransform(lo, nl), ReplacementTransform(lab, nlab), run_time=1.0)
            up, lo, lab = nu, nl, nlab
        self.caption("分割加密：上和变小、下和变大，差 1/n 趋于零，夹住 1/3", "Refining: U falls, L rises, U − L = 1/n → 0", wait=0.8)
        self.play(FadeOut(up), FadeOut(lo), FadeOut(lab), FadeOut(g))
        # 狄利克雷函数
        dots_q = VGroup(*[Dot(ax.c2p(x, 1), radius=0.025, color=ORANGE) for x in np.linspace(0, 1, 61)])
        dots_i = VGroup(*[Dot(ax.c2p(x, 0), radius=0.025, color=STEEL) for x in np.linspace(0.008, 0.992, 61)])
        dl = Text("D(x)：有理数处为 1，无理数处为 0", font_size=24).next_to(ax, UP, buff=0.15)
        self.play(FadeIn(dots_q), FadeIn(dots_i), Write(dl))
        for n in (4, 16):
            nu = VGroup(*[Polygon(ax.c2p(k / n, 0), ax.c2p((k + 1) / n, 0), ax.c2p((k + 1) / n, 1), ax.c2p(k / n, 1),
                                  color=ORANGE, fill_opacity=0.2, stroke_width=1) for k in range(n)])
            nlab = VGroup(MathTex(r"n=%d" % n, font_size=34), MathTex(r"U=1", font_size=34, color=ORANGE),
                          MathTex(r"L=0", font_size=34, color=STEEL), MathTex(r"U-L=1", font_size=34)).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT, buff=0.8)
            if up is None or n == 4:
                self.play(FadeIn(nu), Write(nlab))
            else:
                self.play(ReplacementTransform(up, nu), ReplacementTransform(lab, nlab))
            up, lab = nu, nlab
        self.caption("狄利克雷函数：每一段里都有有理数和无理数，上和恒为 1、下和恒为 0", "Dirichlet: every piece has rationals and irrationals; U = 1, L = 0 always", wait=1.0)
        self.play(*[FadeOut(m) for m in (ax, up, lab, dots_q, dots_i, dl)])
        self.card([["可积准则", "Integrability criterion"],
                   MathTex(r"f\ \text{integrable}\iff\forall\varepsilon>0\ \exists P:\ U(f,P)-L(f,P)<\varepsilon", font_size=40),
                   ["上和与下和能夹紧，函数才可积", "A function is integrable exactly when U and L can squeeze together"]])
