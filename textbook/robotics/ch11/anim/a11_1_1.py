"""动画 11.1.1（配图 11.1.1）：七种关节依次运动。灰色构件 A 不动，蓝色构件 B 按关节允许的方式运动。"""
from manim import *
from wq_anim import *
import numpy as np

O = np.array([-1.2, -0.9, 0.0])     # 关节中心在屏幕上的位置
SC = 1.7


def P(p):
    return proj3(p, O, SC)


def rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1.0, 0, 0], [0, c, -s], [0, s, c]])


def ry(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s], [0, 1.0, 0], [-s, 0, c]])


# 构件 B：一根竖杆和一根横臂（看得出转动），坐标为 B 自己的坐标系
ROD = [(np.array([0, 0, 0.0]), np.array([0, 0, 1.1])), (np.array([0, 0, 0.95]), np.array([0.75, 0, 0.95]))]


def pose(kind, s):
    """关节变量随 s ∈ [0, 1] 变化时 B 的姿态 R 和位置 p。"""
    w = np.sin(np.pi * s)                 # 0 → 1 → 0
    if kind == "R":
        return rz(1.6 * np.pi * s), np.zeros(3)
    if kind == "P":
        return np.eye(3), np.array([0, 0, 0.55 * w])
    if kind == "H":
        th = 2.4 * np.pi * s
        return rz(th), np.array([0, 0, -0.09 * th])
    if kind == "C":
        return rz(1.2 * np.pi * s), np.array([0, 0, 0.45 * np.sin(2 * np.pi * s)])
    if kind == "U":
        return rx(0.5 * np.sin(2 * np.pi * s)) @ ry(0.5 * np.sin(np.pi * s)), np.zeros(3)
    if kind == "S":
        return rz(1.4 * np.pi * s) @ rx(0.55 * w) @ ry(0.3 * np.sin(2 * np.pi * s)), np.zeros(3)
    # E：平面内平移和绕竖直轴的转动
    return rz(0.9 * np.pi * s), np.array([0.5 * np.sin(2 * np.pi * s), 0.6 * w, 0.0])


def body_b(kind, s):
    R, p = pose(kind, s)
    g = VGroup()
    if kind == "E":
        pts = [np.array([x, y, 0.15]) for x, y in ((-0.35, -0.25), (0.35, -0.25), (0.35, 0.25), (-0.35, 0.25))]
        q = [P(R @ v + p) for v in pts]
        g.add(Polygon(*q, color=BLUE, fill_color=BLUE_E, fill_opacity=0.9, stroke_width=3))
        g.add(Line(P(R @ np.array([0, 0, 0.15]) + p), P(R @ np.array([0.55, 0, 0.15]) + p), color=YELLOW, stroke_width=5))
        return g
    for a, b in ROD:
        g.add(Line(P(R @ a + p), P(R @ b + p), color=BLUE, stroke_width=11 if a[2] == 0 else 8))
    g.add(Dot(P(R @ ROD[1][1] + p), radius=0.07, color=YELLOW))
    return g


