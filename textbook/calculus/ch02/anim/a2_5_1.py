"""动画 2.5.1（配图 2.5.1）：函数图像的平移与伸缩。抛物线 f(x) = x² 先左右、上下平移，再横向、纵向伸缩；
最后用 sin x 走一遍算例 2.5.1 的四步，得到 3 sin(2x − π/3) + 1。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.5", "平移与伸缩", "Shifting and scaling")
        ax = Axes(x_range=[-4, 4, 1], y_range=[-2, 5, 1], x_length=8, y_length=5.2, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(LEFT * 1.6 + DOWN * 0.3)
        self.play(Create(ax), run_time=1)
        base = ax.plot(lambda x: x * x, x_range=[-2.3, 2.3], color=GREY_B, stroke_width=3)
        self.play(Create(base))
        c = ValueTracker(0.0)
        d = ValueTracker(0.0)
        moving = always_redraw(lambda: ax.plot(lambda x: (x - c.get_value()) ** 2 + d.get_value(),
                                               x_range=[c.get_value() - 2.2, c.get_value() + 2.2], color=STEEL, stroke_width=5))
        lab = always_redraw(lambda: MathTex(r"y = (x - %.1f)^2 + %.1f" % (c.get_value(), d.get_value()), font_size=36,
                                            color=STEEL).to_corner(UR, buff=0.5).shift(DOWN * 0.8))
        self.play(Create(moving), FadeIn(lab))
        self.caption("f(x − 2)：原来在 x₀ 处的事推迟到 x₀ + 2 才发生，所以向右移", "f(x − 2): everything happens 2 later, so the graph moves right", wait=0.3)
        self.play(c.animate.set_value(2.0), run_time=2.5)
        dot0 = Dot(ax.c2p(0, 0), color=YELLOW)
        dot1 = Dot(ax.c2p(2, 0), color=YELLOW)
        arr = Arrow(ax.c2p(0, -0.6), ax.c2p(2, -0.6), buff=0, color=YELLOW, stroke_width=4)
        self.play(FadeIn(dot0), FadeIn(dot1), GrowArrow(arr))
        self.wait(0.8)
        self.play(FadeOut(dot0), FadeOut(dot1), FadeOut(arr))
        self.caption("f(x) + 1：每个函数值加 1，向上移", "f(x) + 1: every value plus 1, the graph moves up", wait=0.3)
        self.play(d.animate.set_value(1.0), run_time=2)
        self.play(c.animate.set_value(0.0), d.animate.set_value(0.0), run_time=1.5)
        self.play(FadeOut(moving), FadeOut(lab))
        # 横向伸缩：f(bx)
        b = ValueTracker(1.0)
        sq = always_redraw(lambda: ax.plot(lambda x: (b.get_value() * x) ** 2 - 1, x_range=[-2.2 / b.get_value(), 2.2 / b.get_value()],
                                           color=STEEL, stroke_width=5))
        base2 = ax.plot(lambda x: x * x - 1, x_range=[-2.3, 2.3], color=GREY_B, stroke_width=3)
        zeros = always_redraw(lambda: VGroup(Dot(ax.c2p(1 / b.get_value(), 0), color=YELLOW), Dot(ax.c2p(-1 / b.get_value(), 0), color=YELLOW)))
        labb = always_redraw(lambda: MathTex(r"y = f(%.1f\,x),\ f(x) = x^2 - 1" % b.get_value(), font_size=34, color=STEEL)
                             .to_corner(UR, buff=0.5).shift(DOWN * 0.8))
        self.play(ReplacementTransform(base, base2), Create(sq), FadeIn(zeros), FadeIn(labb))
        self.caption("f(2x)：两倍速播放，图像横向压缩一半，零点 ±1 移到 ±1/2", "f(2x): played at double speed; zeros ±1 move to ±1/2", wait=0.3)
        self.play(b.animate.set_value(2.0), run_time=2.5)
        self.wait(0.5)
        self.play(b.animate.set_value(1.0), run_time=1.2)
        self.play(FadeOut(sq), FadeOut(labb))
        a = ValueTracker(1.0)
        st = always_redraw(lambda: ax.plot(lambda x: a.get_value() * (x * x - 1), x_range=[-math.sqrt(4.8 / a.get_value() + 1), math.sqrt(4.8 / a.get_value() + 1)],
                                           color=STEEL, stroke_width=5))
        laba = always_redraw(lambda: MathTex(r"y = %.1f\,f(x)" % a.get_value(), font_size=36, color=STEEL).to_corner(UR, buff=0.5).shift(DOWN * 0.8))
        self.play(Create(st), FadeIn(laba))
        self.caption("2f(x)：纵向拉长两倍，零点不动（0 的两倍还是 0）", "2f(x): stretched vertically; the zeros stay put", wait=0.3)
        self.play(a.animate.set_value(2.0), run_time=2)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in (st, laba, zeros, base2, ax)])
        # 算例 2.5.1 的四步
        ax2 = Axes(x_range=[-0.5, 6.6, 1], y_range=[-3, 4.5, 1], x_length=10, y_length=5.2, tips=False,
                   axis_config={"color": GREY_B, "include_numbers": False}).shift(DOWN * 0.4)
        ticks = VGroup(*[MathTex(s, font_size=28, color=GREY_B).next_to(ax2.c2p(v, 0), DOWN, buff=0.15)
                         for s, v in ((r"\pi", math.pi), (r"2\pi", 2 * math.pi))])
        self.play(Create(ax2), FadeIn(ticks))
        cur = ax2.plot(np.sin, x_range=[-0.5, 6.6], color=GREY_B, stroke_width=4)
        tex = MathTex(r"y = \sin x", font_size=40).to_corner(UR, buff=0.5).shift(DOWN * 0.8)
        self.play(Create(cur), FadeIn(tex))
        steps = [(lambda x: math.sin(2 * x), r"y = \sin 2x", "① 横向压缩一半，周期变为 π", "① Squeeze by 2: period π"),
                 (lambda x: math.sin(2 * (x - math.pi / 6)), r"y = \sin 2\left(x - \tfrac{\pi}{6}\right)", "② 右移 π/6（不是 π/3）", "② Right by π/6 (not π/3)"),
                 (lambda x: 3 * math.sin(2 * x - math.pi / 3), r"y = 3\sin\left(2x - \tfrac{\pi}{3}\right)", "③ 纵向伸长 3 倍，振幅为 3", "③ Stretch by 3: amplitude 3"),
                 (lambda x: 3 * math.sin(2 * x - math.pi / 3) + 1, r"y = 3\sin\left(2x - \tfrac{\pi}{3}\right) + 1", "④ 上移 1，值域 [−2, 4]", "④ Up 1: range [−2, 4]")]
        for f, t, czh, cen in steps:
            new = ax2.plot(f, x_range=[-0.5, 6.6], color=STEEL, stroke_width=5)
            ntex = MathTex(t, font_size=40, color=STEEL).to_corner(UR, buff=0.5).shift(DOWN * 0.8)
            self.caption(czh, cen, wait=0.2)
            self.play(Transform(cur, new), Transform(tex, ntex), run_time=2)
            self.wait(0.6)
        self.card([["y = a f(b(x − c)) + d", "y = a f(b(x − c)) + d"],
                   MathTex(r"x_0 \xrightarrow{\ \div b\ } \xrightarrow{\ +c\ } \tfrac{x_0}{b} + c\qquad y_0 \xrightarrow{\ \times a\ } \xrightarrow{\ +d\ } a y_0 + d", font_size=40),
                   ["图像上的点 (x₀, y₀) 移到哪里", "Where a point (x₀, y₀) of the graph goes"],
                   ["横向：先伸缩、再平移，方向与直觉相反", "Horizontal: scale then shift, opposite to intuition"],
                   ["纵向：先伸缩、再平移，方向与直觉一致", "Vertical: scale then shift, as expected"]])
