"""动画 14.5.1（配图 14.5.1）：UR5e 的 8 组逆解（算例 14.5.1，目标位姿 = 算例 12.3.1 的末端位姿）。
8 组关节角由程序 14.5.1（_ik.ur_ik，次序与表 14.5.1 相同）算出，这里取 6 位小数；正运动学按表 12.1.1 的旋量轴计算。
依次显示 8 组解，相邻两组之间淡入淡出：法兰盘中心与法线（红色箭头）在每一组中都相同。"""
from manim import *
from wq_anim import *
import numpy as np
import math

H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
YD = np.array([0, -1.0, 0])
AXW = [np.array([0, 0, 1.0]), YD, YD, YD, np.array([0, 0, -1.0]), YD]
AXQ = [np.array([0, 0, H1]), np.array([0, -W1, H1]), np.array([-L1, -W1 + W2, H1]), np.array([-L1 - L2, -W1 + W2, H1]),
       np.array([-L1 - L2, -W1 + W2 - W3, H1]), np.array([-L1 - L2, -W1 + W2 - W3, H1 - H2])]
SOLS = [
    ([0.523599, -0.546745, 0.671818, 1.445724, 1.570796, -2.356194], "A", "up", True),
    ([0.523599, 0.096870, -0.671818, 2.145744, 1.570796, -2.356194], "A", "down", True),
    ([0.523599, -1.047198, 1.570796, -2.094395, -1.570796, 0.785398], "A", "up", False),
    ([0.523599, 0.442859, -1.570796, -0.442859, -1.570796, 0.785398], "A", "down", False),
    ([-2.212585, -2.094395, -1.570796, -1.047198, 1.570796, 1.190807], "B", "up", True),
    ([-2.212585, 2.698733, 1.570796, -2.698733, 1.570796, 1.190807], "B", "down", True),
    ([-2.212585, -2.594847, -0.671818, 1.695869, -1.570796, -1.950786], "B", "up", False),
    ([-2.212585, 3.044723, 0.671818, 0.995848, -1.570796, -1.950786], "B", "down", False),
]
ORG = np.array([1.5, -0.4, 0.0])
SC = 4.0


def rot(w, t):
    K = np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def chain(th):
    """连杆折线：基座、关节 1–6 的中心与转折点、法兰中心；以及法兰法线（末端 y 轴）。"""
    Ts = [(np.eye(3), np.zeros(3))]
    R, p = np.eye(3), np.zeros(3)
    for w, q, t in zip(AXW, AXQ, th):
        Ri = rot(w, t)
        p = p + R @ (q - Ri @ q)
        R = R @ Ri
        Ts.append((R.copy(), p.copy()))

    def at(k, x):
        return Ts[k][0] @ x + Ts[k][1]

    q = AXQ
    pts = [np.zeros(3), q[0], at(1, q[1]), at(2, q[1] + np.array([-L1, 0, 0])), at(2, q[2]), at(3, q[3]),
           at(4, q[4]), at(5, q[5]), at(6, q[5] + W4 * YD)]
    return pts, Ts[6][0] @ np.array([0, -1.0, 0])


VAZ, VEL = math.radians(-50), math.radians(18)        # 观察方向：方位角、仰角（正交投影）


def P3(v):
    x, y, z = (float(t) for t in v)
    sx = -math.sin(VAZ) * x + math.cos(VAZ) * y
    sy = z * math.cos(VEL) - (math.cos(VAZ) * x + math.sin(VAZ) * y) * math.sin(VEL)
    return ORG + SC * np.array([sx, sy, 0.0])


def robot(k, col):
    pts, n = chain(SOLS[k][0])
    s = [P3(x) for x in pts]
    g = VGroup()
    widths = [12, 12, 11, 11, 9, 8, 7, 6]
    for i in range(len(s) - 1):
        g.add(Line(s[i], s[i + 1], color=col if i >= 2 else GREY_B, stroke_width=widths[min(i, 7)]))
    for x in s[1:-1]:
        g.add(Dot(x, radius=0.05, color=WHITE))
    return g


def tag(k):
    _, sh, el, nf = SOLS[k]
    zh_t = f"解 {k + 1}：肩 {sh} · 肘{'上' if el == 'up' else '下'} · 腕{'不翻' if nf else '翻'}"
    en_t = f"solution {k + 1}: shoulder {sh} · elbow {el} · wrist {'no flip' if nf else 'flip'}"
    deg = ", ".join(f"{math.degrees(v):.1f}" for v in SOLS[k][0])
    return VGroup(zh(zh_t, 26, YELLOW), en(en_t, 20), MathTex(r"\theta = (" + deg + r")^\circ", font_size=26)
                  ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).to_corner(UR, buff=0.5).shift(DOWN * 0.9)


class Lesson(Base):
    def construct(self):
        self.title("14.5", "UR5e：一个位姿，八种手臂", "UR5e: one pose, eight arms")
        floor = Polygon(P3([-0.7, -0.7, 0]), P3([0.7, -0.7, 0]), P3([0.7, 0.7, 0]), P3([-0.7, 0.7, 0]),
                        color=GREY_D, fill_color=GREY_E, fill_opacity=0.3, stroke_width=1)
        pts, n = chain(SOLS[0][0])
        f = pts[-1]
        flange = VGroup(Dot(P3(f), radius=0.09, color=RED),
                        Arrow(P3(f), P3(f + 0.15 * n), buff=0, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.3))
        self.play(FadeIn(floor), FadeIn(flange))
        cols = [BLUE, BLUE, BLUE, BLUE, ORANGE, ORANGE, ORANGE, ORANGE]
        cur = robot(0, cols[0])
        tg = tag(0)
        self.play(Create(cur), FadeIn(tg))
        self.caption("法兰盘的位置和法线（红点、红箭头）给定，手臂有 8 种摆法",
                     "Flange position and normal (red) are given; the arm can take eight shapes", wait=0.8)
        notes = {1: ("肘上 → 肘下：子问题 3 的两个解", "Elbow up → down: the two roots of Subproblem 3"),
                 2: ("手腕翻转：θ₅ 变号，θ₆ 差 180°", "Wrist flip: θ₅ changes sign, θ₆ moves by 180°"),
                 4: ("肩 B：手臂转到基座另一侧", "Shoulder B: the arm swings to the other side of the base")}
        for k in range(1, 8):
            nxt = robot(k, cols[k])
            nt = tag(k)
            if k in notes:
                self.caption(*notes[k], wait=0)
            self.play(FadeOut(cur), FadeIn(nxt), FadeOut(tg), FadeIn(nt), run_time=1.2)
            self.add(flange)
            self.wait(1.1)
            cur, tg = nxt, nt
        self.caption("8 组解 = 肩、肘、腕三处“二选一”的全部组合", "Eight = every combination of three two-way choices", wait=1.2)
        self.card([["UR5e：三步求出至多 8 组解", "UR5e: three steps, at most eight solutions"],
                   MathTex(r"\theta_1 \to (\theta_5,\theta_6) \to (\theta_3,\theta_2,\theta_4)", font_size=40),
                   ["每一步两个分支：肩、腕、肘", "Two branches at each step: shoulder, wrist, elbow"]])
