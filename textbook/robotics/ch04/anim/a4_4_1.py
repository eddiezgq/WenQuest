"""动画 4.4.1（配图 4.4.1）：矢量 v 绕 ω̂ 转动——沿轴部分不动，垂直部分沿圆周转过 θ。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-1.0, -1.6, 0])
SC = 2.6


class Lesson(Base):
    def construct(self):
        self.title("4.4", "罗德里格斯公式的几何意义", "Rodrigues' formula, geometrically")
        w = np.array([0.0, 0.0, 1.0])
        v = np.array([0.75, 0.15, 0.55])
        vpar = (w @ v) * w
        vperp = v - vpar
        wxv = np.cross(w, v)
        P = lambda p: proj3(p, O, SC)
        axis = Line(P(-0.15 * w), P(1.05 * w), color=INK, stroke_width=4)
        self.add(axis, MathTex(r"\hat\omega", color=INK).next_to(P(1.05 * w), UP, buff=0.1))
        circle = VMobject(color=GREY_B, stroke_width=2).set_points_as_corners(
            [P(vpar + math.cos(a) * vperp + math.sin(a) * wxv) for a in np.linspace(0, 2 * math.pi, 120)])
        self.play(Create(circle), run_time=1)
        v_arrow = Arrow(P(np.zeros(3)), P(v), buff=0, color=WHITE, stroke_width=6)
        self.play(GrowArrow(v_arrow), Write(MathTex("v").next_to(P(v), RIGHT, buff=0.1)))
        self.caption("把 v 拆成沿轴的部分和垂直于轴的部分", "Split v into a part along the axis and a part across it")
        a_par = Arrow(P(np.zeros(3)), P(vpar), buff=0, color=BLUE, stroke_width=6)
        a_perp = Arrow(P(vpar), P(v), buff=0, color=RED, stroke_width=6)
        a_wxv = Arrow(P(vpar), P(vpar + wxv), buff=0, color=GREEN, stroke_width=6)
        self.play(GrowArrow(a_par), Write(MathTex(r"v_\parallel", color=BLUE).next_to(P(vpar * 0.5), LEFT)))
        self.play(GrowArrow(a_perp), Write(MathTex(r"v_\perp", color=RED, font_size=34).next_to(P(vpar + vperp * 0.6), DOWN, buff=0.1)))
        self.play(GrowArrow(a_wxv), Write(MathTex(r"\hat\omega\times v", color=GREEN, font_size=34).next_to(P(vpar + wxv), UP, buff=0.1)))
        self.caption("v⊥ 与 ω̂×v 等长、互相垂直，张成转动所在的平面", "v⊥ and ω̂×v: equal length, perpendicular, spanning the plane of rotation")
        th = ValueTracker(0.0)
        moving = always_redraw(lambda: VGroup(
            Arrow(P(vpar), P(vpar + math.cos(th.get_value()) * vperp + math.sin(th.get_value()) * wxv), buff=0, color=ORANGE, stroke_width=6),
            Arrow(P(np.zeros(3)), P(vpar + math.cos(th.get_value()) * vperp + math.sin(th.get_value()) * wxv), buff=0, color=YELLOW, stroke_width=6)))
        self.add(moving)
        self.caption("转动时：沿轴部分不变，垂直部分在平面内转过 θ", "Turning: the axial part stays, the perpendicular part turns by θ", wait=0)
        self.play(th.animate.set_value(math.radians(125)), run_time=4, rate_func=smooth)
        self.wait(1)
        self.card([["罗德里格斯公式", "Rodrigues' formula"],
                   MathTex(r"v'=v\cos\theta+(\hat\omega\times v)\sin\theta+\hat\omega(\hat\omega\cdot v)(1-\cos\theta)", font_size=36),
                   MathTex(r"R=I+\sin\theta\,[\hat\omega]+(1-\cos\theta)[\hat\omega]^2", font_size=40)])
