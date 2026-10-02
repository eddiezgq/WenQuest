"""动画 9.4.1（配图 9.4.1）：最大似然。钟形曲线（σ = 10 mm）的中心 μ 从 125 mm 滑到 175 mm，
5 个超声读数（148、155、151、144、157 mm）处的密度随之变化；它们的乘积 L(μ) 在下方描出曲线，在样本均值 151 mm 处最大。"""
from manim import *
from wq_anim import *
import numpy as np
import math

Z = [148.0, 155.0, 151.0, 144.0, 157.0]
SG = 10.0


def g(x, m):
    return math.exp(-0.5 * ((x - m) / SG) ** 2) / (SG * math.sqrt(2 * math.pi))


def lik(m):
    p = 1.0
    for z in Z:
        p *= g(z, m)
    return p


LMAX = lik(151.0)


class Lesson(Base):
    def construct(self):
        self.title("9.4", "最大似然：让数据最可能出现", "Maximum likelihood: make the data most probable")
        top = Axes(x_range=[115, 185, 10], y_range=[0, 0.045, 0.01], x_length=10, y_length=2.2,
                   axis_config={"color": GREY_B, "include_tip": False, "font_size": 20},
                   y_axis_config={"include_ticks": False}).shift(UP * 1.05 + LEFT * 0.6)
        bot = Axes(x_range=[115, 185, 10], y_range=[0, 1.1, 0.5], x_length=10, y_length=1.5,
                   axis_config={"color": GREY_B, "include_tip": False, "font_size": 20},
                   x_axis_config={"numbers_to_include": [120, 130, 140, 150, 160, 170, 180]},
                   y_axis_config={"include_ticks": False}).shift(DOWN * 1.45 + LEFT * 0.6)
        lt = MathTex(r"\mathcal N(z;\mu,\sigma^2)", font_size=30, color=BLUE).next_to(top, RIGHT, buff=0.1).shift(UP * 0.6)
        lb = MathTex(r"L(\mu)", font_size=32, color=YELLOW).next_to(bot, RIGHT, buff=0.1)
        dots = VGroup(*[Dot(top.c2p(z, 0), radius=0.07, color=RED) for z in Z])
        self.play(Create(top), Create(bot), FadeIn(dots), Write(lt), Write(lb), run_time=1.5)
        self.caption("5 个超声读数（红点），噪声标准差 10 mm", "Five ultrasonic readings (red), noise std 10 mm")

        mu = ValueTracker(125.0)
        curve = always_redraw(lambda: top.plot(lambda x: g(x, mu.get_value()), x_range=[115, 185, 0.25], color=BLUE, stroke_width=4))
        bars = always_redraw(lambda: VGroup(*[Line(top.c2p(z, 0), top.c2p(z, g(z, mu.get_value())), color=BLUE_B, stroke_width=6) for z in Z]))
        reached = [115.5]                  # 已经扫过的最右位置，曲线画到这里为止

        def trace_curve():
            reached[0] = max(reached[0], mu.get_value())
            return bot.plot(lambda m: lik(m) / LMAX, x_range=[115, reached[0], 0.25], color=YELLOW, stroke_width=4)

        trace = always_redraw(trace_curve)
        marker = always_redraw(lambda: Dot(bot.c2p(mu.get_value(), lik(mu.get_value()) / LMAX), radius=0.07, color=YELLOW))
        mtxt = always_redraw(lambda: MathTex(r"\mu = %.0f\ \mathrm{mm}" % mu.get_value(), font_size=32).to_corner(UR, buff=0.5).shift(DOWN * 0.7))
        self.add(curve, bars, trace, marker, mtxt)
        self.caption("候选的 μ 偏左：读数都在曲线边缘，密度都很小", "μ too far left: the readings sit in the tails, all densities small", wait=0)
        self.play(mu.animate.set_value(140), run_time=3, rate_func=linear)
        self.caption("五个密度之积 L(μ)：μ 越合适，乘积越大", "Their product L(μ) grows as μ fits better", wait=0)
        self.play(mu.animate.set_value(151), run_time=3, rate_func=linear)
        self.wait(0.8)
        self.caption("μ 再往右，乘积又变小", "Move μ further right and the product falls again", wait=0)
        self.play(mu.animate.set_value(175), run_time=3, rate_func=linear)
        self.play(mu.animate.set_value(151), run_time=2, rate_func=smooth)
        line = DashedLine(bot.c2p(151, 0), bot.c2p(151, 1.0), color=YELLOW)
        self.play(Create(line))
        self.caption("最大值正在样本均值 151 mm 处", "The maximum is at the sample mean, 151 mm", wait=1.5)
        for m in (curve, bars, trace, marker, mtxt):
            m.clear_updaters()
        self.card([["最大似然估计", "Maximum likelihood estimate"],
                   MathTex(r"\hat\mu_{\mathrm{ML}}=\arg\max_\mu \prod_i \mathcal N(z_i;\mu,\sigma^2)=\bar z", font_size=38),
                   ["高斯噪声下，最大似然 = 最小二乘", "With Gaussian noise, maximum likelihood = least squares"]])
