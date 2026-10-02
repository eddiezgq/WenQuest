"""动画 7.8.1（配图 7.8.1）：三种运动规律并排（T = 2 s，Δ = 90°）：每列上方是转动的连杆，下方逐点画出角加速度曲线；
三次多项式与梯形速度在角加速度跳跃的时刻，连杆末端出现示意性的抖动（衰减振动，夸大画出）；最后画出加加速度的冲激。"""
from manim import *
from wq_anim import *
import numpy as np
import math

T, D = 2.0, math.pi / 2


def law(name, t):
    if t <= 0:
        return 0.0, 0.0
    if t >= T:
        return D, 0.0
    s = t / T
    if name == 0:
        return D * (3 * s * s - 2 * s ** 3), 6 * D / T ** 2 * (1 - 2 * s)
    if name == 1:
        return D * (10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5), 60 * D / T ** 2 * s * (1 - s) * (1 - 2 * s)
    ta = T / 4
    wc = D / (T - ta)
    a0 = wc / ta
    if t < ta:
        return 0.5 * a0 * t * t, a0
    if t < T - ta:
        return 0.5 * a0 * ta * ta + wc * (t - ta), 0.0
    return D - 0.5 * a0 * (T - t) ** 2, -a0


JUMPS = [[0.0, T], [], [0.0, T / 4, 3 * T / 4, T]]


class Lesson(Base):
    def construct(self):
        self.title("7.8", "平顺的运动：看加速度，更要看加加速度", "Smooth motion: watch the acceleration and the jerk")
        names = [["三次多项式", "cubic"], ["五次多项式", "quintic"], ["梯形速度", "trapezoid"]]
        t = ValueTracker(-0.2)
        cols = []
        for k in range(3):
            cx = -4.4 + 4.4 * k
            hd = bi(names[k], 26, WHITE).move_to([cx, 2.3, 0])
            ax = Axes(x_range=[-0.2, 2.4, 1], y_range=[-3, 3, 1], x_length=3.6, y_length=2.2, tips=False,
                      axis_config={"color": GREY_B, "stroke_width": 1}).move_to([cx, -1.7, 0])
            lbl = zh("α", 24, GREEN).next_to(ax, LEFT, buff=0.1)
            cols.append((cx, ax))
            self.add(hd, ax, lbl)

        def arm(k, cx):
            def draw():
                tt = t.get_value()
                th, _ = law(k, tt)
                shake = 0.0
                for tj in JUMPS[k]:
                    if tt > tj:
                        shake += 0.06 * math.exp(-6 * (tt - tj)) * math.sin(40 * (tt - tj))
                base = np.array([cx - 0.9, 0.0, 0])
                a = th + shake
                tip = base + 1.6 * np.array([math.cos(a), math.sin(a), 0])
                return VGroup(Line(base + LEFT * 0.3, base + RIGHT * 0.3, color=GREY_B, stroke_width=4),
                              Line(base, tip, color=STEEL, stroke_width=10), Dot(base, color=WHITE, radius=0.08),
                              Dot(tip, color=YELLOW, radius=0.08))
            return draw

        def trace(k, ax):
            def draw():
                tt = t.get_value()
                ts = np.linspace(-0.2, max(-0.19, tt), 300)
                pts = [ax.c2p(x, law(k, x)[1]) for x in ts]
                return VMobject(color=GREEN, stroke_width=4).set_points_as_corners(pts)
            return draw

        for k, (cx, ax) in enumerate(cols):
            self.add(always_redraw(arm(k, cx)), always_redraw(trace(k, ax)))
        self.caption("三种规律都在 2 s 内转过 90°，起点终点都静止", "All three turn 90° in 2 s, starting and ending at rest", wait=0.5)
        self.play(t.animate.set_value(2.4), run_time=7, rate_func=linear)
        self.caption("三次多项式和梯形速度：角加速度在起点就“跳”起来，末端随之抖动",
                     "Cubic and trapezoid: the acceleration jumps at once and the tip shakes")
        self.caption("五次多项式：角加速度从零平滑地升起，没有冲击", "Quintic: the acceleration rises smoothly from zero, no shock")
        imp = VGroup()
        SIGNS = [[1, 1], [], [1, -1, -1, 1]]          # up where α jumps up, down where it jumps down
        for k, (cx, ax) in enumerate(cols):
            for tj, sg in zip(JUMPS[k], SIGNS[k]):
                imp.add(Arrow(ax.c2p(tj, 0), ax.c2p(tj, 0) + UP * 0.9 * sg, buff=0, color=RED, stroke_width=4))
        self.play(LaggedStart(*[GrowArrow(a) for a in imp], lag_ratio=0.2))
        self.caption("红色箭头：加速度的跳跃处，加加速度是冲激（无穷大）", "Red arrows: where the acceleration jumps, the jerk is an impulse")
        self.card([["位置 → 速度 → 加速度 → 加加速度", "Position → velocity → acceleration → jerk"],
                   MathTex(r"\theta,\quad \omega=\dot\theta,\quad \alpha=\ddot\theta,\quad j=\dddot\theta", font_size=48),
                   ["加速度连续，运动才平顺", "Continuous acceleration means smooth motion"]])
