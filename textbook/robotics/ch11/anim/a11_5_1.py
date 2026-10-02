"""动画 11.5.1（配图 11.5.1）：四杆机构的构型空间。
曲柄转一周，右边 (θ1, θ3) 正方形中的点沿开式的闭曲线走一圈；换成交叉式，点走另一条曲线；
机架加长到 0.58 m（不满足格拉斯霍夫条件），曲柄转到极限位置就转不过去，点沿曲线拐回，从开式走进交叉式。"""
from manim import *
from wq_anim import *
import numpy as np
import math

S = 5.6                                  # 1 m 画成 5.6 个单位
A0 = np.array([-6.0, -0.6, 0.0])         # 曲柄铰点 A
SQ_C = np.array([3.6, -0.1, 0.0])        # 构型空间正方形的中心
SQ = 4.4                                 # 正方形边长


def u(t):
    return np.array([math.cos(t), math.sin(t), 0.0])


def rocker(L, t1, mode):
    """曲柄角 t1 时的摇杆角（mode = -1 开式，+1 交叉式）；无解返回 None。"""
    l0, l1, l2, l3 = L
    B = np.array([l1 * math.cos(t1), l1 * math.sin(t1)])
    D = np.array([l0, 0.0])
    d = np.linalg.norm(D - B)
    if d > l2 + l3 or d < abs(l2 - l3):
        return None
    a = (l3 ** 2 - l2 ** 2 + d * d) / (2 * d)
    h = math.sqrt(max(l3 ** 2 - a * a, 0.0))
    e = (B - D) / d
    C = D + a * e + mode * h * np.array([-e[1], e[0]])
    return math.atan2(C[1], C[0] - l0)


def to_sq(t1, t3):
    """(θ1, θ3)（弧度）→ 正方形中的点；θ1 ∈ [−π, π)，θ3 ∈ [0, 2π)。"""
    x = (((t1 + math.pi) % (2 * math.pi)) / (2 * math.pi) - 0.5) * SQ
    y = ((t3 % (2 * math.pi)) / (2 * math.pi) - 0.5) * SQ
    return SQ_C + np.array([x, y, 0.0])


def mech(L, t1, t3, faint=False):
    l0, l1, l2, l3 = L
    A = A0
    D = A0 + S * np.array([l0, 0, 0])
    B = A + S * l1 * u(t1)
    C = D + S * l3 * u(t3)
    op = 0.35 if faint else 1.0
    g = VGroup(DashedLine(A, D, color=GREY_B, stroke_width=2),
               Line(A, B, color=BLUE, stroke_width=9, stroke_opacity=op),
               Line(B, C, color=ORANGE, stroke_width=9, stroke_opacity=op),
               Line(D, C, color=BLUE, stroke_width=9, stroke_opacity=op))
    for P in (A, B, C, D):
        g.add(Dot(P, radius=0.08, color=WHITE))
    for P in (A, D):
        g.add(Triangle(color=GREY_B, fill_opacity=0.4).scale(0.17).move_to(P + DOWN * 0.2))
    return g


def curve(L, mode, color):
    pts, seg = [], VGroup()
    for t1 in np.linspace(-math.pi, math.pi, 721):
        t3 = rocker(L, t1, mode)
        if t3 is None:
            continue
        p = to_sq(t1, t3)
        if pts and np.linalg.norm(p - pts[-1]) > SQ / 2:
            seg.add(VMobject(color=color, stroke_width=3).set_points_smoothly(pts))
            pts = []
        pts.append(p)
    if len(pts) > 1:
        seg.add(VMobject(color=color, stroke_width=3).set_points_smoothly(pts))
    return seg


