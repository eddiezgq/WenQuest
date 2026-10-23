"""动画 26.1.1（配图 26.1.1）：用广义动量检测碰撞（算例 26.1.1 的平面示意版；尺寸、质量都是示意值）。
竖直平面内的两连杆臂：a₁ = a₂ = 0.5 m，m₁ = 4 kg、m₂ = 3 kg（均匀杆），关节由 PD 加前馈跟踪 φ₁ = 0.6 + 0.5 sin t、φ₂ = 0.8 + 0.6 sin 1.5t。
t = 2.0～2.3 s 末端撞上一个障碍物，受到 10 N 的水平力。观测器 ṙ = K_O(τ_ext − r)，K_O = 30 s⁻¹，只用 θ、θ̇ 和电机力矩，
利用 Ṁ = C + Cᵀ 算出 Cᵀθ̇，不需要角加速度。上：模型准确；下：模型里的 m₂ 少了 20%，碰撞前残差就有约 2 N·m，而且随动作变化，阈值不好定。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
A1, A2, M1, M2 = 0.5, 0.5, 4.0, 3.0
DT = 0.002
TE = 4.0
KO = 30.0
F = 10.0


def dyn(m2, q, v):
    r1, r2 = A1 / 2, A2 / 2
    I1, I2 = M1 * A1 ** 2 / 12, m2 * A2 ** 2 / 12
    c2, s2 = math.cos(q[1]), math.sin(q[1])
    M = np.array([[I1 + I2 + M1 * r1 ** 2 + m2 * (A1 ** 2 + r2 ** 2 + 2 * A1 * r2 * c2), I2 + m2 * (r2 ** 2 + A1 * r2 * c2)],
                  [I2 + m2 * (r2 ** 2 + A1 * r2 * c2), I2 + m2 * r2 ** 2]])
    h = m2 * A1 * r2 * s2
    c = np.array([-h * (2 * v[0] * v[1] + v[1] ** 2), h * v[0] ** 2])
    CTv = np.array([0.0, -h * v[0] * (v[0] + v[1])])
    g12 = math.cos(q[0] + q[1])
    g = np.array([(M1 * r1 + m2 * A1) * G * math.cos(q[0]) + m2 * r2 * G * g12, m2 * r2 * G * g12])
    return M, c, g, CTv


def ref(t):
    return (np.array([0.6 + 0.5 * math.sin(t), 0.8 + 0.6 * math.sin(1.5 * t)]),
            np.array([0.5 * math.cos(t), 0.9 * math.cos(1.5 * t)]),
            np.array([-0.5 * math.sin(t), -1.35 * math.sin(1.5 * t)]))


def simulate():
    q, v = ref(0)[0].copy(), ref(0)[1].copy()
    out = []
    for k in range(int(TE / DT)):
        t = k * DT
        qr, vr, ar = ref(t)
        M, c, g, _ = dyn(M2, q, v)
        tau = M @ ar + c + g + 400 * (qr - q) + 40 * (vr - v)
        J = np.array([[-A1 * math.sin(q[0]) - A2 * math.sin(q[0] + q[1]), -A2 * math.sin(q[0] + q[1])],
                      [A1 * math.cos(q[0]) + A2 * math.cos(q[0] + q[1]), A2 * math.cos(q[0] + q[1])]])
        ext = J.T @ np.array([-F, 0.0]) if 2.0 <= t < 2.3 else np.zeros(2)
        out.append((t, q.copy(), v.copy(), tau.copy(), ext.copy()))
        acc = np.linalg.solve(M, tau + ext - c - g)
        v = v + acc * DT
        q = q + v * DT
    return out


DATA = simulate()


def observer(m2):
    integ, p0, R = np.zeros(2), None, []
    for t, q, v, tau, ext in DATA:
        M, c, g, CTv = dyn(m2, q, v)
        p = M @ v
        if p0 is None:
            p0 = p.copy()
        r = KO * (p - p0 - integ)
        integ = integ + (tau + CTv - g + r) * DT
        R.append(r[0])
    return np.array(R)


R_OK, R_BAD = observer(M2), observer(0.8 * M2)
EXT = np.array([d[4][0] for d in DATA])
TS = np.array([d[0] for d in DATA])


class Lesson(Base):
    def construct(self):
        self.title("26.1", "用广义动量检测碰撞", "Detecting collisions with the generalized momentum")
        base = np.array([-4.8, -1.2, 0])
        S = 2.6
        self.add(Line(base + LEFT * 0.5, base + RIGHT * 0.5, color=GREY_B, stroke_width=4))
        # 两个曲线框
        boxes = [np.array([2.2, 1.1, 0]), np.array([2.2, -1.4, 0])]
        BW, BH = 6.6, 1.9
        heads = [["模型准确：关节 1 的残差 r₁", "accurate model: joint 1 residual r₁"], ["模型里 m₂ 少 20%", "model with m₂ 20% too small"]]
        ysc = BH / 2 / 12.0
        for b, hd in zip(boxes, heads):
            self.add(Rectangle(width=BW, height=BH, color=GREY_B, stroke_width=1).move_to(b))
            self.add(Line(b + LEFT * BW / 2, b + RIGHT * BW / 2, color=GREY_D, stroke_width=1))
            self.add(bi(hd, 16, INK).move_to(b + UP * (BH / 2 + 0.25)))
            x0, x1 = b[0] - BW / 2 + 2.0 / TE * BW, b[0] - BW / 2 + 2.3 / TE * BW
            self.add(Rectangle(width=x1 - x0, height=BH, stroke_width=0, fill_color=ORANGE, fill_opacity=0.18).move_to([(x0 + x1) / 2, b[1], 0]))
        tk = ValueTracker(0)

        def scene():
            k = int(tk.get_value())
            t, q, v, tau, ext = DATA[k]
            g = VGroup()
            p1 = base + S * A1 * np.array([math.cos(q[0]), math.sin(q[0]), 0])
            p2 = p1 + S * A2 * np.array([math.cos(q[0] + q[1]), math.sin(q[0] + q[1]), 0])
            g.add(Line(base, p1, color=STEEL, stroke_width=12), Line(p1, p2, color="#d29922", stroke_width=9))
            g.add(Dot(base, radius=0.1, color=WHITE), Dot(p1, radius=0.09, color=WHITE))
            if 2.0 <= t < 2.3:
                g.add(Arrow(p2 + RIGHT * 0.9, p2, buff=0, color=RED, stroke_width=6), zh("10 N", 18, RED).next_to(p2 + RIGHT * 0.9, UP, buff=0.05))
            for b, R in zip(boxes, (R_OK, R_BAD)):
                n = max(k, 2)
                idx = np.arange(0, n, 10)
                pts = [[b[0] - BW / 2 + TS[i] / TE * BW, b[1] + np.clip(R[i], -12, 12) * ysc, 0] for i in idx]
                ex = [[b[0] - BW / 2 + TS[i] / TE * BW, b[1] + np.clip(EXT[i], -12, 12) * ysc, 0] for i in idx]
                if len(pts) > 1:
                    g.add(VMobject(color=GREY_B, stroke_width=2).set_points_as_corners(ex))
                    g.add(VMobject(color=RED, stroke_width=3).set_points_as_corners(pts))
            g.add(zh(f"t = {t:.2f} s", 20, INK).move_to([-4.6, 2.3, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("手臂按计划运动，t = 2.0～2.3 s 末端撞上障碍物（灰线是真实的外力矩，红线是观测器的残差）",
                     "The arm follows its plan; from t = 2.0 to 2.3 s the tip hits an obstacle (grey: true external torque, red: observer residual)", wait=0)
        self.play(tk.animate.set_value(len(DATA) - 1), run_time=8, rate_func=linear)
        self.wait(0.5)
        self.caption("模型准确时，残差平时为零，撞上就跳起来；模型错了，残差平时就不为零，阈值不好定",
                     "With an accurate model the residual is zero until the hit; with a wrong model it wanders all the time and a threshold is hard to set", wait=2.5)
        self.card([["广义动量观测器", "Generalized-momentum observer"],
                   MathTex(r"\dot p = \tau + C^{\mathsf T}\dot\theta - g + \tau_{\mathrm{ext}},\qquad \dot M = C + C^{\mathsf T}", font_size=40),
                   MathTex(r"\dot r = K_O(\tau_{\mathrm{ext}} - r)", font_size=40),
                   ["不要角加速度；灵敏度取决于模型准不准——所以要辨识", "No accelerations needed; sensitivity depends on the model, hence identification"]])
