"""动画 11.5.2（配图 11.5.3）：车轮转角决定不了位置。
两台相同的差速 AGV（轮半径 0.05 m、轮距 0.26 m）从同一点出发：A 两轮同时变速转动，B 先只转右轮、再只转左轮，
两轮的总转角与 A 相同。两车最后的轮转角读数相同、车头方向相同，却停在不同的地方。数据算法同程序 11.5.1。"""
from manim import *
from wq_anim import *
import numpy as np
import math

R_W, B_W = 0.05, 0.26
SC = 2.6                                  # 1 m 画成 2.6 个单位
O = np.array([-2.6, -1.9, 0.0])           # 出发点在画面中的位置


def drive(wR, wL, dt):
    q = np.zeros(5)
    out = [q.copy()]
    for a, c in zip(wR, wL):
        v, om = R_W * (a + c) / 2, R_W * (a - c) / B_W
        ph = q[2]
        if abs(om) < 1e-12:
            q[0] += v * dt * math.cos(ph)
            q[1] += v * dt * math.sin(ph)
        else:
            q[0] += v / om * (math.sin(ph + om * dt) - math.sin(ph))
            q[1] += -v / om * (math.cos(ph + om * dt) - math.cos(ph))
        q[2] += om * dt
        q[3] += a * dt
        q[4] += c * dt
        out.append(q.copy())
    return np.array(out)


dt = 1e-3
t = np.arange(0, 4, dt)
QA = drive(10 + 6 * np.sin(1.3 * t), 10 - 4 * np.cos(0.7 * t), dt)
TR, TL = QA[-1, 3], QA[-1, 4]
n = len(t) // 2
QB = drive(np.r_[np.full(n, TR / (n * dt)), np.zeros(len(t) - n)], np.r_[np.zeros(n), np.full(len(t) - n, TL / ((len(t) - n) * dt))], dt)


def P(x, y):
    return O + SC * np.array([x, y, 0.0])


def car(q, color):
    x, y, ph = q[:3]
    c = P(x, y)
    body = Rectangle(width=0.32 * SC, height=0.22 * SC, color=color, fill_color=NAVY, fill_opacity=1, stroke_width=3)
    wl = Rectangle(width=0.1 * SC, height=0.035 * SC, color=GREY_B, fill_color=GREY_D, fill_opacity=1).shift(UP * 0.13 * SC)
    wr = wl.copy().shift(DOWN * 0.26 * SC)
    nose = Triangle(color=YELLOW, fill_opacity=1).scale(0.08).rotate(-PI / 2).shift(RIGHT * 0.12 * SC)
    g = VGroup(body, wl, wr, nose)
    g.rotate(ph, about_point=ORIGIN).shift(c)
    return g


def at(Q, s):
    k = min(int(s * (len(Q) - 1)), len(Q) - 1)
    return Q[k]


def panel(name, q, color):
    rows = VGroup(bi(name, 22, color),
                  MathTex(r"\theta_R = %.1f\ \mathrm{rad}" % q[3], font_size=28),
                  MathTex(r"\theta_L = %.1f\ \mathrm{rad}" % q[4], font_size=28),
                  MathTex(r"\varphi = %.1f^\circ" % math.degrees((q[2] + math.pi) % (2 * math.pi) - math.pi), font_size=28),
                  MathTex(r"(x, y) = (%.2f,\ %.2f)\ \mathrm{m}" % (q[0], q[1]), font_size=28))
    return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.12)


