"""动画 24.2.1（配图 24.2.2）：UR5e 的关节 2、3 看作平面两连杆臂，装夹爪 + SH-301 毛坯，把毛坯平着送向卡盘（算例 24.2.2）。
等效参数取自表 24.2.1（程序 24.2.1 由书中 UR5e 模型算出）：a₁ = 0.425 m；大臂 m₁ = 8.393 kg，r₁ = 0.2125 m，J₁ = 0.51288 kg·m²；
小臂连同手腕和负载 m₂ = 8.7019 kg，r₂ = 0.40061 m，J₂ = 1.5735 kg·m²；转子等效惯量 0.1 kg·m²（s₁ = s₂ = 0）。
φ 从 (120°, −120°) 用五次多项式走到 (30°, −30°)。每一瞬按式 (24.2.9) 算出两个关节力矩的惯性项、速度项和重力项，画成柱状图；
虚线是力矩上限 150 N·m。先以 T = 1 s 播放（放慢 3 倍），再以 T = 0.65 s 播放：惯性项变为约 2.4 倍，关节 2 的力矩逼近上限。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
A1, M1, R1, J1 = 0.425, 8.393, 0.2125, 0.51288
M2, R2, J2 = 8.7019, 0.40061, 1.5735
ARM = 0.1
PA, PB = np.radians([120.0, -120.0]), np.radians([30.0, -30.0])
SC = 3.6                                  # 1 m 画成 3.6 个单位
A2_DRAW = 0.75                            # 小臂 + 手腕 + 夹爪 + 毛坯的示意长度，m


def quintic(T, t):
    u = min(max(t / T, 0.0), 1.0)
    s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5
    sd = (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / T
    sdd = (60 * u - 180 * u ** 2 + 120 * u ** 3) / T ** 2
    d = PB - PA
    return PA + s * d, sd * d, sdd * d


def parts(T, t):
    q, qd, qdd = quintic(T, t)
    b = M2 * A1 * R2 * math.cos(q[1])
    h = M2 * A1 * R2 * math.sin(q[1])
    M = np.array([[J1 + J2 + M2 * A1 ** 2 + 2 * b + ARM, J2 + b], [J2 + b, J2 + ARM]])
    c = np.array([-h * (2 * qd[0] * qd[1] + qd[1] ** 2), h * qd[0] ** 2])
    g2 = M2 * G * R2 * math.cos(q[0] + q[1])
    g = np.array([M1 * G * R1 * math.cos(q[0]) + M2 * G * A1 * math.cos(q[0]) + g2, g2])
    return q, M @ qdd, c, g


class Lesson(Base):
    def construct(self):
        self.title("24.2", "两连杆臂的力矩：惯性、速度与重力", "Two-link arm torques: inertia, velocity and gravity")
        base = np.array([-4.2, -1.6, 0])
        self.add(Line(base + LEFT * 0.6 + DOWN * 0.15, base + RIGHT * 0.6 + DOWN * 0.15, color=GREY_B, stroke_width=4))
        chuck = Rectangle(width=0.5, height=0.9, color=GREY_B, fill_color=GREY_D, fill_opacity=0.8).move_to(base + np.array([4.4, 0.77, 0]))
        self.add(chuck, zh("卡盘", 18, MUTED).next_to(chuck, DOWN, buff=0.1))
        # 柱状图
        cols = [BLUE, GREEN, GREY_B, RED]
        names = [["惯性", "inertia"], ["速度", "velocity"], ["重力", "gravity"], ["合计", "total"]]
        origins = [np.array([1.4, -0.2, 0]), np.array([4.3, -0.2, 0])]
        ysc = 1.5 / 150.0
        for j, o in enumerate(origins):
            self.add(Line(o + LEFT * 0.2, o + RIGHT * 2.3, color=GREY_B, stroke_width=2))
            for sg in (1, -1):
                self.add(DashedLine(o + LEFT * 0.2 + UP * sg * 150 * ysc, o + RIGHT * 2.3 + UP * sg * 150 * ysc, color=RED_E, stroke_width=1.5))
            self.add(bi([["关节 2（肩）", "joint 2 (shoulder)"], ["关节 3（肘）", "joint 3 (elbow)"]][j], 20, INK).move_to(o + UP * 2.55 + RIGHT * 1.05))
            for k in range(4):
                self.add(bi(names[k], 15, cols[k]).move_to(o + RIGHT * (0.2 + 0.58 * k) + DOWN * 1.85))
        self.add(zh("±150 N·m", 16, RED_E).move_to(origins[1] + RIGHT * 1.05 + UP * (150 * ysc + 0.18)))
        tk = ValueTracker(0.0)
        per = {"T": 1.0}

        def scene():
            t = tk.get_value()
            q, inert, vel, grav = parts(per["T"], t)
            g = VGroup()
            p1 = base + SC * A1 * np.array([math.cos(q[0]), math.sin(q[0]), 0])
            p2 = p1 + SC * A2_DRAW * np.array([math.cos(q[0] + q[1]), math.sin(q[0] + q[1]), 0])
            g.add(Line(base, p1, color=STEEL, stroke_width=14), Line(p1, p2, color="#d29922", stroke_width=10))
            g.add(Dot(base, radius=0.12, color=WHITE), Dot(p1, radius=0.1, color=WHITE))
            g.add(Rectangle(width=0.5, height=0.18, color=GREY_A, fill_color=GREY_A, fill_opacity=0.9).move_to(p2))
            tot = inert + vel + grav
            for j, o in enumerate(origins):
                for k, v in enumerate((inert[j], vel[j], grav[j], tot[j])):
                    hgt = v * ysc
                    if abs(hgt) > 1e-3:
                        r = Rectangle(width=0.42, height=abs(hgt), color=cols[k], fill_color=cols[k], fill_opacity=0.85, stroke_width=0)
                        r.move_to(o + RIGHT * (0.2 + 0.58 * k) + UP * hgt / 2)
                        g.add(r)
                g.add(zh(f"{tot[j]:.0f} N·m", 20, RED).move_to(o + RIGHT * 1.05 + UP * 2.0))
            g.add(zh(f"T = {per['T']:.2f} s    t = {t:.2f} s", 22, INK).move_to([-4.0, 2.3, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("关节 2、3 把毛坯平着送向卡盘（T = 1 s，放慢 3 倍）：关节 2 的力矩以重力为主",
                     "Joints 2 and 3 move the blank out flat (T = 1 s, 3x slower): gravity dominates joint 2", wait=0)
        self.play(tk.animate.set_value(1.0), run_time=3.0, rate_func=linear)
        self.wait(0.8)
        self.caption("速度项来自离心力和科氏力：小臂只平动，两个关节的速度项恰好相同",
                     "The velocity terms come from centrifugal and Coriolis effects; with the forearm only translating they are equal", wait=0)
        tk.set_value(0.0)
        self.play(tk.animate.set_value(1.0), run_time=3.0, rate_func=linear)
        self.wait(0.6)
        per["T"] = 0.65
        tk.set_value(0.0)
        self.caption("同一个动作只用 0.65 s：惯性项和速度项变为约 2.4 倍，重力项不变，关节 2 逼近 150 N·m",
                     "The same move in 0.65 s: inertial and velocity terms grow about 2.4x, gravity does not, joint 2 nears 150 N·m", wait=0)
        self.play(tk.animate.set_value(0.65), run_time=3.0, rate_func=linear)
        self.wait(1.0)
        self.card([["两连杆臂的运动方程", "The two-link equations of motion"],
                   MathTex(r"M(\varphi)\ddot\varphi + c(\varphi,\dot\varphi) + g(\varphi) = \tau", font_size=46),
                   MathTex(r"\tau_2 = (J_2 + \beta)\ddot\varphi_1 + J_2\ddot\varphi_2 + h\dot\varphi_1^2 + g_2", font_size=40),
                   ["动作快一倍：惯性项、速度项变为 4 倍，重力项不变", "Twice as fast: inertial and velocity terms x4, gravity unchanged"]])
