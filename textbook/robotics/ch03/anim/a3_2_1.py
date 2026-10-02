"""动画 3.2.1（配图 3.2.1）：a 固定，b 在水平面内绕起点转一周；平行四边形面积与 a×b 的长度同步变化，
b 越过 a 所在直线时 a×b 翻转方向。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-2.6, -0.9, 0])
SC = 1.0
A = np.array([0.0, 2.2, 0.0])          # a 沿 y（屏幕上向右）
LB = 1.7                               # |b|
KZ = 0.55                              # a×b 的显示比例


def bvec(t):
    return LB * np.array([0.0, math.cos(t), math.sin(t)])      # a、b 都在 yz 平面（屏幕平面）内；a×b 沿 x，垂直于屏幕


class Lesson(Base):
    def construct(self):
        self.title("3.2", "叉积：面积与右手定则", "Cross product: area and the right-hand rule")
        P = lambda p: proj3(p, O, SC)
        plane = Polygon(P([0, -1.2, -1.9]), P([0, 2.8, -1.9]), P([0, 2.8, 2.1]), P([0, -1.2, 2.1]),
                        stroke_color=GREY_D, fill_color=GREY_E, fill_opacity=0.2, stroke_width=1)
        zaxis = DashedLine(P([-3.2, 0, 0]), P([3.2, 0, 0]), color=GREY_B, stroke_width=2)     # 平面的法线方向
        self.play(FadeIn(plane), Create(zaxis), run_time=1)
        a_arrow = Arrow(P([0, 0, 0]), P(A), buff=0, color=RED, stroke_width=6)
        self.play(GrowArrow(a_arrow), Write(MathTex(r"\boldsymbol a", color=RED).next_to(P(A), RIGHT, buff=0.1)))
        th = ValueTracker(math.radians(25))

        def scene():
            t = th.get_value()
            b = bvec(t)
            n = KZ * np.cross(A, b)
            g = VGroup(Polygon(P([0, 0, 0]), P(A), P(A + b), P(b), stroke_color=YELLOW, stroke_width=2,
                               fill_color=YELLOW, fill_opacity=0.25),
                       Arrow(P([0, 0, 0]), P(b), buff=0, color=GREEN, stroke_width=6),
                       MathTex(r"\boldsymbol b", color=GREEN).move_to(P(b * 1.15)))
            if abs(n[0]) > 0.05:
                g.add(Arrow(P([0, 0, 0]), P(n), buff=0, color=BLUE, stroke_width=7, max_tip_length_to_length_ratio=0.2),
                      MathTex(r"\boldsymbol a\times\boldsymbol b", color=BLUE, font_size=34).next_to(P(n), LEFT, buff=0.15))
            return g

        def numbers():
            t = th.get_value()
            b = bvec(t)
            cr = abs(np.cross(A, b)[0])
            dt = A @ b
            dt = 0.0 if abs(dt) < 0.005 else dt
            return VGroup(MathTex(r"\varphi = %d^\circ" % round(math.degrees(t) % 360), color=YELLOW, font_size=36),
                          bi(["φ：b 从 a 起逆时针转过的角", "φ: angle turned by b from a, counterclockwise"], 22, GREY_B),
                          MathTex(r"|\boldsymbol a\times\boldsymbol b| = |\boldsymbol a||\boldsymbol b|\,|\sin\varphi| = %.2f" % cr, font_size=34),
                          MathTex(r"\boldsymbol a\cdot\boldsymbol b = |\boldsymbol a||\boldsymbol b|\cos\varphi = %.2f" % dt, font_size=30, color=GREY_B),
                          bi(["黄色平行四边形的面积 = |a×b|", "yellow area = |a×b|"], 24, YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(np.array([3.6, 0.8, 0]))

        sc = always_redraw(scene)
        nums = always_redraw(numbers)
        self.add(sc, nums)
        self.caption("a、b 在平面内；a×b 垂直于平面，长度等于平行四边形的面积", "a, b lie in the plane; a×b is normal to it, its length is the area")
        self.caption("b 转向 90°：面积最大，a×b 最长", "b turns to 90°: largest area, longest a×b", wait=0)
        self.play(th.animate.set_value(math.radians(90)), run_time=2.5, rate_func=smooth)
        self.wait(0.8)
        self.caption("b 与 a 共线：面积为零，a×b = 0", "b along a: zero area, a×b = 0", wait=0)
        self.play(th.animate.set_value(math.radians(180)), run_time=2.5, rate_func=smooth)
        self.wait(0.5)
        self.caption("越过 a 所在直线：a×b 翻转为背向我们（右手定则）", "Past the line of a: a×b flips to point away from us (right-hand rule)", wait=0)
        self.play(th.animate.set_value(math.radians(270)), run_time=2.5, rate_func=smooth)
        self.wait(0.8)
        self.play(th.animate.set_value(math.radians(385)), run_time=2.5, rate_func=smooth)
        self.card([["叉积", "Cross product"],
                   MathTex(r"|\boldsymbol a\times\boldsymbol b| = |\boldsymbol a||\boldsymbol b|\sin\theta,\ \ 0\le\theta\le\pi", font_size=46),
                   ["方向：右手四指从 a 弯向 b，拇指所指", "Direction: curl the fingers from a to b, the thumb points along a×b"],
                   MathTex(r"\boldsymbol b\times\boldsymbol a = -\,\boldsymbol a\times\boldsymbol b", font_size=42)])
