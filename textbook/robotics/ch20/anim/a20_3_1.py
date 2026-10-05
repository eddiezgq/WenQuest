"""动画 20.3.1（配图 20.3.3）：Go2 以 0.8 m/s 小跑（t_c = 0.5 s、β = 0.5、抬脚 0.08 m，与算例 20.3.2 相同）。
上：侧视的机器人（从右侧看，x 向右，机身坐标系中看，地面向后移动），近侧两条腿（右前、右后）实色，远侧（左侧）淡色；下：步态图与扫过的时间线。
每条腿：支撑相中足端相对髋匀速后退 ℓ = 0.2 m；摆动相按摆线（式 (20.3.8)）在地面上前进一个步幅 0.4 m，换算到机身坐标系。
关节角由侧视平面两连杆的逆解求出（髋外摆为零）。播放速度为实际的 1/4，最后一段再放慢。"""
from manim import *
from wq_anim import *
import numpy as np
import math

AX, L1, L2, RF = 0.1934, 0.213, 0.213, 0.022
HH = 0.2648
V, TC, BETA, HS = 0.8, 0.5, 0.5, 0.08
LS, ELL = V * TC, V * BETA * TC
PH = {"RL": 0.0, "FR": 0.0, "FL": 0.5, "RR": 0.5}
SC = 7.0
O = np.array([0.0, 1.45, 0])         # 机身原点在屏幕上的位置


def foot_rel(leg, t):
    """足端相对大腿关节（侧视平面）的 (x, z)，以及是否支撑。"""
    u = (t / TC - PH[leg]) % 1.0
    if u < BETA:
        tau = u / BETA
        return np.array([ELL / 2 - ELL * tau, -HH]), True
    tau = (u - BETA) / (1 - BETA)
    s = tau - math.sin(2 * math.pi * tau) / (2 * math.pi)
    hz = (1 - math.cos(2 * math.pi * tau)) / 2
    return np.array([-ELL / 2 + LS * s - V * (1 - BETA) * TC * tau, -HH + HS * hz]), False


def knee(rel):
    xp, zp = rel
    D = math.hypot(xp, zp)
    c3 = max(-1.0, min(1.0, (D * D - L1 * L1 - L2 * L2) / (2 * L1 * L2)))
    t3 = -math.acos(c3)
    t2 = math.atan2(-xp, -zp) - math.atan2(L2 * math.sin(t3), L1 + L2 * math.cos(t3))
    return np.array([-L1 * math.sin(t2), -L1 * math.cos(t2)])


def S(p):
    return O + np.array([p[0] * SC, p[1] * SC, 0])


class Lesson(Base):
    def construct(self):
        self.title("20.3", "Go2 小跑：对角两条腿轮流支撑", "Go2 trotting: diagonal pairs take turns")
        tk = ValueTracker(0.0)
        gy = O[1] - (HH + RF) * SC
        # 步态图
        rows = ["FL", "FR", "RL", "RR"]
        cols = {"FL": STEEL, "RR": STEEL, "FR": ORANGE, "RL": ORANGE}
        gx0, gw, gy0 = -4.0, 8.0, -1.55
        diag = VGroup()
        for r, leg in enumerate(rows):
            y = gy0 - 0.32 * r
            diag.add(Text(leg, font=LATIN, font_size=20, color=INK).move_to([gx0 - 0.35, y, 0]))
            for k in range(-1, 3):
                a = (PH[leg] + k) / 2
                b = a + BETA / 2
                a, b = max(a, 0), min(b, 1)
                if b > a:
                    diag.add(Rectangle(width=(b - a) * gw, height=0.2, fill_color=cols[leg], fill_opacity=0.85, stroke_width=0)
                             .move_to([gx0 + (a + b) / 2 * gw, y, 0]))
        diag.add(Text("步态图（两个周期，深色为支撑相）", font=CJK, font_size=18, color=MUTED).move_to([0, gy0 + 0.32, 0]))
        cursor = always_redraw(lambda: Line([gx0 + ((tk.get_value() / TC) % 2) / 2 * gw, gy0 + 0.15, 0],
                                            [gx0 + ((tk.get_value() / TC) % 2) / 2 * gw, gy0 - 1.1, 0], color=YELLOW, stroke_width=3))

        def robot():
            t = tk.get_value()
            g = VGroup()
            off = (-(V * t) % 0.1)
            for k in range(-9, 10):
                x = k * 0.1 + off
                g.add(Line(S((x, -HH - RF)), S((x - 0.03, -HH - RF - 0.03)), color=GREY_C, stroke_width=1.5))
            g.add(Line(S((-0.95, -HH - RF)), S((0.95, -HH - RF)), color=GREY_B, stroke_width=3))
            body = [(-0.26, -0.05), (0.26, -0.05), (0.29, 0.0), (0.26, 0.05), (-0.26, 0.05)]
            g.add(Polygon(*[S(c) for c in body], color=GREY_B, fill_color=NAVY, fill_opacity=1, stroke_width=2))
            for leg, far in (("FL", True), ("RL", True), ("FR", False), ("RR", False)):
                hipx = AX if leg[0] == "F" else -AX
                rel, st = foot_rel(leg, t)
                kn = knee(rel)
                h = np.array([hipx, 0.0])
                op = 0.35 if far else 1.0
                c = cols[leg]
                g.add(Line(S(h), S(h + kn), color=c, stroke_width=8, stroke_opacity=op),
                      Line(S(h + kn), S(h + rel), color=c, stroke_width=6, stroke_opacity=op),
                      Dot(S(h + rel), radius=0.1, color=GREY_D if not st else WHITE, fill_opacity=op))
            g.add(Text("t = %.3f s" % t, font=LATIN, font_size=22, color=YELLOW).move_to([4.6, 2.3, 0]))
            return g

        self.play(FadeIn(diag), run_time=0.6)
        self.add(always_redraw(robot), cursor)
        self.caption("蓝：左前与右后一组；橙：右前与左后一组。两组对角腿交替支撑，任一时刻两只脚着地",
                     "Blue: front-left and rear-right; orange: front-right and rear-left. Diagonal pairs alternate; two feet down at any time", wait=0)
        self.play(tk.animate.set_value(2 * TC), run_time=7, rate_func=linear)
        self.caption("支撑相中脚在地上不动，相对机身后退 ℓ = 0.2 m；摆动相中沿摆线前进一个步幅 0.4 m",
                     "In stance the foot stays put and slides back ℓ = 0.2 m relative to the body; in swing it travels one stride, 0.4 m", wait=0)
        self.play(tk.animate.set_value(4 * TC), run_time=6, rate_func=linear)
        self.caption("放慢一个摆动相：摆动脚对地最高 3.2 m/s，先越过落脚点约 2 cm，再收回落地",
                     "One swing in slow motion: up to 3.2 m/s over ground; it overshoots the foothold by about 2 cm, then pulls back to land", wait=0)
        self.play(tk.animate.set_value(5 * TC), run_time=5, rate_func=linear)
        self.card([["小跑的运动学", "Kinematics of the trot"],
                   MathTex(r"L_s = v\,t_c,\qquad \ell = v\,\beta\,t_c,\qquad x_{\mathrm{td}} = \ell/2", font_size=42),
                   MathTex(r"\bar v_{\mathrm{sw}} = \frac{v}{1-\beta},\qquad v_{\mathrm{sw,max}} = \frac{2v}{1-\beta}", font_size=42),
                   ["β < 1/2 时出现四脚腾空的腾空相", "β < 1/2 brings a flight phase with all four feet off the ground"]])
