"""动画 7.1.1（配图 7.1.3）：连杆从 90° 释放，左边摆动，右边状态点 (θ, θ̇) 在相平面上画出闭合的轨线；
再从 175° 释放，状态点沿分界线附近缓慢通过顶点附近。"""
from manim import *
from wq_anim import *
import numpy as np
import math

WN2 = 29.43                      # ω_n² = 3𝔤/(2L)，L = 0.5 m


def simulate(th0, T, h=0.002):
    """RK4 积分 θ̈ = −ω_n² sin θ，返回 (t, θ, θ̇) 数组。"""
    def f(x):
        return np.array([x[1], -WN2 * math.sin(x[0])])
    x = np.array([th0, 0.0])
    out = [x.copy()]
    for _ in range(int(T / h)):
        k1 = f(x)
        k2 = f(x + h / 2 * k1)
        k3 = f(x + h / 2 * k2)
        k4 = f(x + h * k3)
        x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(x.copy())
    out = np.array(out)
    return np.arange(len(out)) * h, out[:, 0], out[:, 1]


class Lesson(Base):
    def construct(self):
        self.title("7.1", "连杆的摆动与相平面", "A swinging link and its phase plane")
        pivot = np.array([-4.3, 1.6, 0])
        Lk = 2.6
        ceiling = Line(pivot + LEFT * 0.8, pivot + RIGHT * 0.8, color=GREY_B, stroke_width=4)
        down = DashedLine(pivot, pivot + DOWN * (Lk + 0.3), color=GREY_C, stroke_width=2)
        ax = Axes(x_range=[-3.6, 3.6, math.pi / 2], y_range=[-12, 12, 4], x_length=6.4, y_length=4.8,
                  axis_config={"color": GREY_B, "include_tip": False}).shift(RIGHT * 2.9 + DOWN * 0.4)
        xl = MathTex(r"\theta", color=INK, font_size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = MathTex(r"\dot\theta", color=INK, font_size=30).next_to(ax.y_axis, UP, buff=0.1)
        ticks = VGroup(MathTex(r"-\pi", font_size=24, color=MUTED).next_to(ax.c2p(-math.pi, 0), DOWN, buff=0.15),
                       MathTex(r"\pi", font_size=24, color=MUTED).next_to(ax.c2p(math.pi, 0), DOWN, buff=0.15))
        self.play(Create(ceiling), Create(down), Create(ax), Write(xl), Write(yl), FadeIn(ticks))

        def link_at(th):
            tip = pivot + Lk * np.array([math.sin(th), -math.cos(th), 0])
            return VGroup(Line(pivot, tip, color=STEEL, stroke_width=14), Dot(pivot, radius=0.1, color=WHITE),
                          Dot(pivot + (tip - pivot) / 2, radius=0.07, color=YELLOW))

        t1, th1, om1 = simulate(math.pi / 2, 2 * 1.3671)
        k = ValueTracker(0)
        link = always_redraw(lambda: link_at(th1[int(k.get_value())]))
        dot = always_redraw(lambda: Dot(ax.c2p(th1[int(k.get_value())], om1[int(k.get_value())]), color=YELLOW, radius=0.08))
        path = always_redraw(lambda: VMobject(color=YELLOW, stroke_width=3).set_points_as_corners(
            [ax.c2p(a, b) for a, b in zip(th1[:int(k.get_value()) + 1:5], om1[:int(k.get_value()) + 1:5])] + [ax.c2p(th1[int(k.get_value())], om1[int(k.get_value())])]))
        self.add(path, link, dot)
        self.caption("从 90° 静止释放：状态 (θ, θ̇) 是相平面上的一个点", "Released from 90° at rest: the state (θ, θ̇) is one point in the plane")
        self.caption("连杆来回摆动一次，状态点沿闭曲线走一圈", "One swing back and forth = one loop of the state point", wait=0)
        self.play(k.animate.set_value(len(th1) - 1), run_time=7, rate_func=linear)
        self.wait(0.5)
        for m in (link, dot, path):
            m.clear_updaters()
        keep = path.copy().set_stroke(color=STEEL, width=2, opacity=0.6)
        self.add(keep)
        self.play(FadeOut(link), FadeOut(dot), FadeOut(path))

        sep = VGroup(*[ax.plot(lambda x, s=s: s * 2 * math.sqrt(WN2) * abs(math.cos(x / 2)), x_range=[-math.pi, math.pi],
                               color=RED, stroke_width=3) for s in (1, -1)])
        self.play(Create(sep))
        self.caption("红线是分界线：刚好能摆到正上方的运动", "Red: the separatrix, a motion that just reaches the top")
        t2, th2, om2 = simulate(math.radians(175), 2.6)
        k2 = ValueTracker(0)
        link2 = always_redraw(lambda: link_at(th2[int(k2.get_value())]))
        dot2 = always_redraw(lambda: Dot(ax.c2p(th2[int(k2.get_value())], om2[int(k2.get_value())]), color=ORANGE, radius=0.08))
        path2 = always_redraw(lambda: VMobject(color=ORANGE, stroke_width=3).set_points_as_corners(
            [ax.c2p(a, b) for a, b in zip(th2[:int(k2.get_value()) + 1:5], om2[:int(k2.get_value()) + 1:5])] + [ax.c2p(th2[int(k2.get_value())], om2[int(k2.get_value())])]))
        self.add(path2, link2, dot2)
        self.caption("从 175° 释放：在顶点附近走得极慢，周期变得很长", "Released from 175°: it creeps near the top, so the period is long", wait=0)
        self.play(k2.animate.set_value(len(th2) - 1), run_time=6, rate_func=linear)
        self.wait(1)
        self.card([["状态与相平面", "State and phase plane"],
                   MathTex(r"x = (\theta,\ \dot\theta),\qquad \dot x = f(x) = (\dot\theta,\ -\omega_n^2\sin\theta)", font_size=40),
                   ["方程规定每一点的流向，解就是顺着流向走出的轨线", "The equation sets the flow at every point; a solution follows it"]])
