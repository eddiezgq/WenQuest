"""动画 13.3.1（配图 13.3.1）：转椅上收臂加速。人和转椅 1.2 kg·m²，两手各握 2.5 kg 的哑铃，平伸时离轴 0.80 m，以 0.50 r/s 转动；
把哑铃收到 0.15 m，转速变为 1.68 r/s（与算例 13.3.1 一致）。俯视图，按真实时间播放。角动量 L = Jω 始终不变。"""
from manim import *
from wq_anim import *
import numpy as np

J0, MD, RO, RI, N0 = 1.2, 2.5, 0.80, 0.15, 0.50
L = (J0 + 2 * MD * RO ** 2) * 2 * np.pi * N0
T1, T2, T3 = 2.5, 1.5, 3.0                                      # 平伸转、收臂、收拢后转（s）
S = 3.0                                                          # 画面单位 / m
C = np.array([-2.2, -0.2, 0])


def r_of(t):
    if t < T1: return RO
    if t < T1 + T2:
        u = (t - T1) / T2; return RO + (RI - RO) * (3 * u * u - 2 * u ** 3)
    return RI


tg = np.linspace(0, T1 + T2 + T3, 4001)
wg = np.array([L / (J0 + 2 * MD * r_of(t) ** 2) for t in tg])
thg = np.concatenate([[0], np.cumsum(0.5 * (wg[1:] + wg[:-1]) * np.diff(tg))])


class Lesson(Base):
    def construct(self):
        self.title("13.3", "转椅上收臂加速", "Pulling in the arms on a swivel chair")
        t = ValueTracker(0.0)

        def person():
            tv = t.get_value(); th = float(np.interp(tv, tg, thg)); r = r_of(tv)
            u = np.array([np.cos(th), np.sin(th), 0]); n = np.array([-np.sin(th), np.cos(th), 0])
            body = Ellipse(width=1.3, height=0.8, color=GREY_B, fill_opacity=0.25).rotate(th).move_to(C)
            head = Circle(radius=0.28, color=GREY_B, fill_opacity=0.4).move_to(C + n * 0.05)
            arms = VGroup(Line(C + u * 0.55, C + u * max(r * S, 0.6), color=GREY_B, stroke_width=6),
                          Line(C - u * 0.55, C - u * max(r * S, 0.6), color=GREY_B, stroke_width=6))
            dbs = VGroup(Dot(C + u * max(r * S, 0.6), radius=0.17, color=RED), Dot(C - u * max(r * S, 0.6), radius=0.17, color=RED))
            return VGroup(Circle(radius=RO * S + 0.3, color=GREY_D, stroke_width=1.5).move_to(C), body, arms, head, dbs)

        self.add(always_redraw(person))

        def panel():
            tv = t.get_value(); r = r_of(tv); J = J0 + 2 * MD * r * r; w = L / J
            rows = [rf"r = {r:.2f}\ \mathrm m", rf"J = {J:.2f}\ \mathrm{{kg\cdot m^2}}", rf"\omega = {w / (2 * np.pi):.2f}\ \mathrm{{r/s}}",
                    rf"L = J\omega = {J * w:.1f}\ \mathrm{{kg\cdot m^2/s}}", rf"E_\mathrm k = \tfrac12 J\omega^2 = {0.5 * J * w * w:.0f}\ \mathrm J"]
            g = VGroup(*[MathTex(s_, font_size=30) for s_ in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            g[3].set_color(YELLOW)
            return g.move_to(np.array([3.4, 0.2, 0]))

        self.add(always_redraw(panel))
        self.caption("哑铃平伸，人和转椅以 0.5 圈每秒转动；转轴的摩擦不计", "Arms out, turning at 0.5 rev/s; ignore friction at the axle", wait=0)
        self.play(t.animate.set_value(T1), run_time=T1, rate_func=linear)
        self.caption("把哑铃收到胸前：转动惯量变小，转速变大，角动量不变", "Pull the dumbbells in: J drops, the spin speeds up, L stays the same", wait=0)
        self.play(t.animate.set_value(T1 + T2), run_time=T2, rate_func=linear)
        self.play(t.animate.set_value(T1 + T2 + T3), run_time=T3, rate_func=linear)
        self.caption("动能却变成 3.4 倍：多出来的能量是收臂时手臂做的功", "Yet the kinetic energy rises 3.4 times: the arms did work pulling in", wait=2.0)
        self.card([["角动量守恒", "Conservation of angular momentum"],
                   MathTex(r"J_1\omega_1 = J_2\omega_2", font_size=46),
                   ["外力对转轴的力矩为零，角动量不变", "no external torque about the axis: L is constant"],
                   ["转动惯量变小，转速就变大", "smaller moment of inertia, faster spin"]])
