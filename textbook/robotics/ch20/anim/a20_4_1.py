"""动画 20.4.1（配图 20.4.2）：俯视 Go2 爬行（左后、左前、右后、右前），v = 0.1 m/s，t_c = 2 s，与算例 20.4.3 相同。
支撑脚落在中性点后在地面上不动；机身侧摆 y_b = −A cos(2πt/t_c)。质心近似取机身上的固定点（机身原点后方 2.2 mm，
算例 20.4.1：抬腿使质心移动不到 1 mm）。先放 β = 0.85、A = 0.02 m 一个周期，再看 β = 0.75 换腿的瞬间。"""
from manim import *
from wq_anim import *
import numpy as np
import math

AX, AYD = 0.1934, 0.142
V, TC = 0.1, 2.0
PH = {"RL": 0.0, "FL": 0.25, "RR": 0.5, "FR": 0.75}
HIP = {"FL": (AX, AYD), "FR": (AX, -AYD), "RL": (-AX, AYD), "RR": (-AX, -AYD)}
CX = -0.0022
SC = 9.0
O = np.array([-1.6, 0.35, 0])


def state(t, beta, A):
    ell, Ls = V * beta * TC, V * TC
    feet, stance = {}, []
    for leg, ph in PH.items():
        u = (t / TC - ph) % 1.0
        t_td = t - u * TC
        hx, hy = HIP[leg]
        x0 = hx + V * t_td + ell / 2
        if u < beta:
            feet[leg] = np.array([x0, hy])
            stance.append(leg)
        else:
            tau = (u - beta) / (1 - beta)
            s = tau - math.sin(2 * math.pi * tau) / (2 * math.pi)
            feet[leg] = np.array([x0 + Ls * s, hy])
    body = np.array([V * t, -A * math.cos(2 * math.pi * t / TC)])
    return feet, stance, body, body + np.array([CX, 0.0])


def hull(P):
    P = sorted(map(tuple, P))
    if len(P) < 3:
        return [np.array(p) for p in P]
    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return [np.array(p) for p in lo[:-1] + up[:-1]]


def margin(poly, c):
    if len(poly) < 3:
        return -1.0
    d, inside = [], True
    for k in range(len(poly)):
        a, b = poly[k], poly[(k + 1) % len(poly)]
        e = b - a
        n = np.array([e[1], -e[0]]) / np.linalg.norm(e)
        s = (c - a) @ n
        inside = inside and s <= 0
        d.append(-s)
    return min(d) if inside else -min(abs(x) for x in d)


def W(p, cam):
    return O + np.array([(p[0] - cam) * SC, p[1] * SC, 0])


class Lesson(Base):
    def construct(self):
        self.title("20.4", "爬行：质心始终留在支撑多边形内", "Crawling: the CoM stays inside the support polygon")
        tk = ValueTracker(0.0)
        prm = {"beta": 0.85, "A": 0.02}
        trail = []

        def scene():
            t = tk.get_value()
            feet, stance, body, c = state(t, prm["beta"], prm["A"])
            cam = 0.0
            g = VGroup()
            bx = [W(body + np.array(q), cam) for q in ((-0.26, -0.1), (0.26, -0.1), (0.26, 0.1), (-0.26, 0.1))]
            g.add(Polygon(*bx, color=GREY_B, stroke_width=2, fill_color=NAVY, fill_opacity=0.5))
            poly = hull([feet[l] for l in stance])
            mg = margin(poly, c)
            col = GREEN if mg > 0.001 else (YELLOW if mg > -0.001 else RED)
            if len(poly) >= 3:
                g.add(Polygon(*[W(p, cam) for p in poly], color=col, stroke_width=3, fill_color=col, fill_opacity=0.15))
            for l, p in feet.items():
                st = l in stance
                g.add(Dot(W(p, cam), radius=0.11, color=WHITE if st else GREY_C, fill_opacity=1 if st else 0.4))
                g.add(Text(l, font=LATIN, font_size=18, color=MUTED).next_to(W(p, cam), UP if p[1] > 0 else DOWN, buff=0.08))
            trail.append(W(c, cam))
            if len(trail) > 1:
                g.add(VMobject(color=RED, stroke_width=2).set_points_as_corners(trail[-400:]))
            g.add(Dot(W(c, cam), radius=0.08, color=RED))
            g.add(Text(("β = %.2f   侧摆 %.0f cm   t = %.2f s   裕度 S = %.1f mm" % (prm["beta"], prm["A"] * 100, t, mg * 1000)).replace("-", "−"),
                       font=CJK, font_size=22, color=col).move_to([0, 2.45, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("白点：着地的脚；灰点：摆动的脚；红点：质心投影。四脚着地时多边形是四边形，抬一条腿就成了三角形",
                     "White: feet down; grey: swinging; red: the CoM. Four feet make a quadrilateral, lifting one leaves a triangle", wait=0)
        self.play(tk.animate.set_value(1.0), run_time=6, rate_func=linear)
        self.caption("抬腿之前，机身先把质心挪进下一个三角形；β = 0.85、侧摆 2 cm 时最小裕度约 7.6 mm",
                     "Before each lift the body shifts the CoM into the next triangle; with β = 0.85 and 2 cm of sway the smallest margin is about 7.6 mm", wait=0)
        self.play(tk.animate.set_value(2.0), run_time=6, rate_func=linear)
        trail.clear()
        prm["beta"], prm["A"] = 0.75, 0.0
        tk.set_value(0.42)
        self.caption("β = 0.75：一只脚落地的同时另一只抬起，两个三角形只共用一条对角线，质心只能落在线上",
                     "β = 0.75: one foot lands as another lifts; the two triangles share only a diagonal, and the CoM must sit on it", wait=0)
        self.play(tk.animate.set_value(0.52), run_time=4, rate_func=linear)
        self.wait(0.8)
        self.card([["静态稳定：质心投影在支撑多边形内", "Static stability: the CoM projection inside the support polygon"],
                   MathTex(r"c_{xy} = \sum_j w_j\,p_j,\quad w_j = \frac{f_{jz}}{m\mathfrak g} \ge 0,\quad \sum_j w_j = 1", font_size=40),
                   ["爬行要有正的裕度须 β > 3/4；裕度约与 (β − 3/4)·L_s 成正比，只有几毫米", "A positive crawl margin needs β > 3/4; it grows with (β − 3/4)·L_s and is only millimetres"]])
