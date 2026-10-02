"""动画 7.3.2（配图 7.3.2）：2R 臂（l₁ = 0.425 m，l₂ = 0.392 m）用牛顿法求到达 p_d = (0.45, 0.35) m 的关节角，
从 (0, 1) rad 出发，一次一次地修正，末端逐步落到目标上；屏幕上显示末端误差。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
PD = np.array([0.45, 0.35])
S = 5.0                                   # 1 m 画成 5 个单位
BASE = np.array([-3.6, -1.9, 0])


def fk(th):
    return np.array([L1 * math.cos(th[0]) + L2 * math.cos(th[0] + th[1]),
                     L1 * math.sin(th[0]) + L2 * math.sin(th[0] + th[1])])


def jac(th):
    s1, c1 = math.sin(th[0]), math.cos(th[0])
    s12, c12 = math.sin(th[0] + th[1]), math.cos(th[0] + th[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


def to_screen(p):
    return BASE + S * np.array([p[0], p[1], 0])


class Lesson(Base):
    def construct(self):
        self.title("7.3", "牛顿法求 2R 臂的逆运动学", "Newton's method for 2R inverse kinematics")
        reach = Circle(radius=S * (L1 + L2), color=GREY_C, stroke_width=2).move_to(BASE)
        reach.set_stroke(opacity=0.5)
        arc = DashedVMobject(Arc(radius=S * (L1 + L2), start_angle=-0.3, angle=math.pi * 0.95, arc_center=BASE, color=GREY_C), num_dashes=40)
        target = Star(n=5, outer_radius=0.22, color=RED, fill_opacity=1).move_to(to_screen(PD))
        tlab = MathTex(r"p_d = (0.45,\ 0.35)\ \mathrm m", color=RED, font_size=28).next_to(target, UP, buff=0.15)
        self.play(Create(arc), FadeIn(target), Write(tlab))
        hist = [np.array([0.0, 1.0])]
        for _ in range(5):
            th = hist[-1]
            hist.append(th - np.linalg.solve(jac(th), fk(th) - PD))
        cur = ValueTracker(0.0)

        def pose():
            u = cur.get_value()
            i = min(int(u), len(hist) - 2)
            a = u - i
            th = (1 - a) * hist[i] + a * hist[i + 1]
            return planar_arm(BASE, [math.degrees(th[0]), math.degrees(th[1])], [S * L1, S * L2])

        arm_m = always_redraw(pose)
        self.add(arm_m)

        def readout():
            u = cur.get_value()
            i = int(round(u))
            th = hist[min(i, len(hist) - 1)]
            r = np.linalg.norm(fk(th) - PD)
            g = VGroup(Text("k = %d" % i, font=LATIN, font_size=26, color=YELLOW),
                       Text("θ = (%.4f, %.4f) rad" % (th[0], th[1]), font=LATIN, font_size=22, color=INK),
                       Text("‖p(θ) − p_d‖ = %.1e m" % r, font=LATIN, font_size=22, color=INK))
            return g.arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.5).shift(DOWN * 0.9)

        ro = always_redraw(readout)
        self.add(ro)
        self.caption("初值 θ = (0, 1) rad：末端离目标 0.19 m", "Start θ = (0, 1) rad: the tip is 0.19 m from the target")
        self.caption("每次迭代：用雅可比矩阵把末端误差换算成关节的修正量", "Each step: the Jacobian turns the tip error into joint corrections", wait=0)
        for k in range(1, 5):
            ghost = pose().set_opacity(0.18)
            self.add(ghost)
            self.play(cur.animate.set_value(float(k)), run_time=1.3, rate_func=smooth)
            self.wait(0.5)
        self.caption("误差 0.19 → 0.067 → 0.004 → 2×10⁻⁵ → 5×10⁻¹⁰ m：二次收敛", "Error 0.19 → 0.067 → 0.004 → 2×10⁻⁵ → 5×10⁻¹⁰ m: quadratic convergence")
        self.wait(1)
        self.card([["方程组的牛顿法", "Newton's method for systems"],
                   MathTex(r"\theta^{(k+1)} = \theta^{(k)} - J(\theta^{(k)})^{-1}\big(p(\theta^{(k)}) - p_d\big)", font_size=42),
                   ["det J = l₁l₂ sin θ₂：手臂伸直或折叠时无法计算", "det J = l₁l₂ sin θ₂: fails when the arm is straight or folded"]])
