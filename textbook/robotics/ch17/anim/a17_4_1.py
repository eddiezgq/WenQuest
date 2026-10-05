"""动画 17.4.1（配图 17.4.1）：协作工位上的搬运（算例 17.4.1）。Panda（旋量轴见表 12.3.1）的手竖直向下，3 s 内从
A = (0.40, 0.35, 0.30) m 沿直线到 B = (0.40, −0.35, 0.30) m；工人的手（半径 0.06 m 的球）在前 1.8 s 从 (−0.45, 0.35, 0.60) m
伸到 (−0.05, 0.12, 0.60) m。先看做法 S1（离 ready 最近的起始形态、最小范数解）；再看做法 S3：搬运前沿自运动把手臂转到
程序 17.4.1 选出的起始形态（θ₃ ≈ 94.7°，这里由牛顿法精确地拉回 A 点的位姿），再用三层优先级（手 > 离开工人的手 > 避限位）搬运。"""
from manim import *
from wq_anim import *
import numpy as np
import math

W_ = [(0, 0, 1), (0, 1, 0), (0, 0, 1), (0, -1, 0), (0, 0, 1), (0, -1, 0), (0, 0, -1)]
Q_ = [(0, 0, 0.333), (0, 0, 0.333), (0, 0, 0.649), (0.0825, 0, 0.649), (0, 0, 1.033), (0, 0, 1.033), (0.088, 0, 1.033)]
LO = np.array([-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973])
HI = np.array([2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973])
READY = np.array([0, -math.pi / 4, 0, -3 * math.pi / 4, 0, math.pi / 2, math.pi / 4])
FL0 = np.array([0.088, 0, 0.926])
A_, B_ = np.array([0.40, 0.35, 0.30]), np.array([0.40, -0.35, 0.30])
C0, C1, RAD = np.array([-0.45, 0.35, 0.60]), np.array([-0.05, 0.12, 0.60]), 0.06
TT, KP, K_D, LAM, KH, D_ACT = 3.0, 5.0, 3.0, 0.03, 2.0, 0.14
SEGLINK = [0, 3, 3, 4, 4, 6, 7]
Q3_DEG = np.array([-36.7, 77.2, 94.7, -123.6, -76.8, 93.2, 132.0])     # 程序 17.4.1 选出的起始形态（取一位小数，下面再精确拉回）


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def rot(w, t):
    K = skew(w)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def chain(th):
    Es = [np.eye(4)]
    for w, q, t in zip(W_, Q_, th):
        R = rot(np.array(w, float), t)
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = np.array(q, float) - R @ np.array(q, float)
        Es.append(Es[-1] @ T)
    return Es


def axes_now(Es):
    out = []
    for i in range(7):
        out.append((Es[i][:3, :3] @ np.array(W_[i], float), Es[i][:3, :3] @ np.array(Q_[i], float) + Es[i][:3, 3]))
    return out


def flange(Es):
    return Es[7][:3, :3] @ FL0 + Es[7][:3, 3]


def jac_g(th):
    Es = chain(th)
    F = flange(Es)
    J = np.zeros((6, 7))
    for i, (w, q) in enumerate(axes_now(Es)):
        J[:, i] = np.r_[w, np.cross(w, F - q)]
    return J, Es, F


def logR(R):
    c = max(-1.0, min(1.0, (np.trace(R) - 1) / 2))
    a = math.acos(c)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / 2
    return v if a < 1e-9 else a / math.sin(a) * v


R_D = chain(READY)[7][:3, :3]


def err(Es, F, p):
    return np.r_[logR(R_D @ Es[7][:3, :3].T), p - F]


M0 = np.array([[math.sqrt(0.5), math.sqrt(0.5), 0, 0.088], [math.sqrt(0.5), -math.sqrt(0.5), 0, 0], [0, 0, -1, 0.926], [0, 0, 0, 1.0]])


def log_twist(T):
    """SE(3) 的对数（定理 6.4.3）。"""
    R, p = T[:3, :3], T[:3, 3]
    wth = logR(R)
    a = float(np.linalg.norm(wth))
    if a < 1e-12:
        return np.r_[np.zeros(3), p]
    K = skew(wth / a)
    Gi = np.eye(3) / a - 0.5 * K + (1 / a - 0.5 / math.tan(a / 2)) * K @ K
    return np.r_[wth, a * (Gi @ p)]


