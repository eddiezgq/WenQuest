"""动画 18.1.1（配图 18.1.1）：工作空间，串联是“和”，并联是“交”。
左：2R 臂（大臂 0.20 m、小臂 0.30 m）。大臂端点走一个圆，每个位置再加上半径 0.30 m 的圆，叠成圆环。
右：平面五杆（电机在 (∓0.15, 0) m，主动杆 0.20 m、从动杆 0.30 m）。两条支链各扫出一个圆环，末端只能在两者的交集里。
最后两台机器人的末端同时沿 y = 0.30 m 的直线向右走，五杆在 x = 0.25 m 处到达交集的边界。"""
from manim import *
from wq_anim import *
import numpy as np
import math

K = 4.0                                   # 1 m 画成 4 个单位
OL = np.array([-3.6, -0.55, 0.0])         # 左图原点（2R 的基座）
OR = np.array([3.6, -0.55, 0.0])          # 右图原点（五杆两台电机的中点）
L1, L2 = 0.20, 0.30
C5, l1, l2 = 0.15, 0.20, 0.30


def SL(x, y):
    return OL + K * np.array([x, y, 0.0])


def SR(x, y):
    return OR + K * np.array([x, y, 0.0])


def ik2(x, y):
    c2 = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    c2 = max(-1.0, min(1.0, c2))
    t2 = math.acos(c2)
    t1 = math.atan2(y, x) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    return t1, t2


def leg(x, y, ax, sg):
    dx, dy = x - ax, y
    d = math.hypot(dx, dy)
    c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    if abs(c) > 1:
        return None
    return math.atan2(dy, dx) + sg * math.acos(c)


def ring(center, r_in, r_out, color, op):
    return Annulus(inner_radius=K * r_in, outer_radius=K * r_out, color=color, fill_opacity=op, stroke_width=0).move_to(center)


