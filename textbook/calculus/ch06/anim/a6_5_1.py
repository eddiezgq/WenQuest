"""动画 6.5.1（配图 6.5.1）：有限覆盖——距离曲线 d(t) 上每一点伸出安全邻域，层层盖住 [0, 1]；
从左端起只保留必要的邻域，剩下有限个；对比 (0, 1) 被 (1/n, 1) 覆盖，任意有限个都在左端留缺口。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("6.5", "有限覆盖：从无穷多个邻域中挑出有限个", "Finite subcover: finitely many neighbourhoods suffice")
        ax = Axes(x_range=[0, 1, 0.25], y_range=[-0.15, 0.4, 0.1], x_length=10, y_length=5, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 18}).shift(DOWN * 0.4)
        # 与程序 6.5.1 相同：两节连杆（0.425 m、0.392 m）关节角由 (10°, 100°) 匀速变到 (80°, 20°)，障碍点 (0.36, 0.62) m
        L1, L2, A, B, O = 0.425, 0.392, np.radians([10, 100]), np.radians([80, 20]), (0.36, 0.62)
        W = B - A
        K = (L1 + L2) * abs(W[0]) + L2 * abs(W[1])

        def d(t):
            t1, t2 = A + W * t
            x, y = L1 * np.cos(t1) + L2 * np.cos(t1 + t2), L1 * np.sin(t1) + L2 * np.sin(t1 + t2)
            return float(np.hypot(x - O[0], y - O[1]))
        curve = ax.plot(d, x_range=[0, 1], color=WHITE, stroke_width=3)
        self.play(Create(ax), Create(curve))
        self.caption("每个时刻 t 有一个安全邻域，半径 d(t)/K", "Each time t has a safe neighbourhood of radius d(t)/K", wait=0.2)
        many = VGroup()
        for k, t in enumerate(np.linspace(0, 1, 41)):
            r = d(t) / K
            y = -0.02 - 0.0025 * (k % 40)
            many.add(Line(ax.c2p(max(0, t - r), y), ax.c2p(min(1, t + r), y), color=GREEN, stroke_width=2, stroke_opacity=0.5))
        self.play(LaggedStart(*[Create(m) for m in many], lag_ratio=0.05), run_time=3)
        self.caption("无穷多个邻域盖住 [0, 1]", "Infinitely many neighbourhoods cover [0, 1]", wait=0.3)
        keep, t, k = VGroup(), 0.0, 0
        while True:
            r = d(t) / K
            y = -0.05 - 0.02 * (k % 3)
            keep.add(Line(ax.c2p(max(0, t - r), y), ax.c2p(min(1, t + r), y), color=GREEN, stroke_width=7))
            k += 1
            if t + r > 1:
                break
            t += 0.9 * r
        self.play(FadeOut(many), LaggedStart(*[Create(m) for m in keep], lag_ratio=0.3), run_time=3)
        self.caption(f"挑出 {k} 个，仍然盖住 [0, 1]", f"{k} of them still cover [0, 1]", wait=0.5)
        self.play(*[FadeOut(m) for m in (ax, curve, keep)])
        nl = NumberLine(x_range=[0, 1, 0.25], length=10, include_numbers=True, font_size=22).shift(UP * 0.6)
        self.play(Create(nl))
        ints = VGroup()
        for j, nn in enumerate((2, 3, 4, 6, 10, 20)):
            ints.add(Line(nl.n2p(1 / nn), nl.n2p(1), color=GREEN, stroke_width=6).shift(DOWN * (0.35 + 0.22 * j)))
        self.play(LaggedStart(*[Create(m) for m in ints], lag_ratio=0.3), run_time=2.5)
        gap = Line(nl.n2p(0), nl.n2p(1 / 20), color=RED, stroke_width=8).shift(DOWN * 1.9)
        self.play(Create(gap))
        self.caption("开区间 (0, 1) 被 (1/n, 1) 覆盖，任意有限个都在左端留下缺口", "(0, 1) is covered by (1/n, 1), but any finitely many leave a gap at the left")
        self.play(*[FadeOut(m) for m in (nl, ints, gap)])
        self.card([["有限覆盖定理", "Heine–Borel theorem"],
                   ["闭区间的任一开覆盖都有有限子覆盖", "Every open cover of a closed interval has a finite subcover"],
                   ["有限次检查就能对无穷多个时刻作出保证", "Finitely many checks can guarantee infinitely many instants"]])
