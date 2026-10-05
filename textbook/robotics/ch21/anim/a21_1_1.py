"""动画 21.1.1（配图 21.1.2）：俯视 X2，四个旋翼的推力依次按四种组合变化：总推力、横滚、俯仰、偏航。
几何取零件库模型：旋翼中心 (±0.14, ±0.18) m，桨盘半径 0.13 m，旋翼 1、3 逆时针转，2、4 顺时针转；
悬停推力 m𝔤/4 = 3.25 N。右侧小图是从机尾看（横滚）或从右侧看（俯仰）的机身倾斜，倾角只为示意。"""
from manim import *
from wq_anim import *
import numpy as np
import math

S = 5.8                                   # 1 m 画成 5.8 个单位
LX, LY, RR = 0.14, 0.18, 0.13
POS = [(-LX, -LY), (-LX, LY), (LX, LY), (LX, -LY)]
SIG = [-1, 1, -1, 1]                      # 反扭矩符号：−1 → 旋翼逆时针转
F0 = 3.25
C0 = np.array([-2.6, 0.05, 0])


def f_of(fz, mx, my, mz):
    """式 (21.1.8)：由总推力与三个力矩求四个推力。"""
    out = []
    for (x, y), s in zip(POS, SIG):
        out.append(fz / 4 + np.sign(y) * mx / (4 * LY) - np.sign(x) * my / (4 * LX) + s * mz / (4 * 0.0201))
    return out


