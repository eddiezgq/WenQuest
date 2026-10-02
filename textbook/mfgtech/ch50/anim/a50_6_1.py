"""动画 50.6.1（配图 50.6.1）：余量为什么是一个范围——上下两道工序的公差带之间的空隙。"""
from manim import *
from wq_anim import *
import numpy as np

S = 6.0          # 1 mm 直径 → 6 个画面单位（只画 35.0–36.6 一段）


def X(d):
    return (d - 35.6) * S


def band(lo, hi, y, color, name):
    r = Rectangle(width=(hi - lo) * S, height=0.5, fill_color=color, fill_opacity=0.9, stroke_width=0)
    r.move_to(np.array([(X(lo) + X(hi)) / 2, y, 0]))
    t = zh(name, 24, INK).next_to(r, LEFT, buff=0.25)
    return VGroup(r, t)


class Lesson(Base):
    def construct(self):
        self.title("50.6", "余量的最小值与最大值", "Minimum and maximum stock")
        ax = NumberLine(x_range=[35.0, 36.6, 0.2], length=1.6 * S, include_numbers=True, decimal_number_config={"num_decimal_places": 1},
                        font_size=22, color=MUTED).move_to(np.array([X(35.8), -2.4, 0]))
        self.play(Create(ax))
        g = band(35.002, 35.018, -1.4, "#2f8f5b", "磨削 Ø35k6")
        self.caption("最后一道工序（磨削）的尺寸就是图纸尺寸 Ø35k6", "The last operation (grinding) is held to the drawing size, Ø35k6")
        self.play(FadeIn(g))
        f = band(35.261, 35.300, 0.0, "#3a7dc9", "精车 Ø35.3h8")
        self.caption("前一道（精车）做成 Ø35.3，公差 IT8：上偏差 0、下偏差 −0.039", "The previous operation (finish turning) is Ø35.3 with IT8: 0 / −0.039")
        self.play(FadeIn(f))
        zmin = DoubleArrow(np.array([X(35.018), -0.7, 0]), np.array([X(35.261), -0.7, 0]), buff=0, color=YELLOW, stroke_width=3)
        lab1 = zh("最小余量 0.243", 22, YELLOW).next_to(zmin, UP, buff=0.08)
        self.caption("精车做得最小、磨削做得最大时，磨削切得最少", "Least grinding stock: finish turning at its smallest, grinding at its largest")
        self.play(GrowFromCenter(zmin), Write(lab1))
        zmax = DoubleArrow(np.array([X(35.002), -1.0, 0]), np.array([X(35.300), -1.0, 0]), buff=0, color=ORANGE, stroke_width=3)
        lab2 = zh("最大余量 0.298", 22, ORANGE).next_to(zmax, DOWN, buff=0.08)
        self.caption("反过来，精车最大、磨削最小时切得最多：余量的变动量 = 两道公差之和", "The other way round it cuts the most: the spread equals the two tolerances added")
        self.play(GrowFromCenter(zmax), Write(lab2))
        self.wait(1)
        need = Line(np.array([X(35.018 + 0.145), -1.75, 0]), np.array([X(35.018 + 0.145), 0.35, 0]), color=RED, stroke_width=3)
        lab3 = zh("必须切掉的最少量 0.145", 22, RED).next_to(need, UP, buff=0.1)
        self.caption("最小余量要能切掉上道留下的粗糙度、缺陷层和变形：它决定了精车尺寸往哪里放", "The minimum must remove the previous roughness, damaged layer and distortion; it decides where the finish size goes")
        self.play(Create(need), Write(lab3))
        self.wait(1)
        self.card([["从最后一道往前推：A₂ ≥ d_max + 2Z_min + T₂", "Work backwards: A₂ ≥ d_max + 2Z_min + T₂"],
                   ["余量的最小值保证“有东西可切”，最大值决定工时和风险", "The minimum guarantees something to cut; the maximum sets time and risk"]])
