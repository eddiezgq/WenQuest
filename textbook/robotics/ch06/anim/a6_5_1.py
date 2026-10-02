"""动画 6.5.1（配图 6.5.1）：算例 6.5.1，从 x 轴方向看 UR5e 的腕部（y–z 平面）。工具绕过尖端、沿 x̂_t 的轴转动，
尖端不动，法兰盘中心走圆弧。同一个运动在 {t}、{b}、{s} 中的三个运动旋量不同，但描述的是同一根转轴。"""
from manim import *
from wq_anim import *
import numpy as np
import math

SC = 14.0
O = np.array([5.6, -1.3, 0])
TIP = np.array([-0.384, 0.063])
PTS = [np.array([-0.134, 0.163]), np.array([-0.134, 0.063]), np.array([-0.234, 0.063])]   # 关节 5、6 中心，法兰盘中心（y, z）


def P(yz):
    return O + SC * np.array([yz[0], yz[1], 0])


def rot(a, x):
    """绕过尖端、沿 x 轴的转动（从 +x 方向看，逆时针为正）。"""
    c, s = math.cos(a), math.sin(a)
    d = x - TIP
    return TIP + np.array([c * d[0] - s * d[1], s * d[0] + c * d[1]])


def wrist(a):
    pts = [rot(a, x) for x in PTS] + [TIP]
    g = VGroup(*[Line(P(p), P(q), color=GREY_B if i < 2 else GOLD, stroke_width=14 if i < 2 else 10) for i, (p, q) in enumerate(zip(pts, pts[1:]))])
    g.add(*[Dot(P(p), radius=0.08, color=WHITE) for p in pts[:2]])
    # 法兰盘坐标系 {b}：零位时 y_b = −y_s、z_b = −z_s；画它的 y、z 轴
    fb = pts[2]
    yb, zb = rot(a, fb + np.array([-0.05, 0])) - fb, rot(a, fb + np.array([0, -0.05])) - fb
    g.add(Arrow(P(fb), P(fb + yb), buff=0, color=GREEN, stroke_width=5), Arrow(P(fb), P(fb + zb), buff=0, color=BLUE, stroke_width=5))
    g.add(MathTex(r"\{b\}", font_size=30).next_to(P(fb), UP, buff=0.25))
    g.add(Arrow(P(TIP), P(TIP + np.array([-0.05, 0])), buff=0, color=GREEN, stroke_width=5),
          Arrow(P(TIP), P(TIP + np.array([0, -0.05])), buff=0, color=BLUE, stroke_width=5),
          Dot(P(TIP), radius=0.1, color=RED), MathTex(r"\{t\}", font_size=30).next_to(P(TIP), UL, buff=0.15))
    return g


def txt(s, color=INK, size=24):
    return Text(s, font=LATIN, font_size=size, color=color)


class Lesson(Base):
    def construct(self):
        self.title("6.5", "伴随变换：同一个运动，三种写法", "The adjoint: one motion, three descriptions")
        a = ValueTracker(0.0)
        w = always_redraw(lambda: wrist(a.get_value()))
        self.play(FadeIn(w))
        ax_s = VGroup(Arrow(LEFT * 5.8 + DOWN * 1.8, LEFT * 6.6 + DOWN * 1.8, buff=0, color=GREEN, stroke_width=4),
                      Arrow(LEFT * 5.8 + DOWN * 1.8, LEFT * 5.8 + DOWN * 1.0, buff=0, color=BLUE, stroke_width=4),
                      Text("y_s", font=LATIN, font_size=20, color=GREEN).move_to(LEFT * 6.6 + DOWN * 2.05),
                      Text("z_s", font=LATIN, font_size=20, color=BLUE).move_to(LEFT * 5.5 + DOWN * 1.0),
                      Text("x_s ⊙", font=LATIN, font_size=20, color=RED).move_to(LEFT * 5.2 + DOWN * 2.05))
        self.add(ax_s)
        self.caption("从 x 轴方向看腕部：工具（金色）绕过尖端的 x 轴转动", "Looking along x: the tool (gold) turns about the x axis through its tip")
        arc = always_redraw(lambda: VMobject(color=RED, stroke_width=4).set_points_as_corners(
            [P(rot(u, PTS[2])) for u in np.linspace(0, a.get_value() if abs(a.get_value()) > 1e-3 else 1e-3, 30)]))
        self.add(arc)
        self.play(a.animate.set_value(0.6), run_time=2.5)
        self.play(a.animate.set_value(-0.6), run_time=3)
        self.play(a.animate.set_value(0.0), run_time=1.5)
        tab = VGroup(txt("V_t = (0.5, 0, 0,  0, 0, 0)", YELLOW),
                     txt("V_b = [Ad_Tbt] V_t = (0.5, 0, 0,  0, 0, -0.075)"),
                     txt("V_s = [Ad_Tst] V_t = (0.5, 0, 0,  0, 0.0315, 0.192)")).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        tab.to_corner(UL, buff=0.4).shift(DOWN * 1.1)
        self.play(FadeIn(tab, shift=RIGHT * 0.2))
        self.caption("三个六维矢量各不相同：线速度部分是三个不同点的速度", "Three different 6-vectors: their linear parts are velocities of three different points")
        self.play(a.animate.set_value(0.5), run_time=2)
        self.caption("但转轴、角速度大小和节距（0）都相同：伴随矩阵只是换了一种写法", "Same axis, same rate, same pitch (0): the adjoint only rewrites the motion")
        self.wait(1)
        self.card([["伴随变换", "The adjoint map"],
                   ["运动旋量从一个坐标系换到另一个坐标系", "Moving a twist from one frame to another"],
                   MathTex(r"\mathcal V_a = [\mathrm{Ad}_{T_{ab}}]\mathcal V_b,\qquad [\mathrm{Ad}_T] = \begin{pmatrix} R & 0 \\ [p]R & R \end{pmatrix}", font_size=44)])
