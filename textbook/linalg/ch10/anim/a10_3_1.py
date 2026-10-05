"""动画 10.3.1：向平面投影就是找平面上离 b 最近的点。平面上的点 q 四处移动，到 b 的距离随之变化；当 q 到达 p 时，
连线 b − q 与平面垂直，距离最小。误差 e = b − p 垂直于平面里的每个向量；再投影一次，p 不动（P² = P）。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("10.3", "投影：平面上离 b 最近的点", "Projection: the closest point in the plane")
        O = np.array([-0.8, -1.25, 0.0])
        s = 1.25
        P = lambda p: proj3(p, O, s)
        plane = Polygon(*[P(np.array(c)) for c in ([-1.5, -2.2, 0], [3.2, -2.2, 0], [3.2, 3.2, 0], [-1.5, 3.2, 0])],
                        color=GOLD, fill_color=GOLD, fill_opacity=0.18, stroke_width=1.5)
        axes = VGroup(*[Arrow(P(np.zeros(3)), P(v), buff=0, color=GREY_B, stroke_width=2, max_tip_length_to_length_ratio=0.06)
                        for v in ([2.6, 0, 0], [0, 3.0, 0], [0, 0, 3.0])])
        self.play(FadeIn(plane), Create(axes))
        self.caption("平面是 A 的列空间；b 不在平面上，Ax = b 无解", "The plane is the column space of A; b is off the plane, so Ax = b has no solution", wait=0.3)
        b = np.array([1.2, 1.6, 2.2])
        p = np.array([1.2, 1.6, 0.0])
        bv = Arrow(P(np.zeros(3)), P(b), buff=0, color=BLUE, stroke_width=6)
        bl = MathTex(r"\boldsymbol b", color=BLUE, font_size=40).next_to(P(b), UP, buff=0.1)
        self.play(GrowArrow(bv), FadeIn(bl))
        u, v = ValueTracker(-0.6), ValueTracker(2.8)

        def probe():
            q = np.array([u.get_value(), v.get_value(), 0.0])
            d = float(np.linalg.norm(b - q))
            g = VGroup(DashedLine(P(q), P(b), color=WHITE, stroke_width=2), Dot(P(q), color=ORANGE, radius=0.08),
                       MathTex(r"\boldsymbol q", color=ORANGE, font_size=34).next_to(P(q), DOWN, buff=0.1))
            g.add(bi([f"距离 ‖b − q‖ = {d:.2f}", f"distance ‖b − q‖ = {d:.2f}"], 28, ORANGE).to_corner(UR, buff=0.5).shift(DOWN * 0.8))
            return g

        pr = always_redraw(probe)
        self.play(FadeIn(pr))
        self.caption("在平面上找一点 q，让它离 b 最近", "Look for the point q in the plane that is closest to b", wait=0.2)
        self.play(u.animate.set_value(2.6), v.animate.set_value(0.4), run_time=2.5)
        self.play(u.animate.set_value(0.2), v.animate.set_value(-0.8), run_time=2)
        self.play(u.animate.set_value(p[0]), v.animate.set_value(p[1]), run_time=2.5)
        self.caption("距离最小时，b − q 恰好与平面垂直：这一点就是投影 p", "At the minimum, b − q is perpendicular to the plane: that point is the projection p", wait=0.3)
        self.play(FadeOut(pr))
        pv = Arrow(P(np.zeros(3)), P(p), buff=0, color=RED, stroke_width=6)
        ev = Arrow(P(p), P(b), buff=0, color=GREEN, stroke_width=6)
        lab = VGroup(MathTex(r"\boldsymbol p = P\boldsymbol b", color=RED, font_size=36).next_to(P(p), DOWN, buff=0.15),
                     MathTex(r"\boldsymbol e = \boldsymbol b - \boldsymbol p", color=GREEN, font_size=36).next_to(P((p + b) / 2), RIGHT, buff=0.15))
        m = 0.3
        corner = VMobject(color=WHITE, stroke_width=2).set_points_as_corners([P(p + [m, 0, 0]), P(p + [m, 0, m]), P(p + [0, 0, m])])
        self.play(GrowArrow(pv), GrowArrow(ev), FadeIn(lab), Create(corner))
        self.caption("e 垂直于平面里的每个向量，也就是 Aᵀe = 0：这正是正规方程", "e is perpendicular to every vector in the plane, i.e. Aᵀe = 0: the normal equations", wait=1.6)
        again = Dot(P(p), color=YELLOW, radius=0.11)
        self.play(Flash(P(p), color=YELLOW), FadeIn(again))
        self.caption("p 已在平面上，再投影一次它不动：P² = P", "p is already in the plane, so projecting again leaves it: P² = P", wait=1.4)
        self.card([["投影 p 是平面上离 b 最近的点", "The projection p is the point of the plane closest to b"],
                   ["误差 e = b − p 垂直于平面：Aᵀ(b − Ax̂) = 0", "The error e = b − p is perpendicular to the plane: Aᵀ(b − Ax̂) = 0"],
                   ["投影矩阵 P = A(AᵀA)⁻¹Aᵀ，P² = P，Pᵀ = P", "Projection matrix P = A(AᵀA)⁻¹Aᵀ, P² = P, Pᵀ = P"]])
