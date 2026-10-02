"""动画 7.3.1（配图 7.3.1）：牛顿法解扭簧连杆的平衡方程 f(θ) = k(π/3 − θ) − m𝔤l_c cos θ = 0：
作切线、走到与横轴的交点、再作切线；右侧逐行列出 θ_k 和误差，误差的位数每步约加倍。"""
from manim import *
from wq_anim import *
import numpy as np
import math

KS, MGL = 10.0, 4.905
ROOT = 0.659580125280635


def f(t):
    return KS * (math.pi / 3 - t) - MGL * math.cos(t)


def df(t):
    return -KS + MGL * math.sin(t)


class Lesson(Base):
    def construct(self):
        self.title("7.3", "牛顿法：顺着切线走到零", "Newton's method: follow the tangent to zero")
        ax = Axes(x_range=[-0.05, 1.1, 0.2], y_range=[-3, 6.5, 2], x_length=6.6, y_length=4.6,
                  axis_config={"color": GREY_B, "include_tip": False}).shift(LEFT * 2.6 + DOWN * 0.3)
        xl = MathTex(r"\theta", font_size=30, color=INK).next_to(ax.x_axis.get_end(), RIGHT, buff=0.1)
        yl = MathTex(r"f(\theta)", font_size=30, color=INK).next_to(ax.y_axis.get_end(), UP, buff=0.1)
        curve = ax.plot(f, x_range=[-0.05, 1.1], color=WHITE, stroke_width=4)
        self.play(Create(ax), Write(xl), Write(yl))
        self.play(Create(curve), run_time=1.0)
        self.caption("扭簧连杆的平衡角：f(θ) 与横轴的交点", "Equilibrium of the spring-held link: where f(θ) crosses the axis")
        table = VGroup(Text("k      θₖ             |θₖ − θ*|", font=LATIN, font_size=20, color=MUTED)).to_corner(UR, buff=0.5).shift(DOWN * 0.9 + LEFT * 1.0)
        self.play(FadeIn(table))
        t = 0.0
        cols = [ORANGE, YELLOW, GREEN, TEAL]
        row = Text("0    %.10f    %.1e" % (t, abs(t - ROOT)), font=LATIN, font_size=20, color=cols[0])
        row.next_to(table, DOWN, aligned_edge=LEFT, buff=0.18)
        self.play(FadeIn(row))
        last = row
        for k in range(3):
            col = cols[k]
            p = ax.c2p(t, f(t))
            v = DashedLine(ax.c2p(t, 0), p, color=GREY_B, stroke_width=2)
            d = Dot(p, color=col, radius=0.07)
            self.play(Create(v), FadeIn(d), run_time=0.5)
            t1 = t - f(t) / df(t)
            tan = Line(ax.c2p(t - 0.05, f(t) - 0.05 * df(t)), ax.c2p(t1 + 0.06, 0.06 * df(t)), color=col, stroke_width=4)
            if k == 0:
                self.caption("在 θ₀ 处作切线", "Draw the tangent at θ₀", wait=0)
            self.play(Create(tan), run_time=0.8)
            nd = Dot(ax.c2p(t1, 0), color=col, radius=0.07)
            self.play(FadeIn(nd, scale=1.6), run_time=0.4)
            if k == 0:
                self.caption("切线与横轴的交点就是 θ₁；再从 θ₁ 出发", "Where the tangent meets the axis is θ₁; start again from θ₁", wait=0)
            t = t1
            err = abs(t - ROOT)
            row = Text("%d    %.10f    %.1e" % (k + 1, t, err), font=LATIN, font_size=20, color=cols[k + 1])
            row.next_to(last, DOWN, aligned_edge=LEFT, buff=0.12)
            self.play(FadeIn(row), run_time=0.5)
            last = row
            self.wait(0.5)
        t = t - f(t) / df(t)
        row = Text("4    %.10f    %.1e" % (t, abs(t - ROOT)), font=LATIN, font_size=20, color=WHITE)
        row.next_to(last, DOWN, aligned_edge=LEFT, buff=0.12)
        self.play(FadeIn(row), run_time=0.5)
        self.caption("误差 10⁻¹ → 10⁻³ → 10⁻⁶ → 10⁻¹²：有效位数每步约加倍", "Error 10⁻¹ → 10⁻³ → 10⁻⁶ → 10⁻¹²: the correct digits double each step")
        self.wait(1)
        self.card([["牛顿法", "Newton's method"],
                   MathTex(r"\theta_{k+1} = \theta_k - \frac{f(\theta_k)}{f'(\theta_k)},\qquad |e_{k+1}| \le \frac{M}{2m}\,e_k^2", font_size=42),
                   ["初值足够近时二次收敛", "quadratic convergence from a close enough start"]])
