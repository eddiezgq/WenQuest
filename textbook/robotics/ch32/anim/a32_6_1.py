"""动画 32.6.1（配图 32.6.1）：背隙与重力预紧。
(1) J2 的齿隙放大画：一个齿夹在两个齿之间，有间隙。没有重力（像 J1 那样竖直的轴）、力矩来回换向时，齿在间隙里两边跳，
    手臂末端跟着晃：0.6 角分 × 0.86 m ≈ 0.15 mm（画面放大）。
(2) 加上重力：力矩一直向下，齿一直贴在下侧，来回走末端都停在同一点——重力预紧。
(3) J1 靠单向接近：每次都从同一侧到达目标。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("32.6", "背隙与重力预紧", "Backlash and gravity preload")
        c = np.array([-4.0, 0.3, 0])
        wall_lo = Rectangle(width=1.0, height=0.5, color=GREY_B, fill_opacity=0.6).move_to(c + DOWN * 0.75)
        wall_hi = Rectangle(width=1.0, height=0.5, color=GREY_B, fill_opacity=0.6).move_to(c + UP * 0.75)
        y = ValueTracker(0.0)
        tooth = always_redraw(lambda: Rectangle(width=0.6, height=0.6, color=BLUE, fill_opacity=0.7).move_to(c + UP * y.get_value()))
        self.add(wall_lo, wall_hi, tooth)
        self.add(zh("齿隙（放大）", 22, GREY_B).next_to(wall_hi, UP))
        o = np.array([-1.5, 0.3, 0])
        arm = always_redraw(lambda: Line(o, o + np.array([6.0, 2.0 * y.get_value(), 0]), color=STEEL, stroke_width=10))
        tip = always_redraw(lambda: Dot(o + np.array([6.0, 2.0 * y.get_value(), 0]), color=YELLOW, radius=0.12))
        self.add(arm, tip, Dot(o, radius=0.12))
        self.add(zh("TCP（晃量放大）", 22, YELLOW).move_to(o + np.array([6.0, 1.2, 0])))
        g = 0.2
        for _ in range(3):
            self.play(y.animate.set_value(g), run_time=0.5)
            self.play(y.animate.set_value(-g), run_time=0.5)
        self.caption("力矩来回换向：齿在间隙里两边跳，TCP 晃 0.6′ × 0.86 m ≈ 0.15 mm",
                     "Torque reversing: the tooth jumps across the gap, the TCP wanders 0.6′ × 0.86 m ≈ 0.15 mm", wait=0.5)
        gv = Arrow(o + np.array([3, 1.2, 0]), o + np.array([3, -0.4, 0]), color=C_F, buff=0)
        self.play(GrowArrow(gv), y.animate.set_value(-g), run_time=0.8)
        for _ in range(3):
            self.play(y.animate.set_value(-g + 0.01), run_time=0.4)
            self.play(y.animate.set_value(-g), run_time=0.4)
        self.caption("加上重力：齿一直贴在下侧，来回走 TCP 都停在同一点——重力预紧（J2、J3）",
                     "With gravity the tooth stays on the lower flank and the TCP returns to the same spot: gravity preload (J2, J3)", wait=1.0)
        self.clear_stage()
        o2 = np.array([0, -0.3, 0])
        tgt = Dot(o2, color=YELLOW, radius=0.12)
        self.add(tgt, zh("目标点", 22, YELLOW).next_to(tgt, UP))
        path1 = Arrow(o2 + LEFT * 3, o2 + LEFT * 0.15, color=GREEN, buff=0)
        path2 = Arrow(o2 + RIGHT * 3, o2 + RIGHT * 0.15, color=RED, buff=0)
        path3 = VGroup(Arrow(o2 + RIGHT * 3, o2 + LEFT * 0.8, color=GREEN, buff=0), Arrow(o2 + LEFT * 0.8 + DOWN * 0.25, o2 + LEFT * 0.15 + DOWN * 0.25, color=GREEN, buff=0))
        self.play(GrowArrow(path1), GrowArrow(path2))
        self.caption("J1 的轴竖直，重力帮不上：从两侧来，停的位置差一个背隙", "J1's axis is vertical, gravity can't help: from the two sides it stops a backlash apart", wait=0.8)
        self.play(FadeOut(path2), Create(path3))
        self.caption("单向接近：先越过一点再退回来，每次都从同一侧到达", "Unidirectional approach: overshoot and come back, always arriving from the same side", wait=1.2)
        self.card([["背隙与重力预紧", "Backlash and gravity preload"],
                   ["背隙乘力臂：根部关节半角分就是零点一毫米以上", "Backlash times lever: half an arcmin at the base is over 0.1 mm"],
                   ["重力预紧（J2、J3）、单向接近（J1、腕部）", "Gravity preload (J2, J3), unidirectional approach (J1, wrist)"],
                   ["绝对精度、轨迹精度仍要补偿", "Absolute and path accuracy still need compensation"]])