class Lesson(Base):
    def construct(self):
        self.title("11.5", "车轮转角决定不了位置", "Wheel angles do not fix the position")
        grid = NumberPlane(x_range=[-0.8, 0.8, 0.25], y_range=[-0.2, 1.5, 0.25], x_length=1.6 * SC, y_length=1.7 * SC,
                           background_line_style={"stroke_color": GREY_D, "stroke_width": 1, "stroke_opacity": 0.6},
                           axis_config={"stroke_color": GREY_C})
        grid.shift(P(0, 0) - grid.c2p(0, 0))
        self.play(FadeIn(grid), run_time=0.6)
        # ---------- 约束：只能沿车头方向走
        c0 = car(QA[0], BLUE)
        ok = Arrow(P(0, 0), P(0.35, 0), color=GREEN, buff=0, stroke_width=6)
        no = DashedLine(P(0, 0), P(0, 0.3), color=RED).add_tip()
        cross = Cross(scale_factor=0.15, stroke_color=RED).move_to(P(0, 0.2))
        eq = MathTex(r"\dot x\sin\varphi - \dot y\cos\varphi = 0", font_size=34).move_to([3.4, 2.3, 0])
        self.play(FadeIn(c0), GrowArrow(ok), Create(no), Create(cross), Write(eq), run_time=1.0)
        self.caption("车轮只能向前滚，不能侧滑：车体的速度只能沿车头方向",
                     "Wheels roll but never slip sideways: the body moves only along its heading", wait=1.0)
        self.play(FadeOut(ok, no, cross), run_time=0.4)
        # ---------- 过程 A
        s = ValueTracker(0.0)
        carA = always_redraw(lambda: car(at(QA, s.get_value()), BLUE))
        trA = VMobject(color=BLUE, stroke_width=3).set_points_as_corners([P(*q[:2]) for q in QA[::40]])
        pA = always_redraw(lambda: panel(["A：两轮同时变速", "A: both wheels, varying"], at(QA, s.get_value()), BLUE).move_to([1.9, 0.2, 0]))
        self.play(FadeOut(c0), run_time=0.15)
        self.add(carA, pA)
        self.caption("车 A：两个轮子同时转，转速不断变化", "Car A: both wheels turn together at changing speeds", wait=0)
        self.play(s.animate.set_value(1.0), Create(trA), run_time=4.0, rate_func=linear)
        endA = car(QA[-1], BLUE)
        self.add(endA, panel(["A：两轮同时变速", "A: both wheels, varying"], QA[-1], BLUE).move_to([1.9, 0.2, 0]))
        self.play(FadeOut(carA), FadeOut(pA), run_time=0.15)
        # ---------- 过程 B
        s2 = ValueTracker(0.0)
        carB = always_redraw(lambda: car(at(QB, s2.get_value()), ORANGE))
        trB = VMobject(color=ORANGE, stroke_width=3).set_points_as_corners([P(*q[:2]) for q in QB[::40]])
        pB = always_redraw(lambda: panel(["B：先右轮，后左轮", "B: right, then left"], at(QB, s2.get_value()), ORANGE).move_to([5.4, 0.2, 0]))
        self.add(carB, pB)
        self.caption("车 B：先只转右轮，再只转左轮，两个轮子转过的总角度与 A 相同",
                     "Car B: right wheel only, then left only; the same total wheel angles as A", wait=0)
        self.play(s2.animate.set_value(1.0), Create(trB), run_time=4.0, rate_func=linear)
        gap = np.linalg.norm(QA[-1, :2] - QB[-1, :2])
        ln = DashedLine(P(*QA[-1, :2]), P(*QB[-1, :2]), color=YELLOW)
        lab = MathTex(r"%.2f\ \mathrm{m}" % gap, font_size=30, color=YELLOW).next_to(ln.get_center(), LEFT, buff=0.25)
        self.play(Create(ln), Write(lab), run_time=0.8)
        self.caption("轮转角相同，车头方向也相同（可积的部分），位置却差了一米多（不可积的部分）",
                     "Same wheel angles, same heading (the integrable part), yet over a metre apart (the non-integrable part)", wait=2.0)
        self.card([["两个约束不可积，一个可积", "Two constraints are non-integrable, one is integrable"],
                   MathTex(r"\varphi - \frac{r}{b}(\theta_R - \theta_L) = \text{const}", font_size=44),
                   ["位置要靠轮速的全部历史积分出来：这就是里程计", "Position must be integrated from the whole history of wheel speeds: odometry"]])
