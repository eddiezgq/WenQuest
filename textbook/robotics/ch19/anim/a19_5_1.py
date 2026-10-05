"""动画 19.5.1（配图 19.5.3）：随机误差的累积。
差速 AGV（轮距 0.26 m）直行 4 m。80 辆“幽灵车”与真车同时出发，每一步两个车轮滚过的距离各有方差 k·Δs 的随机误差
（为了看清，k 取 2×10⁻⁴ m，比算例 19.5.5 大 200 倍）。幽灵车越走越散，散成两端后弯的香蕉形，横向远大于纵向；
到达地面二维码时，位置被重新测定，车群收拢到一点。"""
from manim import *
from wq_anim import *
import numpy as np
import math

B_W = 0.26
K = 2e-4
D = 4.0
N = 400
M = 80
rng = np.random.default_rng(195)
ds = D / N
Q = np.zeros((N + 1, M, 3))
for i in range(N):
    nR = rng.normal(0, math.sqrt(K * ds), M)
    nL = rng.normal(0, math.sqrt(K * ds), M)
    dsR, dsL = ds + nR, ds + nL
    dsm, dph = (dsR + dsL) / 2, (dsR - dsL) / B_W
    q = Q[i].copy()
    q[:, 0] += dsm * np.cos(q[:, 2] + dph / 2)
    q[:, 1] += dsm * np.sin(q[:, 2] + dph / 2)
    q[:, 2] += dph
    Q[i + 1] = q
SX, SY = 2.55, 3.0                      # 纵向 1 m 画成 2.55 个单位，横向 3 个单位
O = np.array([-5.4, 0.2, 0])


def P(x, y):
    return O + np.array([x * SX, y * SY, 0])


class Lesson(Base):
    def construct(self):
        self.title("19.5", "里程计的随机误差", "Random errors of odometry")
        road = Line(P(-0.1, 0), P(D + 0.2, 0), color=GREY_C, stroke_width=2)
        qr = Square(0.45, color=WHITE, fill_color=WHITE, fill_opacity=0.9).move_to(P(D, 0))
        qr_in = VGroup(*[Square(0.1, color=BLACK, fill_color=BLACK, fill_opacity=1).move_to(P(D, 0) + np.array([dx, dy, 0]))
                         for dx, dy in ((-0.12, 0.12), (0.12, 0.12), (-0.12, -0.12), (0.05, -0.05))])
        self.play(Create(road), FadeIn(qr), FadeIn(qr_in), run_time=0.8)
        self.caption("80 辆“幽灵车”与真车一起出发，每一步车轮都有随机的打滑（为看清，比算例 19.5.5 放大 200 倍）",
                     "80 ghost AGVs start with the real one; each wheel slips at random (200 times Example 19.5.5, to be visible)", wait=0.5)
        k = ValueTracker(0)

        def ghosts():
            i = int(k.get_value())
            pts = Q[i]
            g = VGroup(*[Dot(P(p[0], p[1]), radius=0.04, color=STEEL, fill_opacity=0.7) for p in pts])
            car = Rectangle(width=0.5, height=0.3, color=ORANGE, fill_color=ORANGE, fill_opacity=0.9).move_to(P(i * ds, 0))
            return VGroup(g, car)

        def stats():
            i = int(k.get_value())
            pts = Q[i]
            sx, sy = pts[:, 0].std() * 1000, pts[:, 1].std() * 1000
            return VGroup(MathTex(r"D = %.1f\ \mathrm{m}" % (i * ds), font_size=32),
                          MathTex(r"\sigma_x = %.0f\ \mathrm{mm}" % sx, font_size=32, color=GREEN),
                          MathTex(r"\sigma_y = %.0f\ \mathrm{mm}" % sy, font_size=32, color=STEEL)).arrange(DOWN, aligned_edge=LEFT).move_to([-4.8, -1.6, 0])

        gh = always_redraw(ghosts)
        st = always_redraw(stats)
        self.add(gh, st)
        self.caption("航向误差不断累积，又被行驶距离放大成横向误差：横向远大于纵向",
                     "Heading errors pile up and distance turns them into cross-track error, far larger than along-track", wait=0)
        self.play(k.animate.set_value(N), run_time=8, rate_func=linear)
        ban = MathTex(r"\sigma_y \propto D^{3/2},\quad \sigma_x \propto D^{1/2}", font_size=36).move_to([-1.5, 2.3, 0])
        self.play(Write(ban), run_time=0.8)
        self.caption("车群散成两端向后弯的“香蕉”：偏得多的车，前进得也少",
                     "The cloud bends into a banana: the cars that veer most also get least far", wait=1.0)
        # 看到二维码：位置被重新测定
        final = Q[N]
        dots = VGroup(*[Dot(P(p[0], p[1]), radius=0.04, color=STEEL) for p in final])
        self.add(dots)
        self.play(FadeOut(gh), FadeOut(st), run_time=0.3)
        car = Rectangle(width=0.5, height=0.3, color=ORANGE, fill_color=ORANGE, fill_opacity=0.9).move_to(P(D, 0))
        self.add(car)
        self.caption("车底相机看到二维码：位置被重新测定，车群收拢到一点",
                     "The floor camera sees a code: the position is measured again and the cloud collapses", wait=0)
        self.play(*[d.animate.move_to(P(D, 0)) for d in dots], run_time=1.5)
        self.wait(0.8)
        self.card([["里程计只在短距离内可靠", "Odometry is reliable only over short distances"],
                   MathTex(r"\sigma_y^2 = \frac{2kD^3}{3b^2}", font_size=46),
                   ["定位标志的间距由允许的横向误差反推", "Space the landmarks by the cross-track error you can accept"]])
