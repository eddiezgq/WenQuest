"""动画 1.4.1（配图 1.4.1）：尺度之旅。从 1 m 的机械臂出发，一级一级缩小或放大视野，看几个代表性数量级上的物体；
最后把它们排在同一条对数刻度上。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("1.4", "尺度之旅：10 的幂次", "A journey in powers of ten")
        down = [(0, "UR5e 工作半径约 1 m", "UR5e reach, about 1 m"), (-3, "1 mm：卡尺的刻度", "1 mm: a caliper division"),
                (-4, "头发直径约 0.1 mm", "a hair, about 0.1 mm"), (-6, "细菌约 1 μm", "a bacterium, about 1 μm"),
                (-9, "芯片里的鳍宽约几纳米", "a transistor fin, a few nm"), (-10, "原子约 0.1 nm", "an atom, about 0.1 nm"),
                (-15, "质子约 1 fm", "a proton, about 1 fm")]
        up = [(4, "珠穆朗玛峰约 9 km", "Everest, about 9 km"), (7, "地球直径约 1.3 × 10⁷ m", "Earth, about 1.3 × 10⁷ m"),
              (11, "日地距离约 1.5 × 10¹¹ m", "Earth–Sun, about 1.5 × 10¹¹ m"), (16, "1 光年约 10¹⁶ m", "a light-year, about 10¹⁶ m"),
              (21, "银河系约 10²¹ m", "the Milky Way, about 10²¹ m"), (27, "可观测宇宙直径约 10²⁷ m", "the observable universe, about 10²⁷ m across")]
        frame = Square(side_length=4.2, color=GREY_B, stroke_width=2).shift(UP * 0.3)
        self.play(Create(frame))

        def show(items, sign):
            prev = None
            for p, zh_, en_ in items:
                exp = MathTex(f"10^{{{p}}}\\ \\mathrm{{m}}", font_size=60, color=YELLOW).move_to(frame.get_center() + UP * 0.6)
                lab = VGroup(zh(zh_, 30), en(en_, 20)).arrange(DOWN, buff=0.1).move_to(frame.get_center() + DOWN * 0.8)
                grp = VGroup(exp, lab)
                if prev is None:
                    self.play(FadeIn(grp, scale=0.6 if sign < 0 else 1.6), run_time=0.8)
                else:
                    self.play(FadeOut(prev, scale=1.8 if sign < 0 else 0.5), FadeIn(grp, scale=0.5 if sign < 0 else 1.8), run_time=0.8)
                self.wait(0.4)
                prev = grp
            self.play(FadeOut(prev))

        self.caption("向小走：每到一个数量级停一停", "Going down: a stop at each order of magnitude", wait=0)
        show(down, -1)
        self.caption("向大走：每到一个数量级停一停", "Going up: a stop at each order of magnitude", wait=0)
        show(up, +1)
        self.play(FadeOut(frame))
        axis = NumberLine(x_range=[-16, 28, 5], length=12, include_numbers=False, color=GREY_B).shift(DOWN * 0.3)
        ticks = VGroup(*[MathTex(f"10^{{{x}}}", font_size=24).next_to(axis.n2p(x), DOWN, buff=0.15) for x in range(-15, 28, 5)])
        self.play(Create(axis), Write(ticks))
        dots = VGroup()
        for i, (p, zh_, en_) in enumerate(sorted(down + up)):
            d_ = Dot(axis.n2p(p), color=ORANGE)
            side, lev = (UP, DOWN)[i % 2], (i // 2) % 2           # 上下交替，每侧再分两层，避免文字重叠
            t = zh(zh_.split("约")[0].split("：")[-1].split("里的")[-1], 18).next_to(d_, side, buff=0.35 + 0.45 * lev)
            dots.add(Line(d_.get_center(), t.get_edge_center(-side), stroke_width=1, color=GREY_B))
            dots.add(d_, t)
        self.play(LaggedStart(*[FadeIn(m) for m in dots], lag_ratio=0.08), run_time=3)
        self.caption("四十多个数量级：不同的尺度要用不同的理论", "Over forty orders of magnitude: different scales need different theories")
        self.card([["数量级", "Orders of magnitude"],
                   ["先问“大约是 10 的几次方”，再决定用什么模型", "First ask “about ten to the what?”, then choose the model"]])
