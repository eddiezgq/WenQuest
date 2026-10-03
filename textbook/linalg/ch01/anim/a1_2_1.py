"""动画 1.2.1（配图 1.2.2）：平面网格依次经历伸缩 diag(2, 0.5)、旋转 30°、剪切 [[1, 1], [0, 1]]，
最后经历差速 AGV 的矩阵 A（r = 0.075 m，b = 0.40 m；网格的一格代表 8 rad/s 的轮速）。
始终跟踪 (1, 0)、(0, 1) 两个向量：它们落到哪里，矩阵的两列就是什么。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("1.2", "矩阵是平面的变换", "A matrix transforms the plane")
        c, s = math.cos(math.pi / 6), math.sin(math.pi / 6)
        r, b = 0.075, 0.40
        mats = [
            (np.array([[2.0, 0.0], [0.0, 0.5]]), ["伸缩", "Stretch"], r"\begin{pmatrix}2&0\\0&0.5\end{pmatrix}"),
            (np.array([[c, -s], [s, c]]), ["旋转 30°", "Rotation by 30°"], r"\begin{pmatrix}\cos30^\circ&-\sin30^\circ\\ \sin30^\circ&\cos30^\circ\end{pmatrix}"),
            (np.array([[1.0, 1.0], [0.0, 1.0]]), ["剪切", "Shear"], r"\begin{pmatrix}1&1\\0&1\end{pmatrix}"),
            (8 * np.array([[r / 2, r / 2], [-r / b, r / b]]), ["差速 AGV（一格 = 8 rad/s）", "Differential AGV (one cell = 8 rad/s)"],
             r"8\begin{pmatrix}r/2&r/2\\-r/b&r/b\end{pmatrix}=\begin{pmatrix}0.3&0.3\\-1.5&1.5\end{pmatrix}"),
        ]
        O = np.array([-1.8, -0.25, 0.0])
        k = 0.92
        t = ValueTracker(0.0)
        cur = {"M": np.eye(2)}

        def M():
            return (1 - t.get_value()) * np.eye(2) + t.get_value() * cur["M"]

        def P(v):
            w = M() @ np.asarray(v, dtype=float)
            return O + k * np.array([w[0], w[1], 0.0])

        def scene():
            g = VGroup()
            for i in range(-3, 4):
                g.add(Line(P([i, -3]), P([i, 3]), color=BLUE_C if i else WHITE, stroke_width=1.2 if i else 2.4, stroke_opacity=0.6 if i else 0.9))
                g.add(Line(P([-3, i]), P([3, i]), color=BLUE_C if i else WHITE, stroke_width=1.2 if i else 2.4, stroke_opacity=0.6 if i else 0.9))
            g.add(Polygon(P([0, 0]), P([1, 0]), P([1, 1]), P([0, 1]), color=YELLOW, fill_opacity=0.35, stroke_width=2))
            g.add(Arrow(P([0, 0]), P([1, 0]), buff=0, color=RED, stroke_width=7, max_tip_length_to_length_ratio=0.3))
            g.add(Arrow(P([0, 0]), P([0, 1]), buff=0, color=GREEN, stroke_width=7, max_tip_length_to_length_ratio=0.3))
            return g

        ref = VGroup(*[Line(O + k * np.array([i, -3, 0]), O + k * np.array([i, 3, 0]), color=GREY_D, stroke_width=1) for i in range(-3, 4)],
                     *[Line(O + k * np.array([-3, i, 0]), O + k * np.array([3, i, 0]), color=GREY_D, stroke_width=1) for i in range(-3, 4)])
        self.add(ref)
        g = always_redraw(scene)
        self.play(FadeIn(g))
        self.caption("红箭头是 (1, 0)，绿箭头是 (0, 1)，黄色是单位正方形", "Red is (1, 0), green is (0, 1), yellow is the unit square")
        for A, name, tex in mats:
            cur["M"] = A
            t.set_value(0.0)
            head = bi(name, 28, YELLOW).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
            mt = MathTex(tex, font_size=34).next_to(head, DOWN, buff=0.25).align_to(head, RIGHT)
            bg1 = BackgroundRectangle(VGroup(head, mt), fill_opacity=0.85, buff=0.15)
            self.play(FadeIn(bg1), FadeIn(head), Write(mt))
            self.play(t.animate.set_value(1.0), run_time=2.5)
            col1 = MathTex(r"\text{col}_1 = (%.2g,\ %.2g)" % (A[0, 0], A[1, 0]), font_size=30, color=RED)
            col2 = MathTex(r"\text{col}_2 = (%.2g,\ %.2g)" % (A[0, 1], A[1, 1]), font_size=30, color=GREEN)
            cols = VGroup(col1, col2).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(mt, DOWN, buff=0.35).align_to(mt, RIGHT)
            bg2 = BackgroundRectangle(cols, fill_opacity=0.85, buff=0.12)
            self.play(FadeIn(bg2), FadeIn(cols))
            self.caption("(1, 0) 落到第 1 列，(0, 1) 落到第 2 列；直线仍是直线，原点不动",
                         "(1, 0) lands on column 1, (0, 1) on column 2; lines stay lines, the origin stays put", wait=1.2)
            self.play(t.animate.set_value(0.0), FadeOut(VGroup(bg1, bg2, head, mt, cols)), run_time=1.2)
        self.card([["矩阵的两列 = 两个基本向量的像", "The columns = images of the two basic vectors"],
                   MathTex(r"A\begin{pmatrix}1\\0\end{pmatrix}=\boldsymbol a_1,\qquad A\begin{pmatrix}0\\1\end{pmatrix}=\boldsymbol a_2", font_size=44),
                   ["网格线保持平行且等距", "Grid lines stay parallel and evenly spaced"]])
