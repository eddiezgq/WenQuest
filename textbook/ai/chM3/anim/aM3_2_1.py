"""动画 M3.2.1（配图 M3.2.1）：大数定律与中心极限定理。
先看一条抽检的轨迹：样本比例一开始上下乱跳，随着件数增多稳稳地收敛到真实的 2%，而且永远落在
一条按 1/√n 收窄的带子里。再看一件更奇的事：返工工时的分布八成是 0、很不像正态，可是把 n 个
平均起来，它们的分布随 n 增大越来越贴近正态曲线——这就是置信区间能用的理由。
数值都在动画里现算（numpy），与算例 M3.2.2、M3.2.3 用的是同一套公式。"""
import numpy as np
from manim import *
from wq_anim import *

P = 0.02                                       # 真实不合格率
RNG = np.random.default_rng(20261008)


def trace(n=4000):
    d = (RNG.random(n) < P).astype(float)
    return np.cumsum(d) / np.arange(1, n + 1)


def rework(shape):
    hit = RNG.random(shape) < 0.2
    return np.where(hit, RNG.uniform(0.5, 3.0, shape), 0.0)


def curve(xs, ys, color, width=2.2):
    return VMobject(stroke_width=width, color=color).set_points_as_corners(
        [[float(x), float(y), 0] for x, y in zip(xs, ys)])


class Lesson(Base):
    def construct(self):
        self.title("M3.2", "大数定律与中心极限定理", "The law of large numbers and the CLT")

        # ---------- 大数定律：横轴 log n，纵轴样本比例
        ax = VGroup(Line([-5.6, -1.6, 0], [5.6, -1.6, 0], stroke_width=1.4, color=GREY),
                    Line([-5.6, -1.6, 0], [-5.6, 2.2, 0], stroke_width=1.4, color=GREY))
        self.play(Create(ax), run_time=0.6)
        n = 4000
        ns = np.arange(1, n + 1)
        X = -5.6 + 11.2 * np.log10(ns) / np.log10(n)
        def Y(p):
            return -1.6 + np.clip(p, 0, 0.08) / 0.08 * 3.8
        true_line = Line([-5.6, Y(P), 0], [5.6, Y(P), 0], stroke_width=2, color=YELLOW)
        band_hi = curve(X, Y(P + 1.96 * np.sqrt(P * (1 - P) / ns)), GREY, 1.2)
        band_lo = curve(X, Y(P - 1.96 * np.sqrt(P * (1 - P) / ns)), GREY, 1.2)
        self.play(Create(true_line), Create(band_hi), Create(band_lo), run_time=1.0)
        self.caption("真实不合格率 2%（黄线）；灰线是 $\\pm1.96$ 个标准差，按 $1/\\sqrt{n}$ 收窄",
                     "True rate 2% (yellow); the grey band is ±1.96 sd, shrinking as $1/\\sqrt{n}$")
        for col in (BLUE, GREEN, RED):
            self.play(Create(curve(X, Y(trace(n)), col, 1.8)), run_time=1.3)
        self.caption("三次抽检：开头乱跳，几百件以后就贴着真值走了——这就是大数定律",
                     "Three runs: wild at first, hugging the truth after a few hundred — the law of large numbers")

        self.clear_stage()

        # ---------- 中心极限定理：直方图随 n 变正态
        def hist_curve(n, color):
            m = rework((20000, n)).mean(axis=1)
            one = rework(100000)
            z = (m - one.mean()) / (one.std() / np.sqrt(n))
            h, edges = np.histogram(z, bins=np.linspace(-4, 4, 60), density=True)
            mid = (edges[:-1] + edges[1:]) / 2
            return curve(mid * 1.3, -1.6 + np.minimum(h, 0.55) / 0.55 * 3.4, color, 2.0)

        xs = np.linspace(-4, 4, 160)
        normal = curve(xs * 1.3, -1.6 + np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi) / 0.55 * 3.4, YELLOW, 2.4)
        self.play(Create(normal), run_time=0.9)
        self.caption("黄线是标准正态。下面放一个很不像正态的分布：八成的零件返工工时是 0",
                     "The yellow curve is the standard normal. Now a very non-normal quantity: 80% of parts need no rework")
        prev = None
        for n_, col, zh, en in ((1, RED, "一个零件：一半以上的质量堆在“0”上，与正态毫不相干",
                                 "One part: most of the mass sits at zero"),
                                (5, ORANGE, "五个一组取平均：开始有个鼓包了", "Average of five: a bump appears"),
                                (30, GREEN, "三十个一组：已经相当接近", "Thirty: already close"),
                                (200, BLUE, "两百个一组：几乎与黄线重合", "Two hundred: nearly the same curve")):
            c = hist_curve(n_, col)
            self.play(Create(c), run_time=1.0) if prev is None else self.play(Transform(prev, c), run_time=1.0)
            prev = prev or c
            self.caption(zh, en)

        self.card([["两条定律", "Two laws"],
                   MathTex(r"\mathrm{sd}(\bar X) = \frac{\sigma}{\sqrt n}", font_size=46),
                   ["大数定律：样本均值收敛到真值", "LLN: the sample mean converges to the truth"],
                   ["中心极限定理：不管原分布什么样，均值的分布趋于正态",
                    "CLT: whatever the distribution, the mean becomes normal"]])
