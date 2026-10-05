"""动画 17.3.1（配图 17.3.3）：平面 3R 臂（0.425、0.392、0.1 m）的末端固定在 (0.6, 0.2) m，起始形态取工具朝向 −60° 的肘上解（θ₂ < 0）。
半径 0.05 m 的圆形障碍物在 3 s 内从 (0.17, 0.85) m 竖直压到 (0.17, 0.42) m（算例 17.3.3 的平面部分）。
先只用伪逆：手臂不动，被压到；再加入避障次任务（式 (17.3.7)，激活距离 0.10 m，K_d = 3 /s，λ_o = 0.02 m）：
距离降到激活距离时肘部开始让开，末端始终不动。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L = (0.425, 0.392, 0.1)
PT = np.array([0.6, 0.2])
PC0, PC1 = np.array([0.17, 0.85]), np.array([0.17, 0.42])
RAD, D_ACT, K_D, LAM, KP = 0.05, 0.10, 3.0, 0.02, 5.0
SC = 5.4
O = np.array([-4.6, -2.3, 0.0])


def S(p):
    return O + SC * np.array([p[0], p[1], 0.0])


def joints(th):
    pts, a = [np.zeros(2)], 0.0
    for t, l in zip(th, L):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return pts


def jac(th):
    pts = joints(th)
    J = np.zeros((2, 3))
    for i in range(3):
        d = pts[-1] - pts[i]
        J[:, i] = [-d[1], d[0]]
    return J


def seg(p, a, b):
    ab = b - a
    s = float(np.clip((p - a) @ ab / (ab @ ab), 0, 1))
    c = a + s * ab
    return float(np.linalg.norm(p - c)), c


def start():
    phi = math.radians(-60)
    w = PT - L[2] * np.array([math.cos(phi), math.sin(phi)])
    c2 = (w @ w - L[0] ** 2 - L[1] ** 2) / (2 * L[0] * L[1])
    t2 = -math.acos(c2)
    t1 = math.atan2(w[1], w[0]) - math.atan2(L[1] * math.sin(t2), L[0] + L[1] * math.cos(t2))
    return np.array([t1, t2, phi - t1 - t2])


def run(avoid, T_end=4.0, dt=0.004):
    th, rec = start(), []
    for i in range(int(round(T_end / dt)) + 1):
        t = i * dt
        s = (1 - math.cos(math.pi * min(t, 3.0) / 3.0)) / 2
        sd = math.pi / 3.0 * math.sin(math.pi * t / 3.0) / 2 if t < 3.0 else 0.0
        c, cd = PC0 + s * (PC1 - PC0), sd * (PC1 - PC0)
        J = jac(th)
        Jp = J.T @ np.linalg.inv(J @ J.T)
        N = np.eye(3) - Jp @ J
        qd = Jp @ (KP * (PT - joints(th)[-1]))
        pts = joints(th)
        best = min(((seg(c, pts[k], pts[k + 1]) + (k,)) for k in range(3)), key=lambda z: z[0])
        d, x, k = best
        d -= RAD
        if avoid and d < D_ACT:
            u = (x - c) / np.linalg.norm(x - c)
            Jx = np.zeros((2, 3))
            for j in range(k + 1):
                r = x - pts[j]
                Jx[:, j] = [-r[1], r[0]]
            a = u @ Jx
            A1 = a @ N
            qd = qd + A1 / (A1 @ A1 + LAM ** 2) * (u @ cd + K_D * (D_ACT - d) - a @ qd)
        if i % 5 == 0:
            rec.append((th.copy(), c.copy(), d))
        th = th + dt * qd
    return rec


R0, R1 = run(False), run(True)


class Lesson(Base):
    def construct(self):
        self.title("17.3", "避障：末端不动，肘部让开", "Obstacle avoidance: the tip stays, the elbow gives way")
        base = Polygon(O + LEFT * 0.35 + DOWN * 0.25, O + RIGHT * 0.35 + DOWN * 0.25, O + RIGHT * 0.18, O + LEFT * 0.18,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        tgt = Dot(S(PT), radius=0.07, color=RED)
        tl = zh("末端固定", 20, RED).next_to(tgt, DOWN, buff=0.15)
        self.play(FadeIn(base), FadeIn(tgt), FadeIn(tl), run_time=0.6)
        k = ValueTracker(0.0)
        rec = {"R": R0, "col": GREY_B}

        def frame():
            R = rec["R"]
            i = min(int(round(k.get_value())), len(R) - 1)
            th, c, d = R[i]
            pts = [S(p) for p in joints(th)]
            g = VGroup(Line(pts[0], pts[1], color=rec["col"], stroke_width=13), Line(pts[1], pts[2], color=rec["col"], stroke_width=10),
                       Line(pts[2], pts[3], color=rec["col"], stroke_width=7))
            for q in pts[:3]:
                g.add(Dot(q, radius=0.07, color=WHITE))
            hit = d < 0
            g.add(Circle(radius=SC * RAD, color=RED, fill_color=RED if hit else RED_E, fill_opacity=0.85 if hit else 0.55, stroke_width=2).move_to(S(c)))
            g.add(DashedVMobject(Circle(radius=SC * (RAD + D_ACT), color=RED_B, stroke_width=1.5), num_dashes=28).move_to(S(c)))
            g.add(VGroup(zh("距离 d", 24), MathTex(r"= %.3f\ \mathrm m" % d, font_size=30, color=RED if hit else WHITE))
                  .arrange(RIGHT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.9))
            if hit:
                g.add(zh("碰到了！", 26, RED).to_corner(UR, buff=0.6).shift(DOWN * 1.6))
            return g

        fr = always_redraw(frame)
        self.add(fr)
        self.caption("障碍物从上方压下来；虚线圈是激活距离 0.10 m",
                     "An obstacle comes down from above; the dashed ring marks the 0.10 m activation distance", wait=0.6)
        self.caption("只用伪逆：末端的任务已经完成，手臂一动不动，被压到",
                     "Pseudoinverse only: the tip task is done, the arm does not move, and it is hit", wait=0)
        self.play(k.animate.set_value(len(R0) - 1), run_time=5.0, rate_func=linear)
        self.wait(0.6)
        rec["R"], rec["col"] = R1, STEEL
        k.set_value(0)
        elbow = always_redraw(lambda: Dot(S(joints(R1[min(int(round(k.get_value())), len(R1) - 1)][0])[1]), radius=0.05, color=GOLD))
        trail = TracedPath(elbow.get_center, stroke_color=GOLD, stroke_width=3)
        self.add(trail, elbow)
        self.caption("加入避障次任务：距离一到激活距离，肘部就在零空间里让开",
                     "With the avoidance subtask: once inside the activation distance the elbow moves away in the null space", wait=0)
        self.play(k.animate.set_value(len(R1) - 1), run_time=7.0, rate_func=linear)
        dmin = min(r[2] for r in R1)
        self.caption(f"最小距离 {dmin:.3f} m，末端始终在原处",
                     f"Minimum distance {dmin:.3f} m; the tip never moved", wait=1.5)
        self.card([["避障作为次要任务", "Obstacle avoidance as a secondary task"],
                   MathTex(r"\dot d = a\,\dot\theta - u^{\mathsf T}\dot o,\qquad a = u^{\mathsf T}J_y", font_size=36),
                   MathTex(r"\dot\theta = \dot\theta_1 + \frac{(aN)^{\mathsf T}}{(aN)(aN)^{\mathsf T} + \lambda_o^2}\big(u^{\mathsf T}\dot o + K_d(d_a - d) - a\dot\theta_1\big)", font_size=32),
                   ["次要任务只在主任务的零空间里起作用", "The secondary task acts only in the null space of the primary one"]])
