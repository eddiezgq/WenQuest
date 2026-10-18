"""动画 22.2.1（配图 22.2.3）：梯形与 S 形速度曲线的残余振动（算例 22.2.2、22.2.4）。
两条同样的手臂（俯视）绕关节 1 转过 103.43°（1.8051 rad），速度上限 π rad/s、加速度上限 6 rad/s²：
左边按梯形曲线（1.0982 s），右边按 t_j = 1/f_n = 0.125 s 的 S 形曲线（1.2291 s）。末端的弹性模态 f_n = 8 Hz、ζ = 0.02，
φ'' + 2ζωφ' + ω²φ = −θ̈，TCP 离轴 0.442 m；画面中振动位移放大 150 倍。动画中用小步长的经典龙格-库塔法积分。
放慢 3 倍播放。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L, V, A = 1.8051, math.pi, 6.0
FN, ZETA, RB = 8.0, 0.02, 0.442
W = 2 * math.pi * FN
TJ = 1 / FN
SLOW = 3.0
MAG = 150.0
T_END = 3.2                      # 仿真到 3.2 s（运动在 1.1～1.23 s 结束）


def trap_acc(t):
    ta = V / A
    tc = L / V - V / A
    T = 2 * ta + tc
    if t < 0 or t > T:
        return 0.0, T
    return (A if t < ta else (0.0 if t < ta + tc else -A)), T


def scurve_vp():
    # v'²/a + v' a/j = L（式 (22.2.10)），j = a/t_j
    b = TJ
    return (-b + math.sqrt(b * b + 4 * L / A)) / (2 / A)


VP = scurve_vp()


def s_acc(t):
    # 定理 22.2.2：同一 v' 的梯形加速度，用宽 t_j 的盒形窗滑动平均（数值平均）
    ta = VP / A
    tc = L / VP - VP / A
    T = 2 * ta + tc

    def u(x):
        if x < 0 or x > T:
            return 0.0
        return A if x < ta else (0.0 if x < ta + tc else -A)
    xs = np.linspace(t - TJ, t, 41)
    return float(np.mean([u(x) for x in xs])), T + TJ


def simulate(acc, dt=0.001):
    n = int(T_END / dt) + 1
    ts = np.arange(n) * dt
    th = np.zeros(n)
    x = np.zeros(n)
    s = np.array([0.0, 0.0])          # φ, φ'
    w = 0.0
    q = 0.0

    def f(t, y):
        a = acc(t)[0]
        return np.array([y[1], -a - 2 * ZETA * W * y[1] - W * W * y[0]])
    for k in range(1, n):
        t = ts[k - 1]
        k1 = f(t, s)
        k2 = f(t + dt / 2, s + dt / 2 * k1)
        k3 = f(t + dt / 2, s + dt / 2 * k2)
        k4 = f(t + dt, s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        a = acc(t)[0]
        a2 = acc(t + dt)[0]
        q += w * dt + (2 * a + a2) / 6 * dt * dt
        w += (a + a2) / 2 * dt
        th[k] = q
        x[k] = s[0] * RB * 1000        # mm
    return ts, th, x


class Lesson(Base):
    def construct(self):
        self.title("22.2", "梯形与 S 形：停下以后还晃不晃", "Trapezoid and S-curve: does it keep shaking after stopping?")
        tsA, thA, xA = simulate(trap_acc)
        tsB, thB, xB = simulate(s_acc)
        TA, TB = trap_acc(0)[1], s_acc(0)[1]
        cA, cB = np.array([-3.4, 0.55, 0]), np.array([3.4, 0.55, 0])
        R = 1.7
        a0 = -0.9
        heads = VGroup(bi(["梯形曲线", "trapezoid"], 24, GREEN).move_to(cA + UP * 0.9 + LEFT * 1.7),
                       bi([f"S 形曲线，t_j = 1/f_n", "S-curve, t_j = 1/f_n"], 24, PURPLE_A).move_to(cB + UP * 0.9 + LEFT * 1.9))
        axs = []
        for c in (cA, cB):
            ax = Axes(x_range=[0, T_END, 1], y_range=[-2.5, 2.5, 1], x_length=5.2, y_length=1.3, tips=False,
                      axis_config={"stroke_width": 1.5, "color": GREY_B, "include_ticks": False})
            ax.move_to(c + DOWN * 2.35)
            axs.append(ax)
        labs = VGroup(*[MathTex(r"x\ (\mathrm{mm})", font_size=24, color=INK).next_to(ax, LEFT, buff=0.1) for ax in axs])
        tols = VGroup(*[DashedLine(ax.c2p(0, 0.05), ax.c2p(T_END, 0.05), color=GREY_C, stroke_width=1) for ax in axs])
        self.caption("同一个转动（103°），末端有一个 8 Hz 的弹性模态；振动位移放大 150 倍画出",
                     "The same 103° turn; the tip has an 8 Hz flexible mode; vibration drawn 150 times larger", wait=0)
        self.play(FadeIn(heads), *[FadeIn(a) for a in axs], FadeIn(labs), run_time=1.5)
        tk = ValueTracker(0.0)

        def arms():
            t = tk.get_value()
            k = min(int(round(t / 0.001)), len(tsA) - 1)
            g = VGroup()
            for c, th, x, ts, T, col, ax in ((cA, thA, xA, tsA, TA, GREEN, axs[0]), (cB, thB, xB, tsB, TB, PURPLE_A, axs[1])):
                ang = a0 + th[k]
                e = np.array([math.cos(ang), math.sin(ang), 0])
                n = np.array([-math.sin(ang), math.cos(ang), 0])
                tip = c + R * e
                mass = tip + 0.55 * e + (x[k] / 1000 * MAG * 4.5) * n
                g.add(Circle(radius=0.22, color=GREY_B, fill_color=GREY_E, fill_opacity=1).move_to(c),
                      Line(c, tip, color=col, stroke_width=10),
                      Line(tip, mass, color=GREY_B, stroke_width=3),
                      Dot(mass, radius=0.13, color=YELLOW))
                kk = max(2, k)
                pts = [ax.c2p(ts[i], float(np.clip(x[i], -2.5, 2.5))) for i in range(0, kk, 8)]
                if len(pts) >= 2:
                    g.add(VMobject(color=col, stroke_width=2.5).set_points_as_corners(pts))
                state = ("运动中" if t < T else "已停下") + f"  t = {t:.2f} s"
                g.add(Text(state, font=CJK, font_size=20, color=INK).move_to(c + DOWN * 1.15 + RIGHT * 1.3))
            return g

        self.add(always_redraw(arms))
        self.caption("左：加速度跳变四次，每次都“敲”一下；右：加速度在一个振动周期内均匀升降",
                     "Left: four acceleration jumps, each a knock; right: acceleration ramps over exactly one vibration period", wait=0)
        self.play(tk.animate.set_value(1.25), run_time=1.25 * SLOW, rate_func=linear)
        self.caption("停下以后：梯形曲线的末端还在晃（振幅约 1.5 mm），S 形曲线的末端几乎不动",
                     "After stopping: the trapezoid tip keeps shaking (about 1.5 mm); the S-curve tip hardly moves", wait=0)
        self.play(tk.animate.set_value(T_END), run_time=(T_END - 1.25) * SLOW, rate_func=linear)
        self.wait(1.0)
        self.card([["S 形曲线 = 梯形曲线滑动平均", "S-curve = moving average of the trapezoid"],
                   MathTex(r"T_S = \frac{L}{v} + \frac{v}{a} + \frac{a}{j}", font_size=46),
                   MathTex(r"A_S = A\,\left|\frac{\sin(\pi f_n t_j)}{\pi f_n t_j}\right|", font_size=46),
                   ["取 t_j = 1/f_n，激起的振动互相抵消", "Choose t_j = 1/f_n and the excited vibrations cancel"]])
