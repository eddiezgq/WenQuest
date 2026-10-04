"""动画 6.1.1：单位正方形被矩阵连续地变形，同时显示行列式。先拉成平行四边形（det 增大到 2.75）；
再让第 2 列逐渐转向第 1 列，平行四边形变扁，det 减小到 0；继续转过去，图形翻面（变成紫色），det 变为负数。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("6.1", "行列式：有向面积", "The determinant is a signed area")
        k = 1.3
        O = np.array([-2.6, -1.6, 0.0])
        c1 = np.array([2.0, 0.5])
        c2_start = np.array([0.5, 1.5])
        L2 = np.linalg.norm(c2_start)
        a0, a1 = np.arctan2(c2_start[1], c2_start[0]), np.arctan2(c1[1], c1[0]) - np.radians(35)
        s1, s2 = ValueTracker(0.0), ValueTracker(0.0)

        def M():
            t = s1.get_value()
            col1 = (1 - t) * np.array([1.0, 0]) + t * c1
            col2 = (1 - t) * np.array([0.0, 1]) + t * c2_start
            if s2.get_value() > 0:
                a = a0 + (a1 - a0) * s2.get_value()
                col2 = L2 * np.array([np.cos(a), np.sin(a)])
            return np.column_stack([col1, col2])

        def scene():
            T = M()
            P = lambda x, y: O + k * np.array([*(T @ np.array([x, y])), 0.0])
            d = np.linalg.det(T)
            g = VGroup()
            g.add(Line(O + LEFT * 0.5, O + RIGHT * 5.0, color=GREY_B, stroke_width=1.5), Line(O + DOWN * 0.8, O + UP * 3.6, color=GREY_B, stroke_width=1.5))
            g.add(Polygon(P(0, 0), P(1, 0), P(1, 1), P(0, 1), color=WHITE, stroke_width=2,
                          fill_color=GOLD if d >= 0 else PURPLE_B, fill_opacity=0.6))
            g.add(Arrow(P(0, 0), P(1, 0), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.15))
            g.add(Arrow(P(0, 0), P(0, 1), buff=0, color=GREEN, stroke_width=6, max_tip_length_to_length_ratio=0.15))
            num = DecimalNumber(d, num_decimal_places=2, include_sign=True, font_size=44, color=GOLD if d >= 0 else PURPLE_B)
            lab = VGroup(MathTex(r"\det A =", font_size=44), num).arrange(RIGHT, buff=0.2).move_to([4.2, 1.6, 0])
            g.add(lab)
            return g

        G = always_redraw(scene)
        self.play(FadeIn(G))
        self.caption("单位正方形：面积 1，det I = 1", "The unit square: area 1, det I = 1")
        self.play(s1.animate.set_value(1.0), run_time=3)
        self.caption("拉成平行四边形：行列式就是它的面积", "Stretched into a parallelogram: the determinant is its area", wait=1.0)
        self.caption("让第 2 列（绿）转向第 1 列（红）", "Turn column 2 (green) toward column 1 (red)", wait=0.2)
        frac = (np.arctan2(c2_start[1], c2_start[0]) - np.arctan2(c1[1], c1[0])) / (a0 - a1)
        self.play(s2.animate.set_value(frac), run_time=3)
        self.caption("两列平行：平行四边形压成线段，det = 0，矩阵不可逆", "Columns parallel: the parallelogram collapses, det = 0, not invertible", wait=1.2)
        self.play(s2.animate.set_value(1.0), run_time=2.5)
        self.caption("转过头：图形翻面，行列式变为负数", "Past that point the figure flips over and the determinant turns negative", wait=1.2)
        self.card([["|det A| 是面积的伸缩倍数", "|det A| is the factor by which areas scale"],
                   ["det A 的符号表示是否翻面；det A = 0 表示压扁了", "Its sign says whether the figure flipped; det A = 0 means it was flattened"]])
