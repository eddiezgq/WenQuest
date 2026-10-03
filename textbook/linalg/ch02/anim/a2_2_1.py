"""动画 2.2.1（配图 2.2.2）：u = (2, 1)、w = (1, 3) 的线性组合 c₁u + c₂w。先固定 c₂ 让 c₁ 变化，终点扫出一条直线；
再让 c₂ 也变化，扫出的直线族铺满平面；最后走到 b = 2u + 3w = (7, 11)。换成平行的两个向量时，组合只在一条直线上。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("2.2", "线性组合铺满平面", "Linear combinations fill the plane")
        k = 0.28
        O = np.array([-3.2, -2.2, 0.0])
        u, w = np.array([2.0, 1.0]), np.array([1.0, 3.0])

        def P(v):
            return O + k * np.array([v[0], v[1], 0.0])

        axes = VGroup(Line(P([-4, 0]), P([20, 0]), color=GREY_B, stroke_width=1.5), Line(P([0, -3]), P([0, 18]), color=GREY_B, stroke_width=1.5))
        self.play(Create(axes))
        au = Arrow(P([0, 0]), P(u), buff=0, color=BLUE, stroke_width=7, max_tip_length_to_length_ratio=0.35)
        aw = Arrow(P([0, 0]), P(w), buff=0, color=GREEN, stroke_width=7, max_tip_length_to_length_ratio=0.35)
        lu = MathTex(r"\boldsymbol u", color=BLUE, font_size=36).next_to(P(u), DOWN, buff=0.1)
        lw = MathTex(r"\boldsymbol w", color=GREEN, font_size=36).next_to(P(w), LEFT, buff=0.1)
        self.play(GrowArrow(au), GrowArrow(aw), FadeIn(lu), FadeIn(lw))
        self.caption("两个不平行的向量 u = (2, 1)，w = (1, 3)", "Two non-parallel vectors u = (2, 1), w = (1, 3)")
        c1, c2 = ValueTracker(0.0), ValueTracker(0.0)

        def combo():
            a, b = c1.get_value(), c2.get_value()
            e1, e2 = a * u, a * u + b * w
            g = VGroup()
            if abs(a) > 1e-3:
                g.add(Arrow(P([0, 0]), P(e1), buff=0, color=BLUE_C, stroke_width=5, max_tip_length_to_length_ratio=0.12))
            if abs(b) > 1e-3:
                g.add(Arrow(P(e1), P(e2), buff=0, color=GREEN_C, stroke_width=5, max_tip_length_to_length_ratio=0.12))
            g.add(Dot(P(e2), color=YELLOW, radius=0.07))
            return g

        read = always_redraw(lambda: MathTex(r"c_1 = %.1f,\quad c_2 = %.1f" % (c1.get_value(), c2.get_value()), font_size=34)
                             .to_corner(UR, buff=0.5).shift(DOWN * 0.7))
        cg = always_redraw(combo)
        self.add(cg, read)
        trace = TracedPath(lambda: P(c1.get_value() * u + c2.get_value() * w), stroke_color=YELLOW, stroke_width=2, stroke_opacity=0.8)
        self.add(trace)
        self.play(c1.animate.set_value(-1.5), run_time=1.2)
        self.play(c1.animate.set_value(6.0), run_time=2.5)
        self.caption("只让 c₁ 变：终点沿 u 的方向扫出一条直线", "Vary c₁ only: the end point sweeps a line along u")
        lines = VGroup()
        for j in range(-3, 7):
            pts = [t * u + j * w for t in np.linspace(-6, 9, 301)]
            pts = [q for q in pts if -4 <= q[0] <= 19 and -3 <= q[1] <= 14]
            if len(pts) > 1:
                lines.add(Line(P(pts[0]), P(pts[-1]), color=YELLOW, stroke_width=1.5, stroke_opacity=0.5))
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.15), run_time=2.5)
        self.caption("每取一个 c₂，就得到一条平行线；c₂ 取遍实数，这些直线铺满整个平面",
                     "Each c₂ gives a parallel line; as c₂ ranges over all reals the lines fill the plane")
        self.play(FadeOut(trace), run_time=0.4)
        self.play(c1.animate.set_value(2.0), c2.animate.set_value(3.0), run_time=2.5)
        b = MathTex(r"\boldsymbol b = 2\boldsymbol u + 3\boldsymbol w = (7, 11)", color=YELLOW, font_size=34).next_to(P([7, 11]), RIGHT, buff=0.15)
        self.play(Write(b))
        self.caption("目标 b = (7, 11)：c₁ = 2，c₂ = 3，而且只有这一组", "Target b = (7, 11): c₁ = 2, c₂ = 3, and only these")
        self.wait(0.8)
        self.play(FadeOut(VGroup(lines, b, cg, read, au, aw, lu, lw)))
        p, q = np.array([1.0, 2.0]), np.array([-2.0, -4.0])
        ap = Arrow(P([0, 0]), P(p), buff=0, color=BLUE, stroke_width=7, max_tip_length_to_length_ratio=0.35)
        aq = Arrow(P([0, 0]), P(q), buff=0, color=GREEN, stroke_width=7, max_tip_length_to_length_ratio=0.35)
        self.play(GrowArrow(ap), GrowArrow(aq))
        s = ValueTracker(0.0)
        tr2 = TracedPath(lambda: P(s.get_value() * p), stroke_color=ORANGE, stroke_width=4)
        dot = always_redraw(lambda: Dot(P(s.get_value() * p), color=ORANGE, radius=0.07))
        self.add(tr2, dot)
        self.play(s.animate.set_value(8.0), run_time=1.5)
        self.play(s.animate.set_value(-1.0), run_time=2.0)
        self.caption("换成平行的 (1, 2) 与 (−2, −4)：无论系数怎么取，组合都在同一条直线上",
                     "With parallel (1, 2) and (−2, −4), every combination stays on one line")
        x = Cross(scale_factor=0.15, stroke_color=RED).move_to(P([4, 0]))
        nx = bi(["(4, 0) 永远凑不出来", "(4, 0) is never reached"], 24, RED).next_to(x, UP, buff=0.15)
        self.play(Create(x), FadeIn(nx))
        self.wait(1)
        self.card([["两个不平行的向量：组合铺满平面", "Two non-parallel vectors fill the plane"],
                   MathTex(r"c_1\boldsymbol u + c_2\boldsymbol w = \boldsymbol b", font_size=44),
                   ["求系数 = 解方程组", "Finding the coefficients = solving a linear system"]])
