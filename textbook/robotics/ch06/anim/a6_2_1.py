"""动画 6.2.1（配图 6.2.2）：UR5e 关节 1 以 30°/s、关节 6 以 90°/s 转动 1 s。法兰盘坐标系 {b} 随之转动；
角速度 ω 是同一支箭头，它在 {s} 中的分量 ω_s 与在 {b} 中的分量 ω_b 不同，且都随时间变化。"""
from manim import *
from wq_anim import *
import numpy as np
import math

R1, R6 = math.radians(30), math.radians(90)
W1 = np.array([0, 0, 1.0])
W6 = np.array([0, -1.0, 0])
R0 = np.diag([1.0, -1.0, -1.0])
OS = np.array([-3.2, -0.5, 0])
OB = np.array([1.6, -0.5, 0])


def rot(w, t):
    w = np.asarray(w, float)
    K = np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def Rb(t):
    return rot(W1, R1 * t) @ rot(W6, R6 * t) @ R0


def ws(t):
    return R1 * W1 + R6 * rot(W1, R1 * t) @ W6


def omega(o, t):
    w = ws(t) * 0.9
    a = Arrow(o, proj3(w, o, 1.3), buff=0, color=ORANGE, stroke_width=7, max_tip_length_to_length_ratio=0.18)
    return VGroup(a, MathTex(r"\boldsymbol\omega", color=ORANGE, font_size=34).next_to(a.get_end(), UL, buff=0.05))


def nums(v):
    return "(%.2f, %.2f, %.2f)" % tuple(0.0 if abs(x) < 5e-3 else x for x in v)


def txt(s, color=INK):
    return Text(s, font=LATIN, font_size=26, color=color)


class Lesson(Base):
    def construct(self):
        self.title("6.2", "空间角速度与物体角速度", "Spatial and body angular velocity")
        fs = frame3(OS, np.eye(3), length=1.3, labels=(r"\hat x_s", r"\hat y_s", r"\hat z_s"), scale=1.3, name=r"\{s\}")
        self.play(FadeIn(fs))
        t = ValueTracker(0.0)
        fb = always_redraw(lambda: frame3(OB, Rb(t.get_value()), length=1.3, labels=(r"\hat x_b", r"\hat y_b", r"\hat z_b"), scale=1.3, name=r"\{b\}"))
        self.play(FadeIn(fb))
        self.caption("{s} 固定在基座上；{b} 固定在法兰盘上，随关节 1、6 转动", "{s} is fixed to the base; {b} rides on the flange as joints 1 and 6 turn")
        a1 = always_redraw(lambda: omega(OS, t.get_value()))
        a2 = always_redraw(lambda: omega(OB, t.get_value()))
        self.play(FadeIn(a1), FadeIn(a2))
        rd = always_redraw(lambda: VGroup(
            txt("ω_s = " + nums(ws(t.get_value())) + " rad/s"),
            txt("ω_b = Rᵀω_s = " + nums(Rb(t.get_value()).T @ ws(t.get_value())) + " rad/s"),
            txt("t = %.2f s" % t.get_value(), MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.4).shift(DOWN * 0.9))
        self.add(rd)
        self.caption("同一支箭头 ω：在 {s} 中读出 ω_s，在 {b} 中读出 ω_b", "One arrow ω: read in {s} it is ω_s, read in {b} it is ω_b")
        self.play(t.animate.set_value(1.0), run_time=6, rate_func=linear)
        self.caption("关节 6 的轴被关节 1 带着转，ω 的方向不断变化", "Joint 6's axis is carried round by joint 1, so ω keeps changing direction")
        self.wait(1.5)
        self.card([["角速度与 so(3)", "Angular velocity and so(3)"],
                   ["同一个角速度，在两个坐标系中的分量相差一个旋转矩阵", "One angular velocity, two sets of components, related by a rotation"],
                   MathTex(r"[\omega_s] = \dot R R^{\mathsf T},\qquad [\omega_b] = R^{\mathsf T}\dot R,\qquad \omega_s = R\,\omega_b", font_size=42)])
