"""动画 2.7.1（配图 2.7.1）：格拉姆-施密特法：把第一个向量缩放成单位长度；从第二个向量上剥去它沿第一个方向的影子，剩下的部分垂直；再缩放成单位长度。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.7", "格拉姆-施密特法", "The Gram–Schmidt process")
        U = 1.7
        O = np.array([-3.0, -1.8, 0])
        a1 = np.array([2.2, 0.5])
        a2 = np.array([1.1, 1.7])
        e1 = a1 / np.linalg.norm(a1)
        pr = (e1 @ a2) * e1
        w2 = a2 - pr
        e2 = w2 / np.linalg.norm(w2)

        def P(v):
            return O + U * np.array([v[0], v[1], 0])

        circ = Circle(radius=U, color=GREY_D, stroke_width=2).move_to(O)
        A1 = Arrow(P([0, 0]), P(a1), buff=0, color=GREY_B, stroke_width=6)
        A2 = Arrow(P([0, 0]), P(a2), buff=0, color=GREY_B, stroke_width=6)
        l1 = MathTex("a_1", color=GREY_B, font_size=36).next_to(P(a1), RIGHT, buff=0.1)
        l2 = MathTex("a_2", color=GREY_B, font_size=36).next_to(P(a2), UP, buff=0.1)
        self.play(Create(circ), GrowArrow(A1), GrowArrow(A2), FadeIn(l1), FadeIn(l2), run_time=1.5)
        ang = MathTex(r"\angle(a_1, a_2) = %.0f^\circ" % math.degrees(math.acos(e1 @ a2 / np.linalg.norm(a2))), font_size=34).move_to(np.array([4.0, 1.5, 0]))
        self.play(FadeIn(ang), run_time=0.5)
        self.caption("两个不垂直的向量", "Two vectors that are not perpendicular", wait=1.0)
        E1 = Arrow(P([0, 0]), P(e1), buff=0, color=RED, stroke_width=8)
        le1 = MathTex("q_1", color=RED, font_size=36).next_to(P(e1), DOWN, buff=0.15)
        self.caption("① 第一个向量缩放成单位长度：q₁ = a₁ / ‖a₁‖", "① Scale the first to unit length: q₁ = a₁ / ‖a₁‖", wait=0)
        self.play(ReplacementTransform(A1.copy(), E1), FadeIn(le1), run_time=1.8)
        self.wait(0.8)
        line = DashedLine(P(-0.3 * e1), P(2.6 * e1), color=RED_E, stroke_width=2)
        PR = Arrow(P([0, 0]), P(pr), buff=0, color=YELLOW, stroke_width=6)
        drop = DashedLine(P(a2), P(pr), color=YELLOW, stroke_width=3)
        lpr = MathTex(r"(q_1\cdot a_2)\,q_1", color=YELLOW, font_size=32).next_to(P(pr), DOWN, buff=0.35)
        self.caption("② a₂ 在 q₁ 方向上的影子：(q₁·a₂) q₁", "② The shadow of a₂ along q₁: (q₁·a₂) q₁", wait=0)
        self.play(Create(line), Create(drop), GrowArrow(PR), FadeIn(lpr), run_time=2.0)
        self.wait(0.8)
        W2 = Arrow(P(pr), P(a2), buff=0, color=GREEN, stroke_width=7)
        W2o = Arrow(P([0, 0]), P(w2), buff=0, color=GREEN, stroke_width=7)
        lw2 = MathTex("w_2", color=GREEN, font_size=36).next_to(P(w2), LEFT, buff=0.15)
        self.caption("剥去影子，剩下的 w₂ = a₂ − (q₁·a₂) q₁ 与 q₁ 垂直", "Remove the shadow: w₂ = a₂ − (q₁·a₂) q₁ is perpendicular to q₁", wait=0)
        self.play(GrowArrow(W2), run_time=1.2)
        self.play(ReplacementTransform(W2, W2o), FadeIn(lw2), run_time=1.5)
        self.wait(0.6)
        E2 = Arrow(P([0, 0]), P(e2), buff=0, color=GREEN, stroke_width=8)
        le2 = MathTex("q_2", color=GREEN, font_size=36).next_to(P(e2), LEFT, buff=0.15)
        mark = VMobject(color=WHITE, stroke_width=2).set_points_as_corners([P(0.14 * e1), P(0.14 * e1 + 0.14 * e2), P(0.14 * e2)])
        self.caption("③ w₂ 缩放成单位长度：q₁、q₂ 互相垂直，长度都是 1", "③ Scale w₂ to unit length: q₁ ⊥ q₂, both of length 1", wait=0)
        self.play(ReplacementTransform(W2o, E2), ReplacementTransform(lw2, le2), FadeOut(PR), FadeOut(lpr), FadeOut(drop), Create(mark), run_time=1.8)
        res = MathTex(r"q_1\cdot q_2 = 0,\quad \|q_1\| = \|q_2\| = 1", font_size=34).move_to(np.array([4.0, 0.6, 0]))
        self.play(FadeIn(res), run_time=0.6)
        self.wait(1.5)
        self.card([["格拉姆-施密特法", "Gram–Schmidt"],
                   MathTex(r"w_j = a_j - \sum_{i<j} (q_i\cdot a_j)\, q_i,\qquad q_j = \frac{w_j}{\|w_j\|}", font_size=40),
                   ["第一个方向完全保留，误差由后面的方向承担", "the first direction is kept; later ones absorb the error"]])
