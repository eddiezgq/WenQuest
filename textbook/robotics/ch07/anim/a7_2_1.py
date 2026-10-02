"""动画 7.2.1（配图 7.2.1）：欧拉法沿切线一步一步地走（电机起动）；步长减半、再减半，折线逐渐贴近精确解。"""
from manim import *
from wq_anim import *
import numpy as np
import math

TAU = 0.019017                 # 时间常数，s
WINF = 237.72                  # 最终转速，rad/s


def exact(t):
    return WINF * (1 - math.exp(-t / TAU))


def euler(h, T=0.06):
    w, out = 0.0, [(0.0, 0.0)]
    for k in range(int(round(T / h))):
        w = w + h * (WINF - w) / TAU
        out.append(((k + 1) * h, w))
    return out


class Lesson(Base):
    def construct(self):
        self.title("7.2", "欧拉法：沿切线走一步", "Euler's method: one step along the tangent")
        ax = Axes(x_range=[0, 62, 10], y_range=[0, 300, 50], x_length=9.5, y_length=4.0,
                  axis_config={"color": GREY_B, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [0, 20, 40, 60]},
                  y_axis_config={"numbers_to_include": [0, 100, 200, 300]}).shift(UP * 0.05 + RIGHT * 0.3)
        xl = Text("t / ms", font=LATIN, font_size=20, color=MUTED).next_to(ax.x_axis.get_end(), RIGHT, buff=0.15)
        yl = Text("ω / (rad/s)", font=LATIN, font_size=20, color=MUTED).next_to(ax.y_axis, UP, buff=0.1)
        curve = ax.plot(lambda x: exact(x / 1000), x_range=[0, 60], color=WHITE, stroke_width=4)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(Create(curve), run_time=1.2)
        self.caption("白线是精确解 ω(t)；方程给出每一点的斜率 (ω∞ − ω)/τ", "White: the exact ω(t); the equation gives the slope (ω∞ − ω)/τ at every point")

        for h, col, rt in ((0.010, ORANGE, 0.7), (0.005, YELLOW, 1.5), (0.0025, GREEN, 1.5)):
            pts = euler(h)
            grp = VGroup(Dot(ax.c2p(0, 0), color=col, radius=0.06))
            self.add(grp)
            if h == 0.010:
                self.caption("从起点沿切线走 h = 10 ms，得到 ω₁", "From the start, walk h = 10 ms along the tangent: ω₁", wait=0)
            elif h == 0.005:
                self.caption("步长减半：h = 5 ms", "Halve the step: h = 5 ms", wait=0)
            else:
                self.caption("再减半：h = 2.5 ms，折线贴近精确解", "Halve again: h = 2.5 ms, the polyline hugs the curve", wait=0)
            if h == 0.010:
                for (t0, w0), (t1, w1) in zip(pts, pts[1:]):
                    seg = Line(ax.c2p(t0 * 1000, w0), ax.c2p(t1 * 1000, w1), color=col, stroke_width=4)
                    slope = (WINF - w0) / TAU
                    ext = DashedLine(ax.c2p(t0 * 1000, w0), ax.c2p((t0 + 1.4 * h) * 1000, w0 + 1.4 * h * slope), color=col,
                                     stroke_width=2, stroke_opacity=0.6)
                    self.play(Create(ext), run_time=rt * 0.5)
                    self.play(Create(seg), FadeOut(ext), run_time=rt * 0.5)
                    d = Dot(ax.c2p(t1 * 1000, w1), color=col, radius=0.05)
                    self.add(d)
                    grp.add(seg, d)
            else:
                poly = VMobject(color=col, stroke_width=4).set_points_as_corners([ax.c2p(t * 1000, w) for t, w in pts])
                dots = VGroup(*[Dot(ax.c2p(t * 1000, w), color=col, radius=0.04) for t, w in pts])
                self.play(Create(poly), FadeIn(dots, lag_ratio=0.1), run_time=rt)
                grp.add(poly, dots)
            t_end, w_end = pts[-1]
            err = w_end - exact(t_end)
            lab = Text("h = %.1f ms   e(60 ms) = %.2f rad/s" % (h * 1000, err), font=LATIN, font_size=22, color=col)
            lab.to_corner(UR, buff=0.5).shift(DOWN * (0.8 + 0.4 * [0.010, 0.005, 0.0025].index(h)))
            self.play(FadeIn(lab), run_time=0.4)
            self.wait(0.3)
        self.caption("步长减半，误差也约减半：欧拉法是一阶方法", "Halve the step and the error roughly halves: Euler is first order")
        self.wait(1)
        self.card([["欧拉法", "Euler's method"],
                   MathTex(r"x_{k+1} = x_k + h\,f(t_k, x_k)", font_size=46),
                   ["局部误差 ∝ h²，全局误差 ∝ h", "local error ∝ h², global error ∝ h"]])
