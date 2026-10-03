"""动画 1.4.1（配图 1.4.1）：《九章算术》方程第一题的算板。三行竖排、自右而左，每行自上而下为上禾、中禾、下禾的秉数和实。
按方程术：中行遍乘 3、直除右行两次；左行遍乘 3、直除右行一次；左行遍乘 5、直除中行四次，左行只剩下禾 36 与实 99。
再回代：下禾 99/36 = 11/4，中禾 17/4，上禾 37/4（斗）。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("1.4", "方程术：遍乘直除", "The fangcheng rule: multiply and subtract")
        cols = {"R": [3, 2, 1, 39], "M": [2, 3, 1, 34], "L": [1, 2, 3, 26]}
        X = {"R": 2.9, "M": 1.1, "L": -0.7}
        Y = [1.5, 0.6, -0.3, -1.5]
        board = Rectangle(width=6.0, height=4.6, color=GREY_B, fill_color="#5b4426", fill_opacity=0.35).move_to([1.1, 0.0, 0])
        self.play(FadeIn(board))
        heads = VGroup(*[bi(n, 24, GREY_A).move_to([X[c], 2.75, 0]) for c, n in
                         (("R", ["右行", "right"]), ("M", ["中行", "middle"]), ("L", ["左行", "left"]))])
        rows = VGroup(*[bi(n, 22, GREY_A).move_to([-2.6, y, 0]) for n, y in
                        zip((["上禾", "top"], ["中禾", "middle"], ["下禾", "bottom"], ["实", "total"]), Y)])
        sep = DashedLine([-1.7, -0.9, 0], [3.9, -0.9, 0], color=GREY_B)
        self.play(FadeIn(heads), FadeIn(rows), Create(sep))

        def col(c, v, color=WHITE):
            return VGroup(*[MathTex(str(x), font_size=40, color=color).move_to([X[c], y, 0]) for x, y in zip(v, Y)])

        G = {c: col(c, v) for c, v in cols.items()}
        for c in ("R", "M", "L"):
            self.play(FadeIn(G[c], shift=DOWN * 0.2), run_time=0.6)
        self.caption("三个条件各占一竖行，自右向左排列：这就是增广矩阵", "Each condition fills a column, right to left: the augmented matrix")

        def step(c, v, text, color=YELLOW, wait=1.0):
            new = col(c, v, color)
            self.caption(*text, wait=0.1)
            self.play(Transform(G[c], new), run_time=1.0)
            self.wait(wait)
            self.play(G[c].animate.set_color(WHITE), run_time=0.3)

        def mark(c):
            return SurroundingRectangle(G[c], color=BLUE_C, buff=0.12)

        m = mark("R")
        self.play(Create(m))
        step("M", [6, 9, 3, 102], ("以右行上禾 3 遍乘中行", "Multiply the middle column by the right's top entry 3"))
        step("M", [3, 7, 2, 63], ("直除：中行减去右行一次", "Subtract the right column once"), wait=0.5)
        step("M", [0, 5, 1, 24], ("再减一次，中行上禾消为 0", "Once more: the middle's top entry is 0"))
        step("L", [3, 6, 9, 78], ("又乘其次：左行遍乘 3", "Then the next: multiply the left column by 3"))
        step("L", [0, 4, 8, 39], ("直除：减去右行一次，左行上禾也消为 0", "Subtract the right once: the left's top entry is 0"))
        self.play(Transform(m, mark("M")))
        step("L", [0, 20, 40, 195], ("以中行中禾 5 遍乘左行", "Multiply the left column by the middle's entry 5"))
        step("L", [0, 0, 36, 99], ("直除：减去中行四次，左行只剩下禾", "Subtract the middle four times: only the bottom remains"), color=ORANGE, wait=1.5)
        self.play(FadeOut(m))
        def frac(p, q):
            d = math.gcd(p, q)
            return p // d, q // d
        z = frac(99, 36)                                  # 11/4
        y = frac(24 * z[1] - z[0], 5 * z[1])              # (24 − z)/5 = 17/4
        x = frac(39 * 4 - 2 * 17 - 11, 3 * 4)             # (39 − 2y − z)/3 = 37/4
        res = VGroup(MathTex(r"36z = 99\ \Rightarrow\ z = \tfrac{%d}{%d}" % z, font_size=36, color=ORANGE),
                     MathTex(r"5y + z = 24\ \Rightarrow\ y = \tfrac{%d}{%d}" % y, font_size=36, color=YELLOW),
                     MathTex(r"3x + 2y + z = 39\ \Rightarrow\ x = \tfrac{%d}{%d}" % x, font_size=36, color=YELLOW))
        res.arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(RIGHT, buff=0.3).shift(DOWN * 0.2)
        self.play(VGroup(board, heads, rows, sep, *G.values()).animate.shift(LEFT * 2.9).scale(0.85))
        for r_ in res:
            self.play(Write(r_), run_time=0.9)
        self.caption("回代：先得下禾，再得中禾、上禾", "Back-substitution: the bottom first, then the middle and the top", wait=1.0)
        ans = bi(["上禾九斗四分斗之一，中禾四斗四分斗之一，下禾二斗四分斗之三", "Top 9¼, middle 4¼, bottom 2¾ dou per bundle"], 24, GREEN)
        ans.to_edge(DOWN, buff=1.0)
        self.play(FadeIn(ans))
        self.wait(1)
        self.card([["方程术 = 高斯消元法", "The fangcheng rule = Gaussian elimination"],
                   ["遍乘：一行乘以一个数；直除：一行减去另一行", "Multiply a column by a number; subtract one column from another"],
                   ["消成三角形，再回代", "Eliminate to a triangle, then back-substitute"]])
