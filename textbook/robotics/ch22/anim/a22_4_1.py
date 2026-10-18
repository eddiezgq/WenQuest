"""动画 22.4.1（配图 22.4.2）：过三点的圆弧与沿圆弧运动的加速度（算例 22.4.2）。
圆：半径 0.10 m，示教点的圆心角 0°、50°、140°，弧长 0.24435 m。沿弧长先用梯形时间标度（切向加速度 0.5 m/s²、速率 0.25 m/s，
总时间 1.4774 s），再用 S 形时间标度（加加速度 5 m/s³，总时间 1.5774 s）。画面中 0.1 m 画成 2.2 个单位；
加速度箭头 1 m/s² 画成 2.0 个单位：绿为切向，红为法向，黄为总加速度。各放慢 3 倍播放。"""
from manim import *
from wq_anim import *
import numpy as np
import math

RHO, VT, AT, JT = 0.10, 0.25, 0.5, 5.0
L = RHO * math.radians(140)
SC = 22.0                    # 1 m → 22 单位
AS = 2.0                     # 1 m/s² → 2 单位
C0 = np.array([-2.6, -0.35, 0])
SLOW = 3.0


def trap(t):
    ta = VT / AT
    tc = L / VT - VT / AT
    T = 2 * ta + tc
    t = min(max(t, 0.0), T)
    if t < ta:
        return 0.5 * AT * t * t, AT * t, AT
    if t < ta + tc:
        return 0.5 * VT * ta + VT * (t - ta), VT, 0.0
    return L - 0.5 * AT * (T - t) ** 2, AT * (T - t), -AT


def scurve(t):
    # 定理 22.2.2：同一 v′ 的梯形曲线用宽 t_j = a/j 的盒形窗滑动平均（这里 v′ = v，能达到）
    tj = AT / JT
    ta = VT / AT
    tc = L / VT - VT / AT
    T = 2 * ta + tc

    def pos(x):
        x = min(max(x, 0.0), T)
        if x < ta:
            return 0.5 * AT * x * x
        if x < ta + tc:
            return 0.5 * VT * ta + VT * (x - ta)
        return L - 0.5 * AT * (T - x) ** 2

    def vel(x):
        if x <= 0 or x >= T:
            return 0.0
        return AT * x if x < ta else (VT if x < ta + tc else AT * (T - x))
    n = 60
    xs = np.linspace(t - tj, t, n + 1)
    p = float(np.mean([pos(x) for x in xs]))
    v = (pos(t) - pos(t - tj)) / tj
    a = (vel(t) - vel(t - tj)) / tj
    return p, v, a


T_TRAP = 2 * VT / AT + L / VT - VT / AT
T_S = T_TRAP + AT / JT


def P(phi):
    return C0 + SC * RHO * np.array([math.cos(phi), math.sin(phi), 0])


