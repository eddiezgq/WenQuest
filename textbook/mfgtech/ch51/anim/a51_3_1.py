"""动画 51.3.1（配图 51.3.1）：六点定位——底面三点、侧面两点、端面一点，依次限制工件的六个自由度。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("51.3", "六点定位原理", "The six-point locating principle")
        d = np.array([1.2, 0.7, 0])                      # 斜二测的进深方向
        f0 = np.array([-2.2, -1.0, 0])
        front = Polygon(f0, f0 + RIGHT * 4.4, f0 + RIGHT * 4.4 + UP * 1.6, f0 + UP * 1.6, fill_color=STEEL, fill_opacity=0.25, stroke_color=INK)
        top = Polygon(f0 + UP * 1.6, f0 + RIGHT * 4.4 + UP * 1.6, f0 + RIGHT * 4.4 + UP * 1.6 + d, f0 + UP * 1.6 + d, fill_color=STEEL, fill_opacity=0.15, stroke_color=INK)
        side = Polygon(f0 + RIGHT * 4.4, f0 + RIGHT * 4.4 + d, f0 + RIGHT * 4.4 + d + UP * 1.6, f0 + RIGHT * 4.4 + UP * 1.6, fill_color=STEEL, fill_opacity=0.35, stroke_color=INK)
        box = VGroup(front, top, side)
        self.play(Create(box))
        self.caption("一个自由的工件有六个自由度：沿 x、y、z 移动，绕 x、y、z 转动", "A free workpiece has six degrees of freedom: three translations and three rotations")
        counter = readout("限制的自由度", "0")
        counter.to_corner(UR)
        self.play(FadeIn(counter))
        steps = [(3, "底面三点（不共线，围成三角形）：限制沿 z 移动、绕 x 和绕 y 转动", "Three points below (not in a line, forming a triangle): z, rotations about x and y", BLUE, f0 + RIGHT * 2.2 + DOWN * 0.25),
                 (2, "背面两点：限制沿 y 移动、绕 z 转动", "Two points at the back: y and rotation about z", ORANGE, f0 + RIGHT * 2.2 + d + UP * 0.8),
                 (1, "端面一点：限制沿 x 移动", "One point at the end: x", RED, f0 + LEFT * 0.3 + UP * 0.8)]
        # 底面三点不在一条直线上，围成尽量大的三角形（两点靠近前棱，一点靠里），才能稳定地限制两个转动
        tri = [f0 + RIGHT * 0.8 + d * 0.2, f0 + RIGHT * 3.6 + d * 0.2, f0 + RIGHT * 2.2 + d * 0.8]
        total = 0
        for n, zh_t, en_t, col, pos in steps:
            if n == 3:
                dots = VGroup(*[Dot(q + DOWN * 0.25, color=col, radius=0.12) for q in tri])
                dots.add(Polygon(*[q + DOWN * 0.25 for q in tri], stroke_color=col, stroke_width=2, fill_opacity=0))
            else:
                dots = VGroup(*[Dot(pos + RIGHT * 0.6 * (i - (n - 1) / 2), color=col, radius=0.12) for i in range(n)])
            self.play(FadeIn(dots, scale=1.5))
            total += n
            self.play(Transform(counter, readout("限制的自由度", str(total)).to_corner(UR)))
            self.caption(zh_t, en_t)
        self.caption("六个点各限制一个自由度，工件位置唯一确定：完全定位", "Six points, one freedom each: the position is fully determined")
        self.card([["支承点按“3–2–1”布置：面积最大的面三点，最长的面两点，另一面一点", "Arrange 3–2–1: three on the largest face, two on the longest, one on the third"],
                   ["工序要求不需要限制的自由度，可以不限制：不完全定位", "Freedoms the operation does not need can stay free: partial location"]])