def ik(p, th):
    """与程序 17.4.1 相同的数值逆解：空间雅可比、误差旋量 log(T_d T⁻¹)、最小范数的牛顿步。"""
    Td = np.eye(4)
    Td[:3, :3] = R_D @ M0[:3, :3]
    Td[:3, 3] = p
    for _ in range(60):
        Es = chain(th)
        e = log_twist(Td @ np.linalg.inv(Es[7] @ M0))
        if np.linalg.norm(e) < 1e-13:
            break
        J = np.array([np.r_[w, -np.cross(w, q)] for w, q in axes_now(Es)]).T
        th = th + J.T @ np.linalg.solve(J @ J.T, e)
    return th


def points(Es):
    act = lambda T, p: T[:3, :3] @ np.array(p, float) + T[:3, 3]
    return [np.zeros(3), np.array([0, 0, 0.333]), act(Es[3], (0, 0, 0.649)), act(Es[3], (0.0825, 0, 0.649)),
            act(Es[4], (0, 0, 0.649)), act(Es[4], (0, 0, 1.033)), act(Es[6], (0.088, 0, 1.033)), act(Es[7], FL0)]


def human(t):
    Th = 0.6 * TT
    if t >= Th:
        return C1.copy(), np.zeros(3)
    s = (1 - math.cos(math.pi * t / Th)) / 2
    return C0 + s * (C1 - C0), math.pi / Th * math.sin(math.pi * t / Th) / 2 * (C1 - C0)


def closest(Es, c):
    P = points(Es)
    best = None
    for i in range(1, 7):
        ab = P[i + 1] - P[i]
        s = float(np.clip((c - P[i]) @ ab / (ab @ ab), 0, 1))
        x = P[i] + s * ab
        d = float(np.linalg.norm(c - x))
        if best is None or d < best[0]:
            best = (d, x, i)
    return best


def run(q0, pri, dt=0.004):
    th, rec = np.array(q0, float), []
    for i in range(int(round(TT / dt)) + 1):
        t = i * dt
        s = (1 - math.cos(math.pi * t / TT)) / 2
        sd = math.pi / TT * math.sin(math.pi * t / TT) / 2
        J, Es, F = jac_g(th)
        V = np.r_[0, 0, 0, sd * (B_ - A_)]
        Jp = J.T @ np.linalg.inv(J @ J.T)
        N = np.eye(7) - Jp @ J
        qd = Jp @ (V + KP * err(Es, F, A_ + s * (B_ - A_)))
        c, cd = human(t)
        d, x, k = closest(Es, c)
        d -= RAD
        if pri:
            N2 = N
            if d < D_ACT:
                u = (x - c) / np.linalg.norm(x - c)
                Jx = np.zeros((3, 7))
                for j, (w, q) in enumerate(axes_now(Es)[:SEGLINK[k]]):
                    Jx[:, j] = np.cross(w, x - q)
                a = u @ Jx
                A1 = a @ N
                G = A1 / (A1 @ A1 + LAM ** 2)
                qd = qd + G * (u @ cd + K_D * (D_ACT - d) - a @ qd)
                N2 = N - np.outer(G, A1)
            mid, rg = (LO + HI) / 2, HI - LO
            qd = qd - N2 @ (KH * 2 * (th - mid) / rg ** 2)
        if i % 6 == 0:
            rec.append((th.copy(), c.copy(), d))
        th = th + dt * qd
    return rec


QA = ik(A_, READY.copy())
Q3 = ik(A_, np.radians(Q3_DEG))
S1, S3 = run(QA, False), run(Q3, True)


def self_motion(q_from, q_to, h=0.03):
    """沿 A 点的自运动从 q_from 走到 q_to：θ3 单调（定理 17.4.1），取使 θ3 增大的方向，每步牛顿校正。"""
    th, out = q_from.copy(), [q_from.copy()]
    for _ in range(400):
        J, Es, F = jac_g(th)
        c = np.array([(-1) ** (i + 8) * np.linalg.det(np.delete(J, i, axis=1)) for i in range(7)])
        c = c / np.linalg.norm(c) * np.sign(c[2])
        if th[2] + h * c[2] >= q_to[2]:
            break
        th = ik(A_, th + h * c)
        out.append(th.copy())
    out.append(q_to.copy())
    return out


MOVE = self_motion(QA, Q3)
AZ, EL, SCL = math.radians(-60), math.radians(25), 4.4
ORG = np.array([-1.2, -2.3, 0.0])
ER = np.array([-math.sin(AZ), math.cos(AZ), 0.0])
EU = np.array([-math.sin(EL) * math.cos(AZ), -math.sin(EL) * math.sin(AZ), math.cos(EL)])


def P3(p):
    p = np.asarray(p, float)
    return ORG + SCL * np.array([p @ ER, p @ EU, 0.0])


