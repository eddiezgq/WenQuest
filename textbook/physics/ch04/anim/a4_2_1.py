"""动画 4.2.1（配图 4.2.1）：x–t 图的斜率就是速度。AGV 在通道上往返一趟（算例 4.1.1：2 m → 14 m，停 4 s，退回 8 m），
上方是通道上的 AGV，左下画出 x–t 图并在当前时刻作切线，右下同步画出 v–t 图；切线的斜率就是 v–t 图上当时的高度。"""
from manim import *
from wq_anim import *
import numpy as np

VM, AM = 1.0, 0.5


def seg(L):
    ta = VM / AM; tc = (L - AM * ta * ta) / VM; return ta, tc, 2 * ta + tc


def xv(t):
    """往返一趟的位置和速度。"""
    pieces = [(0.0, 2.0, 12.0, 1), (None, 14.0, 4.0, 0), (None, 14.0, 6.0, -1)]
    t0 = 0.0
    for start, x0, L, sgn in pieces:
        if sgn == 0:
            if t <= t0 + L:
                return x0, 0.0
            t0 += L; continue
        ta, tc, T = seg(L)
        if t <= t0 + T:
            u = t - t0
            if u < ta:
                d, v = 0.5 * AM * u * u, AM * u
            elif u < ta + tc:
                d, v = 0.5 * AM * ta * ta + VM * (u - ta), VM
            else:
                w = u - ta - tc; d, v = 0.5 * AM * ta * ta + VM * tc + VM * w - 0.5 * AM * w * w, VM - AM * w
            return x0 + sgn * d, sgn * v
        t0 += T
    return 8.0, 0.0


TT = 26.0


class Lesson(Base):
    def construct(self):
        self.title("4.2", "x–t 图的斜率就是速度", "The slope of the x–t graph is the velocity")
        track = Line([-6, 1.9, 0], [6, 1.9, 0], color=GREY_B, stroke_width=3)
        X = lambda x: -6 + x * 12 / 16
        ticks = VGroup(*[VGroup(Line([X(x), 1.8, 0], [X(x), 2.0, 0], color=GREY_B), Text(str(x), font_size=16, color=GREY_B).move_to([X(x), 1.6, 0]))
                         for x in (0, 2, 8, 14, 16)])
        ax1 = Axes(x_range=[0, 27, 5], y_range=[0, 16, 4], x_length=5.4, y_length=2.6, tips=False,
                   axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).move_to([-3.3, -0.8, 0])
        ax2 = Axes(x_range=[0, 27, 5], y_range=[-1.2, 1.2, 1], x_length=5.4, y_length=2.6, tips=False,
                   axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).move_to([3.3, -0.8, 0])
        l1 = VGroup(MathTex(r"x/\mathrm m", font_size=26).next_to(ax1.y_axis, UP, buff=0.1), MathTex(r"t/\mathrm s", font_size=26).next_to(ax1.x_axis, RIGHT, buff=0.15))
        l2 = VGroup(MathTex(r"v/(\mathrm{m/s})", font_size=26).next_to(ax2.y_axis, UP, buff=0.1), MathTex(r"t/\mathrm s", font_size=26).next_to(ax2.x_axis, RIGHT, buff=0.15))
        self.play(Create(track), FadeIn(ticks), Create(ax1), Create(ax2), FadeIn(l1), FadeIn(l2))
        tr = ValueTracker(0.0)
        car = always_redraw(lambda: agv(width=1.3, height=0.32).move_to([X(xv(tr.get_value())[0]), 2.1, 0]))
        curve1 = always_redraw(lambda: ax1.plot(lambda t: xv(t)[0], x_range=[0, max(0.05, tr.get_value()), 0.05], color=WHITE, stroke_width=3))
        curve2 = always_redraw(lambda: ax2.plot(lambda t: xv(t)[1], x_range=[0, max(0.05, tr.get_value()), 0.05], color=BLUE, stroke_width=3))

        def tangent():
            t = tr.get_value(); x, v = xv(t)
            a, b = max(0, t - 3), min(TT, t + 3)
            return Line(ax1.c2p(a, x + v * (a - t)), ax1.c2p(b, x + v * (b - t)), color=ORANGE, stroke_width=3)
        tan = always_redraw(tangent)
        dot1 = always_redraw(lambda: Dot(ax1.c2p(tr.get_value(), xv(tr.get_value())[0]), color=ORANGE, radius=0.07))
        dot2 = always_redraw(lambda: Dot(ax2.c2p(tr.get_value(), xv(tr.get_value())[1]), color=ORANGE, radius=0.07))
        read = always_redraw(lambda: MathTex(r"v = %.2f\ \mathrm{m/s}" % xv(tr.get_value())[1], font_size=30, color=ORANGE).move_to([3.3, 1.05, 0]))
        self.add(car, curve1, curve2, tan, dot1, dot2, read)
        self.caption("AGV 一边走，一边画出 x–t 图和 v–t 图", "As the AGV moves it draws its x–t and v–t graphs", wait=0)
        self.play(tr.animate.set_value(6.0), run_time=3, rate_func=linear)
        self.caption("橙线是 x–t 图的切线：它的斜率就是此刻的速度", "The orange line is the tangent to x–t: its slope is the velocity now", wait=0)
        self.play(tr.animate.set_value(14.0), run_time=4, rate_func=linear)
        self.caption("停在货架前：x–t 图水平，速度为零", "Stopped at the shelf: x–t is flat, the velocity is zero", wait=0)
        self.play(tr.animate.set_value(18.0), run_time=2, rate_func=linear)
        self.caption("倒车：x 在减小，切线向下倾斜，速度为负", "Reversing: x decreases, the tangent slopes down, the velocity is negative", wait=0)
        self.play(tr.animate.set_value(TT), run_time=4, rate_func=linear)
        self.wait(1.0)
        self.card([["x–t 图的斜率就是速度", "The slope of x–t is the velocity"],
                   ["斜率为正向 +x 走，为负倒车，为零静止", "Positive slope: moving +x; negative: reversing; zero: at rest"],
                   ["v–t 图下的面积就是位移", "The area under v–t is the displacement"]])
