"""动画 15.5.1（配图 15.5.1）：无穷区间上的反常积分——上限 T 向右推进，y = 1/x 与 y = 1/x² 下从 1 到 T 的面积同时累积：
前者随 ln T 无限增长，后者趋于 1。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("15.5", "无穷区间上的积分", "Integrals over infinite intervals")
        ax = Axes(x_range=[0, 12, 2], y_range=[0, 1.2, 0.5], x_length=7.0, y_length=4.2, tips=False,
                  axis_config={"color": GREY_B}).shift(LEFT * 2.4 + DOWN * 0.4)
        g1 = ax.plot(lambda x: 1 / x, x_range=[0.85, 12], color=ORANGE, stroke_width=3)
        g2 = ax.plot(lambda x: 1 / x ** 2, x_range=[0.92, 12], color=STEEL, stroke_width=3)
        l1 = MathTex(r"y=\frac1x", font_size=32, color=ORANGE).move_to(ax.c2p(3.2, 0.55))
        l2 = MathTex(r"y=\frac1{x^2}", font_size=32, color=STEEL).move_to(ax.c2p(1.8, 1.05))
        self.play(Create(ax), Create(g1), Create(g2), Write(l1), Write(l2))
        T = ValueTracker(1.01)
        a1 = always_redraw(lambda: ax.get_area(g1, x_range=[1, T.get_value()], color=ORANGE, opacity=0.25))
        a2 = always_redraw(lambda: ax.get_area(g2, x_range=[1, T.get_value()], color=STEEL, opacity=0.45))
        v1 = always_redraw(lambda: MathTex(r"\int_1^T\frac{dx}{x}=\ln T=%.3f" % np.log(T.get_value()), font_size=32, color=ORANGE)
                           .to_edge(RIGHT, buff=0.3).shift(UP * 1.4))
        v2 = always_redraw(lambda: MathTex(r"\int_1^T\frac{dx}{x^2}=1-\frac1T=%.3f" % (1 - 1 / T.get_value()), font_size=32, color=STEEL)
                           .to_edge(RIGHT, buff=0.3).shift(UP * 0.4))
        self.add(a1, a2, v1, v2)
        self.caption("上限 T 向右推进，两块面积一起累积", "As T moves right, both areas grow", wait=0.2)
        self.play(T.animate.set_value(12), run_time=6, rate_func=linear)
        self.caption("1/x² 的面积不超过 1；1/x 的面积随 ln T 无限增长", "Area under 1/x² stays below 1; under 1/x it grows like ln T", wait=0.4)
        big = MathTex(r"T=10^6:\ \ \ln T=13.8,\qquad 1-\frac1T=0.999999", font_size=30).to_edge(RIGHT, buff=0.3).shift(DOWN * 0.6)
        self.play(Write(big))
        self.caption("1/x 下降得太慢，面积没有上限：积分发散", "1/x falls too slowly: the integral diverges", wait=1.0)
        self.play(*[FadeOut(m) for m in (ax, g1, g2, l1, l2, a1, a2, v1, v2, big)])
        self.card([["反常积分", "Improper integral"],
                   MathTex(r"\int_1^{\infty}\frac{dx}{x^p}=\lim_{T\to\infty}\int_1^T\frac{dx}{x^p}=\begin{cases}\dfrac1{p-1}, & p>1\\ \infty, & p\le 1\end{cases}", font_size=40),
                   ["积分的极限存在才叫收敛", "Converges only when the limit exists"]])
