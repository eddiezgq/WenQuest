"""动画 8.1.1（配图 8.1.2）：梯度与等高线垂直；沿单位方向 u 的变化率 D_u f = ∇f·u = ‖∇f‖cos φ，
u 与 ∇f 同向时最大，反向时最小——负梯度是下降最快的方向。"""
from manim import *
from wq_anim import *
import numpy as np
import math

Q = np.array([[3.0, 1.0], [1.0, 1.5]])
U = 1.25                          # 1 个单位画成 1.25
O = np.array([-2.3, -0.3, 0])


def P(v):
    return O + U * np.array([v[0], v[1], 0])


def level_point(c, a):
    """等高线 ½xᵀQx = c 上，极角为 a 的点。"""
    d = np.array([math.cos(a), math.sin(a)])
    return d * math.sqrt(2 * c / (d @ Q @ d))


class Lesson(Base):
    def construct(self):
        self.title("8.1", "梯度垂直于等高线", "The gradient is perpendicular to the level curves")
        curves = VGroup()
        for c in (0.25, 0.75, 1.5, 2.5):
            pts = [P(level_point(c, a)) for a in np.linspace(0, 2 * math.pi, 120)]
            curves.add(VMobject(color=GREY_B, stroke_width=2).set_points_smoothly(pts))
        self.play(Create(curves), run_time=1.5)
        self.caption("f(x) = ½xᵀQx 的等高线：同一条曲线上 f 的值相同", "Level curves of f(x) = ½xᵀQx: f is constant along each curve")

        ang = ValueTracker(0.6)
        cl = 1.5

        def pt():
            return level_point(cl, ang.get_value())

        def grad_group():
            x = pt()
            g = Q @ x
            gn = g / np.linalg.norm(g)
            t = np.array([-gn[1], gn[0]])
            return VGroup(
                DashedLine(P(x - 0.9 * t), P(x + 0.9 * t), color=WHITE, stroke_width=2, dash_length=0.08),
                Arrow(P(x), P(x + 0.9 * gn), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.2),
                Dot(P(x), color=YELLOW, radius=0.07))

        gg = always_redraw(grad_group)
        lab = always_redraw(lambda: MathTex(r"\nabla f", color=RED, font_size=34).move_to(
            P(pt() + 1.15 * (Q @ pt()) / np.linalg.norm(Q @ pt()))))
        self.play(FadeIn(gg), FadeIn(lab))
        self.caption("红色箭头 ∇f 总与等高线的切线（白色虚线）垂直", "The red arrow ∇f is always perpendicular to the tangent (white dashes)", wait=0)
        self.play(ang.animate.set_value(0.6 + 2 * math.pi), run_time=5, rate_func=linear)
        self.wait(0.5)

        phi = ValueTracker(0.0)

        def u_group():
            x = pt()
            g = Q @ x
            gn = g / np.linalg.norm(g)
            a = math.atan2(gn[1], gn[0]) + phi.get_value()
            u = np.array([math.cos(a), math.sin(a)])
            return Arrow(P(x), P(x + 0.75 * u), buff=0, color=BLUE_C, stroke_width=6, max_tip_length_to_length_ratio=0.25)

        def panel():
            x = pt()
            gnorm = float(np.linalg.norm(Q @ x))
            du = gnorm * math.cos(phi.get_value())
            return VGroup(MathTex(r"\varphi = %d^\circ" % round(math.degrees(phi.get_value()) % 360), color=BLUE_C, font_size=36),
                          MathTex(r"D_u f = \|\nabla f\|\cos\varphi = %+.2f" % du, font_size=36)).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(np.array([3.6, 1.0, 0]))

        ug = always_redraw(u_group)
        pn = always_redraw(panel)
        self.play(FadeIn(ug), FadeIn(pn))
        self.caption("蓝色单位方向 u 转一圈：沿 u 的变化率等于 ∇f 在 u 上的投影", "Turn the unit direction u: the rate of change is the projection of ∇f on u", wait=0)
        self.play(phi.animate.set_value(2 * math.pi), run_time=6, rate_func=linear)
        self.caption("φ = 0 时增加最快，φ = 180° 时减小最快", "Fastest increase at φ = 0, fastest decrease at φ = 180°", wait=0)
        self.play(phi.animate.set_value(math.pi), run_time=2)
        self.wait(1.2)
        self.card([["最速下降方向", "The steepest-descent direction"],
                   MathTex(r"D_u f = \nabla f^{\mathsf T} u,\qquad u^* = -\frac{\nabla f}{\|\nabla f\|}", font_size=44),
                   ["梯度与等高线垂直，指向 f 增加最快的方向", "the gradient is normal to the level curve and points uphill"]])
