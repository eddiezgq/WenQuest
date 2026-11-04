"""动画 17.5.1（配图 17.5.2）：断电的两连杆机械臂（参数同算例 17.5.1）从 q = (0°, 90°) 静止释放，关节不出力，就是一个双摆。
另一只臂 q₁ 的初值多 0.001°。两只臂的运动用 RK4（步长 1 ms）预先算好：开始时完全重合，约 6 s 后末端相差 10 cm，此后毫不相干。"""
from manim import *
from wq_anim import *
import numpy as np

m1, c1, L1, I1 = 8.4, 0.21, 0.425, 0.13
m2, c2, L2, I2 = 2.3, 0.196, 0.392, 0.031
G = 9.81
SC = 3.3                                                        # 画面单位 / m
BASE = np.array([0.0, 0.4, 0.0])
TEND, H, EVERY = 9.0, 1e-3, 20


def f(y):
    q1, q2, d1, d2 = y
    M11 = I1 + I2 + m1 * c1 ** 2 + m2 * (L1 ** 2 + c2 ** 2 + 2 * L1 * c2 * np.cos(q2))
    M12 = I2 + m2 * (c2 ** 2 + L1 * c2 * np.cos(q2)); M22 = I2 + m2 * c2 ** 2
    h = m2 * L1 * c2 * np.sin(q2)
    g1 = G * ((m1 * c1 + m2 * L1) * np.cos(q1) + m2 * c2 * np.cos(q1 + q2)); g2 = G * m2 * c2 * np.cos(q1 + q2)
    b1 = h * (2 * d1 * d2 + d2 ** 2) - g1; b2 = -h * d1 ** 2 - g2; det = M11 * M22 - M12 ** 2
    return np.array([d1, d2, (M22 * b1 - M12 * b2) / det, (M11 * b2 - M12 * b1) / det])


def run(dq1):
    y = np.array([np.radians(dq1), np.radians(90.0), 0.0, 0.0])
    out = [y[:2].copy()]
    for i in range(1, int(round(TEND / H)) + 1):
        k1 = f(y); k2 = f(y + H / 2 * k1); k3 = f(y + H / 2 * k2); k4 = f(y + H * k3)
        y = y + H / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if i % EVERY == 0:
            out.append(y[:2].copy())
    return np.array(out)


QA, QB = run(0.0), run(1e-3)
DT = H * EVERY


def pts(q):
    e = BASE + SC * L1 * np.array([np.cos(q[0]), np.sin(q[0]), 0])
    return e, e + SC * L2 * np.array([np.cos(q[0] + q[1]), np.sin(q[0] + q[1]), 0])


SEP = np.array([np.linalg.norm(pts(a)[1] - pts(b)[1]) / SC for a, b in zip(QA, QB)])


class Lesson(Base):
    def construct(self):
        self.title("17.5", "断电的机械臂：混沌", "An unpowered robot arm: chaos")
        t = ValueTracker(0.0)
        idx = lambda: min(len(QA) - 1, int(round(t.get_value() / DT)))

        def arm_mob(Q, color, width):
            def make():
                e, tip = pts(Q[idx()])
                return VGroup(Line(BASE, e, color=color, stroke_width=width), Line(e, tip, color=color, stroke_width=width * 0.7),
                              Dot(e, radius=0.08, color=WHITE), Dot(tip, radius=0.1, color=color))
            return always_redraw(make)

        def trail(Q, color):
            def make():
                i1 = idx(); i0 = max(0, i1 - int(1.2 / DT))
                p = [pts(Q[i])[1] for i in range(i0, i1 + 1)]
                m = VMobject(stroke_color=color, stroke_width=2, stroke_opacity=0.7)
                m.set_points_as_corners(p if len(p) > 1 else [p[0], p[0]])
                return m
            return always_redraw(make)

        base = Square(0.35, color=GREY_B, fill_color=GREY_E, fill_opacity=1).move_to(BASE)
        A, B = arm_mob(QB, RED, 16), arm_mob(QA, STEEL, 10)
        self.add(base, trail(QB, RED), trail(QA, STEEL), A, B, base)
        clock = always_redraw(lambda: VGroup(zh("t =", 26, MUTED), DecimalNumber(t.get_value(), num_decimal_places=1, font_size=34),
                                             zh("s", 26, MUTED)).arrange(RIGHT, buff=0.12).to_corner(UR, buff=0.5))
        dist = always_redraw(lambda: VGroup(zh("末端相距", 24, MUTED), DecimalNumber(SEP[idx()] * 1000, num_decimal_places=3, font_size=32, color=YELLOW),
                                            zh("mm", 24, MUTED)).arrange(RIGHT, buff=0.12).next_to(clock, DOWN, aligned_edge=RIGHT))
        self.add(clock, dist)
        self.caption("两只一模一样的机械臂断电释放，初始姿态只差 0.001°", "Two identical arms lose power and fall; their starting angles differ by 0.001°")
        self.play(t.animate.set_value(5.0), run_time=10, rate_func=linear)
        self.caption("方程完全确定，可是微小的差别越长越快……", "The equations are exact, yet the tiny difference grows faster and faster…", wait=0)
        self.play(t.animate.set_value(TEND), run_time=8, rate_func=linear)
        self.caption("几秒之后，两只臂毫不相干：这就是混沌", "A few seconds later the two arms have nothing in common: this is chaos")
        self.card([["混沌", "Chaos"],
                   ["确定的方程，长时间的运动却无法预测", "deterministic equations, yet the long-term motion cannot be predicted"],
                   ["初始的微小误差大致按指数增长", "a tiny starting error grows roughly exponentially"],
                   ["检验仿真：看能量守恒，不逐点比轨迹", "to test a simulation, check energy conservation, not trajectories point by point"]])
