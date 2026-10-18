"""动画 22.3.1（配图 22.3.1）：在关节 1、关节 4 的平面上看经过路径点 R、A、M、B 的三种轨迹（算例 22.3.1、22.3.2）。
路径点（度，程序 22.3.1）：θ1 = 98.17、98.17、155.54、201.60，θ4 = −134.95、−118.49、−36.83、−29.18。
每点停下：三段五次多项式，时长 0.5426、1.0004、0.9298 s；三次样条与抛物线过渡：各段时长 0.3893、0.7178、0.6672 s，
抛物线过渡的过渡时长 0.0684、0.2325、0.2819、0.2008 s。三个点同时出发，按实际时间的 2.5 倍放慢。"""
from manim import *
from wq_anim import *
import numpy as np
import math

Q = np.array([[98.17, -134.95], [98.17, -118.49], [155.54, -36.83], [201.60, -29.18]])
TS = np.array([0.5426, 1.0004, 0.9298])
HS = np.array([0.3893, 0.7178, 0.6672])
TB = np.array([0.0684, 0.2325, 0.2819, 0.2008])
SLOW = 2.5


def quintic_stop(t):
    t0 = 0.0
    for k in range(3):
        if t <= t0 + TS[k] or k == 2:
            u = min(max((t - t0) / TS[k], 0.0), 1.0)
            s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5
            return Q[k] + s * (Q[k + 1] - Q[k])
        t0 += TS[k]


def spline_coeffs():
    # 两端速度为零的三次样条：式 (22.3.4) 的三对角方程组（两个未知速度）
    h = HS
    A = np.array([[2 * (1 / h[0] + 1 / h[1]), 1 / h[1]], [1 / h[1], 2 * (1 / h[1] + 1 / h[2])]])
    D = np.diff(Q, axis=0)
    B = np.array([3 * (D[0] / h[0] ** 2 + D[1] / h[1] ** 2), 3 * (D[1] / h[1] ** 2 + D[2] / h[2] ** 2)])
    V = np.vstack([np.zeros(2), np.linalg.solve(A, B), np.zeros(2)])
    segs = []
    for k in range(3):
        T = h[k]
        c2 = (3 * D[k] - (2 * V[k] + V[k + 1]) * T) / T ** 2
        c3 = (-2 * D[k] + (V[k] + V[k + 1]) * T) / T ** 3
        segs.append((Q[k], V[k], c2, c3))
    return segs


SEG = spline_coeffs()
TK = np.concatenate([[0.0], np.cumsum(HS)])


def spline(t):
    t = min(max(t, 0.0), TK[-1])
    k = min(int(np.searchsorted(TK, t, side="right") - 1), 2)
    u = t - TK[k]
    c0, c1, c2, c3 = SEG[k]
    return c0 + c1 * u + c2 * u * u + c3 * u ** 3


VS = np.vstack([np.zeros(2), np.diff(Q, axis=0) / HS[:, None], np.zeros(2)])


def blend(tt):
    t = tt - TB[0] / 2                      # 起点的过渡从 t = −t_b0/2 开始，这里平移到 0
    for m in range(4):
        if abs(t - TK[m]) <= TB[m] / 2:
            vin, vout = VS[m], VS[m + 1]
            u = t - TK[m] + TB[m] / 2
            return Q[m] - vin * TB[m] / 2 + vin * u + (vout - vin) / TB[m] * u * u / 2
    if t < 0:
        return Q[0]
    if t > TK[-1]:
        return Q[-1]
    k = min(int(np.searchsorted(TK, t, side="right") - 1), 2)
    return Q[k] + VS[k + 1] * (t - TK[k])


