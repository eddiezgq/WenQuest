"""动画 16.5.1（配图 16.5.1）：文丘里管——流得快的地方压强小。水管内径 50 mm，喉部 25 mm（与算例 16.5.1 一致），
颗粒在喉部走得快；三根竖管里的水柱高度表示各处的压强，喉部的水柱最低。流速与压强按伯努利方程计算（水柱高度按比例缩小画出）。"""
from manim import *
from wq_anim import *
import numpy as np

D1, D2, V1 = 0.050, 0.025, 1.26
G, RHO = 9.81, 1000.0
L = 9.0                                                          # 管长（画面单位）
Y0 = -1.2


def dia(x):                                                      # x ∈ [0, 1]
    return D1 - (D1 - D2) * np.exp(-((x - 0.5) / 0.12) ** 2)


def speed(x):
    return V1 * (D1 / dia(x)) ** 2


def half(x):                                                     # 画面上的半径
    return dia(x) / D1 * 0.7


class Lesson(Base):
    def construct(self):
        self.title("16.5", "流得快的地方压强小", "Where it flows fast, the pressure is low")
        xs = np.linspace(0, 1, 200)
        top = VMobject(color=GREY_B).set_points_smoothly([np.array([-L / 2 + L * x, Y0 + half(x), 0]) for x in xs])
        bot = VMobject(color=GREY_B).set_points_smoothly([np.array([-L / 2 + L * x, Y0 - half(x), 0]) for x in xs])
        self.play(Create(top), Create(bot))
        cols = []
        for xp in (0.15, 0.5, 0.85):
            dp = 0.5 * RHO * (speed(xp) ** 2 - V1 ** 2)                  # 相对入口的压强降
            hgt = 3.2 - dp / (RHO * G) * 2.0                            # 入口处水柱 3.2（画面单位），压降按比例缩小
            X = -L / 2 + L * xp
            tube = Rectangle(width=0.22, height=3.6, color=GREY_B).move_to(np.array([X, Y0 + half(xp) + 1.8, 0]))
            water = Rectangle(width=0.2, height=max(hgt, 0.05), color=BLUE, fill_opacity=0.7, stroke_width=0).move_to(tube.get_center()).align_to(tube, DOWN)
            cols += [tube, water]
        self.caption("三根竖管里的水柱高度表示管中各处的压强", "The water columns in the three tubes show the pressure in the pipe", wait=0)
        self.play(*[FadeIn(c) for c in cols], run_time=1.5)
        t = ValueTracker(0.0)
        seeds = [(k / 24, yy) for k in range(24) for yy in (-0.6, -0.2, 0.2, 0.6)]

        xg = np.linspace(0, 1, 2001)
        tau = np.concatenate([[0], np.cumsum(np.diff(xg) / (speed(xg[:-1]) / V1 * 0.4))])   # 流过 x 所需的时间（画面上放慢）
        Ttot = tau[-1]

        def pos(p, T):
            tt = (np.interp(p[0], xg, tau) + T) % Ttot
            x = float(np.interp(tt, tau, xg))
            return np.array([-L / 2 + L * x, Y0 + p[1] * half(x), 0])

        dots = always_redraw(lambda: VGroup(*[Dot(pos(p, t.get_value()), radius=0.04, color=YELLOW) for p in seeds]))
        self.add(dots)
        self.caption("喉部截面只有四分之一，流速是 4 倍；那里的水柱最低：流得快，压强小", "The throat has a quarter of the area and four times the speed; its column is lowest: fast flow, low pressure", wait=0)
        self.play(t.animate.set_value(6.0), run_time=7, rate_func=linear)
        self.card([["伯努利方程", "Bernoulli's equation"],
                   MathTex(r"p + \tfrac12\rho v^2 + \rho g h = \text{const}", font_size=46),
                   ["沿一根流线，流速大的地方压强小", "along a streamline, where the speed is high the pressure is low"],
                   ["测出压强差，就能算出流量：文丘里流量计", "measure the pressure difference to get the flow: the Venturi meter"]])
