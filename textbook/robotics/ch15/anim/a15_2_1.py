"""动画 15.2.1（配图 15.2.1）：平面 2R 臂（0.425、0.392 m）的末端被一根虚拟弹簧拉向目标 (0.45, 0.35) m。
关节力矩 τ = Jᵀ F 画成两个圆弧箭头（长度与力矩成正比）；手臂按连续时间的雅可比转置法 θ̇ = K Jᵀ e 运动，
初值 (0, 1) rad（算例 15.2.1）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
PD = np.array([0.45, 0.35])
SC = 8.0
O = np.array([-4.2, -2.3, 0.0])


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


def fk(th):
    e = np.array([L1 * math.cos(th[0]), L1 * math.sin(th[0])])
    p = e + L2 * np.array([math.cos(th[0] + th[1]), math.sin(th[0] + th[1])])
    return e, p


def jac(th):
    s1, c1 = math.sin(th[0]), math.cos(th[0])
    s12, c12 = math.sin(th[0] + th[1]), math.cos(th[0] + th[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


def flow(th0, K=20.0, dt=0.002, T=6.0):
    th = np.array(th0, float)
    out = [th.copy()]
    for _ in range(int(T / dt)):
        e = PD - fk(th)[1]
        th = th + dt * K * jac(th).T @ e
        out.append(th.copy())
    return out


class Lesson(Base):
    def construct(self):
        self.title("15.2", "雅可比转置法：虚拟弹簧", "The Jacobian transpose method: a virtual spring")
        traj = flow([0.0, 1.0])
        tr = ValueTracker(0.0)

        def th():
            i = min(int(tr.get_value() * (len(traj) - 1)), len(traj) - 1)
            return traj[i]

        base = Polygon(O + LEFT * 0.35 + DOWN * 0.25, O + RIGHT * 0.35 + DOWN * 0.25, O + RIGHT * 0.18, O + LEFT * 0.18,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        tgt = Dot(S(*PD), radius=0.11, color=RED)
        tl = zh("目标", 22, RED).next_to(tgt, UP, buff=0.12)

        def scene():
            t = th()
            e, p = fk(t)
            E, P = S(*e), S(*p)
            g = VGroup(Line(O, E, color=STEEL, stroke_width=12), Line(E, P, color=STEEL, stroke_width=9),
                       Dot(O, radius=0.1, color=WHITE), Dot(E, radius=0.09, color=WHITE))
            d = PD - p
            n = np.linalg.norm(d)
            # 弹簧：锯齿线
            if n > 0.004:
                u = d / n
                w = np.array([-u[1], u[0]])
                pts = [p]
                for i in range(1, 12):
                    pts.append(p + d * i / 12 + w * 0.012 * (1 if i % 2 else -1))
                pts.append(PD)
                g.add(VMobject(color=YELLOW, stroke_width=3).set_points_as_corners([S(*q) for q in pts]))
            else:
                g.add(Line(P, P + RIGHT * 0.01, stroke_width=0))
            tau = jac(t).T @ (100 * d)
            for c, tq, r in ((O, tau[0], 0.55), (E, tau[1], 0.45)):
                ang = max(min(tq / 8.0, 1.0), -1.0) * 2.4
                if abs(ang) < 0.3:
                    g.add(Line(c, c + RIGHT * 0.01, stroke_width=0))
                    continue
                a = Arc(radius=r, start_angle=0.6, angle=ang, arc_center=c, color=GREEN, stroke_width=4)
                a.add_tip(tip_length=0.18)
                g.add(a)
            return g

        def trace():
            k = max(2, int(tr.get_value() * (len(traj) - 1)))
            pts = [S(*fk(traj[i])[1]) for i in range(0, k, 10)] + [S(*fk(traj[k - 1])[1])]
            return VMobject(color=ORANGE, stroke_width=2.5).set_points_as_corners(pts)

        def info():
            e = float(np.linalg.norm(PD - fk(th())[1]))
            return VGroup(Text("‖e‖ = %.1f mm" % (1000 * e), font=LATIN, font_size=26, color=WHITE),
                          Text("τ = Jᵀ F", font=LATIN, font_size=26, color=GREEN)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).shift(DOWN * 0.9)

        self.play(FadeIn(base), FadeIn(tgt), Write(tl))
        sc, trc, inf = always_redraw(scene), always_redraw(trace), always_redraw(info)
        self.add(trc, sc, inf)
        self.caption("弹簧把末端拉向目标：F = kₛ e", "A spring pulls the tip toward the target: F = kₛ e")
        self.caption("力传到关节：τ = Jᵀ F（绿色弧线），两个关节都要逆时针转",
                     "The force reaches the joints as τ = Jᵀ F (green arcs); both joints turn counter-clockwise", wait=2.0)
        self.caption("关节转速与力矩成正比：θ̇ = K Jᵀ e", "Joint speed in proportion to torque: θ̇ = K Jᵀ e")
        self.play(tr.animate.set_value(0.35), run_time=4.0, rate_func=linear)
        self.caption("误差只减不增，但越近越慢：弹簧越短，拉力越小",
                     "The error never grows, but it slows down: a shorter spring pulls less", wait=0.5)
        self.play(tr.animate.set_value(1.0), run_time=5.0, rate_func=linear)
        self.wait(0.8)
        self.card([["雅可比转置法", "The Jacobian transpose method"],
                   MathTex(r"\Delta\theta = \alpha\,J^{\mathsf T}e", font_size=44),
                   MathTex(r"\tfrac{\mathrm d}{\mathrm dt}\tfrac12\|e\|^2 = -K\,\|J^{\mathsf T}e\|^2 \le 0", font_size=38),
                   ["不求逆、误差不增；代价是线性收敛", "No inverse, the error never grows; the price is linear convergence"]])
