"""动画 9.1.1：线性映射把网格变成网格。矩阵 [[1, 1], [0.5, 1.5]] 作用于平面：网格线仍是等距的平行直线，原点不动；
e1、e2 的像就是矩阵的两列，知道了它们就知道了整个映射。对照：非线性映射把网格弄弯；平移保持网格平行，但原点动了，也不是线性映射。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def make_plane(self):
        pl = NumberPlane(x_range=[-7, 7, 1], y_range=[-5, 5, 1],
                         background_line_style={"stroke_color": BLUE_D, "stroke_width": 1.5, "stroke_opacity": 0.7})
        pl.prepare_for_nonlinear_transform()
        return pl

    def construct(self):
        self.title("9.1", "线性映射：网格仍是网格", "Linear maps keep grid lines parallel and evenly spaced")
        ghost = NumberPlane(x_range=[-7, 7, 1], y_range=[-5, 5, 1],
                            background_line_style={"stroke_color": GREY_D, "stroke_width": 1, "stroke_opacity": 0.5}, axis_config={"stroke_opacity": 0.3})
        pl = self.make_plane()
        self.add(ghost)
        self.bring_to_back(ghost)
        self.play(Create(pl), run_time=1.5)
        e1 = Arrow(ORIGIN, RIGHT, buff=0, color=RED, stroke_width=7)
        e2 = Arrow(ORIGIN, UP, buff=0, color=GREEN, stroke_width=7)
        dot = Dot(ORIGIN, color=YELLOW, radius=0.09)
        self.play(GrowArrow(e1), GrowArrow(e2), FadeIn(dot))
        self.caption("e₁（红）与 e₂（绿），原点（黄）", "e₁ (red), e₂ (green) and the origin (yellow)", wait=0.8)
        M = np.array([[1.0, 1.0], [0.5, 1.5]])
        M3 = np.array([[1.0, 1.0, 0], [0.5, 1.5, 0], [0, 0, 1]])
        mat = MathTex(r"A=\begin{pmatrix}1&1\\0.5&1.5\end{pmatrix}", font_size=40).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
        mat.add_background_rectangle(opacity=0.8)
        self.play(FadeIn(mat))
        self.caption("用矩阵 A 作用于整个平面", "Apply A to the whole plane", wait=0.2)
        self.play(ApplyMatrix(M3, pl), ApplyMatrix(M3, e1, about_point=ORIGIN), ApplyMatrix(M3, e2, about_point=ORIGIN), run_time=3)
        self.caption("网格线仍是等距的平行直线，原点不动：这是线性映射", "Grid lines stay parallel and evenly spaced, the origin stays put: a linear map", wait=1.5)
        cols = VGroup(MathTex(r"A\boldsymbol e_1=(1,\,0.5)", color=RED, font_size=34),
                      MathTex(r"A\boldsymbol e_2=(1,\,1.5)", color=GREEN, font_size=34)).arrange(DOWN, aligned_edge=LEFT).next_to(mat, DOWN, buff=0.3)
        cols.add_background_rectangle(opacity=0.8)
        self.play(FadeIn(cols))
        self.caption("e₁、e₂ 的像就是 A 的两列；知道它们，就知道每个向量的像", "The images of e₁ and e₂ are the columns of A; they determine the image of every vector", wait=1.8)
        self.play(FadeOut(pl), FadeOut(e1), FadeOut(e2), FadeOut(mat), FadeOut(cols))
        # 非线性
        pl2 = self.make_plane()
        self.play(FadeIn(pl2))
        f = lambda p: np.array([p[0] + 0.5 * np.sin(p[1]), p[1] + 0.5 * np.sin(p[0]), 0])
        self.caption("对照一：f(x, y) = (x + 0.5 sin y, y + 0.5 sin x)", "Contrast 1: f(x, y) = (x + 0.5 sin y, y + 0.5 sin x)", wait=0.2)
        self.play(ApplyPointwiseFunction(f, pl2), run_time=3)
        self.caption("网格线弯了：f 不是线性映射", "The grid lines bend: f is not linear", wait=1.5)
        self.play(FadeOut(pl2))
        # 平移
        pl3 = self.make_plane()
        self.play(FadeIn(pl3))
        self.caption("对照二：平移 T(v) = v + (1, 0.5)", "Contrast 2: the translation T(v) = v + (1, 0.5)", wait=0.2)
        moved = Dot(ORIGIN, color=ORANGE, radius=0.09)
        self.add(moved)
        self.play(pl3.animate.shift(RIGHT + 0.5 * UP), moved.animate.shift(RIGHT + 0.5 * UP), run_time=2.5)
        self.caption("网格仍平行，可原点被移走了：T(0) ≠ 0，平移不是线性映射", "The grid stays parallel but the origin moves: T(0) ≠ 0, so a translation is not linear", wait=1.8)
        self.card([["线性映射：T(u + v) = T(u) + T(v)，T(cv) = cT(v)", "Linear: T(u + v) = T(u) + T(v), T(cv) = cT(v)"],
                   ["网格变成等距平行的网格，原点不动", "Grids go to evenly spaced parallel grids; the origin stays"],
                   ["基向量的像决定整个映射：它们就是矩阵的各列", "The images of the basis vectors, the columns, determine the map"]])
