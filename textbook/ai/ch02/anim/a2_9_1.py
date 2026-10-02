"""动画 2.9.1（配图 2.9.1）：注意力权重矩阵的形成。4 个词元各有查询和键；查询与每个键做点积、除以 √d_k，
填满分数矩阵；每一行做 softmax 变成权重（和为 1）；再加上因果掩码，上三角变为零。数值与程序 2.9.1 的算例 2.9.1 相同。"""
from manim import *
from wq_anim import *
import numpy as np
import math

Q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0]])
K = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [-1.0, 0.0]])


def softmax(z):
    z = z - z.max(-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(-1, keepdims=True)


class Lesson(Base):
    def construct(self):
        self.title("2.9", "注意力权重是怎样算出来的", "How attention weights are computed")
        S = Q @ K.T / math.sqrt(2)
        A = softmax(S)
        Ac = softmax(S + np.triu(np.full((4, 4), -np.inf), 1))
        cell = 0.95
        origin = np.array([-1.2, 1.4, 0])

        def pos(i, j):
            return origin + np.array([j * cell, -i * cell, 0])

        qlab = VGroup(*[MathTex(r"\boldsymbol q_%d" % (i + 1), font_size=30, color=BLUE).move_to(pos(i, -1)) for i in range(4)])
        klab = VGroup(*[MathTex(r"\boldsymbol k_%d" % (j + 1), font_size=30, color=GOLD).move_to(pos(-1, j)) for j in range(4)])
        squares = VGroup(*[Square(cell * 0.95, stroke_width=1.5, color=GREY_B).move_to(pos(i, j)) for i in range(4) for j in range(4)])
        self.play(FadeIn(qlab), FadeIn(klab), Create(squares), run_time=1.0)
        self.caption("每个词元有一个查询 q 和一个键 k", "Each token has a query q and a key k")
        nums = {}
        self.caption("分数：查询与键的点积，再除以 √d_k", "Scores: query · key, divided by √d_k")
        for i in range(4):
            row = []
            for j in range(4):
                t = DecimalNumber(S[i, j], num_decimal_places=2, font_size=24).move_to(pos(i, j))
                nums[(i, j)] = t
                row.append(FadeIn(t, scale=0.6))
            self.play(Indicate(qlab[i], color=BLUE), *row, run_time=0.55)
        formula = MathTex(r"s_{ij} = \frac{\boldsymbol q_i\cdot\boldsymbol k_j}{\sqrt{d_k}}", font_size=36).to_edge(RIGHT, buff=0.6).shift(UP * 1.6)
        self.play(FadeIn(formula))
        self.wait(0.8)
        self.caption("每一行做 softmax：变成和为 1 的权重", "Softmax on each row: weights that sum to 1")
        f2 = MathTex(r"a_{ij} = \frac{e^{s_{ij}}}{\sum_m e^{s_{im}}}", font_size=36).next_to(formula, DOWN, buff=0.5)
        self.play(FadeIn(f2))
        for i in range(4):
            anims = []
            for j in range(4):
                new = DecimalNumber(A[i, j], num_decimal_places=3, font_size=24).move_to(pos(i, j))
                anims.append(Transform(nums[(i, j)], new))
                anims.append(squares[4 * i + j].animate.set_fill(ORANGE, opacity=float(A[i, j])))
            self.play(*anims, run_time=0.6)
        self.wait(1.0)
        self.caption("因果掩码：语言模型不能偷看后面的词元", "Causal mask: a language model may not peek at later tokens")
        anims = []
        for i in range(4):
            for j in range(4):
                new = DecimalNumber(Ac[i, j], num_decimal_places=3, font_size=24).move_to(pos(i, j))
                anims.append(Transform(nums[(i, j)], new))
                anims.append(squares[4 * i + j].animate.set_fill(ORANGE if j <= i else GREY_E, opacity=float(Ac[i, j]) if j <= i else 0.6))
        self.play(*anims, run_time=1.2)
        self.wait(1.2)
        self.caption("输出：用权重对值向量加权平均", "Output: a weighted average of the value vectors", wait=1.5)
        self.card([["缩放点积注意力", "Scaled dot-product attention"],
                   MathTex(r"\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\!\left(\frac{QK^{\mathsf T}}{\sqrt{d_k}} + M\right)V", font_size=40)])
