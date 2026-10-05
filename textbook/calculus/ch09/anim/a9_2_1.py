"""动画 9.2.1（配图 9.2.1）：拉格朗日中值定理——曲线的弦；把弦平移，直到它变成切线，切点就是中值点 ξ；
区间测速：位置曲线的弦是平均速度，切线与弦平行处瞬时速度等于平均速度。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("9.2", "拉格朗日中值定理", "The mean value theorem")
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 5.5, 1], x_length=7.5, y_length=5, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.4)
        f = lambda x: 0.5 + 0.9 * x - 0.55 * np.sin(1.4 * x) + 0.12 * x ** 2 - 0.02 * x ** 3
        df = lambda x: 0.9 - 0.77 * np.cos(1.4 * x) + 0.24 * x - 0.06 * x ** 2
        a, b = 0.3, 3.7
        k = (f(b) - f(a)) / (b - a)
        g = ax.plot(f, x_range=[0, 4], color=WHITE, stroke_width=3)
        A, B = Dot(ax.c2p(a, f(a)), color=YELLOW), Dot(ax.c2p(b, f(b)), color=YELLOW)
        la = MathTex("a", font_size=34).next_to(ax.c2p(a, 0), DOWN)
        lb = MathTex("b", font_size=34).next_to(ax.c2p(b, 0), DOWN)
        chord = Line(ax.c2p(a, f(a)), ax.c2p(b, f(b)), color=RED, stroke_width=3)
        self.play(Create(ax), Create(g), FadeIn(A), FadeIn(B), FadeIn(la), FadeIn(lb))
        self.play(Create(chord))
        slope = MathTex(r"\text{slope}=\frac{f(b)-f(a)}{b-a}", font_size=34, color=RED).move_to(ax.c2p(0.25, 5.0), aligned_edge=LEFT)
        self.play(Write(slope))
        self.caption("弦的斜率是平均变化率", "The chord's slope is the average rate of change", wait=0.3)
        # 把弦平行移动：直线 y = f(a) + k(x − a) + c，c 从 0 增到 max(f − 弦)
        xs = np.linspace(a, b, 2001)
        gap = f(xs) - (f(a) + k * (xs - a))
        i = int(np.argmax(gap))
        xi, cmax = xs[i], gap[i]
        c = ValueTracker(0.0)
        moving = always_redraw(lambda: ax.plot(lambda x: f(a) + k * (x - a) + c.get_value(), x_range=[0.05, 3.95], color=STEEL, stroke_width=2.5))
        self.play(FadeIn(moving))
        self.play(c.animate.set_value(cmax), run_time=3)
        moving.clear_updaters()
        P = Dot(ax.c2p(xi, f(xi)), color=ORANGE, radius=0.09)
        lxi = MathTex(r"\xi", font_size=36, color=ORANGE).next_to(ax.c2p(xi, 0), DOWN)
        vl = DashedLine(ax.c2p(xi, 0), ax.c2p(xi, f(xi)), color=ORANGE)
        self.play(FadeIn(P), Create(vl), FadeIn(lxi))
        eq = MathTex(r"f'(\xi)=\frac{f(b)-f(a)}{b-a}", font_size=40, color=ORANGE).next_to(slope, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(Write(eq))
        self.caption("平移到最后一刻接触曲线时，它就是切线：切点处的导数等于平均变化率",
                     "When the moving line last touches the curve, it is a tangent: there f′ equals the average rate", wait=0.6)
        self.caption("区间测速：平均速度一定等于某一时刻的瞬时速度", "Average-speed cameras: the average speed is attained at some instant", wait=0.6)
        self.play(*[FadeOut(m) for m in (ax, g, A, B, la, lb, chord, slope, moving, P, lxi, vl, eq)])
        self.card([["拉格朗日中值定理", "The mean value theorem"],
                   MathTex(r"f(b)-f(a)=f'(\xi)(b-a),\qquad a<\xi<b", font_size=44),
                   ["条件：f 在 [a, b] 上连续、在 (a, b) 内可导", "f continuous on [a, b], differentiable on (a, b)"]])
