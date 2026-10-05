"""动画 16.4.1（配图 16.4.2）：UR5e 的法兰盘保持 θ* 时的姿态和高度，中心沿水平射线从 ρ = 0.22 m 移到伸直附近
（ρ ≈ 0.9 m）。法兰盘处画出“姿态保持不变”时的线速度椭球（定理 16.4.2）的投影，右侧画出它的可操作度随 ρ 的变化：
靠近基座时椭球被压扁（肩部奇异附近），中间最饱满（ρ ≈ 0.75 m），伸到头时又被压成一片（肘部奇异）。
UR5e 的旋量轴取表 12.1.1；逆解用阻尼牛顿法沿路径延拓（与程序 16.4.1 的解析解同一支）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
YD = np.array([0, -1.0, 0])
WS = [np.array([0, 0, 1.0]), YD, YD, YD, np.array([0, 0, -1.0]), YD]
QS = [np.array([0, 0, H1]), np.array([0, -W1, H1]), np.array([-L1, -W1 + W2, H1]), np.array([-L1 - L2, -W1 + W2, H1]),
      np.array([-L1 - L2, -W1 + W2 - W3, H1]), np.array([-L1 - L2, -W1 + W2 - W3, H1 - H2])]
MR = np.array([[1.0, 0, 0], [0, -1, 0], [0, 0, -1]])
MP = np.array([-L1 - L2, -W1 + W2 - W3 - W4, H1 - H2])
TH0 = np.radians([30, -60, 90, -120, -90, 45])


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def rot(w, t):
    K = skew(w)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def chain(th):
    """各关节此刻的轴（方向、轴上一点）与法兰盘位姿；以及连杆折线上的点。"""
    R, p = np.eye(3), np.zeros(3)
    axes = []
    for w, q, t in zip(WS, QS, th):
        axes.append((R @ w, R @ q + p))
        Ri = rot(w, t)
        p = R @ (q - Ri @ q) + p
        R = R @ Ri
    return axes, R @ MR, R @ MP + p


def points(th):
    R, p = np.eye(3), np.zeros(3)
    keep = [(R.copy(), p.copy())]
    for w, q, t in zip(WS, QS, th):
        Ri = rot(w, t)
        p = R @ (q - Ri @ q) + p
        R = R @ Ri
        keep.append((R.copy(), p.copy()))
    q = QS
    pts = [(0, np.zeros(3)), (0, q[0]), (1, q[1]), (2, q[1] + np.array([-L1, 0, 0])), (2, q[2]), (3, q[3]),
           (4, q[4]), (5, q[5]), (6, q[5] + np.array([0, -W4, 0]))]
    return [keep[k][0] @ x + keep[k][1] for k, x in pts]


def jg(th):
    axes, R, p = chain(th)
    J = np.zeros((6, 6))
    for i, (w, q) in enumerate(axes):
        J[:3, i] = w
        J[3:, i] = np.cross(w, p - q)
    return J, R, p


def logR(R):
    c = max(-1.0, min(1.0, (np.trace(R) - 1) / 2))
    a = math.acos(c)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return v / 2 if a < 1e-9 else a / (2 * math.sin(a)) * v


_, R0, P0 = chain(TH0)
ER = np.array([P0[0], P0[1], 0]) / math.hypot(P0[0], P0[1])
ET = np.cross([0, 0, 1.0], ER)


def solve(rho, th):
    target = np.array([rho * ER[0], rho * ER[1], P0[2]])
    for _ in range(40):
        J, R, p = jg(th)
        e = np.r_[R @ logR(R.T @ R0), target - p]
        if np.linalg.norm(e) < 1e-12:
            break
        th = th + J.T @ np.linalg.solve(J @ J.T + 1e-10 * np.eye(6), e)
    return th


def held(th):
    """姿态保持时法兰盘中心的线速度椭球：{ṗ : ‖J_g⁻¹(0, ṗ)‖ ≤ 1} = {A x : ‖x‖ ≤ 1}，返回 A。"""
    J, _, _ = jg(th)
    G = np.linalg.inv(J)[:, 3:]
    _, s, Vt = np.linalg.svd(G)
    return Vt.T @ np.diag(1 / s)


# 路径：从 θ* 向两侧延拓
RHO0 = math.hypot(P0[0], P0[1])
RHOS = np.linspace(0.22, 0.905, 138)
TABLE = {}
for side in (np.where(RHOS >= RHO0)[0], np.where(RHOS < RHO0)[0][::-1]):
    th = TH0.copy()
    for i in side:
        th = solve(RHOS[i], th)
        TABLE[i] = th.copy()
THS = np.array([TABLE[i] for i in range(len(RHOS))])
WH = np.array([abs(np.linalg.det(held(t))) for t in THS])

S = 5.2
ORG = np.array([-5.6, -2.6, 0.0])
PJ = np.array([ER + 0.32 * ET, np.array([0, 0, 1.0]) + 0.18 * ET])     # 斜投影：径向朝右，竖直朝上


def scr(x):
    v = PJ @ x
    return ORG + S * np.array([v[0], v[1], 0.0])


class Lesson(Base):
    def construct(self):
        self.title("16.4", "可操作度椭球随形态变化", "The manipulability ellipsoid changes with the configuration")
        rho = ValueTracker(RHO0)

        def th_now():
            return np.array([np.interp(rho.get_value(), RHOS, THS[:, k]) for k in range(6)])

        floor = Line(scr(-0.15 * ER), scr(1.0 * ER), color=GREY_B, stroke_width=2)
        path = DashedLine(scr(0.22 * ER + P0[2] * np.array([0, 0, 1.0])), scr(0.905 * ER + P0[2] * np.array([0, 0, 1.0])),
                          color=GREY_C, stroke_width=2)
        self.play(Create(floor), Create(path), run_time=0.8)

        def rig():
            th = th_now()
            pts = [scr(x) for x in points(th)]
            g = VGroup()
            for a, b in zip(pts[:-1], pts[1:]):
                g.add(Line(a, b, color=STEEL, stroke_width=9))
            for a in pts[1:-1]:
                g.add(Dot(a, radius=0.06, color=WHITE))
            A = held(th) * 0.25 * S
            Mp = PJ @ A
            lam, V = np.linalg.eigh(Mp @ Mp.T)
            ax1, ax2 = math.sqrt(max(lam[1], 1e-10)), math.sqrt(max(lam[0], 1e-10))
            ang = math.atan2(V[1, 1], V[0, 1])
            c = pts[-1]
            e = Ellipse(width=2 * ax1, height=2 * ax2, color=ORANGE, stroke_width=4).rotate(ang).move_to(c)
            g.add(e, Dot(c, radius=0.07, color=YELLOW))
            return g

        arm = always_redraw(rig)
        self.play(FadeIn(arm), run_time=0.8)
        self.caption("法兰盘朝下、高度不变，中心沿虚线移动。橙色：姿态保持时单位关节速度能产生的线速度",
                     "Flange down at a fixed height, centre moving along the dashed line. Orange: velocities from unit joint speed with orientation held",
                     wait=1.0)

        ax = Axes(x_range=[0.2, 0.92, 0.1], y_range=[0, 1.05, 0.25], x_length=4.6, y_length=2.6, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_ticks": False}).move_to([3.9, 1.0, 0])
        curve = ax.plot_line_graph(RHOS, WH / WH.max(), line_color=BLUE, add_vertex_dots=False, stroke_width=4)
        lab = VGroup(MathTex(r"w / w_{\max}", font_size=30, color=BLUE).next_to(ax, UP, buff=0.1),
                     MathTex(r"\rho\ /\ \mathrm{m}", font_size=28, color=GREY_B).next_to(ax, DOWN, buff=0.15))
        self.play(Create(ax), Create(curve), FadeIn(lab), run_time=1.0)

        def mark():
            r = rho.get_value()
            w = float(np.interp(r, RHOS, WH)) / WH.max()
            d = Dot(ax.c2p(r, w), radius=0.09, color=YELLOW)
            t = MathTex(r"\rho = %.2f\ \mathrm{m}" % r, font_size=32, color=YELLOW).move_to([3.9, -1.0, 0])
            return VGroup(d, t)

        mk = always_redraw(mark)
        self.add(mk)
        self.play(rho.animate.set_value(0.22), run_time=4.0, rate_func=smooth)
        self.caption("靠近基座：椭球被压扁，接近肩部奇异", "Near the base the ellipsoid is squashed: close to the shoulder singularity", wait=0.6)
        self.play(rho.animate.set_value(float(RHOS[int(np.argmax(WH))])), run_time=5.0, rate_func=smooth)
        self.caption("ρ ≈ 0.75 m：椭球最饱满，可操作度最大", "At ρ ≈ 0.75 m the ellipsoid is fullest: the manipulability peaks", wait=0.8)
        self.play(rho.animate.set_value(0.905), run_time=3.5, rate_func=smooth)
        self.caption("伸到头：椭球压成一片，肘部奇异，径向失去速度", "Fully stretched: the ellipsoid flattens, elbow singularity, radial speed lost", wait=1.0)
        self.card([["姿态保持时的线速度椭球", "Velocity ellipsoid with the orientation held"],
                   MathTex(r"\{\dot p : \|J_g^{-1}(0,\dot p)\| \le 1\}", font_size=38),
                   MathTex(r"w = \sigma_1\sigma_2\sigma_3", font_size=38),
                   ["两端奇异处退化，中间某处最大", "Degenerate at the singular ends, largest in between"]])
