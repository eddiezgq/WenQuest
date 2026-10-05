"""动画 17.2.1（配图 17.2.1）：Panda（零件库 B-ARM-PANDA，旋量轴见表 12.3.1）的手停在 ready 姿态不动，
手臂沿自运动流形运动（算例 17.2.1）。零空间方向取广义叉积 c（式 (17.2.2)），dθ/ds = c/‖c‖，
每步用中点法预测、牛顿法校正（17.2.4 节）。从 ready 出发先向一侧走到关节 2 的下限，再走回来、走到另一侧的下限，最后回到 ready。
右侧是七个关节在各自限位区间中的位置和可操作度 w = ‖c‖。"""
from manim import *
from wq_anim import *
import numpy as np
import math

W_ = [(0, 0, 1), (0, 1, 0), (0, 0, 1), (0, -1, 0), (0, 0, 1), (0, -1, 0), (0, 0, -1)]
Q_ = [(0, 0, 0.333), (0, 0, 0.333), (0, 0, 0.649), (0.0825, 0, 0.649), (0, 0, 1.033), (0, 0, 1.033), (0.088, 0, 1.033)]
LO = np.array([-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973])
HI = np.array([2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973])
READY = np.array([0, -math.pi / 4, 0, -3 * math.pi / 4, 0, math.pi / 2, math.pi / 4])
FLANGE0 = np.array([0.088, 0, 0.926])


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def rot(w, t):
    K = skew(w)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def exp_rev(w, q, t):
    """绕过 q、方向 w 的轴转 t 的齐次变换。"""
    R = rot(np.array(w, float), t)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = np.array(q, float) - R @ np.array(q, float)
    return T


def chain(th):
    Es = [np.eye(4)]
    for w, q, t in zip(W_, Q_, th):
        Es.append(Es[-1] @ exp_rev(w, q, t))
    return Es


def jac(th):
    Es = chain(th)
    J = np.zeros((6, 7))
    for i in range(7):
        w = Es[i][:3, :3] @ np.array(W_[i], float)
        q = Es[i][:3, :3] @ np.array(Q_[i], float) + Es[i][:3, 3]
        J[:, i] = np.r_[w, -np.cross(w, q)]
    return J


def null_vec(J):
    return np.array([(-1) ** (6 + 1 + i + 1) * np.linalg.det(np.delete(J, i, axis=1)) for i in range(7)])


def logR(R):
    c = max(-1.0, min(1.0, (np.trace(R) - 1) / 2))
    a = math.acos(c)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / 2
    return v if a < 1e-9 else a / math.sin(a) * v


def pose_err(T, Td):
    """小误差的空间误差旋量：(转动矢量, 原点处的线速度部分)。"""
    D = Td @ np.linalg.inv(T)
    w = logR(D[:3, :3])
    return np.r_[w, D[:3, 3] - 0.5 * np.cross(w, D[:3, 3])]


TD = chain(READY)[-1]


def unit_c(th):
    c = null_vec(jac(th))
    return c / np.linalg.norm(c)


def step(th, h):
    th = th + h * unit_c(th + 0.5 * h * unit_c(th))
    for _ in range(3):
        J = jac(th)
        th = th + J.T @ np.linalg.solve(J @ J.T, pose_err(chain(th)[-1], TD))
    return th


def inside(th):
    return np.all(th >= LO) and np.all(th <= HI)


def walk(sign, h=0.025):
    th, out = READY.copy(), []
    for _ in range(400):
        nxt = step(th, sign * h)
        if not inside(nxt):
            break
        th = nxt
        out.append(th.copy())
    return out


SIDE_A, SIDE_B = walk(1), walk(-1)
PATH = SIDE_A + SIDE_A[::-1] + [READY] + SIDE_B + SIDE_B[::-1] + [READY]
N1, N2 = len(SIDE_A), len(SIDE_A) * 2 + 1 + len(SIDE_B)


def points(th):
    Es = chain(th)
    act = lambda T, p: T[:3, :3] @ np.array(p, float) + T[:3, 3]
    return [np.zeros(3), np.array([0, 0, 0.333]), act(Es[3], (0, 0, 0.649)), act(Es[3], (0.0825, 0, 0.649)),
            act(Es[4], (0, 0, 0.649)), act(Es[4], (0, 0, 1.033)), act(Es[6], (0.088, 0, 1.033)), act(Es[7], FLANGE0)]


AZ, EL, SCL = math.radians(-58), math.radians(16), 4.4
ORG = np.array([-3.4, -2.6, 0.0])
ER = np.array([-math.sin(AZ), math.cos(AZ), 0.0])
EU = np.array([-math.sin(EL) * math.cos(AZ), -math.sin(EL) * math.sin(AZ), math.cos(EL)])


def P3(p):
    p = np.asarray(p, float)
    return ORG + SCL * np.array([p @ ER, p @ EU, 0.0])


