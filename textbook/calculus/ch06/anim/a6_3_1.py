"""动画 6.3.1（配图 6.3.1）：致密性定理——sin n 的点落在 [−1, 1] 上；二分，保留点多的一半；
区间缩向 ξ，每一步在更后面挑出一项，组成收敛于 ξ 的子数列。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("6.3", "致密性定理：有界数列必有收敛子数列", "Bolzano–Weierstrass: a bounded sequence has a convergent subsequence")
        ax = Axes(x_range=[0, 1000, 200], y_range=[-1, 1, 0.5], x_length=10, y_length=5, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 18}).shift(DOWN * 0.4 + RIGHT * 0.3)
        self.play(Create(ax))
        n = np.arange(1, 1001)
        s = np.sin(n)
        dots = VGroup(*[Dot(ax.c2p(k, v), radius=0.022, color=GREY_B) for k, v in zip(n, s)])
        self.play(LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.004), run_time=3)
        self.caption("sin n 在 [−1, 1] 中跳来跳去，不收敛", "sin n jumps around in [−1, 1] and does not converge", wait=0.3)
        a, b = -1.0, 1.0
        band = Rectangle(width=ax.c2p(1000, 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, b)[1] - ax.c2p(0, a)[1],
                         stroke_width=0, fill_color=STEEL, fill_opacity=0.18).move_to(ax.c2p(500, 0))
        self.add(band)
        picks, last = [], 0
        target = 0.3      # 两半都含无穷多项时任选一半；这里总选含 0.3 的一半
        for k in range(5):
            m = (a + b) / 2
            a, b = (a, m) if target <= m else (m, b)
            nb = Rectangle(width=band.width, height=ax.c2p(0, b)[1] - ax.c2p(0, a)[1], stroke_width=0,
                           fill_color=STEEL, fill_opacity=0.18).move_to(ax.c2p(500, (a + b) / 2))
            idx = [i for i in range(last, 1000) if a <= s[i] <= b]
            if not idx:
                break
            last = idx[0] + 1
            picks.append(dots[idx[0]])
            self.play(Transform(band, nb), dots[idx[0]].animate.set_color(RED).scale(2.2), run_time=1)
        self.caption("每次保留含无穷多项的一半（两半都是时任选其一），并在更后面挑出一项", "Keep the half with infinitely many terms; pick a later term each time", wait=0.4)
        line = VMobject(color=RED).set_points_as_corners([p.get_center() for p in picks])
        self.play(Create(line))
        xi = DashedLine(ax.c2p(0, (a + b) / 2), ax.c2p(1000, (a + b) / 2), color=YELLOW)
        lab = MathTex(r"\xi", color=YELLOW, font_size=36).next_to(ax.c2p(1000, (a + b) / 2), RIGHT, buff=0.1)
        self.play(Create(xi), FadeIn(lab))
        self.caption("区间缩向一点 ξ，挑出的子数列收敛于 ξ", "The intervals shrink to ξ; the chosen subsequence converges to ξ")
        self.play(*[FadeOut(m) for m in (ax, dots, band, line, xi, lab)])
        self.card([["致密性定理", "Bolzano–Weierstrass theorem"],
                   ["有界数列必有收敛的子数列", "Every bounded sequence has a convergent subsequence"],
                   ["证明：二分 + 闭区间套；只保证存在，不说收敛到哪里", "Proof: bisection + nested intervals; existence only"]])