class Lesson(Base):
    def construct(self):
        self.title("11.5", "闭链的构型空间：四杆机构", "The C-space of a closed chain: the four-bar")
        # ---------- 构型空间正方形
        box = Square(SQ, color=GREY_B, stroke_width=2, fill_color=NAVY, fill_opacity=0.35).move_to(SQ_C)
        xl = MathTex(r"\theta_1", font_size=34).next_to(box, DOWN, buff=0.15)
        yl = MathTex(r"\theta_3", font_size=34).next_to(box, LEFT, buff=0.15)
        ticks = VGroup(MathTex(r"-180^\circ", font_size=22).next_to(box.get_corner(DL), DOWN, buff=0.08),
                       MathTex(r"180^\circ", font_size=22).next_to(box.get_corner(DR), DOWN, buff=0.08),
                       MathTex(r"0^\circ", font_size=22).next_to(box.get_corner(DL), LEFT, buff=0.08),
                       MathTex(r"360^\circ", font_size=22).next_to(box.get_corner(UL), LEFT, buff=0.08))
        self.play(Create(box), FadeIn(xl, yl, ticks), run_time=0.8)

        # ---------- 1. 曲柄摇杆机构，开式
        L = (0.40, 0.15, 0.35, 0.30)
        t = ValueTracker(-math.pi)

        def open_mech():
            return mech(L, t.get_value(), rocker(L, t.get_value(), -1))

        m = always_redraw(open_mech)
        dot = always_redraw(lambda: Dot(to_sq(t.get_value(), rocker(L, t.get_value(), -1)), radius=0.09, color=YELLOW))
        cv_open = curve(L, -1, BLUE)
        eq = MathTex(r"l_1 e(\theta_1) + l_2 e(\theta_2) - l_3 e(\theta_3) - l_0 e(0) = 0", font_size=30).move_to([-3.4, 2.2, 0])
        self.play(FadeIn(m), FadeIn(dot), Write(eq), run_time=0.9)
        self.caption("曲柄转一整周，摇杆来回摆；构型空间中的点沿一条闭曲线走一圈",
                     "The crank turns once, the rocker swings; the point runs once round a closed curve", wait=0)
        self.play(t.animate.set_value(math.pi), Create(cv_open), run_time=4.5, rate_func=linear)

        # ---------- 2. 交叉式
        self.play(FadeOut(m), FadeOut(dot), run_time=0.2)
        t.set_value(-math.pi)
        m2 = always_redraw(lambda: mech(L, t.get_value(), rocker(L, t.get_value(), 1)))
        dot2 = always_redraw(lambda: Dot(to_sq(t.get_value(), rocker(L, t.get_value(), 1)), radius=0.09, color=YELLOW))
        cv_cross = curve(L, 1, ORANGE)
        self.add(m2, dot2)
        self.caption("同样的曲柄角，另一种装配模式（交叉式）：点走另一条曲线，两条曲线互不相交",
                     "Same crank angles, the other assembly mode (crossed): a second curve, never meeting the first", wait=0)
        self.play(t.animate.set_value(math.pi), Create(cv_cross), run_time=4.0, rate_func=linear)
        self.play(FadeOut(m2), FadeOut(dot2), run_time=0.4)

        # ---------- 3. 机架加长到 0.58 m：一条闭曲线，经过极限位置
        Ln = (0.58, 0.15, 0.35, 0.30)
        tl = math.acos((Ln[1] ** 2 + Ln[0] ** 2 - (Ln[2] + Ln[3]) ** 2) / (2 * Ln[1] * Ln[0])) - 1e-6
        th = np.linspace(-tl, tl, 400)
        loop = [(a, rocker(Ln, a, -1)) for a in th] + [(a, rocker(Ln, a, 1)) for a in th[::-1]]
        s = ValueTracker(0.0)

        def state():
            k = min(int(s.get_value() * (len(loop) - 1)), len(loop) - 1)
            return loop[k]

        m3 = always_redraw(lambda: mech(Ln, *state()))
        dot3 = always_redraw(lambda: Dot(to_sq(*state()), radius=0.09, color=YELLOW))
        cv_ng = VMobject(color=GREY_A, stroke_width=3).set_points_smoothly([to_sq(a, b) for a, b in loop] + [to_sq(*loop[0])])
        cv_ng.set_stroke(opacity=0.9)
        lims = VGroup(*[Dot(to_sq(*loop[k]), radius=0.08, color=RED) for k in (0, len(th) - 1)])
        self.play(FadeOut(cv_open, cv_cross), FadeIn(m3), FadeIn(dot3), run_time=0.6)
        self.caption("机架加长到 0.58 m：s + l > p + q，曲柄转到极限位置（红点）就转不过去",
                     "Frame 0.58 m: s + l > p + q; the crank stops at the limit positions (red)", wait=0)
        self.play(FadeIn(lims), s.animate.set_value(0.5), Create(cv_ng.copy().pointwise_become_partial(cv_ng, 0, 0.5)), run_time=3.5, rate_func=linear)
        self.caption("在极限位置，点沿曲线拐回：机构从开式连续地进入交叉式，两种模式连成一条曲线",
                     "At a limit position the point turns back: open passes into crossed, one single loop", wait=0)
        self.play(s.animate.set_value(1.0), Create(cv_ng.copy().pointwise_become_partial(cv_ng, 0.5, 1.0)), run_time=3.5, rate_func=linear)
        self.wait(0.5)
        self.card([["闭环方程把 T³ 削成一条曲线", "Loop closure cuts T³ down to a curve"],
                   MathTex(r"K_1\cos\theta_3 - K_2\cos\theta_1 + K_3 = \cos(\theta_1 - \theta_3)", font_size=40),
                   ["格拉斯霍夫：最短杆作曲柄能整周转 ⇔ s + l ≤ p + q", "Grashof: the shortest link turns fully ⇔ s + l ≤ p + q"]])
