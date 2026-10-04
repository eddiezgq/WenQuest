"""动画 53.1.1（配图 53.1.1）：尺寸链——环一个接一个连成封闭回路；增环变大，封闭环跟着变大，减环变大，封闭环变小。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("53.1", "尺寸链：增环与减环", "Dimension chains: increasing and decreasing links")
        y1, y2, y0 = 1.2, 0.2, -1.0
        a1 = ValueTracker(5.0)
        a2 = ValueTracker(2.0)

        def bar(x0, x1, y, col, name):
            ln = Arrow(np.array([x0, y, 0]), np.array([x1, y, 0]), buff=0, color=col, stroke_width=5)
            lab = MathTex(name, color=col).scale(0.8).next_to(ln, UP, buff=0.08)
            return VGroup(ln, lab)

        def chain():
            L1, L2 = a1.get_value(), a2.get_value()
            x0 = -3.0
            g = VGroup(bar(x0, x0 + L1, y1, ORANGE, "A_1"), bar(x0 + L1, x0 + L1 - L2, y2, BLUE, "A_2"),
                       bar(x0 + L1 - L2, x0, y0, INK, "A_0"))         # 封闭环从 A2 的终点指回起点，三个箭头首尾相接成回路
            g.add(DashedLine(np.array([x0, y1 + 0.4, 0]), np.array([x0, y0 - 0.3, 0]), color=MUTED))
            g.add(DashedLine(np.array([x0 + L1, y1 + 0.4, 0]), np.array([x0 + L1, y2 - 0.3, 0]), color=MUTED))
            g.add(DashedLine(np.array([x0 + L1 - L2, y2 + 0.4, 0]), np.array([x0 + L1 - L2, y0 - 0.3, 0]), color=MUTED))
            return g

        cg = always_redraw(chain)
        self.play(FadeIn(cg))
        self.caption("A1、A2 是加工中直接得到的组成环，A0 是最后间接形成的封闭环", "A1 and A2 are made directly; A0 is what results — the closing link")
        self.caption("回路法：A1 → A2 → A0 首尾相接；A2 与 A0 同向（都向左），是减环；A1 反向，是增环", "Loop rule: A1 → A2 → A0 head to tail; A2 points the same way as A0 (left) — decreasing; A1 opposite — increasing")
        self.play(a1.animate.set_value(5.8), run_time=2)
        self.caption("A1 变大，A0 跟着变大：A1 是增环", "A1 grows and A0 grows: A1 is an increasing link")
        self.play(a1.animate.set_value(5.0), run_time=1)
        self.play(a2.animate.set_value(2.8), run_time=2)
        self.caption("A2 变大，A0 反而变小：A2 是减环", "A2 grows and A0 shrinks: A2 is a decreasing link")
        eq = MathTex(r"A_0 = A_1 - A_2,\quad T_0 = T_1 + T_2", color=INK).to_edge(DOWN)
        self.play(Write(eq))
        self.caption("封闭环的公差是各组成环公差之和：环越多，每一环分到的公差越少", "The closing tolerance is the sum of the link tolerances: more links, less for each")
        self.card([["先找封闭环：加工中最后间接形成的那个尺寸", "Find the closing link first: the one that results indirectly"],
                   ["尺寸链要最短：每多一环，其他环的公差就要再压一点", "Keep the chain short: every extra link squeezes the others"]])
