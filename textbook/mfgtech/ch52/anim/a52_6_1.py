"""动画 52.6.1（配图 52.6.4）：钻套怎样引导钻头——间隙让钻头偏移和歪斜，钻套离工件越远，孔位误差越大。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("52.6", "钻套引导钻头", "How a drill bushing guides the drill")
        plate = Rectangle(width=5.0, height=0.6, fill_color=STEEL, fill_opacity=0.25, stroke_color=INK).move_to(UP * 1.4)
        bush_l = Rectangle(width=0.5, height=1.6, fill_color=BLUE, fill_opacity=0.35, stroke_color=BLUE).move_to(LEFT * 0.75 + UP * 1.2)
        bush_r = bush_l.copy().move_to(RIGHT * 0.75 + UP * 1.2)
        work = Rectangle(width=5.0, height=0.6, fill_color=STEEL, fill_opacity=0.15, stroke_color=INK).move_to(DOWN * 1.6)
        self.play(FadeIn(plate), FadeIn(bush_l), FadeIn(bush_r), FadeIn(work))
        axis = DashedLine(UP * 2.6, DOWN * 2.2, color=MUTED)
        self.add(axis)
        self.caption("钻套装在钻模板上，位置由钻模的制造精度保证", "The bushing sits in the jig plate; its position is set when the jig is made")
        drill = Rectangle(width=0.9, height=4.0, fill_color=RED, fill_opacity=0.3, stroke_color=RED).move_to(UP * 0.3)
        self.play(FadeIn(drill))
        self.caption("钻头与钻套之间有间隙 X，钻头可以偏到一侧", "There is a clearance X; the drill can shift to one side")
        self.play(drill.animate.shift(RIGHT * 0.08), run_time=1)
        self.play(Rotate(drill, angle=-0.05, about_point=drill.get_center()), run_time=1.2)
        self.caption("最坏时上端靠一侧、下端靠另一侧：钻头歪斜 X/H", "Worst case: top against one side, bottom against the other — tilt X/H")
        gap = DoubleArrow(np.array([2.0, 0.4, 0]), np.array([2.0, -1.3, 0]), color=INK, buff=0)
        s_lab = MathTex("s", color=INK).next_to(gap, RIGHT)
        self.play(GrowFromCenter(gap), Write(s_lab))
        self.caption("钻尖到工件时偏离 X/2 + s·X/H：s 越大越偏", "At the work the point is off by X/2 + s·X/H: the larger s, the worse")
        self.card([["钻套离工件的距离 s 一般取 (0.3–1)d：太近排屑难，太远引偏大", "Keep the bushing (0.3–1)d from the work: too close traps chips, too far lets the drill wander"],
                   ["钻套导向长度 H 取 (1–2.5)d；精度要求高时用长钻套、小间隙", "Guide length H of (1–2.5)d; for precision use longer bushings and tighter clearance"]])
