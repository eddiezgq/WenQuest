"""动画 24.1.1（配图 24.1.1）：桁架小车吊运（算例 24.1.2）。吊绳 1.0 m，摆动周期 T_p = 2π√(l/𝔤) = 2.006 s。
两台同样的小车同时以 0.5 m/s² 起动：上面一台加速半个周期（1.003 s），下面一台加速一个周期（2.006 s），然后都匀速前进。
场景程序自己用 RK4（步长 1 ms）积分非线性方程 (24.1.19)：l φ̈ + ẍ cos φ + 𝔤 sin φ = 0；与程序 24.1.1 的结果一致：
前者残留约 5.8° 的摆动，后者到匀速时恰好静止。画面中吊绳的摆角放大 3 倍显示；右侧画两个摆角随时间的曲线（不放大）。
按实际时间播放 8 s。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G, LROPE, ACC = 9.81, 1.0, 0.5
TP = 2 * math.pi * math.sqrt(LROPE / G)
DT, TEND = 0.001, 8.0
SCALE, AMP = 0.72, 3.0                     # 1 m 画成 0.72 个单位；摆角放大 3 倍显示


def run(ta):
    s = np.zeros(4)                        # x, ẋ, φ, φ̇
    out = [s.copy()]
    n = int(round(TEND / DT))
    for k in range(n):
        t = k * DT

        def f(y, tt):
            a = ACC if tt < ta - 1e-12 else 0.0
            return np.array([y[1], a, y[3], -(a * math.cos(y[2]) + G * math.sin(y[2])) / LROPE])
        k1 = f(s, t)
        k2 = f(s + DT / 2 * k1, t + DT / 2)
        k3 = f(s + DT / 2 * k2, t + DT / 2)
        k4 = f(s + DT * k3, t + DT)
        s = s + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(s.copy())
    return np.array(out)


class Lesson(Base):
    def construct(self):
        self.title("24.1", "桁架吊运：加速多久，吊重才不摆", "Gantry transfer: how long to accelerate so the load does not swing")
        runs = [run(round(TP / 2, 3)), run(round(TP, 3))]
        ys = [1.55, -0.65]
        cols = [RED, BLUE]
        heads = [["加速半个周期（1.0 s）", "accelerate for half a period (1.0 s)"], ["加速一个周期（2.0 s）", "accelerate for one period (2.0 s)"]]
        x0 = -6.4
        for k in range(2):
            self.add(Line([-6.9, ys[k] + 0.18, 0], [0.5, ys[k] + 0.18, 0], color=GREY_B, stroke_width=4))
            self.add(bi(heads[k], 22, cols[k]).move_to([-2.6, ys[k] + 0.7, 0]))
        # 右边：摆角曲线
        ax = Axes(x_range=[0, 8, 2], y_range=[-7, 7, 7], x_length=4.4, y_length=3.0, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 1.5, "include_numbers": True, "font_size": 20}).move_to([4.6, 0.2, 0])
        self.add(ax, bi(["吊重摆角 / (°)", "swing angle / (°)"], 20, INK).next_to(ax, UP, buff=0.15),
                 zh("t / s", 18, MUTED).next_to(ax.x_axis, DOWN, buff=0.35).shift(RIGHT * 1.9))
        tk = ValueTracker(0.0)

        def scene():
            t = tk.get_value()
            i = min(int(round(t / DT)), len(runs[0]) - 1)
            g = VGroup()
            for k in range(2):
                x, ph = runs[k][i, 0], runs[k][i, 2]
                cx = x0 + SCALE * x
                top = np.array([cx, ys[k], 0])
                cart = Rectangle(width=0.7, height=0.32, color=cols[k], fill_color=cols[k], fill_opacity=0.35).move_to(top + UP * 0.08)
                a = AMP * ph
                end = top + 1.0 * np.array([math.sin(a), -math.cos(a), 0])
                rope = Line(top, end, color=GREY_A, stroke_width=2)
                load = Square(side_length=0.3, color="#d29922", fill_color="#d29922", fill_opacity=0.9).move_to(end + DOWN * 0.15)
                g.add(rope, cart, load, Dot(top, radius=0.05, color=WHITE))
                acc_on = t < round((TP / 2, TP)[k], 3)
                lab = ["加速", "accelerating"] if acc_on else ["匀速", "cruising"]
                g.add(bi(lab, 18, YELLOW if acc_on else GREY_B).move_to([1.15, ys[k] - 0.25, 0]))
                pts = [ax.c2p(j * DT, math.degrees(runs[k][j, 2])) for j in range(0, i + 1, 40)] or [ax.c2p(0, 0)]
                if len(pts) > 1:
                    g.add(VMobject(color=cols[k], stroke_width=2.5).set_points_as_corners(pts))
                g.add(zh(f"{math.degrees(ph):+.1f}°", 22, cols[k]).move_to([1.15, ys[k] - 0.85, 0]))
            g.add(zh(f"t = {t:.2f} s", 24, INK).move_to([4.6, -2.0, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("两台小车同时以 0.5 m/s² 起动；吊绳 1 m，摆动周期约 2 s（画面中摆角放大 3 倍）",
                     "Both carts start at 0.5 m/s²; 1 m rope, swing period about 2 s (angles drawn 3x)", wait=0)
        self.play(tk.animate.set_value(2.2), run_time=2.2, rate_func=linear)
        self.caption("上面一台只加速了半个周期，吊重一直摆；下面一台加速满一个周期，到匀速时吊重恰好静止",
                     "Top: half a period, the load keeps swinging; bottom: a full period, the load is still when cruising", wait=0)
        self.play(tk.animate.set_value(TEND), run_time=TEND - 2.2, rate_func=linear)
        self.card([["加速时间取摆动周期的整数倍，就不残留摆动", "Accelerate for a whole number of swing periods: no residual swing"],
                   MathTex(r"\ddot\varphi + \frac{\mathfrak g}{l}\varphi = -\frac{\ddot x}{l}", font_size=44),
                   MathTex(r"\varphi_{\mathrm{res}} = \frac{2a}{\mathfrak g}\left|\sin\frac{\omega t_a}{2}\right|", font_size=44),
                   ["方程来自拉格朗日方程：小车加速激起摆动，摆动又拉扯小车", "From Lagrange's equations: the cart excites the swing, the swing pulls the cart"]])
