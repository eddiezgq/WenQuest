"""动画 17.1.1：不能对角化的矩阵。若尔当块 J = λI + N，N = [[0, 1], [0, 0]]。
第 1 步：N 把 e₂ 送到 e₁、把 e₁ 送到 0——若尔当链 e₂ → e₁ → 0；第 2 步：J = I + N 是剪切，平面上只有 e₁ 方向不转；
第 3 步：反复作用 J，任何向量的方向都越来越贴近 e₁（J^k = I + kN）；对照：可对角化的 diag(1, 1.5) 有两条不转的直线。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("17.1", "若尔当块：只有一个特征方向", "A Jordan block: only one eigendirection")
        s = 0.9
        O = np.array([-1.8, -0.5, 0.0])
        P = lambda x, y: O + s * np.array([x, y, 0.0])
        m3 = lambda M: np.block([[M, np.zeros((2, 1))], [np.zeros((1, 2)), np.ones((1, 1))]])
        plane = NumberPlane(x_range=[-6, 6, 1], y_range=[-3, 3, 1], x_length=12 * s, y_length=6 * s,
                            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.6}).move_to(O)
        self.play(Create(plane), run_time=1.0)
        board = MathTex(r"J=\begin{pmatrix}1 & 1\\ 0 & 1\end{pmatrix}=I+N", font_size=36).to_corner(UR, buff=0.4).shift(DOWN * 0.9)
        self.play(FadeIn(board))
        e1 = Arrow(P(0, 0), P(1, 0), buff=0, color=YELLOW, stroke_width=7, max_tip_length_to_length_ratio=0.25)
        e2 = Arrow(P(0, 0), P(0, 1), buff=0, color=GREEN, stroke_width=7, max_tip_length_to_length_ratio=0.25)
        l1 = MathTex(r"\boldsymbol e_1", color=YELLOW, font_size=34).next_to(P(1, 0), DOWN, buff=0.12)
        l2 = MathTex(r"\boldsymbol e_2", color=GREEN, font_size=34).next_to(P(0, 1), LEFT, buff=0.12)
        self.play(GrowArrow(e1), GrowArrow(e2), FadeIn(l1), FadeIn(l2))
        nb = MathTex(r"N\boldsymbol e_2=\boldsymbol e_1,\quad N\boldsymbol e_1=\boldsymbol 0", font_size=34).next_to(board, DOWN, buff=0.35)
        self.play(FadeIn(nb))
        ghost = e2.copy().set_opacity(0.35)
        self.add(ghost)
        self.play(Transform(e2, Arrow(P(0, 0), P(1, 0), buff=0, color=GREEN, stroke_width=7, max_tip_length_to_length_ratio=0.25).shift(UP * 0.12)),
                  Transform(e1, Dot(P(0, 0), color=YELLOW, radius=0.08)), run_time=1.6)
        self.caption("若尔当链：N 把 e₂ 送到 e₁，再把 e₁ 送到 0。e₂ 是“广义特征向量”", "Jordan chain: N sends e₂ to e₁ and e₁ to 0; e₂ is a generalized eigenvector", wait=1.2)
        self.play(FadeOut(e1), FadeOut(e2), FadeOut(ghost), FadeOut(l1), FadeOut(l2), FadeOut(nb))
        # 第 2 步：剪切
        pts = [(1.5, 0.0), (1.2, 1.2), (0.0, 1.5), (-1.2, 1.2), (-1.5, 0.0), (-1.2, -1.2), (0.0, -1.5), (1.2, -1.2)]
        arrows = VGroup(*[Arrow(P(0, 0), P(*p), buff=0, color=(YELLOW if abs(p[1]) < 1e-9 else TEAL), stroke_width=5,
                                max_tip_length_to_length_ratio=0.18) for p in pts])
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.08), run_time=1.2)
        J = np.array([[1.0, 1.0], [0.0, 1.0]])
        self.play(ApplyMatrix(m3(J), plane, about_point=O), ApplyMatrix(m3(J), arrows, about_point=O), run_time=2.0)
        self.caption("J 是剪切：横轴（黄）上的向量不转，其余的都转了。只有一个特征方向", "J is a shear: vectors on the x-axis (yellow) keep their direction, all others turn. Only one eigendirection", wait=1.4)
        for k in range(2):
            self.play(ApplyMatrix(m3(J), plane, about_point=O), ApplyMatrix(m3(J), arrows, about_point=O), run_time=1.3)
        self.caption("反复作用：Jᵏ = I + kN，所有向量的方向都越来越贴近 e₁", "Repeat: Jᵏ = I + kN, and every direction creeps towards e₁", wait=1.4)
        self.play(FadeOut(arrows), FadeOut(plane), FadeOut(board))
        # 对照：可对角化
        plane2 = NumberPlane(x_range=[-6, 6, 1], y_range=[-2, 2, 1], x_length=12 * s, y_length=4 * s,
                             background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.6}).move_to(O)
        board2 = MathTex(r"D=\begin{pmatrix}1 & 0\\ 0 & 1.5\end{pmatrix}", font_size=36).to_corner(UR, buff=0.4).shift(DOWN * 0.9)
        arrows2 = VGroup(*[Arrow(P(0, 0), P(*np.array(p) * 0.7), buff=0, color=(YELLOW if abs(p[1]) < 1e-9 or abs(p[0]) < 1e-9 else TEAL),
                                 stroke_width=5, max_tip_length_to_length_ratio=0.18) for p in pts])
        self.play(Create(plane2), FadeIn(board2), LaggedStart(*[GrowArrow(a) for a in arrows2], lag_ratio=0.08), run_time=1.4)
        D = np.diag([1.0, 1.5])
        self.play(ApplyMatrix(m3(D), plane2, about_point=O), ApplyMatrix(m3(D), arrows2, about_point=O), run_time=2.0)
        self.caption("对照：可对角化的 D 有两条不转的直线（横轴、纵轴），向量可以按它们分解", "Compare: the diagonalizable D has two invariant lines, and vectors split along them", wait=1.4)
        self.card([["若尔当块只有一个特征方向", "A Jordan block has a single eigendirection"],
                   ["若尔当链：(A − λI) 把链上的向量逐个送向 0", "Jordan chain: A − λI pushes each vector down the chain to 0"],
                   ["Jᵏ = λᵏI + kλᵏ⁻¹N：多出 k·λᵏ⁻¹ 这样的项", "Jᵏ = λᵏI + kλᵏ⁻¹N: an extra k·λᵏ⁻¹ term"]])
