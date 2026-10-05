"""动画 8.5.1：四个子空间的全景图。以秩 1 的 A = [[1, 2], [3, 6]] 为例：
左边是输入空间 ℝ²，行空间（沿 (1, 2)）与零空间（沿 (−2, 1)）垂直；右边是输出空间 ℝ²，列空间（沿 (1, 3)）与左零空间（沿 (−3, 1)）垂直。
配色与图 8.5.1 相同：行空间蓝、零空间绿、列空间红、左零空间橙。
x 分解为 x_r + x_n；A 把 x_n 压成零，把 x_r 送到列空间中的 Ax = A x_r；左零空间的方向永远到不了。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("8.5", "四个基本子空间的全景图", "The big picture of the four subspaces")
        A = np.array([[1.0, 2.0], [3.0, 6.0]])
        r = np.array([1.0, 2.0]) / np.sqrt(5)
        n = np.array([-2.0, 1.0]) / np.sqrt(5)
        c = np.array([1.0, 3.0]) / np.sqrt(10)
        ln = np.array([-3.0, 1.0]) / np.sqrt(10)
        OL, OR, s = np.array([-3.4, -0.6, 0]), np.array([3.4, -0.6, 0]), 0.75
        PL = lambda v: OL + s * np.array([v[0], v[1], 0])
        PR = lambda v: OR + 0.2 * s * np.array([v[0], v[1], 0])

        def frame(O, zh, en):
            ax = VGroup(Line(O + LEFT * 2.6, O + RIGHT * 2.6, color=GREY_D, stroke_width=1.5),
                        Line(O + DOWN * 2.4, O + UP * 2.4, color=GREY_D, stroke_width=1.5))
            return VGroup(ax, bi([zh, en], 24, GREY_B).next_to(O + UP * 2.4, UP, buff=0.1))

        FL, FR = frame(OL, "输入空间 ℝ²", "input space ℝ²"), frame(OR, "输出空间 ℝ²", "output space ℝ²")
        self.play(FadeIn(FL), FadeIn(FR))
        L = 3.0
        rowL = Line(PL(-L * r), PL(L * r), color=BLUE, stroke_width=5)
        nulL = Line(PL(-L * n), PL(L * n), color=GREEN, stroke_width=5)
        colL = Line(PR(-15 * c), PR(15 * c), color=RED, stroke_width=5)
        lnuL = Line(PR(-15 * ln), PR(15 * ln), color=ORANGE, stroke_width=5)
        tags = VGroup(bi(["行空间", "row space"], 22, BLUE).move_to(PL(2.3 * r) + RIGHT * 0.9),
                      bi(["零空间", "null space"], 22, GREEN).move_to(PL(2.6 * n) + UP * 0.45),
                      bi(["列空间", "column space"], 22, RED).move_to(PR(-11 * c) + RIGHT * 1.0),
                      bi(["左零空间", "left null space"], 22, ORANGE).move_to(PR(13 * ln) + UP * 0.45))
        self.play(Create(rowL), Create(nulL), FadeIn(tags[0]), FadeIn(tags[1]))
        self.caption("A = [[1, 2], [3, 6]]，秩 1：行空间与零空间各一维，互相垂直", "A = [[1, 2], [3, 6]], rank 1: row space and null space are lines, perpendicular", wait=1.0)
        self.play(Create(colL), Create(lnuL), FadeIn(tags[2]), FadeIn(tags[3]))
        self.caption("输出空间里：列空间沿 (1, 3)，左零空间沿 (−3, 1)，也互相垂直", "In the output space: column space along (1, 3), left null space along (−3, 1), also perpendicular", wait=1.0)

        a, b = ValueTracker(1.6), ValueTracker(1.2)
        z = np.zeros(2)

        def arrow(P, p, q, c, w=5):
            return Arrow(P(p), P(q), buff=0, color=c, stroke_width=w, max_tip_length_to_length_ratio=0.18) \
                if np.linalg.norm(np.array(q) - np.array(p)) > 0.12 else Dot(P(q), color=c, radius=0.06)

        def left():
            xr, xn = a.get_value() * r, b.get_value() * n
            return VGroup(DashedLine(PL(xr), PL(xr + xn), color=GREY_B, stroke_width=2),
                          DashedLine(PL(xn), PL(xr + xn), color=GREY_B, stroke_width=2),
                          arrow(PL, z, xr, BLUE), arrow(PL, z, xn, GREEN), arrow(PL, z, xr + xn, YELLOW, 6),
                          MathTex(r"\boldsymbol x", color=YELLOW, font_size=34).next_to(PL(xr + xn), UP, buff=0.08))

        def right():
            ax = A @ (a.get_value() * r + b.get_value() * n)
            return VGroup(arrow(PR, z, ax, YELLOW, 6),
                          MathTex(r"A\boldsymbol x", color=YELLOW, font_size=34).next_to(PR(ax), LEFT, buff=0.12))

        X = always_redraw(left)
        self.play(FadeIn(X))
        self.caption("每个 x 分解为 x = x_r + x_n：行空间分量（蓝）加零空间分量（绿）", "Every x splits as x = x_r + x_n: row-space part (blue) plus null-space part (green)", wait=1.0)
        Y = always_redraw(right)
        self.play(FadeIn(Y))
        self.caption("A 作用：Ax 落在列空间里", "Apply A: Ax lands in the column space", wait=0.8)
        self.caption("改变零空间分量 x_n：Ax 一动不动", "Change the null-space part x_n: Ax does not move", wait=0.2)
        self.play(b.animate.set_value(-1.6), run_time=2.5)
        self.play(b.animate.set_value(0.8), run_time=1.5)
        self.caption("A 把零空间压成零，Ax = A x_r", "A sends the null space to zero, so Ax = A x_r", wait=0.8)
        self.caption("改变行空间分量 x_r：Ax 沿列空间一一对应地移动", "Change the row-space part x_r: Ax moves along the column space, one-to-one", wait=0.2)
        self.play(a.animate.set_value(-1.2), run_time=2.5)
        self.play(a.animate.set_value(1.0), run_time=1.5)
        self.play(Indicate(lnuL, color=ORANGE, scale_factor=1.05), run_time=1.5)
        self.caption("左零空间的方向，Ax 永远到达不了：b 在这个方向上有分量时 Ax = b 无解", "Ax never reaches the left-null-space direction: if b has a part there, Ax = b has no solution", wait=1.2)
        self.play(FadeOut(X), FadeOut(Y))
        self.card([["ℝⁿ = 行空间 ⊕ 零空间，维数 r 与 n − r", "ℝⁿ = row space ⊕ null space, dimensions r and n − r"],
                   ["ℝᵐ = 列空间 ⊕ 左零空间，维数 r 与 m − r", "ℝᵐ = column space ⊕ left null space, dimensions r and m − r"],
                   ["A 把行空间一一对应到列空间，把零空间压成零", "A: row space ↔ column space, null space → 0"]])
