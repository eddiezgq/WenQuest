"""动画 10.7.1（配图 10.7.1）：依次固定刚体上的三个点。A 在空间中自由移动（3 个数）；固定 A 后，B 只能在以 A 为心的
球面上移动（2 个数）；再固定 B，C 只能绕直线 AB 转动（1 个数）；三点都固定，刚体不能再动。3 + 2 + 1 = 6。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-1.2, -0.9, 0])
SC = 1.9
A0 = np.array([0.0, 0.0, 0.0])
RB = 1.1


def P(p):
    return proj3(p, O, SC)


def sph(th, ph, r=RB):
    return np.array([r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph), r * math.cos(th)])


class Lesson(Base):
    def construct(self):
        self.title("10.7", "刚体为什么需要六个数", "Why a rigid body needs six numbers")
        axes = frame3(origin=np.array([-5.2, -2.0, 0]), length=0.6, scale=SC)
        self.play(FadeIn(axes))
        count = MathTex("3", font_size=60, color=YELLOW).move_to(np.array([4.6, 1.6, 0]))
        # 1. A 自由移动
        a = ValueTracker(0.0)
        Apos = lambda: A0 + 0.5 * np.array([math.sin(a.get_value()), math.sin(1.7 * a.get_value()), 0.6 * math.sin(2.3 * a.get_value())])
        dotA = always_redraw(lambda: Dot(P(Apos()), radius=0.1, color=RED))
        labA = always_redraw(lambda: MathTex("A", font_size=34, color=RED).next_to(P(Apos()), DL, buff=0.08))
        self.add(dotA, labA)
        self.caption("A 可以去空间中任何地方：3 个数", "A can go anywhere in space: 3 numbers", wait=0)
        self.play(a.animate.set_value(2 * math.pi), Write(count), run_time=4, rate_func=linear)
        dotA.clear_updaters()
        labA.clear_updaters()
        pin = Circle(radius=0.17, color=RED, stroke_width=3).move_to(P(A0))
        self.play(dotA.animate.move_to(P(A0)), labA.animate.next_to(P(A0), DL, buff=0.08), Create(pin), run_time=0.6)
        # 2. B 在球面上
        rings = VGroup(*[Polygon(*[P(sph(th, u)) for u in np.linspace(0, 2 * math.pi, 48)[:-1]], color=BLUE_D, stroke_width=1.5)
                         for th in (math.pi / 4, math.pi / 2, 3 * math.pi / 4)],
                       *[Polygon(*[P(sph(u, ph)) for u in np.linspace(0, 2 * math.pi, 48)[:-1]], color=BLUE_D, stroke_width=1.5)
                         for ph in (0, math.pi / 3, 2 * math.pi / 3)])
        self.play(Create(rings), run_time=1.0)
        b = ValueTracker(0.0)
        Bpos = lambda: sph(1.25 + 0.35 * math.sin(b.get_value()), 1.3 + 1.0 * b.get_value() / (2 * math.pi))
        dotB = always_redraw(lambda: Dot(P(Bpos()), radius=0.1, color=GREEN))
        rodAB = always_redraw(lambda: Line(P(A0), P(Bpos()), color=INK, stroke_width=4))
        labB = always_redraw(lambda: MathTex("B", font_size=34, color=GREEN).next_to(P(Bpos()), UR, buff=0.08))
        self.add(rodAB, dotB, labB)
        self.caption("固定 A：B 到 A 的距离不变，只能在球面上走：再加 2 个数", "Fix A: B keeps its distance, so it moves on a sphere: 2 more numbers", wait=0)
        self.play(b.animate.set_value(2 * math.pi), Transform(count, MathTex("3 + 2", font_size=60, color=YELLOW).move_to(count)), run_time=4, rate_func=linear)
        Bf = Bpos()
        for m in (dotB, rodAB, labB):
            m.clear_updaters()
        self.play(FadeOut(rings), Create(Circle(radius=0.17, color=GREEN, stroke_width=3).move_to(P(Bf))), run_time=0.6)
        # 3. C 绕 AB 的圆
        u = Bf / np.linalg.norm(Bf)
        e1 = np.cross(u, [0, 0, 1.0])
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(u, e1)
        foot = 0.5 * Bf
        rc = 0.9
        Cpos = lambda ang: foot + rc * (math.cos(ang) * e1 + math.sin(ang) * e2)
        circ = Polygon(*[P(Cpos(x)) for x in np.linspace(0, 2 * math.pi, 60)[:-1]], color=PURPLE_B, stroke_width=2)
        axis = DashedLine(P(-0.4 * Bf), P(1.4 * Bf), color=GREY_B, stroke_width=2)
        self.play(Create(axis), Create(circ), run_time=1.0)
        c = ValueTracker(0.0)
        tri = always_redraw(lambda: Polygon(P(A0), P(Bf), P(Cpos(c.get_value())), color=INK, fill_color=STEEL, fill_opacity=0.35, stroke_width=3))
        dotC = always_redraw(lambda: Dot(P(Cpos(c.get_value())), radius=0.1, color=PURPLE_B))
        labC = always_redraw(lambda: MathTex("C", font_size=34, color=PURPLE_B).next_to(P(Cpos(c.get_value())), UP, buff=0.08))
        self.add(tri, dotC, labC)
        self.caption("再固定 B：C 只能绕直线 AB 转动，只剩 1 个数", "Fix B as well: C can only turn about line AB, 1 number left", wait=0)
        self.play(c.animate.set_value(2 * math.pi), Transform(count, MathTex("3 + 2 + 1", font_size=60, color=YELLOW).move_to(count)), run_time=4, rate_func=linear)
        self.play(Transform(count, MathTex("3 + 2 + 1 = 6", font_size=60, color=YELLOW).move_to(count)), FadeOut(circ), run_time=1)
        self.caption("三点都固定，刚体不能再动：空间中的刚体有 6 个自由度", "With all three points fixed the body cannot move: a rigid body in space has 6 degrees of freedom")
        self.card([["刚体的六个自由度", "Six degrees of freedom"],
                   MathTex(r"3 + 2 + 1 = 6 = 9 - 3", font_size=50),
                   ["位置 3 个数 + 姿态 3 个数；速度也是 6 个数：v 和 ω", "3 for position + 3 for orientation; velocity is 6 numbers too: v and ω"]])
