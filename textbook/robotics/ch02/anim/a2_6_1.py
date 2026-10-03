"""动画 2.6.1（配图 2.6.1）：平面 3R 臂末端停在原处，手臂连续改变形态；同时画出当前形态下的零空间方向（三个关节速度的比例）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2, L3 = 0.425, 0.392, 0.1


def fk(th):
    pts, a = [np.zeros(2)], 0.0
    for t, l in zip(th, (L1, L2, L3)):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return pts


def ik_rest(t1, p):
    e = np.array([L1 * math.cos(t1), L1 * math.sin(t1)])
    q = p - e
    c3 = (q @ q - L2 ** 2 - L3 ** 2) / (2 * L2 * L3)
    t3 = -math.acos(max(-1.0, min(1.0, c3)))
    a = math.atan2(q[1], q[0]) - math.atan2(L3 * math.sin(t3), L2 + L3 * math.cos(t3))
    return [t1, a - t1, t3]


def null_dir(th):
    pts = fk(th)
    tip = pts[3]
    J = np.array([[-(tip[1] - pts[i][1]) for i in range(3)], [tip[0] - pts[i][0] for i in range(3)]])
    n = np.cross(J[0], J[1])
    n = n / np.linalg.norm(n)
    return n if n[2] > 0 else -n


class Lesson(Base):
    def construct(self):
        self.title("2.6", "自运动：末端不动，手臂在动", "Self-motion: the end-effector stays, the arm moves")
        tip = fk([math.radians(30), math.radians(60), math.radians(-60)])[3]
        U = 5.2
        O = np.array([-4.6, -2.4, 0])
        t1 = ValueTracker(30.0)

        def P(v):
            return O + U * np.array([v[0], v[1], 0])

        def arm():
            th = ik_rest(math.radians(t1.get_value()), tip)
            pts = [P(p) for p in fk(th)]
            g = VGroup(Polygon(pts[0] + LEFT * 0.35 + DOWN * 0.25, pts[0] + RIGHT * 0.35 + DOWN * 0.25, pts[0] + RIGHT * 0.15, pts[0] + LEFT * 0.15,
                               color=GREY_B, fill_color=GREY_E, fill_opacity=1))
            for i, w in enumerate((14, 10, 7)):
                g.add(Line(pts[i], pts[i + 1], color=STEEL, stroke_width=w))
            for p in pts[:3]:
                g.add(Dot(p, radius=0.09, color=WHITE))
            return g

        def bars():
            th = ik_rest(math.radians(t1.get_value()), tip)
            n = null_dir(th)
            base = np.array([3.0, -0.1, 0])
            g = VGroup(Line(base + LEFT * 0.4, base + RIGHT * 2.6, color=GREY_B))
            for i in range(3):
                x = base + RIGHT * (0.2 + 0.8 * i)
                hgt = 1.6 * n[i]
                g.add(Rectangle(width=0.5, height=max(abs(hgt), 0.01), color=YELLOW, fill_color=YELLOW, fill_opacity=0.7).move_to(x + UP * hgt / 2))
                g.add(MathTex(r"\dot\theta_%d" % (i + 1), font_size=30).move_to(x + DOWN * 2.0))
            g.add(bi(["零空间方向 n", "null-space direction n"], 24).move_to(base + UP * 2.2 + RIGHT * 1.0))
            g.add(MathTex(r"\theta_1 = %.0f^\circ" % t1.get_value(), color=YELLOW, font_size=32).move_to(base + DOWN * 2.45 + RIGHT * 1.0))
            return g

        trail = TracedPath(lambda: P(fk(ik_rest(math.radians(t1.get_value()), tip))[1]), stroke_color=GREY_B, stroke_width=2)
        a = always_redraw(arm)
        b = always_redraw(bars)
        star = Star(5, outer_radius=0.16, color=YELLOW, fill_opacity=1).move_to(P(tip))
        self.add(trail, a, star)
        self.play(FadeIn(b), run_time=0.6)
        self.caption("末端（星号）不动，θ₁ 从 30° 增大到 55°", "The end-effector (star) stays; θ₁ grows from 30° to 55°", wait=0)
        self.play(t1.animate.set_value(55), run_time=4, rate_func=smooth)
        self.caption("再减小到 27°：其余两个关节随之调整", "Back down to 27°: the other two joints follow", wait=0)
        self.play(t1.animate.set_value(27), run_time=4.5, rate_func=smooth)
        self.caption("零空间方向随形态而变：它是自运动的瞬时方向", "The null-space direction changes with the shape: it is the instantaneous self-motion", wait=0)
        self.play(t1.animate.set_value(40), run_time=3, rate_func=smooth)
        self.wait(1.2)
        self.card([["零空间与自运动", "Null space and self-motion"],
                   MathTex(r"J\dot\theta = 0", font_size=48),
                   ["的解 = 末端不动的关节运动；rank J + dim N(J) = 3", "solutions = joint motions that keep the end-effector still; rank J + dim N(J) = 3"]])
