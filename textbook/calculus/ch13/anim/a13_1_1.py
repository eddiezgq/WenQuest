"""动画 13.1.1（配图 13.1.1）：变上限积分——上限 x 向右移动，曲线下的面积 Φ(x) 随之增长；下方画出 Φ 的图像。
x 处再添一条宽 Δx 的窄条，面积的增量约为 f(x)Δx，所以 Φ 的增长率（切线斜率）就是 f(x) 的高度。"""
from manim import *
from wq_anim import *
import numpy as np

F = lambda t: 0.5 + 0.9 * np.exp(-((t - 1.2) ** 2) / 0.35) + 0.25 * np.sin(2.4 * t)
TS = np.linspace(0, 3, 30001)
CUM = np.concatenate([[0], np.cumsum((F(TS[1:]) + F(TS[:-1])) / 2 * np.diff(TS))])
PHI = lambda x: float(np.interp(x, TS, CUM))


class Lesson(Base):
    def construct(self):
        self.title("13.1", "变上限积分", "The integral as a function of its upper limit")
        top = Axes(x_range=[0, 3.2, 1], y_range=[0, 1.8, 1], x_length=8, y_length=2.4, tips=False,
                   axis_config={"color": GREY_B}).shift(UP * 1.35 + LEFT * 0.8)
        bot = Axes(x_range=[0, 3.2, 1], y_range=[0, 3.2, 1], x_length=8, y_length=2.4, tips=False,
                   axis_config={"color": GREY_B}).shift(DOWN * 1.75 + LEFT * 0.8)
        g = top.plot(F, x_range=[0, 3], color=WHITE, stroke_width=3)
        lf = MathTex("f(t)", font_size=32).next_to(top, RIGHT, buff=0.1).shift(UP * 0.6)
        lp = MathTex(r"\Phi(x)=\int_0^x f(t)\,dt", font_size=32, color=STEEL).next_to(bot, RIGHT, buff=0.1).shift(UP * 0.5)
        self.play(Create(top), Create(g), Write(lf), Create(bot), Write(lp))
        x = ValueTracker(0.05)
        area = always_redraw(lambda: top.get_area(g, x_range=[0, x.get_value()], color=STEEL, opacity=0.35))
        vl = always_redraw(lambda: DashedLine(top.c2p(x.get_value(), 0), top.c2p(x.get_value(), F(x.get_value())), color=ORANGE))
        trace = always_redraw(lambda: bot.plot(PHI, x_range=[0, max(x.get_value(), 0.01)], color=STEEL, stroke_width=3))
        dot = always_redraw(lambda: Dot(bot.c2p(x.get_value(), PHI(x.get_value())), color=ORANGE))
        self.add(area, vl, trace, dot)
        self.caption("上限 x 向右移动，阴影面积 Φ(x) 随之增长", "As x moves right, the shaded area Φ(x) grows", wait=0.2)
        self.play(x.animate.set_value(1.2), run_time=4, rate_func=linear)
        dx = 0.25
        strip = Rectangle(width=top.c2p(dx, 0)[0] - top.c2p(0, 0)[0], height=top.c2p(0, F(1.2))[1] - top.c2p(0, 0)[1],
                          color=ORANGE, fill_opacity=0.5, stroke_width=2).move_to(top.c2p(1.2 + dx / 2, F(1.2) / 2))
        tan = Line(bot.c2p(0.55, PHI(1.2) - 0.65 * F(1.2)), bot.c2p(1.85, PHI(1.2) + 0.65 * F(1.2)), color=ORANGE)
        note = MathTex(r"\Delta\Phi\approx f(x)\,\Delta x", font_size=34, color=ORANGE).move_to(top.c2p(2.6, 1.6))
        self.play(FadeIn(strip), Write(note))
        self.caption("多走 Δx，面积多出一个窄条，约为 f(x)Δx", "One more Δx adds a strip of about f(x)Δx", wait=0.6)
        self.play(Create(tan))
        self.caption("所以 Φ 的切线斜率就是 f(x)：曲线高的地方，Φ 涨得快", "So the slope of Φ is f(x): where f is high, Φ climbs fast", wait=0.8)
        self.play(FadeOut(strip), FadeOut(tan), FadeOut(note))
        self.play(x.animate.set_value(3.0), run_time=5, rate_func=linear)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in (top, bot, g, lf, lp, area, vl, trace, dot)])
        self.card([["微积分基本定理（第一部分）", "Fundamental theorem, part 1"],
                   MathTex(r"\frac{d}{dx}\int_a^x f(t)\,dt=f(x)", font_size=48),
                   ["f 连续时，面积对上限的变化率等于曲线的高度", "For continuous f, the area grows at the rate of the height"]])
