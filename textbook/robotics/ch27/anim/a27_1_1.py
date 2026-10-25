"""动画 27.1.1（配图 27.1.1）：接触模型。数值与算例 27.1.1、27.1.2 相同。
(1) 三种法向接触模型的力-间隙（压入量）关系：刚性接触的互补条件（一个直角，λ 不是 φ 的函数）；线性弹簧 λ = kδ；
    赫兹接触 λ = Kδ^{3/2}（Ø10 mm 钢球压钢板：19.4 N 时压入 1.47 μm）。
(2) MuJoCo 的软接触规定的是加速度：1 kg 和 100 kg 的球静止在地面上，陷进去一样深（默认参数 0.367 mm，图中放大显示）；
    穿透量 |r| = (1 − d)𝔤(d_w τ ζ)²/d²，τ 加倍，穿透量约变为 2～3 倍。"""
from manim import *
from wq_anim import *
import numpy as np
import math

N_LINE = 19.42           # 每条接触线的载荷 / N（算例 27.1.1）
D_BALL = 1.472           # 同一载荷下 Ø10 mm 钢球的压入量 / μm
PEN = 0.367              # MuJoCo 默认参数下的穿透量 / mm（算例 27.1.2）
PEN40 = 0.833            # τ = 40 ms 时 / mm


class Lesson(Base):
    def construct(self):
        self.title("27.1", "接触模型：只能压，不能拉", "Contact models: push, never pull")
        axs = []
        names = [["刚性接触：互补条件", "rigid: complementarity"], ["线性弹簧 λ = kδ", "linear spring λ = kδ"],
                 ["赫兹接触 λ = Kδ^1.5", "Hertz λ = Kδ^1.5"]]
        for i in range(3):
            ax = Axes(x_range=[-1, 3, 1], y_range=[0, 3, 1], x_length=3.4, y_length=2.6, tips=False,
                      axis_config=dict(color=GREY_B, stroke_width=2, include_ticks=False)).move_to([-4.4 + 4.4 * i, 0.3, 0])
            lab = bi(names[i], 22, YELLOW).next_to(ax, UP, buff=0.2)
            xl = zh("φ" if i == 0 else "δ", 22, MUTED).next_to(ax.x_axis.get_end(), DOWN, buff=0.1)
            yl = zh("λ", 22, MUTED).next_to(ax.y_axis.get_end(), LEFT, buff=0.1)
            axs.append(ax)
            self.play(Create(ax), FadeIn(lab), FadeIn(xl), FadeIn(yl), run_time=0.6)
        a = axs[0]
        rigid = VGroup(Line(a.c2p(0, 0), a.c2p(2.9, 0), color=BLUE, stroke_width=6),
                       Line(a.c2p(0, 0), a.c2p(0, 2.9), color=BLUE, stroke_width=6))
        self.play(Create(rigid), run_time=1.0)
        dot = Dot(a.c2p(2.0, 0), color=RED, radius=0.09)
        self.add(dot)
        self.play(dot.animate.move_to(a.c2p(0, 0)), run_time=0.8)
        self.play(dot.animate.move_to(a.c2p(0, 2.4)), run_time=0.8)
        self.caption("分开时没有力；碰上以后间隙为零，力多大由运动方程决定——力不是间隙的函数",
                     "Apart: no force. Touching: zero gap, and the force comes from the equations of motion, not from the gap", wait=2.0)
        b, c = axs[1], axs[2]
        lin = b.plot(lambda x: 0.95 * x, x_range=[0, 2.9], color=ORANGE, stroke_width=5)
        lin0 = Line(b.c2p(-1, 0), b.c2p(0, 0), color=ORANGE, stroke_width=5)
        her = c.plot(lambda x: 0.6 * max(x, 0) ** 1.5, x_range=[0, 2.9], color=GREEN, stroke_width=5)
        her0 = Line(c.c2p(-1, 0), c.c2p(0, 0), color=GREEN, stroke_width=5)
        self.play(Create(lin0), Create(lin), run_time=1.0)
        self.play(Create(her0), Create(her), run_time=1.0)
        self.caption(f"钢件真实的接触是赫兹接触：Ø10 mm 钢球压 {N_LINE:.1f} N，只压进 {D_BALL:.2f} μm——越压越硬",
                     f"Steel parts touch like Hertz: a Ø10 mm ball under {N_LINE:.1f} N sinks only {D_BALL:.2f} μm, and stiffens as it goes", wait=2.5)
        self.clear_stage()
        # (2) MuJoCo：两个球陷进地面一样深
        g = Line([-6, -1.2, 0], [6, -1.2, 0], color=GREY_B, stroke_width=4)
        hatch = VGroup(*[Line([x, -1.2, 0], [x - 0.25, -1.45, 0], color=GREY_B, stroke_width=2) for x in np.arange(-5.8, 6, 0.35)])
        self.add(g, hatch)
        balls = []
        for x, r, m, col in ((-2.5, 0.45, "1 kg", BLUE), (2.5, 1.0, "100 kg", ORANGE)):
            ball = Circle(radius=r, color=col, fill_opacity=0.55, stroke_width=3).move_to([x, 2.6, 0])
            lab = zh(m, 26, WHITE).move_to(ball)
            balls.append(VGroup(ball, lab))
        self.play(*[FadeIn(bb) for bb in balls], run_time=0.5)
        sink = 0.35                                   # 放大显示的陷入深度
        self.play(balls[0].animate.move_to([-2.5, -1.2 + 0.45 - sink, 0]), balls[1].animate.move_to([2.5, -1.2 + 1.0 - sink, 0]),
                  rate_func=rate_functions.ease_in_quad, run_time=1.0)
        for x, r in ((-2.5, 0.45), (2.5, 1.0)):
            br = Brace(Line([x + r + 0.2, -1.2, 0], [x + r + 0.2, -1.2 - sink, 0]), RIGHT, color=YELLOW)
            self.add(br, zh(f"{PEN:.3f} mm", 22, YELLOW).next_to(br, RIGHT, buff=0.1))
        self.caption("MuJoCo 的软接触规定的是加速度，不是力：1 kg 和 100 kg 的球陷进去一样深（图中放大约一千倍）",
                     "MuJoCo's soft contact prescribes an acceleration, not a force: 1 kg and 100 kg sink equally (shown ~1000× enlarged)", wait=2.5)
        f = MathTex(r"|r| = \frac{(1-d)\,\mathfrak g\,(d_w\tau\zeta)^2}{d^2}", font_size=44, color=WHITE).move_to([0, 2.4, 0])
        self.play(Write(f), run_time=1.2)
        self.caption(f"穿透量由 solref 的时间常数 τ 决定：τ 从 20 ms 加到 40 ms，{PEN:.3f} mm 变成 {PEN40:.3f} mm",
                     f"The time constant τ sets it: from 20 ms to 40 ms, {PEN:.3f} mm becomes {PEN40:.3f} mm", wait=2.5)
        self.card([["接触模型", "Contact models"],
                   MathTex(r"\varphi \ge 0,\quad \lambda \ge 0,\quad \varphi\lambda = 0", font_size=40),
                   ["钢件之间的接触极硬：微米级的变形", "Steel on steel is very stiff: micrometre deformations"],
                   ["仿真用罚函数或软接触，穿透量由参数决定，与质量无关", "Simulators use penalty or soft contact; penetration set by parameters, not mass"]])
