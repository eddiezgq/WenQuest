"""动画 23.2.1（配图 23.2.2）：复摆的周期与悬挂点。三根相同的 1 m 均匀米尺，挂在离中点 d = 0.5 m（一端）、
0.289 m（= k = L/√12）、0.1 m 处，同时从 12° 释放（无阻尼，按非线性方程 J_o θ̈ = −m𝔤 d sin θ 积分，RK4，步长 2 ms）。
小幅周期 T = 2π √((k² + d²)/(𝔤 d))：1.638 s、1.524 s、1.938 s；挂在 d = k 处的摆得最快。
第二段：d = 0.2 m 与它的共轭点 k²/d = 0.4167 m（在中点另一侧）各挂一根，周期相同（1.575 s），两根一起摆。
画面按实际时间播放。1 m 画成 2.6 个单位。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
LS = 1.0
K = LS / math.sqrt(12)
SC = 2.6


def simulate(d, th0, T, dt=0.002):
    """θ̈ = −𝔤 d sin θ / (k² + d²)；返回时刻与角度。"""
    w2 = G * d / (K * K + d * d)
    n = int(T / dt)
    th, om = th0, 0.0
    out = np.zeros(n + 1)
    out[0] = th
    for i in range(n):
        def f(x, v):
            return v, -w2 * math.sin(x)
        k1 = f(th, om)
        k2 = f(th + dt / 2 * k1[0], om + dt / 2 * k1[1])
        k3 = f(th + dt / 2 * k2[0], om + dt / 2 * k2[1])
        k4 = f(th + dt * k3[0], om + dt * k3[1])
        th += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        om += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        out[i + 1] = th
    return np.arange(n + 1) * dt, out


def period(d):
    return 2 * math.pi * math.sqrt((K * K + d * d) / (G * d))


def stick(pivot, d, th, col):
    """尺子：悬挂点在离中点 d 处（中点在悬挂点下方 d），转过 th。"""
    u = np.array([math.sin(th), -math.cos(th), 0.0])            # 从悬挂点指向中点
    c = pivot + SC * d * u
    a, b = c - SC * LS / 2 * u, c + SC * LS / 2 * u
    g = VGroup(Line(a, b, color=col, stroke_width=11))
    for i in range(1, 10):
        p = a + SC * 0.1 * i * u
        n = np.array([u[1], -u[0], 0])
        g.add(Line(p - 0.06 * n, p + 0.06 * n, color=BG, stroke_width=2))
    g.add(Dot(pivot, radius=0.07, color=WHITE), Dot(c, radius=0.05, color=RED))
    return g


class Lesson(Base):
    def construct(self):
        self.title("23.2", "复摆：挂在哪里摆得最快", "A physical pendulum: where to hang it")
        ds = [0.5, K, 0.1]
        cols = [GREEN, YELLOW, STEEL]
        xs = [-4.4, -0.9, 2.6]
        y0 = 1.3
        th0 = math.radians(12)
        T_run = 9.0
        data = [simulate(d, th0, T_run) for d in ds]
        rail = Line([-6.2, y0, 0], [5.4, y0, 0], color=GREY_B, stroke_width=3)
        self.add(rail)
        labels = VGroup()
        for x, d, col in zip(xs, ds, cols):
            labels.add(VGroup(Text(f"d = {d:.3f} m", font=CJK, font_size=24, color=col),
                              Text(f"T = {period(d):.3f} s", font=CJK, font_size=22, color=col)).arrange(DOWN, buff=0.06).move_to([x + 1.9, y0 - 0.55, 0]))
        tt = ValueTracker(0.0)

        def scene():
            t = tt.get_value()
            g = VGroup()
            for (ts, th), x, d, col in zip(data, xs, ds, cols):
                g.add(stick(np.array([x, y0, 0]), d, float(np.interp(t, ts, th)), col))
            g.add(Text(f"t = {t:.2f} s", font=CJK, font_size=24, color=INK).to_corner(UR, buff=0.4).shift(DOWN * 0.6))
            return g

        self.add(always_redraw(scene))
        self.play(FadeIn(labels), run_time=0.6)
        self.caption("三根一样的米尺挂在不同位置：中间这根挂在离中点 k = L/√12 处，摆得最快",
                     "Three identical metre sticks hung at different points: the middle one, at k = L/√12, swings fastest", wait=0)
        self.play(tt.animate.set_value(T_run), run_time=T_run, rate_func=linear)
        self.clear_stage()
        # 第二段：共轭的两个悬挂点
        d1, d2 = 0.2, K * K / 0.2
        data2 = [simulate(d1, th0, 7.0), simulate(d2, th0, 7.0)]
        xs2 = [-3.2, 1.6]
        self.add(rail)
        lab2 = VGroup(*[VGroup(Text(f"d = {d:.4f} m", font=CJK, font_size=24, color=c),
                               Text(f"T = {period(d):.3f} s", font=CJK, font_size=22, color=c)).arrange(DOWN, buff=0.06).move_to([x + 2.0, y0 - 0.55, 0])
                        for x, d, c in zip(xs2, (d1, d2), (ORANGE, PURPLE_B))])
        t2 = ValueTracker(0.0)

        def scene2():
            t = t2.get_value()
            g = VGroup()
            for (ts, th), x, d, c in zip(data2, xs2, (d1, d2), (ORANGE, PURPLE_B)):
                g.add(stick(np.array([x, y0, 0]), d, float(np.interp(t, ts, th)), c))
            return g

        self.add(always_redraw(scene2))
        self.play(FadeIn(lab2), run_time=0.6)
        self.caption("挂在 d = 0.2 m 和它的共轭点 k²/d：两根尺子步调一致——悬挂点与振动中心可以互换",
                     "Hung at d = 0.2 m and at its conjugate k²/d, the two keep in step: pivot and centre of oscillation can be swapped", wait=0)
        self.play(t2.animate.set_value(7.0), run_time=7.0, rate_func=linear)
        self.card([["复摆的周期只取决于回转半径与悬挂点", "The period depends only on the radius of gyration and the pivot"],
                   MathTex(r"T = 2\pi\sqrt{\frac{k^2 + d^2}{\mathfrak g\,d}},\qquad l_e = d + \frac{k^2}{d}", font_size=44),
                   ["d = k 时周期最短；d 与 k²/d 周期相同（惠更斯 1673）", "Shortest at d = k; d and k²/d give the same period (Huygens 1673)"]])
