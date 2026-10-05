"""动画 20.2.1（配图 20.2.1）：Go2 四只脚踩在原地，机身抬头、低头、下蹲、升高；每条腿按定理 20.2.1 单独求逆解。
侧视（x 向右、z 向上），只画左侧的前腿和后腿（右侧与之重合）。尺寸取零件库模型：髋点 x = ±0.1934 m，
l₁ = l₂ = 0.213 m，足端小球半径 0.022 m，站立时机身原点离地 0.2868 m；小腿关节限位 −156°～−48°。"""
from manim import *
from wq_anim import *
import numpy as np
import math

AX, L1, L2, RF, H0 = 0.1934, 0.213, 0.213, 0.022, 0.2868
SC = 6.0
O = np.array([0.0, -2.2, 0])          # 地面上 x = 0 的点
LIM3 = (-2.7227, -0.83776)


def R2(p):
    return np.array([[math.cos(p), math.sin(p)], [-math.sin(p), math.cos(p)]])


def leg(sx, pitch, z):
    """足端在 {s} 中固定于 (sx·a_x, r_f)；返回 髋、膝、足 的世界坐标与 (θ2, θ3)。"""
    R = R2(pitch)
    base = np.array([0.0, z])
    hip = base + R @ np.array([sx * AX, 0.0])
    foot = np.array([sx * AX, RF])
    rel = R.T @ (foot - base) - np.array([sx * AX, 0.0])
    xp, zp = rel
    D = math.hypot(xp, zp)
    c3 = max(-1.0, min(1.0, (D * D - L1 * L1 - L2 * L2) / (2 * L1 * L2)))
    t3 = -math.acos(c3)
    t2 = math.atan2(-xp, -zp) - math.atan2(L2 * math.sin(t3), L1 + L2 * math.cos(t3))
    knee_b = np.array([sx * AX, 0.0]) + L1 * np.array([-math.sin(t2), -math.cos(t2)])
    knee = base + R @ knee_b
    ok = LIM3[0] - 1e-6 <= t3 <= LIM3[1] + 1e-6 and D <= L1 + L2
    return hip, knee, foot, t2, t3, ok


def W(p):
    return O + np.array([p[0] * SC, p[1] * SC, 0])


class Lesson(Base):
    def construct(self):
        self.title("20.2", "脚不动，机身动：浮动基座", "Feet planted, body moving: the floating base")
        g = Line(W((-0.5, 0)), W((0.5, 0)), color=GREY_B, stroke_width=3)
        self.play(Create(g), run_time=0.6)
        pit = ValueTracker(0.0)
        hz = ValueTracker(H0)

        def scene():
            p, z = pit.get_value(), hz.get_value()
            R = R2(p)
            base = np.array([0.0, z])
            body = [base + R @ np.array(c) for c in ((-0.26, -0.05), (0.26, -0.05), (0.29, 0.0), (0.26, 0.05), (-0.26, 0.05))]
            grp = VGroup(Polygon(*[W(c) for c in body], color=GREY_B, fill_color=NAVY, fill_opacity=1, stroke_width=2))
            txt = []
            for sx, name in ((1, "前腿"), (-1, "后腿")):
                hip, knee, foot, t2, t3, ok = leg(sx, p, z)
                col = STEEL if ok else RED
                grp.add(Line(W(hip), W(knee), color=col, stroke_width=9), Line(W(knee), W(foot), color=col, stroke_width=7),
                        Dot(W(hip), radius=0.07, color=WHITE), Dot(W(knee), radius=0.06, color=WHITE), Dot(W(foot), radius=0.13, color=GREY_D))
                txt.append(Text(f"{name}  θ₂ = {math.degrees(t2):.1f}°   θ₃ = {math.degrees(t3):.1f}°".replace("-", "−"),
                                font=CJK, font_size=22, color=col))
            info = VGroup(Text(f"机身俯仰 ϑ = {math.degrees(p):.1f}°，离地 {z:.3f} m".replace("-", "−"), font=CJK, font_size=24, color=YELLOW),
                          *txt).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.5).shift(DOWN * 0.6)
            grp.add(info)
            return grp

        self.add(always_redraw(scene))
        self.caption("四只脚踩在原地不动：每条腿由“脚在机身坐标系中的位置”单独求逆解",
                     "Feet stay put: each leg is solved on its own from where its foot lies in the body frame", wait=0.5)
        self.caption("抬头：前腿伸长、后腿收缩；四条腿像并联机构的支链一样托着机身",
                     "Nose up: front legs stretch, rear legs fold, like the limbs of a parallel mechanism", wait=0)
        self.play(pit.animate.set_value(math.radians(-20)), run_time=2.5)
        self.caption("低头：前腿收缩、后腿伸长", "Nose down: front legs fold, rear legs stretch", wait=0)
        self.play(pit.animate.set_value(math.radians(20)), run_time=3.0)
        self.play(pit.animate.set_value(0.0), run_time=1.5)
        self.caption("下蹲到小腿关节的限位 −156°，升高到 −48°：机身高度在约 0.11～0.41 m 之间",
                     "Crouch to the calf limit −156°, rise to −48°: body height from about 0.11 to 0.41 m", wait=0)
        self.play(hz.animate.set_value(0.115), run_time=2.5)
        self.play(hz.animate.set_value(0.41), run_time=3.0)
        self.play(hz.animate.set_value(H0), run_time=1.5)
        self.caption("超过限位的姿态（红色）不可行：此时某条腿的小腿关节要伸过 −48° 的限位才够得着地面上的那只脚",
                     "Poses past a limit (red) are infeasible: a calf joint would have to open beyond −48° to reach its foot", wait=0)
        self.play(pit.animate.set_value(math.radians(-42)), run_time=2.0)
        self.wait(0.8)
        self.play(pit.animate.set_value(0.0), run_time=1.2)
        self.card([["浮动基座：位形 = 机身位姿 + 关节角", "Floating base: configuration = body pose + joint angles"],
                   MathTex(r"p_{b,i} = T_{sb}^{-1}\,p_{s,i},\qquad \theta_i = \mathrm{IK}_i(p_{b,i})", font_size=42),
                   MathTex(r"J_i\,\dot\theta_i = [p_{b,i}]\,\omega_b - v_b", font_size=42),
                   ["四脚站立的足式机器人是一个并联机构", "A robot standing on four feet is a parallel mechanism"]])
