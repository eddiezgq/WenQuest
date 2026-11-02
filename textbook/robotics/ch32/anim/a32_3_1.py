"""动画 32.3.1：RV 减速器（配 32.3 节）。
(1) 第一级：太阳轮（输入）带动两个行星齿轮（装在曲柄轴上），减速 z_pl/z_s。
(2) 第二级：曲柄轴偏心转动，带摆线轮做偏心摆动（不自转一整圈）；摆线轮 11 个齿、针齿 12 个（画面缩小；实际约 40 个），
    曲柄转一圈，摆线轮相对针齿反转一个齿：输出盘慢慢转动。总减速比 i = 1 + (z_pl/z_s)·z_p（式 (32.3.1)）。"""
from manim import *
from wq_anim import *
import numpy as np

ZD = 11


class Lesson(Base):
    def construct(self):
        self.title("32.3", "RV 减速器", "The RV reducer")
        # (1) 第一级
        o1 = np.array([-4.2, 0.0, 0])
        th = ValueTracker(0.0)
        sun = always_redraw(lambda: VGroup(Circle(radius=0.45, color=RED, fill_opacity=0.3).move_to(o1),
                                           Line(o1, o1 + 0.45 * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0]), color=RED)))
        def planets():
            g = VGroup()
            for k in (0, 1):
                c = o1 + np.array([1.35 * np.cos(np.pi * k), 0, 0])
                a = -th.get_value() / 3 + np.pi * k
                g.add(Circle(radius=0.9, color=BLUE, fill_opacity=0.2).move_to(c), Line(c, c + 0.9 * np.array([np.cos(a), np.sin(a), 0]), color=BLUE))
            return g
        pl = always_redraw(planets)
        self.add(sun, pl)
        t1 = VGroup(zh("第一级：太阳轮（输入）", 22, RED), zh("带动行星齿轮 = 曲柄轴（减速 3 倍）", 22, BLUE)).arrange(DOWN, aligned_edge=LEFT).move_to([-4.0, -2.0, 0])
        fit(t1, 5.5)
        self.add(t1)
        # (2) 第二级
        o2 = np.array([2.6, -0.1, 0])
        Rp, e = 2.0, 0.18
        pins = VGroup(*[Circle(radius=0.13, color=GREY_B, fill_opacity=0.6).move_to(o2 + Rp * np.array([np.cos(a), np.sin(a), 0]))
                        for a in np.linspace(0, 2 * np.pi, ZD + 1, endpoint=False)])
        def disc():
            c = th.get_value() / 3                 # 曲柄转角
            ctr = o2 + e * np.array([np.cos(c), np.sin(c), 0])
            rot = -c / ZD                          # 摆线轮相对针齿慢慢反转
            pts = []
            for p in np.linspace(0, 2 * np.pi, 240, endpoint=False):
                r = Rp - 0.32 + 0.16 * np.cos(ZD * (p - rot))
                pts.append(ctr + r * np.array([np.cos(p), np.sin(p), 0]))
            mark = Dot(ctr + 0.9 * np.array([np.cos(rot), np.sin(rot), 0]), color=YELLOW, radius=0.1)
            return VGroup(Polygon(*pts, color=GREEN, stroke_width=2, fill_opacity=0.2), mark, Dot(ctr, color=ORANGE))
        d = always_redraw(disc)
        self.add(pins, d)
        t2 = VGroup(zh("第二级：摆线轮 11 齿、针齿 12 个（画面）", 22, GREEN), zh("曲柄转一圈，摆线轮（黄点）反转一个齿", 22, YELLOW)).arrange(DOWN, aligned_edge=LEFT).move_to([2.6, -2.75, 0])
        fit(t2, 6.0)
        self.add(t2)
        self.play(th.animate.set_value(6 * np.pi), run_time=8, rate_func=linear)
        self.caption("i = 1 + (z_pl/z_s)·z_p：例如 1 + 3 × 40 = 121；几十个针齿同时受力：刚度高、抗冲击",
                     "i = 1 + (z_pl/z_s)·z_p, e.g. 1 + 3 × 40 = 121; dozens of pins share the load: stiff and shock-proof", wait=1.5)
        self.card([["RV 减速器", "The RV reducer"],
                   ["行星 + 摆线针轮两级；背隙主要看最后一级", "Planetary plus cycloid; backlash set by the last stage"],
                   ["几百到几千牛·米：工业机器人的大关节", "Hundreds to thousands of N·m: big industrial joints"],
                   ["同样转矩下比谐波重得多", "Much heavier than a strain wave gear of the same torque"]])
