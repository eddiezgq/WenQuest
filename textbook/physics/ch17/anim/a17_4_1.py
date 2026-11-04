"""动画 17.4.1（配图 17.4.1）：所有可能路径中，真实路径让作用量取极值。0.50 kg 的球 t = 0 从地面出发、t = 2.0 s 落回地面
（与算例 17.4.1 一致）。先让抛物线 y = A t(2 − t) 的 A 从小到大扫过去，右边实时画出作用量 S(A)，在 A = g/2 处最小；
再在真实路径上叠加正弦扰动，作用量的读数总是变大。"""
from manim import *
from wq_anim import *
import numpy as np

M, TT, G = 0.50, 2.0, 9.81
TS = np.linspace(0, TT, 401)


def path(A, eps=0.0):
    return A * TS * (TT - TS) + eps * np.sin(2 * np.pi * TS / TT)


def action(A, eps=0.0):
    y = path(A, eps)
    yd = np.gradient(y, TS)
    return float(np.trapezoid(0.5 * M * yd ** 2 - M * G * y, TS))


S_TRUE = action(G / 2)


def dS(A):
    return action(A) - S_TRUE


class Lesson(Base):
    def construct(self):
        self.title("17.4", "真实路径让作用量取驻值", "Of all possible paths, the true one makes the action stationary")
        ax = Axes(x_range=[0, 2, 0.5], y_range=[-1, 9, 2], x_length=5.6, y_length=4.0, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(LEFT * 3.3 + UP * 0.1)
        xl = zh("t / s", 22, MUTED).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = zh("y / m", 22, MUTED).next_to(ax.y_axis, UP, buff=0.15)
        bx = Axes(x_range=[2, 8, 1], y_range=[0, 7, 1], x_length=4.6, y_length=3.1, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(RIGHT * 3.6 + UP * 0.2)
        bxl = zh("A / (m/s²)", 20, MUTED).next_to(bx.x_axis, DOWN, buff=0.35)
        byl = zh("S − S真 / (J·s)", 20, MUTED).next_to(bx.y_axis, UP, buff=0.15)
        ends = VGroup(Dot(ax.c2p(0, 0), color=YELLOW, radius=0.09), Dot(ax.c2p(2, 0), color=YELLOW, radius=0.09))
        self.play(Create(ax), FadeIn(xl, yl), FadeIn(ends))
        self.caption("球在 t = 0 从地面出发，t = 2 s 回到地面：两个端点是固定的", "The ball leaves the ground at t = 0 and is back at t = 2 s: both ends are fixed")

        A = ValueTracker(2.0)
        eps = ValueTracker(0.0)
        curve = always_redraw(lambda: ax.plot_line_graph(TS[::8], path(A.get_value(), eps.get_value())[::8], add_vertex_dots=False,
                                                         line_color=STEEL, stroke_width=4))
        lab = always_redraw(lambda: VGroup(MathTex(r"S =", font_size=40),
                                           DecimalNumber(action(A.get_value(), eps.get_value()), num_decimal_places=2, font_size=40, color=YELLOW),
                                           zh("J·s", 26, WHITE)).arrange(RIGHT, buff=0.15).move_to(RIGHT * 3.6 + UP * 2.65))
        self.add(curve)
        self.play(FadeIn(lab))
        self.caption("每一条可能的路径都算一个数：作用量 S = ∫(T − V) dt", "Every possible path gets a number: the action S = ∫(T − V) dt")
        self.play(Create(bx), FadeIn(bxl, byl))
        trace = VMobject(color=BLUE, stroke_width=4)
        trace.set_points_as_corners([bx.c2p(2.0, dS(2.0))] * 2)

        def grow(m):
            a = A.get_value()
            if a > 2.0:
                xs = np.linspace(2.0, a, max(2, int((a - 2.0) * 20)))
                m.set_points_as_corners([bx.c2p(x, dS(x)) for x in xs])
        trace.add_updater(grow)
        dot = always_redraw(lambda: Dot(bx.c2p(A.get_value(), dS(A.get_value())), color=YELLOW, radius=0.08))
        self.add(trace, dot)
        self.caption("A 从小到大：抛得太低、太高，作用量都大", "Sweep A: thrown too low or too high, the action is larger")
        self.play(A.animate.set_value(8.0), run_time=6, rate_func=linear)
        trace.clear_updaters()
        self.play(A.animate.set_value(G / 2), run_time=2.5)
        best = ax.plot_line_graph(TS[::8], path(G / 2)[::8], add_vertex_dots=False, line_color=RED, stroke_width=5)
        mark = Dot(bx.c2p(G / 2, 0.0), color=RED, radius=0.11)
        self.play(FadeIn(best), FadeIn(mark))
        self.caption("最小值在 A = g/2：正是由牛顿定律得到的真实运动", "The minimum is at A = g/2: exactly the true motion given by Newton's laws")
        self.caption("在真实路径上加一点扰动，作用量也变大", "Add a wiggle to the true path, and the action grows too", wait=0)
        self.play(eps.animate.set_value(0.8), run_time=2)
        self.play(eps.animate.set_value(-0.8), run_time=3)
        self.play(eps.animate.set_value(0.0), run_time=2)
        ball = Dot(ax.c2p(0, 0), color=YELLOW, radius=0.14)
        self.add(ball)
        self.caption("真实的球就走这一条", "The real ball takes this one", wait=0)
        self.play(MoveAlongPath(ball, best["line_graph"]), run_time=2.5, rate_func=linear)
        self.wait(0.5)
        self.card([["哈密顿原理", "Hamilton's principle"],
                   MathTex(r"S = \int_{t_1}^{t_2} L\,\mathrm{d}t , \qquad \delta S = 0", font_size=46),
                   ["端点相同的所有可能运动中，真实运动使作用量取驻值", "among all motions with the same end points, the true one makes the action stationary"],
                   ["由它可以推出拉格朗日方程", "Lagrange's equations follow from it"]])
