"""动画 55.2.1（配图 55.2.1）：车削的残留面积——刀尖圆弧每转前进 f，相邻两转之间留下残留；进给量减半，残留高度降到约四分之一；
刀尖圆弧加大一倍，残留高度减半。高度放大画出，读数按 h = r − √(r² − f²/4)（式 (55.2.1)）的真实值：r = 0.4 mm，f = 0.15、0.075 mm，r = 0.8 mm。"""
from manim import *
from wq_anim import *
import numpy as np

SX, SY = 9.0, 45.0            # 画面放大：进给方向 1 mm = 9 单位，高度 1 mm = 45 单位


def h_real(f, r):
    return r - np.sqrt(r * r - f * f / 4)


class Lesson(Base):
    def construct(self):
        self.title("55.2", "车削的残留面积", "The residual area in turning")
        y0, x0 = -1.2, -5.5
        base = Line(np.array([x0, y0 - 0.6, 0]), np.array([5.5, y0 - 0.6, 0]), color=MUTED)
        self.play(Create(base))

        def scallops(f, r, n, color):
            pts = []
            for k in range(n * 40 + 1):
                x = k * f / 40
                xc = (x % f) - f / 2
                z = r - np.sqrt(r * r - xc * xc)
                pts.append(np.array([x0 + x * SX, y0 + z * SY, 0]))
            return VMobject(color=color, stroke_width=3).set_points_as_corners(pts)

        def nose(c, r, color=ORANGE):
            t = np.linspace(-PI / 2 - 0.5, -PI / 2 + 0.5, 40)
            pts = [np.array([x0 + (c + r * np.cos(a)) * SX, y0 + (r + r * np.sin(a)) * SY, 0]) for a in t]
            return VMobject(color=color, stroke_width=4).set_points_smoothly(pts)

        f, r = 0.15, 0.4
        prof = scallops(f, r, 8, INK)
        tools = [nose(k * f, r) for k in range(8)]
        self.play(Create(tools[0]))
        self.caption("刀尖圆弧（r = 0.4 mm）每转沿进给方向前进 f = 0.15 mm", "The nose (r = 0.4 mm) advances f = 0.15 mm per revolution")
        for k in range(1, 8):
            self.play(Transform(tools[0], tools[k]), run_time=0.35)
        self.play(Create(prof), FadeOut(tools[0]), run_time=1.2)
        rd = zh(f"残留高度 h = {h_real(f, r) * 1000:.1f} µm", 30, YELLOW).move_to(np.array([2.8, 2.0, 0]))
        self.play(FadeIn(rd))
        self.caption("相邻两转之间没有切掉的部分就是残留面积（高度放大约 5 倍）", "What is left between passes is the residual area (heights exaggerated)")
        prof2 = scallops(f / 2, r, 16, GREEN)
        rd2 = zh(f"f 减半：h = {h_real(f / 2, r) * 1000:.2f} µm（约 1/4）", 30, GREEN).move_to(np.array([2.8, 1.3, 0]))
        self.play(Transform(prof, prof2), FadeIn(rd2), run_time=1.5)
        self.caption("进给量减半，残留高度降到约四分之一：h ≈ f²/(8r)", "Halve the feed and h drops to about a quarter: h ≈ f²/(8r)")
        prof3 = scallops(f, 2 * r, 8, STEEL)
        rd3 = zh(f"r 加倍（f 不变）：h = {h_real(f, 2 * r) * 1000:.2f} µm（减半）", 30, STEEL).move_to(np.array([2.8, 0.6, 0]))
        self.play(Transform(prof, prof3), FadeIn(rd3), run_time=1.5)
        self.caption("刀尖圆弧加大一倍，残留高度减半——比减小进给量更不影响效率", "Double the nose radius and h halves — without slowing the cut")
        self.card([["h = r − √(r² − f²/4) ≈ f²/(8r)，Ra ≈ 0.0321 f²/r", "h = r − √(r² − f²/4) ≈ f²/(8r), Ra ≈ 0.0321 f²/r"],
                   ["减小 f、加大 r、用修光刃：残留面积变小", "Smaller f, larger r, a wiper edge: smaller scallops"]])