class Lesson(Base):
    def construct(self):
        self.title("17.4", "协作搬运：先选好形态，再动手", "Collaborative transfer: choose the posture first, then move")
        floor = Polygon(P3((-0.6, -0.6, 0)), P3((0.6, -0.6, 0)), P3((0.6, 0.6, 0)), P3((-0.6, 0.6, 0)),
                        stroke_width=1, color=GREY_D, fill_color=GREY_E, fill_opacity=0.35)
        ped = Line(P3((0, 0, 0)), P3((0, 0, 0.333)), color=GREY_B, stroke_width=16)
        path = DashedLine(P3(A_), P3(B_), color=WHITE, stroke_width=2)
        la = Text("A", font=LATIN, font_size=24).next_to(P3(A_), DOWN, buff=0.12)
        lb = Text("B", font=LATIN, font_size=24).next_to(P3(B_), DOWN, buff=0.12)
        self.play(FadeIn(floor), FadeIn(ped), Create(path), FadeIn(la), FadeIn(lb), run_time=0.8)
        st = {"seq": [(QA, C0, 1.0)], "col": RED_C, "min": 9.9}
        k = ValueTracker(0.0)

        def scene_now():
            seq = st["seq"]
            i = min(int(round(k.get_value())), len(seq) - 1)
            th, c, d = seq[i]
            if d < 9:
                st["min"] = min(st["min"], d)
            Es = chain(th)
            pts = [P3(p) for p in points(Es)]
            g = VGroup()
            for j in range(1, 7):
                g.add(Line(pts[j], pts[j + 1], color=st["col"], stroke_width=10 if j < 5 else 7))
            for j in (1, 3, 5, 7):
                g.add(Dot(pts[j], radius=0.055, color=WHITE))
            g.add(Dot(pts[3], radius=0.08, color=YELLOW))
            near = d < 0.10
            g.add(Circle(radius=SCL * RAD, color=RED, fill_color=RED, fill_opacity=0.9 if near else 0.55, stroke_width=1).move_to(P3(c)))
            txt = r"d = %.3f\ \mathrm m" % d if d < 9 else r"d = \text{---}"
            mn = r"d_{\min} = %.3f\ \mathrm m" % st["min"] if st["min"] < 9 else r"d_{\min} = \text{---}"
            g.add(VGroup(MathTex(txt, font_size=30, color=RED if near else WHITE), MathTex(mn, font_size=30))
                  .arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.9))
            g.add(zh("工人的手", 20, RED_B).next_to(P3(c), UP, buff=0.35))
            return g

        sc = always_redraw(scene_now)
        self.add(sc)
        self.caption("任务：手竖直向下，从 A 沿直线搬到 B；工人的手从左后方伸进来",
                     "Task: hand pointing down, straight from A to B; a worker reaches in from behind on the left", wait=0.8)
        st["seq"] = S1
        self.caption("S1：从离 ready 最近的形态出发，只用最小范数解",
                     "S1: start from the configuration nearest to ready, minimum-norm solution only", wait=0)
        self.play(k.animate.set_value(len(S1) - 1), run_time=5.0, rate_func=linear)
        self.caption(f"肘部迎着工人的手过去，最近只有 {st['min'] * 100:.1f} cm，不够 10 cm",
                     f"The elbow swings towards the worker: only {st['min'] * 100:.1f} cm at the closest, below 10 cm", wait=1.5)
        st["seq"], st["col"], st["min"] = [(q, C0, 9.5) for q in MOVE], STEEL, 9.9
        k.set_value(0)
        self.caption("S3：搬运之前，手停在 A 不动，沿自运动把肘部转到另一侧",
                     "S3: before the transfer, the hand stays at A while self-motion turns the elbow to the other side", wait=0)
        self.play(k.animate.set_value(len(MOVE) - 1), run_time=4.0, rate_func=smooth)
        st["seq"], st["min"] = S3, 9.9
        k.set_value(0)
        self.caption("再按三层优先级搬运：手的路径完全相同",
                     "Then transfer with three priority levels: exactly the same hand path", wait=0)
        self.play(k.animate.set_value(len(S3) - 1), run_time=5.0, rate_func=linear)
        self.caption(f"全程离工人的手至少 {st['min'] * 100:.1f} cm：好的起点让问题消失",
                     f"At least {st['min'] * 100:.1f} cm from the worker's hand: a good start makes the problem disappear", wait=1.5)
        self.card([["全局挑选 + 局部控制", "Global choice + local control"],
                   ["全局：沿自运动流形挑选起始形态（规划）", "Global: choose the start on the self-motion manifold (planning)"],
                   ["局部：零空间里避障、避限位（控制）", "Local: avoid obstacles and limits in the null space (control)"],
                   MathTex(r"\dot\theta = J^{+}\dot x + G(\cdots) - k_H(N - G\,aN)\nabla H", font_size=34)])