class Lesson(Base):
    def construct(self):
        self.title("21.1", "四个推力，四个通道", "Four thrusts, four channels")
        mx, my, mz, yaw = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)
        fz = ValueTracker(4 * F0)

        def rot(p):
            a = yaw.get_value()
            c, s = math.cos(a), math.sin(a)
            return C0 + S * np.array([c * p[0] - s * p[1], s * p[0] + c * p[1], 0])

        def drone():
            f = f_of(fz.get_value(), mx.get_value(), my.get_value(), mz.get_value())
            g = VGroup()
            for i, (p, s) in enumerate(zip(POS, SIG)):
                d = f[i] - F0
                col = BLUE if d > 0.02 else RED if d < -0.02 else GREY_B
                op = min(0.75, 0.15 + abs(d) * 0.35)
                g.add(Line(rot((0, 0)), rot(p), color=GREY_B, stroke_width=7))
                g.add(Circle(radius=RR * S, color=GREY_B, stroke_width=2, fill_color=col, fill_opacity=op).move_to(rot(p)))
                a0 = yaw.get_value() + (math.radians(200) if s < 0 else math.radians(320))
                g.add(Arc(radius=RR * S * 0.75, start_angle=a0, angle=(1 if s < 0 else -1) * math.radians(120), color=PURPLE_B,
                          stroke_width=3).move_arc_center_to(rot(p)).add_tip(tip_length=0.15))
                lab = Text(f"{i + 1}", font=CJK, font_size=26, weight=BOLD, color=WHITE).move_to(rot((p[0] * 0.62, p[1] * 0.62)))
                val = Text(f"{f[i]:.2f} N", font=CJK, font_size=20, color=BLUE_B if d > 0.02 else RED_B if d < -0.02 else INK)
                val.move_to(rot((p[0] * 2.1, p[1] * 1.8)))
                g.add(lab, val)
            body = Ellipse(width=0.32 * S, height=0.08 * S, color=GREY_A, fill_color=NAVY, fill_opacity=1, stroke_width=2)
            body.rotate(yaw.get_value()).move_to(C0)
            nose = Dot(rot((0.17, 0)), radius=0.08, color=YELLOW)
            g.add(body, nose)
            g.add(Arrow(C0, rot((0.11, 0)), buff=0, color=RED, stroke_width=4, max_tip_length_to_length_ratio=0.25))
            g.add(Arrow(C0, rot((0, 0.11)), buff=0, color=GREEN, stroke_width=4, max_tip_length_to_length_ratio=0.25))
            return g

        def side():
            """右侧小图：上半为从机尾看（横滚），下半为从右侧看（俯仰）。倾角取 0.5 rad/(N·m)，只为示意。"""
            g = VGroup()
            for k, (ang, lbl) in enumerate(((0.5 * mx.get_value(), "从机尾看：横滚 φ"), (0.5 * my.get_value(), "从右侧看：俯仰 θ"))):
                c = np.array([4.2, 1.5 - 2.7 * k, 0])
                t = Text(lbl, font=CJK, font_size=20, color=MUTED).move_to(c + UP * 1.0)
                # 从机尾看：y_b 向左，屏幕向左为 +y；横滚 φ > 0 时左侧抬起 → 屏幕上顺时针转
                # 从右侧看：x_b 向右；俯仰 θ > 0 机头向下 → 屏幕上顺时针转
                a = -ang
                u = np.array([math.cos(a), math.sin(a), 0])
                n = np.array([-math.sin(a), math.cos(a), 0])
                ln = Line(c - 1.3 * u, c + 1.3 * u, color=GREY_B, stroke_width=6)
                bars = VGroup(*[Line(c + sx * 1.3 * u + 0.12 * n - 0.45 * u, c + sx * 1.3 * u + 0.12 * n + 0.45 * u,
                                     color=GREY_A, stroke_width=4) for sx in (-1, 1)])
                zb = Arrow(c, c + 0.9 * n, buff=0, color=BLUE, stroke_width=4)
                hz = DashedLine(c - 1.5 * RIGHT, c + 1.5 * RIGHT, color=GREY_D, stroke_width=1.5)
                tag = Text("左" if k == 0 else "机头", font=CJK, font_size=18, color=YELLOW).move_to(c + (-1.75 if k == 0 else 1.8) * u)
                g.add(t, hz, ln, bars, zb, tag)
            return g

        d = always_redraw(drone)
        sd = always_redraw(side)
        self.play(FadeIn(d), FadeIn(sd), run_time=1.0)
        self.caption("悬停：四个推力都是 mg/4 ≈ 3.25 N，两个逆时针、两个顺时针旋翼的反扭矩相互抵消",
                     "Hover: each thrust is mg/4 ≈ 3.25 N; the reaction torques of the two pairs cancel", wait=1.5)
        self.caption("总推力：四个一起增大，机身上升；一起减小，机身下降",
                     "Collective: all four up and the body climbs; all down and it descends", wait=0)
        self.play(fz.animate.set_value(4 * F0 + 2.0), run_time=1.5)
        self.play(fz.animate.set_value(4 * F0), run_time=1.0)
        self.caption("横滚：左边 2、3 增，右边 1、4 减，m_x > 0，左侧抬起",
                     "Roll: left 2, 3 up, right 1, 4 down; m_x > 0 lifts the left side", wait=0)
        self.play(mx.animate.set_value(0.8), run_time=1.8)
        self.wait(0.6)
        self.play(mx.animate.set_value(0.0), run_time=1.0)
        self.caption("俯仰：后面 1、2 增，前面 3、4 减，m_y > 0，机头向下",
                     "Pitch: rear 1, 2 up, front 3, 4 down; m_y > 0 tips the nose down", wait=0)
        self.play(my.animate.set_value(0.8), run_time=1.8)
        self.wait(0.6)
        self.play(my.animate.set_value(0.0), run_time=1.0)
        self.caption("偏航：顺时针转的 2、4 增，逆时针转的 1、3 减，反扭矩不再抵消，机身逆时针转",
                     "Yaw: clockwise rotors 2, 4 up, counter-clockwise 1, 3 down; the body turns counter-clockwise", wait=0)
        self.play(mz.animate.set_value(0.06), run_time=1.0)
        self.play(yaw.animate.set_value(math.radians(35)), run_time=3.0, rate_func=linear)
        self.play(mz.animate.set_value(0.0), run_time=0.8)
        self.caption("同样 0.1 N·m 的力矩，偏航要改变的推力约是横滚的 9 倍：偏航是最弱的通道",
                     "For the same 0.1 N·m, yaw needs about 9 times the thrust change of roll: yaw is the weakest channel", wait=2.0)
        self.card([["推力分配矩阵：四行两两正交，四个通道互不干扰", "Allocation matrix: orthogonal rows, independent channels"],
                   MathTex(r"\begin{pmatrix} f \\ m_x \\ m_y \\ m_z \end{pmatrix} = "
                           r"\begin{pmatrix} 1 & 1 & 1 & 1 \\ -l_y & l_y & l_y & -l_y \\ l_x & l_x & -l_x & -l_x \\ "
                           r"-c_\tau & c_\tau & -c_\tau & c_\tau \end{pmatrix}"
                           r"\begin{pmatrix} f_1 \\ f_2 \\ f_3 \\ f_4 \end{pmatrix}", font_size=40),
                   ["四个推力都沿 z_b：机身受到的力永远沿 z_b", "All four thrusts lie along z_b, and so does the total force"]])
