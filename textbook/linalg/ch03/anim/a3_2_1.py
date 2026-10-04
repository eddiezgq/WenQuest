"""动画 3.2.1：二元方程组 2x − y = 1、x + y = 5 的消元。第 2 个方程减去第 1 个方程的 1/2 倍，第二条直线绕交点 (2, 3)
转成水平线 1.5y = 4.5；第 1 个方程加上新第 2 个方程的 2/3 倍，第一条直线转成竖直线 2x = 4。直线在变，交点始终不动。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("3.2", "消元：换直线，不换交点", "Elimination: new lines, same point")
        O = np.array([-3.4, -2.6, 0.0])
        k = 0.85

        def P(x, y):
            return O + k * np.array([x, y, 0.0])

        axes = VGroup(Line(P(-0.5, 0), P(6, 0), color=GREY_B), Line(P(0, -0.5), P(0, 6), color=GREY_B))
        self.play(Create(axes))
        e1, e2 = np.array([2.0, -1.0, 1.0]), np.array([1.0, 1.0, 5.0])
        t1, t2 = ValueTracker(0.0), ValueTracker(0.0)

        def cur():
            r2 = e2 - 0.5 * t1.get_value() * e1
            r1 = e1 + (2 / 3) * t2.get_value() * (e2 - 0.5 * e1)
            return r1, r2

        def seg(r, color):
            a, b, c = r
            pts = []
            for x in (-0.5, 6):
                if abs(b) > 1e-9:
                    pts.append((x, (c - a * x) / b))
            for y in (-0.5, 6):
                if abs(a) > 1e-9:
                    pts.append(((c - b * y) / a, y))
            pts = [p for p in pts if -0.51 <= p[0] <= 6.01 and -0.51 <= p[1] <= 6.01]
            pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in pts))
            return Line(P(*pts[0]), P(*pts[-1]), color=color, stroke_width=5)

        def eqtex(r, color):
            a, b, c = r
            def term(v, name, first):
                if abs(v) < 1e-9:
                    return ""
                sgn = "" if first and v > 0 else ("+" if v > 0 else "-")
                return f"{sgn}{'' if abs(abs(v) - 1) < 1e-9 else format(abs(v), '.2g')}{name}"
            s = term(a, "x", True) + term(b, "y", abs(a) < 1e-9)
            return MathTex(s + f"={c:.2g}", color=color, font_size=36)

        L = always_redraw(lambda: VGroup(seg(cur()[0], BLUE), seg(cur()[1], GREEN), Dot(P(2, 3), color=RED, radius=0.09)))
        E = always_redraw(lambda: VGroup(eqtex(cur()[0], BLUE), eqtex(cur()[1], GREEN)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).shift(DOWN * 0.6))
        self.play(FadeIn(L), FadeIn(E))
        self.caption("两个方程，两条直线，交点 (2, 3)", "Two equations, two lines, meeting at (2, 3)")
        self.caption("第 2 个方程减去第 1 个方程的 1/2 倍", "Subtract 1/2 of equation 1 from equation 2", wait=0.2)
        self.play(t1.animate.set_value(1.0), run_time=3)
        self.caption("第二条直线绕交点转成水平线：y = 3 已经求出", "The second line turns level about the point: y = 3", wait=1.0)
        self.caption("第 1 个方程加上新第 2 个方程的 2/3 倍", "Add 2/3 of the new equation 2 to equation 1", wait=0.2)
        self.play(t2.animate.set_value(1.0), run_time=3)
        self.caption("第一条直线转成竖直线：x = 2。直线一直在变，交点始终不动", "The first line turns vertical: x = 2. The lines changed, the point never moved", wait=1.2)
        self.card([["行变换换掉了直线，却不改变交点", "Row operations change the lines, not the point"],
                   ["消元就是把直线转到最容易读出交点的位置", "Elimination turns the lines until the point is easy to read"]])
