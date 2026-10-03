"""动画 14.4.1（配图 14.4.1）：球形手腕六轴臂（表 14.4.1：肩高 0.163、大臂 0.425、小臂 0.392、腕长 0.1 m）。
第一段：末端位置不变、姿态连续变化——腕心不动，θ1–θ3 不变，只有 θ4–θ6 在转。
第二段：末端姿态不变、位置平移——θ1–θ3 变化，θ4–θ6 由 R456 = R123ᵀ R_d 按“滚—俯—滚”（x、−y、x）欧拉角求出。
正运动学按指数积公式计算（旋量轴同表 14.4.1），三维点按给定的观察方向正交投影到屏幕上。"""
from manim import *
from wq_anim import *
import numpy as np
import math

H1, LA, LB, D6 = 0.163, 0.425, 0.392, 0.1
XH, YD, ZH = np.array([1.0, 0, 0]), np.array([0, -1.0, 0]), np.array([0, 0, 1.0])
PW0 = np.array([LA + LB, 0, H1])
AX = [(ZH, np.zeros(3)), (YD, np.array([0, 0, H1])), (YD, np.array([LA, 0, H1])), (XH, PW0), (YD, PW0), (XH, PW0)]
ORG = np.array([-1.7, -0.8, 0.0])
SC = 4.6


def rot(w, t):
    K = np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def chain(th):
    """各关节转过 θ 后：肩、肘、腕心、法兰中心的位置，以及末端姿态。"""
    R, p = np.eye(3), np.zeros(3)
    Ts = []
    for (w, q), t in zip(AX, th):
        Ri = rot(w, t)
        p = p + R @ (q - Ri @ q)          # 绕过 q 的轴转动：x ↦ Ri x + (I − Ri) q，累积到当前位姿
        R = R @ Ri
        Ts.append((R.copy(), p.copy()))

    def at(k, x):
        Rk, pk = Ts[k]
        return Rk @ x + pk

    pts = [np.zeros(3), np.array([0, 0, H1]), at(1, np.array([LA, 0, H1])), at(2, PW0), at(5, PW0 + D6 * XH)]
    return pts, Ts[5][0]


def wrist_from(R456, sign=1.0):
    """R456 = Rx(a) R_{−y}(b) Rx(c)：滚—俯—滚欧拉角；取 b 的符号为 sign。"""
    cb = max(-1.0, min(1.0, R456[0, 0]))
    beta = -sign * math.acos(cb)                  # R_{−y}(b) = Ry(−b)
    sb = math.sin(beta)
    a = math.atan2(R456[1, 0] / sb, -R456[2, 0] / sb)
    c = math.atan2(R456[0, 1] / sb, R456[0, 2] / sb)
    return a, -beta, c


VAZ, VEL = math.radians(-60), math.radians(20)        # 观察方向：方位角、仰角（正交投影）


def P3(v):
    x, y, z = (float(t) for t in v)
    sx = -math.sin(VAZ) * x + math.cos(VAZ) * y
    sy = z * math.cos(VEL) - (math.cos(VAZ) * x + math.sin(VAZ) * y) * math.sin(VEL)
    return ORG + SC * np.array([sx, sy, 0.0])


TH0 = np.radians([30, 40, -70, 20, 50, -30])


class Lesson(Base):
    def construct(self):
        self.title("14.4", "腕心不动，只转手腕", "Wrist centre fixed: only the wrist turns")
        th = [ValueTracker(float(v)) for v in TH0]
        floor = Polygon(P3([-0.3, -0.4, 0]), P3([0.9, -0.4, 0]), P3([0.9, 0.7, 0]), P3([-0.3, 0.7, 0]),
                        color=GREY_D, fill_color=GREY_E, fill_opacity=0.25, stroke_width=1)
        self.add(floor)

        def robot():
            pts, R = chain([t.get_value() for t in th])
            s = [P3(x) for x in pts]
            g = VGroup(Line(s[0], s[1], color=GREY_B, stroke_width=14), Line(s[1], s[2], color=STEEL, stroke_width=12),
                       Line(s[2], s[3], color=STEEL, stroke_width=10), Line(s[3], s[4], color=GREY_B, stroke_width=7))
            for x in s[1:3]:
                g.add(Dot(x, radius=0.08, color=WHITE))
            g.add(Dot(s[3], radius=0.12, color=YELLOW))
            for k, col in enumerate((RED, GREEN, BLUE)):
                g.add(Arrow(s[4], P3(pts[4] + 0.12 * R[:, k]), buff=0, color=col, stroke_width=4, max_tip_length_to_length_ratio=0.3))
            return g

        def table():
            vals = [math.degrees(t.get_value()) for t in th]
            rows = VGroup(*[MathTex(r"\theta_%d = %6.1f^\circ" % (i + 1, v), font_size=30, color=(GREY_B if i < 3 else YELLOW))
                            for i, v in enumerate(vals)]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            return rows.to_corner(UR, buff=0.6).shift(DOWN * 0.8)

        rb, tb = always_redraw(robot), always_redraw(table)
        self.add(rb, tb)
        lab = VGroup(Dot(radius=0.1, color=YELLOW), zh("腕心", 22, YELLOW)).arrange(RIGHT, buff=0.12).to_corner(UL, buff=0.6).shift(DOWN * 1.2)
        self.play(FadeIn(lab))
        self.caption("目标的位置不变、姿态在变：腕心不动", "Target position fixed, orientation changing: the wrist centre stays put")
        self.play(th[3].animate.set_value(math.radians(80)), th[4].animate.set_value(math.radians(25)),
                  th[5].animate.set_value(math.radians(60)), run_time=4.0, rate_func=smooth)
        self.caption("θ₁、θ₂、θ₃ 一直不变，只有手腕的三个关节在转",
                     "θ₁, θ₂, θ₃ never change; only the three wrist joints turn")
        self.play(th[3].animate.set_value(math.radians(-10)), th[4].animate.set_value(math.radians(70)),
                  th[5].animate.set_value(math.radians(-60)), run_time=3.5, rate_func=smooth)

        # 第二段：姿态不变，平移目标
        R_d = chain([t.get_value() for t in th])[1]
        a0 = [t.get_value() for t in th[:3]]
        a1 = np.radians([55, 25, -45])
        s = ValueTracker(0.0)

        def upd(_):
            u = s.get_value()
            q = [x + u * (y - x) for x, y in zip(a0, a1)]
            R123 = rot(AX[0][0], q[0]) @ rot(AX[1][0], q[1]) @ rot(AX[2][0], q[2])
            w4, w5, w6 = wrist_from(R123.T @ R_d, 1.0)
            for k, v in enumerate(list(q) + [w4, w5, w6]):
                th[k].set_value(v)

        driver = Mobject()
        driver.add_updater(upd)
        self.add(driver)
        self.caption("姿态不变、位置平移：前三个关节送腕心，手腕随之补偿",
                     "Orientation fixed, position moving: joints 1–3 carry the wrist centre, the wrist compensates")
        self.play(s.animate.set_value(1.0), run_time=4.5, rate_func=smooth)
        driver.clear_updaters()
        self.wait(0.5)
        self.card([["球形手腕：位置与姿态分开求", "Spherical wrist: position and orientation solved apart"],
                   MathTex(r"e^{[\mathcal S_1]\theta_1}e^{[\mathcal S_2]\theta_2}e^{[\mathcal S_3]\theta_3}\,p_{w0} = T_d M^{-1} p_{w0}", font_size=38),
                   ["前三个关节定腕心，后三个关节定姿态", "Joints 1–3 place the wrist centre; joints 4–6 set the orientation"]])
