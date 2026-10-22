"""动画 25.1.1（配图 25.1.1）：牛顿-欧拉递推的两遍，以竖直平面内的三连杆臂为例（尺寸、质量都是示意值）。
连杆长 0.50、0.40、0.25 m，质量 5、3、1.5 kg（均匀杆，质心在中点，对质心的转动惯量 mL²/12）；
此刻 θ = (40°, −60°, −30°)，θ̇ = (1.0, 1.5, 2.0) rad/s，θ̈ = (2.0, −1.0, 3.0) rad/s²。
前向：从基座出发，每过一个关节，角速度加上 θ̇_i，关节点的速度、加速度按 10.7 节的速度、加速度传递公式算出（基座以 𝔤 向上加速，代替重力）。
反向：从末端出发，每个连杆的合力 = m a_c（含 𝔤），关节 i 传来的力 = 关节 i+1 传来的力 + 本连杆的 m a_c；关节力矩由力矩平衡逐个算出。
画面右侧的数是这样逐个算出的关节力矩，它们与把 9 个方程联立求解的结果相同。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
L = [0.50, 0.40, 0.25]
M = [5.0, 3.0, 1.5]
TH = np.radians([40.0, -60.0, -30.0])
THD = np.array([1.0, 1.5, 2.0])
THDD = np.array([2.0, -1.0, 3.0])
SC = 4.6                                  # 1 m 画成 4.6 个单位
BASE = np.array([-5.4, -2.2, 0])
VS = 0.6                                  # 速度箭头：1 m/s 画成 0.9 个单位
FS = 0.012                                # 力箭头：1 N 画成 0.012 个单位


def kz(r):
    return np.array([-r[1], r[0]])


def recursion():
    """平面三连杆的牛顿-欧拉递推：返回关节点、质心、速度、加速度、关节力、关节力矩。"""
    phi = np.cumsum(TH)
    w = np.cumsum(THD)
    a = np.cumsum(THDD)
    p = [np.zeros(2)]
    v = [np.zeros(2)]
    acc = [np.array([0.0, G])]           # 基座以 𝔤 向上加速
    c, vc, ac = [], [], []
    for i in range(3):
        r = L[i] * np.array([math.cos(phi[i]), math.sin(phi[i])])
        rc = r / 2
        c.append(p[i] + rc)
        vc.append(v[i] + w[i] * kz(rc))
        ac.append(acc[i] + a[i] * kz(rc) - w[i] ** 2 * rc)
        p.append(p[i] + r)
        v.append(v[i] + w[i] * kz(r))
        acc.append(acc[i] + a[i] * kz(r) - w[i] ** 2 * r)
    f = [None] * 4
    n = [None] * 4
    f[3], n[3] = np.zeros(2), 0.0
    for i in reversed(range(3)):
        I = M[i] * L[i] ** 2 / 12
        f[i] = f[i + 1] + M[i] * ac[i]
        r_next = p[i + 1] - p[i]
        rc = c[i] - p[i]
        n[i] = n[i + 1] + (r_next[0] * f[i + 1][1] - r_next[1] * f[i + 1][0]) + M[i] * (rc[0] * ac[i][1] - rc[1] * ac[i][0]) + I * a[i]
    return p, c, v, acc, f, n


P, Cm, V, ACC, F, N = recursion()


def S(x):
    return BASE + SC * np.array([x[0], x[1], 0])


class Lesson(Base):
    def construct(self):
        self.title("25.1", "牛顿-欧拉递推：先向外传运动，再向里传力", "Recursive Newton–Euler: motion outward, then forces inward")
        self.add(Line(BASE + LEFT * 0.7 + DOWN * 0.12, BASE + RIGHT * 0.7 + DOWN * 0.12, color=GREY_B, stroke_width=4))
        cols = [STEEL, "#d29922", GREEN_C]
        links = VGroup(*[Line(S(P[i]), S(P[i + 1]), color=cols[i], stroke_width=16 - 3 * i) for i in range(3)])
        joints = VGroup(*[Dot(S(P[i]), radius=0.11, color=WHITE) for i in range(3)])
        self.play(Create(links), FadeIn(joints), run_time=1.2)
        for i in range(3):
            mid = (S(P[i]) + S(P[i + 1])) / 2
            d = S(P[i + 1]) - S(P[i])
            nrm = np.array([d[1], -d[0], 0]) / np.linalg.norm(d)
            self.add(zh(f"连杆 {i + 1}", 18, cols[i]).move_to(mid + 0.42 * nrm))
        # 右侧的表
        tab_o = np.array([2.2, 2.0, 0])
        self.add(bi(["此刻（示意值）", "at this instant (illustrative)"], 18, MUTED).move_to(tab_o + RIGHT * 1.8 + UP * 0.25))
        rows = [r"\theta = (40^\circ, -60^\circ, -30^\circ)", r"\dot\theta = (1.0,\ 1.5,\ 2.0)\ \mathrm{rad/s}",
                r"\ddot\theta = (2.0,\ -1.0,\ 3.0)\ \mathrm{rad/s^2}"]
        for k, r in enumerate(rows):
            self.add(MathTex(r, font_size=26, color=INK).move_to(tab_o + RIGHT * 1.8 + DOWN * (0.25 + 0.45 * k)))
        # ---------------- 前向
        self.caption("第一遍（前向）：从基座出发，每过一个关节，加上这个关节自己的转动",
                     "Pass 1 (forward): start at the base and add each joint's own motion as you go out", wait=0.5)
        prev = None
        for i in range(3):
            hl = links[i].copy().set_stroke(YELLOW, width=20, opacity=0.45)
            self.play(FadeIn(hl), run_time=0.4)
            v = V[i + 1]
            arr = Arrow(S(P[i + 1]), S(P[i + 1]) + VS * np.array([v[0], v[1], 0]), buff=0, color=C_V, stroke_width=5,
                        max_tip_length_to_length_ratio=0.2)
            lab = MathTex(r"v_{%d}" % (i + 2) if i < 2 else r"v_{\mathrm{tip}}", font_size=26, color=C_V).next_to(arr.get_end(), UP, buff=0.05)
            wtxt = MathTex(r"\omega_{%d} = %.1f\ \mathrm{rad/s}" % (i + 1, np.cumsum(THD)[i]), font_size=24, color=INK)
            wtxt.move_to(np.array([2.2 + 1.8, -0.45 - 0.42 * i, 0]))
            anims = [GrowArrow(arr), FadeIn(lab), FadeIn(wtxt)]
            if prev is not None:
                anims.append(FadeOut(prev))
            self.play(*anims, run_time=0.8)
            prev = hl
            self.wait(0.3)
        self.play(FadeOut(prev), run_time=0.3)
        self.caption("角速度一级级相加；关节点的速度 = 上一个关节点的速度 + ω × r（10.7 节）；加速度同样一级级算出",
                     "Angular rates add up link by link; each joint point's velocity = previous one + ω × r; accelerations likewise", wait=2.0)
        # ---------------- 反向
        self.caption("第二遍（反向）：从末端出发，每个连杆的 m·a（含重力）加到传过来的力上",
                     "Pass 2 (backward): from the tip inward, add each link's m·a (gravity included) to the force passed in", wait=0.5)
        tq = []
        for i in reversed(range(3)):
            hl = links[i].copy().set_stroke(RED, width=20, opacity=0.45)
            f = F[i]
            arr = Arrow(S(P[i]), S(P[i]) + FS * np.array([f[0], f[1], 0]) * SC / 3.6, buff=0, color=C_F, stroke_width=6,
                        max_tip_length_to_length_ratio=0.15)
            lab = MathTex(r"f_{%d} = %.0f\ \mathrm{N}" % (i + 1, np.linalg.norm(f)), font_size=24, color=C_F)
            lab.next_to(arr.get_end(), LEFT, buff=0.08)
            t = MathTex(r"\tau_{%d} = %.1f\ \mathrm{N\cdot m}" % (i + 1, N[i]), font_size=28, color=YELLOW)
            t.move_to(np.array([4.0, -0.45 - 0.42 * (2 - i), 0]) + RIGHT * 0.0 + DOWN * 1.4)
            self.play(FadeIn(hl), GrowArrow(arr), FadeIn(lab), run_time=0.8)
            self.play(Write(t), run_time=0.6)
            self.play(FadeOut(hl), run_time=0.3)
            tq.append(t)
        self.caption("关节 1 要扛住整条手臂：力和力矩从末端一级级累加回来，关节力矩依次得出",
                     "Joint 1 carries the whole arm: forces and moments accumulate from the tip, giving each joint torque in turn", wait=2.0)
        self.caption("不必把 3 个连杆的 9 个方程联立求解：每个连杆只用一次，计算量与连杆数成正比",
                     "No need to solve all 9 equations together: each link is used once, so the work grows in proportion to the number of links", wait=2.5)
        self.card([["牛顿-欧拉递推", "Recursive Newton–Euler"],
                   MathTex(r"\mathcal V_i = [\mathrm{Ad}_{T_{i,i-1}}]\mathcal V_{i-1} + \mathcal A_i\dot\theta_i", font_size=40),
                   MathTex(r"\mathcal F_i = [\mathrm{Ad}_{T_{i+1,i}}]^{\mathsf T}\mathcal F_{i+1} + \mathcal G_i\dot{\mathcal V}_i - [\mathrm{ad}_{\mathcal V_i}]^{\mathsf T}\mathcal G_i\mathcal V_i", font_size=36),
                   MathTex(r"\tau_i = \mathcal A_i^{\mathsf T}\mathcal F_i", font_size=40),
                   ["前向传运动，反向传力；重力用“基座向上加速 𝔤”代替", "Motion outward, forces inward; gravity as the base accelerating upward at g"]])
