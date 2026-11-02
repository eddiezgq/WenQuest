"""动画 57.2.1（配图 57.2.1）：从最后一道往前推工序尺寸（式 57.2.1）——SH-101 轴承位：图纸 Ø25 k6 的公差带（25.002–25.015），
加磨削的最小余量 0.325 和半精车公差 0.05、往大取整，得半精车 Ø25.4 0/−0.05；再加半精车的最小余量 0.8 和粗车公差 0.2、
取整到 0.5，得粗车 Ø26.5 0/−0.2；最后核算两段余量的最小值（0.335 ≥ 0.325，0.90 ≥ 0.80）。"""
from manim import *
from wq_anim import *
import numpy as np

X0, S = 25.0, 4.2           # 直径 25.0 画在 x = -5，1 mm = 4.2 单位


def xx(d):
    return -5 + (d - X0) * S


class Lesson(Base):
    def construct(self):
        self.title("57.2", "从最后一道往前推工序尺寸", "Working the operation sizes back from the last operation")
        axis = NumberLine(x_range=[25.0, 27.0, 0.5], length=2.0 * S, include_numbers=False, color=MUTED).move_to(np.array([xx(26.0), -1.9, 0]))
        nums = VGroup(*[zh(f"{d:.1f}", 18, MUTED).move_to(np.array([xx(d), -2.2, 0])) for d in (25.0, 25.5, 26.0, 26.5, 27.0)])
        self.play(Create(axis), FadeIn(nums))

        def band(lo, hi, y, c, text):
            r = Rectangle(width=max((hi - lo) * S, 0.05), height=0.5, color=c, fill_opacity=0.7, stroke_width=1).move_to(np.array([xx((lo + hi) / 2), y, 0]))
            t = zh(text, 20, c).next_to(r, RIGHT, buff=0.15)
            return VGroup(r, t)

        g = band(25.002, 25.015, -1.0, ORANGE, "磨削 Ø25 k6：25.002–25.015")
        self.play(FadeIn(g))
        self.caption("最后一道的尺寸就是图纸尺寸", "The last size is the drawing size")
        a = Arrow(np.array([xx(25.015), -0.5, 0]), np.array([xx(25.34), -0.5, 0]), buff=0, color=WHITE, stroke_width=3)
        self.play(GrowArrow(a), FadeIn(zh("+ 磨削最小余量 0.325", 18, WHITE).next_to(a, UP, buff=0.05)))
        s2 = band(25.35, 25.4, 0.2, STEEL, "半精车 Ø25.4 0/−0.05")
        self.play(FadeIn(s2))
        self.caption("A₂ ≥ 25.015 + 0.325 + 0.05 = 25.39，取整为 Ø25.4 0/−0.05（入体）", "A₂ ≥ 25.39 → Ø25.4")
        b = Arrow(np.array([xx(25.4), 0.7, 0]), np.array([xx(26.2), 0.7, 0]), buff=0, color=WHITE, stroke_width=3)
        self.play(GrowArrow(b), FadeIn(zh("+ 半精车最小余量 0.8", 18, WHITE).next_to(b, UP, buff=0.05)))
        s1 = band(26.3, 26.5, 1.4, GREEN, "粗车 Ø26.5 0/−0.2")
        self.play(FadeIn(s1))
        self.caption("A₁ ≥ 25.4 + 0.8 + 0.2 = 26.4，取整到 0.5 为 Ø26.5 0/−0.2", "A₁ ≥ 26.4 → Ø26.5")
        c1 = DoubleArrow(np.array([xx(25.015), -1.45, 0]), np.array([xx(25.35), -1.45, 0]), buff=0, color=YELLOW, stroke_width=3, tip_length=0.15)
        c2 = DoubleArrow(np.array([xx(25.4), 2.0, 0]), np.array([xx(26.3), 2.0, 0]), buff=0, color=YELLOW, stroke_width=3, tip_length=0.15)
        self.play(Create(c1), Create(c2))
        self.caption("核算：磨削余量最小 0.335 ≥ 0.325，半精车余量最小 0.90 ≥ 0.80", "Check: 0.335 ≥ 0.325, 0.90 ≥ 0.80")
        self.card([["前一道尺寸 ≥ 后一道最大尺寸 + 后一道最小余量 + 前一道公差", "A_prev ≥ A_max + 2Z_min + T_prev"],
                   ["往大取整，按入体原则标注，最后核算余量", "Round up, tolerance into the material, check the stock"]])
