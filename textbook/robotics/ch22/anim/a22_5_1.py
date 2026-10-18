"""动画 22.5.1（配图 22.5.1）：平面上的同一个刚体从 A（原点、转角 0）移到 B（(3.2, 1.0)、转角 120°），三种插值同时播放：
左：以 P（物体坐标系原点）为参考点的解耦插值，P 走直线；中：以 Q（物体坐标系中 (1.9, 0)）为参考点的解耦插值，Q 走直线；
右：旋量插值，平面上就是绕极点 c 转动（6.1 节），P、Q 都走圆弧。转角在三种插值中完全相同。"""
from manim import *
from wq_anim import *
import numpy as np
import math

SHAPE = np.array([[0, -0.25], [2.0, -0.25], [2.0, 0.25], [0.5, 0.25], [0.5, 0.9], [0, 0.9]])
PB, QB = np.array([0.0, 0.0]), np.array([1.9, 0.0])
XB, YB, AB = 3.2, 1.0, math.radians(120)


def rot(a):
    return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


def pole():
    # 平面位移的极点：c = (I − R)⁻¹ p
    return np.linalg.solve(np.eye(2) - rot(AB), np.array([XB, YB]))


C = pole()


def pose(kind, s):
    a = AB * s
    R = rot(a)
    if kind == 2:
        p = C - R @ C                      # 绕 c 转 a：x ↦ R(x − c) + c
        return R, p
    d = PB if kind == 0 else QB
    pd = (1 - s) * d + s * (rot(AB) @ d + np.array([XB, YB]))
    return R, pd - R @ d


SC = 0.72


class Lesson(Base):
    def construct(self):
        self.title("22.5", "位姿插值：解耦还是旋量", "Pose interpolation: decoupled or screw")
        centers = [np.array([-6.0, -1.5, 0]), np.array([-1.6, -1.5, 0]), np.array([2.8, -1.5, 0])]
        heads = [["解耦：P 走直线", "decoupled: P goes straight"], ["解耦：Q 走直线", "decoupled: Q goes straight"], ["旋量：绕极点转动", "screw: rotation about the pole"]]

        def scr(k, x):
            return centers[k] + SC * np.array([x[0], x[1], 0])

        hd = VGroup(*[bi(heads[k], 22, [RED_B, GREEN_B, YELLOW][k]).move_to(centers[k] + UP * 3.4 + RIGHT * 1.3) for k in range(3)])
        ghostA = VGroup(*[Polygon(*[scr(k, x) for x in SHAPE], color=GREY_B, fill_color=GREY_E, fill_opacity=0.6, stroke_width=1.5) for k in range(3)])
        ghostB = VGroup(*[Polygon(*[scr(k, rot(AB) @ x + np.array([XB, YB])) for x in SHAPE], color=BLUE_D, fill_color=BLUE_E, fill_opacity=0.3,
                                  stroke_width=1.5) for k in range(3)])
        self.caption("同一个物体，从 A（灰）移到 B（蓝），转 120°", "One body from A (grey) to B (blue), turning 120°", wait=0)
        self.play(FadeIn(hd), FadeIn(ghostA), FadeIn(ghostB), run_time=1.5)
        cdot = Dot(scr(2, C), radius=0.07, color=YELLOW)
        clab = MathTex("c", font_size=30, color=YELLOW).next_to(cdot, UP, buff=0.08)
        self.play(FadeIn(cdot), FadeIn(clab), run_time=0.6)
        tk = ValueTracker(0.0)
        trails = [[VMobject(color=RED, stroke_width=3), VMobject(color=GREEN, stroke_width=3)] for _ in range(3)]

        def bodies():
            s = tk.get_value()
            g = VGroup()
            for k in range(3):
                R, p = pose(k, s)
                g.add(Polygon(*[scr(k, R @ x + p) for x in SHAPE], color=WHITE, fill_color=STEEL, fill_opacity=0.55, stroke_width=2))
                for pb, col in ((PB, RED), (QB, GREEN)):
                    ss = np.linspace(0, s, max(2, int(60 * s) + 2))
                    pts = [scr(k, pose(k, u)[0] @ pb + pose(k, u)[1]) for u in ss]
                    g.add(VMobject(color=col, stroke_width=3).set_points_as_corners(pts))
                    g.add(Dot(scr(k, R @ pb + p), radius=0.07, color=col))
            return g

        labels = VGroup()
        for k in range(3):
            labels.add(MathTex("P", font_size=28, color=RED).next_to(scr(k, PB), DL, buff=0.05),
                       MathTex("Q", font_size=28, color=GREEN).next_to(scr(k, QB), DOWN, buff=0.08))
        self.add(always_redraw(bodies))
        self.play(FadeIn(labels), run_time=0.5)
        self.caption("三种插值同时播放：转角处处相同，区别只在位置", "All three play together: the same rotation at every instant, only the positions differ", wait=0)
        self.play(tk.animate.set_value(1.0), run_time=6.0, rate_func=smooth)
        self.wait(0.8)
        self.caption("解耦插值：所选的参考点走直线，换一个参考点，运动就变了", "Decoupled: the chosen point goes straight; another point gives another motion", wait=2.2)
        self.caption("旋量插值：绕固定的轴转动（平面上是极点），与坐标系、参考点的选取无关",
                     "Screw: rotation about a fixed axis (the pole in the plane), independent of frames and reference points", wait=2.5)
        self.card([["SE(3) 上的位姿插值", "Pose interpolation on SE(3)"],
                   MathTex(r"p_d(s) = (1-s)\,p_{dA} + s\,p_{dB},\qquad R(s) = R_A\,e^{[r]s}", font_size=40),
                   MathTex(r"T(s) = T_A\,e^{[\mathcal V]s},\qquad [\mathcal V] = \log\!\big(T_A^{-1}T_B\big)", font_size=40),
                   ["要某一点走直线用解耦插值；要与坐标系无关用旋量插值", "Decoupled when one point must go straight; screw when frames must not matter"]])
