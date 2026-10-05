"""动画 13.1.1：变换下不改变方向的向量。A = [[3, 1], [0, 2]] 作用于整个平面：一般的向量 (1, 1) 被转离它原来所在的直线；
x 轴上的向量只被拉长 3 倍，直线 y = −x 上的向量只被拉长 2 倍——这两条直线在变换下不动，它们上面的向量就是特征向量。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("13.1", "特征向量：变换后仍在原来直线上的向量", "Eigenvectors: vectors that stay on their own line")
        s = 0.55
        O = np.array([0.0, -0.5, 0.0])
        P = lambda x: O + s * np.array([x[0], x[1], 0.0])
        A = np.array([[3.0, 1.0], [0.0, 2.0]])
        A3 = np.eye(3); A3[:2, :2] = A
        Ai3 = np.eye(3); Ai3[:2, :2] = np.linalg.inv(A)
        mk = lambda: NumberPlane(x_range=[-12, 12, 1], y_range=[-6, 6, 1], x_length=24 * s, y_length=12 * s,
                                 background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.6}).move_to(O)
        plane = mk()
        self.play(Create(plane), run_time=1.0)
        board = MathTex(r"A = \begin{pmatrix}3 & 1\\ 0 & 2\end{pmatrix}", font_size=36).to_corner(UR, buff=0.5).shift(DOWN * 0.9)
        self.play(FadeIn(board))

        def arr(x, col):
            return Arrow(P((0, 0)), P(x), buff=0, color=col, stroke_width=6, max_tip_length_to_length_ratio=0.2)

        def span(d, col):
            d = np.array(d, float) / np.linalg.norm(d)
            return DashedLine(P(-9 * d), P(9 * d), color=col, stroke_width=2)

        v = np.array([1.0, 1.0])
        V, Lv = arr(v, YELLOW), span(v, YELLOW)
        self.play(Create(Lv), GrowArrow(V))
        self.caption("取一个向量 v = (1, 1)，虚线是它所在的直线", "Take v = (1, 1); the dashed line is the line it spans", wait=0.6)
        self.play(ApplyMatrix(A3, plane, about_point=O), Transform(V, arr(A @ v, YELLOW)), run_time=2)
        self.caption("Av = (4, 2) 离开了原来的直线：方向变了", "Av = (4, 2) has left its line: the direction changed", wait=1.2)
        self.play(ApplyMatrix(Ai3, plane, about_point=O), Transform(V, arr(v, YELLOW)), run_time=1.2)
        self.play(FadeOut(V), FadeOut(Lv))
        e1, e2 = np.array([1.0, 0.0]), np.array([-1.0, 1.0])
        L1, L2 = span(e1, RED), span(e2, GREEN)
        E1, E2 = arr(e1, RED), arr(e2, GREEN)
        self.play(Create(L1), Create(L2), GrowArrow(E1), GrowArrow(E2))
        self.caption("再看两条特别的直线：x 轴和 y = −x", "Now two special lines: the x-axis and y = −x", wait=0.6)
        self.play(ApplyMatrix(A3, plane, about_point=O), Transform(E1, arr(A @ e1, RED)), Transform(E2, arr(A @ e2, GREEN)), run_time=2.2)
        l1 = MathTex(r"A\boldsymbol x_1 = 3\boldsymbol x_1", color=RED, font_size=34).next_to(P(A @ e1), DOWN, buff=0.15)
        l2 = MathTex(r"A\boldsymbol x_2 = 2\boldsymbol x_2", color=GREEN, font_size=34).next_to(P(A @ e2), LEFT, buff=0.15)
        self.play(FadeIn(l1), FadeIn(l2))
        self.caption("它们仍在原来的直线上，只被拉长 3 倍、2 倍：这就是特征向量与特征值", "They stay on their lines, only stretched 3× and 2×: eigenvectors and eigenvalues", wait=1.8)
        self.card([["Ax = λx：方向不变，长度乘以 λ", "Ax = λx: same line, length times λ"],
                   ["特征向量所在的直线在变换下不动", "The line through an eigenvector is mapped to itself"],
                   ["用特征向量作基，A 就成了对角矩阵", "In a basis of eigenvectors, A becomes diagonal"]])
