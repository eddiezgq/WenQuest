"""动画 14.3.1（配图 14.3.1）：三角代换——半圆 y = √(1 − x²) 下的面积。令 x = sin θ，点在圆上转动，
窄条宽 dx = cos θ dθ、高 cos θ，面积元化成 cos²θ dθ；θ 从 −π/2 转到 π/2，面积累积到 π/2。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("14.3", "三角代换", "Trigonometric substitution")
        ax = Axes(x_range=[-1.2, 1.2, 1], y_range=[0, 1.2, 1], x_length=6.4, y_length=3.2, tips=False,
                  axis_config={"color": GREY_B}).shift(LEFT * 2.2 + DOWN * 0.4)
        semi = ax.plot(lambda x: np.sqrt(max(1 - x * x, 0)), x_range=[-1, 1, 0.002], color=WHITE, stroke_width=3)
        lab = MathTex(r"y=\sqrt{1-x^2}", font_size=32).next_to(ax.c2p(0.8, 0.8), UR, buff=0.1)
        self.play(Create(ax), Create(semi), Write(lab))
        th = ValueTracker(-PI / 2 + 0.001)
        area = always_redraw(lambda: ax.get_area(semi, x_range=[-1, np.sin(th.get_value())], color=STEEL, opacity=0.4))
        dot = always_redraw(lambda: Dot(ax.c2p(np.sin(th.get_value()), np.cos(th.get_value())), color=ORANGE, radius=0.08))
        rad = always_redraw(lambda: Line(ax.c2p(0, 0), ax.c2p(np.sin(th.get_value()), np.cos(th.get_value())), color=ORANGE))
        self.add(area, rad, dot)
        sub = MathTex(r"x=\sin\theta,\quad dx=\cos\theta\,d\theta", font_size=36, color=ORANGE).to_edge(RIGHT, buff=0.3).shift(UP * 1.6)
        self.play(Write(sub))
        self.caption("令 x = sin θ：圆上的点随 θ 转动，它的横坐标就是 x", "Let x = sin θ: as θ turns, the point's abscissa is x", wait=0.3)
        val = always_redraw(lambda: MathTex(r"\theta=%.2f,\ \ \text{area}=%.3f" % (th.get_value(), (th.get_value() + PI / 2) / 2 + np.sin(2 * th.get_value()) / 4),
                                            font_size=32, color=STEEL).next_to(sub, DOWN, buff=0.5))
        self.add(val)
        self.play(th.animate.set_value(0.6), run_time=4, rate_func=linear)
        w = 0.12
        x0 = np.sin(0.6)
        strip = Rectangle(width=ax.c2p(w, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, np.cos(0.6))[1] - ax.c2p(0, 0)[1],
                          color=YELLOW, fill_opacity=0.6, stroke_width=1).move_to(ax.c2p(x0 + w / 2, np.cos(0.6) / 2))
        el = MathTex(r"\sqrt{1-x^2}\,dx=\cos\theta\cdot\cos\theta\,d\theta", font_size=34, color=YELLOW).next_to(val, DOWN, buff=0.5)
        self.play(FadeIn(strip), Write(el))
        self.caption("窄条高 cos θ、宽 cos θ dθ：根号消失了", "Strip height cos θ, width cos θ dθ: the root is gone", wait=0.6)
        self.play(FadeOut(strip))
        self.play(th.animate.set_value(PI / 2 - 0.001), run_time=3, rate_func=linear)
        res = MathTex(r"\int_{-1}^{1}\sqrt{1-x^2}\,dx=\int_{-\pi/2}^{\pi/2}\cos^2\theta\,d\theta=\frac{\pi}{2}", font_size=28, color=WHITE).to_edge(RIGHT, buff=0.3).shift(DOWN * 1.2)
        self.play(Write(res))
        self.caption("半个单位圆的面积是 π/2", "Half the unit disk has area π/2", wait=1.0)
        self.play(*[FadeOut(m) for m in (ax, semi, lab, area, rad, dot, sub, val, el, res)])
        self.card([["三角代换", "Trigonometric substitution"],
                   MathTex(r"\sqrt{a^2-x^2}:\ x=a\sin\theta\qquad \sqrt{a^2+x^2}:\ x=a\tan\theta\qquad \sqrt{x^2-a^2}:\ x=a\sec\theta", font_size=34),
                   ["用 sin²θ + cos²θ = 1 一类恒等式把根号化掉", "Use identities like sin²θ + cos²θ = 1 to clear the root"]])
