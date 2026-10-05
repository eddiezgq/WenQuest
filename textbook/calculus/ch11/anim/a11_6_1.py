"""动画 11.6.1（配图 11.6.1）：梯度下降——小球沿 f(x) = 0.6x² 滑向谷底：xₖ₊₁ = xₖ − ηf′(xₖ)。
步长小（η = 0.4）时稳稳地逼近；步长大（η = 1.5）时越过谷底来回振荡，仍收敛；步长再大（η = 1.8）时越摆越远，发散。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("11.6", "梯度下降", "Gradient descent")
        ax = Axes(x_range=[-4, 4, 1], y_range=[0, 9, 3], x_length=9, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.6)
        f = lambda x: 0.6 * x * x
        df = lambda x: 1.2 * x
        g = ax.plot(f, x_range=[-3.9, 3.9], color=WHITE, stroke_width=3)
        self.play(Create(ax), Create(g))
        for eta, n, col, cn, en in ((0.4, 7, GREEN, "η = 0.4：每步都朝谷底走一段，稳稳地逼近", "η = 0.4: each step moves towards the bottom"),
                                    (1.5, 9, YELLOW, "η = 1.5：越过谷底来回振荡，振幅逐步变小", "η = 1.5: overshoots and oscillates, but shrinks"),
                                    (1.8, 4, RED, "η = 1.8 > 2/f″：越摆越远，发散", "η = 1.8 > 2/f″: swings grow, divergence")):
            lab = MathTex(r"x_{k+1}=x_k-\eta f'(x_k),\quad \eta=%.1f" % eta, font_size=36, color=col).to_edge(UP).shift(DOWN * 0.9)
            self.play(Write(lab))
            self.caption(cn, en, wait=0.2)
            x = 3.2 if eta < 1.7 else 2.4
            ball = Dot(ax.c2p(x, f(x)), color=col, radius=0.11)
            self.play(FadeIn(ball))
            trail = VGroup()
            for _ in range(n):
                xn = x - eta * df(x)
                if abs(xn) > 3.95:
                    break
                arrow = Arrow(ax.c2p(x, f(x)), ax.c2p(xn, f(xn)), buff=0.05, color=col, stroke_width=3, max_tip_length_to_length_ratio=0.12)
                self.play(GrowArrow(arrow), ball.animate.move_to(ax.c2p(xn, f(xn))), run_time=0.55)
                trail.add(arrow)
                x = xn
            self.wait(0.5)
            self.play(FadeOut(trail), FadeOut(ball), FadeOut(lab))
        self.play(FadeOut(ax), FadeOut(g))
        self.card([["梯度下降的步长", "Step size in gradient descent"],
                   MathTex(r"x_{k+1}-x^*\approx(1-\eta f''(x^*))(x_k-x^*),\qquad 0<\eta<\frac{2}{f''(x^*)}", font_size=40),
                   ["步长太小走得慢，太大会振荡甚至发散", "Too small is slow; too large oscillates or diverges"]])
