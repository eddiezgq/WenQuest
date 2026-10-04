"""动画 4.3.1：先剪切再旋转（RS）与先旋转再剪切（SR）。左右两个网格同时变形：左边先做剪切 S = [[1, 1], [0, 1]]，
再转 30°；右边先转 30°，再做剪切。两边各做两步，最后的网格和小旗不同，乘积矩阵 RS ≠ SR。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("4.3", "次序要紧：RS 与 SR", "Order matters: RS versus SR")
        k = 0.92
        CL, CR = np.array([-3.5, -0.3, 0.0]), np.array([3.5, -0.3, 0.0])
        a, b = ValueTracker(0.0), ValueTracker(0.0)   # a: first step, b: second step (0 → 1 each)

        def R(u):
            t = np.radians(30) * u
            return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])

        def S(u):
            return np.array([[1.0, u], [0.0, 1.0]])

        def ML():   # left: shear first, then rotate → R S
            return R(b.get_value()) @ S(a.get_value())

        def MR():   # right: rotate first, then shear → S R
            return S(b.get_value()) @ R(a.get_value())

        flag = [(0, 0), (1, 0), (1, 0.5), (0.5, 0.5), (0.5, 1), (0, 1)]

        def scene(M, C):
            P = lambda x, y: C + k * np.array([*(M @ np.array([x, y])), 0.0])
            g = VGroup()
            for j in range(-3, 4):
                i = 0.5 * j
                g.add(Line(P(i, -1.5), P(i, 1.5), color=BLUE_D if j else GREY_B, stroke_width=1.5 if j else 2.5, stroke_opacity=0.6))
                g.add(Line(P(-1.5, i), P(1.5, i), color=BLUE_D if j else GREY_B, stroke_width=1.5 if j else 2.5, stroke_opacity=0.6))
            g.add(Polygon(*[P(x, y) for x, y in flag], color=GOLD_E, fill_color=GOLD, fill_opacity=0.7, stroke_width=2))
            g.add(Arrow(P(0, 0), P(1, 0), buff=0, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.25))
            g.add(Arrow(P(0, 0), P(0, 1), buff=0, color=GREEN, stroke_width=5, max_tip_length_to_length_ratio=0.25))
            return g

        left = always_redraw(lambda: scene(ML(), CL))
        right = always_redraw(lambda: scene(MR(), CR))
        hl = bi(["左：先剪切，再旋转", "Left: shear, then rotate"], 26).move_to(CL + UP * 2.75)
        hr = bi(["右：先旋转，再剪切", "Right: rotate, then shear"], 26).move_to(CR + UP * 2.75)
        self.play(FadeIn(left), FadeIn(right), FadeIn(hl), FadeIn(hr))
        self.caption("同一面小旗，同样两步，只是次序不同", "The same flag, the same two steps, in different orders")
        self.caption("第一步：左边剪切，右边旋转 30°", "Step 1: shear on the left, rotate 30° on the right", wait=0.2)
        self.play(a.animate.set_value(1.0), run_time=3)
        self.caption("第二步：左边旋转 30°，右边剪切", "Step 2: rotate 30° on the left, shear on the right", wait=0.2)
        self.play(b.animate.set_value(1.0), run_time=3)
        mL = MathTex(r"RS=\begin{pmatrix}0.87&0.37\\0.50&1.37\end{pmatrix}", font_size=34).move_to(CL + UP * 2.45 + LEFT * 1.3)
        mR = MathTex(r"SR=\begin{pmatrix}1.37&0.37\\0.50&0.87\end{pmatrix}", font_size=34).move_to(CR + UP * 2.45 + LEFT * 1.3)
        self.play(FadeOut(hl), FadeOut(hr), FadeIn(mL), FadeIn(mR))
        self.caption("结果不同：RS ≠ SR。红、绿箭头就是乘积矩阵的两列", "Different results: RS ≠ SR. The red and green arrows are the columns of the products", wait=1.2)
        self.card([["矩阵乘法就是变换的复合，从右往左读：RS 是先 S 后 R", "A product is a composition, read right to left: RS means S first, then R"],
                   ["次序一换，结果就变：矩阵乘法一般不可交换", "Change the order and the result changes: matrix multiplication does not commute in general"]])
