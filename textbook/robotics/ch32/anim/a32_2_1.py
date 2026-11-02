"""动画 32.2.1：谐波减速器的工作原理（配 32.2 节）。
刚轮（外圈，固定）42 齿、柔轮（椭圆，内圈）40 齿（实际是 202 / 200，缩小便于看清）；椭圆的波发生器转一圈，
柔轮在长轴两端与刚轮啮合，柔轮反向转过 2 个齿：i = 40 / (42 − 40) = 20（画面）；实际 200 / 2 = 100。"""
from manim import *
from wq_anim import *
import numpy as np

ZC, ZF = 42, 40


class Lesson(Base):
    def construct(self):
        self.title("32.2", "谐波减速器", "The strain wave gear")
        R = 2.2
        o = np.array([-2.2, -0.2, 0])
        wg = ValueTracker(0.0)                   # 波发生器转角

        def ring():
            pts = []
            for k in range(ZC):
                for u, rr in ((0, R + 0.18), (0.25, R), (0.5, R), (0.75, R + 0.18)):
                    a = 2 * np.pi * (k + u) / ZC
                    pts.append(o + [rr * np.cos(a), rr * np.sin(a), 0])
            return Polygon(*pts, color=GREY_B, stroke_width=2)

        def flex():
            th = wg.get_value()
            rot = -th * (ZC - ZF) / ZF            # 柔轮反向
            pts = []
            for k in range(ZF):
                for u, dr in ((0, -0.15), (0.25, 0.0), (0.5, 0.0), (0.75, -0.15)):
                    a = rot + 2 * np.pi * (k + u) / ZF
                    e = 0.12 * np.cos(2 * (a - th))           # 椭圆：长轴沿波发生器
                    rr = R - 0.12 + e + dr
                    pts.append(o + [rr * np.cos(a), rr * np.sin(a), 0])
            mark_a = rot
            mark = Dot(o + [(R - 0.5) * np.cos(mark_a), (R - 0.5) * np.sin(mark_a), 0], color=YELLOW, radius=0.09)
            return VGroup(Polygon(*pts, color=BLUE, stroke_width=2, fill_opacity=0.15), mark)

        def wave():
            th = wg.get_value()
            e = Ellipse(width=2 * (R - 0.45), height=2 * (R - 0.75), color=ORANGE, stroke_width=3).move_to(o).rotate(th)
            return e
        g = VGroup(ring())
        f = always_redraw(flex)
        w = always_redraw(wave)
        self.add(g, f, w, Dot(o))
        labs = VGroup(zh("刚轮（固定）42 齿", 22, GREY_B), zh("柔轮 40 齿（黄点跟着它转）", 22, BLUE), zh("波发生器（椭圆）", 22, ORANGE)).arrange(DOWN, aligned_edge=LEFT).move_to([3.6, 1.6, 0])
        self.play(FadeIn(labs))
        self.play(wg.animate.set_value(2 * np.pi), run_time=6, rate_func=linear)
        self.caption("波发生器转一圈，柔轮反向转过 2 个齿：i = 40/2 = 20（画面）；WQ-CR5 用 200/2 = 100",
                     "One turn of the wave generator moves the flexspline back two teeth: i = 40/2 = 20 here, 200/2 = 100 in WQ-CR5", wait=1.5)
        pts = VGroup(zh("同时啮合的齿多：背隙小、单级大减速比", 24, INK), zh("柔轮反复变形：有疲劳寿命，刚度不高", 24, INK),
                     zh("中空：线缆从中间穿过", 24, INK)).arrange(DOWN, aligned_edge=LEFT).move_to([3.6, -1.3, 0])
        fit(pts, 6.2)
        self.play(LaggedStart(*[FadeIn(p) for p in pts], lag_ratio=0.4), run_time=2)
        self.card([["谐波减速器", "The strain wave gear"],
                   ["i = z_f / (z_c − z_f)：齿差 2，单级减速 100", "i = z_f/(z_c − z_f): two teeth difference, 100 in one stage"],
                   ["寿命：力矩三次方、转速一次方", "Life: torque cubed, speed to the first power"],
                   ["WQ-CR5 的六个关节都用它", "All six joints of WQ-CR5 use it"]])
