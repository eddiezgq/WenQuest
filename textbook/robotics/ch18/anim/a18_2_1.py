"""动画 18.2.1（配图 18.2.1）：平面五杆（电机在 (∓0.15, 0) m，主动杆 0.20 m，从动杆 0.30 m，肘部朝外）的末端
沿 y 轴从 0.40 m 降到 y* = √(0.2² − 0.15²) ≈ 0.1323 m。以两个肘点为圆心、半径 0.30 m 的两个圆的交点就是两种装配模式；
末端对外施加 20 N 向下的力时，电机力矩 τ = Jᵀ f 随 det A → 0 急剧增大；到 y* 两圆相切，两种装配模式合一。"""
from manim import *
from wq_anim import *
import numpy as np
import math

C5, l1, l2 = 0.15, 0.20, 0.30
YS = math.sqrt(l1 * l1 - C5 * C5)
K = 6.0
O = np.array([-2.6, -2.2, 0.0])


def S(x, y):
    return O + K * np.array([x, y, 0.0])


def state(y):
    """末端在 (0, y) 时：两个肘点、另一种装配模式的末端、两个电机力矩（末端对外施加 20 N 向下的力）。"""
    out = {}
    th = []
    for ax, sg in ((-C5, 1), (C5, -1)):
        dx, dy = -ax, y
        d = math.hypot(dx, dy)
        c = max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))
        th.append(math.atan2(dy, dx) + sg * math.acos(c))
    B1 = np.array([-C5 + l1 * math.cos(th[0]), l1 * math.sin(th[0])])
    B2 = np.array([C5 + l1 * math.cos(th[1]), l1 * math.sin(th[1])])
    mid = (B1 + B2) / 2
    dd = B2 - B1
    L = np.linalg.norm(dd)
    h = math.sqrt(max(l2 * l2 - L * L / 4, 0.0))
    n = np.array([-dd[1], dd[0]]) / L
    P = np.array([0.0, y])
    A = np.array([P - B1, P - B2])
    Bm = np.diag([l1 * ((P - B1) @ np.array([-math.sin(th[0]), math.cos(th[0])])),
                  l1 * ((P - B2) @ np.array([-math.sin(th[1]), math.cos(th[1])]))])
    det = np.linalg.det(A)
    tau = np.array([float("inf"), float("inf")])
    if abs(det) > 1e-9:
        J = np.linalg.solve(A, Bm)
        tau = J.T @ np.array([0.0, -20.0])
    out.update(B1=B1, B2=B2, Q=mid - h * n, det=det, tau=tau)
    return out


