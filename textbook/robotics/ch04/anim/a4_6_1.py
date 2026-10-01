"""动画 4.6.1（配图 4.6.1）：转角连续增加到 720°。旋转矩阵每转一圈复原；四元数 q 转一圈变成 −q，转两圈才复原。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("4.6", "双重覆盖：转两圈四元数才复原", "Double cover: a quaternion needs two turns")
        th = ValueTracker(0.0)
        C = np.array([-4.2, -0.4, 0])
        disc = Circle(radius=1.6, color=GREY_B).move_to(C)
        arm_ = always_redraw(lambda: Arrow(C, C + 1.6 * np.array([math.cos(th.get_value()), math.sin(th.get_value()), 0]),
                                           buff=0, color=YELLOW, stroke_width=7))
        self.add(disc, arm_, zh("物体的转动", 24, INK).next_to(disc, UP, buff=0.3))
        ax = Axes(x_range=[0, 4 * math.pi, math.pi], y_range=[-1.1, 1.1, 1], x_length=7.2, y_length=3.2,
                  axis_config={"color": GREY_B, "include_tip": False}).move_to(np.array([2.4, -0.4, 0]))
        ticks = VGroup(*[MathTex(s, font_size=28).next_to(ax.c2p(k * math.pi, -1.1), DOWN, buff=0.15)
                         for k, s in ((1, r"\pi"), (2, r"2\pi"), (3, r"3\pi"), (4, r"4\pi"))])
        self.add(ax, ticks)
        r11 = ax.plot(lambda t: (1 + 2 * math.cos(t)) / 3, x_range=[0, 4 * math.pi], color=BLUE)
        q0 = ax.plot(lambda t: math.cos(t / 2), x_range=[0, 4 * math.pi], color=ORANGE)
        self.add(MathTex(r"r_{11}", color=BLUE, font_size=30).next_to(ax.c2p(0.2, 1.0), RIGHT),
                 MathTex(r"q_0=\cos\frac{\theta}{2}", color=ORANGE, font_size=30).move_to(ax.c2p(2.9 * math.pi, 1.25)))
        cursor = always_redraw(lambda: VGroup(
            Dot(ax.c2p(th.get_value(), (1 + 2 * math.cos(th.get_value())) / 3), color=BLUE),
            Dot(ax.c2p(th.get_value(), math.cos(th.get_value() / 2)), color=ORANGE),
            DashedLine(ax.c2p(th.get_value(), -1.1), ax.c2p(th.get_value(), 1.1), color=GREY_B, stroke_width=2)))
        self.play(Create(r11), Create(q0), run_time=1.5)
        self.add(cursor)
        self.caption("转第一圈：物体和旋转矩阵回到原样，q₀ 却变成 −1", "First turn: the matrix is back, but q₀ = −1", wait=0)
        self.play(th.animate.set_value(2 * math.pi), run_time=4, rate_func=linear)
        self.caption("q 与 −q 表示同一个转动", "q and −q are the same rotation", wait=1)
        self.caption("转第二圈：四元数才回到原值", "Second turn: only now the quaternion is back", wait=0)
        self.play(th.animate.set_value(4 * math.pi), run_time=4, rate_func=linear)
        self.wait(1)
        self.card([["双重覆盖", "Double cover"],
                   MathTex(r"q=\left(\cos\tfrac{\theta}{2},\ \sin\tfrac{\theta}{2}\,\hat\omega\right)", font_size=42),
                   ["每个转动恰好对应 ±q 两个单位四元数", "every rotation corresponds to exactly two unit quaternions ±q"]])
