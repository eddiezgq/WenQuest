"""动画 8.1.1（配图 8.1.1）：微分是增量的线性主部——方形钢板边长增加 Δx：两条长条 2xΔx 是 dS，角上的小方块 (Δx)² 是高阶小量；
Δx 缩小时，小方块在增量中所占的比例趋于零。再看曲线：Δy 与切线的增量 dy 之差随 Δx 平方缩小。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("8.1", "微分：增量的线性主部", "The differential: the linear part of the increment")
        x = 3.0
        dx = ValueTracker(1.0)
        O = LEFT * 4.6 + DOWN * 2.4
        base = Square(side_length=x, color=WHITE, fill_color=STEEL, fill_opacity=0.35).move_to(O + (x / 2) * (RIGHT + UP))
        right = always_redraw(lambda: Rectangle(width=dx.get_value(), height=x, stroke_width=1, color=YELLOW, fill_color=YELLOW, fill_opacity=0.5)
                              .move_to(O + RIGHT * (x + dx.get_value() / 2) + UP * x / 2))
        top = always_redraw(lambda: Rectangle(width=x, height=dx.get_value(), stroke_width=1, color=YELLOW, fill_color=YELLOW, fill_opacity=0.5)
                            .move_to(O + RIGHT * x / 2 + UP * (x + dx.get_value() / 2)))
        corner = always_redraw(lambda: Square(side_length=dx.get_value(), stroke_width=1, color=RED, fill_color=RED, fill_opacity=0.7)
                               .move_to(O + (x + dx.get_value() / 2) * (RIGHT + UP)))
        lx = MathTex("x", font_size=34).next_to(base, DOWN, buff=0.15)
        self.play(FadeIn(base), FadeIn(lx))
        self.play(FadeIn(right), FadeIn(top), FadeIn(corner))
        lab = VGroup(MathTex(r"\Delta S = 2x\,\Delta x + (\Delta x)^2", font_size=36),
                     MathTex(r"dS = 2x\,dx", font_size=36, color=YELLOW),
                     MathTex(r"(\Delta x)^2", font_size=36, color=RED)).arrange(DOWN, aligned_edge=LEFT, buff=0.35).to_edge(RIGHT).shift(UP * 0.6 + LEFT * 0.6)
        ratio = always_redraw(lambda: MathTex(r"\frac{(\Delta x)^2}{\Delta A} = %.3f" % (dx.get_value() ** 2 / (2 * x * dx.get_value() + dx.get_value() ** 2)),
                                              font_size=36).next_to(lab, DOWN, buff=0.5, aligned_edge=LEFT))
        self.play(Write(lab), FadeIn(ratio))
        self.caption("黄色长条是微分 dS，红色小方块是高阶小量", "Yellow strips: the differential dS; red square: higher order", wait=0.3)
        self.play(dx.animate.set_value(0.08), run_time=4)
        self.caption("Δx 越小，小方块所占的比例越小：ΔS ≈ dS", "The smaller Δx, the smaller the red share: ΔS ≈ dS", wait=0.5)
        for m in (right, top, corner, ratio):
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in (base, right, top, corner, lab, ratio, lx)])
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 3, 1], x_length=7, y_length=5, tips=False, axis_config={"color": GREY_B}).shift(DOWN * 0.4)
        f = lambda t: 0.25 * t ** 2 + 0.3 * t + 0.3
        g = ax.plot(f, x_range=[0, 3], color=WHITE, stroke_width=3)
        x0 = 1.0
        tan = ax.plot(lambda t: f(x0) + (0.5 * x0 + 0.3) * (t - x0), x_range=[0, 3], color=STEEL, stroke_width=2)
        self.play(Create(ax), Create(g), Create(tan))
        h = ValueTracker(1.6)
        dy = always_redraw(lambda: Line(ax.c2p(x0 + h.get_value(), f(x0)), ax.c2p(x0 + h.get_value(), f(x0) + (0.5 * x0 + 0.3) * h.get_value()), color=STEEL, stroke_width=6))
        gap = always_redraw(lambda: Line(ax.c2p(x0 + h.get_value(), f(x0) + (0.5 * x0 + 0.3) * h.get_value()), ax.c2p(x0 + h.get_value(), f(x0 + h.get_value())), color=RED, stroke_width=6))
        self.play(FadeIn(dy), FadeIn(gap))
        self.caption("蓝：切线的增量 dy；红：Δy − dy", "Blue: dy along the tangent; red: Δy − dy", wait=0.3)
        self.play(h.animate.set_value(0.2), run_time=4)
        self.caption("Δx 缩小一半，红段约缩小到四分之一", "Halve Δx and the red part shrinks to about a quarter")
        for m in (dy, gap):
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in (ax, g, tan, dy, gap)])
        self.card([["微分", "The differential"],
                   MathTex(r"\Delta y = f'(x)\,\Delta x + o(\Delta x),\qquad dy = f'(x)\,dx", font_size=42),
                   ["增量 = 线性主部（微分）+ 高阶小量", "Increment = linear part (differential) + higher-order term"]])
