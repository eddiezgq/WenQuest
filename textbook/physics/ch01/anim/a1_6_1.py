"""动画 1.6.1（配图 1.6.1）：最小二乘。数据点（单摆的 T²–L，与算例 1.6.1 同一组数）固定，一条过数据重心的直线
逐步改变斜率，竖直的红线段是残差，右侧的柱子是残差平方和；平方和最小时，直线就是最小二乘直线。"""
from manim import *
from wq_anim import *
import numpy as np

L = np.array([0.20, 0.35, 0.50, 0.65, 0.80, 0.95])
T2 = np.array([18.55, 24.31, 28.91, 32.84, 36.42, 39.39]) ** 2 / 400      # 算例 1.6.1 的 t₂₀ → T²


class Lesson(Base):
    def construct(self):
        self.title("1.6", "最小二乘：让残差平方和最小", "Least squares: the smallest sum of squared residuals")
        ax = Axes(x_range=[0, 1.05, 0.2], y_range=[0, 6, 1], x_length=7.5, y_length=4.2, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(LEFT * 1.8 + DOWN * 0.1)
        xl = MathTex(r"L/\mathrm m", font_size=28).next_to(ax.x_axis, DOWN, buff=0.4).align_to(ax.x_axis, RIGHT)
        yl = MathTex(r"T^2/\mathrm s^2", font_size=28).next_to(ax.y_axis, UP, buff=0.1)
        pts = VGroup(*[Dot(ax.c2p(x, y), color=BLUE, radius=0.07) for x, y in zip(L, T2)])
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), LaggedStart(*[FadeIn(p, scale=2) for p in pts], lag_ratio=0.2))
        xb, yb = L.mean(), T2.mean()
        b_best = np.sum((L - xb) * (T2 - yb)) / np.sum((L - xb) ** 2)
        k = ValueTracker(1.0)

        def line_at():
            b = k.get_value()
            return Line(ax.c2p(0, yb - b * xb), ax.c2p(1.05, yb + b * (1.05 - xb)), color=RED_B, stroke_width=4)

        def resid():
            b = k.get_value()
            return VGroup(*[Line(ax.c2p(x, y), ax.c2p(x, yb + b * (x - xb)), color=RED, stroke_width=3) for x, y in zip(L, T2)])

        bar_base = RIGHT * 4.6 + DOWN * 2.2

        def S(b):
            return float(np.sum((T2 - (yb + b * (L - xb))) ** 2))

        smax = max(S(1.0), S(7.0))

        def bar():
            h = 3.8 * S(k.get_value()) / smax
            r = Rectangle(width=0.8, height=max(h, 0.02), fill_color=ORANGE, fill_opacity=0.8, stroke_width=0)
            return r.move_to(bar_base, aligned_edge=DOWN)

        ln, rs, br = always_redraw(line_at), always_redraw(resid), always_redraw(bar)
        lab = VGroup(zh("残差平方和", 22), en("sum of squares", 16)).arrange(DOWN, buff=0.05).next_to(bar_base, DOWN, buff=0.15)
        self.add(ln, rs, br); self.play(FadeIn(lab))
        self.caption("直线总过数据的重心；先让斜率小一些", "The line passes through the centroid; start with a small slope", wait=0.5)
        self.play(k.animate.set_value(7.0), run_time=3)
        self.caption("斜率太大，残差又变大了", "Too steep: the residuals grow again", wait=0.5)
        self.play(k.animate.set_value(b_best), run_time=2.5)
        best = MathTex(f"T^2 = {yb - b_best * xb:.3f} + {b_best:.3f}\\,L", font_size=34, color=RED_B).to_corner(UR).shift(DOWN * 1.2)
        self.play(Write(best))
        self.caption("平方和最小的这条，就是最小二乘直线", "The one with the smallest sum of squares is the least-squares line")
        self.card([["最小二乘法", "Least squares"],
                   MathTex(r"b=\frac{\sum (x_i-\bar x)(y_i-\bar y)}{\sum (x_i-\bar x)^2},\qquad a=\bar y-b\bar x", font_size=40),
                   ["斜率 g = 4π²/b，用斜率求 g，避开了摆长的系统误差", "g = 4π²/b from the slope, which sidesteps the length offset"]])
