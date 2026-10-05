"""动画 16.2.1（配图 16.2.1）：ZYX 欧拉角的速率与角速度，ω_s = B(η) η̇。
B 的三列是三根“转轴”：ẑ（α̇）、R_z(α) ŷ（β̇）、R_z(α) R_y(β) x̂（γ̇）。俯仰角 β 从 0 增大到 90°，
第三根轴从水平转到竖直向下，与第一根轴共线，det B = −cos β → 0。角速度取水平的 ω = (cos α, sin α, 0) rad/s 时，
所需的欧拉角速率为 α̇ = tan β、γ̇ = 1/cos β（式 (16.2.7)），在 β → 90° 时趋于无穷。"""
from manim import *
from wq_anim import *
import numpy as np
import math

ORG = np.array([-2.8, -0.35, 0.0])
SC = 1.9
ALPHA = math.radians(35)


def rz(a):
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1.0]])


def ry(b):
    return np.array([[math.cos(b), 0, math.sin(b)], [0, 1.0, 0], [-math.sin(b), 0, math.cos(b)]])


def P(v):
    """斜投影：x 向左下，y 向右，z 向上（与 wq_anim.proj3 相同）。"""
    return proj3(v, ORG, SC)


class Lesson(Base):
    def construct(self):
        self.title("16.2", "欧拉角速率不是角速度", "Euler-angle rates are not the angular velocity")
        beta = ValueTracker(math.radians(10))
        ring = VGroup(*[Line(P([math.cos(t), math.sin(t), 0]), P([math.cos(t + 0.1), math.sin(t + 0.1), 0]), color=GREY_D, stroke_width=2)
                        for t in np.arange(0, 2 * math.pi, 0.1)])
        self.play(Create(ring), run_time=0.8)

        def axes_now():
            b = beta.get_value()
            v1 = np.array([0, 0, 1.0])
            v2 = rz(ALPHA) @ np.array([0, 1.0, 0])
            v3 = rz(ALPHA) @ ry(b) @ np.array([1.0, 0, 0])
            g = VGroup()
            for v, c in ((v1, BLUE), (v2, GREEN), (v3, RED)):
                g.add(Arrow(P([0, 0, 0]), P(v), buff=0, color=c, stroke_width=7, max_tip_length_to_length_ratio=0.12))
            g.add(MathTex(r"\hat z\ (\dot\alpha)", color=BLUE, font_size=34).next_to(P(v1), UP, buff=0.12))
            g.add(MathTex(r"R_z\hat y\ (\dot\beta)", color=GREEN, font_size=34).next_to(P(v2), RIGHT, buff=0.12))
            g.add(MathTex(r"R_zR_y\hat x\ (\dot\gamma)", color=RED, font_size=34).next_to(P(v3), RIGHT, buff=0.15))
            return g

        ax = always_redraw(axes_now)
        self.play(FadeIn(ax), run_time=0.8)
        eq = MathTex(r"\omega_s = \hat z\,\dot\alpha + R_z(\alpha)\hat y\,\dot\beta + R_z(\alpha)R_y(\beta)\hat x\,\dot\gamma = B(\eta)\,\dot\eta",
                     font_size=32).to_edge(UP, buff=1.25).shift(RIGHT * 0.6)
        self.play(Write(eq), run_time=1.2)
        self.caption("三根轴就是 B 的三列：欧拉角各自变化时，物体绕哪根轴转",
                     "The three axes are the columns of B: the axis each Euler-angle rate turns the body about", wait=1.2)

        def panel():
            b = beta.get_value()
            cb = math.cos(b)
            rows = VGroup(
                MathTex(r"\beta = %.1f^\circ" % math.degrees(b), font_size=34),
                MathTex(r"\det B = -\cos\beta = %.3f" % (-cb), font_size=34),
                MathTex(r"\omega = 1\ \mathrm{rad/s}\ \text{(horizontal)}", font_size=28, color=GREY_B),
                MathTex(r"\dot\alpha = \tan\beta = %.1f" % math.tan(b), font_size=34, color=BLUE),
                MathTex(r"\dot\gamma = 1/\cos\beta = %.1f" % (1 / cb), font_size=34, color=RED),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            return rows.to_edge(RIGHT, buff=0.7).shift(DOWN * 0.4)

        pn = always_redraw(panel)
        self.play(FadeIn(pn), run_time=0.6)
        self.caption("俯仰角 β 增大：第三根轴向下转，三根轴越来越“扁”",
                     "As the pitch β grows, the third axis tips down and the three axes flatten", wait=0.2)
        self.play(beta.animate.set_value(math.radians(80)), run_time=4.0, rate_func=smooth)
        self.caption("同样的水平角速度，需要的欧拉角速率越来越大",
                     "The same horizontal angular velocity needs larger and larger Euler-angle rates", wait=0.2)
        self.play(beta.animate.set_value(math.radians(89.4)), run_time=3.0, rate_func=smooth)
        self.wait(0.6)
        self.caption("β = 90°：第一、三根轴共线，B 奇异——这是“表示”的奇异，机器人本身毫无异常",
                     "β = 90°: the first and third axes line up and B is singular: a singularity of the description, not of the robot",
                     wait=2.0)
        self.card([["解析雅可比与几何雅可比", "Analytic and geometric Jacobians"],
                   MathTex(r"J_a(\theta) = \begin{pmatrix} B(\eta)^{-1} & 0 \\ 0 & I \end{pmatrix} J_g(\theta)", font_size=40),
                   MathTex(r"\det B = -\cos\beta", font_size=40),
                   ["β → 90° 时 J_a 奇异，J_g 仍然正常", "J_a is singular as β → 90°, while J_g stays healthy"]])
