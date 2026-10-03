"""动画 14.2.1（配图 14.2.2）：平面 3R 臂（0.425、0.392、0.1 m）末端停在 P = (0.75, 0.10) m 不动，工具朝向 φ 在可行范围内转动。
腕点 W = P − l3 (cos φ, sin φ) 沿以 P 为圆心、半径 l3 的小圆移动；只有落在 2R 外圆以内的一段可用（式 (14.2.10)）。画肘下一支。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2, L3 = 0.425, 0.392, 0.1
SC = 6.0
O = np.array([-4.6, -0.6, 0.0])
P = np.array([0.75, 0.10])
R = float(np.hypot(*P))
B = math.atan2(P[1], P[0])
HALF = math.acos((R * R + L3 * L3 - (L1 + L2) ** 2) / (2 * L3 * R))
LO, HI = B - HALF, B + HALF


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


def ik3(phi):
    wx, wy = P[0] - L3 * math.cos(phi), P[1] - L3 * math.sin(phi)
    r = math.hypot(wx, wy)
    c = (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    c = max(-1.0, min(1.0, c))
    t2 = math.atan2(math.sqrt(max(0.0, 1 - c * c)), c)
    t1 = math.atan2(wy, wx) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    return t1, t2, phi - t1 - t2, (wx, wy)


class Lesson(Base):
    def construct(self):
        self.title("14.2", "末端不动，工具转向：一族解", "Tip fixed, tool turning: a family of solutions")
        phi = ValueTracker(LO + 0.03)
        arcs = VGroup()
        for a0, a1, col, dash in ((-0.25, 0.55, BLUE_C, False),):
            t = np.linspace(a0, a1, 60)
            arcs.add(VMobject(color=col, stroke_width=2).set_points_smoothly([S((L1 + L2) * math.cos(s), (L1 + L2) * math.sin(s)) for s in t]))
        lab_edge = zh("2R 的外圆", 22, BLUE_C).move_to(S(0.86 * math.cos(0.5), 0.86 * math.sin(0.5)) + RIGHT * 0.2)
        good = VMobject(color=YELLOW, stroke_width=4).set_points_smoothly(
            [S(P[0] - L3 * math.cos(f), P[1] - L3 * math.sin(f)) for f in np.linspace(LO, HI, 80)])
        bad = DashedVMobject(VMobject(color=GREY_B, stroke_width=3).set_points_smoothly(
            [S(P[0] - L3 * math.cos(f), P[1] - L3 * math.sin(f)) for f in np.linspace(HI, LO + 2 * math.pi, 40)]), num_dashes=12)
        base = Polygon(O + LEFT * 0.35 + DOWN * 0.25, O + RIGHT * 0.35 + DOWN * 0.25, O + RIGHT * 0.18, O + LEFT * 0.18,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        tip = Dot(S(*P), radius=0.1, color=RED)
        self.play(Create(arcs), FadeIn(lab_edge), FadeIn(base), FadeIn(tip))
        self.play(Create(good), Create(bad))

        def arm():
            t1, t2, t3, w = ik3(phi.get_value())
            p1 = S(L1 * math.cos(t1), L1 * math.sin(t1))
            p2 = S(*w)
            g = VGroup(Line(O, p1, color=STEEL, stroke_width=11), Line(p1, p2, color=STEEL, stroke_width=8),
                       Line(p2, S(*P), color=ORANGE, stroke_width=6),
                       Dot(O, radius=0.1, color=WHITE), Dot(p1, radius=0.09, color=WHITE), Dot(p2, radius=0.09, color=YELLOW))
            return g

        def read():
            f = math.degrees(phi.get_value())
            return MathTex(r"\varphi = %.1f^\circ" % f, font_size=36).to_corner(UR, buff=0.7).shift(DOWN * 0.7)

        a, rd = always_redraw(arm), always_redraw(read)
        self.add(a, tip, rd)
        self.caption("只给末端位置：工具朝向 φ 可以变，腕点在以 P 为圆心的小圆上",
                     "Position only: the tool angle φ may vary; the wrist moves on a small circle about P")
        self.play(phi.animate.set_value(B), run_time=4.0, rate_func=smooth)
        self.caption("腕点必须在 2R 的外圆以内：只有黄色的一段可用",
                     "The wrist must stay inside the 2R reach: only the yellow arc is usable")
        self.play(phi.animate.set_value(HI - 0.03), run_time=4.5, rate_func=smooth)
        self.caption("到达可行范围的端点：大臂、小臂伸直", "At the end of the range the upper and lower arm are straight", wait=1.0)
        self.play(phi.animate.set_value(LO + 0.03), run_time=5.0, rate_func=smooth)
        self.wait(0.5)
        self.card([["给定位置与朝向：两组解；只给位置：一族解", "Position and angle: two solutions; position only: a family"],
                   MathTex(r"\cos(\varphi - \beta) \ge \frac{r^2 + l_3^2 - (l_1 + l_2)^2}{2 r l_3}", font_size=40),
                   ["先由工具朝向定腕点，再解 2R", "Fix the wrist from the tool angle, then solve the 2R"]])
