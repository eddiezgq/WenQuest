"""动画 14.1.1（配图 14.1.1）：平面 2R 臂（l1 = 0.425 m、l2 = 0.392 m），目标点从 A = (0.45, 0.35) m 沿 OA 方向向外移动。
肘上（θ2 < 0）、肘下（θ2 > 0）两组解随目标移动；到外边界 r = l1 + l2 上合为一组（手臂伸直），越过边界后无解。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
SC = 4.0
O = np.array([-3.0, -2.0, 0.0])
BETA = math.atan2(0.35, 0.45)
R_A = math.hypot(0.45, 0.35)


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


def ik(r):
    """返回 [(θ1, θ2) 肘下, 肘上]；无解时返回 []。"""
    c = (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if c > 1 + 1e-12:
        return []
    c = min(1.0, c)
    s = math.sqrt(max(0.0, 1 - c * c))
    out = []
    for sg in (1.0, -1.0):
        t2 = math.atan2(sg * s, c)
        t1 = BETA - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
        out.append((t1, t2))
    return out


class Lesson(Base):
    def construct(self):
        self.title("14.1", "同一个目标，两种手臂", "One target, two arms")
        r = ValueTracker(R_A)

        ring = Annulus(inner_radius=SC * abs(L1 - L2), outer_radius=SC * (L1 + L2), color=BLUE_E, fill_opacity=0.25,
                       stroke_width=0).move_to(O)
        edge = Circle(radius=SC * (L1 + L2), color=BLUE_C, stroke_width=2).move_to(O)
        base = Polygon(O + LEFT * 0.35 + DOWN * 0.25, O + RIGHT * 0.35 + DOWN * 0.25, O + RIGHT * 0.18, O + LEFT * 0.18,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        ray = DashedLine(O, S(0.95 * math.cos(BETA), 0.95 * math.sin(BETA)), color=GREY_B, stroke_width=2)
        self.play(FadeIn(ring), Create(edge), FadeIn(base), Create(ray))

        def target():
            rr = r.get_value()
            p = S(rr * math.cos(BETA), rr * math.sin(BETA))
            ok = rr <= L1 + L2 + 1e-9
            return VGroup(Dot(p, radius=0.09, color=RED if ok else GREY_B),
                          Cross(stroke_color=RED, stroke_width=4).scale(0.14).move_to(p) if not ok else VGroup())

        def arms():
            g = VGroup()
            sols = ik(r.get_value())
            for (t1, t2), col in zip(sols, (ORANGE, BLUE)):
                e = S(L1 * math.cos(t1), L1 * math.sin(t1))
                tip = S(L1 * math.cos(t1) + L2 * math.cos(t1 + t2), L1 * math.sin(t1) + L2 * math.sin(t1 + t2))
                g.add(Line(O, e, color=col, stroke_width=10), Line(e, tip, color=col, stroke_width=7),
                      Dot(e, radius=0.09, color=WHITE), Dot(O, radius=0.1, color=WHITE))
            return g

        def info():
            rr = r.get_value()
            n = len(ik(rr))
            if n == 2 and abs(ik(rr)[0][1]) < 1e-6:
                n = 1
            txt = MathTex(r"r = %.3f\ \mathrm{m}" % rr, font_size=34, color=WHITE)
            lab = zh(["无解", "一组解", "两组解"][min(n, 2)], 28, YELLOW)
            return VGroup(txt, lab).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.6)

        tg, ar, inf = always_redraw(target), always_redraw(arms), always_redraw(info)
        self.add(ar, tg, inf)
        leg = VGroup(VGroup(Line(ORIGIN, RIGHT * 0.5, color=ORANGE, stroke_width=8), zh("肘下", 22, ORANGE)).arrange(RIGHT, buff=0.15),
                     VGroup(Line(ORIGIN, RIGHT * 0.5, color=BLUE, stroke_width=8), zh("肘上", 22, BLUE)).arrange(RIGHT, buff=0.15)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UL, buff=0.6).shift(DOWN * 1.2)
        self.play(FadeIn(leg))
        self.caption("圆环内的目标有两组解：肘上、肘下，关于基座—目标连线对称",
                     "Inside the ring there are two solutions, mirror images about the base–target line")
        self.play(r.animate.set_value(0.75), run_time=3.0, rate_func=smooth)
        self.caption("目标越靠近外边界，两组解越接近", "The nearer the outer edge, the closer the two solutions")
        self.play(r.animate.set_value(L1 + L2), run_time=3.0, rate_func=smooth)
        self.caption("恰在外边界上：手臂伸直，两组解合为一组", "On the edge: the arm is straight, the two become one", wait=1.5)
        self.play(r.animate.set_value(0.9), run_time=2.0, rate_func=linear)
        self.caption("越过边界：够不着，没有解", "Beyond the edge: out of reach, no solution", wait=1.2)
        self.play(r.animate.set_value(R_A), run_time=2.5, rate_func=smooth)
        self.wait(0.5)
        self.card([["2R 臂：圆环内两组，边界上一组，环外无解", "2R arm: two inside the ring, one on its edge, none outside"],
                   MathTex(r"|l_1 - l_2| < r < l_1 + l_2", font_size=40),
                   ["两组解只在奇异位形（伸直、折回）处相遇", "The two meet only at singular postures (straight, folded)"]])
