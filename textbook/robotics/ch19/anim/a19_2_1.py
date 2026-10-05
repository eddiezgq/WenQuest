"""动画 19.2.1（配图 19.2.3）：AGV 沿数字工厂的真实路线从热处理炉驶向数控车床 B。
路线的转折点与程序 19.2.1 相同（工厂布置 factory/digital/wqbus/layout.py 换到 y 轴向上的坐标），拐角用半径 0.5 m 的圆弧过渡；
车速曲线：直线 ≤ 1.0 m/s，圆弧 ≤ 0.5 m/s，加减速 ≤ 0.5 m/s²。两轮转速按式 (19.2.10)，r = 0.05 m，b = 0.26 m。时间压缩约 3.4 倍。"""
from manim import *
from wq_anim import *
import numpy as np
import math

R_W, B_W = 0.05, 0.26
PTS = [(17, 12), (17, 9.5), (7, 9.5), (7, 19), (24, 19), (24, 21.9)]
RHO = 0.5


def build_path(ds=0.01):
    P = [np.array(p, float) for p in PTS]
    xy, kap, cen = [], [], []
    cur = P[0]
    segs = []
    for k in range(1, len(P) - 1):
        a, b, c = P[k - 1], P[k], P[k + 1]
        u = (b - a) / np.linalg.norm(b - a)
        w = (c - b) / np.linalg.norm(c - b)
        turn = math.atan2(u[0] * w[1] - u[1] * w[0], u @ w)
        d = RHO * math.tan(abs(turn) / 2)
        t1 = b - d * u
        segs.append(("L", cur, t1))
        nrm = np.array([-u[1], u[0]]) * (1 if turn > 0 else -1)
        segs.append(("A", t1 + RHO * nrm, t1, turn))
        cur = b + d * w
    segs.append(("L", cur, P[-1]))
    for sg in segs:
        if sg[0] == "L":
            L = np.linalg.norm(sg[2] - sg[1])
            n = max(1, int(L / ds))
            for i in range(n):
                xy.append(sg[1] + (sg[2] - sg[1]) * (i + 0.5) / n)
                kap.append(0.0)
                cen.append(None)
        else:
            c, p0, turn = sg[1], sg[2], sg[3]
            a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
            n = max(1, int(abs(turn) * RHO / ds))
            sgn = 1 if turn > 0 else -1
            for i in range(n):
                a = a0 + turn * (i + 0.5) / n
                xy.append(c + RHO * np.array([math.cos(a), math.sin(a)]))
                kap.append(sgn / RHO)
                cen.append(c)
    xy = np.array(xy)
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(xy, axis=0).T))]
    v = np.where(np.abs(kap) > 0, 0.5, 1.0)
    acc = 0.5
    v[0] = 0.0
    for i in range(1, len(v)):
        v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * acc * (s[i] - s[i - 1])))
    v[-1] = 0.0
    for i in range(len(v) - 2, -1, -1):
        v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * acc * (s[i + 1] - s[i])))
    dt = 2 * np.diff(s) / np.maximum(v[:-1] + v[1:], 1e-9)
    t = np.r_[0, np.cumsum(dt)]
    head = np.r_[np.arctan2(*np.diff(xy, axis=0).T[::-1]), 0]
    head[-1] = head[-2]
    return xy, np.array(kap), cen, v, t, head


XY, KAP, CEN, V, TT, HEAD = build_path()
SC = 0.3
OFF = np.array([-15.5, -15.6])


def M(p):
    q = (np.asarray(p, float) + OFF) * SC
    return np.array([q[0] - 1.2, q[1], 0.0])


