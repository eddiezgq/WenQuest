"""动画 12.7.1（配图 12.7.1）：斜面上谁先到。实心球、实心圆柱、薄圆筒（看成圆环）从 30° 斜面顶端同时由静止滚下（不打滑），
沿斜面走 2.0 m（与算例 12.7.1 一致）。加速度 a = g sin θ/(1 + J/(MR²))，与质量和半径无关：实心球最先到，圆筒最后到。"""
from manim import *
from wq_anim import *
import numpy as np

G, TH, L = 9.81, np.radians(30), 2.0
OBJS = [("实心球", "solid sphere", 2 / 5, RED, 0.20), ("实心圆柱", "solid cylinder", 1 / 2, BLUE, 0.30), ("薄圆筒", "thin hoop", 1.0, GREEN, 0.25)]   # 最后一项：画面半径，三者不同
S = 2.6                                     # 画面单位 / m
O = np.array([-2.6, 2.3, 0])
U = np.array([np.cos(TH), -np.sin(TH), 0]); N = np.array([np.sin(TH), np.cos(TH), 0])


class Lesson(Base):
    def construct(self):
        self.title("12.7", "斜面上谁先到", "Who reaches the bottom first")
        rails = VGroup()
        for i in range(3):
            off = np.array([0, -0.85 * i, 0])
            rails.add(Line(O + off, O + off + U * L * S, color=GREY_B, stroke_width=3))
        self.play(Create(rails))
        t = ValueTracker(0.0)
        def body(i, k, col, R):
            def make():
                a = G * np.sin(TH) / (1 + k)
                s = min(L, 0.5 * a * t.get_value() ** 2)
                phi = -s * S / R                                                 # 纯滚动：转过的角度 = 画面上走过的路程 / 画面半径（顺时针为负）
                c = O + np.array([0, -0.85 * i, 0]) + U * s * S + N * R
                disk = Circle(radius=R, color=col, fill_opacity=0.35 if k < 1 else 0.0, stroke_width=4)
                mark = Line(c, c + R * np.array([np.cos(phi), np.sin(phi), 0]), color=WHITE, stroke_width=3)
                return VGroup(disk.move_to(c), mark)
            return always_redraw(make)
        names = VGroup()
        for i, (zh_, en_, k, col, R) in enumerate(OBJS):
            self.add(body(i, k, col, R))
            names.add(bi([zh_ + f"  J = {['2/5', '1/2', '1'][i]} MR²", en_], size=18, color=col).next_to(O + np.array([0, -0.85 * i, 0]), LEFT, buff=0.5))
        self.play(FadeIn(names))
        self.caption("三个物体同时从静止滚下，质量、半径都不同", "Three bodies roll from rest together; their masses and radii differ", wait=0)
        T_end = np.sqrt(2 * L / (G * np.sin(TH) / 2))
        self.play(t.animate.set_value(T_end + 0.1), run_time=5, rate_func=linear)
        res = VGroup(*[MathTex(rf"{np.sqrt(2 * L / (G * np.sin(TH) / (1 + k))):.2f}\ \mathrm s", font_size=30, color=col)
                       .next_to(O + np.array([0, -0.85 * i, 0]) + U * L * S, RIGHT, buff=0.6) for i, (_, _, k, col, _) in enumerate(OBJS)])
        self.play(FadeIn(res))
        self.caption("实心球最先到，圆筒最后到：转动惯量占比越大，越多的能量用来转动", "The solid sphere wins and the hoop is last: the bigger J/(MR²), the more energy goes into spinning", wait=2.0)
        self.card([["滚下斜面", "Rolling down an incline"],
                   MathTex(r"a = \frac{g\sin\theta}{1 + J/(MR^2)}", font_size=46),
                   ["与质量、半径无关，只看质量怎样分布", "independent of mass and radius; only the mass distribution matters"],
                   ["实心球 > 实心圆柱 > 圆筒", "solid sphere > solid cylinder > hoop"]])
