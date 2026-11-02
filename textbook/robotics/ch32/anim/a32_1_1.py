"""动画 32.1.1（配图 32.1.1）：齿轮啮合与背隙。
(1) WQR-105 第一级：24 齿的输入齿轮带动 72 齿的大齿轮，转速降为 1/3（画面上齿形简化）；接触点沿啮合线移动。
(2) 侧隙：输入齿轮反向时，大齿轮先停在原处，等输入齿轮转过侧隙（放大画）才跟着反向——背隙。
(3) 两级串联：第一级的背隙在中间轴上，经第二级缩小 3.5 倍；输出轴的背隙主要来自最后一级（算例 32.1.3：5.3～12.3 角分）。"""
from manim import *
from wq_anim import *
import numpy as np


def gear(r, z, color, phase=0.0, depth=0.12):
    pts = []
    for k in range(z):
        for u, rr in ((0.0, r - depth), (0.2, r + depth), (0.5, r + depth), (0.7, r - depth)):
            a = phase + 2 * np.pi * (k + u) / z
            pts.append([rr * np.cos(a), rr * np.sin(a), 0])
    return Polygon(*pts, color=color, stroke_width=2, fill_opacity=0.25)


class Lesson(Base):
    def construct(self):
        self.title("32.1", "齿轮啮合与背隙", "Gear mesh and backlash")
        r1, r2 = 0.8, 2.4
        c1, c2 = np.array([-3.8, 0.2, 0]), np.array([-3.8 + r1 + r2, 0.2, 0])
        a1, a2 = ValueTracker(0.0), ValueTracker(0.0)
        g1 = always_redraw(lambda: gear(r1, 24, RED, a1.get_value()).move_to(c1))
        g2 = always_redraw(lambda: gear(r2, 72, BLUE, a2.get_value() + np.pi / 72).move_to(c2))
        self.add(g1, g2, Dot(c1), Dot(c2))
        lab = VGroup(zh("SH-101 · 24 齿", 22, RED).next_to(c1, DOWN, buff=1.1), zh("GR-202 · 72 齿", 22, BLUE).next_to(c2, DOWN, buff=2.7))
        self.add(lab)
        line = Line(c1 + np.array([r1, 0, 0]) + np.array([-0.6, -1.6, 0]) * 0.5, c1 + np.array([r1, 0, 0]) + np.array([0.6, 1.6, 0]) * 0.5,
                    color=YELLOW, stroke_width=3)
        self.play(Create(line))
        self.play(a1.animate.set_value(2 * np.pi), a2.animate.set_value(-2 * np.pi / 3), run_time=4, rate_func=linear)
        self.caption("小齿轮转一圈，大齿轮转 1/3 圈：i = 72/24 = 3；接触点总在啮合线（黄）上",
                     "One turn of the pinion, a third of a turn of the gear: i = 72/24 = 3; contact stays on the line of action", wait=1.0)
        # (2) 背隙
        gap = 0.25
        self.play(a1.animate.set_value(2 * np.pi - gap), run_time=1.5, rate_func=linear)
        t = VGroup(zh("输入反向：大齿轮先不动", 24, ORANGE), zh("齿要先走过侧隙", 24, ORANGE)).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT).shift(UP * 0.8)
        fit(t, 4.4)
        self.play(FadeIn(t))
        self.play(a1.animate.set_value(2 * np.pi - gap - 1.0), a2.animate.set_value(-2 * np.pi / 3 + 1.0 / 3), run_time=1.5, rate_func=linear)
        self.caption("侧隙让齿轮转向时“空走”一段：背隙。WQR-105 的输出轴约 5～12 角分",
                     "The clearance gives a dead travel on reversal: backlash, about 5–12 arcmin at WQR-105's output", wait=1.0)
        self.clear_stage()
        rows = VGroup(zh("第一级：中间轴上 5.1～11.2′ → ÷3.5 → 输出轴 1.5～3.2′", 26, INK),
                      zh("第二级：输出轴上 3.8～9.1′", 26, INK),
                      zh("合计 5.3～12.3′：背隙主要看最后一级", 28, YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        fit(rows, 12)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rows], lag_ratio=0.5), run_time=2.5)
        self.wait(1.0)
        self.card([["齿轮传动基础", "Gear basics"],
                   ["传动比 = 齿数比的连乘；转矩乘以效率", "Ratio = product of tooth ratios; torque times efficiency"],
                   ["背隙来自侧隙，主要看最后一级", "Backlash comes from clearance, mostly in the last stage"],
                   ["普通齿轮减速器几角分到十几角分，机器人关节要 1 角分以下", "Ordinary gearboxes: several arcmin; robot joints need under 1"]])
