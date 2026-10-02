"""动画 9.1.1（配图 9.1.1）：测力读数一个个到来，直方图逐渐长高，轮廓趋于高斯曲线；样本均值与 ±s 随之稳定。
数据与算例 9.1.2 相同：真实值 15 N，高斯噪声标准差 0.08 N，2000 个读数，固定种子。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("9.1", "噪声读数的直方图", "The histogram of noisy readings")
        rng = np.random.default_rng(901)
        data = 15.0 + 0.08 * rng.standard_normal(2000)
        edges = np.arange(14.70, 15.30 + 1e-9, 0.02)
        nb = len(edges) - 1

        ax = Axes(x_range=[14.70, 15.30, 0.1], y_range=[0, 230, 50], x_length=8.6, y_length=3.7,
                  axis_config={"color": GREY_B, "include_tip": False, "font_size": 22},
                  x_axis_config={"numbers_to_include": [14.8, 14.9, 15.0, 15.1, 15.2], "decimal_number_config": {"num_decimal_places": 1}},
                  y_axis_config={"numbers_to_include": [0, 100, 200]}).shift(UP * 0.45 + LEFT * 1.2)
        xl = zh("读数 / N", 20, MUTED).next_to(ax.x_axis, RIGHT, buff=0.2)
        self.play(Create(ax), FadeIn(xl), run_time=1.0)

        n = ValueTracker(1)

        def counts():
            k = int(n.get_value())
            c, _ = np.histogram(data[:k], bins=edges)
            return c, k

        def bars():
            c, k = counts()
            scale = 2000.0 / max(k, 1)          # 按 2000 个读数的比例画，便于与最终的曲线比较
            g = VGroup()
            for i in range(nb):
                h = min(c[i] * scale, 228)
                if h <= 0:
                    continue
                p0 = ax.c2p(edges[i] + 0.001, 0)
                p1 = ax.c2p(edges[i + 1] - 0.001, h)
                g.add(Rectangle(width=p1[0] - p0[0], height=max(p1[1] - p0[1], 0.001), stroke_width=0,
                                fill_color=GREY_B, fill_opacity=0.75).move_to((p0 + p1) / 2))
            return g

        hist = always_redraw(bars)
        self.add(hist)

        def stats():
            k = max(int(n.get_value()), 2)
            m = float(np.mean(data[:k]))
            s = float(np.std(data[:k], ddof=1))
            line = DashedLine(ax.c2p(m, 0), ax.c2p(m, 225), color=YELLOW, stroke_width=3)
            arr = DoubleArrow(ax.c2p(m - s, 215), ax.c2p(m + s, 215), buff=0, color=ORANGE, stroke_width=4,
                              tip_length=0.18)
            txt = VGroup(MathTex(r"n = %d" % k, font_size=34),
                         MathTex(r"\bar x = %.3f\ \mathrm{N}" % m, font_size=34, color=YELLOW),
                         MathTex(r"s = %.3f\ \mathrm{N}" % s, font_size=34, color=ORANGE)).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            txt.to_edge(RIGHT, buff=0.5).shift(UP * 0.6)
            return VGroup(line, arr, txt)

        st = always_redraw(stats)
        self.add(st)
        self.caption("读数一个个到来：每 0.02 N 一组，数出每组的个数", "Readings arrive one by one: count them in bins 0.02 N wide", wait=0)
        self.play(n.animate.set_value(60), run_time=3, rate_func=linear)
        self.caption("几十个读数时，柱子参差不齐", "With a few dozen readings the bars are ragged", wait=0)
        self.play(n.animate.set_value(400), run_time=4, rate_func=linear)
        self.caption("读数越多，轮廓越光滑，像一口钟", "With more readings the outline smooths into a bell", wait=0)
        self.play(n.animate.set_value(2000), run_time=5, rate_func=linear)
        hist.clear_updaters()
        st.clear_updaters()

        m = float(np.mean(data))
        s = float(np.std(data, ddof=1))
        curve = ax.plot(lambda x: 2000 * 0.02 * math.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi)),
                        x_range=[14.70, 15.30, 0.002], color=BLUE, stroke_width=5)
        self.caption("用样本均值和样本标准差画出高斯曲线：两者吻合", "The Gaussian with the sample mean and std fits the bars", wait=0)
        self.play(Create(curve), run_time=2.5)
        self.wait(1.5)
        self.caption("样本均值和 s 随读数增多而稳定，接近 15 N 和 0.08 N", "x̄ and s settle near 15 N and 0.08 N as readings accumulate")
        self.card([["高斯分布", "Gaussian distribution"],
                   MathTex(r"\mathcal N(x;\mu,\sigma^2)=\frac{1}{\sigma\sqrt{2\pi}}\,e^{-(x-\mu)^2/(2\sigma^2)}", font_size=40),
                   ["许多独立小扰动之和，近似服从高斯分布", "A sum of many small independent disturbances is nearly Gaussian"]])
