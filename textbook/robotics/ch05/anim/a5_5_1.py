"""动画 5.5.1（配图 5.5.1）：侧视示意。相机看到工件，坐标链的两条路径依次亮起，在抓取点闭合；机械臂先到预抓取位姿，再沿接近方向下降。"""
from manim import *
from wq_anim import *
import numpy as np
import math

U = 5.2
W = np.array([-4.6, -2.2, 0])             # 工作台坐标系 {w} 的原点（台面左前角，侧视）
L1, L2, L3 = 0.425, 0.392, 0.25           # 大臂、小臂、手腕到指尖（法兰 0.1 m + 夹爪 0.15 m）
SH = np.array([0.30, 0.163])              # 肩关节（基座在 x = 0.30 m 处，肩高 0.163 m）


def scr(x, z):
    return W + U * np.array([x, z, 0])


def ik(tip):
    """平面三连杆：最后一段竖直向下，指尖到 tip。返回三个相对角（度）。"""
    wr = np.array([tip[0], tip[1] + L3]) - SH
    d = np.linalg.norm(wr)
    c2 = (d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    q2 = -math.acos(max(-1.0, min(1.0, c2)))                     # 肘部在上
    q1 = math.atan2(wr[1], wr[0]) - math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
    q3 = -math.pi / 2 - q1 - q2
    return [math.degrees(q1), math.degrees(q2), math.degrees(q3)]


class Lesson(Base):
    def construct(self):
        self.title("5.5", "相机-机械臂-工件的坐标链", "The camera-arm-part chain")
        table = Line(scr(-0.05, 0), scr(1.25, 0), color=GREY_B, stroke_width=5)
        stand = VGroup(Line(scr(1.17, 0), scr(1.17, 0.98), color=GREY_B, stroke_width=5),
                       Line(scr(1.17, 0.98), scr(1.05, 0.98), color=GREY_B, stroke_width=5))
        cam = Square(0.3, color=WHITE, fill_color=GREY_D, fill_opacity=1).move_to(scr(1.05, 0.9))
        tray = Rectangle(width=0.2 * U, height=0.02 * U, color=GOLD, fill_color="#5a3d0a", fill_opacity=1).move_to(scr(0.80, 0.01))
        part = Rectangle(width=0.08 * U, height=0.03 * U, color=YELLOW, fill_color="#8a6d2b", fill_opacity=1).move_to(scr(0.80, 0.035))
        base = Polygon(scr(0.24, 0), scr(0.36, 0), scr(0.33, 0.1), scr(0.27, 0.1), color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        tip = ValueTracker(0.0)
        pts = [np.array([0.62, 0.30]), np.array([0.80, 0.085]), np.array([0.80, 0.035])]

        def pose():
            s = tip.get_value()
            k = min(int(s), 1)
            f = s - k
            return pts[k] * (1 - f) + pts[k + 1] * f

        arm_m = always_redraw(lambda: planar_arm(scr(*SH), ik(pose()), [L1 * U, L2 * U, L3 * U], color=STEEL))
        fw = frame2(scr(0, 0), 0, 0.8, ("x_w", "z_w"), name=r"\{w\}")
        self.play(Create(table), FadeIn(stand), FadeIn(cam), FadeIn(tray), FadeIn(part), FadeIn(base), FadeIn(arm_m), Create(fw))
        self.caption("工作台、机器人、相机和料盘里的齿轮坯（侧视）", "Worktable, robot, camera and the gear blank in its tray (side view)")

        g = scr(0.80, 0.035)
        ray = DashedLine(cam.get_center(), g, color=YELLOW)
        self.play(Create(ray))
        self.caption("相机报告工件相对相机的位姿", "The camera reports the part's pose relative to itself", wait=1.0)

        def link(a, b, color, label, d):
            ar = Arrow(a, b, buff=0.08, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.08)
            lb = MathTex(label, color=color, font_size=34).next_to(ar.get_center(), d, buff=0.12)
            return VGroup(ar, lb)

        red = VGroup(link(scr(0, 0), cam.get_center(), RED, r"T_{wc}", UL),
                     link(cam.get_center(), g, RED, r"T_{co}T_{og}", RIGHT))
        blue = VGroup(link(scr(0, 0), scr(0.30, 0), BLUE, r"T_{ws}", DOWN),
                      link(scr(0.30, 0), g + UP * 0.1, BLUE, r"T_{sb}(\theta)\,T_{bt}", UP))
        blue[1][1].move_to(scr(0.56, 0.16))
        self.play(FadeOut(ray), LaggedStart(*[FadeIn(m) for m in red], lag_ratio=0.5), run_time=1.5)
        self.caption("相机一侧：工作台 → 相机 → 工件 → 抓取点", "Camera side: table → camera → part → grasp point", wait=1.0)
        self.play(LaggedStart(*[FadeIn(m) for m in blue], lag_ratio=0.5), run_time=2)
        self.caption("机器人一侧：工作台 → 基座 → 法兰 → 工具；两条路径必须在抓取点相遇", "Robot side: table → base → flange → tool; both paths must meet at the grasp point")
        eq = MathTex(r"T_{ws}\,T_{sb}\,T_{bt} = T_{wc}\,T_{co}\,T_{og}", font_size=38).to_corner(UR, buff=0.5).shift(DOWN * 0.9)
        sol = MathTex(r"T_{sb}^{*} = T_{sw}\,T_{wc}\,T_{co}\,T_{og}\,T_{tb}", font_size=38, color=YELLOW).next_to(eq, DOWN, buff=0.3)
        self.play(Write(eq))
        self.play(Write(sol))
        self.play(FadeOut(red), FadeOut(blue))
        self.caption("先到工件上方 50 mm 的预抓取位姿", "First to the pre-grasp pose, 50 mm above the part", wait=0)
        self.play(tip.animate.set_value(1.0), run_time=2, rate_func=smooth)
        self.caption("再沿夹爪的接近方向竖直下降，夹住齿轮坯", "Then straight down along the approach direction to grip", wait=0)
        self.play(tip.animate.set_value(2.0), run_time=1.5, rate_func=smooth)
        self.wait(1)
        self.card([["闭合方程", "The closure equation"],
                   MathTex(r"T_{ws}\,T_{sb}(\theta)\,T_{bt} = T_{wc}\,T_{co}\,T_{og}", font_size=42),
                   ["两条路径到达同一个坐标系，位姿必须相等", "two paths to the same frame must give the same pose"]])
