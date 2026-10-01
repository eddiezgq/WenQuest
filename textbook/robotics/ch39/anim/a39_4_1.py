"""动画 39.4.1（配图 39.4.1）：滑动平均的窗口（20 ms，恰好一个 50 Hz 周期）沿带干扰的力信号滑过，窗口内正负半周
相互抵消，输出（蓝点）落在真实的力附近。"""
from manim import *
from wq_anim import *
import numpy as np

X0, X1 = -6.0, 6.0
Y0, KY = -2.0, 0.13          # 30 N 画成约 3.9 个单位
TMAX = 0.3


def tx(t):
    return X0 + (X1 - X0) * t / TMAX


def force(t):
    u = np.clip(t / 0.2, 0, 1)
    return 30 * u ** 2 * (3 - 2 * u)


def noisy(t):
    return force(t) + 2 * np.sin(2 * np.pi * 50 * t)


class Lesson(Base):
    def construct(self):
        self.title("39.4", "滑动平均为什么能消除工频", "Why a moving average removes mains hum")
        ts = np.linspace(0, TMAX, 1200)
        raw = VMobject(color=GREY_B, stroke_width=2).set_points_as_corners([[tx(t), Y0 + KY * noisy(t), 0] for t in ts])
        true = DashedVMobject(VMobject(color=WHITE, stroke_width=2).set_points_as_corners([[tx(t), Y0 + KY * force(t), 0] for t in ts]), num_dashes=60)
        self.play(Create(raw), run_time=2)
        self.play(Create(true))
        self.caption("灰线：读数（真实的力 + 50 Hz 干扰）；白色虚线：真实的力", "Grey: readings (true force + 50 Hz hum); dashed: the true force")
        tk = ValueTracker(0.02)
        W = 0.02

        def window():
            t1 = tk.get_value()
            r = Rectangle(width=tx(t1) - tx(t1 - W), height=4.6, color=YELLOW, fill_opacity=0.12, stroke_width=2)
            return r.move_to([(tx(t1) + tx(t1 - W)) / 2, Y0 + 1.9, 0])

        out_pts = []

        def output():
            t1 = tk.get_value()
            m = np.mean(noisy(np.linspace(t1 - W, t1, 21)[1:]))
            return Dot([tx(t1), Y0 + KY * m, 0], radius=0.07, color=BLUE)

        win = always_redraw(window)
        dot = always_redraw(output)
        path = TracedPath(lambda: dot.get_center(), stroke_color=BLUE, stroke_width=4)
        self.add(win, dot, path)
        self.caption("黄框：最近 20 个采样（20 ms，恰好一个 50 Hz 周期）；蓝点：它们的平均", "Yellow: the last 20 samples (20 ms, one 50 Hz period); blue: their mean", wait=0)
        self.play(tk.animate.set_value(TMAX), run_time=7, rate_func=linear)
        self.caption("干扰的正负半周在窗口内抵消，输出贴着真实的力，只是晚了半个窗口", "The hum cancels inside the window; the output follows the true force, half a window late")
        self.card([["滑动平均", "Moving average"],
                   MathTex(r"y_k=\frac{1}{N}\sum_{i=0}^{N-1}x_{k-i},\qquad |H(f)|=0\ \ \text{at}\ \ f=\frac{f_s}{N}", font_size=42),
                   ["窗口盖住干扰的整数个周期，干扰完全抵消；代价是延迟 (N−1)/2 个采样", "a window of whole hum periods cancels it; the price is a delay of (N−1)/2 samples"]])
