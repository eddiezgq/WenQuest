"""动画 29.3.1（配图 29.3.1）：时间步长与稳定性。
弹簧-阻尼器 ẍ = −ω²x − cẋ（ω = 1，ζ = 1）用半隐式欧拉法积分：阻尼显式时稳定界限 hω = 2(√2 − 1) ≈ 0.83；
取 hω = 0.5 时点沿真实轨线收敛，取 hω = 0.95 时每一步“刹过头”，振幅一步比一步大；阻尼改成隐式，hω = 2 也稳定。
最后是 WQ-CR5 的腕关节 J6：出厂位置环的 kv 显式处理，Euler 的步长上限约 2.0 ms，3 ms 时手腕抖起来（与算例 29.3.1 一致）。"""
from manim import *
from wq_anim import *
import numpy as np
import math


def run(h, n, implicit=False, w=1.0, z=1.0):
    c = 2 * z * w
    x, v = 1.0, 0.0
    out = [(0.0, x)]
    for k in range(n):
        if implicit:
            v = (v - h * w * w * x) / (1 + h * c)
        else:
            v = v + h * (-w * w * x - c * v)
        x = x + h * v
        out.append(((k + 1) * h, x))
    return out


class Lesson(Base):
    def construct(self):
        self.title("29.3", "步长取大了，仿真会“炸”", "Take too large a step and the simulation blows up")
        ax = Axes(x_range=[0, 14, 2], y_range=[-2.5, 2.5, 1], x_length=9, y_length=4.2, tips=False,
                  axis_config=dict(color=GREY_B, include_numbers=True, font_size=20)).move_to([-0.8, -0.2, 0])
        self.play(Create(ax), run_time=0.6)
        exact = ax.plot(lambda t: (1 + t) * math.exp(-t), x_range=[0, 14], color=GREEN)
        self.play(Create(exact), run_time=0.8)
        self.add(zh("真实解（临界阻尼）", 22, GREEN).move_to(ax.c2p(9, 1.8)))
        eq = MathTex(r"\ddot x = -\omega^2 x - c\dot x,\ \ \zeta = 1", font_size=34).to_corner(UR, buff=0.5).shift(DOWN * 0.8)
        self.add(eq)

        def show(h, n, col, label, implicit=False):
            pts = run(h, n, implicit)
            dots = VGroup(*[Dot(ax.c2p(t, max(min(x, 2.45), -2.45)), color=col, radius=0.05) for t, x in pts])
            path = VMobject(color=col, stroke_width=2).set_points_as_corners([ax.c2p(t, max(min(x, 2.45), -2.45)) for t, x in pts])
            lab = zh(label, 24, col).to_corner(UR, buff=0.5).shift(DOWN * 1.5)
            self.play(FadeIn(lab), run_time=0.3)
            self.play(Create(path), LaggedStart(*[FadeIn(d) for d in dots], lag_ratio=0.05), run_time=2.2)
            return VGroup(dots, path, lab)
        g1 = show(0.5, 28, BLUE, "hω = 0.5：收敛")
        self.caption("步长小：每一步都离真实轨线不远，误差随步长减小", "Small step: every point stays near the true curve", wait=1.0)
        self.play(FadeOut(g1), run_time=0.4)
        g2 = show(0.95, 14, RED, "hω = 0.95：越过 2(√2 − 1) ≈ 0.83")
        self.caption("阻尼按当前速度显式计算，步长大了它“刹过头”，速度一步就反向，振幅越来越大",
                     "Damping from the current speed over-brakes on a large step: the speed flips sign and grows", wait=1.5)
        self.play(FadeOut(g2), run_time=0.4)
        g3 = show(2.0, 7, YELLOW, "hω = 2，阻尼隐式：仍然稳定", implicit=True)
        self.caption("阻尼改成隐式（用下一步的速度算）：阻尼越大越稳。MuJoCo 的 implicitfast 就是这样",
                     "Implicit damping (computed from the next speed) gets steadier with more damping; MuJoCo's implicitfast does this", wait=1.5)
        self.clear_stage()
        # WQ-CR5 的手腕
        hub = np.array([-2.5, 0.0, 0])
        th = ValueTracker(0.0)
        wrist = always_redraw(lambda: VGroup(Circle(radius=1.0, color=BLUE, stroke_width=6).move_to(hub),
                                             Line(hub, hub + 1.6 * np.array([math.cos(th.get_value()), math.sin(th.get_value()), 0]), color=ORANGE, stroke_width=10)))
        self.add(wrist, zh("WQ-CR5 的腕关节 J6", 24).next_to(hub, UP, buff=1.3))
        info = VGroup(zh("I = 0.040 kg·m²（八成是电机转子）", 24),
                      zh("kv = 40 N·m·s/rad，显式：c = kv/I ≈ 1000 s⁻¹", 24),
                      zh("Euler 步长上限 ≈ 1/c ≈ 2.0 ms", 26, YELLOW)).arrange(DOWN, aligned_edge=LEFT).move_to([3.0, 0.8, 0])
        self.play(FadeIn(info), run_time=0.8)
        hlab = zh("h = 1.8 ms：稳定", 26, GREEN).move_to([3.0, -1.0, 0])
        self.play(FadeIn(hlab), th.animate.set_value(0.05), run_time=1.0)
        self.play(Transform(hlab, zh("h = 3 ms：手腕抖起来", 26, RED).move_to([3.0, -1.0, 0])), run_time=0.5)
        for k in range(10):
            self.play(th.animate.set_value((0.04 + 0.05 * k) * (-1) ** k), run_time=0.12, rate_func=linear)
        self.caption("最快的模态决定步长：轻的手腕加上高增益的伺服。用 implicitfast，或把阻尼写在关节上",
                     "The fastest mode sets the step: a light wrist with a stiff servo. Use implicitfast, or put the damping on the joint", wait=2.0)
        self.card([["稳定步长", "Stable step"],
                   MathTex(r"(h\omega)^2 + 2hc \le 4\quad(\text{damping explicit})", font_size=38),
                   MathTex(r"(h\omega)^2 \le 4 + 2hc\quad(\text{damping implicit})", font_size=38),
                   ["WQ-CR5 出厂位置环：Euler 约 2.0 ms，implicitfast 不受限", "WQ-CR5 stock loop: about 2.0 ms with Euler, unlimited with implicitfast"]])
