"""动画 20.1.1（配图 20.1.2）：Go2 左前脚沿抬脚—前伸—落地的轨迹运动，每一时刻按定理 20.1.2 求逆解。
左：正视（从前方看，y 向右），髋外摆轴、偏距 d、θ₁；右：侧视的腿平面，平面两连杆，膝向后的解（实线）与膝向前的解（虚线，超限）。
尺寸取零件库模型：d = 0.0955 m，l₁ = l₂ = 0.213 m；足端相对大腿关节的轨迹：x 从 −0.10 m 到 +0.10 m，抬高 0.08 m，
侧向先外移 0.03 m 再回到原处（示意）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

D_OFF, L1, L2, H = 0.0955, 0.213, 0.213, 0.2648
SC = 9.0


def ik(xp, y_rel, zp_target):
    """y_rel：足端相对大腿关节的侧向偏移（正为向外）；返回 θ1、z′、两组 (θ2, θ3)。"""
    ry, rz = D_OFF + y_rel, zp_target
    rho = math.hypot(ry, rz)
    zp = -math.sqrt(rho * rho - D_OFF * D_OFF)
    t1 = math.atan2(rz, ry) - math.atan2(zp, D_OFF)
    c3 = (xp * xp + zp * zp - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    c3 = max(-1.0, min(1.0, c3))
    out = []
    for s in (-1, 1):
        t3 = s * math.acos(c3)
        t2 = math.atan2(-xp, -zp) - math.atan2(L2 * math.sin(t3), L1 + L2 * math.cos(t3))
        out.append((t2, t3))
    return t1, zp, out


def path(u):
    """u ∈ [0, 1]：摆线进度的抬脚—前伸—落地轨迹（足端相对大腿关节，单位 m）。"""
    s = u - math.sin(2 * math.pi * u) / (2 * math.pi)
    hz = (1 - math.cos(2 * math.pi * u)) / 2
    return -0.10 + 0.20 * s, 0.03 * math.sin(math.pi * u), -H + 0.08 * hz


class Lesson(Base):
    def construct(self):
        self.title("20.1", "把脚放到落脚点上：腿的逆运动学", "Placing the foot: inverse kinematics of a leg")
        OF = np.array([-3.6, 1.2, 0])          # 正视图中髋外摆轴的位置
        OS = np.array([2.6, 1.2, 0])           # 侧视图中大腿关节的位置
        lab_f = zh("正视：先定 θ₁", 24, INK).move_to(OF + UP * 1.35)
        lab_s = zh("侧视：再解两连杆", 24, INK).move_to(OS + UP * 1.35)
        g1 = Line(OF + LEFT * 1.4 + DOWN * (H * SC + 0.2), OF + RIGHT * 2.0 + DOWN * (H * SC + 0.2), color=GREY_B)
        g2 = Line(OS + LEFT * 2.4 + DOWN * (H * SC + 0.2), OS + RIGHT * 2.4 + DOWN * (H * SC + 0.2), color=GREY_B)
        axis_dot = VGroup(Circle(0.12, color=RED, stroke_width=3).move_to(OF), Dot(OF, radius=0.04, color=RED))
        self.play(FadeIn(VGroup(lab_f, lab_s, g1, g2, axis_dot)), run_time=0.8)
        self.caption("足端中心沿一条抬脚、前伸、落地的轨迹移动；每一时刻都要求三个关节角",
                     "The foot follows a lift–reach–land path; at every instant we need three joint angles", wait=0.5)
        u = ValueTracker(0.0)

        def front():
            xp, yr, zt = path(u.get_value())
            t1, zp, _ = ik(xp, yr, zt)
            R = np.array([[math.cos(t1), -math.sin(t1)], [math.sin(t1), math.cos(t1)]])
            A = R @ np.array([D_OFF, 0.0]) * SC
            B = R @ np.array([D_OFF, zp]) * SC
            pA, pB = OF + np.array([A[0], A[1], 0]), OF + np.array([B[0], B[1], 0])
            g = VGroup(Line(OF, pA, color=GREY_B, stroke_width=10), Line(pA, pB, color=STEEL, stroke_width=9),
                       Dot(pB, radius=0.17, color=GREY_D), DashedLine(OF, OF + RIGHT * 1.3, color=GREY_C, stroke_width=2))
            arc = Arc(radius=0.75, start_angle=0, angle=t1, arc_center=OF, color=YELLOW, stroke_width=4)
            g.add(arc, Text(("θ₁ = %.1f°" % math.degrees(t1)).replace("-", "−"), font=LATIN, color=YELLOW, font_size=26).move_to(OF + np.array([0.9, -3.3, 0])))
            g.add(Text("|z′| = %.3f m" % abs(zp), font=LATIN, color=STEEL, font_size=26).move_to(OF + np.array([0.9, -3.8, 0])))
            return g

        def side():
            xp, yr, zt = path(u.get_value())
            _, zp, sols = ik(xp, yr, zt)
            F = OS + np.array([xp * SC, zp * SC, 0])
            g = VGroup()
            for k, (t2, t3) in enumerate(sols):
                K = OS + L1 * SC * np.array([-math.sin(t2), -math.cos(t2), 0])
                if k == 0:
                    g.add(Line(OS, K, color=STEEL, stroke_width=10), Line(K, F, color=BLUE_E, stroke_width=8),
                          Dot(K, radius=0.09, color=WHITE))
                    g.add(Text(("θ₂ = %.1f°,  θ₃ = %.1f°" % (math.degrees(t2), math.degrees(t3))).replace("-", "−"), font=LATIN,
                               color=WHITE, font_size=26).move_to(OS + np.array([0.0, -3.3, 0])))
                else:
                    g.add(DashedLine(OS, K, color=ORANGE, stroke_width=4), DashedLine(K, F, color=ORANGE, stroke_width=4))
            g.add(Dot(OS, radius=0.08, color=WHITE), Dot(F, radius=0.17, color=GREY_D))
            g.add(DashedLine(OS, F, color=GREY_B, stroke_width=2))
            return g

        trail = VMobject(color=YELLOW, stroke_width=3)
        pts = []
        for i in range(61):
            xp, yr, zt = path(i / 60)
            _, zp, _ = ik(xp, yr, zt)
            pts.append(OS + np.array([xp * SC, zp * SC, 0]))
        trail.set_points_smoothly(pts)
        self.add(always_redraw(front), always_redraw(side))
        self.play(Create(trail), run_time=1.0)
        self.caption("正视：ρ² = d² + z′²，先由足端到髋外摆轴的距离求 z′，再由方向角之差得 θ₁",
                     "Front: ρ² = d² + z′² gives z′, then θ₁ is a difference of two angles", wait=0)
        self.play(u.animate.set_value(0.5), run_time=5, rate_func=linear)
        self.caption("侧视：余弦定理定膝角 θ₃；膝向前的一组（橙色虚线）θ₃ > 0，超出小腿关节的限位",
                     "Side: the law of cosines gives θ₃; the knee-forward solution (orange) has θ₃ > 0, outside the limits", wait=0)
        self.play(u.animate.set_value(1.0), run_time=5, rate_func=linear)
        self.wait(1.0)
        self.caption("足在髋外摆轴下方、膝向后：Go2 的限位内只剩这一组解",
                     "Foot below the abduction axis, knee back: the only solution inside Go2's limits", wait=1.5)
        self.card([["腿的逆运动学：先定髋外摆，再解两连杆", "Leg IK: abduction first, then the two-link leg"],
                   MathTex(r"z' = -\sqrt{\rho^2 - d^2},\quad \theta_1 = \mathrm{atan2}(r_z, r_y) - \mathrm{atan2}(z', s_y d)", font_size=38),
                   MathTex(r"\cos\theta_3 = \frac{D^2 - l_1^2 - l_2^2}{2 l_1 l_2},\quad \theta_3 < 0", font_size=38),
                   ["四组解中只有一组在限位内（ρ > 2d）", "Only one of four solutions is within the limits (ρ > 2d)"]])
