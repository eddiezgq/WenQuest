"""动画 24.5.1（配图 24.5.1）：e^{iθ} 绕单位圆旋转，实部和虚部分别画出余弦和正弦；
再把 e^{iπ} 的级数 1 + iπ + (iπ)²/2! + … 的各项首尾相接，折线绕一圈落到 −1。"""
from manim import *
from wq_anim import *
import numpy as np
import math

R = 1.3
C = np.array([-4.2, 0.9, 0])          # 单位圆圆心
TW = 1.0                              # θ 每增加 1，曲线前进的屏幕长度


class Lesson(Base):
    def construct(self):
        self.title("24.5", "欧拉公式：e^(iθ) 绕单位圆旋转", "Euler's formula: e^(iθ) going round the circle")
        circ = Circle(radius=R, color=GREY_B, stroke_width=2).move_to(C)
        axes_h = Line(C + LEFT * 1.6, C + RIGHT * 1.6, color=GREY_D, stroke_width=1)
        axes_v = Line(C + DOWN * 1.6, C + UP * 1.6, color=GREY_D, stroke_width=1)
        x0 = C[0] + 1.9
        sin_ax = Line([x0, C[1], 0], [x0 + 2 * np.pi * TW, C[1], 0], color=GREY_D, stroke_width=1)
        cos_ax = Line([C[0], C[1] - 1.9, 0], [C[0], C[1] - 1.9 - 0.42 * 2 * np.pi * TW, 0], color=GREY_D, stroke_width=1)
        lab_s = MathTex(r"\sin\theta = \operatorname{Im} e^{i\theta}", font_size=30, color=GREEN).move_to([x0 + 4.6, C[1] + 1.75, 0])
        lab_c = MathTex(r"\cos\theta = \operatorname{Re} e^{i\theta}", font_size=30, color=BLUE).next_to(cos_ax, RIGHT, buff=0.3).shift(UP * 0.6)
        self.play(Create(circ), Create(axes_h), Create(axes_v), Create(sin_ax), Create(cos_ax))
        self.caption("复平面上的单位圆：e^(iθ) 是辐角为 θ 的点", "On the unit circle: e^(iθ) is the point at angle θ", wait=0.3)
        th = ValueTracker(0.0)
        pt = lambda: C + R * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0])
        rad = always_redraw(lambda: Line(C, pt(), color=WHITE, stroke_width=3))
        dot = always_redraw(lambda: Dot(pt(), color=RED, radius=0.08))
        lab = always_redraw(lambda: MathTex(r"e^{i\theta}", font_size=30, color=RED).next_to(dot, UR, buff=0.05))
        hline = always_redraw(lambda: DashedLine(pt(), [x0 + th.get_value() * TW, pt()[1], 0], color=GREEN, stroke_width=1.5))
        vline = always_redraw(lambda: DashedLine(pt(), [pt()[0], C[1] - 1.9 - 0.42 * th.get_value() * TW, 0], color=BLUE, stroke_width=1.5))
        sin_c = always_redraw(lambda: VMobject(color=GREEN, stroke_width=3).set_points_smoothly(
            [[x0 + t * TW, C[1] + R * np.sin(t), 0] for t in np.linspace(0, max(th.get_value(), 1e-3), 80)]))
        cos_c = always_redraw(lambda: VMobject(color=BLUE, stroke_width=3).set_points_smoothly(
            [[C[0] + R * np.cos(t), C[1] - 1.9 - 0.42 * t * TW, 0] for t in np.linspace(0, max(th.get_value(), 1e-3), 80)]))
        self.add(rad, dot, lab, hline, vline, sin_c, cos_c)
        self.play(FadeIn(lab_s), FadeIn(lab_c))
        self.caption("点绕圆转动：高度画出正弦，水平位置画出余弦", "As it turns, its height traces sine and its horizontal position cosine", wait=0)
        self.play(th.animate.set_value(2 * np.pi), run_time=8, rate_func=linear)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in (circ, axes_h, axes_v, sin_ax, cos_ax, lab_s, lab_c, rad, dot, lab, hline, vline, sin_c, cos_c)])
        # 级数 e^{iπ} 的各项首尾相接
        U = 0.78
        plane = NumberPlane(x_range=[-4.5, 2, 1], y_range=[-2.5, 3.5, 1], x_length=6.5 * U, y_length=6 * U,
                            background_line_style={"stroke_color": GREY_D, "stroke_opacity": 0.5}).move_to([0, 0.05, 0])
        to = lambda z: plane.c2p(z.real, z.imag)
        uc = Circle(radius=U * (plane.c2p(1, 0)[0] - plane.c2p(0, 0)[0]), color=GREY_B).move_to(plane.c2p(0, 0))
        self.play(Create(plane), Create(uc))
        self.caption("e^(iπ) = 1 + iπ + (iπ)²/2! + (iπ)³/3! + …：每一项转 90°、长度乘 π/n", "Each term turns 90° and is scaled by π/n", wait=0.3)
        z, term = 0j, 1 + 0j
        cols = [YELLOW, ORANGE, RED, PINK, PURPLE, BLUE, TEAL, GREEN]
        segs = []
        for n in range(14):
            a = Arrow(to(z), to(z + term), buff=0, color=cols[n % len(cols)], stroke_width=4, max_tip_length_to_length_ratio=0.15 if abs(term) > 0.3 else 0.5)
            self.play(GrowArrow(a), run_time=0.6 if n < 6 else 0.3)
            segs.append(a)
            z += term
            term *= 1j * math.pi / (n + 1)
        end = Dot(to(-1 + 0j), color=RED, radius=0.1)
        endl = MathTex(r"-1", font_size=34, color=RED).next_to(end, DOWN + LEFT, buff=0.1)
        self.play(FadeIn(end), FadeIn(endl))
        self.caption("折线绕了一大圈，最后落在 −1：e^(iπ) + 1 = 0", "The path swings round and lands on −1: e^(iπ) + 1 = 0", wait=1.5)
        self.play(*[FadeOut(m) for m in segs + [plane, uc, end, endl]])
        self.card([["欧拉公式", "Euler's formula"],
                   MathTex(r"e^{i\theta}=\sum_{n=0}^{\infty}\frac{(i\theta)^n}{n!}=\cos\theta+i\sin\theta", font_size=44),
                   ["实部的级数是 cos θ，虚部的级数是 sin θ；乘以 e^(iθ) 就是在复平面上旋转 θ",
                    "The real part is the series for cos θ, the imaginary part that for sin θ; multiplying by e^(iθ) rotates by θ"]])
