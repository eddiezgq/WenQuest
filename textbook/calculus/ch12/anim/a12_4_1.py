"""动画 12.4.1（配图 12.4.1）：积分中值定理——在曲线下面积不变的前提下，一个矩形的高度上下调整，直到矩形面积等于曲线下的面积；
这时矩形的上边与曲线相交，交点的横坐标就是 ξ，矩形的高就是平均值。"""
from manim import *
from wq_anim import *
import numpy as np

F = lambda x: 0.4 + 1.6 * np.exp(-((x - 1.1) ** 2) / 0.5) + 0.3 * x


class Lesson(Base):
    def construct(self):
        self.title("12.4", "积分中值定理", "Mean value theorem for integrals")
        a, b = 0.0, 3.0
        ax = Axes(x_range=[0, 3.2, 1], y_range=[0, 2.6, 1], x_length=8, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.5)
        g = ax.plot(F, x_range=[a, b], color=WHITE, stroke_width=3)
        area = ax.get_area(g, x_range=[a, b], color=STEEL, opacity=0.35)
        xs = np.linspace(a, b, 100001)
        I = float(np.sum((F(xs[1:]) + F(xs[:-1])) / 2 * np.diff(xs)))
        mean = I / (b - a)
        self.play(Create(ax), Create(g))
        self.play(FadeIn(area))
        lab = MathTex(r"\int_a^b f(x)\,dx=%.3f" % I, font_size=36, color=STEEL).to_corner(UR).shift(DOWN * 1.0 + LEFT * 0.3)
        self.play(Write(lab))
        h = ValueTracker(2.2)
        rect = always_redraw(lambda: Rectangle(width=ax.c2p(b, 0)[0] - ax.c2p(a, 0)[0], height=ax.c2p(0, h.get_value())[1] - ax.c2p(0, 0)[1],
                                               color=ORANGE, stroke_width=3).move_to(ax.c2p((a + b) / 2, h.get_value() / 2)))
        rl = always_redraw(lambda: MathTex(r"h\,(b-a)=%.3f" % (h.get_value() * (b - a)), font_size=36, color=ORANGE).next_to(lab, DOWN, aligned_edge=RIGHT))
        self.play(Create(rect), Write(rl))
        self.caption("矩形太高，面积大于曲线下的面积", "Too tall: the rectangle has more area", wait=0.3)
        self.play(h.animate.set_value(0.5), run_time=2.5)
        self.caption("太矮，面积又不够", "Too short: not enough area", wait=0.3)
        self.play(h.animate.set_value(mean), run_time=2)
        rect.clear_updaters()
        rl.clear_updaters()
        roots = [x for x0, x1 in zip(xs[:-1:100], xs[100::100]) if (F(x0) - mean) * (F(x1) - mean) < 0 for x in [(x0 + x1) / 2]]
        dots = VGroup(*[Dot(ax.c2p(x, mean), color=YELLOW, radius=0.09) for x in roots])
        xl = VGroup(*[MathTex(r"\xi", font_size=34, color=YELLOW).next_to(ax.c2p(x, 0), DOWN) for x in roots])
        vl = VGroup(*[DashedLine(ax.c2p(x, 0), ax.c2p(x, mean), color=YELLOW) for x in roots])
        self.play(FadeIn(dots), Create(vl), FadeIn(xl))
        self.caption("面积相等时，矩形的高就是平均值，它等于 f 在某点 ξ 处的值", "Equal areas: the height is the mean value, attained at some ξ", wait=0.8)
        self.play(*[FadeOut(m) for m in (ax, g, area, lab, rect, rl, dots, xl, vl)])
        self.card([["积分中值定理", "Mean value theorem for integrals"],
                   MathTex(r"\int_a^b f(x)\,dx=f(\xi)(b-a),\qquad a\le\xi\le b", font_size=44),
                   ["f 在 [a, b] 上连续；f(ξ) 就是 f 在区间上的平均值", "f continuous on [a, b]; f(ξ) is its average value"]])
