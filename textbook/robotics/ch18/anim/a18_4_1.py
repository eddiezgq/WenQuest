"""动画 18.4.1（配图 18.4.2）：零件库 Delta（R_b = 0.15 m，R_p = 0.04 m，L_a = 0.22 m，L_b = 0.5 m，主动臂转速上限 10.47 rad/s）
走 25/305/25 mm 的拾放循环（中心 (0, 0)、拾放高度 −0.45 m、沿 x 方向）。每段按电机转速限制下的最大匀速走：
在这段路径上最“吃力”的那一点，有一台电机正好到达上限。右边三根柱条是三台电机的转速，虚线为 ±10.47 rad/s。
画面放慢 40 倍：真实的一次往返只需约 0.27 s。"""
from manim import *
from wq_anim import *
import numpy as np
import math

RB, RP, LA, LB = 0.15, 0.04, 0.22, 0.5
WMAX = 10.471976
SC = 7.0
ORG = np.array([-2.6, 1.75, 0.0])
AZ, EL = math.radians(-70), math.radians(14)
RIGHT_ = np.array([-math.sin(AZ), math.cos(AZ), 0.0])
UP_ = np.array([-math.sin(EL) * math.cos(AZ), -math.sin(EL) * math.sin(AZ), math.cos(EL)])


def P(v):
    v = np.asarray(v, dtype=float)
    return ORG + SC * np.array([v @ RIGHT_, v @ UP_, 0.0])


def ek(k):
    f = 2 * math.pi * k / 3
    return np.array([math.cos(f), math.sin(f), 0.0])


def elbow(k, th):
    e = ek(k)
    return RB * e + LA * (math.cos(th) * e - math.sin(th) * np.array([0, 0, 1.0]))


def ik(p):
    out = []
    for k in range(3):
        e = ek(k)
        q = p + (RP - RB) * e
        u, h = q @ e, q[2]
        A, B = -2 * LA * u, 2 * LA * h
        C = LB * LB - LA * LA - q @ q
        r = math.hypot(A, B)
        out.append(math.atan2(B, A) + math.acos(max(-1.0, min(1.0, C / r))))
    return np.array(out)


def jac(p, th):
    A = np.zeros((3, 3))
    B = np.zeros(3)
    for k in range(3):
        d = p + RP * ek(k) - elbow(k, th[k])
        u = d / np.linalg.norm(d)
        dE = LA * (-math.sin(th[k]) * ek(k) - math.cos(th[k]) * np.array([0, 0, 1.0]))
        A[k] = u
        B[k] = u @ dE
    return np.linalg.solve(A, np.diag(B))


# 循环的四个角点与每段的最大匀速
C3 = np.array([0.0, 0.0, -0.45])
AX = np.array([0.1525, 0.0, 0.0])
PTS = [C3 - AX, C3 - AX + [0, 0, 0.025], C3 + AX + [0, 0, 0.025], C3 + AX]
SEGS = []
for S0, S1 in zip(PTS[:-1], PTS[1:]):
    L = float(np.linalg.norm(S1 - S0))
    d = (S1 - S0) / L
    vm = min(WMAX / np.abs(np.linalg.solve(jac(S0 + s * (S1 - S0), ik(S0 + s * (S1 - S0))), d)).max() for s in np.linspace(0, 1, 81))
    SEGS.append((S0, S1, L, d, vm))
T_HALF = sum(L / vm for _, _, L, _, vm in SEGS)


def state(t):
    """t ∈ [0, 2 T_HALF]：去程沿 PTS，回程倒走。返回 (p, θ̇)。"""
    back = t > T_HALF
    tt = 2 * T_HALF - t if back else t
    for S0, S1, L, d, vm in SEGS:
        if tt <= L / vm + 1e-12:
            p = S0 + d * vm * tt
            w = np.linalg.solve(jac(p, ik(p)), vm * d)
            return p, (-w if back else w)
        tt -= L / vm
    S0, S1, L, d, vm = SEGS[-1]
    return S1, np.zeros(3)


