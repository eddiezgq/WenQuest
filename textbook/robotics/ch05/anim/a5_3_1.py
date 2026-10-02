"""动画 5.3.1（配图 5.3.1）：两只夹爪从同一位姿 T 出发，分别执行右乘 T·Rot(z, 90°) 与左乘 Rot(z, 90°)·T。"""
from manim import *
from wq_anim import *
import numpy as np
import math

U = 1.7
OS = np.array([-1.2, -1.7, 0])            # 基座坐标系 {s} 的原点
X0, Y0, A0 = 1.5, 0.9, 30.0               # 起始位姿 T（m、度），与图 5.3.1 相同


def scr(x, y):
    return OS + U * np.array([x, y, 0])


def gripper(x, y, deg, color):
    """平面夹爪：手掌在原点，两指沿自身 x 轴伸出；再画一支 x 轴箭头。"""
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    R = lambda p: scr(x + c * p[0] - s * p[1], y + s * p[0] + c * p[1])
    g = VGroup(Line(R((0, -0.18)), R((0, 0.18)), color=color, stroke_width=7),
               Line(R((0, 0.18)), R((0.27, 0.18)), color=color, stroke_width=7),
               Line(R((0, -0.18)), R((0.27, -0.18)), color=color, stroke_width=7),
               Arrow(R((0, 0)), R((0.55, 0)), buff=0, color=color, stroke_width=4),
               Dot(R((0, 0)), color=color, radius=0.06))
    return g


class Lesson(Base):
    def construct(self):
        self.title("5.3", "左乘与右乘", "Left- and right-multiplication")
        fs = frame2(OS, 0, 1.0, ("x_s", "y_s"), name=r"\{s\}")
        start = gripper(X0, Y0, A0, GREY_B)
        lab0 = MathTex("T", color=GREY_B, font_size=34).next_to(start, DOWN, buff=0.15)
        self.play(Create(fs), FadeIn(start), Write(lab0))
        self.caption("两只夹爪从同一个位姿 T 出发，都转 90°", "Two grippers start at the same pose T; both turn 90°")

        phi = ValueTracker(0.0)

        def right():
            return gripper(X0, Y0, A0 + phi.get_value(), GOLD)

        def left():
            t = math.radians(phi.get_value())
            c, s = math.cos(t), math.sin(t)
            return gripper(c * X0 - s * Y0, s * X0 + c * Y0, A0 + phi.get_value(), BLUE)

        gR, gL = always_redraw(right), always_redraw(left)
        r = math.hypot(X0, Y0)
        a0 = math.atan2(Y0, X0)
        trace = always_redraw(lambda: Arc(radius=U * r, start_angle=a0, angle=math.radians(phi.get_value()) + 1e-6,
                                          arc_center=OS, color=BLUE, stroke_width=3).set_stroke(opacity=0.7))
        tR = MathTex(r"T\,\mathrm{Rot}(z, 90^\circ)", color=GOLD, font_size=34).to_corner(UR, buff=0.6).shift(DOWN * 0.9)
        tL = MathTex(r"\mathrm{Rot}(z, 90^\circ)\,T", color=BLUE, font_size=34).next_to(tR, DOWN, buff=0.3, aligned_edge=LEFT)
        self.add(trace, gR, gL)
        self.play(Write(tR), Write(tL))
        self.caption("金色：右乘，绕夹爪自己的原点转；蓝色：左乘，绕基座 {s} 的原点转", "Gold: right, about the gripper's own origin; blue: left, about the origin of {s}", wait=0)
        self.play(phi.animate.set_value(90.0), run_time=4, rate_func=smooth)
        self.wait(0.8)
        chord = DashedLine(scr(X0, Y0), scr(-Y0, X0), color=RED)
        d = MathTex(r"\sqrt{2}\,r", color=RED, font_size=34).next_to(chord.get_center(), UP, buff=0.15)
        self.play(Create(chord), Write(d))
        self.caption("左乘的转动把夹爪甩出一段弦长：√2 乘以它到 z_s 轴的距离", "The left turn flings the gripper by √2 times its distance from the z_s axis")
        self.wait(1)
        self.card([["左乘相对固定坐标系，右乘相对自身", "Left: relative to the fixed frame; right: relative to the body"],
                   MathTex(r"T_{sb'} = D\,T_{sb} \quad\text{or}\quad T_{sb'} = T_{sb}\,D", font_size=42),
                   ["转动不但有方向，还有转动中心", "a rotation has a direction and also a centre"]])
