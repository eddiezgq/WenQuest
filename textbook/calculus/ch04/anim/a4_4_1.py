"""动画 4.4.1（配图 4.4.1）：ε–δ 的挑战与应答。f(x) = x² 在 x = 2 附近，ε = 1、0.3、0.1 依次给出，找到 δ；
最后看符号函数在 0 处：把带放在 1 附近，ε = 0.5 时无论 δ 多小，左侧总有一段跑出带外。"""
from manim import *
from wq_anim import *
import math


class Lesson(Base):
    def construct(self):
        self.title("4.4", "ε–δ：对手给 ε，你找 δ", "ε–δ: they give ε, you find δ")
        ax = Axes(x_range=[0.8, 3.2, 0.4], y_range=[0, 10, 2], x_length=9, y_length=5, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(DOWN * 0.4)
        f = ax.plot(lambda x: x * x, x_range=[0.8, 3.15], color=WHITE, stroke_width=3)
        pt = Dot(ax.c2p(2, 4), color=YELLOW)
        self.play(Create(ax), Create(f), FadeIn(pt))
        self.caption("f(x) = x²，在 x = 2 处极限 L = 4", "f(x) = x², limit L = 4 at x = 2", wait=0.3)
        W = ax.c2p(3.2, 0)[0] - ax.c2p(0.8, 0)[0]
        H = ax.c2p(0, 10)[1] - ax.c2p(0, 0)[1]
        for eps in (1.0, 0.3, 0.1):
            d = min(2 - math.sqrt(4 - eps), math.sqrt(4 + eps) - 2)
            hb = Rectangle(width=W, height=ax.c2p(0, 4 + eps)[1] - ax.c2p(0, 4 - eps)[1], stroke_width=0,
                           fill_color=RED, fill_opacity=0.25).move_to(ax.c2p(2, 4))
            el = MathTex(r"\varepsilon = %g" % eps, font_size=34, color=RED).next_to(ax.c2p(3.2, 4 + eps), UR, buff=0.1)
            self.play(FadeIn(hb), FadeIn(el))
            vb = Rectangle(width=ax.c2p(2 + d, 0)[0] - ax.c2p(2 - d, 0)[0], height=H, stroke_width=0,
                           fill_color=STEEL, fill_opacity=0.3).move_to(ax.c2p(2, 5))
            dl = MathTex(r"\delta \approx %.3f" % d, font_size=34, color=STEEL).next_to(ax.c2p(2 + d, 10), UR, buff=0.1)
            seg = ax.plot(lambda x: x * x, x_range=[2 - d, 2 + d], color=GREEN, stroke_width=7)
            self.play(FadeIn(vb), FadeIn(dl), Create(seg))
            self.caption("竖直带内的曲线，全部落进水平带", "Inside the vertical band, the curve stays in the horizontal band", wait=0.6)
            self.play(*[FadeOut(m) for m in (hb, el, vb, dl, seg)], run_time=0.6)
        self.caption("ε 再小，也总有 δ 应答：lim x² = 4", "However small ε, a δ answers: lim x² = 4", wait=0.3)
        self.play(*[FadeOut(m) for m in (ax, f, pt)])
        ax2 = Axes(x_range=[-1, 1, 0.5], y_range=[-1.5, 1.5, 0.5], x_length=9, y_length=5, tips=False,
                   axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(DOWN * 0.4)
        left = ax2.plot(lambda x: -1, x_range=[-1, -0.002], color=WHITE, stroke_width=3)
        right = ax2.plot(lambda x: 1, x_range=[0.002, 1], color=WHITE, stroke_width=3)
        holes = VGroup(Circle(0.07, color=WHITE).move_to(ax2.c2p(0, 1)), Circle(0.07, color=WHITE).move_to(ax2.c2p(0, -1)),
                       Dot(ax2.c2p(0, 0), color=WHITE))
        self.play(Create(ax2), Create(left), Create(right), FadeIn(holes))
        self.caption("符号函数 sgn x 在 0 处", "The sign function sgn x at 0", wait=0.2)
        W2 = ax2.c2p(1, 0)[0] - ax2.c2p(-1, 0)[0]
        H2 = ax2.c2p(0, 1.5)[1] - ax2.c2p(0, -1.5)[1]
        hb = Rectangle(width=W2, height=ax2.c2p(0, 1.5)[1] - ax2.c2p(0, 0.5)[1], stroke_width=0,
                       fill_color=RED, fill_opacity=0.25).move_to(ax2.c2p(0, 1))
        el = MathTex(r"L = 1,\ \varepsilon = 0.5", font_size=32, color=RED).to_corner(UR).shift(DOWN * 1.2)
        self.play(FadeIn(hb), FadeIn(el))
        for d in (0.6, 0.2, 0.05):
            vb = Rectangle(width=ax2.c2p(d, 0)[0] - ax2.c2p(-d, 0)[0], height=H2, stroke_width=0,
                           fill_color=STEEL, fill_opacity=0.3).move_to(ax2.c2p(0, 0))
            bad = ax2.plot(lambda x: -1, x_range=[-d, -0.002], color=RED, stroke_width=7)
            self.play(FadeIn(vb), Create(bad), run_time=0.8)
            self.wait(0.3)
            self.play(FadeOut(vb), FadeOut(bad), run_time=0.4)
        self.caption("δ 再小，左侧总有一段在带外：L = 1 不是极限", "However small δ, the left part escapes: L = 1 is not the limit", wait=0.3)
        el2 = MathTex(r"L = 0,\ \varepsilon = 0.5", font_size=32, color=RED).move_to(el)
        self.play(hb.animate.move_to(ax2.c2p(0, 0)), Transform(el, el2), run_time=1.2)
        d = 0.05
        vb = Rectangle(width=ax2.c2p(d, 0)[0] - ax2.c2p(-d, 0)[0], height=H2, stroke_width=0,
                       fill_color=STEEL, fill_opacity=0.3).move_to(ax2.c2p(0, 0))
        bad = VGroup(ax2.plot(lambda x: -1, x_range=[-d, -0.002], color=RED, stroke_width=7),
                     ax2.plot(lambda x: 1, x_range=[0.002, d], color=RED, stroke_width=7))
        self.play(FadeIn(vb), Create(bad), run_time=0.8)
        self.caption("L 取任何值都不行：宽为 1 的带盖不住相距为 2 的 −1 和 1", "No L works: a band of width 1 cannot cover both −1 and 1, which are 2 apart", wait=0.4)
        self.caption("所以 sgn x 在 0 处没有极限", "So sgn x has no limit at 0")
        self.play(*[FadeOut(m) for m in (ax2, left, right, holes, hb, el, vb, bad)])
        self.card([["函数极限的定义", "The limit of a function"],
                   MathTex(r"\forall\varepsilon>0,\ \exists\delta>0,\ 0<|x-a|<\delta\ \Rightarrow\ |f(x)-L|<\varepsilon", font_size=42),
                   ["ε 是给定的误差带，δ 是“离 a 多近”", "ε: the given band; δ: how close to a"]])