class Lesson(Base):
    def construct(self):
        self.title("22.4", "过三点的圆弧", "An arc through three points")
        pts = [P(math.radians(a)) for a in (0, 50, 140)]
        dots = VGroup(*[Dot(p, radius=0.09, color=WHITE) for p in pts])
        labs = VGroup(*[MathTex(f"p_{i + 1}", font_size=32, color=INK).next_to(p, [RIGHT, UR, UL][i], buff=0.12) for i, p in enumerate(pts)])
        self.caption("示教时给出三个点：起点、中间一点、终点", "Three taught points: start, a middle point, end", wait=0)
        self.play(FadeIn(dots), FadeIn(labs), run_time=1.2)
        chords = VGroup(Line(pts[0], pts[1], color=GREY_B, stroke_width=2), Line(pts[1], pts[2], color=GREY_B, stroke_width=2))
        bis = VGroup()
        for a, b in ((pts[0], pts[1]), (pts[1], pts[2])):
            m = (a + b) / 2
            d = b - a
            n = np.array([-d[1], d[0], 0]) / np.linalg.norm(d)
            uc = (C0 - m) / np.linalg.norm(C0 - m)
            bis.add(DashedLine(m - 0.5 * uc, C0 + 0.5 * uc, color=YELLOW, stroke_width=2))
        self.caption("两条弦的中垂线交于一点，它到三点的距离相等，就是圆心",
                     "The perpendicular bisectors of two chords meet at the point equidistant from all three: the centre", wait=0)
        self.play(Create(chords), run_time=0.8)
        self.play(Create(bis), run_time=1.2)
        cdot = Dot(C0, radius=0.09, color=RED)
        clab = MathTex("c", font_size=32, color=RED).next_to(cdot, DL, buff=0.1)
        arc = Arc(radius=SC * RHO, start_angle=0, angle=math.radians(140), arc_center=C0, color=BLUE, stroke_width=5)
        self.play(FadeIn(cdot), FadeIn(clab), Create(arc), run_time=1.5)
        self.play(FadeOut(bis), FadeOut(chords), run_time=0.5)
        tk = ValueTracker(0.0)
        mode = {"f": trap, "T": T_TRAP}
        panel_x = 3.4

        def mover():
            t = tk.get_value()
            l, v, a = mode["f"](t)
            phi = l / RHO
            p = P(phi)
            et = np.array([-math.sin(phi), math.cos(phi), 0])
            en = -np.array([math.cos(phi), math.sin(phi), 0])
            an = v * v / RHO
            g = VGroup(Dot(p, radius=0.12, color=ORANGE))
            if abs(a) > 1e-6:
                g.add(Arrow(p, p + AS * a * et, buff=0, color=GREEN, stroke_width=6, max_tip_length_to_length_ratio=0.25))
            if an > 1e-6:
                g.add(Arrow(p, p + AS * an * en, buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.25))
            tot = a * et + an * en
            if np.linalg.norm(tot) > 1e-6:
                g.add(Arrow(p, p + AS * tot, buff=0, color=YELLOW, stroke_width=4, max_tip_length_to_length_ratio=0.2))
            rows = VGroup(Text(f"t = {t:.2f} s", font=CJK, font_size=24, color=INK),
                          Text(f"速率 {v:.3f} m/s", font=CJK, font_size=24, color=INK),
                          Text(f"切向 {a:+.3f} m/s²", font=CJK, font_size=24, color=GREEN),
                          Text(f"法向 {an:.3f} m/s²", font=CJK, font_size=24, color=RED),
                          Text(f"总加速度 {math.hypot(a, an):.3f} m/s²", font=CJK, font_size=24, color=YELLOW))
            rows.arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to(np.array([panel_x, 0.4, 0]))
            g.add(rows)
            return g

        self.add(always_redraw(mover))
        self.caption("梯形时间标度：法向加速度 κv² 随速率增大，加速结束的一瞬间总加速度突然变小",
                     "Trapezoidal timing: the normal acceleration κv² grows with speed; the total acceleration drops suddenly when acceleration ends",
                     wait=0)
        self.play(tk.animate.set_value(T_TRAP), run_time=T_TRAP * SLOW, rate_func=linear)
        self.wait(0.6)
        mode["f"], mode["T"] = scurve, T_S
        tk.set_value(0.0)
        self.caption("S 形时间标度：切向加速度逐渐升降，总加速度连续变化，最大值也更小",
                     "S-curve timing: the tangential acceleration ramps, the total acceleration changes continuously and peaks lower", wait=0)
        self.play(tk.animate.set_value(T_S), run_time=T_S * SLOW, rate_func=linear)
        self.wait(0.8)
        self.card([["圆弧插补", "Circular interpolation"],
                   MathTex(r"c = p_1 + \frac{\|b\|^2(n\times a) + \|a\|^2(b\times n)}{2\|n\|^2},\quad a = p_2 - p_1,\ b = p_3 - p_1,\ n = a\times b",
                           font_size=34),
                   MathTex(r"\ddot p = p'(\ell)\,\ddot\ell + p''(\ell)\,\dot\ell^2,\qquad a_t = \ddot\ell,\quad a_n = \kappa\dot\ell^2", font_size=40),
                   ["弯得越急，走得越慢：v ≤ √(a_max/κ)", "The sharper the bend, the slower: v ≤ √(a_max/κ)"]])
