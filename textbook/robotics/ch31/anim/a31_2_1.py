"""动画 31.2.1（配图 31.2.1）：小转角乘力臂。
(1) WQ-CR5 伸直，抓起 5 kg：J2 的谐波减速器扭一个小角度（2.2 角分，画面放大 300 倍），整条手臂跟着转，TCP 下沉 0.54 mm = 转角 × 0.86 m。
(2) 再加上 J3（0.33 mm）、腕部（0.06 mm）、大臂弯曲（0.16 mm）、小臂弯曲（0.05 mm）：右边的条一段段叠成 1.16 mm（关节按 K1，程序 31.2.1）。
(3) 手臂收回：同样的力，J2 到 TCP 的力臂短了，转角小、乘的力臂也小：竖直刚度从 52 N/mm 升到 209 N/mm。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("31.2", "小转角乘力臂", "Small angle times lever arm")
        s = 8.0
        o = np.array([-6.0, 1.6, 0])
        ang = ValueTracker(0.0)                   # J2 的转角（画面放大后的弧度）

        def arm():
            a = -ang.get_value()
            R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
            P = lambda x, y=0.0: o + R @ np.array([s * x, s * y, 0])      # noqa: E731
            g = VGroup(Line(P(0), P(0.40), color=STEEL, stroke_width=16), Line(P(0.40), P(0.76), color=GREEN, stroke_width=12),
                       Line(P(0.76), P(0.86), color=ORANGE, stroke_width=10), Line(P(0.86), P(0.86, -0.19), color=WHITE, stroke_width=4),
                       Square(side_length=0.4, color=YELLOW, fill_opacity=0.7).move_to(P(0.86, -0.22)),
                       Circle(radius=0.3, color=BLUE, fill_opacity=0.9).move_to(P(0)), Circle(radius=0.24, color=BLUE, fill_opacity=0.9).move_to(P(0.40)))
            return g
        ghost = VGroup(Line(o, o + RIGHT * s * 0.86, color=GREY_B, stroke_width=3), Line(o + RIGHT * s * 0.86, o + RIGHT * s * 0.86 + DOWN * s * 0.19, color=GREY_B, stroke_width=2))
        A = always_redraw(arm)
        self.add(ghost, A)
        self.caption("抓起 5 kg：负载对 J2 的力矩 5 × 9.81 × 0.86 = 42.2 N·m", "Picking up 5 kg puts 5 × 9.81 × 0.86 = 42.2 N·m on J2", wait=1.0)
        arc = always_redraw(lambda: Arc(radius=1.4, start_angle=0, angle=-max(ang.get_value(), 0.001), arc_center=o, color=RED, stroke_width=4))
        self.add(arc)
        self.play(ang.animate.set_value(0.19), run_time=2.0)
        t1 = VGroup(zh("J2 的减速器（32 号，K1 = 6.7×10⁴ N·m/rad）扭 2.2 角分", 22, RED),
                    zh("TCP 下沉 = 转角 × 0.86 m = 0.54 mm（画面放大 300 倍）", 22, YELLOW)).arrange(DOWN, aligned_edge=LEFT).move_to([1.2, -1.2, 0])
        fit(t1, 9.0)
        self.play(FadeIn(t1))
        self.wait(1.0)
        # (2) 叠成总下沉
        parts = [("J2", 0.541, RED), ("J3", 0.335, "#ff9896"), ("腕部", 0.061, PINK), ("大臂弯曲", 0.165, BLUE), ("小臂弯曲", 0.052, TEAL), ("扭转", 0.006, GREY_B)]
        x0, y0, k = 4.6, 2.6, 3.4
        bars = VGroup()
        y = y0
        ylab = y0 + 10.0
        for n, v, c in parts:
            r = Rectangle(width=0.7, height=k * v, color=c, fill_opacity=0.85, stroke_width=1).move_to([x0, y - k * v / 2, 0])
            yl = min(y - k * v / 2, ylab - 0.34)                 # 小的几段标签往下错开，不重叠
            ylab = yl
            t = zh(f"{n} {v:.3f}", 18, c).move_to([x0 + 0.5, yl, 0], aligned_edge=LEFT)
            bars.add(VGroup(r, t))
            y -= k * v
        self.play(FadeOut(t1))
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.1) for b in bars], lag_ratio=0.35), run_time=3.0)
        tot = zh("加 5 kg 后 TCP 又下沉 1.16 mm：关节占 81%", 24, YELLOW).move_to([0.0, -2.0, 0])
        self.play(FadeIn(tot))
        self.caption("大头在关节，尤其是根部的 J2：小转角乘上最长的力臂", "The joints dominate, J2 above all: the smallest angle times the longest lever", wait=1.5)
        self.clear_stage()
        # (3) 收回
        kz = VGroup(zh("伸直：TCP 竖直刚度 52 N/mm", 26, RED), zh("收回到离 J1 轴 0.37 m：209 N/mm", 26, GREEN),
                    zh("力臂进雅可比两次：C_x = J_v C_θ J_vᵀ，刚度按力臂的平方变", 24, INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        fit(kz, 12)
        self.play(LaggedStart(*[FadeIn(m) for m in kz], lag_ratio=0.5), run_time=2.0)
        self.card([["小转角乘力臂", "Small angle times lever arm"],
                   ["每处柔性转 δφ，TCP 移 δφ × (p − c)", "Each compliance turns δφ; the TCP moves δφ × (p − c)"],
                   ["协作臂：减速器是大头，J2 一个占近一半", "A cobot: the gears dominate, J2 alone nearly half"],
                   ["重的、要求准的工序放在离机器人近的地方", "Put heavy and precise work close to the robot"]])
