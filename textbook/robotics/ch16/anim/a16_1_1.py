"""动画 16.1.1（配图 16.1.1）：末端速度是各关节贡献之和。
平面 3R 臂（UR5e 侧视尺寸 0.425、0.392、0.1 m），θ = (35°, −50°, −60°)，θ̇ = (25, 35, 50) °/s。
关节 i 单独转动时末端速度为 θ̇_i ẑ × (p − p_i)，垂直于 p_i 到末端的连线；三者首尾相接得到末端速度。
随后手臂按这组关节速度运动，三个箭头和它们的和随形态连续变化：雅可比矩阵的列是“此刻”的轴。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L = (0.425, 0.392, 0.1)
S = 6.5                                  # 1 m 在画面上的长度
BASE = np.array([-5.4, -2.3, 0.0])
VS = 3.5                                 # 速度箭头：1 m/s 画成 3.5 个单位
COLS = (RED, GREEN, GOLD)


def joints(th):
    pts, a = [BASE.copy()], 0.0
    for t, l in zip(th, L):
        a += t
        pts.append(pts[-1] + S * l * np.array([math.cos(a), math.sin(a), 0.0]))
    return pts


def contrib(th, dth, i):
    """关节 i 的贡献（m/s，画面坐标中的方向）。"""
    pts = joints(th)
    d = (pts[-1] - pts[i]) / S
    return dth[i] * np.array([-d[1], d[0], 0.0])


class Lesson(Base):
    def construct(self):
        self.title("16.1", "末端速度：各关节的贡献相加", "Tip velocity: the joint contributions add up")
        th0 = np.radians([35.0, -50.0, -60.0])
        dth = np.radians([25.0, 35.0, 50.0])
        t = ValueTracker(0.0)

        def cur():
            return th0 + dth * t.get_value()

        def arm():
            pts = joints(cur())
            g = VGroup(Polygon(BASE + LEFT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.2, BASE + LEFT * 0.2,
                               color=GREY_B, fill_color=GREY_E, fill_opacity=1))
            for k in range(3):
                g.add(Line(pts[k], pts[k + 1], color=STEEL, stroke_width=14 - 3 * k))
            for k in range(3):
                g.add(Dot(pts[k], radius=0.11, color=WHITE), Dot(pts[k], radius=0.06, color=COLS[k]))
            g.add(Dot(pts[3], radius=0.07, color=WHITE))
            return g

        rig = always_redraw(arm)
        self.play(FadeIn(rig), run_time=0.8)
        labels = VGroup(*[MathTex("p_%d" % (k + 1), color=COLS[k], font_size=30).next_to(joints(th0)[k], UP + LEFT * 0.6, buff=0.12)
                          for k in range(3)])
        self.play(FadeIn(labels), run_time=0.5)

        n = ValueTracker(1)

        def arrows():
            th = cur()
            p = joints(th)[-1]
            g = VGroup()
            c = p.copy()
            for k in range(int(round(n.get_value()))):
                v = contrib(th, dth, k) * VS
                g.add(Arrow(c, c + v, buff=0, color=COLS[k], stroke_width=6, max_tip_length_to_length_ratio=0.18))
                c = c + v
            return g

        arr = always_redraw(arrows)
        self.add(arr)
        self.caption("只转关节 1：末端绕 p₁ 转动，速度垂直于 p₁ 到末端的连线",
                     "Joint 1 alone: the tip turns about p₁, its velocity is perpendicular to the line from p₁")
        self.play(n.animate.set_value(2), run_time=0.3)
        self.caption("再加上关节 2 的贡献：θ̇₂ ẑ × (p − p₂)，首尾相接",
                     "Add joint 2's share θ̇₂ ẑ × (p − p₂), head to tail")
        self.play(n.animate.set_value(3), run_time=0.3)

        def total():
            th = cur()
            p = joints(th)[-1]
            v = sum(contrib(th, dth, k) for k in range(3)) * VS
            return Arrow(p, p + v, buff=0, color=WHITE, stroke_width=7, max_tip_length_to_length_ratio=0.12)

        tot = always_redraw(total)
        self.play(FadeIn(tot), run_time=0.6)
        eq = MathTex(r"\dot p = \sum_i \dot\theta_i\,\hat z\times(p - p_i)", font_size=36).to_corner(UR, buff=0.6).shift(DOWN * 1.2)
        self.play(Write(eq), run_time=1.0)
        self.caption("三者之和就是末端速度：每个关节贡献一列，排起来就是雅可比矩阵",
                     "Their sum is the tip velocity: each joint gives one column of the Jacobian")
        self.play(FadeOut(labels), run_time=0.3)
        self.caption("手臂一动，各关节“此刻”的位置变了，各列也随之改变",
                     "As the arm moves, each joint's present location changes, and so does its column", wait=0.2)
        self.play(t.animate.set_value(0.45), run_time=4.5, rate_func=linear)
        self.wait(0.8)
        self.card([["空间雅可比的第 i 列", "Column i of the space Jacobian"],
                   MathTex(r"J_{si} = [\mathrm{Ad}_{e^{[\mathcal S_1]\theta_1}\cdots e^{[\mathcal S_{i-1}]\theta_{i-1}}}]\,\mathcal S_i", font_size=40),
                   MathTex(r"\mathcal V_s = J_s(\theta)\,\dot\theta = \sum_i J_{si}\,\dot\theta_i", font_size=40),
                   ["关节 i 此刻的旋量轴，在 {s} 中表示", "joint i's screw axis where it is now, expressed in {s}"]])
