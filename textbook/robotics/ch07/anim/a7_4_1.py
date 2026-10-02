"""动画 7.4.1（配图 7.4.2）：编码器读数一格一格地跳动；后向差商的跨度从 1 ms 加大到 20 ms，
估计出的角速度由剧烈跳动变得平滑，但开始滞后于真实的角速度。"""
from manim import *
from wq_anim import *
import numpy as np
import math

A, OM = 2.0, 2 * math.pi
Q = 2 * math.pi / 16384
TS = 1e-3
T = np.arange(0, 1.0, TS)
TH = A * np.sin(OM * T)
THQ = np.floor(TH / Q) * Q
W = A * OM * np.cos(OM * T)
I0, I1 = 850, 930                         # 画 0.85 s 到 0.93 s 这一段（角速度为正、逐渐增大）


def estimate(n):
    i = np.arange(I0, I1)
    return (THQ[i] - THQ[i - n]) / (n * TS)


def rms(n):
    i = np.arange(100, len(T))
    e = (THQ[i] - THQ[i - n]) / (n * TS) - W[i]
    return float(np.sqrt(np.mean(e ** 2)))


class Lesson(Base):
    def construct(self):
        self.title("7.4", "编码器测速：差商的跨度", "Speed from an encoder: the span of the difference")
        top = Axes(x_range=[0, 12, 4], y_range=[0, 16, 4], x_length=5.4, y_length=3.0,
                   axis_config={"color": GREY_B, "include_tip": False}).shift(LEFT * 3.4 + DOWN * 0.1)
        tl = VGroup(zh("角度的减少量（计数）", 18, MUTED), en("decrease of the angle (counts)", 14)).arrange(DOWN, buff=0.03).next_to(top.y_axis.get_end(), UP, buff=0.1).align_to(top, LEFT)
        xl1 = Text("t / ms", font=LATIN, font_size=16, color=MUTED).next_to(top.x_axis.get_end(), DOWN, buff=0.15)
        # 速度过零附近（t ≈ 0.25 s）读数变化最慢，台阶最清楚
        j0 = 250
        ts = np.linspace(0, 12, 300)
        true_c = top.plot_line_graph(ts, [(A - A * math.sin(OM * (0.25 + x / 1000))) / Q for x in ts], add_vertex_dots=False,
                                     line_color=WHITE, stroke_width=3)
        stairs = VMobject(color=ORANGE, stroke_width=4)
        pts = []
        for k in range(12):
            yv = (A - THQ[j0 + k] - Q) / Q + 1
            pts += [top.c2p(k, yv), top.c2p(k + 1, yv)]
        stairs.set_points_as_corners(pts)
        self.play(Create(top), FadeIn(tl), FadeIn(xl1))
        self.play(Create(true_c), Create(stairs), run_time=1.5)
        self.caption("编码器每 1 ms 读一次，读数只能是整数个计数", "Read every 1 ms; the reading is a whole number of counts")

        bot = Axes(x_range=[850, 930, 20], y_range=[6, 12.5, 1], x_length=6.0, y_length=3.6,
                   axis_config={"color": GREY_B, "include_tip": False}).shift(RIGHT * 3.3 + DOWN * 0.1)
        bl = VGroup(zh("角速度 / (rad/s)", 18, MUTED), en("speed / (rad/s)", 14)).arrange(DOWN, buff=0.03).next_to(bot.y_axis.get_end(), UP, buff=0.1).align_to(bot, LEFT)
        xl2 = Text("t / ms", font=LATIN, font_size=16, color=MUTED).next_to(bot.x_axis.get_end(), DOWN, buff=0.15)
        tw = bot.plot_line_graph(np.arange(I0, I1), W[I0:I1], add_vertex_dots=False, line_color=WHITE, stroke_width=3)
        self.play(Create(bot), FadeIn(bl), FadeIn(xl2), Create(tw))
        n = ValueTracker(1)

        def est_curve():
            k = max(1, int(round(n.get_value())))
            return bot.plot_line_graph(np.arange(I0, I1), estimate(k), add_vertex_dots=False, line_color=ORANGE, stroke_width=3)

        def label():
            k = max(1, int(round(n.get_value())))
            return Text("h = %d ms    RMS = %.3f rad/s" % (k, rms(k)), font=LATIN, font_size=22, color=ORANGE).next_to(bot.c2p(853, 12.3), RIGHT, buff=0.0)

        ec = always_redraw(est_curve)
        lb = always_redraw(label)
        self.add(ec, lb)
        self.caption("跨度 1 ms：多走一个计数，速度就跳 0.38 rad/s", "Span 1 ms: one extra count makes the speed jump by 0.38 rad/s")
        self.caption("加大跨度：量化误差变小，估计变平滑", "A longer span: less quantization error, a smoother estimate", wait=0)
        self.play(n.animate.set_value(2), run_time=1.5)
        self.wait(0.8)
        self.play(n.animate.set_value(10), run_time=2.5)
        self.caption("跨度太大：估计落后于真值，截断误差变大", "Too long a span: the estimate lags, the truncation error grows", wait=0)
        self.play(n.animate.set_value(20), run_time=2.0)
        self.wait(1.0)
        self.card([["后向差商的权衡", "The trade-off of a backward difference"],
                   MathTex(r"\dot\theta \approx \frac{\theta(t) - \theta(t-h)}{h},\qquad E(h) \approx \frac{M_2}{2}h + \frac{q}{h}", font_size=42),
                   ["跨度小则跳，跨度大则慢", "short span: jumpy; long span: late"]])