class Lesson(Base):
    def construct(self):
        self.title("18.1", "工作空间：串联是“和”，并联是“交”", "Workspaces: a sum for serial, an intersection for parallel")
        hl = bi(["2R 串联臂", "2R serial arm"], 24, BLUE).move_to(SL(0, 0.62))
        hr = bi(["平面五杆机器人", "planar five-bar"], 24, ORANGE).move_to(SR(0, 0.62))
        self.play(FadeIn(hl), FadeIn(hr))

        # ---------------- 左：和
        base = Dot(SL(0, 0), radius=0.08, color=WHITE)
        c1 = Circle(radius=K * L1, color=BLUE_B, stroke_width=2).move_to(SL(0, 0))
        self.add(base)
        self.caption("串联：大臂端点走一个半径 0.20 m 的圆", "Serial: the end of the upper arm runs round a circle of radius 0.20 m", wait=0)
        self.play(Create(c1), run_time=1.0)
        a = ValueTracker(0.0)
        circles = VGroup()

        def arm():
            t = a.get_value()
            e = SL(L1 * math.cos(t), L1 * math.sin(t))
            return VGroup(Line(SL(0, 0), e, color=BLUE, stroke_width=8), Dot(e, radius=0.07, color=WHITE),
                          Circle(radius=K * L2, color=BLUE_D, stroke_width=2).move_to(e))

        g = always_redraw(arm)
        self.add(g)
        self.caption("每个位置再加上小臂的圆：两者的“和”（闵可夫斯基和）", "add the forearm's circle at every position: their (Minkowski) sum", wait=0)
        for k in range(12):
            t = 2 * math.pi * (k + 1) / 12
            self.play(a.animate.set_value(t), run_time=0.22, rate_func=linear)
            e = SL(L1 * math.cos(t), L1 * math.sin(t))
            circles.add(Circle(radius=K * L2, color=BLUE_E, stroke_width=1, stroke_opacity=0.6).move_to(e))
            self.add(circles)
        annL = ring(SL(0, 0), L2 - L1, L1 + L2, BLUE, 0.35)
        self.play(FadeIn(annL), FadeOut(circles), FadeOut(g), run_time=0.8)
        self.caption("结果是内半径 0.1 m、外半径 0.5 m 的圆环", "The result is a ring from 0.1 m to 0.5 m", wait=0.6)

        # ---------------- 右：交
        A1, A2 = SR(-C5, 0), SR(C5, 0)
        m1, m2 = Square(0.16, color=ORANGE, fill_opacity=1).move_to(A1), Square(0.16, color=ORANGE, fill_opacity=1).move_to(A2)
        self.add(m1, m2)
        r1 = ring(A1, l2 - l1, l1 + l2, YELLOW, 0.18)
        r2 = ring(A2, l2 - l1, l1 + l2, TEAL, 0.18)
        self.caption("并联：每条支链单独能到的范围，是以各自电机为圆心的圆环", "Parallel: each leg alone reaches a ring about its own motor", wait=0)
        self.play(FadeIn(r1), run_time=0.8)
        self.play(FadeIn(r2), run_time=0.8)
        inter = Intersection(r1, r2, color=ORANGE, fill_opacity=0.35, stroke_width=0)
        self.caption("末端必须同时满足两条支链：工作空间是两者的“交”", "The end point must suit both legs: the workspace is the intersection", wait=0)
        self.play(FadeIn(inter), r1.animate.set_fill(opacity=0.06), r2.animate.set_fill(opacity=0.06), run_time=1.2)
        self.wait(0.6)

        # ---------------- 沿直线 y = 0.30 m 向右走
        x = ValueTracker(-0.2)
        yline = 0.30
        path_l = DashedLine(SL(-0.45, yline), SL(0.45, yline), color=GREY_B, stroke_width=2)
        path_r = DashedLine(SR(-0.45, yline), SR(0.45, yline), color=GREY_B, stroke_width=2)
        self.play(Create(path_l), Create(path_r), run_time=0.6)

        def both():
            xv = x.get_value()
            t1, t2 = ik2(xv, yline)
            e = SL(L1 * math.cos(t1), L1 * math.sin(t1))
            w = SL(xv, yline)
            left = VGroup(Line(SL(0, 0), e, color=BLUE, stroke_width=8), Line(e, w, color=BLUE, stroke_width=6),
                          Dot(SL(0, 0), radius=0.07, color=WHITE), Dot(e, radius=0.07, color=WHITE), Dot(w, radius=0.08, color=RED))
            xr = min(xv, 0.2499)
            g1, g2 = leg(xr, yline, -C5, 1), leg(xr, yline, C5, -1)
            right = VGroup()
            if g1 is not None and g2 is not None:
                b1 = SR(-C5 + l1 * math.cos(g1), l1 * math.sin(g1))
                b2 = SR(C5 + l1 * math.cos(g2), l1 * math.sin(g2))
                p = SR(xr, yline)
                right = VGroup(Line(A1, b1, color=YELLOW, stroke_width=8), Line(A2, b2, color=YELLOW, stroke_width=8),
                               Line(b1, p, color=YELLOW, stroke_width=5), Line(b2, p, color=YELLOW, stroke_width=5),
                               Dot(b1, radius=0.07, color=WHITE), Dot(b2, radius=0.07, color=WHITE), Dot(p, radius=0.08, color=RED))
            return VGroup(left, right)

        gg = always_redraw(both)
        self.add(gg)
        self.caption("两个末端同时沿 y = 0.30 m 向右走", "Both end points move right along y = 0.30 m", wait=0)
        self.play(x.animate.set_value(0.25), run_time=3.0, rate_func=linear)
        mark = Cross(scale_factor=0.18, stroke_color=RED).move_to(SR(0.25, yline) + RIGHT * 0.35)
        self.caption("五杆在 x = 0.25 m 处到达交集的边界：左边的支链已经伸直", "The five-bar stops at x = 0.25 m: its left leg is fully stretched", wait=0)
        self.play(FadeIn(mark), x.animate.set_value(0.40), run_time=2.0, rate_func=linear)
        self.wait(0.8)
        self.card([["串联：工作空间是各段运动的“和”", "Serial: the workspace is the sum of the segments"],
                   ["并联：工作空间是各支链工作空间的“交”", "Parallel: it is the intersection of the legs' workspaces"],
                   MathTex(r"W = W_1 \cap W_2 \cap \cdots \cap W_k", font_size=44)])
