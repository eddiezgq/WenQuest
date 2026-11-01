"""动画 12.2.1（配图 12.2.1）：同样的质量，离轴越远越难转。两根轻杆上各装两个 1.0 kg 的小球，左边离轴 0.10 m，右边离轴 0.40 m，
加上同样的 0.50 N·m 力矩，从静止开始转（与算例 12.2.1 一致）。转动惯量相差 16 倍，角加速度相差 16 倍，转一圈的时间相差 4 倍。"""
from manim import *
from wq_anim import *
import numpy as np

TAU_, M = 0.50, 1.0
CASES = [(0.10, np.array([-3.3, -0.1, 0]), BLUE), (0.40, np.array([3.3, -0.1, 0]), RED)]
S = 4.0                                     # 画面单位 / m


class Lesson(Base):
    def construct(self):
        self.title("12.2", "离轴越远，越难转动", "The farther from the axis, the harder to turn")
        t = ValueTracker(0.0)
        groups = []
        for r, c, col in CASES:
            J = 2 * M * r * r
            al = TAU_ / J

            def make(r=r, c=c, col=col, al=al):
                th = 0.5 * al * t.get_value() ** 2
                u = np.array([np.cos(th), np.sin(th), 0])
                rod = Line(c - u * 1.8, c + u * 1.8, color=GREY_B, stroke_width=4)
                b1 = Dot(c + u * r * S, radius=0.18, color=col); b2 = Dot(c - u * r * S, radius=0.18, color=col)
                return VGroup(rod, b1, b2, Dot(c, radius=0.08, color=WHITE))
            g = always_redraw(make)
            lab = MathTex(rf"r = {r:.2f}\ \mathrm m ,\quad J = {J:.2f}\ \mathrm{{kg\cdot m^2}}", font_size=28).move_to(c + np.array([0, -2.25, 0]))
            groups.append((g, lab, al))
        self.add(*[g for g, _, _ in groups])
        self.play(*[FadeIn(lab) for _, lab, _ in groups])
        turns = always_redraw(lambda: VGroup(*[MathTex(rf"{0.5 * al * t.get_value() ** 2 / (2 * np.pi):.2f}\ \text{{turns}}", font_size=30, color=YELLOW).move_to(c + np.array([0, 2.35, 0]))
                                               for (_, _, al), (_, c, _) in zip(groups, CASES)]))
        self.add(turns)
        self.caption("两边质量相同、力矩相同：左边的球靠近转轴，右边的远离转轴", "Same masses, same torque: on the left the balls are near the axis, on the right far from it", wait=0)
        self.play(t.animate.set_value(0.709), run_time=2.5, rate_func=linear)
        self.caption("左边转满一圈时，右边才转了十六分之一圈", "When the left one has made a full turn, the right one has made one sixteenth", wait=1.0)
        self.play(t.animate.set_value(2.836), run_time=5.5, rate_func=linear)
        self.caption("距离加倍，转动惯量变成 4 倍：J = Σ m r²", "Double the distance, four times the moment of inertia: J = Σ m r²", wait=2.0)
        self.card([["转动惯量", "Moment of inertia"],
                   MathTex(r"J = \sum m_i r_i^2 , \qquad M = J\alpha", font_size=46),
                   ["质量相同，离轴越远，转动惯量越大，越难加速", "same mass, farther from the axis: larger J, harder to spin up"],
                   ["机械臂把重的电机放在靠近肩部的地方，就是这个道理", "that is why arms keep their heavy motors near the shoulder"]])
