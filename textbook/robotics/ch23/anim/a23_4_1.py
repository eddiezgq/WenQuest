"""动画 23.4.1（配图 23.4.2）：网球拍定理（算例 23.4.2）。工具箱 0.40 × 0.24 × 0.10 m、6 kg（示意值），I = (0.0338, 0.085, 0.1088) kg·m²，
同时让三个同样的工具箱分别主要绕最小、中间、最大惯量轴以 8 rad/s 转动，另两轴各 1% 的扰动。场景程序自己用 RK4 积分欧拉方程
（步长 2 ms，与程序 23.4.1 的结果一致：绕中间轴的在 1.60 s 第一次翻转，此后每 2.71 s 一次），姿态按物体角速度逐步右乘 e^{[ω]Δt}。
每个工具箱的 +z 面（最大的面）涂成橙色，便于看出翻转。右边：中间那个工具箱的角动量在物体坐标系中的端点，沿球面与能量椭球的交线运动；
红线是分界线。画面按实际时间播放 10 s。"""
from manim import *
from wq_anim import *
import numpy as np
import math

DIM = np.array([0.40, 0.24, 0.10])
MASS = 6.0
I = MASS / 12 * np.array([DIM[1] ** 2 + DIM[2] ** 2, DIM[0] ** 2 + DIM[2] ** 2, DIM[0] ** 2 + DIM[1] ** 2])
W0, EPS, DT, TEND = 8.0, 0.01, 0.002, 10.0


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def expso3(w, t):
    th = np.linalg.norm(w) * t
    if th < 1e-12:
        return np.eye(3)
    K = skew(w / np.linalg.norm(w))
    return np.eye(3) + math.sin(th) * K + (1 - math.cos(th)) * K @ K


def rhs(w):
    return np.cross(I * w, w) / I


def run(k):
    w = np.full(3, EPS * W0)
    w[k] = W0
    R = np.eye(3)
    n = int(TEND / DT)
    Ws, Rs = [w.copy()], [R.copy()]
    for _ in range(n):
        k1 = rhs(w)
        k2 = rhs(w + DT / 2 * k1)
        k3 = rhs(w + DT / 2 * k2)
        k4 = rhs(w + DT * k3)
        wn = w + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        R = R @ expso3((w + wn) / 2, DT)
        w = wn
        Ws.append(w.copy())
        Rs.append(R.copy())
    return np.array(Ws), np.array(Rs)


VIEW = np.array([[0.80, 0.60, 0.0], [-0.21, 0.28, 0.94], [0.56, -0.75, 0.35]])     # 正交投影：前两行是屏幕的 x、y，第三行是深度


def box(center, R, scale):
    h = DIM * 2.0                                                  # 画图：1 m 画成 4 个单位，半边长 = 2 × 尺寸
    corners = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]) * h / 2
    pts = (R @ corners.T).T
    faces = [([0, 1, 3, 2], -1, 0), ([4, 5, 7, 6], 1, 0), ([0, 1, 5, 4], -1, 1), ([2, 3, 7, 6], 1, 1), ([0, 2, 6, 4], -1, 2), ([1, 3, 7, 5], 1, 2)]
    polys = []
    for idx, sg, ax in faces:
        n = R[:, ax] * sg
        if (VIEW @ n)[2] < 0:                                       # 背面不画
            continue
        depth = float(np.mean([(VIEW @ pts[i])[2] for i in idx]))
        col = ORANGE if (ax == 2 and sg == 1) else (GREY_B if ax == 0 else GREY_D)
        P2 = [center + scale * np.array([(VIEW @ pts[i])[0], (VIEW @ pts[i])[1], 0]) for i in idx]
        polys.append((depth, Polygon(*P2, color=WHITE, stroke_width=1.2, fill_color=col, fill_opacity=0.9)))
    polys.sort(key=lambda x: x[0])
    return VGroup(*[p for _, p in polys])


