"""动画 15.1.1（配图 15.1.1）：辛普森公式——每两段用一条过三个点的抛物线代替曲线，一段段拼出整条曲线；
与梯形公式的折线比较，分段加倍时两者的误差。"""
from manim import *
from wq_anim import *
import numpy as np

F = lambda x: 0.5 + 0.9 * np.sin(1.3 * x) + 0.12 * x * x
XS = np.linspace(0, 3, 30001)
EXACT = float(np.sum((F(XS[1:]) + F(XS[:-1])) / 2 * np.diff(XS)))


def trap(n):
    x = np.linspace(0, 3, n + 1)
    return float(np.sum((F(x[1:]) + F(x[:-1])) / 2 * np.diff(x)))


def simp(n):
    x = np.linspace(0, 3, n + 1)
    h = 3 / n
    return float(h / 3 * (F(x[0]) + F(x[-1]) + 4 * F(x[1:-1:2]).sum() + 2 * F(x[2:-1:2]).sum()))


class Lesson(Base):
    def construct(self):
        self.title("15.1", "辛普森公式", "Simpson's rule")
        ax = Axes(x_range=[0, 3.2, 1], y_range=[0, 2.0, 1], x_length=6.6, y_length=4.4, tips=False,
                  axis_config={"color": GREY_B}).shift(LEFT * 2.6 + DOWN * 0.4)
        g = ax.plot(F, x_range=[0, 3], color=WHITE, stroke_width=3)
        self.play(Create(ax), Create(g))
        lab = MathTex(r"\int_0^3 f\,dx=%.5f" % EXACT, font_size=32).to_corner(UR).shift(DOWN * 1.0 + LEFT * 0.2)
        self.play(Write(lab))
        n = 4
        x = np.linspace(0, 3, n + 1)
        poly = VMobject(color=STEEL, stroke_width=3).set_points_as_corners([ax.c2p(a, F(a)) for a in x])
        dots = VGroup(*[Dot(ax.c2p(a, F(a)), color=STEEL, radius=0.06) for a in x])
        self.play(Create(poly), FadeIn(dots))
        tl = MathTex(r"T_4=%.5f" % trap(4), font_size=32, color=STEEL).next_to(lab, DOWN, aligned_edge=RIGHT)
        self.play(Write(tl))
        self.caption("梯形公式：相邻两点连直线", "Trapezoid: join neighbouring points by straight lines", wait=0.4)
        parts = VGroup()
        for k in range(n // 2):
            a, b = x[2 * k], x[2 * k + 2]
            m = (a + b) / 2
            c = np.polyfit([a, m, b], [F(a), F(m), F(b)], 2)
            pg = ax.plot(lambda t, c=c: float(np.polyval(c, t)), x_range=[a, b], color=ORANGE, stroke_width=4)
            area = ax.get_area(pg, x_range=[a, b], color=ORANGE, opacity=0.3)
            parts.add(pg, area)
            self.play(Create(pg), FadeIn(area), run_time=1.2)
        sl = MathTex(r"S_4=%.5f" % simp(4), font_size=32, color=ORANGE).next_to(tl, DOWN, aligned_edge=RIGHT)
        self.play(Write(sl))
        self.caption("辛普森公式：每两段用一条过三点的抛物线", "Simpson: one parabola through every three points", wait=0.6)
        self.play(FadeOut(poly), FadeOut(dots), FadeOut(parts))
        tab = VGroup()
        for i, m in enumerate((4, 8, 16)):
            row = MathTex(r"n=%d:\ \ |T-I|=%.1e,\ \ |S-I|=%.1e" % (m, abs(trap(m) - EXACT), abs(simp(m) - EXACT)), font_size=26)
            tab.add(row)
        tab.arrange(DOWN, aligned_edge=LEFT).next_to(sl, DOWN, buff=0.5).to_edge(RIGHT, buff=0.3)
        for row in tab:
            self.play(Write(row), run_time=0.8)
        self.caption("分段加倍：梯形误差约变为 1/4，辛普森约变为 1/16", "Double n: trapezoid error ÷4, Simpson ÷16", wait=1.0)
        self.play(*[FadeOut(m) for m in (ax, g, lab, tl, sl, tab)])
        self.card([["辛普森公式", "Simpson's rule"],
                   MathTex(r"\int_a^b f\,dx\approx\frac h3\bigl[f_0+4f_1+2f_2+4f_3+\cdots+4f_{n-1}+f_n\bigr]", font_size=40),
                   ["对三次多项式准确；误差与 h⁴ 成正比", "Exact for cubics; error proportional to h⁴"]])
