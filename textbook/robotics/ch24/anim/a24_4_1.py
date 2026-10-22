"""动画 24.4.1（配图 24.4.2）：双摆的混沌（算例 24.4.5）。两根相同的均匀细杆，长 0.3 m、质量 0.2 kg，从 (120°, 60°) 静止放开；
第二个双摆的上杆初始角多 10⁻⁹ rad。场景程序自己用 RK4（步长 1 ms）积分两连杆臂的方程 (24.2.9)（τ = 0），
与程序 24.4.1 的结果一致：约 8.2 s 后两者相差 0.1 rad 以上，此后各走各的路；两者的机械能都守恒。
右边的柱状图是第一个双摆的动能、势能（以两杆下垂为零点）和机械能。按实际时间播放 12 s。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G, L, M = 9.81, 0.3, 0.2
R = L / 2
J = M * L * L / 3
DT, TEND = 0.001, 12.0
SC = 4.0                                   # 1 m 画成 4 个单位


def mass(p2):
    b = M * L * R * math.cos(p2)
    return np.array([[J + J + M * L * L + 2 * b, J + b], [J + b, J]])


def acc(x):
    p, pd = x[:2], x[2:]
    h = M * L * R * math.sin(p[1])
    c = np.array([-h * (2 * pd[0] * pd[1] + pd[1] ** 2), h * pd[0] ** 2])
    g2 = M * G * R * math.cos(p[0] + p[1])
    g = np.array([M * G * R * math.cos(p[0]) + M * G * L * math.cos(p[0]) + g2, g2])
    return np.linalg.solve(mass(p[1]), -c - g)


def f(x):
    return np.r_[x[2:], acc(x)]


def run(x0):
    x = np.array(x0, float)
    out = [x.copy()]
    for _ in range(int(round(TEND / DT))):
        k1 = f(x)
        k2 = f(x + DT / 2 * k1)
        k3 = f(x + DT / 2 * k2)
        k4 = f(x + DT * k3)
        x = x + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(x.copy())
    return np.array(out)


def energy(x):
    p, pd = x[:2], x[2:]
    K = 0.5 * pd @ mass(p[1]) @ pd
    y1 = R * math.sin(p[0])
    y2 = L * math.sin(p[0]) + R * math.sin(p[0] + p[1])
    U = M * G * (y1 + y2) - M * G * (-R - (L + R))
    return K, U


class Lesson(Base):
    def construct(self):
        self.title("24.4", "双摆的混沌：轨迹分道扬镳，能量始终守恒", "Chaos in a double pendulum: paths part, energy stays")
        x0 = np.array([math.radians(120), math.radians(60), 0.0, 0.0])
        A = run(x0)
        B = run(x0 + np.array([1e-9, 0, 0, 0]))
        piv = np.array([-2.2, 0.5, 0])
        self.add(Dot(piv, radius=0.08, color=WHITE), Line(piv + LEFT * 0.5, piv + RIGHT * 0.5, color=GREY_B, stroke_width=4))
        # 能量柱
        o = np.array([3.0, -1.6, 0])
        Etot = sum(energy(A[0]))
        ysc = 3.0 / 2.2
        self.add(Line(o + LEFT * 0.3, o + RIGHT * 2.8, color=GREY_B, stroke_width=2))
        labs = [["动能 K", "kinetic"], ["势能 U", "potential"], ["机械能 E", "total"]]
        cols = [RED, BLUE, YELLOW]
        for k in range(3):
            self.add(bi(labs[k], 18, cols[k]).move_to(o + RIGHT * (0.3 + 0.95 * k) + DOWN * 0.45))
        self.add(DashedLine(o + LEFT * 0.3 + UP * Etot * ysc, o + RIGHT * 2.8 + UP * Etot * ysc, color=YELLOW, stroke_width=1.5))
        tk = ValueTracker(0.0)

        def pend(x, col, op):
            p1 = piv + SC * L * np.array([math.cos(x[0]), math.sin(x[0]), 0])
            p2 = p1 + SC * L * np.array([math.cos(x[0] + x[1]), math.sin(x[0] + x[1]), 0])
            return VGroup(Line(piv, p1, color=col, stroke_width=9, stroke_opacity=op), Line(p1, p2, color=col, stroke_width=9, stroke_opacity=op),
                          Dot(p1, radius=0.07, color=WHITE), Dot(p2, radius=0.06, color=col))

        def scene():
            t = tk.get_value()
            i = min(int(round(t / DT)), len(A) - 1)
            g = VGroup(pend(B[i], RED, 0.75), pend(A[i], BLUE, 0.85))
            K, U = energy(A[i])
            for k, v in enumerate((K, U, K + U)):
                if v * ysc > 1e-3:
                    g.add(Rectangle(width=0.6, height=v * ysc, color=cols[k], fill_color=cols[k], fill_opacity=0.85, stroke_width=0)
                          .move_to(o + RIGHT * (0.3 + 0.95 * k) + UP * v * ysc / 2))
            gap = abs(A[i, 0] - B[i, 0]) + abs(A[i, 1] - B[i, 1])
            g.add(zh(f"t = {t:.2f} s", 24, INK).move_to([-5.2, -2.3, 0]))
            g.add(zh(f"两者的角度差 {gap:.1e} rad" if gap < 1e-3 else f"两者的角度差 {gap:.2f} rad", 22, GREY_A).move_to([-1.0, -2.3, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("蓝、红两个双摆的初始角度只差十亿分之一弧度，起初完全重合",
                     "The blue and red pendulums start a billionth of a radian apart and move as one", wait=0)
        self.play(tk.animate.set_value(6.0), run_time=6.0, rate_func=linear)
        self.caption("差别被指数地放大：约 8 秒后两者分道扬镳。动能、势能此消彼长，机械能始终不变",
                     "The difference grows exponentially: after about 8 s they part. K and U trade, E stays constant", wait=0)
        self.play(tk.animate.set_value(TEND), run_time=TEND - 6.0, rate_func=linear)
        self.card([["混沌：比较轨迹只在短时间内有意义，检验仿真要用守恒量", "Chaos: compare paths only briefly; test simulations with conserved quantities"],
                   MathTex(r"\frac{\mathrm dE}{\mathrm dt} = \dot\theta^{\mathsf T}\tau", font_size=48),
                   ["不加驱动、不加摩擦时，机械能 E = K + U 守恒", "With no drive and no friction, E = K + U is conserved"]])
