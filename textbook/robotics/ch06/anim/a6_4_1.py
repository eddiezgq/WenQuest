"""动画 6.4.1（配图 6.4.1）：算例 6.4.2。UR5e 法兰盘从零位（灰）到目标（金）的位移，由对数映射求出螺旋轴；
指数映射 e^{[S]θs}M（s 从 0 到 1）让法兰盘坐标系沿这根轴“拧”到目标，法兰盘中心画出螺旋线。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([0.0, 0.1, 0])
SC = 5.5
H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
AX = [(np.array([0, 0, 1.0]), np.array([0, 0, H1])), (np.array([0, -1.0, 0]), np.array([0, -W1, H1])),
      (np.array([0, -1.0, 0]), np.array([-L1, -W1 + W2, H1])), (np.array([0, -1.0, 0]), np.array([-L1 - L2, -W1 + W2, H1])),
      (np.array([0, 0, -1.0]), np.array([-L1 - L2, -W1 + W2 - W3, H1])), (np.array([0, -1.0, 0]), np.array([-L1 - L2, -W1 + W2 - W3, H1 - H2]))]
M = np.array([[1.0, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
TH = np.radians([30, -45, 60, -15, 90, 30])


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def exp6(S, t):
    w, v = S[:3], S[3:]
    K = skew(w)
    T = np.eye(4)
    T[:3, :3] = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    T[:3, 3] = (np.eye(3) * t + (1 - math.cos(t)) * K + (t - math.sin(t)) * K @ K) @ v
    return T


def log6(T):
    R, p = T[:3, :3], T[:3, 3]
    t = math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2)))
    W = (R - R.T) / (2 * math.sin(t))
    w = np.array([W[2, 1], W[0, 2], W[1, 0]])
    K = skew(w)
    Gi = np.eye(3) / t - K / 2 + (1 / t - 0.5 / math.tan(t / 2)) * K @ K
    return np.r_[w, Gi @ p], t


SL = [np.r_[w, -np.cross(w, q)] for w, q in AX]


def fk(th, upto=6):
    T = np.eye(4)
    for S, t in zip(SL[:upto], th[:upto]):
        T = T @ exp6(S, t)
    return T


def skeleton(th):
    pts = [np.zeros(3)]
    for i, (w, q) in enumerate(AX):
        pts.append((fk(th, i) @ np.r_[q, 1])[:3])
    pts.append((fk(th) @ M)[:3, 3])
    return pts


AZ, EL = math.radians(60), math.radians(22)
CEN = np.array([-0.45, -0.3, 0.25])          # 画面中心对准的点 (m)


def P(x):
    """与图 6.4.1 相同的视角（方位角 60°、仰角 22°）的正投影。"""
    x = np.asarray(x, float) - CEN
    u = -math.sin(AZ) * x[0] + math.cos(AZ) * x[1]
    v = -math.cos(AZ) * math.sin(EL) * x[0] - math.sin(AZ) * math.sin(EL) * x[1] + math.cos(EL) * x[2]
    return O + SC * np.array([u, v, 0])


def arm_lines(th, color, op):
    pts = skeleton(th)
    return VGroup(*[Line(P(a), P(b), color=color, stroke_width=9, stroke_opacity=op) for a, b in zip(pts, pts[1:])])


TT = fk(TH) @ M
D = TT @ np.linalg.inv(M)
S, THL = log6(D)
w = S[:3]
Q = np.cross(w, S[3:])


def frame_at(T, length=0.13):
    g = VGroup()
    for i, c in enumerate((RED, GREEN, BLUE)):
        g.add(Arrow(P(T[:3, 3]), P(T[:3, 3] + length * T[:3, i]), buff=0, color=c, stroke_width=6, max_tip_length_to_length_ratio=0.3))
    return g


class Lesson(Base):
    def construct(self):
        self.title("6.4", "指数映射与对数映射", "The exponential and logarithm maps")
        home = arm_lines(np.zeros(6), GREY_B, 0.6)
        goal = arm_lines(TH, GOLD, 0.8)
        self.play(Create(home), Create(goal), run_time=1.5)
        f0, f1 = frame_at(M), frame_at(TT)
        self.play(FadeIn(f0), FadeIn(f1))
        self.caption("已知两个位姿：零位（灰）与目标（金）。连接它们的螺旋运动是什么？", "Two poses: home (grey) and target (gold). Which screw motion joins them?")
        axis = DashedLine(P(Q - 0.5 * w), P(Q + 0.75 * w), color=YELLOW, stroke_width=4)
        self.play(Create(axis))
        self.caption("对数映射：由 D = T M⁻¹ 求出螺旋轴、转角 66.45° 和节距", "Log map: from D = T M⁻¹ get the screw axis, the angle 66.45° and the pitch")
        s = ValueTracker(0.0)
        moving = always_redraw(lambda: frame_at(exp6(S, THL * s.get_value()) @ M, 0.16))
        trace = always_redraw(lambda: VMobject(color=RED, stroke_width=4).set_points_as_corners(
            [P((exp6(S, THL * u) @ M)[:3, 3]) for u in np.linspace(0, max(s.get_value(), 1e-3), 50)]))
        self.add(trace, moving)
        self.caption("指数映射：e^[S]θs M，s 从 0 到 1，坐标系沿螺旋轴“拧”到目标", "Exp map: e^[S]θs M for s from 0 to 1 screws the frame onto the target")
        self.play(s.animate.set_value(1.0), run_time=5, rate_func=smooth)
        self.caption("法兰盘中心走一段螺旋线，到轴的距离始终不变", "The flange centre follows a helix, at a constant distance from the axis")
        self.wait(1.5)
        self.card([["指数映射与对数映射", "Exponential and logarithm maps"],
                   ["由旋量得到位移，由位移求出旋量", "From a screw to a displacement, and back"],
                   MathTex(r"T = e^{[\mathcal S]\theta},\qquad [\mathcal S]\theta = \log T", font_size=46)])
