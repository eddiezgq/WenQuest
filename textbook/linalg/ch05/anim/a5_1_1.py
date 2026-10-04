"""动画 5.1.1：可逆与奇异。网格和小旗先被可逆矩阵 A = [[1.2, 0.8], [0.2, 1.0]] 拉歪，再被 A⁻¹ 拉回原样；
换成奇异矩阵 S = [[1, 0.5], [0.6, 0.3]]，整个平面被压成一条直线，不同的点落到同一处，无法还原。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("5.1", "逆矩阵：撤销一个变换", "The inverse undoes a transformation")
        k = 0.9
        O = np.array([0.0, -0.2, 0.0])
        A = np.array([[1.2, 0.8], [0.2, 1.0]])
        S = np.array([[1.0, 0.5], [0.6, 0.3]])
        s = ValueTracker(0.0)
        src = {"M0": np.eye(2), "M1": np.eye(2)}

        def M():
            t = s.get_value()
            return (1 - t) * src["M0"] + t * src["M1"]

        flag = [(0, 0), (1, 0), (1, 0.5), (0.5, 0.5), (0.5, 1), (0, 1)]

        def scene():
            T = M()
            pt = lambda x, y: O + k * np.array([*(T @ np.array([x, y])), 0.0])
            g = VGroup()
            for j in range(-4, 5):
                i = 0.5 * j
                g.add(Line(pt(i, -2), pt(i, 2), color=BLUE_D if j else GREY_B, stroke_width=1.5 if j else 2.5, stroke_opacity=0.6))
                g.add(Line(pt(-2, i), pt(2, i), color=BLUE_D if j else GREY_B, stroke_width=1.5 if j else 2.5, stroke_opacity=0.6))
            g.add(Polygon(*[pt(x, y) for x, y in flag], color=GOLD_E, fill_color=GOLD, fill_opacity=0.7, stroke_width=2))
            g.add(Arrow(pt(0, 0), pt(1, 0), buff=0, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.25))
            g.add(Arrow(pt(0, 0), pt(0, 1), buff=0, color=GREEN, stroke_width=5, max_tip_length_to_length_ratio=0.25))
            return g

        G = always_redraw(scene)
        self.play(FadeIn(G))

        def go(M1, run=3):
            src["M0"], src["M1"] = M(), M1
            s.set_value(0.0)
            self.play(s.animate.set_value(1.0), run_time=run)

        self.caption("A 把网格和小旗拉歪", "A skews the grid and the flag", wait=0.2)
        go(A)
        self.caption("再用 A⁻¹：一切回到原样", "Then A⁻¹: everything returns", wait=0.2)
        go(np.eye(2))
        self.caption("A⁻¹A = I：先做 A 再做 A⁻¹，等于什么也没做", "A⁻¹A = I: doing A then A⁻¹ does nothing", wait=1.0)
        self.caption("换成奇异矩阵 S：两列共线", "Now a singular matrix S: its columns are parallel", wait=0.2)
        go(S)
        dots = VGroup(Dot(O + k * np.array([*(S @ np.array([1.0, 0.0])), 0.0]), color=YELLOW, radius=0.09))
        self.play(FadeIn(dots))
        self.caption("整个平面压成一条直线：(1, 0) 与 (0, 2) 落到同一点", "The plane is flattened to a line: (1, 0) and (0, 2) land on the same point", wait=1.2)
        self.caption("压扁后无从知道原来在哪里，没有矩阵能把它还原", "Once flattened, nothing can tell where points came from: no matrix undoes it", wait=1.2)
        self.card([["可逆：变换可以撤销，A⁻¹A = AA⁻¹ = I", "Invertible: the map can be undone, A⁻¹A = AA⁻¹ = I"],
                   ["奇异：某个方向被压成零，信息丢失，无法撤销", "Singular: some direction is crushed to zero; the information is lost"]])
