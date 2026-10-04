"""动画 4.5.1（配图 4.5.1）：夹逼出 sin x / x → 1。三角形 OAB、扇形 OAB、三角形 OAD 随圆心角缩小，
面积之比趋于 1；cos x 与 1 把 sin x / x 夹在中间；放大原点附近，三条曲线汇于一点。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("4.5", "夹逼出 sin x / x → 1", "Squeezing sin x / x → 1")
        R = 3.6
        O = LEFT * 5.2 + DOWN * 2.6
        x = ValueTracker(0.9)
        P = lambda t: O + R * np.array([np.cos(t), np.sin(t), 0])
        arc = Arc(radius=R, start_angle=0, angle=PI / 2, arc_center=O, color=GREY_B, stroke_width=2)
        big = always_redraw(lambda: Polygon(O, O + R * RIGHT, O + R * RIGHT + R * np.tan(x.get_value()) * UP,
                                            color=RED, fill_opacity=0.15, stroke_width=2))
        sec = always_redraw(lambda: Sector(radius=R, angle=x.get_value(), arc_center=O, color=YELLOW, fill_opacity=0.35, stroke_width=0))
        tri = always_redraw(lambda: Polygon(O, O + R * RIGHT, P(x.get_value()), color=STEEL, fill_opacity=0.45, stroke_width=2))
        self.play(Create(arc), FadeIn(big), FadeIn(sec), FadeIn(tri))
        def row(i, tex, val, col):
            lab = MathTex(tex, font_size=34, color=col)
            num = always_redraw(lambda: DecimalNumber(val(x.get_value()), num_decimal_places=5, font_size=34, color=col))
            g = VGroup(lab, num)
            lab.move_to(RIGHT * 2.2 + UP * (1.5 - 0.9 * i), aligned_edge=LEFT)
            num.add_updater(lambda m: m.next_to(lab, RIGHT, buff=0.3))
            return VGroup(lab, num)
        rows = VGroup(row(0, r"x =", lambda t: t, WHITE),
                      row(1, r"\tfrac12\sin x =", lambda t: np.sin(t) / 2, STEEL),
                      row(2, r"\tfrac12 x =", lambda t: t / 2, YELLOW),
                      row(3, r"\tfrac12\tan x =", lambda t: np.tan(t) / 2, RED),
                      row(4, r"\sin x / x =", lambda t: np.sin(t) / t, GREEN))
        self.play(FadeIn(rows))
        self.caption("三角形 < 扇形 < 大三角形：sin x < x < tan x", "triangle < sector < big triangle: sin x < x < tan x", wait=0.3)
        self.play(x.animate.set_value(0.08), run_time=5, rate_func=smooth)
        self.caption("角越小，三个面积越接近：sin x / x → 1", "As the angle shrinks the areas agree: sin x / x → 1", wait=0.5)
        self.play(*[FadeOut(m) for m in (arc, big, sec, tri, rows)])
        def scene(xr, yr, xs, ys):
            ax = Axes(x_range=xr, y_range=yr, x_length=10, y_length=5, tips=False,
                      axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(DOWN * 0.4)
            lo, hi = xr[0], xr[1]
            c = ax.plot(np.cos, x_range=[lo, hi], color=STEEL, stroke_width=3)
            one = ax.plot(lambda t: 1, x_range=[lo, hi], color=GREEN, stroke_width=3)
            f = VGroup(ax.plot(lambda t: np.sin(t) / t, x_range=[lo, -1e-4], color=RED, stroke_width=4),
                       ax.plot(lambda t: np.sin(t) / t, x_range=[1e-4, hi], color=RED, stroke_width=4))
            return VGroup(ax, c, one, f)
        g1 = scene([-2.5, 2.5, 0.5], [-0.8, 1.2, 0.2], 1, 1)
        leg = VGroup(MathTex(r"\cos x", color=STEEL, font_size=32), MathTex(r"\sin x / x", color=RED, font_size=32),
                     MathTex(r"1", color=GREEN, font_size=32)).arrange(RIGHT, buff=0.6).to_edge(UP).shift(DOWN * 0.9)
        self.play(Create(g1), FadeIn(leg), run_time=2)
        self.caption("cos x 与 1 把 sin x / x 夹在中间", "cos x and 1 squeeze sin x / x between them", wait=0.5)
        g2 = scene([-0.3, 0.3, 0.1], [0.95, 1.01, 0.01], 1, 1)
        self.play(ReplacementTransform(g1, g2), run_time=2)
        self.caption("放大原点附近：三条曲线汇于 (0, 1)", "Zoom in near 0: the three curves meet at (0, 1)", wait=0.5)
        self.play(FadeOut(g2), FadeOut(leg))
        self.card([["重要极限", "A key limit"],
                   MathTex(r"\cos x<\frac{\sin x}{x}<1\ \Rightarrow\ \lim_{x\to0}\frac{\sin x}{x}=1", font_size=46),
                   ["x 以弧度计；这是三角函数求导的基础", "x in radians; the basis of differentiating trig functions"]])
