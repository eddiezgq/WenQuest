"""动画 9.3.1（配图 9.3.3）：AGV 沿通道行驶，里程计的先验逐渐变宽；激光雷达测到 6.00 m 处的标志，
似然与先验相乘，得到后验 𝒩(5.246, 0.029²)（算例 9.3.3）。"""
from manim import *
from wq_anim import *
import numpy as np
import math


def g(x, m, s):
    return math.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


class Lesson(Base):
    def construct(self):
        self.title("9.3", "先验 × 似然 → 后验", "Prior × likelihood → posterior")
        ax = Axes(x_range=[3.0, 6.2, 0.5], y_range=[0, 15, 5], x_length=11.5, y_length=3.0,
                  axis_config={"color": GREY_B, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0], "decimal_number_config": {"num_decimal_places": 1}},
                  y_axis_config={"include_ticks": False}).shift(DOWN * 0.35)
        xl = zh("通道上的位置 x / m", 20, MUTED).next_to(ax.x_axis, UP, buff=0.12).align_to(ax.x_axis, LEFT).shift(RIGHT * 0.3)
        floor_y = ax.c2p(0, 14.5)[1]
        wall = VGroup(Line(ax.c2p(6.0, 0), [ax.c2p(6.0, 0)[0], floor_y + 1.4, 0], color=GREY_B, stroke_width=6),
                      Dot([ax.c2p(6.0, 0)[0] - 0.08, floor_y + 0.45, 0], radius=0.09, color=YELLOW))
        tag = zh("标志", 20, YELLOW).next_to(wall[1], RIGHT, buff=0.12)
        self.play(Create(ax), FadeIn(xl), FadeIn(wall), FadeIn(tag), run_time=1.2)

        mu = ValueTracker(3.2)
        sd = ValueTracker(0.02)
        car = always_redraw(lambda: agv(width=1.0, height=0.32).move_to([ax.c2p(mu.get_value(), 0)[0], floor_y + 0.3, 0]))
        prior = always_redraw(lambda: ax.plot(lambda x: min(g(x, mu.get_value(), sd.get_value()), 15), x_range=[3.0, 6.2, 0.004],
                                              color=GREY_B, stroke_width=4))
        self.add(car, prior)
        self.caption("AGV 按里程计行驶：先验的中心随车前进", "The AGV drives by odometry: the prior moves with it", wait=0)
        self.play(mu.animate.set_value(5.20), sd.animate.set_value(0.10), run_time=4, rate_func=smooth)
        sdl = MathTex(r"\mathcal N(5.20,\ 0.10^2)", font_size=32, color=GREY_B).move_to(ax.c2p(4.55, 5.5))
        self.play(FadeIn(sdl))
        self.caption("里程计的误差不断累积，先验越走越宽", "Odometry errors pile up: the prior widens as it goes", wait=1.0)
        prior.clear_updaters()
        car.clear_updaters()

        beam = DashedLine([ax.c2p(5.20, 0)[0] + 0.5, floor_y + 0.45, 0], wall[1].get_center(), color=RED, stroke_width=3)
        dl = MathTex(r"0.75\ \mathrm{m}", font_size=30, color=RED).next_to(beam, UP, buff=0.08)
        self.play(Create(beam), Write(dl), run_time=1.0)
        lik = ax.plot(lambda x: g(x, 5.25, 0.03), x_range=[5.0, 5.5, 0.002], color=ORANGE, stroke_width=4)
        likl = MathTex(r"p(z\mid x),\ z = 5.25", font_size=30, color=ORANGE).move_to(ax.c2p(5.66, 12.5))
        self.caption("激光雷达测到标志：似然以 z = 6.00 − 0.75 = 5.25 m 为中心", "The lidar sees the tag: the likelihood is centred at z = 5.25 m", wait=0)
        self.play(Create(lik), FadeIn(likl), run_time=1.8)
        self.wait(1.0)

        K = 0.01 / 0.0109
        m1 = 5.20 + K * 0.05
        s1 = math.sqrt((1 - K) * 0.01)
        post = ax.plot(lambda x: g(x, m1, s1), x_range=[5.0, 5.5, 0.002], color=BLUE, stroke_width=6)
        postl = MathTex(r"\mathcal N(5.246,\ 0.029^2)", font_size=32, color=BLUE).move_to(ax.c2p(4.6, 11.5))
        self.caption("二者相乘再归一化：后验比先验和测量都窄", "Multiply and normalize: the posterior is narrower than both", wait=0)
        self.play(TransformFromCopy(VGroup(prior, lik), post), FadeIn(postl), run_time=2.5)
        self.play(car.animate.move_to([ax.c2p(m1, 0)[0], floor_y + 0.3, 0]), run_time=1.0)
        self.caption("中心偏向更准的激光雷达：权重约 92%", "The centre leans to the more precise lidar: weight about 92%", wait=1.5)
        self.card([["高斯先验 × 高斯似然 = 高斯后验", "Gaussian prior × Gaussian likelihood = Gaussian posterior"],
                   MathTex(r"\mu_1=\mu_0+K(z-\mu_0),\quad K=\frac{\sigma_0^2}{\sigma_0^2+\sigma_z^2}", font_size=38),
                   MathTex(r"\frac{1}{\sigma_1^2}=\frac{1}{\sigma_0^2}+\frac{1}{\sigma_z^2}", font_size=38)])
