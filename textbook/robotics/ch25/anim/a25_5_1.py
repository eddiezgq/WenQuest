"""动画 25.5.1（配图 25.5.1、25.5.2）：UR5e 做第 22 章的上下料动作（A → B，五次多项式），法兰上是夹爪 + 毛坯。
每一瞬用牛顿-欧拉递推（算法 25.2.1）算出六个关节的力矩，画成“力矩 / 上限”的柱（关节 1～3 上限 150 N·m，关节 4～6 上限 28 N·m）。
模型参数抄自书中的 UR5e 模型（MuJoCo Menagerie，与程序 25.2.1 相同）：各连杆的位置、姿态、质量、质心、主惯量，转子等效惯量 0.1 kg·m²。
θ_A = (98.1725°, −86.0425°, 114.5326°, −118.4901°, −90°, 8.1725°)，θ_B = (201.5997°, −50.543°, 79.7267°, −29.1837°, −68.4003°, 0)（算例 22.1.1）。
三种情形：(1) 负载 3.8 kg（夹爪 1 kg + 毛坯），T = 1.318 s（第 22 章的最短时间）；(2) 负载按质量放大到 10 kg；
(3) 负载 5 kg、T = 0.6 s（关节速度已超过上限，只作“假如”）。负载的质心在法兰外 0.161 m，主惯量按质量等比放大。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
ARM = 0.1
LIM = np.array([150.0, 150, 150, 28, 28, 28])
# 书中 UR5e 模型的连杆：(pos, quat, axis, mass, ipos, iquat, diag)；基座 quat = (0, 0, 0, −1)
BASE_Q = (0, 0, 0, -1)
LINKS = [
    ((0, 0, 0.163), (1, 0, 0, 0), (0, 0, 1), 3.7, (0, 0, 0), (1, 0, 0, 0), (0.0102675, 0.0102675, 0.00666)),
    ((0, 0.138, 0), (1, 0, 1, 0), (0, 1, 0), 8.393, (0, 0, 0.2125), (1, 0, 0, 0), (0.133886, 0.133886, 0.0151074)),
    ((0, -0.131, 0.425), (1, 0, 0, 0), (0, 1, 0), 2.275, (0, 0, 0.196), (1, 0, 0, 0), (0.0311796, 0.0311796, 0.004095)),
    ((0, 0, 0.392), (1, 0, 1, 0), (0, 1, 0), 1.219, (0, 0.127, 0), (1, 0, 0, 0), (0.0025599, 0.0025599, 0.0021942)),
    ((0, 0.127, 0), (1, 0, 0, 0), (0, 0, 1), 1.219, (0, 0, 0.1), (1, 0, 0, 0), (0.0025599, 0.0025599, 0.0021942)),
    ((0, 0, 0.1), (1, 0, 0, 0), (0, 1, 0), 0.1889, (0, 0.0771683, 0), (1, 0, 0, 1), (0.000132134, 9.90863e-05, 9.90863e-05)),
]
PL_C = 0.1 + 0.16114                      # 负载质心在连杆 6 坐标系中的 y
PL_I = np.array([0.0260338, 0.0017083, 0.0262671]) / 3.8   # 每千克的主惯量
THA = np.radians([98.1725, -86.0425, 114.5326, -118.4901, -90.0, 8.1725])
THB = np.radians([201.5997, -50.543, 79.7267, -29.1837, -68.4003, 0.0])


def qR(q):
    w, x, y, z = np.array(q, float) / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def sk(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def rot(w, t):
    K = sk(w)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def Ad(R, p):
    A = np.zeros((6, 6))
    A[:3, :3] = R
    A[3:, 3:] = R
    A[3:, :3] = sk(p) @ R
    return A


def adm(V):
    A = np.zeros((6, 6))
    A[:3, :3] = sk(V[:3])
    A[3:, 3:] = sk(V[:3])
    A[3:, :3] = sk(V[3:])
    return A


def Gmat(m, c, Ic):
    P = sk(c)
    G = np.zeros((6, 6))
    G[:3, :3] = Ic - m * P @ P
    G[:3, 3:] = m * P
    G[3:, :3] = -m * P
    G[3:, 3:] = m * np.eye(3)
    return G


# 连杆坐标系：零位时 {i} 在 {i−1} 中的位姿
REL = []
for k, (pos, quat, ax, m, ip, iq, dg) in enumerate(LINKS):
    R = qR(quat)
    if k == 0:
        R = qR(BASE_Q) @ R
        pos = qR(BASE_Q) @ np.array(pos, float)
    REL.append((R, np.array(pos, float)))
AX = [np.array(L[2], float) for L in LINKS]
GS = [Gmat(L[3], np.array(L[4], float), qR(L[5]) @ np.diag(L[6]) @ qR(L[5]).T) for L in LINKS]


def rnea(th, thd, thdd, m_pl):
    G6 = GS[5] + Gmat(m_pl, np.array([0, PL_C, 0]), np.diag(PL_I * m_pl))
    Gs = GS[:5] + [G6]
    V, Vd = np.zeros(6), np.array([0, 0, 0, 0, 0, G])
    Ts, Vs, Vds = [], [], []
    for i in range(6):
        Rp, pp = REL[i]                               # {i} 在 {i−1} 中（零位）
        Rj = rot(AX[i], th[i])
        R_ip = (Rp @ Rj).T                            # T_{i,i−1} 的转动
        p_ip = -R_ip @ pp
        A = np.r_[AX[i], 0, 0, 0]
        AdT = Ad(R_ip, p_ip)
        V = AdT @ V + A * thd[i]
        Vd = AdT @ Vd + adm(V) @ A * thd[i] + A * thdd[i]
        Ts.append(AdT)
        Vs.append(V)
        Vds.append(Vd)
    F = np.zeros(6)
    tau = np.zeros(6)
    for i in reversed(range(6)):
        if i < 5:
            F = Ts[i + 1].T @ F
        F = F + Gs[i] @ Vds[i] - adm(Vs[i]).T @ Gs[i] @ Vs[i]
        tau[i] = F[:3] @ AX[i] + ARM * thdd[i]
    return tau


def points(th):
    """各关节原点、法兰、负载质心在世界坐标系中的位置。"""
    R, p = np.eye(3), np.zeros(3)
    pts = []
    for i in range(6):
        Rp, pp = REL[i]
        p = p + R @ pp
        R = R @ Rp @ rot(AX[i], th[i])
        pts.append(p.copy())
    pts.append(p + R @ np.array([0, 0.1, 0]))
    pts.append(p + R @ np.array([0, PL_C + 0.09, 0]))
    return pts


def quintic(T, t):
    u = min(max(t / T, 0.0), 1.0)
    s = 10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5
    sd = (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / T
    sdd = (60 * u - 180 * u ** 2 + 120 * u ** 3) / T ** 2
    d = THB - THA
    return THA + s * d, sd * d, sdd * d


CA, SA = math.cos(math.radians(150)), math.sin(math.radians(150))


def view(p):
    """斜视投影：水平方向取动作中段手臂伸出的方向（θ₁ ≈ 150°），纵深方向略向上抬。"""
    x, y, z = p
    u = -CA * x - SA * y                      # 沿手臂伸出的方向
    w = SA * x - CA * y                       # 纵深
    return np.array([-5.6 + 3.8 * (u + 0.25 * w), -2.0 + 3.8 * (z + 0.18 * w), 0])


class Lesson(Base):
    def construct(self):
        self.title("25.5", "UR5e 搬工件：六个关节的力矩", "UR5e carrying a part: torques at the six joints")
        st = {"T": 1.318, "m": 3.8, "peak": np.zeros(6)}
        tk = ValueTracker(0.0)
        o = np.array([1.0, -1.6, 0])
        bw = 0.75
        self.add(Line(o + LEFT * 0.2, o + RIGHT * (6 * bw + 0.1), color=GREY_B, stroke_width=2))
        H = 3.0
        self.add(DashedLine(o + UP * H + LEFT * 0.2, o + UP * H + RIGHT * (6 * bw + 0.1), color=RED_E, stroke_width=2))
        self.add(zh("上限", 16, RED_E).next_to(o + UP * H + RIGHT * (6 * bw + 0.1), RIGHT, buff=0.08))
        for j in range(6):
            self.add(zh(f"关节{j + 1}", 15, INK).move_to(o + RIGHT * (bw * j + bw / 2) + DOWN * 0.25))
            self.add(zh("150" if j < 3 else "28", 13, MUTED).move_to(o + RIGHT * (bw * j + bw / 2) + DOWN * 0.52))
        self.add(zh("N·m", 13, MUTED).move_to(o + RIGHT * (6 * bw + 0.35) + DOWN * 0.52))
        self.add(Line(view([0, 0, 0]) + LEFT * 0.6, view([0, 0, 0]) + RIGHT * 0.6, color=GREY_B, stroke_width=4))

        def scene():
            t = tk.get_value()
            q, qd, qdd = quintic(st["T"], t)
            tau = rnea(q, qd, qdd, st["m"])
            r = np.abs(tau) / LIM
            st["peak"] = np.maximum(st["peak"], r)
            g = VGroup()
            P = [view(p) for p in points(q)]
            chain = [view([0, 0, 0])] + P
            for k in range(len(chain) - 2):
                g.add(Line(chain[k], chain[k + 1], color=STEEL, stroke_width=10 if k < 4 else 7))
            for k in range(1, 7):
                g.add(Dot(chain[k], radius=0.07, color=WHITE))
            g.add(Line(chain[-2], chain[-1], color="#d29922", stroke_width=6 + 1.2 * st["m"]))
            for j in range(6):
                hgt = max(r[j] * H, 0.005)
                col = RED if r[j] > 1 else (YELLOW if r[j] > 0.8 else (BLUE if j < 3 else GREEN))
                g.add(Rectangle(width=bw * 0.62, height=hgt, color=col, fill_color=col, fill_opacity=0.85, stroke_width=0)
                      .move_to(o + RIGHT * (bw * j + bw / 2) + UP * hgt / 2))
                pk = min(st["peak"][j], 1.25) * H
                g.add(Line(o + RIGHT * (bw * j + 0.12) + UP * pk, o + RIGHT * (bw * j + bw - 0.12) + UP * pk, color=WHITE, stroke_width=2))
                g.add(zh(f"{100 * st['peak'][j]:.0f}%", 14, WHITE).move_to(o + RIGHT * (bw * j + bw / 2) + UP * (pk + 0.18)))
            g.add(zh(f"负载 {st['m']:.1f} kg    T = {st['T']:.2f} s    t = {t:.2f} s", 22, INK).move_to([2.9, 2.35, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("负载 3.8 kg，第 22 章的最短时间 1.32 s（放慢 2 倍）：白线是每个关节到目前为止的峰值",
                     "3.8 kg, the shortest time of Chapter 22, 1.32 s (2x slower); white ticks mark each joint's peak so far", wait=0)
        self.play(tk.animate.set_value(1.318), run_time=2.6, rate_func=linear)
        self.caption("关节 2 扛着整条手臂，力矩最大；关节 4 的力矩小，可上限也只有 28 N·m——两者都用了约三分之一",
                     "Joint 2 carries the whole arm and has the largest torque; joint 4's is small but so is its 28 N·m limit; both use about a third", wait=2.2)
        st["m"], st["peak"] = 10.0, np.zeros(6)
        tk.set_value(0.0)
        self.caption("负载加到 10 kg：最先逼近上限的是腕部的关节 4，不是肩",
                     "Raise the payload to 10 kg: the first joint to near its limit is wrist joint 4, not the shoulder", wait=0)
        self.play(tk.animate.set_value(1.318), run_time=2.6, rate_func=linear)
        self.wait(1.2)
        st["m"], st["T"], st["peak"] = 5.0, 0.6, np.zeros(6)
        tk.set_value(0.0)
        self.caption("假如 5 kg 只用 0.6 s（速度其实已超限）：惯性项变为约 4.8 倍，关节 4 超过上限",
                     "What if 5 kg took only 0.6 s (the speed limit is already broken): inertial terms grow about 4.8x and joint 4 exceeds its limit", wait=0)
        self.play(tk.animate.set_value(0.6), run_time=2.4, rate_func=linear)
        self.wait(1.5)
        self.card([["哪个关节先超限", "Which joint hits its limit first"],
                   MathTex(r"\tau(t) = \mathrm{RNEA}\big(\theta(t), \dot\theta(t), \ddot\theta(t)\big)", font_size=38),
                   ["大关节扛重量，小关节的上限低：腕部关节常常先到上限", "Big joints carry the weight, small ones have low limits: a wrist joint often hits its limit first"],
                   ["负载、重心偏移、动作快慢都要一起核算", "Check payload, centre-of-gravity offset and speed together"]])