class Lesson(Base):
    def construct(self):
        self.title("18.4", "Delta 的拾放循环：电机转速决定节拍", "Delta pick cycle: motor speed sets the pace")
        t = ValueTracker(0.0)
        tri = Polygon(*[P(2 * RB * np.array([math.cos(a), math.sin(a), 0])) for a in np.radians([60, 180, 300])],
                      color=GREY_B, fill_color=GREY_E, fill_opacity=0.8)
        belt = Polygon(*[P(np.array(v)) for v in ([-0.3, -0.12, -0.47], [0.3, -0.12, -0.47], [0.3, 0.12, -0.47], [-0.3, 0.12, -0.47])],
                       color=GREY_C, fill_color=GREY_D, fill_opacity=0.5, stroke_width=1)
        path = VMobject(color=RED, stroke_width=3).set_points_as_corners([P(v) for v in PTS])
        self.add(belt, tri, path)
        cols = [RED, GREEN, BLUE]

        def robot():
            p, _ = state(t.get_value())
            th = ik(p)
            g = VGroup()
            for k in range(3):
                H, E = RB * ek(k), elbow(k, th[k])
                tk = np.cross([0, 0, 1.0], ek(k))
                Q = p + RP * ek(k)
                g.add(Line(P(H), P(E), color=cols[k], stroke_width=8))
                for s in (1, -1):
                    g.add(Line(P(E + s * 0.03 * tk), P(Q + s * 0.03 * tk), color=GREY_A, stroke_width=2))
                g.add(Dot(P(H), radius=0.05, color=WHITE))
            plat = Polygon(*[P(p + 1.9 * RP * np.array([math.cos(a), math.sin(a), 0])) for a in np.radians([60, 180, 300])],
                           color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.9)
            g.add(plat, Dot(P(p), radius=0.06, color=YELLOW))
            return g

        rb = always_redraw(robot)
        self.add(rb)
        X0, Y0, H = 3.6, 0.15, 1.7          # 柱条：中线 Y0，±WMAX 对应 ±H

        frame_ = VGroup(DashedLine([X0 - 0.5, Y0 + H, 0], [X0 + 2.0, Y0 + H, 0], color=GREY_B),
                        DashedLine([X0 - 0.5, Y0 - H, 0], [X0 + 2.0, Y0 - H, 0], color=GREY_B),
                        Line([X0 - 0.5, Y0, 0], [X0 + 2.0, Y0, 0], color=GREY_C, stroke_width=1),
                        MathTex(r"+10.47", font_size=22, color=GREY_B).next_to([X0 - 0.5, Y0 + H, 0], LEFT, buff=0.08),
                        MathTex(r"-10.47", font_size=22, color=GREY_B).next_to([X0 - 0.5, Y0 - H, 0], LEFT, buff=0.08),
                        bi(["电机转速 / (rad/s)", "motor speeds / (rad/s)"], 20).move_to([X0 + 0.75, Y0 + H + 0.45, 0]))
        names = VGroup(*[MathTex(r"\dot\theta_%d" % (k + 1), font_size=28, color=cols[k]).move_to([X0 + 0.7 * k, Y0 - H - 0.35, 0]) for k in range(3)])
        self.add(frame_, names)

        def bars():
            _, w = state(t.get_value())
            g = VGroup()
            for k in range(3):
                hgt = H * w[k] / WMAX
                r = Rectangle(width=0.4, height=max(abs(hgt), 0.01), color=cols[k], fill_opacity=0.85, stroke_width=0)
                r.move_to([X0 + 0.7 * k, Y0 + hgt / 2, 0])
                g.add(r)
            return g

        self.add(always_redraw(bars))
        slow = 40.0
        self.caption("红线：上升 25 mm、平移 305 mm、下降 25 mm，再原路返回", "Red: up 25 mm, across 305 mm, down 25 mm, then back", wait=1.0)
        self.caption("每段都按电机允许的最大匀速走（放慢 40 倍）", "Each leg runs at the fastest constant speed the motors allow (40 times slower)", wait=0)
        self.play(t.animate.set_value(T_HALF), run_time=T_HALF * slow, rate_func=linear)
        self.caption("最吃力的那一点上，总有一台电机到达 10.47 rad/s", "At the hardest point of each leg one motor reaches 10.47 rad/s", wait=0)
        self.play(t.animate.set_value(2 * T_HALF), run_time=T_HALF * slow, rate_func=linear)
        self.caption("真实的一次往返约 0.27 s；加上加速、减速，还要更长", "In reality one round trip takes about 0.27 s, more once accelerations count", wait=1.5)
        self.card([["Delta 的速度关系", "Velocity relation of the Delta"],
                   MathTex(r"u_k^{\mathsf T}\,v = \Big(u_k\cdot\frac{\partial E_k}{\partial\theta_k}\Big)\dot\theta_k ,\qquad v = J\dot\theta", font_size=40),
                   ["沿方向 d 的最大速度 = ω_max / ‖J⁻¹d‖∞", "Top speed along d = ω_max / ‖J⁻¹d‖∞"]])
