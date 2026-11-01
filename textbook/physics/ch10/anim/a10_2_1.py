"""动画 10.2.1（配图 10.2.2）：机械臂关节的重力平衡弹簧（与算例 10.2.2 一致：6.0 kg、质心离轴 0.30 m，a = 0.10 m，b = 0.15 m，
零长度弹簧 k = mgr/(ab)）。连杆从竖直转到 150°：重力势能减少多少，弹簧的弹性势能就增加多少，总势能不变，关节不用出力就能停在任何位置。"""
from manim import *
from wq_anim import *
import numpy as np

M, R, A, B, G = 6.0, 0.30, 0.10, 0.15, 9.81
K = M * G * R / (A * B)
S = 6.0                                    # 画面单位 / m
O = np.array([-3.4, 0.4, 0])


def Ug(phi):
    return M * G * R * np.cos(phi)


def Us(phi):
    return 0.5 * K * (A * A + B * B - 2 * A * B * np.cos(phi))


def zigzag(p, q, n=14, amp=0.07):
    d = q - p; L = np.linalg.norm(d); u = d / L; nrm = np.array([-u[1], u[0], 0])
    pts = [p + u * L * i / (2 * n) + nrm * (amp if i % 2 else -amp) * (0 < i < 2 * n) for i in range(2 * n + 1)]
    return VMobject(color=GREEN, stroke_width=3).set_points_as_corners(pts)


class Lesson(Base):
    def construct(self):
        self.title("10.2", "让弹簧来托住机械臂", "Let a spring hold the arm up")
        phi = ValueTracker(0.15)
        post = Line(O, O + np.array([0, A * S + 0.2, 0]), color=GREY_B, stroke_width=6)
        pivot = Dot(O, radius=0.12, color=GREY_A)
        Apt = O + np.array([0, A * S, 0])
        u = lambda: np.array([np.sin(phi.get_value()), np.cos(phi.get_value()), 0])
        link = always_redraw(lambda: Line(O, O + u() * 0.42 * S, color=STEEL, stroke_width=12))
        mass = always_redraw(lambda: Square(0.32, color=RED, fill_opacity=0.9).move_to(O + u() * R * S))
        spring = always_redraw(lambda: zigzag(Apt, O + u() * B * S))
        self.play(FadeIn(post), FadeIn(pivot))
        self.add(link, spring, mass)
        # 能量柱
        base = np.array([3.0, -1.75, 0]); KS = 0.085                    # 画面单位 / J
        def bar(val, color, x, y0=0.0):
            h = max(1e-3, abs(val) * KS)
            return Rectangle(width=0.7, height=h, stroke_width=0, fill_color=color, fill_opacity=0.85).move_to(base + np.array([x, y0 * KS + h / 2, 0]))
        U0 = Ug(np.pi)                                                  # 以连杆朝下为零点，让柱子都为正
        bars = always_redraw(lambda: VGroup(
            bar(Ug(phi.get_value()) - U0, BLUE, -1.0),
            bar(Us(phi.get_value()), GREEN, 0.0),
            bar(Ug(phi.get_value()) - U0, BLUE, 1.0), bar(Us(phi.get_value()), GREEN, 1.0, Ug(phi.get_value()) - U0)))
        names = VGroup(bi(["重力势能", "gravity PE"], size=16, color=BLUE).move_to(base + np.array([-1.0, -0.45, 0])),
                       bi(["弹性势能", "spring PE"], size=16, color=GREEN).move_to(base + np.array([0.0, -0.45, 0])),
                       bi(["总和", "total"], size=16).move_to(base + np.array([1.0, -0.45, 0])))
        top = DashedLine(base + np.array([0.55, (Ug(0) - U0 + Us(0)) * KS, 0]), base + np.array([1.45, (Ug(0) - U0 + Us(0)) * KS, 0]), color=YELLOW)
        self.add(bars); self.play(FadeIn(names), Create(top))
        self.caption("连杆放下时重力势能减少，弹簧被拉长，弹性势能增加", "As the link swings down, gravity PE falls while the stretched spring gains elastic PE", wait=0)
        self.play(phi.animate.set_value(np.radians(150)), run_time=5, rate_func=smooth)
        self.caption("取 kab = mgr，两者之和处处相等：总势能与角度无关", "With kab = mgr their sum is the same everywhere: total PE does not depend on the angle", wait=0)
        self.play(phi.animate.set_value(np.radians(40)), run_time=4, rate_func=smooth)
        self.caption("势能曲线是平的，力矩 −dU/dφ 为零：关节不用出力就能停在任何位置", "A flat potential curve means zero torque −dU/dφ: the joint can stop anywhere without effort", wait=2.0)
        self.card([["重力平衡", "Gravity balancing"],
                   MathTex(r"U = mgr\cos\varphi + \tfrac12 k(a^2 + b^2 - 2ab\cos\varphi)", font_size=36),
                   MathTex(r"kab = mgr \;\Rightarrow\; \frac{\mathrm dU}{\mathrm d\varphi} = 0", font_size=40),
                   ["电机只需提供加速所需的转矩，停住不费力", "the motor only supplies torque to accelerate; holding costs nothing"]])
