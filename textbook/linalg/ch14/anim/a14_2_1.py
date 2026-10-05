"""动画 14.2.1：谱定理 A = QΛQᵀ 的几何意义。A = [[2, 1], [1, 2]]，特征值 1、3，特征向量 (1, −1)/√2、(1, 1)/√2 互相垂直。
把 A 的作用拆成三步：Qᵀ 把两条主轴转到坐标轴上；Λ 沿坐标轴分别伸缩 1 倍、3 倍；Q 再转回去。单位圆变成主轴沿特征向量的椭圆，
与直接用 A 变换的结果完全相同。对称矩阵 = 转动 + 沿互相垂直的方向伸缩 + 转回来。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("14.2", "谱定理：对称矩阵 = 转过去、伸缩、转回来", "The spectral theorem: rotate, stretch, rotate back")
        s = 0.85
        O = np.array([0.0, -0.45, 0.0])
        P = lambda x: O + s * np.array([x[0], x[1], 0.0])
        A = np.array([[2.0, 1.0], [1.0, 2.0]])
        Q = np.array([[1.0, 1.0], [-1.0, 1.0]]) / np.sqrt(2)          # 列：(1, −1)/√2 → λ = 1，(1, 1)/√2 → λ = 3
        L = np.diag([1.0, 3.0])
        m3 = lambda M: np.block([[M, np.zeros((2, 1))], [np.zeros((1, 2)), np.ones((1, 1))]])
        mk = lambda: NumberPlane(x_range=[-5, 5, 1], y_range=[-3, 3, 1], x_length=10 * s, y_length=6 * s,
                                 background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.5}).move_to(O)
        plane = mk()
        self.play(Create(plane), run_time=1.0)
        board = MathTex(r"A = \begin{pmatrix}2 & 1\\ 1 & 2\end{pmatrix} = Q\Lambda Q^{\mathsf T}", font_size=34).to_corner(UR, buff=0.45).shift(DOWN * 0.85)
        self.play(FadeIn(board))
        t = np.linspace(0, 2 * np.pi, 181)
        circ = VMobject(color=GOLD, stroke_width=4).set_points_smoothly([P((np.cos(a), np.sin(a))) for a in t])
        q1 = Arrow(P((0, 0)), P(Q[:, 0]), buff=0, color=GREEN, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        q2 = Arrow(P((0, 0)), P(Q[:, 1]), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        grp = VGroup(circ, q1, q2)
        self.play(Create(circ), GrowArrow(q1), GrowArrow(q2))
        self.caption("单位圆和两个互相垂直的特征向量：q₁（λ = 1）、q₂（λ = 3）", "The unit circle and two perpendicular eigenvectors: q₁ (λ = 1), q₂ (λ = 3)", wait=1.0)
        self.play(ApplyMatrix(m3(Q.T), grp, about_point=O), run_time=1.6)
        self.caption("第 1 步 Qᵀ：转动，把两个特征向量转到坐标轴上", "Step 1, Qᵀ: rotate the eigenvectors onto the axes", wait=0.9)
        self.play(ApplyMatrix(m3(L), grp, about_point=O), run_time=1.8)
        self.caption("第 2 步 Λ：沿坐标轴伸缩，横向 1 倍、纵向 3 倍，互不干扰", "Step 2, Λ: stretch along the axes, 1× and 3×, independently", wait=1.0)
        self.play(ApplyMatrix(m3(Q), grp, about_point=O), run_time=1.6)
        self.caption("第 3 步 Q：转回去。得到主轴沿特征向量的椭圆", "Step 3, Q: rotate back. An ellipse with axes along the eigenvectors", wait=1.0)
        direct = VMobject(color=WHITE, stroke_width=2).set_points_smoothly([P(A @ np.array([np.cos(a), np.sin(a)])) for a in t])
        direct.set_stroke(opacity=0.9)
        self.play(Create(direct), run_time=1.5)
        self.caption("直接用 A 变换单位圆（白线），结果完全相同", "Transforming the circle by A directly (white) gives exactly the same ellipse", wait=1.4)
        self.card([["对称矩阵的特征向量互相垂直，特征值是实数", "A symmetric matrix has perpendicular eigenvectors and real eigenvalues"],
                   ["A = QΛQᵀ：转过去、沿主轴伸缩、转回来", "A = QΛQᵀ: rotate, stretch along the axes, rotate back"],
                   ["单位圆的像是椭圆，半轴沿特征向量、长度是 |λ|", "The unit circle maps to an ellipse with semi-axes |λ| along the eigenvectors"]])