class Lesson(Base):
    def construct(self):
        self.title("22.3", "样条与过路径点", "Splines through via points")
        ax = Axes(x_range=[95, 210, 20], y_range=[0, 120, 20], x_length=8.2, y_length=4.6, tips=False,
                  axis_config={"stroke_width": 1.5, "color": GREY_B, "font_size": 20},
                  x_axis_config={"include_numbers": True}, y_axis_config={"include_numbers": False})
        ax.move_to(np.array([-0.6, -0.15, 0]))
        yticks = VGroup(*[Text(str(v), font=LATIN, font_size=16, color=GREY_B).next_to(ax.c2p(95, v + 140), LEFT, buff=0.12)
                          for v in range(-140, -19, 20)])

        def P(q):
            return ax.c2p(q[0], q[1] + 140)
        xl = MathTex(r"\theta_1\ (^\circ)", font_size=26, color=INK).next_to(ax.x_axis, RIGHT, buff=0.15).shift(DOWN * 0.3)
        yl = MathTex(r"\theta_4\ (^\circ)", font_size=26, color=INK).next_to(ax.y_axis, UP, buff=0.1)
        dots = VGroup(*[Dot(P(q), radius=0.08, color=WHITE) for q in Q])
        names = VGroup(*[Text(n, font=CJK, font_size=22, color=INK).next_to(dots[i], [DR, UL, UL, DR][i], buff=0.08)
                         for i, n in enumerate("RAMB")])
        self.caption("关节平面上的四个路径点：抓取 R、提升后 A、越过防护罩 M、卡盘前 B",
                     "Four via points in the joint plane: grasp R, lifted A, over the guard M, before the chuck B", wait=0)
        self.play(Create(ax), FadeIn(yticks), FadeIn(xl), FadeIn(yl), FadeIn(dots), FadeIn(names), run_time=1.5)
        poly = VMobject(color=ORANGE, stroke_width=3).set_points_as_corners([P(q) for q in Q])
        tt = np.linspace(0, TK[-1], 300)
        spl = VMobject(color=BLUE, stroke_width=4).set_points_smoothly([P(spline(t)) for t in tt])
        tb_end = TK[-1] + (TB[0] + TB[3]) / 2
        bl = VMobject(color=GREEN, stroke_width=3).set_points_smoothly([P(blend(t)) for t in np.linspace(0, tb_end, 300)])
        self.caption("橙：每点停下，走折线；蓝：三次样条，经过每个点、加速度连续；绿：抛物线过渡，从点旁切过",
                     "Orange: stop at each point (polyline); blue: cubic spline through every point; green: parabolic blends cut the corners", wait=0)
        self.play(Create(poly), Create(spl), Create(bl), run_time=2.5)
        legend = VGroup(bi(["每点停下 2.47 s", "stop at each 2.47 s"], 20, ORANGE), bi(["三次样条 1.77 s", "cubic spline 1.77 s"], 20, BLUE),
                        bi(["抛物线过渡 1.91 s", "parabolic blends 1.91 s"], 20, GREEN)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        legend.to_corner(UR, buff=0.4).shift(DOWN * 0.9)
        self.play(FadeIn(legend), run_time=0.6)
        tk = ValueTracker(0.0)
        T_end = float(TS.sum())

        def movers():
            t = tk.get_value()
            g = VGroup(Dot(P(quintic_stop(t)), radius=0.11, color=ORANGE), Dot(P(spline(t)), radius=0.11, color=BLUE),
                       Dot(P(blend(t)), radius=0.11, color=GREEN),
                       Text(f"t = {t:.2f} s", font=CJK, font_size=22, color=INK).move_to(np.array([4.6, -1.0, 0])))
            return g

        self.add(always_redraw(movers))
        self.caption("三个点同时出发（放慢 2.5 倍）：停下的那个在 A、M 处各停一下",
                     "All three start together (2.5× slower): the stopping one halts at A and M", wait=0)
        self.play(tk.animate.set_value(T_end), run_time=T_end * SLOW, rate_func=linear)
        self.caption("同样的限值下，样条比每点停下快 28%；抛物线过渡离 A、M 约 2 cm",
                     "Within the same limits the spline is 28% faster; the blends pass about 2 cm from A and M", wait=2.0)
        self.card([["经过路径点的三次样条", "A cubic spline through via points"],
                   MathTex(r"\frac{v_{k-1}}{h_{k-1}} + 2\Big(\frac{1}{h_{k-1}}+\frac{1}{h_k}\Big)v_k + \frac{v_{k+1}}{h_k}"
                           r" = 3\Big(\frac{\Delta_{k-1}}{h_{k-1}^2}+\frac{\Delta_k}{h_k^2}\Big)", font_size=36),
                   MathTex(r"q(t_k) - q_k = \frac{(v_{\rm out}-v_{\rm in})\,t_b}{8}", font_size=40),
                   ["样条：经过每个点，加速度连续；过渡：从点旁切过", "Spline: through every point, continuous acceleration; blend: cuts the corner"]])
