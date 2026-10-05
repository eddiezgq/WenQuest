"""动画 13.6.1（配图 13.6.1）：由加速度到速度、由速度到位置——AGV 的加速度（加速、匀速、减速）逐段积分：
加速度曲线下的面积是速度的改变量，速度曲线下的面积是位置的改变量；上方的小车按算出的位置行驶。"""
from manim import *
from wq_anim import *
import numpy as np

A, V, D = 0.5, 1.2, 10.0
TA = V / A
TT = 2 * TA + (D - V * TA) / V
acc = lambda t: A if t < TA else (0.0 if t < TT - TA else -A)
TS = np.linspace(0, TT, 20001)
AV = np.array([acc(t) for t in TS])
VV = np.concatenate([[0], np.cumsum((AV[1:] + AV[:-1]) / 2 * np.diff(TS))])
XX = np.concatenate([[0], np.cumsum((VV[1:] + VV[:-1]) / 2 * np.diff(TS))])
vel = lambda t: float(np.interp(t, TS, VV))
pos = lambda t: float(np.interp(t, TS, XX))


class Lesson(Base):
    def construct(self):
        self.title("13.6", "由加速度到速度、由速度到位置", "From acceleration to velocity to position")
        kw = dict(x_range=[0, 11, 2], x_length=7.5, tips=False, axis_config={"color": GREY_B})
        aa = Axes(y_range=[-0.6, 0.6, 0.5], y_length=1.1, **kw).shift(UP * 0.85 + LEFT * 0.6)
        av = Axes(y_range=[0, 1.4, 0.5], y_length=1.1, **kw).shift(DOWN * 0.6 + LEFT * 0.6)
        ax = Axes(y_range=[0, 11, 5], y_length=1.1, **kw).shift(DOWN * 2.05 + LEFT * 0.6)
        la = MathTex("a(t)", font_size=30, color=RED).next_to(aa, RIGHT, buff=0.15)
        lv = MathTex(r"v=\int a\,dt", font_size=30, color=ORANGE).next_to(av, RIGHT, buff=0.15)
        lx = MathTex(r"x=\int v\,dt", font_size=30, color=STEEL).next_to(ax, RIGHT, buff=0.15)
        ga = aa.plot(acc, x_range=[0, TT], color=RED, stroke_width=3, discontinuities=[TA, TT - TA], use_smoothing=False)
        track = Line(LEFT * 4.4, RIGHT * 3.4, color=GREY_B).shift(UP * 2.1)
        self.play(Create(aa), Create(av), Create(ax), Write(la), Write(lv), Write(lx), Create(ga), Create(track))
        t = ValueTracker(0.01)
        car = always_redraw(lambda: agv(width=0.9, height=0.3).move_to(track.point_from_proportion(min(max(pos(t.get_value()) / D, 0.0), 1.0)) + UP * 0.25))
        sa = always_redraw(lambda: aa.get_area(ga, x_range=[0, t.get_value()], color=RED, opacity=0.35))
        gv = always_redraw(lambda: av.plot(vel, x_range=[0, max(t.get_value(), 0.02)], color=ORANGE, stroke_width=3))
        gx = always_redraw(lambda: ax.plot(pos, x_range=[0, max(t.get_value(), 0.02)], color=STEEL, stroke_width=3))
        sweep = always_redraw(lambda: Line(aa.c2p(t.get_value(), 0.6), ax.c2p(t.get_value(), 0), color=GREY_B, stroke_width=1.5))
        self.add(sa, gv, gx, car, sweep)
        self.caption("加速段：加速度曲线下的面积越积越多，速度线性增大", "Accelerating: the area under a(t) grows, speed rises linearly", wait=0.2)
        self.play(t.animate.set_value(TA), run_time=3, rate_func=linear)
        self.caption("匀速段：加速度为零，面积不再增加，速度不变，位置匀速增长", "Cruising: zero acceleration, constant speed, position grows steadily", wait=0.2)
        self.play(t.animate.set_value(TT - TA), run_time=4, rate_func=linear)
        self.caption("减速段：负的面积把速度减回零，小车恰好停在 10 m 处", "Braking: negative area brings the speed back to zero at 10 m", wait=0.2)
        self.play(t.animate.set_value(TT), run_time=3, rate_func=linear)
        self.wait(0.6)
        self.play(*[FadeOut(m) for m in (aa, av, ax, la, lv, lx, ga, track, sa, gv, gx, car, sweep)])
        self.card([["积分的运动学意义", "Kinematics by integration"],
                   MathTex(r"v(t)=v_0+\int_0^t a\,d\tau,\qquad x(t)=x_0+\int_0^t v\,d\tau", font_size=40),
                   ["测量误差也一样被积分：加速度的零偏 b 使位置误差按 bt²/2 增长", "Errors integrate too: a bias b grows into a position error bt²/2"]])
