"""动画 52.4.1（配图 52.4.1）：圆偏心夹紧——偏心轮转动时，夹紧点相当于沿一个斜楔爬升；升角不超过摩擦角就自锁。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("52.4", "圆偏心夹紧与自锁", "Eccentric clamping and self-locking")
        R, e = 1.6, 0.35
        pivot = np.array([-2.0, 0.2, 0])
        work = Rectangle(width=3.6, height=0.5, fill_color=STEEL, fill_opacity=0.3, stroke_color=INK).move_to(pivot + DOWN * (R + e + 0.25))
        self.play(FadeIn(work))
        self.caption("偏心轮绕转轴转动，轮廓到转轴的距离随转角变化", "The eccentric turns about its pivot; its distance to the pivot changes with angle")
        g = ValueTracker(0.0)

        def cam():
            th = g.get_value()
            c = pivot + e * np.array([np.cos(th - PI / 2), np.sin(th - PI / 2), 0])
            disk = Circle(radius=R, color=BLUE, fill_opacity=0.15).move_to(c)
            handle = Line(c, c + 2.2 * np.array([np.cos(th + PI / 2 + 0.6), np.sin(th + PI / 2 + 0.6), 0]), color=INK, stroke_width=6)
            return VGroup(disk, handle, Dot(pivot, color=RED), Dot(c, color=BLUE, radius=0.05))

        cg = always_redraw(cam)
        self.add(cg)
        self.play(g.animate.set_value(PI / 2), run_time=3)
        self.caption("转过 90° 附近升角最大：tan α = e/(D/2)", "Near 90° the lift angle is largest: tan α = e/(D/2)")
        wedge = Polygon(np.array([1.2, -1.8, 0]), np.array([4.6, -1.8, 0]), np.array([4.6, -1.2, 0]), color=ORANGE, fill_opacity=0.4)
        lab = MathTex(r"\alpha", color=ORANGE).next_to(wedge, LEFT, buff=0.1).shift(UP * 0.1)
        self.play(FadeIn(wedge), Write(lab))
        self.caption("把轮廓展开，就是一个绕在圆上的斜楔", "Unrolled, the profile is a wedge wrapped round a circle")
        self.caption("斜楔自锁的条件：升角不大于摩擦角", "A wedge self-locks when its angle does not exceed the friction angle")
        cond = MathTex(r"\frac{2e}{D} \le \mu", color=INK).to_corner(UR)
        self.play(Write(cond))
        self.caption("μ = 0.1 时 D/e ≥ 20；偏心距再大，松手就会退回", "With μ = 0.1, D/e ≥ 20; any larger eccentricity and it backs off when released")
        self.card([["偏心夹紧快，但行程只有 2e，只适合尺寸变化小的工件", "Eccentrics are fast but their stroke is only 2e — for parts of steady size"],
                   ["振动大的工序（铣、粗车）慎用偏心夹紧", "Avoid eccentrics on heavy-vibration operations (milling, rough turning)"]])
