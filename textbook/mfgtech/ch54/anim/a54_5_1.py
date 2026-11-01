"""动画 54.5.1（配图 54.5.2、54.5.3）：磨床开机后没有预热就按冷态调好的尺寸批量磨削——砂轮架逐渐热伸长，磨出的直径逐件变小，
约 3τ 后趋于稳定；预热到热平衡再调整尺寸，直径就稳定在公差中间。数值与仿真车间“磨床未预热”情景相同：
直径上的热伸长 δ∞ = 10 µm、时间常数 τ = 6 件（sim/errors.py），Ø35 k6 公差带 35.002–35.018。"""
from manim import *
from wq_anim import *
import numpy as np

DINF, TAU, N = 0.010, 6.0, 30


class Lesson(Base):
    def construct(self):
        self.title("54.5", "开机后的热伸长", "Warming up after start-up")
        ax = Axes(x_range=[0, N, 5], y_range=[34.994, 35.020, 0.004], x_length=8.5, y_length=3.6, tips=False,
                  axis_config={"color": MUTED}).shift(DOWN * 0.3 + LEFT * 1.0)
        lo = DashedLine(ax.c2p(0, 35.002), ax.c2p(N, 35.002), color=RED)
        hi = DashedLine(ax.c2p(0, 35.018), ax.c2p(N, 35.018), color=RED)
        lab = VGroup(zh("公差带 Ø35 k6", 20, RED).next_to(hi, UP, buff=0.05).align_to(hi, RIGHT),
                     zh("零件序号（开机后）", 20, MUTED).next_to(ax, DOWN, buff=0.15),
                     zh("直径", 20, MUTED).next_to(ax, LEFT, buff=0.1))
        self.play(Create(ax), Create(lo), Create(hi), FadeIn(lab))
        # 砂轮架：右侧的一个矩形，热伸长时向左（工件）伸出
        grow = ValueTracker(0.0)
        head = always_redraw(lambda: Rectangle(width=1.6 + grow.get_value() * 120, height=0.9, color=ORANGE, fill_opacity=0.5)
                             .move_to(np.array([5.6 - grow.get_value() * 60, 1.6, 0])))
        hl = zh("砂轮架", 20, ORANGE).move_to(np.array([5.6, 2.3, 0]))
        rd = always_redraw(lambda: zh(f"热伸长 {grow.get_value() * 1000:4.1f} µm", 22, ORANGE).move_to(np.array([5.4, 0.8, 0])))
        self.play(FadeIn(head), FadeIn(hl), FadeIn(rd))
        self.caption("冷态下调好尺寸：第 1 件在公差中间", "Size set with the machine cold: part 1 is mid-tolerance")
        rng = np.random.default_rng(54)
        dots = VGroup()
        for i in range(N):
            d = 35.010 - DINF * (1 - np.exp(-i / TAU)) + rng.normal(0, 0.0008)
            g = DINF * (1 - np.exp(-i / TAU))
            dot = Dot(ax.c2p(i + 0.5, d), radius=0.05, color=BLUE if d >= 35.002 else RED)
            dots.add(dot)
            self.play(FadeIn(dot), grow.animate.set_value(g), run_time=0.18)
        curve = ax.plot(lambda x: 35.010 - DINF * (1 - np.exp(-x / TAU)), x_range=[0, N], color=YELLOW)
        self.play(Create(curve))
        self.caption("砂轮架向工件伸长，直径逐件变小；约 3τ 以后才稳定——后面的件已经偏小、报废",
                     "The wheelhead grows toward the work; size drops part by part and settles after about 3τ — the later parts are undersize")
        self.card([["先预热到热平衡，再调整尺寸；或者用在机测量随时补偿", "Warm up to equilibrium first, then set size — or compensate with in-process gauging"],
                   ["数据的指纹：开机后逐件单调变化，按指数规律趋于稳定", "Fingerprint: a monotonic change after start-up that levels off exponentially"]])
