"""动画 19.2.1（配图 19.2.1）：方向场与解曲线——y′ = x − y 在每一点规定一个斜率，铺成方向场；从几个初值出发顺着
斜率走出积分曲线，它们互不相交，都靠向直线 y = x − 1；最后用步长 1、0.5、0.25 的欧拉折线逼近 y(0) = 2 的积分曲线。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("19.2", "方向场与解曲线", "Direction fields and solution curves")
        ax = Axes(x_range=[-1, 4, 1], y_range=[-2, 4, 1], x_length=7.0, y_length=5.2, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(LEFT * 2.6 + DOWN * 0.3)
        self.play(Create(ax))
        f = lambda x, y: x - y
        segs = VGroup()
        for x in np.linspace(-0.75, 3.75, 13):
            for y in np.linspace(-1.75, 3.75, 15):
                s = f(x, y)
                d = np.array([1.0, s]) / np.sqrt(1 + s * s) * 0.16
                segs.add(Line(ax.c2p(x - d[0], y - d[1]), ax.c2p(x + d[0], y + d[1]), color=GREY_B, stroke_width=2))
        eq = MathTex(r"y'=x-y", font_size=44).to_edge(RIGHT, buff=0.9).shift(UP * 2.2)
        self.play(Write(eq), LaggedStart(*[Create(s) for s in segs], lag_ratio=0.004, run_time=2.5))
        self.caption("方程在每一点规定了积分曲线的斜率：这就是方向场", "The equation prescribes a slope at every point: the direction field", wait=0.6)
        sol = lambda C: (lambda x: x - 1 + C * np.exp(-x))
        curves = VGroup()
        for C, col in ((-3, STEEL), (-1.2, STEEL), (2, GREEN), (5, GREEN)):
            xs = np.linspace(-1, 4, 2001)
            ok = xs[(sol(C)(xs) >= -2) & (sol(C)(xs) <= 4)]
            c = ax.plot(sol(C), x_range=[ok[0], 4], color=col, stroke_width=3)
            curves.add(c)
            dot = Dot(c.get_start(), color=YELLOW)
            self.play(MoveAlongPath(dot, c), Create(c), run_time=1.6, rate_func=linear)
            self.play(FadeOut(dot), run_time=0.2)
        self.caption("顺着斜率走，就画出积分曲线；它们互不相交", "Follow the slopes to trace solution curves; they never cross", wait=0.6)
        line = ax.plot(lambda x: x - 1, x_range=[-1, 4], color=ORANGE, stroke_width=5)
        lt = MathTex(r"y=x-1", font_size=38, color=ORANGE).next_to(eq, DOWN, buff=0.4)
        self.play(Create(line), Write(lt))
        gen = MathTex(r"y=x-1+Ce^{-x}", font_size=38).next_to(lt, DOWN, buff=0.4)
        self.play(Write(gen))
        self.caption("等倾线 y = x − 1 上斜率为 1，它本身就是积分曲线；其他曲线都靠向它", "On the isocline y = x − 1 the slope is 1: it is itself a solution, and all others approach it", wait=0.8)
        self.play(FadeOut(curves), FadeOut(line), FadeOut(lt), segs.animate.set_opacity(0.35))
        exact = ax.plot(sol(3), x_range=[0, 4], color=GREEN, stroke_width=4)
        self.play(Create(exact))
        prev = None
        for h, col in ((1.0, RED), (0.5, ORANGE), (0.25, YELLOW)):
            pts = [(0.0, 2.0)]
            while pts[-1][0] < 4 - 1e-9:
                x, y = pts[-1]
                pts.append((x + h, y + h * f(x, y)))
            poly = VMobject(color=col, stroke_width=3).set_points_as_corners([ax.c2p(x, y) for x, y in pts])
            dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.05, color=col) for x, y in pts])
            ht = MathTex(r"h=%g" % h, font_size=38, color=col).next_to(gen, DOWN, buff=0.5)
            if prev is None:
                self.play(Create(poly), FadeIn(dots), Write(ht), run_time=2)
                self.caption("欧拉法：沿当前点的斜率走一步 h，再按新点的斜率走下一步", "Euler's method: step h along the current slope, then repeat", wait=0.6)
            else:
                self.play(ReplacementTransform(prev[0], poly), ReplacementTransform(prev[1], dots), ReplacementTransform(prev[2], ht), run_time=1.5)
            prev = (poly, dots, ht)
        self.caption("步长越小，折线越贴近积分曲线（19.6 节）", "The smaller the step, the closer the polygon to the curve (Section 19.6)", wait=1.0)
        self.play(*[FadeOut(m) for m in (ax, segs, exact, prev[0], prev[1], prev[2], eq, gen)])
        self.card([["方向场与解曲线", "Direction fields and solution curves"],
                   MathTex(r"y'=f(x,y):\ \text{slope } f(x,y)\text{ at every point}", font_size=40),
                   ["积分曲线处处与方向场相切；在唯一性成立的地方，积分曲线互不相交", "Solution curves are tangent to the field and, where uniqueness holds, never cross"]])
