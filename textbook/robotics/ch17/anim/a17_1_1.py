"""动画 17.1.1（配图 17.1.1）：平面 3R 臂（0.425、0.392、0.1 m）只管末端位置，末端停在 B = (0.75, 0.10) m 不动。
以工具朝向 φ 为参数：腕点在以 B 为圆心、半径 0.1 m 的小圆上，只有落在 2R 外圆以内的一段可用（式 (14.2.10)）。
手臂先沿肘下的一族（θ₂ > 0，第 14 章的约定）把 φ 从一端走到另一端，在 θ₂ = 0 处变为肘上的一族，再走回起点：一条闭曲线（算例 17.1.1）。
右侧同步画出 (θ₁, θ₂) 平面上的闭曲线和当前的点。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L = (0.425, 0.392, 0.1)
PB = np.array([0.75, 0.10])
SC = 5.2
O = np.array([-6.0, -0.9, 0.0])


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def ik2(x, y, up):
    c2 = (x * x + y * y - L[0] ** 2 - L[1] ** 2) / (2 * L[0] * L[1])
    c2 = max(-1.0, min(1.0, c2))
    t2 = math.acos(c2) * (1 if up else -1)
    t1 = math.atan2(y, x) - math.atan2(L[1] * math.sin(t2), L[0] + L[1] * math.cos(t2))
    return t1, t2


def joints(th):
    pts, a = [np.zeros(2)], 0.0
    for t, l in zip(th, L):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return pts


# φ 的可行区间（腕点落在 2R 外圆以内）
r = float(np.linalg.norm(PB))
beta = math.atan2(PB[1], PB[0])
half = math.acos((r * r + L[2] ** 2 - (L[0] + L[1]) ** 2) / (2 * r * L[2]))
PHIS = np.linspace(beta - half + 1e-6, beta + half - 1e-6, 120)


def branch(up):
    out = []
    for f in PHIS:
        w = PB - L[2] * np.array([math.cos(f), math.sin(f)])
        t1, t2 = ik2(w[0], w[1], up)
        out.append(np.array([t1, t2, wrap(f - t1 - t2)]))
    return out


LOOP = branch(True) + branch(False)[::-1]          # 肘下（θ₂ > 0）从一端到另一端，再沿肘上走回来
LOOP.append(LOOP[0])


class Lesson(Base):
    def construct(self):
        self.title("17.1", "自运动：末端不动，手臂在动", "Self-motion: the tip stays, the arm moves")
        base = Polygon(O + LEFT * 0.35 + DOWN * 0.25, O + RIGHT * 0.35 + DOWN * 0.25, O + RIGHT * 0.18, O + LEFT * 0.18,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        R2 = L[0] + L[1]
        outer = DashedVMobject(Arc(radius=SC * R2, start_angle=-0.25, angle=0.7, arc_center=O, color=GREY_B, stroke_width=2), num_dashes=24)
        ol = zh("2R 外圆", 18, GREY_B).move_to(S(R2 * math.cos(0.5), R2 * math.sin(0.5)) + RIGHT * 0.55)
        tgt = Dot(S(*PB), radius=0.08, color=RED)
        tl = Text("B", font=LATIN, font_size=26, color=RED).move_to(S(*PB) + np.array([0.15, 0.95, 0]))
        ts = np.linspace(0, 2 * math.pi, 160)
        small = DashedVMobject(Circle(radius=SC * L[2], color=GREY_C, stroke_width=1.5).move_to(S(*PB)), num_dashes=30)
        good = VMobject(color=YELLOW, stroke_width=3).set_points_smoothly([S(*(PB - L[2] * np.array([math.cos(f), math.sin(f)]))) for f in PHIS])

        ax = Axes(x_range=[-45, 60, 15], y_range=[-90, 90, 30], x_length=4.6, y_length=4.6,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 18}, tips=False).to_edge(RIGHT, buff=0.6).shift(DOWN * 0.15)
        xl = MathTex(r"\theta_1\,/\,^\circ", font_size=26).next_to(ax.x_axis.get_right(), UP, buff=0.15).shift(LEFT * 0.2)
        yl = MathTex(r"\theta_2\,/\,^\circ", font_size=26).next_to(ax.y_axis, UP, buff=0.1)
        curve = VMobject(color=TEAL, stroke_width=3).set_points_as_corners([ax.c2p(math.degrees(q[0]), math.degrees(q[1])) for q in LOOP])

        self.play(FadeIn(base), Create(outer), FadeIn(ol), FadeIn(tgt), FadeIn(tl), run_time=1.0)
        k = ValueTracker(0.0)

        def cur():
            x = k.get_value()
            i = min(int(x), len(LOOP) - 2)
            a = x - i
            return (1 - a) * LOOP[i] + a * LOOP[i + 1]

        def arm():
            pts = [S(*p) for p in joints(cur())]
            g = VGroup(Line(pts[0], pts[1], color=STEEL, stroke_width=12), Line(pts[1], pts[2], color=STEEL, stroke_width=9),
                       Line(pts[2], pts[3], color=ORANGE, stroke_width=7))
            for q in pts[:3]:
                g.add(Dot(q, radius=0.07, color=WHITE))
            return g

        def info():
            th = cur()
            phi = math.degrees(sum(th))
            return VGroup(MathTex(r"\theta_2 = %.1f^\circ" % math.degrees(th[1]), font_size=28),
                          MathTex(r"\varphi = %.1f^\circ" % phi, font_size=28)).arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to(LEFT * 1.0 + UP * 2.3)

        arm_m = always_redraw(arm)
        inf = always_redraw(info)
        self.play(FadeIn(arm_m), FadeIn(inf))
        self.caption("末端停在 B；三个关节、两个位置方程，还剩一个自由度",
                     "The tip stays at B: three joints, two position equations, one freedom left", wait=1.0)
        self.play(Create(small), Create(good), run_time=1.0)
        self.caption("腕点只能在以 B 为圆心的小圆上，而且不能超出 2R 外圆（黄色一段）",
                     "The wrist lies on the small circle around B, inside the 2R reach (yellow arc)", wait=1.0)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.0)
        dot = always_redraw(lambda: Dot(ax.c2p(math.degrees(cur()[0]), math.degrees(cur()[1])), radius=0.08, color=YELLOW))
        trail = TracedPath(dot.get_center, stroke_color=TEAL, stroke_width=3)
        self.add(trail, dot)
        n_up = len(PHIS)
        self.caption("沿肘下的一族（θ₂ > 0）走：φ 从可行区间的一端转到另一端",
                     "Along the elbow-down family (θ₂ > 0): φ runs from one end of its range to the other", wait=0)
        self.play(k.animate.set_value(n_up - 1), run_time=5.0, rate_func=linear)
        self.caption("到头时腕点在外圆上，θ₂ = 0：肘下、肘上两族在这里相接",
                     "At the end the wrist is on the outer circle, θ₂ = 0: the two families join here", wait=1.2)
        self.caption("接着沿肘上的一族（θ₂ < 0）走回来，回到起点：一条闭曲线",
                     "Then back along the elbow-up family (θ₂ < 0) to the start: one closed curve", wait=0)
        self.play(k.animate.set_value(len(LOOP) - 1), run_time=5.0, rate_func=linear)
        self.add(curve)
        self.caption("整个过程中末端一直在 B：这条曲线就是 B 的自运动流形",
                     "The tip never left B: this curve is the self-motion manifold of B", wait=1.5)
        self.card([["自运动流形", "Self-motion manifold"],
                   MathTex(r"\Theta(x_d) = \{\theta : f(\theta) = x_d\},\quad \dim = n - m", font_size=38),
                   MathTex(r"T_\theta\Theta = N\big(J(\theta)\big)", font_size=38),
                   ["冗余度为 1 时，它由若干条闭曲线组成", "With one degree of redundancy it consists of closed curves"]])
