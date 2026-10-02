"""动画 5.2.1（配图 5.2.2）：工件先绕原点转 60°，再平移 (2.4, 0.6)。点 (p, 1) 跟着转动和平移；方向 (v, 0) 只转动。"""
from manim import *
from wq_anim import *
import numpy as np
import math

U = 1.75
O = np.array([-5.4, -2.5, 0])
BODY = [(0.2, 0.2), (1.4, 0.2), (1.4, 0.9), (0.2, 0.9)]
P = np.array([1.4, 0.9])
V0 = np.array([0.4, 0.55])
V = np.array([0.7, 0.0])


def scr(x):
    return O + U * np.array([x[0], x[1], 0])


class Lesson(Base):
    def construct(self):
        self.title("5.2", "齐次坐标：点和方向", "Homogeneous coordinates: points and directions")
        fa = frame2(O, 0, 1.1, ("x_a", "y_a"), name=r"\{a\}")
        self.play(Create(fa))
        th, dx, dy = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)

        def move(x):
            t = math.radians(th.get_value())
            c, s = math.cos(t), math.sin(t)
            return np.array([c * x[0] - s * x[1] + dx.get_value(), s * x[0] + c * x[1] + dy.get_value()])

        def turn(x):
            t = math.radians(th.get_value())
            c, s = math.cos(t), math.sin(t)
            return np.array([c * x[0] - s * x[1], s * x[0] + c * x[1]])

        ghost = Polygon(*[scr(p) for p in BODY], color=GREY_B, stroke_width=2).set_fill(GREY_D, 0.3)
        body = always_redraw(lambda: Polygon(*[scr(move(p)) for p in BODY], color=GOLD, stroke_width=3).set_fill("#5a3d0a", 0.6))
        dotP = always_redraw(lambda: Dot(scr(move(P)), color=YELLOW, radius=0.08))
        labP = always_redraw(lambda: MathTex("P", color=YELLOW, font_size=34).next_to(dotP, UR, buff=0.05))
        arrV = always_redraw(lambda: Arrow(scr(move(V0)), scr(move(V0)) + U * np.r_[turn(V), 0], buff=0, color=BLUE, stroke_width=6))
        labV = always_redraw(lambda: MathTex("v", color=BLUE, font_size=34).next_to(arrV.get_end(), RIGHT, buff=0.1))
        ghost.set_z_index(-1)
        self.add(ghost)
        self.play(FadeIn(body), FadeIn(dotP), Write(labP), GrowArrow(arrV), Write(labV))

        hp = always_redraw(lambda: MathTex(r"(p,\,1) = (%.2f,\ %.2f,\ 1)" % tuple(move(P)), color=YELLOW, font_size=34)
                           .to_corner(UR, buff=0.5).shift(DOWN * 1.0 + LEFT * 0.3))
        hv = always_redraw(lambda: MathTex(r"(v,\,0) = (%.2f,\ %.2f,\ 0)" % tuple(turn(V)), color=BLUE, font_size=34)
                           .next_to(hp, DOWN, buff=0.3, aligned_edge=LEFT))
        self.play(Write(hp), Write(hv))
        self.caption("点的齐次坐标末位为 1，方向的末位为 0", "A point ends in 1, a direction ends in 0")

        self.caption("先转 60°：点和方向都跟着转", "Turn 60°: both the point and the direction turn", wait=0)
        self.play(th.animate.set_value(60.0), run_time=3, rate_func=smooth)
        self.wait(0.5)
        self.caption("再平移 (2.4, 0.6)：点跟着移，方向的读数一点也不变", "Then shift by (2.4, 0.6): the point moves, the direction's numbers stay", wait=0)
        self.play(dx.animate.set_value(2.4), dy.animate.set_value(0.6), run_time=3, rate_func=smooth)
        self.wait(0.8)
        box = SurroundingRectangle(hv, color=BLUE, buff=0.12)
        self.play(Create(box))
        self.caption("平移乘的是末位：末位为 0，平移就加不进来", "The shift multiplies the last entry: with 0 it never gets added")
        self.wait(1)
        self.card([["齐次变换作用在点和方向上", "A homogeneous transform on points and directions"],
                   MathTex(r"\begin{pmatrix} R & p \\ 0 & 1 \end{pmatrix}\begin{pmatrix} x \\ 1 \end{pmatrix} = \begin{pmatrix} Rx + p \\ 1 \end{pmatrix}", font_size=40),
                   MathTex(r"\begin{pmatrix} R & p \\ 0 & 1 \end{pmatrix}\begin{pmatrix} v \\ 0 \end{pmatrix} = \begin{pmatrix} Rv \\ 0 \end{pmatrix}", font_size=40),
                   ["点既转又移，方向只转不移", "points turn and move; directions only turn"]])
