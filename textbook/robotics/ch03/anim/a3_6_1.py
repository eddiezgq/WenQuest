"""动画 3.6.1（配图 3.6.1）：圆盘绕竖直轴转动，盘上各点速度垂直于半径、大小与到轴的距离成正比；
参考点沿轴移动，r 改变而 ω × r 不变。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-2.6, -1.4, 0])
SC = 1.6
W = 0.9                                     # 角速度，rad/s（动画中的数值）
RADII = (0.6, 1.2, 1.8)


class Lesson(Base):
    def construct(self):
        self.title("3.6", "角速度矢量与 v = ω × r", "Angular velocity and v = ω × r")
        P = lambda p: proj3(p, O, SC)
        disk = Polygon(*[P([2.0 * math.cos(t), 2.0 * math.sin(t), 0]) for t in np.linspace(0, 2 * math.pi, 72)[:-1]],
                       stroke_color=YELLOW_E, fill_color=YELLOW_E, fill_opacity=0.15, stroke_width=2)
        axis = DashedLine(P([0, 0, -0.6]), P([0, 0, 2.4]), color=GREY_B)
        w_arrow = Arrow(P([0, 0, 1.7]), P([0, 0, 2.5]), buff=0, color=WHITE, stroke_width=7)
        w_lab = MathTex(r"\boldsymbol\omega", font_size=40).next_to(w_arrow, RIGHT, buff=0.1)
        self.play(FadeIn(disk), Create(axis), GrowArrow(w_arrow), Write(w_lab), run_time=1.2)
        ang = ValueTracker(0.0)

        def points():
            t = ang.get_value()
            g = VGroup()
            for k, r in enumerate(RADII):
                ph = t + k * 2.1
                pos = np.array([r * math.cos(ph), r * math.sin(ph), 0])
                v = np.cross([0, 0, W], pos)
                g.add(Line(P([0, 0, 0]), P(pos), color=GREY_B, stroke_width=2),
                      Dot(P(pos), radius=0.07, color=RED),
                      Arrow(P(pos), P(pos + 0.8 * v), buff=0, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.3))
            return g

        pts = always_redraw(points)
        self.add(pts)
        self.caption("各点的速度都垂直于半径，大小与到轴的距离 ρ 成正比", "Every velocity is perpendicular to the radius, with magnitude proportional to the distance ρ", wait=0)
        self.play(ang.animate.set_value(2.4), run_time=5, rate_func=linear)
        self.play(FadeOut(pts), run_time=0.5)
        # 第二部分：参考点沿轴移动
        Pt = np.array([0.0, 1.5, 0.0])
        h = ValueTracker(0.0)
        v_fixed = np.cross([0, 0, W], Pt)
        dotP = Dot(P(Pt), radius=0.08, color=RED)
        vP = Arrow(P(Pt), P(Pt + 0.8 * v_fixed), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.3)
        self.play(FadeIn(dotP), GrowArrow(vP), Write(MathTex("P", font_size=34).next_to(P(Pt), DR, buff=0.1)))

        def ref():
            o = np.array([0, 0, h.get_value()])
            r = Pt - o
            c = np.cross([0, 0, W], r)
            return VGroup(Dot(P(o), radius=0.08, color=BLUE), Arrow(P(o), P(Pt), buff=0, color=BLUE, stroke_width=5),
                          MathTex(r"\boldsymbol r", color=BLUE, font_size=34).move_to(P(0.5 * (o + Pt)) + UP * 0.25),
                          VGroup(MathTex(r"r = (%.2f,\ %.2f,\ %.2f)" % tuple(r), font_size=32, color=BLUE),
                                 MathTex(r"\boldsymbol\omega\times\boldsymbol r = (%.2f,\ %.2f,\ %.2f)" % tuple(c), font_size=32, color=RED)
                                 ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(np.array([3.6, 0.8, 0])))

        rg = always_redraw(ref)
        self.add(rg)
        self.caption("参考点 O 沿转轴上下移动：r 在变，ω × r 不变", "Slide the reference point O along the axis: r changes, ω × r does not", wait=0)
        self.play(h.animate.set_value(1.6), run_time=3, rate_func=smooth)
        self.play(h.animate.set_value(-0.5), run_time=3, rate_func=smooth)
        self.wait(0.5)
        self.card([["绕定轴转动", "Rotation about a fixed axis"],
                   MathTex(r"\boldsymbol v = \boldsymbol\omega\times\boldsymbol r,\qquad |\boldsymbol v| = \rho\,\dot\theta", font_size=46),
                   ["r 从转轴上任意一点量起；ω 沿转轴，按右手定则", "r from any point on the axis; ω along the axis by the right-hand rule"]])
