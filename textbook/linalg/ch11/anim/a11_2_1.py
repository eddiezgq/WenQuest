"""动画 11.2.1：格拉姆–施密特正交化。三个线性无关的向量 a、b、c：先把 a 单位化得 q₁；从 b 中减去它在 q₁ 上的投影，得到与 q₁ 垂直的 B，
单位化得 q₂；从 c 中减去它在 q₁、q₂ 平面上的投影，得到与平面垂直的 C，单位化得 q₃。每一步都是“减去投影，留下垂直的部分”。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("11.2", "格拉姆–施密特：减去投影，留下垂直的部分", "Gram–Schmidt: subtract projections, keep what is perpendicular")
        O = np.array([-0.4, -1.2, 0.0])
        s = 1.7
        P = lambda p: proj3(p, O, s)
        a, b, c = np.array([0.0, 1.8, 0.3]), np.array([-1.2, 0.8, 1.4]), np.array([1.6, 0.2, 0.8])
        q1 = a / np.linalg.norm(a)
        pb = (q1 @ b) * q1
        B = b - pb
        q2 = B / np.linalg.norm(B)
        pc = (q1 @ c) * q1 + (q2 @ c) * q2
        C = c - pc
        q3 = C / np.linalg.norm(C)

        def arr(u, v, col, w=5):
            return Arrow(P(u), P(v), buff=0, color=col, stroke_width=w, max_tip_length_to_length_ratio=0.12)

        def lab(tex, v, col, d=UR):
            return MathTex(tex, color=col, font_size=36).next_to(P(v), d, buff=0.08)

        A_ = arr(np.zeros(3), a, GREY_B); B_ = arr(np.zeros(3), b, GREY_B); C_ = arr(np.zeros(3), c, GREY_B)
        L = VGroup(lab(r"\boldsymbol a", a, GREY_B, RIGHT), lab(r"\boldsymbol b", b, GREY_B, RIGHT), lab(r"\boldsymbol c", c, GREY_B, UP))
        self.play(GrowArrow(A_), GrowArrow(B_), GrowArrow(C_), FadeIn(L))
        self.caption("三个线性无关、但互不垂直的向量", "Three independent vectors, not perpendicular to each other", wait=0.8)
        Q1 = arr(np.zeros(3), q1, RED, 7)
        self.play(GrowArrow(Q1), FadeIn(lab(r"\boldsymbol q_1", q1, RED, LEFT)))
        self.caption("第 1 步：把 a 单位化，q₁ = a/‖a‖", "Step 1: normalize a, q₁ = a/‖a‖", wait=0.8)
        proj_b = arr(np.zeros(3), pb, YELLOW, 4)
        drop = DashedLine(P(b), P(pb), color=YELLOW)
        self.play(GrowArrow(proj_b), Create(drop))
        self.caption("第 2 步：b 在 q₁ 方向上的投影 (q₁·b)q₁", "Step 2: the projection of b onto q₁, (q₁·b)q₁", wait=0.6)
        Bv = arr(pb, b, GREEN, 6)
        self.play(GrowArrow(Bv))
        m = 0.2
        sq = VMobject(color=WHITE, stroke_width=2).set_points_as_corners([P(pb + m * q2), P(pb + m * q2 - m * q1), P(pb - m * q1)])
        self.play(Create(sq))
        self.caption("减去投影，剩下的 B = b − (q₁·b)q₁ 与 q₁ 垂直", "Subtract it: B = b − (q₁·b)q₁ is perpendicular to q₁", wait=1.0)
        Q2 = arr(np.zeros(3), q2, GREEN, 7)
        self.play(FadeOut(proj_b), FadeOut(drop), FadeOut(sq), ReplacementTransform(Bv, Q2), FadeIn(lab(r"\boldsymbol q_2", q2, GREEN, RIGHT)))
        self.caption("把 B 单位化得到 q₂", "Normalize B to get q₂", wait=0.6)
        plane = Polygon(*[P(u * q1 + v * q2) for u, v in ((-0.6, -0.6), (2.2, -0.6), (2.2, 1.6), (-0.6, 1.6))],
                        color=GOLD, fill_color=GOLD, fill_opacity=0.18, stroke_width=1)
        self.play(FadeIn(plane))
        proj_c = arr(np.zeros(3), pc, YELLOW, 4)
        drop2 = DashedLine(P(c), P(pc), color=YELLOW)
        self.play(GrowArrow(proj_c), Create(drop2))
        self.caption("第 3 步：c 在 q₁、q₂ 平面上的投影 (q₁·c)q₁ + (q₂·c)q₂", "Step 3: the projection of c onto the q₁q₂ plane", wait=0.6)
        Cv = arr(pc, c, BLUE, 6)
        self.play(GrowArrow(Cv))
        self.caption("剩下的 C 与整个平面垂直", "What is left, C, is perpendicular to the whole plane", wait=1.0)
        Q3 = arr(np.zeros(3), q3, BLUE, 7)
        self.play(FadeOut(proj_c), FadeOut(drop2), ReplacementTransform(Cv, Q3), FadeIn(lab(r"\boldsymbol q_3", q3, BLUE, UP)))
        self.play(FadeOut(A_), FadeOut(B_), FadeOut(C_), FadeOut(L))
        self.caption("q₁、q₂、q₃：两两垂直的单位向量，与 a、b、c 张成同样的空间", "q₁, q₂, q₃: perpendicular unit vectors spanning the same space as a, b, c", wait=1.6)
        self.card([["每一步：减去在已有 q 上的投影，再单位化", "Each step: subtract projections onto the q's so far, then normalize"],
                   ["q₁, …, q_k 与 a₁, …, a_k 张成同一个子空间", "q₁, …, q_k span the same subspace as a₁, …, a_k"],
                   ["记录投影系数，就得到 A = QR", "Recording the projection coefficients gives A = QR"]])
