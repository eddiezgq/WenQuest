"""动画 15.4.1（配图 15.4.2）：平面 3R 臂（0.425、0.392、0.1 m）的两个任务（算例 15.4.2）。
主任务：末端到达 (0.75, 0.10) m；次任务：工具朝向 φ_d = 160°，超出式 (14.2.10) 的可行范围。
任务优先级的迭代 Δθ = J₁⁺e₁ + (J₂N₁)#(k_p e₂ − J₂J₁⁺e₁)（阻尼 λ₂ = 0.3，k_p = 0.1，两部分各自限幅 0.2 rad）：
末端先到达目标，此后只在零空间里转动，朝向升到可行范围的端点 131.8° 停住，腕点落在 2R 外圆上。最后与加权最小二乘的结果比较。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L = (0.425, 0.392, 0.1)
PD = np.array([0.75, 0.10])
PHI_D = math.radians(160.0)
SC = 9.0
O = np.array([-5.9, -1.5, 0.0])


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


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


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def solve(mode, th0, iters=60):
    th = np.array(th0, float)
    out = [th.copy()]
    for _ in range(iters):
        p = joints(th)[-1]
        e1, e2 = PD - p, wrap(PHI_D - sum(th))
        J1, J2 = jac(th), np.ones((1, 3))
        if mode == "priority":
            J1p = np.linalg.pinv(J1)
            N1 = np.eye(3) - J1p @ J1
            B = J2 @ N1
            parts = [J1p @ e1, B.T @ np.linalg.solve(B @ B.T + 0.09 * np.eye(1), 0.1 * np.array([e2]) - J2 @ J1p @ e1)]
        else:
            A = np.vstack([J1, 0.1 * J2])
            parts = [np.linalg.solve(A.T @ A + 1e-4 * np.eye(3), A.T @ np.r_[e1, 0.1 * e2])]
        for i, q in enumerate(parts):
            m = np.abs(q).max()
            if m > 0.2:
                parts[i] = q * 0.2 / m
        th = th + sum(parts)
        out.append(th.copy())
    return out


class Lesson(Base):
    def construct(self):
        self.title("15.4", "任务优先级：先保位置，再顾朝向", "Task priority: position first, then orientation")
        th0 = np.radians([20, -40, 10])
        pri = solve("priority", th0, 40)
        wei = solve("weighted", th0, 400)
        r = math.hypot(*PD)
        beta = math.atan2(PD[1], PD[0])
        half = math.acos((r * r + L[2] ** 2 - (L[0] + L[1]) ** 2) / (2 * r * L[2]))
        phi_hi = beta + half

        base = Polygon(O + LEFT * 0.35 + DOWN * 0.25, O + RIGHT * 0.35 + DOWN * 0.25, O + RIGHT * 0.18, O + LEFT * 0.18,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        R = L[0] + L[1]
        outer = Arc(radius=SC * R, start_angle=-0.35, angle=0.75, arc_center=O, color=GREY_B, stroke_width=2).set_stroke(opacity=0.7)
        outer = DashedVMobject(outer, num_dashes=30)
        ol = zh("2R 外圆", 20, GREY_B).move_to(S(R * math.cos(0.38), R * math.sin(0.38)) + RIGHT * 0.7)
        tgt = Dot(S(*PD), radius=0.09, color=RED)
        ts = np.linspace(0, 2 * math.pi, 200)
        ok = np.cos(ts - beta) >= math.cos(half) - 1e-12
        good = VMobject(color=BLUE, stroke_width=3).set_points_as_corners([S(PD[0] - L[2] * math.cos(t), PD[1] - L[2] * math.sin(t)) for t in ts[ok]])
        bad = DashedVMobject(VMobject(color=RED_C, stroke_width=3).set_points_smoothly(
            [S(PD[0] - L[2] * math.cos(t), PD[1] - L[2] * math.sin(t)) for t in np.linspace(beta + half, beta + 2 * math.pi - half, 60)]), num_dashes=18)
        want = DashedLine(S(*PD), S(*(PD + 0.16 * np.array([math.cos(PHI_D), math.sin(PHI_D)]))), color=RED, stroke_width=3).add_tip(tip_length=0.2)
        wl = zh("要求的朝向 160°", 20, RED).next_to(want.get_end(), UP, buff=0.15).shift(LEFT * 0.6)
        self.play(FadeIn(base), Create(outer), FadeIn(ol), FadeIn(tgt), run_time=1.0)

        k = ValueTracker(0.0)

        def arm_of(seq, color, width=1.0):
            def make():
                i = min(int(round(k.get_value())), len(seq) - 1)
                pts = [S(*p) for p in joints(seq[i])]
                g = VGroup(Line(pts[0], pts[1], color=color, stroke_width=12 * width), Line(pts[1], pts[2], color=color, stroke_width=9 * width),
                           Line(pts[2], pts[3], color=color, stroke_width=7 * width))
                for q in pts[:3]:
                    g.add(Dot(q, radius=0.08, color=WHITE))
                return g
            return make

        arm = always_redraw(arm_of(pri, STEEL))

        def info():
            i = min(int(round(k.get_value())), len(pri) - 1)
            th = pri[i]
            e = np.linalg.norm(PD - joints(th)[-1]) * 1000
            ph = math.degrees(sum(th))
            return VGroup(Text(f"k = {i}", font=LATIN, font_size=24),
                          VGroup(zh("位置误差", 22), Text(f"{e:.3g} mm" if e > 1e-6 else "< 1e-6 mm", font=LATIN, font_size=22)).arrange(RIGHT, buff=0.2),
                          VGroup(zh("朝向 φ", 22), Text(f"{ph:.1f}°", font=LATIN, font_size=22)).arrange(RIGHT, buff=0.2)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.5).shift(DOWN * 1.0)

        inf = always_redraw(info)
        self.play(FadeIn(arm), FadeIn(inf))
        self.caption("红点是位置目标；工具还要求指向左上方 160°",
                     "Red dot: the position goal; the tool should also point up-left at 160°", wait=0.5)
        self.play(Create(want), FadeIn(wl))
        self.play(Create(good), Create(bad), run_time=1.0)
        self.caption("腕点只能落在以目标为圆心的小圆上，且不能超出 2R 外圆：蓝色部分可行",
                     "The wrist must lie on the small circle around the goal and inside the 2R reach: blue part feasible", wait=1.5)
        self.caption("主任务优先：几步之内末端就到达目标",
                     "The primary task first: within a few steps the tip is on the goal", wait=0)
        self.play(k.animate.set_value(6), run_time=3.0, rate_func=linear)
        self.caption("此后次任务只在零空间里改进：末端不动，工具转向 160°",
                     "Then the secondary task acts only in the null space: the tip stays, the tool turns toward 160°", wait=0)
        self.play(k.animate.set_value(len(pri) - 1), run_time=6.0, rate_func=linear)
        self.caption(f"朝向升到可行范围的端点 {math.degrees(phi_hi):.1f}° 停住：腕点已在 2R 外圆上",
                     f"φ stops at the end of the feasible range, {math.degrees(phi_hi):.1f}°: the wrist is on the 2R outer circle", wait=1.8)
        ew = np.linalg.norm(PD - joints(wei[-1])[-1]) * 1000
        phw = math.degrees(sum(wei[-1]))
        ghost = arm_of(wei, ORANGE, 0.7)()
        ghost.set_opacity(0.75)
        gl = zh("加权最小二乘：两头都差一点", 22, ORANGE).to_corner(DL, buff=0.6).shift(UP * 1.1)
        self.play(FadeIn(ghost), FadeIn(gl))
        self.caption(f"对照：加权最小二乘把两个误差一起压，位置偏了 {ew:.0f} mm，朝向只到 {phw:.1f}°",
                     f"Compare: weighted least squares trades both: the tip is {ew:.0f} mm off and φ reaches only {phw:.1f}°", wait=2.0)
        self.card([["任务优先级", "Task priority"],
                   MathTex(r"\Delta\theta = J_1^{+}e_1 + (J_2N_1)^{+}\big(e_2 - J_2J_1^{+}e_1\big)", font_size=40),
                   MathTex(r"N_1 = I - J_1^{+}J_1,\qquad J_1(J_2N_1)^{+} = 0", font_size=36),
                   ["次任务不会破坏主任务；做不到时停在最接近的地方", "The secondary task never spoils the primary; if unreachable it stops at the best feasible value"]])
