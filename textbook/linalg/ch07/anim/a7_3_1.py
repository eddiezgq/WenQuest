"""动画 7.3.1：三维空间中过原点的平面是子空间：平面上两个向量 u、w 之和与倍数都留在平面上。
把平面沿法向平移，离开原点：u、w 仍在平移后的平面上，u + w 却离开了它，零向量也不在上面。最后，过原点的直线同样是子空间。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("7.3", "子空间：过原点的平面", "Subspaces: planes through the origin")
        O = np.array([0.0, -0.4, 0.0])
        s = 1.15
        P = lambda p: proj3(p, O, s)
        axes = VGroup(*[Arrow(P(-a), P(a), buff=0, color=GREY_B, stroke_width=2, max_tip_length_to_length_ratio=0.05)
                        for a in (np.array([2.2, 0, 0]), np.array([0, 2.6, 0]), np.array([0, 0, 2.2]))])
        labels = VGroup(*[Text(t, font_size=24, color=GREY_B).move_to(P(v)) for t, v in (("x", [2.5, 0, 0]), ("y", [0, 2.9, 0]), ("z", [0, 0, 2.5]))])
        self.play(Create(axes), FadeIn(labels))
        b1, b2 = np.array([1.0, -1.0, 0.0]), np.array([1.0, 0.0, -1.0])   # basis of x + y + z = 0
        nrm = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)
        h = ValueTracker(0.0)

        def plane():
            c = h.get_value() * nrm
            pts = [P(c + a * b1 + b * b2) for a, b in ((-1.1, -0.7), (1.3, -0.7), (1.3, 1.3), (-1.1, 1.3))]
            return Polygon(*pts, color=GOLD, fill_color=GOLD, fill_opacity=0.25, stroke_width=1.5)

        pl = always_redraw(plane)
        ghost = DashedVMobject(Polygon(*[P(a * b1 + b * b2) for a, b in ((-1.1, -0.7), (1.3, -0.7), (1.3, 1.3), (-1.1, 1.3))], color=GREY_B, stroke_width=1.5), num_dashes=40)
        self.play(FadeIn(pl))
        self.caption("平面 x + y + z = 0 过原点", "The plane x + y + z = 0 passes through the origin")
        u0, w0 = 0.9 * b1 + 0.2 * b2, -0.3 * b1 + 0.9 * b2

        def vecs():
            c = h.get_value() * nrm
            u, w = c + u0, c + w0
            g = VGroup(Arrow(P(np.zeros(3)), P(u), buff=0, color=RED, stroke_width=5),
                       Arrow(P(np.zeros(3)), P(w), buff=0, color=GREEN, stroke_width=5),
                       Arrow(P(np.zeros(3)), P(u + w), buff=0, color=BLUE, stroke_width=5))
            g.add(MathTex(r"\boldsymbol u", color=RED, font_size=34).next_to(P(u), DOWN, buff=0.1),
                  MathTex(r"\boldsymbol w", color=GREEN, font_size=34).next_to(P(w), UP, buff=0.1),
                  MathTex(r"\boldsymbol u+\boldsymbol w", color=BLUE, font_size=34).next_to(P(u + w), RIGHT, buff=0.1))
            off = abs(float(np.dot(u + w, nrm)) - h.get_value())
            g.add(bi([f"u + w 到平面的距离 {off:.2f}", f"distance from u + w to the plane: {off:.2f}"], 26, BLUE).to_corner(UR, buff=0.5).shift(DOWN * 0.7))
            return g

        V = always_redraw(vecs)
        self.play(FadeIn(V))
        self.caption("u、w 在平面上，u + w 也在平面上（距离为 0）", "u and w lie in the plane, and so does u + w (distance 0)", wait=1.2)
        k2 = ValueTracker(1.0)
        sc = always_redraw(lambda: Arrow(P(np.zeros(3)), P(k2.get_value() * u0), buff=0, color=PURPLE_B, stroke_width=6)
                           if abs(k2.get_value()) > 0.08 else Dot(P(np.zeros(3)), color=PURPLE_B))
        self.add(sc)
        self.caption("数乘：c·u 沿 u 的方向伸缩，仍在平面上", "Scaling: c·u stretches along u and stays in the plane", wait=0.2)
        self.play(k2.animate.set_value(-1.2), run_time=2)
        self.play(k2.animate.set_value(1.0), run_time=1)
        self.play(FadeOut(sc), run_time=0.3)
        self.caption("把平面沿法向平移，离开原点", "Shift the plane along its normal, away from the origin", wait=0.2)
        self.add(ghost)
        self.play(h.animate.set_value(0.9), run_time=3)
        self.caption("u、w 仍在平移后的平面上，u + w 却离开了它：不是子空间", "u and w still lie in the shifted plane, but u + w leaves it: not a subspace", wait=1.5)
        self.caption("零向量也不在平移后的平面上", "Nor does the zero vector lie in the shifted plane", wait=1.0)
        self.play(h.animate.set_value(0.0), run_time=2)
        self.play(FadeOut(V), FadeOut(pl), FadeOut(ghost))
        d = np.array([0.6, 1.0, 0.8])
        line = Line(P(-1.8 * d), P(1.8 * d), color=PURPLE_B, stroke_width=5)
        self.play(Create(line))
        a1 = Arrow(P(np.zeros(3)), P(0.7 * d), buff=0, color=RED, stroke_width=5)
        a2 = Arrow(P(np.zeros(3)), P(-1.4 * d), buff=0, color=GREEN, stroke_width=5)
        self.play(GrowArrow(a1))
        self.caption("过原点的直线：向量的倍数和相互之和都留在直线上", "A line through the origin: multiples and sums stay on the line", wait=0.3)
        self.play(TransformFromCopy(a1, a2))
        a3 = Arrow(P(np.zeros(3)), P(-0.7 * d), buff=0, color=BLUE, stroke_width=5)
        self.play(GrowArrow(a3))
        self.caption("红 + 绿 = 蓝：和也在直线上", "red + green = blue: the sum stays on the line", wait=0.8)
        self.card([["子空间对加法和数乘封闭，一定含零向量", "A subspace is closed under addition and scaling and contains 0"],
                   ["ℝ³ 的子空间：原点、过原点的直线、过原点的平面、ℝ³ 本身", "Subspaces of ℝ³: the origin, lines and planes through it, and ℝ³"]])
