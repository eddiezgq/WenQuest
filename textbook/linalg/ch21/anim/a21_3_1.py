"""动画 21.3.1：格什戈林圆盘。算例 21.3.1 的矩阵 A，把非对角元乘以 t：A(t) = diag(A) + t(A − diag(A))。
第 1 步：t = 0，特征值就是对角元 10、4、−2；
第 2 步：t 从 0 增大到 1，三个圆盘（半径 tRᵢ）随之扩大，特征值（红点）从圆心出发移动，但始终不离开圆盘；三个圆盘互不相交，各含一个特征值；
第 3 步：t 继续增大到 3，第 1、2 个圆盘相交，此后只能断定并集里有两个特征值；
第 4 步：回到 t = 1，用 D = diag(1, 1, 0.25) 缩放，前两个圆盘缩小、第三个扩大，特征值不动。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("21.3", "格什戈林圆盘：不求特征值，先圈出它们", "Gershgorin discs: locate eigenvalues without computing them")
        A = np.array([[10.0, 1.0, -0.5], [0.4, 4.0, 0.8], [0.6, 0.2, -2.0]])
        Dg = np.diag(np.diag(A))
        s = 0.5
        O = np.array([-2.7, -0.4, 0.0])                     # 复平面上 0 的位置
        P = lambda z: O + s * np.array([z.real, z.imag, 0.0])
        axis = NumberLine(x_range=[-5, 14, 1], length=19 * s, include_numbers=False, color=GREY_B).move_to(P(4.5 + 0j))
        yax = Line(P(-4.4j), P(4.4j), color=GREY_B, stroke_width=2)
        labels = VGroup(*[MathTex(str(k), font_size=24, color=GREY_B).next_to(P(k + 0j), DOWN, buff=0.15) for k in (-4, -2, 0, 2, 4, 6, 8, 10, 12)])
        self.play(Create(axis), Create(yax), FadeIn(labels), run_time=1.0)
        t = ValueTracker(0.0)
        dsc = ValueTracker(1.0)                              # 第 3 个分量的缩放 δ
        cols = (RED_C, GREEN_C, BLUE_C)

        def mat():
            M = Dg + t.get_value() * (A - Dg)
            D = np.diag([1.0, 1.0, dsc.get_value()])
            return np.linalg.inv(D) @ M @ D

        def discs():
            M = mat()
            c = np.diag(M)
            r = np.sum(np.abs(M), axis=1) - np.abs(c)
            g = VGroup()
            for ci, ri, col in zip(c, r, cols):
                g.add(Circle(radius=max(ri * s, 0.001), color=col, stroke_width=3, fill_color=col, fill_opacity=0.15).move_to(P(ci + 0j)))
            return g

        def eigs():
            z = np.linalg.eigvals(mat())
            return VGroup(*[Dot(P(complex(w)), radius=0.08, color=YELLOW) for w in z])

        D_ = always_redraw(discs)
        E_ = always_redraw(eigs)
        centers = VGroup(*[Cross(scale_factor=0.12, stroke_color=WHITE, stroke_width=3).move_to(P(c + 0j)) for c in np.diag(A)])
        self.play(FadeIn(centers), FadeIn(E_))
        mat_tex = MathTex(r"A(t)=\begin{pmatrix}10 & t & -0.5t\\ 0.4t & 4 & 0.8t\\ 0.6t & 0.2t & -2\end{pmatrix}", font_size=30).to_corner(UR, buff=0.4).shift(DOWN * 0.7)
        tl = MathTex("t=", font_size=32).next_to(mat_tex, DOWN, buff=0.3).shift(LEFT * 0.4)
        tv = DecimalNumber(0, num_decimal_places=2, font_size=32).next_to(tl, RIGHT, buff=0.1)
        tv.add_updater(lambda m: m.set_value(t.get_value()))
        self.play(FadeIn(mat_tex), FadeIn(tl), FadeIn(tv))
        self.caption("非对角元为零时，特征值（黄点）就是对角元 10、4、−2", "With zero off-diagonal entries the eigenvalues (yellow) are the diagonal entries 10, 4, −2", wait=1.0)
        self.add(D_)
        self.play(t.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        self.caption("非对角元把特征值推离对角元，但推不出圆盘：半径 = 同一行非对角元绝对值之和",
                     "Off-diagonal entries push eigenvalues away from the diagonal, but never out of the discs: radius = sum of |off-diagonal| in the row", wait=1.6)
        self.caption("三个圆盘互不相交，各含一个特征值：不解三次方程就知道三个特征值都是实数，两正一负",
                     "The three discs are disjoint and each holds one eigenvalue: all real, two positive and one negative, without solving a cubic", wait=1.6)
        self.play(t.animate.set_value(3.0), run_time=3.0, rate_func=linear)
        self.caption("非对角元再大，前两个圆盘相交：只能断定它们的并集里有两个特征值",
                     "With larger off-diagonal entries the first two discs overlap: we only know their union holds two eigenvalues", wait=1.6)
        self.play(t.animate.set_value(1.0), run_time=2.0)
        dl = MathTex(r"D^{-1}AD,\ D=\mathrm{diag}(1,1,\delta)", font_size=30).next_to(tl, DOWN, buff=0.35).align_to(mat_tex, LEFT)
        dvl = MathTex(r"\delta=", font_size=30).next_to(dl, DOWN, buff=0.25).align_to(tl, LEFT)
        dv = DecimalNumber(1, num_decimal_places=2, font_size=30).next_to(dvl, RIGHT, buff=0.1)
        dv.add_updater(lambda m: m.set_value(dsc.get_value()))
        self.play(FadeIn(dl), FadeIn(dvl), FadeIn(dv))
        self.play(dsc.animate.set_value(0.25), run_time=3.0)
        self.caption("对角相似变换不改变特征值：δ 变小，前两个圆盘收紧，第三个变大——选 D 是一种权衡",
                     "A diagonal similarity keeps the eigenvalues: smaller δ tightens the first two discs and enlarges the third, a trade-off", wait=1.6)
        self.card([["格什戈林圆盘定理", "Gershgorin circle theorem"],
                   ["每个特征值都在某个圆盘 |z − aᵢᵢ| ≤ Σⱼ≠ᵢ |aᵢⱼ| 中", "Every eigenvalue lies in some disc |z − aᵢᵢ| ≤ Σⱼ≠ᵢ |aᵢⱼ|"],
                   ["孤立的 k 个圆盘恰含 k 个特征值；严格对角占优 ⇒ 可逆", "k isolated discs hold exactly k eigenvalues; strict diagonal dominance ⇒ invertible"]])
