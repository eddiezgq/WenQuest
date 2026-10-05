"""动画 15.1.1（配图 15.1.1）：平面 3R 臂（0.425、0.392、0.1 m）在 SE(2) 上的牛顿-拉夫森迭代。
目标位姿：末端 (0.6, 0.05) m、工具朝下（算例 14.2.2）；初值 θ⁽⁰⁾ = (30°, −40°, −20°)（算例 15.1.1）。
每一步：求误差旋量 V_b = log(T⁻¹T_d)（转角 φ 与极点 c），画出 {b} 绕 c 转到 {d} 的圆弧，再按 J_b Δθ = V_b 修正关节角。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L = (0.425, 0.392, 0.1)
SC = 6.0
O = np.array([-4.2, -1.4, 0.0])
TD = (0.6, 0.05, -math.pi / 2)


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


def joints(th):
    a, p, pts = 0.0, np.zeros(2), [np.zeros(2)]
    for l, t in zip(L, th):
        a += t
        p = p + l * np.array([math.cos(a), math.sin(a)])
        pts.append(p.copy())
    return pts, a


def se2(x, y, phi):
    c, s = math.cos(phi), math.sin(phi)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])


def pose(th):
    pts, a = joints(th)
    return se2(pts[-1][0], pts[-1][1], a)


def log2(T):
    phi = math.atan2(T[1, 0], T[0, 0])
    if abs(phi) < 1e-12:
        return np.array([0.0, T[0, 2], T[1, 2]])
    A = np.array([[math.sin(phi), -(1 - math.cos(phi))], [1 - math.cos(phi), math.sin(phi)]]) / phi
    v = np.linalg.solve(A, T[:2, 2])
    return np.array([phi, v[0], v[1]])


def jb(th):
    pts, a = joints(th)
    c, s = math.cos(a), math.sin(a)
    J = np.zeros((3, 3))
    for i in range(3):
        d = pts[-1] - pts[i]
        vs = np.array([-d[1], d[0]])
        J[:, i] = [1.0, c * vs[0] + s * vs[1], -s * vs[0] + c * vs[1]]
    return J


def iterates(th0, n=5):
    Td = se2(*TD)
    out = [np.array(th0, float)]
    for _ in range(n):
        th = out[-1]
        V = log2(np.linalg.inv(pose(th)) @ Td)
        out.append(th + np.linalg.solve(jb(th), V))
    return out


class Lesson(Base):
    def construct(self):
        self.title("15.1", "李群上的牛顿-拉夫森迭代", "Newton-Raphson iteration on a Lie group")
        th_list = iterates(np.radians([30, -40, -20]))
        Td = se2(*TD)
        tr = ValueTracker(0.0)

        def cur():
            t = tr.get_value()
            k = min(int(t), len(th_list) - 2)
            f = t - k
            return th_list[k] * (1 - f) + th_list[k + 1] * f

        base = Polygon(O + LEFT * 0.35 + DOWN * 0.25, O + RIGHT * 0.35 + DOWN * 0.25, O + RIGHT * 0.18, O + LEFT * 0.18,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)

        def arrow(a, b, col, width):
            d = b - a
            n = np.linalg.norm(d)
            u = d / n
            w = np.array([-u[1], u[0], 0.0])
            h = min(0.2, 0.35 * n)
            tip = Polygon(b, b - h * u + 0.45 * h * w, b - h * u - 0.45 * h * w, color=col, fill_color=col, fill_opacity=1,
                          stroke_width=1)
            return VGroup(Line(a, b - 0.8 * h * u, color=col, stroke_width=width), tip)

        def frame_at(T, length=0.55, width=5):
            o = S(T[0, 2], T[1, 2])
            ex = np.array([T[0, 0], T[1, 0], 0.0]) * length
            ey = np.array([T[0, 1], T[1, 1], 0.0]) * length
            return VGroup(arrow(o, o + ex, RED, width), arrow(o, o + ey, GREEN, width))

        def arm():
            pts, _ = joints(cur())
            P = [S(*p) for p in pts]
            g = VGroup()
            for i in range(3):
                g.add(Line(P[i], P[i + 1], color=STEEL, stroke_width=[12, 9, 7][i]))
            for p in P[:-1]:
                g.add(Dot(p, radius=0.09, color=WHITE))
            g.add(frame_at(pose(cur())))
            return g

        def pole_arc():
            th = cur()
            T = pose(th)
            V = log2(np.linalg.inv(T) @ Td)
            hide = abs(V[0]) < math.radians(1.5)
            if abs(V[0]) < 1e-6:
                V = np.array([1e-6, V[1], V[2]])
            cb = np.array([-V[2], V[1]]) / V[0]
            cs = T[:2, :2] @ cb + T[:2, 2]
            r = np.linalg.norm(T[:2, 2] - cs)
            a0 = math.atan2(T[1, 2] - cs[1], T[0, 2] - cs[0])
            arc = Arc(radius=SC * r, start_angle=a0, angle=V[0], arc_center=S(*cs), color=YELLOW, stroke_width=3)
            g = VGroup(arc, Cross(stroke_color=YELLOW, stroke_width=4).scale(0.12).move_to(S(*cs)),
                       Line(S(*cs), S(T[0, 2], T[1, 2]), color=YELLOW, stroke_width=1.5),
                       Line(S(*cs), S(Td[0, 2], Td[1, 2]), color=YELLOW, stroke_width=1.5))
            if hide or r > 3:
                g.set_stroke(opacity=0)
                g[1].set_fill(opacity=0)
            a, b = S(T[0, 2], T[1, 2]), S(Td[0, 2], Td[1, 2])
            if np.linalg.norm(b - a) > 0.02:
                tline = DashedLine(a, b, color=YELLOW, stroke_width=3)
            else:
                tline = Line(a, a + RIGHT * 0.01, color=YELLOW, stroke_width=0)
            if not hide:
                tline.set_stroke(opacity=0)
            g.add(tline)
            return g

        def info():
            th = cur()
            V = log2(np.linalg.inv(pose(th)) @ Td)
            n = float(np.linalg.norm(V))
            k = int(round(tr.get_value())) if abs(tr.get_value() - round(tr.get_value())) < 1e-6 else None
            e = int(math.floor(math.log10(max(n, 1e-16))))
            n = max(n, 1e-16)
            m = n / 10 ** e
            sup = str(e).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
            lines = [Text("‖V_b‖ = %.1f × 10%s" % (m, sup), font=LATIN, font_size=26, color=WHITE),
                     Text("φ = %.1f°" % math.degrees(V[0]), font=LATIN, font_size=24, color=YELLOW)]
            if k is not None:
                lines.insert(0, Text("k = %d" % k, font=LATIN, font_size=26, color=BLUE_B))
            return VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.9)

        tgt = frame_at(Td, 0.6, 6)
        tlab = MathTex(r"\{d\}", font_size=32, color=WHITE).next_to(S(Td[0, 2], Td[1, 2]), RIGHT + DOWN, buff=0.25)
        self.play(FadeIn(base), FadeIn(tgt), Write(tlab))
        a, pa, inf = always_redraw(arm), always_redraw(pole_arc), always_redraw(info)
        self.add(a)
        self.caption("当前末端坐标系 {b} 与目标 {d}：差多少？", "Current end-effector frame {b} and the target {d}: how far apart?")
        self.play(FadeIn(pa), FadeIn(inf))
        self.caption("误差是一个位移：绕极点 c 转过 φ，即 V_b = log(T⁻¹T_d)",
                     "The error is a displacement: a turn φ about the pole c, V_b = log(T⁻¹T_d)", wait=2.0)
        self.caption("解 J_b Δθ = V_b，关节修正一步", "Solve J_b Δθ = V_b and correct the joints")
        self.play(tr.animate.set_value(1.0), run_time=2.2, rate_func=smooth)
        self.wait(0.6)
        self.caption("朝向已经对上（φ 是关节角之和），剩下的平移误差（虚线）迅速缩短",
                     "The heading already matches (φ is the sum of the joint angles); the remaining shift (dashed) shrinks fast")
        for k in (2, 3, 4, 5):
            self.play(tr.animate.set_value(float(k)), run_time=1.4, rate_func=smooth)
            self.wait(0.4)
        self.caption("五步后误差到 10⁻¹³：每步有效数字约翻一番", "After five steps the error is 10⁻¹³: the digits roughly double each step", wait=2.0)
        self.card([["李群上的牛顿-拉夫森迭代", "Newton-Raphson on a Lie group"],
                   MathTex(r"[\mathcal V_b] = \log\big(T(\theta)^{-1}T_d\big)", font_size=40),
                   MathTex(r"J_b(\theta^{(k)})\,\Delta\theta = \mathcal V_b^{(k)},\quad \theta^{(k+1)} = \theta^{(k)} + \Delta\theta", font_size=36),
                   ["在解附近二次收敛", "Quadratic convergence near a solution"]])
