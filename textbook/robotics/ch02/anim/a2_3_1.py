"""动画 2.3.1（配图 2.3.1）：向量 x 沿单位圆转一圈，它的像 Ax 随之转动；Ax 与 x 在同一直线上的时刻，x 是特征向量。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.3", "特征向量：只伸缩、不转向", "Eigenvectors: stretched, not turned")
        K = np.array([[1.6, 0.65], [0.65, 0.9]])            # 实测刚度矩阵，以 1000 N/m 为单位
        w, V = np.linalg.eigh(K)
        U = 1.45
        O = np.array([-1.6, -0.5, 0])
        a = ValueTracker(0.0)

        def P(v):
            return O + U * np.array([v[0], v[1], 0])

        circle = Circle(radius=U, color=GREY_B, stroke_width=2).move_to(O)
        ell = ParametricFunction(lambda t: P(K @ np.array([math.cos(t), math.sin(t)])), t_range=[0, 2 * PI], color=YELLOW_E, stroke_width=2)
        self.play(Create(circle), run_time=0.8)

        def vecs():
            t = a.get_value()
            x = np.array([math.cos(t), math.sin(t)])
            y = K @ x
            ang = math.degrees(math.acos(max(-1.0, min(1.0, float(x @ y) / np.linalg.norm(y)))))
            on = ang < 1.0
            g = VGroup(Arrow(P([0, 0]), P(x), buff=0, color=WHITE, stroke_width=5, max_tip_length_to_length_ratio=0.15),
                       Arrow(P([0, 0]), P(y), buff=0, color=RED if on else ORANGE, stroke_width=7, max_tip_length_to_length_ratio=0.12))
            g.add(MathTex("x", font_size=34).move_to(P(1.18 * x)), MathTex("Ax", color=RED if on else ORANGE, font_size=34).move_to(P(y + 0.22 * y / np.linalg.norm(y))))
            return g

        def panel():
            t = a.get_value()
            x = np.array([math.cos(t), math.sin(t)])
            y = K @ x
            ang = math.degrees(math.acos(max(-1.0, min(1.0, float(x @ y) / np.linalg.norm(y)))))
            return VGroup(MathTex(r"\angle(x, Ax) = %.1f^\circ" % ang, font_size=36),
                          MathTex(r"\|Ax\| / \|x\| = %.2f" % np.linalg.norm(y), font_size=36)).arrange(DOWN, buff=0.3).move_to(np.array([4.3, 0.8, 0]))

        v = always_redraw(vecs)
        p = always_redraw(panel)
        self.add(v, p)
        self.caption("x 沿单位圆转动：Ax 一般与 x 不在同一方向上", "x goes round the unit circle; Ax usually points elsewhere", wait=0)
        self.play(Create(ell), a.animate.set_value(PI / 2), run_time=3, rate_func=linear)
        e1 = math.atan2(V[1, 1], V[0, 1]) % PI
        e2 = (e1 + PI / 2) % PI
        targets = sorted([e1, e2])
        self.play(a.animate.set_value(targets[1] if targets[1] > PI / 2 else targets[1] + PI), run_time=1.5)
        self.caption("Ax 与 x 共线：x 是特征向量，长度之比是特征值 λ", "Ax lines up with x: x is an eigenvector, the length ratio is λ", wait=1.5)
        self.play(a.animate.set_value(PI + targets[0]), run_time=3, rate_func=linear)
        self.caption("另一个特征方向与它垂直：对称矩阵的特征向量互相正交", "The other eigen-direction is perpendicular: K is symmetric", wait=1.5)
        lines = VGroup(*[DashedLine(P(-1.9 * V[:, i]), P(1.9 * V[:, i]), color=RED, stroke_width=2) for i in range(2)])
        labs = VGroup(MathTex(r"\lambda_1 = %.2f" % w[1], color=RED, font_size=30).move_to(P(2.15 * V[:, 1] * np.sign(V[1, 1]))),
                      MathTex(r"\lambda_2 = %.2f" % w[0], color=RED, font_size=30).move_to(P(1.6 * V[:, 0] * np.sign(V[1, 0]) + np.array([-0.3, 0.1]))))
        self.play(Create(lines), FadeIn(labs), run_time=1.2)
        self.play(a.animate.set_value(2 * PI + targets[1]), run_time=2.5, rate_func=linear)
        self.wait(0.8)
        self.card([["特征值与特征向量", "Eigenvalues and eigenvectors"],
                   MathTex(r"A v = \lambda v", font_size=48),
                   ["沿特征方向，变换只伸缩 λ 倍、不转向", "along an eigen-direction the map only stretches by λ"]])
