"""动画 5.1.1（配图 5.1.1）：AGV 原地转向，航向指针连续转动；航向读数取主值，越过 ±π 时跳变；
差商估计的角速度出现尖峰；解卷绕把读数接回连续的曲线（5.2.4 节）。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("5.1", "连续与跳变：AGV 的航向读数", "Continuity and jumps: an AGV's heading reading")
        th0, w = 2.5, 0.5
        t = ValueTracker(0)
        C = LEFT * 4.6 + DOWN * 0.3
        ring = Circle(radius=1.5, color=GREY_B).move_to(C)
        cut = DashedLine(C, C + LEFT * 1.8, color=RED)
        pi_lab = MathTex(r"\pm\pi", font_size=30, color=RED).next_to(C + LEFT * 1.8, LEFT, buff=0.1)
        arrow = always_redraw(lambda: Arrow(C, C + 1.4 * np.array([np.cos(th0 + w * t.get_value()), np.sin(th0 + w * t.get_value()), 0]),
                                            buff=0, color=STEEL, stroke_width=6))
        self.play(Create(ring), Create(cut), FadeIn(pi_lab), GrowArrow(arrow))
        ax = Axes(x_range=[0, 16, 4], y_range=[-4, 11, 2], x_length=7, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 18}).shift(RIGHT * 2.4 + DOWN * 0.4)
        self.play(Create(ax))
        true = always_redraw(lambda: ax.plot(lambda s: th0 + w * s, x_range=[0, max(t.get_value(), 1e-3)], color=GREY_B, stroke_width=2))

        def rd(s):
            v = th0 + w * s
            return np.arctan2(np.sin(v), np.cos(v))

        jt = [((np.pi - th0) + 2 * np.pi * k) / w for k in range(2)]      # 越过 π 的时刻

        def reading():
            T = t.get_value()
            edges = [0.0] + [s for s in jt if s < T] + [T]
            g = VGroup()
            for a, b in zip(edges, edges[1:]):
                if b - a > 2e-3:
                    g.add(ax.plot(rd, x_range=[a + 1e-3, b - 1e-3], color=STEEL, stroke_width=4))
            return g
        rline = always_redraw(reading)
        self.add(true, rline)
        self.caption("真实航向连续增大；读数取主值 (−π, π]", "The true heading grows continuously; the reading is the principal value", wait=0.2)
        self.play(t.animate.set_value(16), run_time=8, rate_func=linear)
        jumps = VGroup(*[Circle(radius=0.25, color=RED).move_to(ax.c2p(s, 0)) for s in jt])
        self.play(Create(jumps))
        self.caption("越过 ±π 时读数跳变约 2π：差商算出约 −314 rad/s", "At ±π the reading jumps by about 2π: the difference quotient gives about −314 rad/s", wait=0.8)
        unw = ax.plot(lambda s: th0 + w * s, x_range=[0, 16], color=GREEN, stroke_width=5)
        rline.clear_updaters()
        self.play(FadeOut(jumps), Create(unw), rline.animate.set_opacity(0.3), run_time=2)
        self.caption("解卷绕：每次跳变补上 ±2π，读数接回连续的曲线", "Unwrapping: add ±2π at each jump to restore a continuous curve")
        true.clear_updaters()
        arrow.clear_updaters()
        self.play(*[FadeOut(m) for m in (ring, cut, pi_lab, arrow, ax, true, rline, unw)])
        self.card([["在一点连续", "Continuity at a point"],
                   MathTex(r"\lim_{x\to a}f(x)=f(a)", font_size=52),
                   ["输入差一点，输出也只差一点；差商、导数、积分都要求函数不跳", "A small input change gives a small output change; rates, derivatives and integrals need it"]])
