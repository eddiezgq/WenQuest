"""动画 20.3.1：条件数。两条直线的交点是 2 阶方程组 n₁ᵀx = c₁、n₂ᵀx = c₂ 的解。
第 1 步：两条直线夹角大（70°），把第二条直线平移一点，交点只移动一点；
第 2 步：把第二条直线转到与第一条只差 8°，同样的平移让交点跑得很远；
第 3 步：两条直线各有 ±δ 的不确定带，交点的不确定区域是一个平行四边形：夹角越小，它越细长。条件数 κ₂ = cot(φ/2)。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("20.3", "条件数：直线几乎平行时", "Condition number: when the lines are nearly parallel")
        O = np.array([-1.2, -0.4, 0.0])
        s = 1.0
        P = lambda v: O + s * np.array([v[0], v[1], 0.0])
        plane = NumberPlane(x_range=[-6, 6, 1], y_range=[-3.5, 3.5, 1], x_length=12 * s, y_length=7 * s,
                            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.4}).move_to(O)
        self.play(Create(plane), run_time=0.8)
        a1 = np.radians(20.0)
        d1 = np.array([np.cos(a1), np.sin(a1)])
        ang = ValueTracker(90.0)            # 第二条直线的方向（度）
        off = ValueTracker(0.0)             # 第二条直线沿法向的平移

        def d2():
            a = np.radians(ang.get_value())
            return np.array([np.cos(a), np.sin(a)])

        def n2():
            d = d2()
            return np.array([-d[1], d[0]])

        def cross():
            n1 = np.array([-d1[1], d1[0]])
            N = np.vstack([n1, n2()])
            return np.linalg.solve(N, np.array([0.0, off.get_value()]))

        def long_line(p0, d, color, width=4, opacity=1.0):
            return Line(P(p0 - 12 * d), P(p0 + 12 * d), color=color, stroke_width=width, stroke_opacity=opacity)

        L1 = long_line(np.zeros(2), d1, YELLOW)
        L2 = always_redraw(lambda: long_line(off.get_value() * n2(), d2(), TEAL))
        dot = always_redraw(lambda: Dot(P(cross()), radius=0.09, color=RED))
        self.play(Create(L1), Create(L2), run_time=1.2)
        self.play(FadeIn(dot))
        phi = DecimalNumber(70, num_decimal_places=0, font_size=32, unit="^\\circ", color=WHITE).to_corner(DR, buff=0.5).shift(UP * 1.9)
        phi.add_updater(lambda m: m.set_value(abs(((ang.get_value() - 20 + 90) % 180) - 90)))
        phil = zh("夹角", 24, WHITE).next_to(phi, LEFT, buff=0.15)
        kap = DecimalNumber(1.43, num_decimal_places=1, font_size=32, color=ORANGE).next_to(phi, DOWN, buff=0.3, aligned_edge=RIGHT)
        kap.add_updater(lambda m: m.set_value(1 / np.tan(np.radians(max(abs(((ang.get_value() - 20 + 90) % 180) - 90), 0.5)) / 2)))
        kapl = MathTex(r"\kappa_2=", font_size=32, color=ORANGE).next_to(kap, LEFT, buff=0.12)
        self.play(FadeIn(phil), FadeIn(phi), FadeIn(kapl), FadeIn(kap))
        self.caption("两条直线的交点就是方程组的解；夹角 70° 时条件数约 1.4", "The intersection solves the 2×2 system; at 70° the condition number is about 1.4", wait=1.0)
        trail = TracedPath(lambda: P(cross()), stroke_color=RED, stroke_width=4)
        self.add(trail)
        for v in (0.3, -0.3, 0.0):
            self.play(off.animate.set_value(v), run_time=1.0)
        self.caption("把第二条直线平移 0.3：交点只移动约 0.3", "Shift the second line by 0.3: the intersection moves about 0.3", wait=1.0)
        self.play(FadeOut(trail), run_time=0.3)
        self.play(ang.animate.set_value(28.0), run_time=2.5)
        self.caption("把它转到与第一条只差 8°：条件数变成约 14", "Turn it to within 8° of the first line: κ₂ becomes about 14", wait=1.0)
        trail2 = TracedPath(lambda: P(cross()), stroke_color=RED, stroke_width=4)
        self.add(trail2)
        for v in (0.3, -0.3, 0.0):
            self.play(off.animate.set_value(v), run_time=1.4)
        self.caption("同样平移 0.3，交点却跑出两个多单位：放大约 7 倍（只动一条线时为 1/sin φ，最坏情形约为 κ₂）", "The same 0.3 shift moves the intersection over 2 units: about 7× (1/sin φ for one line; about κ₂ at worst)", wait=1.6)
        self.play(FadeOut(trail2), run_time=0.3)

        # 第 3 步：两条带的交集
        def band(p_dir, n, half, color):
            q = [P(-12 * p_dir + half * n), P(12 * p_dir + half * n), P(12 * p_dir - half * n), P(-12 * p_dir - half * n)]
            return Polygon(*q, color=color, fill_color=color, fill_opacity=0.18, stroke_width=0)

        n1 = np.array([-d1[1], d1[0]])

        def para():
            N = np.vstack([n1, n2()])
            corners = [np.linalg.solve(N, np.array([a, b])) for a, b in ((0.25, 0.25), (0.25, -0.25), (-0.25, -0.25), (-0.25, 0.25))]
            return Polygon(*[P(c) for c in corners], color=RED, fill_color=RED, fill_opacity=0.6, stroke_width=2)

        B1 = band(d1, n1, 0.25, YELLOW)
        B2 = always_redraw(lambda: band(d2(), n2(), 0.25, TEAL))
        PG = always_redraw(para)
        self.play(FadeIn(B1), FadeIn(B2), FadeIn(PG))
        self.caption("每条直线有 ±δ 的不确定带，交点落在红色平行四边形里：夹角小，它就细长", "Each line has a ±δ band; the solution lies in the red parallelogram, long and thin when the angle is small", wait=1.2)
        self.play(ang.animate.set_value(110.0), run_time=2.5)
        self.caption("夹角 90° 时平行四边形最小：条件数为 1", "At 90° the parallelogram is smallest: κ₂ = 1", wait=1.2)
        self.card([["条件数：数据误差被放大多少倍", "Condition number: how much data errors are amplified"],
                   ["直线几乎平行 ⇔ 矩阵接近奇异 ⇔ 条件数大", "Nearly parallel lines ⇔ nearly singular matrix ⇔ large κ"],
                   [r"κ₂ = σ₁/σₙ；两条直线时 κ₂ = cot(φ/2)", "κ₂ = σ₁/σₙ; for two lines κ₂ = cot(φ/2)"]])
