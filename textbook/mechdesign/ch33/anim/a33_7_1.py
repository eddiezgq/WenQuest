"""动画 33.7.1（配图 33.7.2）：转速升高经过临界转速时，轴的弯曲挠度急剧增大；越过以后又变小，并且质心转到内侧。"""
from manim import *
from wq_anim import *
import numpy as np

Z = 0.04


def amp(r):
    return r * r / np.sqrt((1 - r * r) ** 2 + (2 * Z * r) ** 2)


class Lesson(Base):
    def construct(self):
        self.title("33.7", "临界转速：共振的轴", "Critical speed: a shaft in resonance")
        r = ValueTracker(0.05)
        A, B = np.array([-5.5, 0.4, 0]), np.array([-1.5, 0.4, 0])
        brg = VGroup(*[Triangle(color=WHITE).scale(0.18).move_to(p + DOWN * 0.3) for p in (A, B)])

        def bent():
            y = 0.18 * min(amp(r.get_value()), 6.5)
            pts = [A + RIGHT * 4 * s + UP * y * np.sin(PI * s) for s in np.linspace(0, 1, 30)]
            return VMobject(color=GREY_B, stroke_width=8).set_points_smoothly(pts)
        shaft = always_redraw(bent)
        disk = always_redraw(lambda: RoundedRectangle(width=0.25, height=1.6, corner_radius=0.05, color="#d29922", fill_opacity=1)
                             .move_to((A + B) / 2 + UP * 0.18 * min(amp(r.get_value()), 6.5)))
        self.play(FadeIn(brg), FadeIn(shaft), FadeIn(disk))
        ax = Axes(x_range=[0, 2.5, 0.5], y_range=[0, 7, 1], x_length=5.6, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B}).move_to([3.3, 0.2, 0])
        xl = MathTex(r"n/n_\mathrm c", font_size=28).next_to(ax.x_axis, DOWN, buff=0.2)
        yl = MathTex(r"y/e", font_size=28).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), Write(xl), Write(yl))
        trace = always_redraw(lambda: ax.plot(lambda x: min(amp(x), 6.8), x_range=[0.01, r.get_value(), 0.005], color=RED))
        dot = always_redraw(lambda: Dot(ax.c2p(r.get_value(), min(amp(r.get_value()), 6.8)), color=YELLOW))
        num = always_redraw(lambda: MathTex(r"n/n_\mathrm c = %.2f" % r.get_value(), font_size=30, color=YELLOW).move_to([-3.5, 2.4, 0]))
        self.add(trace, dot, num)
        self.caption("圆盘的质心偏离轴线 e：旋转时离心力把轴弯曲", "The disk's centre of mass is off the axis by e; centrifugal force bends the shaft")
        self.play(r.animate.set_value(0.7), run_time=3, rate_func=linear)
        self.caption("接近临界转速 nc：离心力与轴的弹性力“同拍”，挠度急剧增大", "Near the critical speed nc the bending grows sharply — resonance", wait=0)
        self.play(r.animate.set_value(1.0), run_time=3, rate_func=linear)
        self.wait(0.5)
        self.caption("快速越过以后，挠度又减小，趋于偏心距 e：质心转到了轴线内侧（自动定心）",
                     "Past it, the bending falls back towards e: the centre of mass moves inside (self-centring)", wait=0)
        self.play(r.animate.set_value(2.4), run_time=4, rate_func=linear)
        self.wait(1)
        self.card([["临界转速", "Critical speed"],
                   MathTex(r"n_\mathrm c=\frac{60}{2\pi}\sqrt{\frac{k}{m}}", font_size=44),
                   ["刚性轴：n ≤ 0.7nc；挠性轴：1.3nc ≤ n ≤ 0.7nc2，起停时快速通过", "Rigid shaft: n ≤ 0.7nc; flexible shaft: run between 1.3nc and 0.7nc2, pass quickly"]])
