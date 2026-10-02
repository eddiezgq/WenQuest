"""动画 9.5.1（配图 9.5.1）：一维卡尔曼滤波的预测—更新周期。
AGV 沿通道行驶，每个周期按里程计前进 1 m：预测时钟形曲线前移并变宽（方差加 σ_w²），
测量到来时与似然相乘而变窄。为看清变化，数值取得较大：σ_w = 0.35 m，σ_v = 0.4 m，初始标准差 0.6 m。"""
from manim import *
from wq_anim import *
import numpy as np
import math

SW, SV = 0.35, 0.4
ZS = [1.25, 1.85, 3.1, 4.05]          # 四次测量（m），真实位置为 1、2、3、4 m 附近


def g(x, m, s):
    return math.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


class Lesson(Base):
    def construct(self):
        self.title("9.5", "卡尔曼滤波：预测与更新", "The Kalman filter: predict and update")
        ax = Axes(x_range=[-0.8, 5.2, 1], y_range=[0, 1.6, 0.5], x_length=12, y_length=3.0,
                  axis_config={"color": GREY_B, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 1, 2, 3, 4, 5]},
                  y_axis_config={"include_ticks": False}).shift(DOWN * 0.55)
        ax.y_axis.set_opacity(0)
        xl = zh("位置 x / m", 20, MUTED).next_to(ax.x_axis, DOWN, buff=0.12).align_to(ax.x_axis, LEFT)
        self.play(Create(ax), FadeIn(xl), run_time=1.0)
        floor = ax.c2p(0, 1.6)[1] + 0.05

        mu = ValueTracker(0.0)
        sd = ValueTracker(0.6)
        car = always_redraw(lambda: agv(width=0.9, height=0.3).move_to([ax.c2p(mu.get_value(), 0)[0], floor + 0.25, 0]))
        bel = always_redraw(lambda: ax.plot(lambda x: g(x, mu.get_value(), sd.get_value()), x_range=[-0.8, 5.2, 0.01],
                                            color=BLUE, stroke_width=5))
        info = always_redraw(lambda: MathTex(r"\sqrt{P} = %.2f\ \mathrm m" % sd.get_value(), font_size=34, color=BLUE)
                             .to_corner(UR, buff=0.5).shift(DOWN * 0.75))
        self.add(car, bel, info)
        self.caption("开始时不太清楚 AGV 在哪里：曲线很宽", "At first the AGV's position is uncertain: a wide curve", wait=1.0)

        P = 0.36
        x = 0.0
        for k, z in enumerate(ZS):
            Pm = P + SW ** 2
            xm = x + 1.0
            if k == 0:
                self.caption("预测：按里程计前进 1 m，方差加上过程噪声的方差，曲线变宽", "Predict: move 1 m by odometry, add the process-noise variance, the curve widens", wait=0)
            self.play(mu.animate.set_value(xm), sd.animate.set_value(math.sqrt(Pm)), run_time=1.6 if k < 2 else 1.0)
            lik = ax.plot(lambda t: g(t, z, SV), x_range=[-0.8, 5.2, 0.01], color=ORANGE, stroke_width=4)
            zd = Dot(ax.c2p(z, 0), color=ORANGE, radius=0.08)
            if k == 0:
                self.caption("测量 z 到来：橙色为它的似然", "A measurement z arrives: its likelihood in orange", wait=0)
            self.play(Create(lik), FadeIn(zd), run_time=0.9 if k < 2 else 0.6)
            K = Pm / (Pm + SV ** 2)
            x = xm + K * (z - xm)
            P = (1 - K) * Pm
            if k == 0:
                self.caption("更新：二者相乘，均值向测量移动 K 倍，曲线变窄", "Update: multiply, the mean moves K of the way, the curve narrows", wait=0)
            kt = MathTex(r"K = %.2f" % K, font_size=34, color=ORANGE).to_corner(UR, buff=0.5).shift(DOWN * 1.4)
            self.play(mu.animate.set_value(x), sd.animate.set_value(math.sqrt(P)), FadeIn(kt), run_time=1.6 if k < 2 else 1.0)
            self.play(FadeOut(lik), FadeOut(zd), FadeOut(kt), run_time=0.4)
        self.caption("几个周期以后，变宽和变窄达到平衡：不确定度稳定下来", "After a few cycles widening and narrowing balance: the uncertainty settles", wait=1.5)
        for m in (car, bel, info):
            m.clear_updaters()
        self.card([["一维卡尔曼滤波", "One-dimensional Kalman filter"],
                   MathTex(r"\hat x_k^- = \hat x_{k-1} + u\Delta t,\quad P_k^- = P_{k-1} + \sigma_w^2", font_size=36),
                   MathTex(r"K_k = \frac{P_k^-}{P_k^- + \sigma_v^2},\quad \hat x_k = \hat x_k^- + K_k(z_k - \hat x_k^-),\quad P_k = (1-K_k)P_k^-", font_size=32)])
