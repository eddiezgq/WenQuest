"""动画 14.3.1（配图 14.3.2）：子问题 2。两根轴交于 r（原点），ω1 竖直（z），ω2 水平（x）。
p 绕 ω2 转一圈画出一个圆，q 绕 ω1 反向转一圈画出另一个圆；两圆交于 c1、c2（式 (14.3.6)–(14.3.8)）。
然后演示第一组解：p 绕 ω2 转到 c1，再绕 ω1 转到 q。三维点用 wq_anim.proj3 斜投影到屏幕上。"""
from manim import *
from wq_anim import *
import numpy as np
import math

ORG = np.array([0.6, -0.6, 0.0])
SC = 2.6
W1 = np.array([0.0, 0.0, 1.0])
W2 = np.array([1.0, 0.0, 0.0])


def rot(w, t):
    w = np.asarray(w, float)
    K = np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def P3(v):
    return proj3(v, ORG, SC)


p = np.array([0.35, 0.55, 0.62])
p = p / np.linalg.norm(p)
q = rot(W1, math.radians(70)) @ rot(W2, math.radians(-60)) @ p
k = W1 @ W2
al = (k * (W2 @ p) - W1 @ q) / (k * k - 1)
be = (k * (W1 @ q) - W2 @ p) / (k * k - 1)
n = np.cross(W1, W2)
ga = math.sqrt((p @ p - al * al - be * be - 2 * al * be * k) / (n @ n))
C1 = al * W1 + be * W2 + ga * n
C2 = al * W1 + be * W2 - ga * n


def ang(w, a, b):
    a2, b2 = a - w * (w @ a), b - w * (w @ b)
    return math.atan2(w @ np.cross(a2, b2), a2 @ b2)


T2 = ang(W2, p, C1)
T1 = ang(W1, C1, q)


def circle_pts(w, v, t0=0.0, t1=2 * math.pi, n=90):
    return [P3(rot(w, t) @ v) for t in np.linspace(t0, t1, n)]


class Lesson(Base):
    def construct(self):
        self.title("14.3", "子问题 2：两个圆的交点", "Subproblem 2: where two circles meet")
        sphere = VGroup()
        for lat in (-60, -30, 0, 30, 60):
            z, rr = math.sin(math.radians(lat)), math.cos(math.radians(lat))
            sphere.add(VMobject(color=GREY_D, stroke_width=1).set_points_smoothly(
                [P3(np.array([rr * math.cos(t), rr * math.sin(t), z])) for t in np.linspace(0, 2 * math.pi, 60)]))
        for lon in (0, 45, 90, 135):
            a = math.radians(lon)
            sphere.add(VMobject(color=GREY_D, stroke_width=1).set_points_smoothly(
                [P3(np.array([math.cos(t) * math.cos(a), math.cos(t) * math.sin(a), math.sin(t)])) for t in np.linspace(0, 2 * math.pi, 60)]))
        ax1 = Arrow(P3(-1.3 * W1), P3(1.4 * W1), buff=0, color=WHITE, stroke_width=4)
        ax2 = Arrow(P3(-1.3 * W2), P3(1.6 * W2), buff=0, color=WHITE, stroke_width=4)
        l1 = MathTex(r"\omega_1", font_size=34).next_to(ax1.get_end(), UP, buff=0.1)
        l2 = MathTex(r"\omega_2", font_size=34).next_to(ax2.get_end(), DOWN, buff=0.1)
        rdot = Dot(P3(np.zeros(3)), radius=0.06, color=WHITE)
        rlab = MathTex("r", font_size=30).next_to(rdot, DR, buff=0.08)
        self.play(FadeIn(sphere), GrowArrow(ax1), GrowArrow(ax2), FadeIn(l1), FadeIn(l2), FadeIn(rdot), FadeIn(rlab))
        pd = Dot(P3(p), radius=0.09, color=BLUE)
        qd = Dot(P3(q), radius=0.09, color=RED)
        pl = MathTex("p", font_size=32, color=BLUE).next_to(pd, UR, buff=0.06)
        ql = MathTex("q", font_size=32, color=RED).next_to(qd, UL, buff=0.06)
        self.play(FadeIn(pd), FadeIn(ql), FadeIn(qd), FadeIn(pl))
        self.caption("要求 θ₁、θ₂：先绕 ω₂ 转，再绕 ω₁ 转，把 p 送到 q",
                     "Find θ₁, θ₂: turn about ω₂, then about ω₁, taking p to q", wait=0.8)

        cp = VMobject(color=BLUE, stroke_width=4).set_points_smoothly(circle_pts(W2, p))
        cq = VMobject(color=RED, stroke_width=4).set_points_smoothly(circle_pts(W1, q, 0, -2 * math.pi))
        mp = Dot(P3(p), radius=0.07, color=BLUE)
        self.caption("p 绕 ω₂ 转动，走蓝色的圆", "p turning about ω₂ traces the blue circle", wait=0)
        self.play(Create(cp), MoveAlongPath(mp, cp), run_time=3.0, rate_func=linear)
        mq = Dot(P3(q), radius=0.07, color=RED)
        self.caption("q 绕 ω₁ 反向转动，走红色的圆", "q turned back about ω₁ traces the red circle", wait=0)
        self.play(Create(cq), MoveAlongPath(mq, cq), run_time=3.0, rate_func=linear)
        self.play(FadeOut(mp), FadeOut(mq), run_time=0.3)
        c1d = Dot(P3(C1), radius=0.11, color=YELLOW)
        c2d = Dot(P3(C2), radius=0.11, color=YELLOW)
        c1l = MathTex("c_1", font_size=32, color=YELLOW).next_to(c1d, RIGHT, buff=0.08)
        c2l = MathTex("c_2", font_size=32, color=YELLOW).next_to(c2d, LEFT, buff=0.08)
        self.play(FadeIn(c1d, scale=1.6), FadeIn(c2d, scale=1.6), FadeIn(c1l), FadeIn(c2l))
        self.caption("两圆都在以 r 为球心的球面上，交于 c₁、c₂：两组解",
                     "Both circles lie on a sphere about r; they meet at c₁ and c₂: two solutions", wait=1.0)

        mv = Dot(P3(p), radius=0.1, color=ORANGE)
        path1 = VMobject(color=ORANGE, stroke_width=5).set_points_smoothly(circle_pts(W2, p, 0, T2, 40))
        path2 = VMobject(color=ORANGE, stroke_width=5).set_points_smoothly(circle_pts(W1, C1, 0, T1, 40))
        self.add(mv)
        self.caption(f"绕 ω₂ 转 θ₂ = {math.degrees(T2):.1f}°，到达 c₁", f"Turn θ₂ = {math.degrees(T2):.1f}° about ω₂ to reach c₁", wait=0)
        self.play(Create(path1), MoveAlongPath(mv, path1), run_time=2.0)
        self.caption(f"再绕 ω₁ 转 θ₁ = {math.degrees(T1):.1f}°，到达 q", f"Then θ₁ = {math.degrees(T1):.1f}° about ω₁ to reach q", wait=0)
        self.play(Create(path2), MoveAlongPath(mv, path2), run_time=2.0)
        self.wait(1.0)
        self.card([["子问题 2：中间点 c 在两个圆的交点上", "Subproblem 2: the middle point c is where two circles meet"],
                   MathTex(r"c - r = \alpha\,\hat\omega_1 + \beta\,\hat\omega_2 + \gamma\,\hat\omega_1\times\hat\omega_2", font_size=40),
                   ["求出 c 后，θ₂、θ₁ 各是一次子问题 1", "Once c is known, θ₂ and θ₁ are each a Subproblem 1"]])
