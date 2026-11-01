"""动画 31.5.1（配图 31.5.1）：WQ-CR5 的振型与衰减振动。
(1) 第一阶（11.8 Hz，关节按 K1，程序 31.5.1）：J2、J3、J4 的转角比约 0.89 : 1 : 0.75，整条手臂在竖直面里“点头”（侧视，放大）。
(2) 第二阶（14.6 Hz）：J1、J5 为主（1 : 0.83），手臂在水平面里“摇头”（俯视，放大）。
(3) 急停后末端的衰减振动 y = e^(−ζωt) sin(ω_d t)：ζ = 0.02 晃两秒多，ζ = 0.1 半秒就停。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("31.5", "振型与衰减振动", "Mode shapes and decaying vibration")
        s = 6.5
        o = np.array([-5.6, 1.2, 0])
        t = ValueTracker(0.0)
        f1, f2 = 11.8, 14.6
        slow = 1 / 12.0                            # 画面慢放：11.8 Hz → 约 1 Hz

        def chain(angles, lengths, origin, colors, widths):
            pts = [origin]
            a = 0.0
            for th, L in zip(angles, lengths):
                a += th
                pts.append(pts[-1] + s * L * np.array([np.cos(a), np.sin(a), 0]))
            return VGroup(*[Line(pts[i], pts[i + 1], color=colors[i], stroke_width=widths[i]) for i in range(len(lengths))],
                          *[Dot(p, color=WHITE, radius=0.07) for p in pts[:-1]])

        def side():
            a = 0.10 * np.sin(2 * PI * f1 * slow * t.get_value())
            return chain([-0.89 * a, -1.0 * a, -0.75 * a, 0], [0.40, 0.36, 0.10, 0.0001], o,
                         [STEEL, GREEN, ORANGE, WHITE], [14, 10, 8, 1])
        g1 = always_redraw(side)
        ghost = Line(o, o + RIGHT * s * 0.86, color=GREY_B, stroke_width=2)
        lab1 = VGroup(zh("第一阶 11.8 Hz：点头（侧视）", 26, YELLOW), zh("J2 : J3 : J4 ≈ 0.89 : 1 : 0.75", 22, INK)).arrange(DOWN, aligned_edge=LEFT).move_to([3.2, 2.0, 0])
        self.add(ghost, g1, lab1)
        self.play(t.animate.set_value(2.0 / (f1 * slow)), run_time=4.0, rate_func=linear)
        self.caption("J2、J3、J4 三个平行的关节一起摆：减速器是弹簧，负载和手臂是质量", "J2, J3 and J4 swing together: the gears are springs, the payload and arm the mass", wait=0.5)
        self.clear_stage()
        # (2) 第二阶：俯视
        t.set_value(0)
        o2 = np.array([-5.6, 0.6, 0])

        def top():
            a = 0.10 * np.sin(2 * PI * f2 * slow * t.get_value())
            return chain([a, 0.0, 0.83 * a], [0.76, 0.0001, 0.10], o2, [STEEL, GREEN, ORANGE], [12, 1, 8])
        g2 = always_redraw(top)
        lab2 = VGroup(zh("第二阶 14.6 Hz：摇头（俯视）", 26, YELLOW), zh("J1 : J5 ≈ 1 : 0.83", 22, INK)).arrange(DOWN, aligned_edge=LEFT).move_to([3.2, 2.0, 0])
        self.add(Line(o2, o2 + RIGHT * s * 0.86, color=GREY_B, stroke_width=2), g2, lab2)
        self.play(t.animate.set_value(2.0 / (f2 * slow)), run_time=4.0, rate_func=linear)
        self.caption("J1 带着整条手臂在水平面里摆，手腕 J5 跟着反过来", "J1 swings the whole arm sideways and the wrist's J5 answers", wait=0.5)
        self.clear_stage()
        # (3) 衰减振动
        ax = Axes(x_range=[0, 3, 0.5], y_range=[-1.1, 1.1, 0.5], x_length=11, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B}).move_to(DOWN * 0.3)
        xl = zh("时间 / s", 20, MUTED).next_to(ax.x_axis, DOWN, buff=0.2)
        self.play(Create(ax), FadeIn(xl))
        w = 2 * PI * f1
        for z, col, nm in ((0.02, RED, "ζ = 0.02"), (0.10, GREEN, "ζ = 0.10")):
            wd = w * np.sqrt(1 - z * z)
            cv = ax.plot(lambda x, z=z, wd=wd: np.exp(-z * w * x) * np.sin(wd * x), x_range=[0, 3, 0.002], color=col, stroke_width=2.5)
            self.play(Create(cv), run_time=2.0)
            self.add(zh(nm, 22, col).next_to(ax, UP, buff=0.1).shift(RIGHT * (-3 if z < 0.05 else 1)))
        self.caption("阻尼小，晃得久；伺服带宽要离结构频率远一点（3 倍以上），否则控制器会把共振喂大",
                     "Little damping, long ringing; keep the servo bandwidth well below the structure's frequency (3× or more)", wait=1.5)
        self.card([["振动与模态", "Vibration and modes"],
                   ["关节是扭簧、连杆是刚体：K v = ω² M v", "Joints as torsion springs, links rigid: K v = ω² M v"],
                   ["第一阶点头约 12 Hz，第二阶摇头约 15 Hz（5 kg，伸直）", "Mode 1 nods at about 12 Hz, mode 2 shakes at about 15 Hz (5 kg, outstretched)"],
                   ["负载越重、伸得越远，频率越低", "Heavier payload, farther reach, lower frequency"]])
