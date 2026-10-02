"""动画 8.3.2（配图 8.3.3）：单关节 2 s 内转过 2 rad、首末速度为零的最小能量轨迹。不限速时速度是抛物线（位置是三次多项式），
峰值 1.5 rad/s；把限速 v_max 从 1.5 rad/s 逐渐降低，速度曲线被“压平”，中段贴着限速匀速运行，代价 ∫a²dt 随之增大。"""
from manim import *
from wq_anim import *
import numpy as np
import math

T_, THF = 2.0, 2.0


def profile(vmax, t):
    """限速 vmax（θ_f/T ≤ vmax ≤ 1.5θ_f/T）时的最优速度：加速段 vmax(1 − (1 − t/t1)²)，匀速段 vmax，减速段对称。"""
    t1 = 3 * (vmax * T_ - THF) / (2 * vmax)
    s = min(t, T_ - t)
    return vmax * (1 - (1 - s / t1) ** 2) if s < t1 else vmax


def cost(vmax):
    t1 = 3 * (vmax * T_ - THF) / (2 * vmax)
    return 8 * vmax ** 2 / (3 * t1)


class Lesson(Base):
    def construct(self):
        self.title("8.3", "限速下的最小能量轨迹", "Minimum-energy motion under a speed limit")
        ax = Axes(x_range=[0, 2, 0.5], y_range=[0, 1.6, 0.5], x_length=7, y_length=4.2, tips=False,
                  axis_config=dict(color=GREY_B, include_numbers=True, font_size=24)).move_to(np.array([-1.6, -0.2, 0]))
        xl = MathTex(r"t\ /\ \mathrm{s}", font_size=28).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = MathTex(r"\omega\ /\ (\mathrm{rad/s})", font_size=28).next_to(ax.y_axis, UP, buff=0.15)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        free = ax.plot(lambda t: 1.5 * THF / T_ * 4 * (t / T_) * (1 - t / T_), x_range=[0, 2], color=GREY_B, stroke_width=4)
        self.play(Create(free), run_time=1.5)
        self.caption("不限速：最优速度是抛物线，峰值 1.5 rad/s，∫a²dt = 6", "No limit: the best speed is a parabola peaking at 1.5 rad/s; ∫a²dt = 6")
        vm = ValueTracker(1.5)
        lim = always_redraw(lambda: DashedLine(ax.c2p(0, vm.get_value()), ax.c2p(2, vm.get_value()), color=RED, stroke_width=3))
        cur = always_redraw(lambda: ax.plot(lambda t: profile(vm.get_value(), t), x_range=[0, 2, 0.01], color=BLUE_C, stroke_width=5))
        panel = always_redraw(lambda: VGroup(MathTex(r"v_{\max} = %.2f\ \mathrm{rad/s}" % vm.get_value(), font_size=32, color=RED),
                                             MathTex(r"\int a^2\,dt = %.2f" % cost(vm.get_value()), font_size=32, color=BLUE_C),
                                             MathTex(r"t_1 = %.2f\ \mathrm{s}" % (3 * (vm.get_value() * T_ - THF) / (2 * vm.get_value())), font_size=30))
                              .arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(np.array([4.6, 1.0, 0])))
        self.play(FadeIn(lim), FadeIn(cur), FadeIn(panel))
        self.caption("降低限速：速度曲线被压平，中段贴着限速匀速运行", "Lower the limit: the curve flattens and cruises at the limit in the middle", wait=0)
        self.play(vm.animate.set_value(1.2), run_time=3)
        self.wait(0.8)
        self.caption("v_max = 1.2 rad/s：0.5 s 到 1.5 s 约束起作用，代价 7.68，比不限速多 28%", "v_max = 1.2 rad/s: the limit is active from 0.5 s to 1.5 s; cost 7.68, 28% more", wait=1.5)
        self.play(vm.animate.set_value(1.05), run_time=2.5)
        self.caption("限速逼近平均速度 1 rad/s 时，加速段越来越短，代价急剧增大", "As the limit nears the mean speed 1 rad/s, the ramps shorten and the cost soars", wait=1.5)
        self.play(vm.animate.set_value(1.2), run_time=1.5)
        self.wait(0.5)
        self.card([["二次规划", "A quadratic program"],
                   MathTex(r"\min \int_0^T a^2\,dt\quad \text{s.t.}\ \ \theta(T) = \theta_f,\ \ \omega(T) = 0,\ \ \omega(t) \le v_{\max}", font_size=38),
                   ["约束起作用的那一段，乘子 μ 为正", "the multipliers μ are positive exactly where the limit is active"]])
