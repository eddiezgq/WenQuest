"""动画 7.2.1（配图 7.2.2）：放大镜。正方形窗口中心是曲线上的一点，窗口宽度 2w 逐渐缩小（放大倍数 1/w）：
sin x 在 x = 1 处越放大越直，与切线重合；|x| 在原点的尖角形状不变；∛x 在原点变成竖直线。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("7.2", "放大镜：可导就是放大后变直", "Magnifier: differentiable means straight when magnified")
        S = 2.6                                     # half side of the window on screen
        C = np.array([0.0, -0.3, 0.0])
        frame = Square(side_length=2 * S, color=GREY_B, stroke_width=2).move_to(C)
        self.add(frame)
        z = ValueTracker(0.0)                       # lg of the zoom

        def window(fn, x0, slope=None):
            def draw():
                w = 2.0 * 10 ** (-z.get_value())
                y0 = fn(x0)
                xs = np.linspace(x0 - w, x0 + w, 401)
                pts = [C + np.array([(x - x0) / w * S, (fn(x) - y0) / w * S, 0.0]) for x in xs]
                pts = [p for p in pts if abs(p[1] - C[1]) <= S]
                g = VGroup()
                if slope is not None:
                    g.add(Line(C + np.array([-S, -slope * S, 0]), C + np.array([S, slope * S, 0]), color=RED, stroke_width=3))
                g.add(VMobject(color=WHITE, stroke_width=5).set_points_smoothly(pts) if len(pts) > 3 else VGroup())
                g.add(Dot(C, color=YELLOW, radius=0.07))
                return g
            return draw

        def zoomtext():
            return zh("放大 %d 倍" % round(10 ** z.get_value()), 26, INK).next_to(frame, RIGHT, buff=0.4).shift(UP * 1.5)

        # 1. sin x at 1
        g = always_redraw(window(math.sin, 1.0, math.cos(1.0)))
        zt = always_redraw(zoomtext)
        name = zh("y = sin x，x₀ = 1", 28, WHITE).next_to(frame, LEFT, buff=0.4).shift(UP * 1.5)
        self.play(FadeIn(g), FadeIn(zt), FadeIn(name))
        self.caption("光滑曲线，红线是切线", "A smooth curve; red is the tangent", wait=0.5)
        self.play(z.animate.set_value(2.0), run_time=5, rate_func=linear)
        self.caption("放大 100 倍：曲线与切线重合了", "100×: the curve sits on its tangent")
        self.play(FadeOut(g), FadeOut(name))
        # 2. |x| at 0
        z.set_value(0.0)
        g2 = always_redraw(window(abs, 0.0))
        name2 = zh("y = |x|，x₀ = 0", 28, WHITE).next_to(frame, LEFT, buff=0.4).shift(UP * 1.5)
        self.play(FadeIn(g2), FadeIn(name2))
        self.caption("尖角：怎样放大都还是尖角", "A corner stays a corner however far we zoom", wait=0.3)
        self.play(z.animate.set_value(3.0), run_time=5, rate_func=linear)
        self.caption("左、右导数 −1 与 1 不相等，函数在这里不可导", "One-sided derivatives −1 and 1 differ: not differentiable here")
        self.play(FadeOut(g2), FadeOut(name2))
        # 3. cube root at 0
        z.set_value(0.0)
        g3 = always_redraw(window(lambda x: math.copysign(abs(x) ** (1 / 3), x), 0.0))
        name3 = zh("y = ∛x，x₀ = 0", 28, WHITE).next_to(frame, LEFT, buff=0.4).shift(UP * 1.5)
        self.play(FadeIn(g3), FadeIn(name3))
        self.caption("越放大越接近竖直线：竖直切线，导数为无穷大", "It tends to a vertical line: a vertical tangent, infinite slope", wait=0.3)
        self.play(z.animate.set_value(2.0), run_time=5, rate_func=linear)
        self.wait(1)
        self.card([["可导 ⇔ 局部线性", "Differentiable ⇔ locally linear"],
                   MathTex(r"f(x_0+h)\approx f(x_0)+f'(x_0)\,h", font_size=48),
                   ["角点、尖点、竖直切线处不可导", "Corners, cusps and vertical tangents are not differentiable"]])
