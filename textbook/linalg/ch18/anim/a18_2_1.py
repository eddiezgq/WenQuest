"""动画 18.2.1（配图 18.2.1）：A = UΣVᵀ 的三步——Vᵀ 转 −45°，Σ 沿坐标轴伸缩 √45 与 √5 倍，U 转约 71.6°；
最终与 A 直接作用的结果重合。画面按 0.4 倍缩小。"""
from manim import *
from wq_anim import *
import numpy as np
import math


def R(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


class Lesson(Base):
    def construct(self):
        self.title("18.2", "转、伸缩、再转", "Rotate, stretch, rotate")
        A = np.array([[3.0, 0.0], [4.0, 5.0]])
        s1, s2 = math.sqrt(45), math.sqrt(5)
        alpha = math.degrees(math.atan2(3.0, 1.0))          # U = R(α)，α = arctan 3 ≈ 71.57°
        k = 0.42
        O = np.array([0.0, -0.4, 0.0])
        s = ValueTracker(0.0)

        def M():
            x = s.get_value()
            if x <= 1:
                return R(-45 * x)
            if x <= 2:
                u = x - 1
                return np.diag([1 + u * (s1 - 1), 1 + u * (s2 - 1)]) @ R(-45)
            u = x - 2
            return R(alpha * u) @ np.diag([s1, s2]) @ R(-45)

        def P(v):
            w = M() @ np.asarray(v, dtype=float)
            return O + k * np.array([w[0], w[1], 0.0])

        def scene():
            g = VGroup()
            for i in range(-3, 4):
                g.add(Line(P([i, -3]), P([i, 3]), color=GREY_B, stroke_width=1, stroke_opacity=0.4))
                g.add(Line(P([-3, i]), P([3, i]), color=GREY_B, stroke_width=1, stroke_opacity=0.4))
            pts = [P([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 121)]
            g.add(Polygon(*pts[:-1], color=YELLOW, stroke_width=4))
            flag = [[0.25, 0.15], [0.56, 0.15], [0.56, 0.27], [0.44, 0.27], [0.44, 0.36], [0.25, 0.36]]
            g.add(Polygon(*[P(q) for q in flag], color=GOLD, fill_color=GOLD, fill_opacity=0.8, stroke_width=2))
            r2 = 1 / math.sqrt(2)
            g.add(Arrow(O, P([r2, r2]), buff=0, color=RED, stroke_width=6),
                  Arrow(O, P([-r2, r2]), buff=0, color=GREEN, stroke_width=6))
            return g

        sc = always_redraw(scene)
        self.play(FadeIn(sc))
        self.caption("单位圆、一面小旗，以及 v₁（红）、v₂（绿）", "Unit circle, a small flag, v1 (red) and v2 (green)")
        step = bi(["① Vᵀ：转动，把 v₁、v₂ 转到坐标轴上", "① Vᵀ: rotate v1, v2 onto the axes"], 26, WHITE).to_corner(UR, buff=0.5)
        self.play(FadeIn(step))
        self.play(s.animate.set_value(1.0), run_time=2.5)
        self.wait(0.5)
        step2 = bi(["② Σ：沿坐标轴伸缩 √45 倍与 √5 倍", "② Σ: stretch the axes by √45 and √5"], 26, WHITE).move_to(step)
        self.play(FadeOut(step), FadeIn(step2))
        self.play(s.animate.set_value(2.0), run_time=3)
        self.wait(0.5)
        step3 = bi(["③ U：再转动约 71.6°", "③ U: rotate again by about 71.6°"], 26, WHITE).move_to(step2)
        self.play(FadeOut(step2), FadeIn(step3))
        self.play(s.animate.set_value(3.0), run_time=2.5)
        pts = [O + k * np.array([*(A @ [math.cos(a), math.sin(a)]), 0.0]) for a in np.linspace(0, 2 * math.pi, 121)]
        direct = Polygon(*pts[:-1], color=BLUE, stroke_width=8, stroke_opacity=0.6)
        self.caption("蓝色：A 直接作用的结果，与三步的结果完全重合", "Blue: A applied directly — the same ellipse")
        self.play(Create(direct), run_time=1.5)
        self.wait(1)
        self.card([["任何线性变换 = 转 · 伸缩 · 转", "Every linear map = rotate · stretch · rotate"],
                   MathTex(r"A = U\,\Sigma\,V^{\mathsf T}", font_size=56),
                   ["小旗没有被翻面：这里 U、V 都是转动", "The flag is not flipped: U and V are both rotations"]])
