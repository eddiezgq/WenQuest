"""动画 8.5.1（配图 8.5.2）：LM 步 Δ(μ) = −(JᵀJ + μI)⁻¹Jᵀr 随阻尼系数 μ 的变化（平面 2R 臂，θ = (30°, 30°)）。
μ 大时步子短、方向接近负梯度；μ → 0 时变成高斯-牛顿步。每个 Δ(μ) 都是线性化模型在半径 ‖Δ(μ)‖ 的圆内的最小点。
高斯-牛顿步让 F 反而增大，增益比 ρ < 0，LM 法就加大 μ、缩短步长。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
PD = np.array([0.5, 0.4])
TH = np.radians([30.0, 30.0])
U = 2.6                                 # 1 rad 画成 2.6 个单位
O = np.array([-0.3, -2.0, 0])


def tip(t):
    return np.array([L1 * math.cos(t[0]) + L2 * math.cos(t[0] + t[1]), L1 * math.sin(t[0]) + L2 * math.sin(t[0] + t[1])])


def jac(t):
    s1, s12, c1, c12 = math.sin(t[0]), math.sin(t[0] + t[1]), math.cos(t[0]), math.cos(t[0] + t[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


def F(t):
    r = tip(t) - PD
    return 0.5 * float(r @ r)


def P(v):
    return O + U * np.array([v[0], v[1], 0])


class Lesson(Base):
    def construct(self):
        self.title("8.5", "LM 步：在梯度方向与高斯-牛顿步之间", "The LM step: between the gradient and the Gauss-Newton step")
        r0, J = tip(TH) - PD, jac(TH)
        A, g = J.T @ J, J.T @ r0
        step = lambda lam: -np.linalg.solve(A + lam * np.eye(2), g)
        conts = VGroup()
        for lv in (1e-3, 3e-3, 7e-3, 0.0136, 0.025):
            conts.add(ImplicitFunction(lambda x, y, lv=lv: F(TH + np.array([(x - O[0]) / U, (y - O[1]) / U])) - lv,
                                       x_range=[-3.2, 2.0], y_range=[-2.9, 2.4], color=GREY_B, stroke_width=2, min_depth=6, max_quads=3000))
        self.play(Create(conts), run_time=1.5)
        cur = Dot(P([0, 0]), color=WHITE, radius=0.08)
        cl = bi(["当前点 θ", "current point θ"], 20, WHITE).next_to(cur, DR, buff=0.08)
        self.play(FadeIn(cur), FadeIn(cl))
        self.caption("灰色：F(θ + Δ) 的等高线（以当前点为原点）", "Grey: level curves of F(θ + Δ), centred on the current point")
        dgn = step(0.0)
        gnp = Square(0.18, color=BLUE_C, fill_opacity=1).move_to(P(dgn))
        gl = bi(["高斯-牛顿步（μ = 0）", "Gauss-Newton step (μ = 0)"], 20, BLUE_C).next_to(gnp, LEFT, buff=0.12)
        gd = -g / np.linalg.norm(g)
        garr = Arrow(P([0, 0]), P(0.35 * gd), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        gal = MathTex(r"-\nabla F", color=RED, font_size=32).next_to(garr.get_end(), DOWN, buff=0.1)
        self.play(FadeIn(gnp), FadeIn(gl), GrowArrow(garr), FadeIn(gal))
        self.caption("红色：负梯度方向；蓝色方块：高斯-牛顿步", "Red: the negative gradient; blue square: the Gauss-Newton step")
        lgl = ValueTracker(math.log10(30.0))

        def moving():
            lam = 10 ** lgl.get_value()
            d = step(lam)
            rad = float(np.linalg.norm(d))
            return VGroup(Circle(radius=U * rad, color=PURPLE_B, stroke_width=2).move_to(P([0, 0])),
                          Dot(P(d), color=ORANGE, radius=0.09))

        def trail():
            lams = 10 ** np.linspace(math.log10(30.0), lgl.get_value(), 60)
            return VMobject(color=ORANGE, stroke_width=5).set_points_smoothly([P(step(l)) for l in lams])

        def panel():
            lam = 10 ** lgl.get_value()
            d = step(lam)
            pred = 0.5 * float(r0 @ r0) - 0.5 * float((r0 + J @ d) @ (r0 + J @ d))
            act = F(TH) - F(TH + d)
            return VGroup(MathTex(r"\mu = %s" % ("%.3f" % lam if lam < 10 else "%.1f" % lam), font_size=30, color=ORANGE),
                          MathTex(r"\|\Delta\| = %.3f\ \mathrm{rad}" % np.linalg.norm(d), font_size=30, color=PURPLE_B),
                          MathTex(r"\rho = \frac{F(\theta) - F(\theta + \Delta)}{L(0) - L(\Delta)} = %.2f" % (act / pred), font_size=30)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(np.array([4.4, 1.4, 0]))

        mv = always_redraw(moving)
        tr = always_redraw(trail)
        pn = always_redraw(panel)
        self.play(FadeIn(mv), FadeIn(tr), FadeIn(pn))
        self.caption("μ 大：步子短，方向接近负梯度；紫圈是信赖域", "Large μ: a short step close to the negative gradient; the purple circle is the trust region", wait=1.2)
        self.caption("μ 减小：步子变长，逐渐转向高斯-牛顿步", "Smaller μ: the step grows and turns towards the Gauss-Newton step", wait=0)
        self.play(lgl.animate.set_value(-6.0), run_time=6, rate_func=smooth)
        self.wait(0.5)
        self.caption("高斯-牛顿步越过了谷底，F 反而增大：ρ < 0，这一步被拒绝", "The Gauss-Newton step overshoots the valley and F grows: ρ < 0, the step is rejected", wait=1.5)
        self.caption("LM 法于是加大 μ，在更小的信赖域内重新求步", "LM then raises μ and solves again inside a smaller trust region", wait=0)
        self.play(lgl.animate.set_value(math.log10(0.02)), run_time=2.5)
        self.wait(1.2)
        self.card([["列文伯格-马夸特法", "The Levenberg-Marquardt method"],
                   MathTex(r"(J^{\mathsf T}J + \mu I)\,\Delta = -J^{\mathsf T} r", font_size=46),
                   ["μ 在梯度下降与高斯-牛顿之间连续调节，由增益比 ρ 决定增减", "μ blends gradient descent and Gauss-Newton; the gain ratio ρ tells it to grow or shrink"]])
