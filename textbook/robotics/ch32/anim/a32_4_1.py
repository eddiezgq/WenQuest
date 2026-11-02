"""动画 32.4.1：行星减速器（配 32.4 节）。太阳轮 20 齿、内齿圈 70 齿、3 个行星轮 25 齿。
(1) 内齿圈固定：太阳轮转 4.5 圈，行星架转 1 圈（同向）；行星轮在内齿圈里滚动，自转 −1.8 倍于行星架。
(2) 行星架固定：成了定轴齿轮，内齿圈反向，i = −3.5。"""
from manim import *
from wq_anim import *
import numpy as np

ZS, ZR, ZP = 20, 70, 25
K = 0.036                                  # 画面：每齿 0.036 → 半径 = z·K


class Lesson(Base):
    def construct(self):
        self.title("32.4", "行星减速器", "The planetary gearbox")
        o = np.array([-2.6, -0.2, 0])
        rs, rp, rr = ZS * K, ZP * K, ZR * K
        sun_a, car_a, ring_a = ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)

        def draw():
            s, c, r = sun_a.get_value(), car_a.get_value(), ring_a.get_value()
            g = VGroup(Circle(radius=rr + 0.12, color=GREY_B, stroke_width=6).move_to(o),
                       Line(o + rr * np.array([np.cos(r), np.sin(r), 0]), o + (rr + 0.3) * np.array([np.cos(r), np.sin(r), 0]), color=GREY_B, stroke_width=6),
                       Circle(radius=rs, color=RED, fill_opacity=0.3).move_to(o),
                       Line(o, o + rs * np.array([np.cos(s), np.sin(s), 0]), color=RED, stroke_width=4))
            arm = VGroup()
            for k in range(3):
                a = c + 2 * np.pi * k / 3
                pc = o + (rs + rp) * np.array([np.cos(a), np.sin(a), 0])
                # 行星轮自转：相对行星架 (n_s − n_c)·(−z_s/z_p)，再加上行星架的转角
                psi = c - (s - c) * ZS / ZP
                g.add(Circle(radius=rp, color=BLUE, fill_opacity=0.2).move_to(pc), Line(pc, pc + rp * np.array([np.cos(psi), np.sin(psi), 0]), color=BLUE))
                arm.add(Line(o, pc, color=ORANGE, stroke_width=5))
            return VGroup(arm, g)
        m = always_redraw(draw)
        self.add(m)
        lab = VGroup(zh("太阳轮 20 齿（红）", 22, RED), zh("行星轮 25 齿 × 3（蓝）", 22, BLUE), zh("行星架（橙）", 22, ORANGE),
                     zh("内齿圈 70 齿（灰）", 22, GREY_B)).arrange(DOWN, aligned_edge=LEFT).move_to([4.0, 1.5, 0])
        self.add(lab)
        t = zh("内齿圈固定：i = 1 + 70/20 = 4.5", 26, YELLOW).move_to([4.0, -0.6, 0])
        self.play(FadeIn(t))
        self.play(sun_a.animate.set_value(4.5 * 2 * np.pi), car_a.animate.set_value(2 * np.pi), run_time=7, rate_func=linear)
        self.caption("太阳轮转 4.5 圈，行星架同向转 1 圈；三个行星轮分担转矩，所以小而有力",
                     "The sun turns 4.5 times, the carrier once the same way; three planets share the torque", wait=1.0)
        t2 = zh("行星架固定：i = −70/20 = −3.5（内齿圈反向）", 26, YELLOW).move_to([3.7, -0.6, 0])
        fit(t2, 6.0)
        self.play(FadeOut(t), FadeIn(t2))
        s0, c0 = sun_a.get_value(), car_a.get_value()
        self.play(sun_a.animate.set_value(s0 + 3.5 * 2 * np.pi), ring_a.animate.set_value(-2 * np.pi), run_time=6, rate_func=linear)
        self.caption("固定哪一个、哪个输入、哪个输出，传动比不同：威利斯式 (n_s − n_c)/(n_r − n_c) = −z_r/z_s",
                     "Which member is fixed sets the ratio: Willis, (n_s − n_c)/(n_r − n_c) = −z_r/z_s", wait=1.5)
        self.card([["行星减速器", "The planetary gearbox"],
                   ["效率高（一级约 98%）、同轴、能反推", "Efficient (about 98 % per stage), coaxial, back-drivable"],
                   ["回程间隙几角分：适合车轮、直线轴，不进协作臂的关节", "Several arcmin of backlash: wheels and linear axes, not cobot joints"]])
