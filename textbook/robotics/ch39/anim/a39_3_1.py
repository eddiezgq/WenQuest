"""动画 39.3.1（配图 39.3.1）：采样频率 1 kHz 固定，信号频率从 50 Hz 升到 1050 Hz；采样点连成的波形（红）先变快、
过了 500 Hz 反而变慢，1000 Hz 时成为直线，1050 Hz 时又像 50 Hz。"""
from manim import *
from wq_anim import *
import numpy as np

FS = 1000.0
T = 0.02                 # 画 20 ms
X0, X1, A = -5.6, 5.6, 1.4
Y0 = 0.3


def tx(t):
    return X0 + (X1 - X0) * t / T


class Lesson(Base):
    def construct(self):
        self.title("39.3", "混叠：高频信号伪装成低频", "Aliasing: a high frequency in disguise")
        f = ValueTracker(50.0)
        axis = Line([X0, Y0, 0], [X1, Y0, 0], color=GREY_B, stroke_width=2)
        self.play(Create(axis))

        def wave():
            ff = f.get_value()
            ts = np.linspace(0, T, 1500)
            return VMobject(color=GREY_B, stroke_width=1.5).set_points_smoothly([[tx(t), Y0 + A * np.sin(2 * np.pi * ff * t), 0] for t in ts][::3])

        def samples():
            ff = f.get_value()
            n = np.arange(0, int(T * FS) + 1)
            pts = [[tx(k / FS), Y0 + A * np.sin(2 * np.pi * ff * k / FS), 0] for k in n]
            g = VGroup(*[Dot(p, radius=0.05, color=YELLOW) for p in pts])
            g.add(VMobject(color=RED, stroke_width=4).set_points_as_corners(pts))
            return g

        def label():
            ff = f.get_value()
            r = ff % FS
            fa = min(r, FS - r)
            return VGroup(MathTex(r"f = %d\ \mathrm{Hz}" % round(ff), font_size=36),
                          MathTex(r"f_a = %d\ \mathrm{Hz}" % round(fa), color=RED, font_size=36)).arrange(RIGHT, buff=0.8).to_corner(UR, buff=0.5).shift(DOWN * 0.8)

        w, s, l = always_redraw(wave), always_redraw(samples), always_redraw(label)
        self.add(w, s, l)
        self.caption("采样频率 1 kHz；黄点是采样值，红线是采样值连成的波形", "Sampling at 1 kHz: yellow dots are samples, red is what they trace")
        self.caption("信号频率升高，红线也变快——直到 500 Hz", "As the signal speeds up so does the red trace, up to 500 Hz", wait=0)
        self.play(f.animate.set_value(450), run_time=4, rate_func=linear)
        self.caption("超过 500 Hz（奈奎斯特频率），红线反而变慢", "Beyond 500 Hz (Nyquist) the red trace slows down", wait=0)
        self.play(f.animate.set_value(950), run_time=4, rate_func=linear)
        self.wait(1)
        self.caption("950 Hz 的信号，采样后看起来就是 50 Hz", "A 950 Hz signal, once sampled, looks like 50 Hz")
        self.play(f.animate.set_value(1000), run_time=1.5, rate_func=linear)
        self.caption("1000 Hz：每次都采在同一相位，变成一条直线", "At 1000 Hz every sample hits the same phase: a flat line")
        self.play(f.animate.set_value(1050), run_time=1.5, rate_func=linear)
        self.wait(1)
        self.card([["采样定理", "The sampling theorem"],
                   MathTex(r"f_s > 2 f_{max},\qquad f_a = |f - k f_s|", font_size=46),
                   ["采样之前先用模拟低通滤波器去掉高于 f_s/2 的成分", "remove everything above f_s/2 with an analogue filter before sampling"]])