class Lesson(Base):
    def construct(self):
        self.title("19.2", "沿车间里的真实路线行驶", "Driving a real route through the workshop")
        floor = VGroup()
        for y in (9.5, 19.0):
            floor.add(Rectangle(width=26 * SC, height=2 * SC, fill_color="#26313a", fill_opacity=1, stroke_width=0).move_to(M((17, y))))
        floor.add(Rectangle(width=2 * SC, height=11.5 * SC, fill_color="#26313a", fill_opacity=1, stroke_width=0).move_to(M((7, 14.25))))
        units = [((17, 15), 5, 4, ["热处理炉", "furnace"]), ((24, 24), 4, 2.2, ["数控车床 B", "lathe B"])]
        for c, w, h, nm in units:
            hl = nm[0] in ("热处理炉", "数控车床 B")
            floor.add(Rectangle(width=w * SC, height=h * SC, color=YELLOW if hl else GREY_B, fill_color="#3a3320" if hl else "#2b343c",
                                fill_opacity=1, stroke_width=2).move_to(M(c)))
            floor.add(zh(nm[0], 16, INK).move_to(M(c)))
        poly = VMobject(color=GREY_B, stroke_width=2).set_points_as_corners([M(p) for p in PTS])
        poly = DashedVMobject(poly, num_dashes=60)
        path = VMobject(color=STEEL, stroke_width=4).set_points_as_corners([M(p) for p in XY[::20]] + [M(XY[-1])])
        self.play(FadeIn(floor), run_time=0.8)
        self.play(Create(poly), run_time=0.8)
        self.caption("工厂仿真给的是折线：直角拐弯，车速一律按 1.0 m/s 计算",
                     "The plant model gives a polyline with right-angle corners and a flat 1.0 m/s", wait=0.6)
        self.play(Create(path), run_time=1.0)
        self.caption("真实的 AGV：拐角用半径 0.5 m 的圆弧过渡，弯前减速，弯后加速",
                     "A real AGV rounds each corner on a 0.5 m arc, slowing before it and speeding up after", wait=0)
        tk = ValueTracker(0.0)
        Ttot = TT[-1]

        def idx():
            return min(int(np.searchsorted(TT, tk.get_value())), len(TT) - 1)

        def car():
            i = idx()
            body = Rectangle(width=0.32 * SC * 3, height=0.22 * SC * 3, color=ORANGE, fill_color=ORANGE, fill_opacity=0.9, stroke_width=2)
            nose = Triangle(color=YELLOW, fill_opacity=1).scale(0.07).rotate(-PI / 2).shift(RIGHT * 0.12)
            g = VGroup(body, nose).rotate(HEAD[i]).move_to(M(XY[i]))
            return g

        def icr():
            i = idx()
            if CEN[i] is None:
                return VGroup()
            c = M(CEN[i])
            return VGroup(Dot(c, radius=0.06, color=YELLOW), DashedLine(c, M(XY[i]), color=YELLOW, dash_length=0.05))

        def panel():
            i = idx()
            v, k = V[i], KAP[i]
            wR, wL = v * (1 + k * B_W / 2) / R_W, v * (1 - k * B_W / 2) / R_W
            rows = VGroup(MathTex(r"t = %.1f\ \mathrm{s}" % tk.get_value(), font_size=30),
                          MathTex(r"v = %.2f\ \mathrm{m/s}" % v, font_size=30, color=STEEL),
                          MathTex(r"\omega_R = %.1f\ \mathrm{rad/s}" % wR, font_size=30, color=RED),
                          MathTex(r"\omega_L = %.1f\ \mathrm{rad/s}" % wL, font_size=30, color=GREEN))
            bars = VGroup()
            for j, (w, col) in enumerate(((wR, RED), (wL, GREEN))):
                bars.add(Rectangle(width=0.3, height=max(0.01, w / 20 * 1.6), fill_color=col, fill_opacity=0.9, stroke_width=0)
                         .move_to([5.0 + 0.5 * j, -1.3 + max(0.01, w / 20 * 1.6) / 2, 0]))
            bars.add(Line([4.7, -1.3 + 1.6, 0], [5.8, -1.3 + 1.6, 0], color=GREY_B, stroke_width=2), zh("20 rad/s", 16, MUTED).move_to([6.25, 0.3, 0]))
            return VGroup(rows.arrange(DOWN, aligned_edge=LEFT, buff=0.15).move_to([5.3, 1.6, 0]), bars)

        self.add(always_redraw(icr), always_redraw(car), always_redraw(panel))
        self.play(tk.animate.set_value(Ttot), run_time=14, rate_func=linear)
        self.caption("进入圆弧时两轮转速分开，瞬心落在圆弧的圆心；全程约 48 s，比按折线估计的 41.9 s 长",
                     "On the arcs the wheel speeds split and the ICR sits at the arc centre; about 48 s, not the 41.9 s estimate", wait=1.5)
        self.card([["沿路线行驶：先规划车速，再由曲率求两轮转速", "Follow a route: plan the speed, then wheel speeds from curvature"],
                   MathTex(r"\omega_{R,L} = \frac{v}{r}\Big(1 \pm \frac{\kappa b}{2}\Big)", font_size=46),
                   ["拐角处的减速使实际时间比 L/v 长", "Slowing for corners makes the trip longer than L/v"]])
