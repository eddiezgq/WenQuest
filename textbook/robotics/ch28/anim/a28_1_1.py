"""动画 28.1.1（配图 28.1.1）：AGV 过弯，侧滑还是侧翻。数值与算例 28.1.2 相同（满载 800 kg，质心高 0.65 m，轮距 0.8 m，示意值）。
(1) 后视：车速升高，侧向加速度 a_y = v²/R 增大，内侧车轮的法向力 m𝔤/2 − m a_y h/w 减小；干地面（μ = 0.7）上 a_y 到 6.04 m/s²
    时内侧降到零，车绕外侧车轮翻倒，此时还没到摩擦的上限 μ𝔤 = 6.87 m/s²。
(2) 俯视：湿地面（μ = 0.4）上侧向力先达到 μm𝔤，a_y 最多 3.92 m/s²，车速再高，车就向弯道外侧滑出。
(3) 极限侧向加速度与质心高度：侧翻 𝔤w/(2h)，侧滑 μ𝔤，质心高于 w/(2μ) = 0.57 m 的车先翻。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
M = 800.0
H = 0.65
W = 0.8
R = 3.0
RC = math.hypot(3.0, 0.55)        # 质心的转弯半径
A_TIP = G * W / (2 * H)           # 6.04
A_DRY, A_WET = 0.7 * G, 0.4 * G   # 6.87, 3.92


def ay_of(v):
    return (v / R) ** 2 * RC


class Lesson(Base):
    def construct(self):
        self.title("28.1", "AGV 过弯：先滑还是先翻", "AGV in a bend: skid or roll over first")
        # (1) 后视
        gy = -1.6
        self.add(Line([-6.2, gy, 0], [0.2, gy, 0], color=GREY_B, stroke_width=3))
        sc = 3.2                                     # 图中 1 m 的长度
        v = ValueTracker(1.0)
        tilt = ValueTracker(0.0)
        piv = np.array([-3.0 + W / 2 * sc, gy, 0])     # 后视，车向左转：内侧在左、外侧在右；翻车时绕外侧车轮的接地点转

        def body():
            b = VGroup()
            box = Rectangle(width=1.0 * sc, height=0.9 * sc, color=STEEL, fill_color=NAVY, fill_opacity=0.9).move_to([-3.0, gy + 0.2 * sc + 0.45 * sc, 0])
            wl = Circle(radius=0.15 * sc * 0.6, color=GREY_B, fill_color=GREY_D, fill_opacity=1).move_to([-3.0 - W / 2 * sc, gy + 0.09 * sc, 0])
            wr = Circle(radius=0.15 * sc * 0.6, color=GREY_B, fill_color=GREY_D, fill_opacity=1).move_to([-3.0 + W / 2 * sc, gy + 0.09 * sc, 0])
            cg = Dot([-3.0, gy + H * sc, 0], color=YELLOW, radius=0.09)
            b.add(box, wl, wr, cg)
            b.rotate(-tilt.get_value(), about_point=piv)
            return b
        car = always_redraw(body)
        self.add(car)
        self.add(zh("内侧", 22, MUTED).move_to([-3.0 - W / 2 * sc, gy - 0.35, 0]), zh("外侧", 22, MUTED).move_to([-3.0 + W / 2 * sc, gy - 0.35, 0]))

        def bars():
            ay = min(ay_of(v.get_value()), A_TIP)
            fin = max(M * G / 2 - M * ay * H / W, 0.0)
            fout = M * G - fin
            k = 1.4 / (M * G)
            g = VGroup()
            for x, f, col in ((-3.0 - W / 2 * sc, fin, GREEN if fin > 1 else RED), (-3.0 + W / 2 * sc, fout, GREEN)):
                g.add(Arrow([x, gy - 0.6 - f * k, 0], [x, gy - 0.6, 0], buff=0, color=col, stroke_width=6, max_tip_length_to_length_ratio=0.2)
                      if f > 1 else Dot([x, gy - 0.6, 0], color=RED))
            fy = M * ay
            if fy > 10:
                a = Arrow([-3.0, gy + 0.05, 0], [-3.0 - fy * k * 2.5, gy + 0.05, 0], buff=0, color=C_F, stroke_width=6)
                g.add(a, zh("地面侧向力", 20, C_F).next_to(a, UP, buff=0.05))
            return g
        self.add(always_redraw(bars))
        rd = always_redraw(lambda: VGroup(
            zh(f"v = {v.get_value():.2f} m/s", 28),
            zh(f"a_y = {min(ay_of(v.get_value()), A_TIP):.2f} m/s²", 28, YELLOW),
            zh(f"内侧法向力 {max(M * G / 2 - M * min(ay_of(v.get_value()), A_TIP) * H / W, 0):.0f} N", 26, GREEN),
            zh("干地面 μ𝔤 = 6.87 m/s²", 24, MUTED),
            zh("侧翻 𝔤w/(2h) = 6.04 m/s²", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT).move_to([3.4, 0.6, 0]))
        self.add(rd)
        self.play(v.animate.set_value(4.22), run_time=5.0, rate_func=linear)
        self.play(tilt.animate.set_value(0.9), run_time=1.6, rate_func=rate_functions.ease_in_quad)
        self.caption("满载 AGV 的质心高：干地面上内侧车轮先离地，车在打滑之前就翻了",
                     "The loaded AGV's centre of mass is high: on a dry floor the inner wheels lift before the tyres slide", wait=2.5)
        self.clear_stage()
        # (2) 俯视：湿地面侧滑
        c0 = np.array([-1.0, -2.2, 0])
        s2 = 1.15
        arc = Arc(radius=R * s2, start_angle=0, angle=PI * 0.9, arc_center=c0, color=GREY_B, stroke_width=3)
        self.add(arc, zh("弯道 R = 3 m", 22, MUTED).move_to(c0 + np.array([R * s2 + 0.9, 0.3, 0])))
        th = ValueTracker(0.0)
        drift = ValueTracker(0.0)

        def top():
            t = th.get_value()
            r = (R + drift.get_value()) * s2
            p = c0 + r * np.array([math.cos(t), math.sin(t), 0])
            b = Rectangle(width=0.45, height=0.9, color=STEEL, fill_color=NAVY, fill_opacity=1).move_to(p).rotate(t)
            return b
        self.add(always_redraw(top))
        self.caption("换到湿地面：摩擦系数只有 0.4", "Now a wet floor: the friction coefficient is only 0.4", wait=0.5)
        v2 = ValueTracker(2.5)
        rd2 = always_redraw(lambda: VGroup(
            zh("湿地面 μ = 0.4", 28, BLUE),
            zh(f"v = {v2.get_value():.2f} m/s", 26),
            zh(f"a_y = {min(ay_of(v2.get_value()), A_WET):.2f} m/s²", 26, YELLOW),
            zh("上限 μ𝔤 = 3.92 m/s²", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT).move_to([4.2, 1.2, 0]))
        self.add(rd2)
        self.play(th.animate.set_value(1.2), v2.animate.set_value(3.4), run_time=3.0, rate_func=linear)
        self.play(th.animate.set_value(2.2), v2.animate.set_value(3.9), drift.animate.set_value(1.6), run_time=2.5, rate_func=linear)
        self.caption("湿地面上侧向力先到摩擦的上限：a_y 不能再大，车速再高，车就向弯道外侧滑出",
                     "On a wet floor the lateral force reaches the friction limit first: a_y cannot grow and the AGV slides outward", wait=2.5)
        self.clear_stage()
        # (3) 极限与质心高度
        ax = Axes(x_range=[0.2, 1.4, 0.2], y_range=[0, 14, 2], x_length=7, y_length=4.2, tips=False,
                  axis_config=dict(color=GREY_B, include_numbers=True, font_size=22)).move_to([-0.6, 0.2, 0])
        self.play(Create(ax), run_time=0.8)
        tip = ax.plot(lambda x: G * W / (2 * x), x_range=[0.29, 1.4], color=YELLOW)
        dry = ax.plot(lambda x: A_DRY, x_range=[0.2, 1.4], color=BLUE)
        wet = ax.plot(lambda x: A_WET, x_range=[0.2, 1.4], color=RED)
        self.play(Create(tip), Create(dry), Create(wet), run_time=1.5)
        self.add(zh("侧翻 𝔤w/(2h)", 22, YELLOW).next_to(ax.c2p(0.4, 9.8), RIGHT),
                 zh("侧滑（干）μ𝔤", 22, BLUE).next_to(ax.c2p(1.0, 6.9), UP, buff=0.1),
                 zh("侧滑（湿）", 22, RED).next_to(ax.c2p(1.15, 3.9), UP, buff=0.1),
                 zh("质心高度 h / m", 22, MUTED).next_to(ax, DOWN, buff=0.15),
                 zh("极限 a_y", 22, MUTED).next_to(ax, LEFT, buff=0.1).shift(UP * 1.5))
        hs = ax.c2p(W / (2 * 0.7), A_DRY)
        self.play(FadeIn(Dot(hs, color=WHITE)), FadeIn(DashedLine(ax.c2p(0.65, 0), ax.c2p(0.65, 13), color=WHITE)), run_time=0.6)
        self.add(zh("满载 AGV", 22).next_to(ax.c2p(0.65, 12.5), RIGHT, buff=0.1))
        self.caption("质心高于 w/(2μ) 的车先翻后滑：高大的车和满载的 AGV 弯道限速要按侧翻算",
                     "Vehicles whose centre of mass is above w/(2μ) roll over before they skid: limit their cornering speed by rollover", wait=2.5)
        self.card([["轮式车的极限", "Limits of a wheeled vehicle"],
                   MathTex(r"a_y \le \mu\mathfrak g,\qquad a_y \le \frac{\mathfrak g\,w}{2h}", font_size=44),
                   MathTex(r"F_{z,\text{in}} = \frac{m\mathfrak g}{2} - \frac{m a_y h}{w}", font_size=40),
                   ["加速、制动、转弯都会让载荷在车轮之间转移", "Accelerating, braking and turning all shift load between the wheels"]])
