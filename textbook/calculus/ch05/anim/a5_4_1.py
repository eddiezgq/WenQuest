"""动画 5.4.1（配图 5.4.1）：介值定理——水平线 y = C 在 f(a)、f(b) 之间上下移动，总与曲线相交；
有间断时反例；零点定理的证明就是二分法：区间一次次减半，夹住一个零点。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("5.4", "介值定理与二分法", "The intermediate value theorem and bisection")
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 3, 1], x_length=9, y_length=4.8, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": False}).shift(DOWN * 0.4)
        f = lambda x: 1 + 0.9 * np.sin(1.4 * x) + 0.35 * x
        g = ax.plot(f, x_range=[0, 4], color=WHITE, stroke_width=3)
        la, lb = MathTex("a", font_size=30).next_to(ax.c2p(0, 0), DOWN), MathTex("b", font_size=30).next_to(ax.c2p(4, 0), DOWN)
        self.play(Create(ax), Create(g), FadeIn(la), FadeIn(lb))
        C = ValueTracker(1.2)
        line = always_redraw(lambda: DashedLine(ax.c2p(0, C.get_value()), ax.c2p(4, C.get_value()), color=RED))
        xs = np.linspace(0, 4, 4001)

        def hits():
            c = C.get_value()
            v = f(xs) - c
            idx = np.where(np.diff(np.sign(v)) != 0)[0]
            return VGroup(*[Dot(ax.c2p(xs[i], c), color=RED, radius=0.07) for i in idx])
        dots = always_redraw(hits)
        self.play(Create(line), FadeIn(dots))
        self.caption("C 取 f(a) 与 f(b) 之间的任何值，水平线都与曲线相交", "For any C between f(a) and f(b), the line meets the curve", wait=0.2)
        fb = f(4.0)
        refs = VGroup(DashedLine(ax.c2p(0, 1.0), ax.c2p(4, 1.0), color=GREY_B, stroke_width=1.5),
                      DashedLine(ax.c2p(0, fb), ax.c2p(4, fb), color=GREY_B, stroke_width=1.5))
        self.play(FadeIn(refs))
        self.play(C.animate.set_value(fb - 0.03), run_time=3)
        self.play(C.animate.set_value(1.03), run_time=3)
        line.clear_updaters(); dots.clear_updaters()
        self.play(*[FadeOut(m) for m in (line, dots, g, refs)])
        left = ax.plot(lambda x: 0.8, x_range=[0, 2], color=WHITE, stroke_width=3)
        right = ax.plot(lambda x: 2.2, x_range=[2.02, 4], color=WHITE, stroke_width=3)
        hole = Circle(radius=0.07, color=WHITE).move_to(ax.c2p(2, 2.2))
        cl = DashedLine(ax.c2p(0, 1.5), ax.c2p(4, 1.5), color=RED)
        self.play(Create(left), Create(right), FadeIn(hole), Create(cl))
        self.caption("函数有跳跃：C = 1.5 被“跳过”了", "With a jump, C = 1.5 is skipped", wait=0.6)
        self.play(*[FadeOut(m) for m in (left, right, hole, cl)])
        h = lambda x: 1 + 0.9 * np.sin(1.4 * x) + 0.35 * x - 1.6
        ax2 = Axes(x_range=[0, 4, 1], y_range=[-1, 1.5, 0.5], x_length=9, y_length=4.8, tips=False,
                   axis_config={"color": GREY_B, "include_numbers": False}).shift(DOWN * 0.4)
        g2 = ax2.plot(h, x_range=[0, 4], color=WHITE, stroke_width=3)
        self.play(ReplacementTransform(ax, ax2), Create(g2))
        self.caption("零点定理：两端异号，用二分法夹住一个零点", "Zero theorem: opposite signs at the ends; bisection traps a zero", wait=0.2)
        lo, hi = 0.0, 4.0
        bar = Line(ax2.c2p(lo, 0), ax2.c2p(hi, 0), color=STEEL, stroke_width=10)
        self.play(Create(bar))
        for k in range(7):
            m = (lo + hi) / 2
            md = Dot(ax2.c2p(m, h(m)), color=RED)
            self.play(FadeIn(md), run_time=0.4)
            if (h(m) > 0) == (h(lo) > 0):
                lo = m
            else:
                hi = m
            self.play(bar.animate.put_start_and_end_on(ax2.c2p(lo, 0), ax2.c2p(hi, 0)), FadeOut(md), run_time=0.5)
        xi = Dot(ax2.c2p((lo + hi) / 2, 0), color=YELLOW, radius=0.09)
        xl = MathTex(r"\xi", font_size=36, color=YELLOW).next_to(xi, UR, buff=0.08)
        self.play(FadeIn(xi), FadeIn(xl))
        self.caption("区间每步减半，长度趋于 0；闭区间套给出极限点 ξ，连续性给出 f(ξ) = 0",
                     "The interval halves each step; nested intervals give a point ξ, continuity gives f(ξ) = 0")
        self.play(*[FadeOut(m) for m in (ax2, g2, bar, la, lb, xi, xl)])
        self.card([["介值定理", "Intermediate value theorem"],
                   ["f 在 [a, b] 上连续，C 介于 f(a)、f(b) 之间 ⇒ 存在 ξ，f(ξ) = C", "f continuous on [a, b], C between f(a) and f(b) ⇒ some ξ has f(ξ) = C"],
                   ["条件：闭区间、连续；结论：只说存在，不说在哪里", "Needs a closed interval and continuity; says a root exists, not where"]])