def body_a(kind):
    g = VGroup()
    grey = dict(color=GREY_B, fill_color=GREY_D, fill_opacity=1, stroke_width=2)
    if kind in ("R", "H", "C"):
        h0, h1 = (-1.0, 0.0) if kind == "R" else (-0.25, 0.15)
        r = 0.28
        ring = [P(np.array([r * np.cos(t), r * np.sin(t), h1])) for t in np.linspace(0, 2 * np.pi, 40)]
        ring0 = [P(np.array([r * np.cos(t), r * np.sin(t), h0])) for t in np.linspace(0, 2 * np.pi, 40)]
        i0 = int(np.argmin([q[0] for q in ring]))
        i1 = int(np.argmax([q[0] for q in ring]))
        g.add(Polygon(*ring0, color=GREY_B, fill_color=GREY_E, fill_opacity=0.8, stroke_width=2))
        g.add(Polygon(ring0[i0], ring0[i1], ring[i1], ring[i0], color=GREY_E, fill_color=GREY_E, fill_opacity=0.8, stroke_width=0))
        g.add(Line(ring0[i0], ring[i0], color=GREY_B, stroke_width=2), Line(ring0[i1], ring[i1], color=GREY_B, stroke_width=2))
        g.add(Polygon(*ring, color=GREY_B, fill_color=GREY_D, fill_opacity=0.9, stroke_width=2))
        if kind != "R":
            g.add(DashedLine(P(np.array([0, 0, -1.3])), P(np.array([0, 0, 1.3])), color=GREY_B, stroke_width=2))
    elif kind == "P":
        c = [np.array([x, y, z]) for z in (-0.6, 0.2) for x, y in ((-0.2, -0.2), (0.2, -0.2), (0.2, 0.2), (-0.2, 0.2))]
        for i in range(4):
            g.add(Line(P(c[i]), P(c[(i + 1) % 4]), color=GREY_B), Line(P(c[4 + i]), P(c[4 + (i + 1) % 4]), color=GREY_B),
                  Line(P(c[i]), P(c[4 + i]), color=GREY_B))
    elif kind in ("U", "S"):
        g.add(Line(P(np.array([0, 0, -1.0])), P(np.array([0, 0, -0.25])), color=GREY_B, stroke_width=12))
        if kind == "U":
            g.add(Line(P(np.array([-0.3, 0, -0.25])), P(np.array([0.3, 0, -0.25])), color=GREY_B, stroke_width=8))
            g.add(Line(P(np.array([-0.32, 0, 0])), P(np.array([0.32, 0, 0])), color=ORANGE, stroke_width=6))
            g.add(Line(P(np.array([0, -0.32, 0])), P(np.array([0, 0.32, 0])), color=ORANGE, stroke_width=6))
        else:
            g.add(Circle(radius=0.3 * SC, color=GREY_B, stroke_width=3).move_to(P(np.zeros(3))))
            g.add(Dot(P(np.zeros(3)), radius=0.16, color=GREY_C))
    else:
        c = [np.array([x, y, 0.0]) for x, y in ((-1.1, -0.9), (1.1, -0.9), (1.1, 1.0), (-1.1, 1.0))]
        g.add(Polygon(*[P(v) for v in c], color=GREY_B, fill_color=GREY_E, fill_opacity=0.6, stroke_width=2))
    return g


JOINTS = [
    ("R", "转动关节 R：绕一根轴转动", "Revolute R: turns about one axis", 1),
    ("P", "移动关节 P：沿一个方向滑动", "Prismatic P: slides along one direction", 1),
    ("H", "螺旋副 H：每转一个角度，沿轴前进一段", "Helical H: advances along the axis as it turns", 1),
    ("C", "圆柱副 C：可转、可滑，互不影响", "Cylindrical C: turns and slides independently", 2),
    ("U", "万向节 U：绕两根相交的轴摆动", "Universal U: swings about two crossing axes", 2),
    ("S", "球关节 S：绕球心任意转动", "Spherical S: any rotation about the centre", 3),
    ("E", "平面副 E：在平面上平移和转动", "Planar E: slides and turns on a plane", 3),
]


class Lesson(Base):
    def construct(self):
        self.title("11.1", "关节即旋量：七种关节", "Joints as screws: seven joint types")
        s = ValueTracker(0.0)
        for kind, zt, et, f in JOINTS:
            a = body_a(kind)
            b = always_redraw(lambda k=kind: body_b(k, s.get_value()))
            tag = VGroup(MathTex(r"\mathrm{%s}" % kind, font_size=72, color=YELLOW),
                         MathTex(r"f = %d,\quad c = %d" % (f, 6 - f), font_size=40)).arrange(DOWN, buff=0.25).move_to([4.0, 0.6, 0])
            trace = None
            if kind == "H":
                trace = TracedPath(lambda: P(pose("H", s.get_value())[0] @ ROD[1][1] + pose("H", s.get_value())[1]),
                                   stroke_color=ORANGE, stroke_width=3)
            s.set_value(0.0)
            self.play(FadeIn(a), FadeIn(b), FadeIn(tag), run_time=0.4)
            if trace is not None:
                self.add(trace)
            self.caption(zt, et, wait=0)
            self.play(s.animate.set_value(1.0), run_time=2.0, rate_func=linear)
            gone = [a, b, tag] + ([trace] if trace is not None else [])
            self.play(*[FadeOut(m) for m in gone], run_time=0.3)
        self.card([["一个关节 = 一组旋量轴", "A joint = a set of screw axes"],
                   MathTex(r"\mathcal{V} = \mathcal{S}_1\dot\theta_1 + \cdots + \mathcal{S}_k\dot\theta_k,\qquad f = \mathrm{rank}\,(\mathcal{S}_1\ \cdots\ \mathcal{S}_k)", font_size=40),
                   ["约束数 c = 6 − f", "constraints c = 6 − f"]])