class Lesson(Base):
    def construct(self):
        self.title("23.4", "网球拍定理：绕中间轴转动不稳定", "The tennis-racket theorem: rotation about the middle axis is unstable")
        data = [run(k) for k in range(3)]
        centers = [np.array([-5.0, -0.2, 0]), np.array([-2.3, -0.2, 0]), np.array([0.4, -0.2, 0])]
        heads = [["绕最小惯量轴", "least axis"], ["绕中间轴", "intermediate axis"], ["绕最大惯量轴", "greatest axis"]]
        hd = VGroup(*[bi(heads[k], 24, [GREEN_B, RED_B, BLUE_B][k]).move_to(centers[k] + UP * 2.1) for k in range(3)])
        self.add(hd)
        # 右边：角动量的端点（中间那个工具箱）
        Ws = data[1][0]
        Lb = Ws * I
        rad = np.linalg.norm(Lb[0])
        cR = np.array([4.6, -0.5, 0])
        sR = 1.55 / rad

        def proj(L):
            q = VIEW @ L
            return cR + sR * np.array([q[0], q[1], 0])

        self.add(Circle(radius=1.55, color=GREY_D, stroke_width=1.5).move_to(cR))
        E2 = float((I * Ws[0] ** 2).sum())
        sep = VGroup()
        for s1 in (1, -1):
            for s3 in (1, -1):
                tt = np.linspace(-1, 1, 200)
                L2 = math.sqrt(E2 * I[1]) * tt
                rest = E2 * I[1] - L2 ** 2
                L1 = s1 * np.sqrt(np.maximum(rest * I[0] * (I[2] - I[1]) / (I[1] * (I[2] - I[0])), 0))
                L3 = s3 * np.sqrt(np.maximum(rest * I[2] * (I[1] - I[0]) / (I[1] * (I[2] - I[0])), 0))
                pts = [proj(np.array([a, b, c])) for a, b, c in zip(L1, L2, L3)]
                sep.add(VMobject(color=RED, stroke_width=2).set_points_as_corners(pts))
        self.add(sep)
        for k, (lab, col) in enumerate(((r"L_1", GREEN), (r"L_2", RED), (r"L_3", BLUE))):
            e = np.zeros(3)
            e[k] = rad * 1.25
            self.add(DashedLine(proj(-e), proj(e), color=GREY_C, stroke_width=1.2), MathTex(lab, color=col, font_size=28).move_to(proj(e * 1.15)))
        self.add(bi(["中间那个的角动量（物体坐标系）", "its angular momentum in body axes"], 22, INK).move_to(cR + UP * 2.4))
        tk = ValueTracker(0.0)

        def scene():
            t = tk.get_value()
            i = min(int(round(t / DT)), len(Ws) - 1)
            g = VGroup()
            for k in range(3):
                g.add(box(centers[k], data[k][1][i], 2.0))
            trail = [proj(L) for L in Lb[: i + 1: 5]] or [proj(Lb[0])]
            if len(trail) > 1:
                g.add(VMobject(color=YELLOW, stroke_width=3).set_points_as_corners(trail))
            g.add(Dot(proj(Lb[i]), radius=0.08, color=YELLOW))
            g.add(Text(f"t = {t:.2f} s", font=CJK, font_size=24, color=INK).move_to([-2.3, -2.4, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("三个一样的工具箱，分别绕三根主轴转起来，另两轴各有 1% 的扰动（橙色是最大的面）",
                     "Three identical tool cases spun about the three principal axes, with 1% perturbations (orange: the largest face)", wait=0)
        self.play(tk.animate.set_value(3.0), run_time=3.0, rate_func=linear)
        self.caption("绕中间轴转的那个：1.6 s 后翻过来，此后每 2.7 s 翻一次；另两个一直平稳",
                     "About the middle axis it flips after 1.6 s and every 2.7 s thereafter; the other two stay steady", wait=0)
        self.play(tk.animate.set_value(7.0), run_time=4.0, rate_func=linear)
        self.caption("角动量的端点只能在球面与能量椭球的交线上走：中间轴附近的交线绕到另一端，于是翻转",
                     "L can only move along the intersection of the sphere and the energy ellipsoid: near the middle axis it runs to the far end", wait=0)
        self.play(tk.animate.set_value(TEND), run_time=TEND - 7.0, rate_func=linear)
        self.card([["网球拍定理", "The tennis-racket theorem"],
                   ["绕最大、最小惯量轴的转动稳定，绕中间轴的不稳定", "Spin about the greatest or least axis is stable; about the middle one, unstable"],
                   MathTex(r"\lambda = \omega_0\sqrt{\frac{(I_3 - I_2)(I_2 - I_1)}{I_1 I_3}}", font_size=44),
                   ["工具箱：λ = 4.6 rad/s，扰动每 0.22 s 放大 e 倍", "Tool case: λ = 4.6 rad/s, the perturbation grows e-fold every 0.22 s"]])
