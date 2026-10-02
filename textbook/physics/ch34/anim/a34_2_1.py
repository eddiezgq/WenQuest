"""动画 34.2.1（配图 34.2.1）：楞次定律。N 极靠近线圈时，感应电流的磁场 B′ 与磁铁的磁场相反，线圈像一个
N 极朝外的小磁铁推斥磁铁；N 极离开时 B′ 反向，线圈吸引磁铁。阻碍的是“变化”。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("34.2", "楞次定律：阻碍变化", "Lenz's law: opposing the change")
        coil = Ellipse(width=0.4, height=1.8, color=ORANGE, stroke_width=6).move_to(RIGHT * 1.5)
        s = Rectangle(width=0.8, height=0.4, fill_color=BLUE, fill_opacity=1, stroke_width=1)
        n = Rectangle(width=0.8, height=0.4, fill_color=RED, fill_opacity=1, stroke_width=1).next_to(s, RIGHT, buff=0)
        mag = VGroup(s, n, Text("S", font_size=22).move_to(s), Text("N", font_size=22).move_to(n)).move_to(LEFT * 3.5)
        self.play(Create(coil), FadeIn(mag))
        B = vec(coil.get_center() + UP * 1.3 + LEFT * 0.6, coil.get_center() + UP * 1.3 + RIGHT * 0.6, BLUE, r"\boldsymbol B", UP)
        self.play(FadeIn(B))
        self.caption("磁铁静止：穿过线圈的磁通量不变，没有感应电流", "Magnet at rest: the flux is steady and there is no induced current")

        def induced(left):
            """B′ (left or right), the coil as an equivalent magnet, and the current on the coil's near side
            (B′ to the left: the near side carries the current upward, clockwise seen from the right)."""
            a, b = (RIGHT, LEFT) if left else (LEFT, RIGHT)
            bp = vec(coil.get_center() + DOWN * 1.3 + a * 0.6, coil.get_center() + DOWN * 1.3 + b * 0.6, GREEN, r"\boldsymbol B'", DOWN)
            cols = (RED, BLUE) if left else (BLUE, RED)
            gh = VGroup(*[Rectangle(width=0.5, height=0.3, fill_color=c, fill_opacity=0.5, stroke_width=0) for c in cols]
                        ).arrange(RIGHT, buff=0).move_to(coil)
            d = UP if left else DOWN
            cur = Arrow(coil.get_right() + RIGHT * 0.5 - d * 0.4, coil.get_right() + RIGHT * 0.5 + d * 0.4, buff=0,
                        color=YELLOW, stroke_width=5, max_tip_length_to_length_ratio=0.35)
            lab = MathTex("I", color=YELLOW, font_size=30).next_to(cur, RIGHT, buff=0.1)
            return VGroup(bp, gh, cur, lab)

        ind1 = induced(True)
        self.caption("N 极靠近，向右的磁通量增大：感应电流的磁场 B′ 向左，线圈左侧相当于 N 极，推斥磁铁",
                     "N pole approaching, rightward flux growing: the induced field B′ points left; the coil acts like an N pole and repels the magnet")
        self.play(mag.animate.shift(RIGHT * 2.2), FadeIn(ind1), run_time=3)
        self.play(FadeOut(ind1), run_time=0.6)
        self.caption("磁铁停下：磁通量不再变化，感应电流立即消失", "The magnet stops: the flux no longer changes and the induced current vanishes")
        ind2 = induced(False)
        self.caption("N 极离开，磁通量减小：B′ 改为向右，线圈吸引离开的磁铁", "N pole leaving, flux falling: B′ turns right and the coil attracts the receding magnet")
        self.play(mag.animate.shift(LEFT * 2.2), FadeIn(ind2), run_time=3)
        self.play(FadeOut(ind2), run_time=0.6)
        self.caption("阻碍的不是磁场本身，而是磁通量的变化", "What is opposed is not the field but its change")
        self.wait(1)
        self.card([["楞次定律", "Lenz's law"],
                   ["感应电流的磁场总是阻碍引起它的磁通量的变化", "The induced current's field always opposes the change of flux that causes it"],
                   ["推磁铁要做功，这份功变成了电能——能量守恒", "Pushing the magnet takes work, which becomes electrical energy: energy is conserved"]])
