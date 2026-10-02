"""动画 33.5.1（配图 33.5.2）：轴旋转时，表面上一点的弯曲应力是对称循环；转矩产生的切应力随起停脉动。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("33.5", "弯矩不转，轴在转", "The moment stays put, the shaft turns")
        c = np.array([-4.2, 0.2, 0])
        R = 1.5
        disk = Circle(R, color=GREY_B, fill_color="#3b4b5a", fill_opacity=1).move_to(c)
        nline = DashedLine(c + LEFT * (R + 0.4), c + RIGHT * (R + 0.4), color=MUTED)
        tens = zh("受拉", 22, RED).next_to(disk, UP, buff=0.15)
        comp = zh("受压", 22, BLUE).next_to(disk, DOWN, buff=0.15)
        Mv = Arrow(c + DOWN * 2.6 + LEFT * 0.9, c + DOWN * 2.6 + RIGHT * 0.9, color=YELLOW, buff=0)
        Ml = MathTex(r"M", color=YELLOW, font_size=32).next_to(Mv, DOWN, buff=0.08)
        self.play(FadeIn(disk), Create(nline), FadeIn(tens), FadeIn(comp), GrowArrow(Mv), Write(Ml))
        self.caption("弯矩方向由齿轮力决定，不随轴转动：上面受拉、下面受压", "The bending moment is fixed by the gear force: tension on top, compression below")
        th = ValueTracker(PI / 2)
        P = always_redraw(lambda: Dot(c + R * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0]), radius=0.11, color=YELLOW))
        Pl = always_redraw(lambda: MathTex("P", color=YELLOW, font_size=30).move_to(c + (R + 0.35) * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0])))
        ax = Axes(x_range=[0, 4 * PI, PI], y_range=[-1.3, 1.3, 1], x_length=6.2, y_length=3.2, tips=False,
                  axis_config={"color": GREY_B}).move_to([2.4, 0.2, 0])
        lab = MathTex(r"\sigma_P", color=WHITE, font_size=30).next_to(ax.y_axis, UP, buff=0.1)
        tl = MathTex(r"\omega t", color=WHITE, font_size=28).next_to(ax.x_axis, RIGHT, buff=0.1)
        self.play(Create(ax), Write(lab), Write(tl), FadeIn(P), FadeIn(Pl))
        curve = always_redraw(lambda: ax.plot(lambda x: np.sin(x + PI / 2) * 1.0, x_range=[0, max(0.01, th.get_value() - PI / 2)], color=RED))
        self.add(curve)
        self.caption("点 P 随轴转一圈：拉 → 0 → 压 → 0 → 拉，应力按正弦变化", "Point P goes round: tension, zero, compression, zero — a sine wave")
        self.play(th.animate.set_value(PI / 2 + 4 * PI), run_time=6, rate_func=linear)
        self.caption("这就是对称循环：σa = M/W，σm = 0。轴每转一圈就是一次应力循环", "A fully reversed cycle: σa = M/W, σm = 0 — one cycle per revolution", wait=2)
        self.clear_stage()
        ax2 = Axes(x_range=[0, 75, 25], y_range=[0, 1.8, 0.5], x_length=9, y_length=3.0, tips=False,
                   axis_config={"color": GREY_B}).move_to([0, 0.3, 0])
        lab2 = MathTex(r"T/T_\mathrm{rated}", color=WHITE, font_size=28).next_to(ax2.y_axis, UP, buff=0.1)

        def tq(t):
            u = t % 25
            if u < 1:
                return 1.6 * u
            if u < 2:
                return 0.75 + 0.85 * np.exp(-4 * (u - 1))
            if u < 22:
                return 0.75 + 0.08 * np.sin(PI * u)
            if u < 23:
                return 0.75 * (23 - u)
            return 0.0
        self.play(Create(ax2), Write(lab2))
        g = ax2.plot(tq, x_range=[0, 75, 0.05], color=PURPLE_B)
        self.play(Create(g), run_time=4, rate_func=linear)
        self.caption("转矩不随轴转动而变，但随起动、运行、停机变化：起停一次是一次大循环", "Torque does not change with rotation, but each start–stop is one large cycle", wait=2)
        self.card([["轴上的两种应力循环", "The two stress cycles on a shaft"],
                   MathTex(r"\sigma:\ \text{fully reversed},\ \sigma_m=0\qquad \tau:\ \text{repeated},\ \tau_a=\tau_m=\tfrac{\tau}{2}", font_size=36),
                   ["弯曲应力每转一次循环，次数极多；转矩循环看起停的次数", "Bending cycles every revolution; torque cycles with every start and stop"]])