class Lesson(Base):
    def construct(self):
        self.title("18.2", "正运动学奇异：两种装配模式合一", "A direct singularity: two assembly modes merge")
        y = ValueTracker(0.40)
        A1, A2 = S(-C5, 0), S(C5, 0)
        ground_ = VGroup(Square(0.22, color=GREY_B, fill_opacity=1).move_to(A1), Square(0.22, color=GREY_B, fill_opacity=1).move_to(A2))
        self.add(ground_)

        def scene_():
            st = state(y.get_value())
            B1, B2, P, Q = S(*st["B1"]), S(*st["B2"]), S(0, y.get_value()), S(*st["Q"])
            g = VGroup(
                Circle(radius=K * l2, color=GREY_C, stroke_width=1.5).move_to(B1).set_stroke(opacity=0.6),
                Circle(radius=K * l2, color=GREY_C, stroke_width=1.5).move_to(B2).set_stroke(opacity=0.6),
                Line(A1, B1, color=ORANGE, stroke_width=9), Line(A2, B2, color=ORANGE, stroke_width=9),
                Line(B1, P, color=YELLOW, stroke_width=6), Line(B2, P, color=YELLOW, stroke_width=6),
                DashedLine(B1, Q, color=BLUE_C, stroke_width=3), DashedLine(B2, Q, color=BLUE_C, stroke_width=3),
                Dot(B1, radius=0.08, color=WHITE), Dot(B2, radius=0.08, color=WHITE),
                Dot(P, radius=0.11, color=RED), Circle(radius=0.11, color=BLUE_B, stroke_width=3).move_to(Q))
            return g

        mech = always_redraw(scene_)
        self.add(mech)
        leg = VGroup(VGroup(Dot(color=RED), bi(["本装配模式的末端", "end point, this mode"], 20, RED)).arrange(RIGHT, buff=0.15),
                     VGroup(Circle(radius=0.1, color=BLUE_B), bi(["另一种装配模式", "the other assembly mode"], 20, BLUE_B)).arrange(RIGHT, buff=0.15)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UL, buff=0.5).shift(DOWN * 1.3)
        self.play(FadeIn(leg))

        # 右侧：电机力矩（对数刻度的柱条）与 det A
        base_y = -2.3
        X0 = 4.2

        def bars():
            st = state(y.get_value())
            g = VGroup()
            for i, t in enumerate(st["tau"]):
                v = abs(t) if math.isfinite(t) else 1e4
                hgt = 1.15 * max(0.0, math.log10(max(v, 1.0)))        # 1 N·m → 0，10 N·m → 1.15，100 N·m → 2.3
                hgt = min(hgt, 3.45)
                r = Rectangle(width=0.6, height=max(hgt, 0.02), color=RED if v > 50 else ORANGE, fill_opacity=0.85, stroke_width=0)
                r.move_to(np.array([X0 + 1.0 * i, base_y + r.height / 2, 0]))
                g.add(r, MathTex(r"\tau_%d" % (i + 1), font_size=30).next_to(np.array([X0 + 1.0 * i, base_y, 0]), DOWN, buff=0.15))
            return g

        bg = always_redraw(bars)
        axis = VGroup(Line(np.array([X0 - 0.6, base_y, 0]), np.array([X0 + 1.6, base_y, 0]), color=GREY_B),
                      *[VGroup(Line(np.array([X0 - 0.65, base_y + 1.15 * k, 0]), np.array([X0 - 0.55, base_y + 1.15 * k, 0]), color=GREY_B),
                               MathTex(r"10^{%d}" % k, font_size=22, color=GREY_B).next_to(np.array([X0 - 0.65, base_y + 1.15 * k, 0]), LEFT, buff=0.08))
                        for k in range(0, 4)])
        self.add(axis, bg)
        lab1 = MathTex(r"|\tau|_{\max} =", font_size=32).move_to(np.array([X0 - 0.3, 2.65, 0]))
        lab2 = MathTex(r"\det A =", font_size=30, color=GREY_A).move_to(np.array([X0 - 0.3, 2.1, 0]))
        lab3 = MathTex(r"y =", font_size=30, color=YELLOW).move_to(np.array([X0 - 0.3, 1.55, 0]))
        n1 = DecimalNumber(0, num_decimal_places=1, font_size=32, unit=r"\,\mathrm{N\,m}").next_to(lab1, RIGHT, buff=0.15)
        n2 = DecimalNumber(0, num_decimal_places=4, font_size=30, color=GREY_A, unit=r"\,\mathrm{m^2}").next_to(lab2, RIGHT, buff=0.15)
        n3 = DecimalNumber(0, num_decimal_places=3, font_size=30, color=YELLOW, unit=r"\,\mathrm{m}").next_to(lab3, RIGHT, buff=0.15)

        def upd1(m):
            st = state(y.get_value())
            t = max(abs(v) for v in st["tau"])
            m.set_value(min(t, 9999.0) if math.isfinite(t) else 9999.0)
        n1.add_updater(upd1)
        n2.add_updater(lambda m: m.set_value(state(y.get_value())["det"]))
        n3.add_updater(lambda m: m.set_value(y.get_value()))
        self.add(lab1, lab2, lab3, n1, n2, n3)
        self.caption("末端对外施加 20 N 向下的力；两个圆的交点就是两种装配模式", "The end point pushes down with 20 N; the two circles meet at the two assembly modes", wait=1.0)
        self.caption("末端下降：两个交点相互靠近，电机力矩越来越大", "Going down: the two crossings approach, the motor torques grow", wait=0)
        self.play(y.animate.set_value(0.20), run_time=4.0, rate_func=smooth)
        self.play(y.animate.set_value(0.14), run_time=3.0, rate_func=smooth)
        self.play(y.animate.set_value(YS + 0.0008), run_time=3.0, rate_func=smooth)
        self.caption("到 y* ≈ 0.132 m：两圆相切，两种装配模式合一，两根从动杆连成一条直线",
                     "At y* ≈ 0.132 m the circles touch, the two modes merge and the forearms line up", wait=0)
        self.play(y.animate.set_value(YS), run_time=1.5, rate_func=smooth)
        inf = MathTex(r"\infty", font_size=34).next_to(lab1, RIGHT, buff=0.15)
        n1.clear_updaters()
        self.play(FadeOut(n1), FadeIn(inf), run_time=0.5)
        self.wait(1.0)
        self.caption("电机锁死，末端仍能上下作一阶的运动；竖直的力无法平衡", "With motors locked the end point can still move up and down to first order; a vertical force cannot be held",
                     wait=1.5)
        self.card([["正运动学奇异：两种装配模式合一", "Direct singularity: two assembly modes merge"],
                   MathTex(r"\det A = 0 \;\Rightarrow\; \|(f,\mu)\| \sim 1/\sigma_{\min}(G) \to \infty", font_size=40),
                   ["设计时要让工作区远离它", "Keep the workspace well away from it"]])
