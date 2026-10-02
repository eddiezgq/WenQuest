"""动画 10.3.1（配图 10.3.2）：SCARA 关节 1 匀速转动（1.0 rad/s）、关节 2 匀速伸直手臂（−1.5 rad/s），
局部基 e_ρ、e_φ 随末端一起转动；速度的径向、横向分量和横向加速度中 ρφ̈、2ρ̇φ̇ 两项实时变化。时间放慢 5 倍。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.35, 0.25
W1, W2 = 1.0, -1.5
TH1, TH2 = math.radians(20), math.radians(130)
SC = 6.0                                    # 1 m 画成 6 个单位
BASE = np.array([-3.6, -2.0, 0])


def kin(t):
    """t 时刻末端的 ρ、φ 及其导数（式 (10.3.11)–(10.3.13)，两关节匀速）。"""
    q1, q2 = TH1 + W1 * t, TH2 + W2 * t
    rho = math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(q2))
    beta = math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
    rhod = -L1 * L2 * math.sin(q2) * W2 / rho
    rhodd = (-L1 * L2 * math.cos(q2) * W2 ** 2 - rhod ** 2) / rho
    db = (L2 * L2 + L1 * L2 * math.cos(q2)) / rho ** 2
    d2b = -L1 * L2 * math.sin(q2) * (L1 ** 2 - L2 ** 2) / rho ** 4
    return q1, q2, rho, q1 + beta, rhod, rhodd, W1 + db * W2, d2b * W2 ** 2


class Lesson(Base):
    def construct(self):
        self.title("10.3", "径向分量与横向分量", "Radial and transverse components")
        axes = VGroup(Arrow(BASE + LEFT * 0.3, BASE + RIGHT * 4.3, buff=0, color=RED, stroke_width=3),
                      Arrow(BASE + DOWN * 0.3, BASE + UP * 4.2, buff=0, color=GREEN, stroke_width=3))
        self.play(FadeIn(axes))
        t = ValueTracker(0.0)

        def scene():
            q1, q2, rho, phi, rd, rdd, pd, pdd = kin(t.get_value())
            arm_ = planar_arm(BASE, [math.degrees(q1), math.degrees(q2)], [L1 * SC, L2 * SC])
            E = BASE + SC * rho * np.array([math.cos(phi), math.sin(phi), 0])
            er = np.array([math.cos(phi), math.sin(phi), 0])
            ep = np.array([-math.sin(phi), math.cos(phi), 0])
            g = VGroup(arm_, DashedLine(BASE, E, color=GREY_B, stroke_width=2),
                       MathTex(r"\rho", font_size=30, color=INK).move_to(BASE + (E - BASE) * 0.45 + 0.3 * ep),
                       Arc(radius=0.6, start_angle=0, angle=phi, arc_center=BASE, color=YELLOW, stroke_width=3),
                       MathTex(r"\varphi", font_size=30, color=YELLOW).move_to(BASE + 0.85 * np.array([math.cos(phi / 2), math.sin(phi / 2), 0])))
            k = 3.0
            vr, vp = rd * er * k, rho * pd * ep * k
            g.add(Arrow(E, E + 0.7 * er, buff=0, color=RED, stroke_width=4, max_tip_length_to_length_ratio=0.2),
                  Arrow(E, E + 0.7 * ep, buff=0, color=GREEN, stroke_width=4, max_tip_length_to_length_ratio=0.2),
                  MathTex(r"e_\rho", font_size=28, color=RED).move_to(E + 0.95 * er),
                  MathTex(r"e_\varphi", font_size=28, color=GREEN).move_to(E + 0.95 * ep))
            g.add(DashedLine(E, E + vr, color=C_V, stroke_width=3), DashedLine(E, E + vp, color=C_V, stroke_width=3),
                  Arrow(E, E + vr + vp, buff=0, color=C_V, stroke_width=6, max_tip_length_to_length_ratio=0.15),
                  MathTex(r"\boldsymbol v", font_size=30, color=C_V).move_to(E + (vr + vp) * 1.12))
            panel = VGroup(
                MathTex(r"\dot\rho = %.3f\ \mathrm{m/s}" % rd, font_size=30),
                MathTex(r"\rho\dot\varphi = %.3f\ \mathrm{m/s}" % (rho * pd), font_size=30),
                MathTex(r"\rho\ddot\varphi = %+.3f\ \mathrm{m/s^2}" % (rho * pdd), font_size=30, color=BLUE_B),
                MathTex(r"2\dot\rho\dot\varphi = %+.3f\ \mathrm{m/s^2}" % (2 * rd * pd), font_size=30, color=ORANGE),
                MathTex(r"a_\varphi = %+.3f\ \mathrm{m/s^2}" % (rho * pdd + 2 * rd * pd), font_size=32, color=RED),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(np.array([4.2, 0.5, 0]))
            g.add(panel)
            return g

        sc = always_redraw(scene)
        self.add(sc)
        self.caption("关节 1 匀速转动，关节 2 匀速伸直：末端离轴越来越远", "Joint 1 turns steadily, joint 2 straightens steadily: the tool moves away from the axis", wait=0)
        self.play(t.animate.set_value(0.6), run_time=5, rate_func=linear)
        self.caption("局部基 e_ρ、e_φ 跟着末端转动：这就是加速度里多出来的项", "The local basis turns with the tool: that is where the extra terms come from", wait=0)
        self.play(t.animate.set_value(1.0), run_time=4, rate_func=linear)
        self.caption("边转边伸时，横向加速度中的“二倍伸出速度乘角速度”一项往往最大", "Turning while extending, the term “twice the outward speed times the turn rate” is often the largest", wait=0)
        self.play(t.animate.set_value(1.25), run_time=3, rate_func=linear)
        self.wait(1)
        self.card([["柱面坐标中的加速度", "Acceleration in cylindrical coordinates"],
                   MathTex(r"\boldsymbol a = (\ddot\rho - \rho\dot\varphi^2)\,\boldsymbol e_\rho + (\rho\ddot\varphi + 2\dot\rho\dot\varphi)\,\boldsymbol e_\varphi + \ddot z\,\boldsymbol e_z", font_size=40),
                   ["系数 2：伸出的速度在转向，转动的速度在变大，各占一半", "The factor 2: the outward velocity turns, the turning velocity grows; half each"]])
