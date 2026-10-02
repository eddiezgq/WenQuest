"""动画 5.1.1（配图 5.1.1）：点 P 不动，坐标系 {b} 平移并转动；P 在 {b} 中的坐标随之变化，矢量三角形始终闭合。"""
from manim import *
from wq_anim import *
import numpy as np
import math

U = 1.6                                   # 1 m 画成 1.6 个单位
OA = np.array([-4.6, -2.0, 0])            # {a} 的原点在屏幕上的位置
P = np.array([3.4, 2.75])                 # 点 P 在 {a} 中的坐标（m）


def scr(x):
    return OA + U * np.array([x[0], x[1], 0])


class Lesson(Base):
    def construct(self):
        self.title("5.1", "原点不同的两个坐标系", "Two frames with different origins")
        fa = frame2(OA, 0, 1.3, ("x_a", "y_a"), name=r"\{a\}")
        dotP = Dot(scr(P), color=YELLOW, radius=0.09)
        labP = MathTex("P", color=YELLOW).next_to(dotP, UR, buff=0.08)
        self.play(Create(fa), FadeIn(dotP), Write(labP))
        vaP = Arrow(OA, scr(P), buff=0, color=INK, stroke_width=4)
        pa = MathTex(r"p_a=(3.4,\ 2.75)", color=INK, font_size=32).to_corner(UR, buff=0.5).shift(DOWN * 0.9 + LEFT * 0.4)
        self.play(GrowArrow(vaP), Write(pa))
        self.caption("P 在 {a} 中的坐标：从 {a} 的原点指向 P 的箭头在 {a} 中的分量",
                     "P in {a}: components of the arrow from the origin of {a} to P")

        ox, oy, ang = ValueTracker(2.3), ValueTracker(0.8), ValueTracker(35.0)

        def ob():
            return np.array([ox.get_value(), oy.get_value()])

        def pb():
            t = math.radians(ang.get_value())
            d = P - ob()
            return np.array([math.cos(t) * d[0] + math.sin(t) * d[1], -math.sin(t) * d[0] + math.cos(t) * d[1]])

        fb = always_redraw(lambda: frame2(scr(ob()), ang.get_value(), 1.1, ("x_b", "y_b"), color=STEEL, name=r"\{b\}"))
        vab = always_redraw(lambda: Arrow(OA, scr(ob()), buff=0, color=GOLD, stroke_width=4))
        vbP = always_redraw(lambda: Arrow(scr(ob()), scr(P), buff=0, color=BLUE, stroke_width=4))
        readout = always_redraw(lambda: MathTex(r"p_b=(%.2f,\ %.2f)" % tuple(pb()), color=BLUE, font_size=32)
                                .next_to(pa, DOWN, buff=0.25, aligned_edge=LEFT))
        pab = always_redraw(lambda: MathTex(r"p_{ab}=(%.2f,\ %.2f)" % tuple(ob()), color=GOLD, font_size=32)
                            .next_to(readout, DOWN, buff=0.25, aligned_edge=LEFT))
        self.play(FadeIn(fb), GrowArrow(vab), GrowArrow(vbP), Write(readout), Write(pab))
        self.caption("三支箭头首尾相接，这个矢量等式与坐标系无关",
                     "The three arrows close head to tail, in every frame")

        self.caption("{b} 平移：P 没有动，但 P 在 {b} 中的坐标变了", "Move {b}: P stays, its coordinates in {b} change", wait=0)
        self.play(ox.animate.set_value(1.2), oy.animate.set_value(1.9), run_time=3, rate_func=smooth)
        self.wait(0.5)
        self.caption("{b} 转动：同一支蓝色箭头，在转过的坐标轴上读出不同的数", "Turn {b}: the same blue arrow, read on turned axes", wait=0)
        self.play(ang.animate.set_value(-20.0), run_time=3, rate_func=smooth)
        self.wait(0.5)
        self.caption("P 在 {a} 中的坐标始终不变；在 {b} 中的坐标由 {b} 的位置和朝向决定",
                     "P in {a} never changes; P in {b} depends on where {b} is and how it is turned")
        self.wait(1)
        self.card([["点的坐标变换", "Coordinates of a point"],
                   MathTex(r"p_a = R_{ab}\,p_b + p_{ab}", font_size=46),
                   MathTex(r"p_b = R_{ab}^{\mathsf T}\,(p_a - p_{ab})", font_size=40),
                   ["先转动，再加上原点之间的平移", "turn first, then add the offset between the origins"]])
