"""动画 2.2.1（配图 2.2.1）：线性变换让整个平面的方格均匀变形；基向量落到矩阵的两列上，单位正方形的面积变为 |det A|。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.2", "线性变换：方格的均匀变形", "A linear map deforms the grid evenly")
        U = 1.25                                   # 屏幕上 1 个单位的长度
        O = np.array([-2.2, -0.6, 0])
        t = ValueTracker(0.0)
        state = {"M": np.eye(2)}

        def cur():
            s = t.get_value()
            return (1 - s) * np.eye(2) + s * state["M"]

        def P(x, y, M):
            v = M @ np.array([x, y])
            return O + U * np.array([v[0], v[1], 0])

        def grid():
            M = cur()
            g = VGroup()
            for k in np.arange(-3, 3.01, 1):
                g.add(Line(P(k, -2.5, M), P(k, 2.5, M), color=BLUE_E, stroke_width=1.5))
                g.add(Line(P(-3, k, M), P(3, k, M), color=BLUE_E, stroke_width=1.5))
            sq = Polygon(P(0, 0, M), P(1, 0, M), P(1, 1, M), P(0, 1, M), color=YELLOW, fill_color=YELLOW, fill_opacity=0.35, stroke_width=2)
            e1 = Arrow(P(0, 0, M), P(1, 0, M), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.2)
            e2 = Arrow(P(0, 0, M), P(0, 1, M), buff=0, color=GREEN, stroke_width=6, max_tip_length_to_length_ratio=0.2)
            return VGroup(g, sq, e1, e2)

        def panel():
            M = cur()
            m = MathTex(r"A=\begin{pmatrix}%.2f & %.2f\\ %.2f & %.2f\end{pmatrix}" % (M[0, 0], M[0, 1], M[1, 0], M[1, 1]), font_size=40)
            d = MathTex(r"\det A = %.2f" % np.linalg.det(M), color=YELLOW, font_size=38)
            return VGroup(m, d).arrange(DOWN, buff=0.35).move_to(np.array([4.2, 0.9, 0]))

        g = always_redraw(grid)
        pnl = always_redraw(panel)
        self.add(g)
        self.play(FadeIn(pnl), run_time=0.6)
        self.caption("红、绿箭头是两个基向量，黄色是单位正方形", "Red and green: the basis vectors; yellow: the unit square", wait=1.0)
        cases = [
            (np.array([[math.cos(math.radians(30)), -math.sin(math.radians(30))], [math.sin(math.radians(30)), math.cos(math.radians(30))]]),
             "转动 30°：面积不变，det = 1", "Rotation by 30°: area kept, det = 1"),
            (np.array([[1.0, 0.5], [0.0, 1.0]]), "剪切：正方形变成平行四边形，面积仍为 1", "Shear: the square becomes a parallelogram of area 1"),
            (np.array([[1.5, 0.0], [0.0, 0.5]]), "伸缩 1.5 倍与 0.5 倍：面积变为 0.75", "Scaling by 1.5 and 0.5: area 0.75"),
            (np.array([[1.0, 0.0], [0.0, -1.0]]), "反射：面积不变，方向翻转，det = −1", "Reflection: area kept, orientation flipped, det = −1"),
        ]
        for M, zh_t, en_t in cases:
            state["M"] = M
            t.set_value(0)
            self.caption(zh_t, en_t, wait=0)
            self.play(t.animate.set_value(1), run_time=2.0)
            self.wait(1.2)
            self.play(t.animate.set_value(0), run_time=0.8)
        self.caption("直线仍是直线，平行等距的格线仍平行等距", "Lines stay lines; parallel, evenly spaced grid lines stay so", wait=0)
        state["M"] = np.array([[1.0, 0.5], [0.0, 1.0]])
        self.play(t.animate.set_value(1), run_time=1.5)
        self.wait(1.0)
        self.card([["线性变换的矩阵", "The matrix of a linear map"],
                   ["第 j 列 = 第 j 个基向量的像", "column j = image of the j-th basis vector"],
                   ["面积放大 |det A| 倍；det < 0 表示翻转", "areas scale by |det A|; det < 0 means a flip"]])
