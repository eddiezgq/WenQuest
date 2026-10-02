"""动画 44.1.1（配图 44.1.1）：粒子一个一个出现在屏上，落点随机；积累得越多，直方图越接近概率密度 |ψ|²
（宽 L 的盒子中 n = 2 的定态）。统计诠释：波函数给出的是概率。"""
from manim import *
from wq_anim import *
import numpy as np
import random


class Lesson(Base):
    def construct(self):
        self.title("44.1", "一个一个的粒子，积累成概率", "Particle by particle, a probability builds up")
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 2.6, 1], x_length=8, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.6)
        lab = MathTex(r"|\psi|^2 = \tfrac{2}{L}\sin^2\tfrac{2\pi x}{L}", color=PURPLE_B, font_size=32).next_to(ax, UP, buff=0.15).shift(RIGHT * 2.2)
        curve = ax.plot(lambda x: 2 * np.sin(2 * np.pi * x) ** 2, color=PURPLE_B, stroke_width=4)
        xl = MathTex(r"x/L", font_size=28).next_to(ax.x_axis, DOWN, buff=0.15).align_to(ax.x_axis, RIGHT)
        yl = MathTex(r"L\,|\psi|^2", font_size=28).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.caption("每个粒子落在哪里无法预言", "Where each particle lands cannot be predicted", wait=0.5)
        random.seed(441)

        def draw():                              # 按 |ψ|² 舍选抽样
            while True:
                x, y = random.random(), random.uniform(0, 2)
                if y < 2 * np.sin(2 * np.pi * x) ** 2:
                    return x

        nb = 25
        counts = np.zeros(nb)
        bars = VGroup()
        shown = 0
        for target, rt in ((12, 0.25), (60, 0.04), (400, 0.0), (3000, 0.0)):
            if target == 400:
                self.caption("粒子多了，分布的轮廓显现出来", "With more particles the shape of the distribution appears", wait=0)
            dots = VGroup()
            while shown < target:
                x = draw(); shown += 1
                counts[min(nb - 1, int(x * nb))] += 1
                if target <= 60:
                    dots.add(Dot(ax.c2p(x, 2.45), radius=0.05, color=YELLOW))
            if len(dots):
                self.play(LaggedStart(*[FadeIn(d_, scale=2) for d_ in dots], lag_ratio=1.0), run_time=max(1.0, rt * len(dots)))
            h = counts / (shown / nb)            # 归一化为概率密度
            new = VGroup(*[Rectangle(width=8 / nb * 0.9, height=max(1e-3, ax.y_length * min(h[i], 2.6) / 2.6), fill_color=BLUE,
                                     fill_opacity=0.6, stroke_width=0).move_to(ax.c2p((i + 0.5) / nb, 0), aligned_edge=DOWN)
                         for i in range(nb)])
            self.play(Transform(bars, new) if len(bars) else FadeIn(new), FadeOut(dots) if len(dots) else Wait(0.01), run_time=1)
            if not len(bars):
                bars = new
            cnt = MathTex(f"N = {shown}", font_size=34).to_corner(UR).shift(DOWN * 1.2)
            self.play(FadeIn(cnt), run_time=0.2); self.wait(0.5); self.play(FadeOut(cnt), run_time=0.2)
        self.play(Create(curve), Write(lab))
        self.caption("粒子越多，直方图越接近 |ψ|²：波函数给出的是概率", "The more particles, the closer the histogram is to |ψ|²: the wave function gives probabilities")
        self.card([["玻恩的统计诠释", "Born's statistical interpretation"],
                   MathTex(r"P\,\mathrm{d}x = |\Psi|^2\,\mathrm{d}x", font_size=48),
                   ["单次结果随机，大量结果的分布确定", "Single outcomes are random; their distribution is not"]])
