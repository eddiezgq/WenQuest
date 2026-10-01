"""动画 4.2.1（配图 4.2.2）：两本书按做法 A（先 x 后 z）、做法 B（先 z 后 x）绕固定轴转动，最后姿态不同。"""
from manim import *
from wq_anim import *
import numpy as np
import math

DIMS = (0.7, 1.0, 0.18)


def book(R, origin, scale=1.6):
    a, b, c = (d / 2 for d in DIMS)
    V = [np.array([x, y, z]) for x in (-a, a) for y in (-b, b) for z in (-c, c)]
    P = [proj3(R @ v, origin, scale) for v in V]
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    g = VGroup(*[Polygon(*[P[i] for i in f], color="#8a6d2b", fill_color="#e9dfc8", fill_opacity=0.35, stroke_width=2)
                 for f in faces])
    g.add(Line(P[0], P[2], color=YELLOW, stroke_width=8), Line(P[1], P[3], color=YELLOW, stroke_width=8))
    return g


def axes_at(origin):
    return frame3(origin, np.eye(3), length=1.25, scale=1.0)


class Lesson(Base):
    def construct(self):
        self.title("4.2", "转动的次序不能交换", "The order of rotations matters")
        oA, oB = np.array([-3.4, -0.3, 0]), np.array([3.4, -0.3, 0])
        self.add(axes_at(oA), axes_at(oB))
        lA = zh("做法 A：先绕 x 转 90°，再绕 z 转 90°", 24, YELLOW).move_to(oA + UP * 2.6)
        lB = zh("做法 B：先绕 z 转 90°，再绕 x 转 90°", 24, YELLOW).move_to(oB + UP * 2.6)
        self.play(FadeIn(lA), FadeIn(lB))
        state = {"A": np.eye(3), "B": np.eye(3)}
        bA, bB = book(np.eye(3), oA), book(np.eye(3), oB)
        self.play(FadeIn(bA), FadeIn(bB))
        self.caption("金色粗边为书脊；两本书起初完全相同", "The gold edge is the spine; both books start the same")
        t = ValueTracker(0.0)
        steps = [(rot_x, rot_z), (rot_z, rot_x)]
        for k in range(2):
            fA, fB = steps[0][k], steps[1][k]
            RA0, RB0 = state["A"], state["B"]
            bA.add_updater(lambda m: m.become(book(fA(90 * t.get_value()) @ RA0, oA)))
            bB.add_updater(lambda m: m.become(book(fB(90 * t.get_value()) @ RB0, oB)))
            names = ("x", "z") if k == 0 else ("z", "x")
            self.caption(f"第 {k + 1} 步：A 绕 {names[0]} 轴，B 绕 {names[1]} 轴，各转 90°",
                         f"Step {k + 1}: A about {names[0]}, B about {names[1]}, 90° each", wait=0)
            self.play(t.animate.set_value(1.0), run_time=2.5)
            bA.clear_updaters()
            bB.clear_updaters()
            state["A"], state["B"] = fA(90) @ RA0, fB(90) @ RB0
            t.set_value(0.0)
            self.wait(0.5)
        self.caption("A 的书脊竖直向上，B 的书脊水平向左：结果不同", "A: spine points up; B: spine points left - different results")
        self.wait(1.5)
        self.card([["空间转动不可交换", "Spatial rotations do not commute"],
                   MathTex(r"R_z R_x \neq R_x R_z", font_size=50),
                   ["后做的写在左边（绕固定轴）", "the later rotation is written on the left (fixed axes)"]])