class Lesson(Base):
    def construct(self):
        self.title("17.2", "Panda 的自运动：手不动，肘在摆", "Panda's self-motion: the hand stays, the elbow swings")
        k = ValueTracker(0.0)

        def cur():
            x = k.get_value()
            i = min(int(x), len(PATH) - 2)
            a = x - i
            return (1 - a) * PATH[i] + a * PATH[i + 1]

        floor = Polygon(P3((-0.45, -0.55, 0)), P3((0.6, -0.55, 0)), P3((0.6, 0.55, 0)), P3((-0.45, 0.55, 0)),
                        stroke_width=1, color=GREY_D, fill_color=GREY_E, fill_opacity=0.35)
        ped = Line(P3((0, 0, 0)), P3((0, 0, 0.333)), color=GREY_B, stroke_width=16)
        Tb = chain(READY)[-1]
        F = Tb[:3, :3] @ FLANGE0 + Tb[:3, 3]
        hand_frame = VGroup(*[Arrow(P3(F), P3(F + 0.12 * (Tb[:3, :3] @ np.array([0.7071, 0.7071, 0]) if i == 0 else
                                                            Tb[:3, :3] @ np.array([0.7071, -0.7071, 0]) if i == 1 else
                                                            Tb[:3, :3] @ np.array([0, 0, -1.0]))),
                                    buff=0, color=col, stroke_width=4, max_tip_length_to_length_ratio=0.3)
                              for i, col in enumerate((RED, GREEN, BLUE))])
        gear = RegularPolygon(8, color=GOLD, fill_color=GOLD_E, fill_opacity=1).scale(0.18).move_to(P3(F + Tb[:3, :3] @ np.array([0, 0, -0.1])))
        self.play(FadeIn(floor), FadeIn(ped), run_time=0.6)

        def arm():
            pts = [P3(p) for p in points(cur())]
            g = VGroup()
            for i in range(1, 7):
                g.add(Line(pts[i], pts[i + 1], color=STEEL if i not in (2, 3) else BLUE_B, stroke_width=11 if i < 5 else 8))
            for i in (1, 3, 5, 7):
                g.add(Dot(pts[i], radius=0.06, color=WHITE))
            return g

        arm_m = always_redraw(arm)
        elbow = always_redraw(lambda: Dot(P3(points(cur())[3]), radius=0.09, color=YELLOW))
        self.play(FadeIn(arm_m), FadeIn(elbow), FadeIn(gear), FadeIn(hand_frame))

        # 右侧：七个关节的限位条与可操作度
        bars = VGroup()
        x0, y0, wbar = 2.6, 2.0, 3.2
        for j in range(7):
            y = y0 - 0.5 * j
            bars.add(Rectangle(width=wbar, height=0.16, color=GREY_C, stroke_width=1.5).move_to([x0 + wbar / 2, y, 0]),
                     Text(f"θ{j + 1}", font=LATIN, font_size=20, color=INK).move_to([x0 - 0.35, y, 0]))
        btitle = zh("关节在限位区间中的位置", 20, MUTED).move_to([x0 + wbar / 2, y0 + 0.45, 0])

        def marks():
            th = cur()
            g = VGroup()
            for j in range(7):
                u = (th[j] - LO[j]) / (HI[j] - LO[j])
                near = min(u, 1 - u) < 0.02
                g.add(Rectangle(width=0.07, height=0.3, color=RED if near else YELLOW, fill_opacity=1, stroke_width=0)
                      .move_to([x0 + wbar * min(max(u, 0), 1), y0 - 0.5 * j, 0]))
            c = null_vec(jac(th))
            g.add(VGroup(zh("可操作度", 22), MathTex(r"w = \|c\| = %.4f" % np.linalg.norm(c), font_size=28)).arrange(RIGHT, buff=0.2)
                  .move_to([x0 + wbar / 2, y0 - 3.75, 0]))
            return g

        mk = always_redraw(marks)
        self.play(FadeIn(bars), FadeIn(btitle), FadeIn(mk))
        self.caption("手和齿轮停在 ready 姿态；七个关节、六个位姿方程，多出一个自由度",
                     "Hand and gear held at the ready pose: seven joints, six pose equations, one spare freedom", wait=0.8)
        trail = TracedPath(elbow.get_center, stroke_color=YELLOW, stroke_width=2.5, stroke_opacity=0.8)
        self.add(trail)
        self.caption("沿零空间矢量 c 走：肘部绕肩腕连线摆开，手一动不动",
                     "Move along the null vector c: the elbow swings about the shoulder–wrist line, the hand does not move", wait=0)
        self.play(k.animate.set_value(N1 - 1), run_time=5.0, rate_func=smooth)
        self.caption("走到头：关节 2 到了下限（红色），再走就超出限位",
                     "End of the road: joint 2 reaches its lower limit (red); beyond this the limits are violated", wait=1.2)
        self.caption("往回走，经过 ready，走向另一侧",
                     "Back through ready and on to the other side", wait=0)
        self.play(k.animate.set_value(N2 - 1), run_time=7.0, rate_func=smooth)
        self.caption("另一侧也是关节 2 先到下限；可操作度在 ready 处最大",
                     "On this side too joint 2 hits its lower limit first; manipulability is largest at ready", wait=1.0)
        self.play(k.animate.set_value(len(PATH) - 1), run_time=3.0, rate_func=smooth)
        self.card([["零空间运动", "Null-space motion"],
                   MathTex(r"\frac{\mathrm d\theta}{\mathrm ds} = \frac{c(\theta)}{\|c(\theta)\|},\quad c_i = (-1)^{m+1+i}\det J_{(i)}", font_size=36),
                   MathTex(r"Jc = 0,\qquad \|c\| = \sqrt{\det(JJ^{\mathsf T})} = w", font_size=36),
                   ["每走一步用牛顿法校正，手就不会漂离", "Correct each step with Newton's method and the hand never drifts"]])
