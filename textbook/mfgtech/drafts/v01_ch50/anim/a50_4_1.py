"""动画 50.4.1（配图 50.4.1）：粗基准只用一次——先用毛坯外圆夹住、钻出中心孔，以后各道精加工都以中心孔为精基准。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("50.4", "粗基准与精基准", "Rough and finish datums")
        axis = DashedLine(LEFT * 6, RIGHT * 6, color=MUTED, dash_length=0.15)
        bar = Rectangle(width=8, height=2.2, fill_color=GREY_B, fill_opacity=1, stroke_color=INK).shift(DOWN * 0.05 + UP * 0.05)
        bent = bar.copy().apply_function(lambda p: p + np.array([0, 0.12 * (1 - (p[0] / 4) ** 2), 0]))
        self.play(FadeIn(bent), Create(axis))
        self.caption("热轧棒料表面粗糙、略有弯曲：它是唯一能用的定位面", "A hot-rolled bar is rough and slightly bent, yet it is the only surface to locate on")
        jaws = VGroup(*[Rectangle(width=1.2, height=0.5, fill_color="#d98c3a", fill_opacity=1, stroke_color=INK).move_to(np.array([-3.6, s * 1.45, 0]))
                        for s in (1, -1)])
        self.play(FadeIn(jaws, shift=RIGHT * 0.3))
        self.caption("20 粗车：三爪卡盘夹外圆（粗基准），车端面、钻中心孔", "20 Rough turning: a chuck grips the OD (rough datum); face and centre-drill")
        hole = Triangle(fill_color=BG, fill_opacity=1, stroke_color=INK).scale(0.25).rotate(PI / 2).move_to(np.array([3.85, 0, 0]))       # 锥尖朝向工件内部
        self.play(FadeIn(hole))
        hole2 = hole.copy().rotate(PI).move_to(np.array([-3.85, 0, 0]))
        self.caption("调头再夹一次，钻另一端中心孔：两个中心孔连成的直线就是以后的基准", "Turn it round and centre-drill the other end: the line through both holes becomes the datum")
        self.play(FadeOut(jaws), FadeIn(hole2))
        straight = bar.copy().set_fill("#3a7dc9")
        c1 = Triangle(fill_color=STEEL, fill_opacity=1, stroke_color=INK).scale(0.4).rotate(-PI / 2).move_to(np.array([-4.5, 0, 0]))
        c2 = c1.copy().rotate(PI).move_to(np.array([4.5, 0, 0]))
        self.play(FadeIn(c1, shift=RIGHT * 0.3), FadeIn(c2, shift=LEFT * 0.3))
        self.caption("40 精车、60 磨削都用两顶尖装夹：同一个精基准，各外圆同轴", "40 Finish turning and 60 grinding both run between centres: one finish datum, concentric seats")
        self.play(Transform(bent, straight), run_time=2)
        self.caption("粗基准只用一次；精基准统一，减少基准转换误差", "Use the rough datum once; keep one finish datum to avoid datum-shift errors")
        self.card([["粗基准：只用一次，选不加工或余量最小、最平整的表面", "Rough datum: use once; pick the surface left as-is or with least stock"],
                   ["精基准：基准重合、基准统一", "Finish datum: coincide with the design datum, and keep it the same"]])
