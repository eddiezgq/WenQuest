"""动画 3.3.1（配图 3.3.1）：矩形面积和逼近曲线下的面积。AGV 起步的速度 v = 1 − e^(−t/1.2)（算例 3.3.1），
前 5 s 的路程是 v–t 曲线下的面积。用左矩形和，Δt = 1、0.5、0.25、0.1 s，矩形一次比一次窄，面积之和逼近精确值。"""
from manim import *
from wq_anim import *
import numpy as np

TAU = 1.2
v_of = lambda t: 1 - np.exp(-t / TAU)
EXACT = 5 - TAU * (1 - np.exp(-5 / TAU))


class Lesson(Base):
    def construct(self):
        self.title("3.3", "矩形面积和逼近曲线下的面积", "Rectangles approaching the area under a curve")
        ax = Axes(x_range=[0, 5.2, 1], y_range=[0, 1.2, 0.5], x_length=7.0, y_length=3.7, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 24}).shift(LEFT * 1.8 + UP * 0.35)
        xl = MathTex(r"t/\mathrm s", font_size=28).next_to(ax.x_axis, RIGHT, buff=0.2)
        yl = ax.get_y_axis_label(MathTex(r"v/(\mathrm{m/s})", font_size=28), edge=UP, direction=LEFT)
        curve = ax.plot(v_of, x_range=[0, 5], color=WHITE, stroke_width=4)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), Create(curve))
        self.caption("AGV 起步：速度 v = 1 − e^(−t/1.2) m/s，前 5 s 走了多远？", "An AGV starts: v = 1 − e^(−t/1.2) m/s. How far in the first 5 s?", wait=1.0)
        area = ax.get_area(curve, x_range=[0, 5], color=YELLOW, opacity=0.25)
        self.play(FadeIn(area))
        self.caption("路程就是曲线下的面积", "The distance is the area under the curve", wait=1.0)
        self.play(FadeOut(area))

        def rects(dt):
            return ax.get_riemann_rectangles(curve, x_range=[0, 5], dx=dt, input_sample_type="left", stroke_width=1,
                                             stroke_color=BLUE_E, fill_opacity=0.55, color=[BLUE, BLUE_D])

        def total(dt):
            ts = np.arange(0, 5 - 1e-9, dt); return float(np.sum(v_of(ts)) * dt)
        dts = [1.0, 0.5, 0.25, 0.1]
        R = rects(dts[0])
        info = VGroup(MathTex(r"\Delta t = 1\ \mathrm s", font_size=32),
                      MathTex(r"\sum v_i\,\Delta t = %.3f\ \mathrm m" % total(dts[0]), font_size=32)).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT, buff=0.4).shift(UP * 0.9)
        self.play(Create(R), FadeIn(info))
        self.caption("每段把速度当作段起点的值：一个矩形的面积 = v Δt", "In each interval take the speed at its start: each rectangle is v Δt", wait=1.0)
        for dt in dts[1:]:
            R2 = rects(dt)
            info2 = VGroup(MathTex(r"\Delta t = %g\ \mathrm s" % dt, font_size=32),
                           MathTex(r"\sum v_i\,\Delta t = %.3f\ \mathrm m" % total(dt), font_size=32)).arrange(DOWN, aligned_edge=LEFT).move_to(info, aligned_edge=LEFT)
            self.play(Transform(R, R2), Transform(info, info2), run_time=1.6)
            self.wait(0.8)
        ex = MathTex(r"\int_0^5 v\,\mathrm dt = %.3f\ \mathrm m" % EXACT, font_size=34, color=YELLOW).next_to(info, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(Write(ex))
        self.caption("矩形越窄，面积之和越接近曲线下的面积：极限就是定积分", "The narrower the rectangles, the closer the sum: its limit is the definite integral", wait=2.0)
        self.card([["矩形面积和逼近曲线下的面积", "Rectangles approaching the area"],
                   ["左矩形和：Σ v(t_i) Δt；速度增大时偏小", "Left sum Σ v(t_i) Δt; low while v increases"],
                   ["Δt → 0 的极限是定积分 ∫ v dt，即路程", "Its limit as Δt → 0 is the integral ∫ v dt, the distance"]])
