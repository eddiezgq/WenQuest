"""动画 1.4.1（配图 1.4.2）：自由度的计数。

一块平面上的板可以平移和转动：3 个自由度 (x, y, φ)；用转动关节把它钉在地上，只剩转角 θ₁；
再用第二个转动关节接上一根连杆，多出 θ₂：开链的自由度等于各关节自由度之和。
"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("1.4", "自由度：确定位置需要几个数", "Degrees of freedom: how many numbers fix the position")
        count = ValueTracker(3)
        meter = always_redraw(lambda: VGroup(zh("自由度", 26, YELLOW), MathTex(str(int(round(count.get_value()))),
                                                                                  color=YELLOW, font_size=56))
                              .arrange(RIGHT, buff=0.25).to_corner(UR, buff=0.7).shift(DOWN * 0.6))
        self.add(meter)
        plate = Rectangle(width=2.4, height=0.9, color=STEEL, fill_color=NAVY, fill_opacity=0.9).move_to([-2.5, 0.2, 0])
        A = Dot(plate.get_center() + LEFT * 0.8, color=YELLOW)
        B = Dot(plate.get_center() + RIGHT * 0.8, color=YELLOW)
        body = VGroup(plate, A, B)
        labA = always_redraw(lambda: MathTex("A", color=YELLOW, font_size=28).next_to(A, DOWN, buff=0.08))
        labB = always_redraw(lambda: MathTex("B", color=YELLOW, font_size=28).next_to(B, DOWN, buff=0.08))
        self.play(FadeIn(body), FadeIn(labA), FadeIn(labB))
        self.caption("两点 4 个坐标，减去 1 个距离约束：平面刚体有 3 个自由度", "4 coordinates of two points minus 1 distance constraint: 3 DOF", wait=0)
        self.play(body.animate.shift(RIGHT * 1.8), run_time=1.0)
        self.play(body.animate.shift(UP * 0.9), run_time=1.0)
        self.play(Rotate(body, angle=PI / 4), run_time=1.0)
        tag = MathTex(r"(x,\ y,\ \varphi)", color=YELLOW, font_size=36).next_to(meter, DOWN, buff=0.3)
        self.play(Write(tag))
        self.wait(0.8)
        self.play(FadeOut(tag), FadeOut(labA), FadeOut(labB), FadeOut(body))

        base = np.array([-3.0, -1.2, 0])
        ped = Polygon(base + LEFT * 0.5 + DOWN * 0.3, base + RIGHT * 0.5 + DOWN * 0.3, base + RIGHT * 0.25, base + LEFT * 0.25,
                      color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        t1 = ValueTracker(50)
        t2 = ValueTracker(0)
        show2 = ValueTracker(0)

        def arm_now():
            a1 = np.radians(t1.get_value())
            p1 = base + 2.4 * np.array([np.cos(a1), np.sin(a1), 0])
            g = VGroup(Line(base, p1, color=STEEL, stroke_width=16), Dot(base, radius=0.13, color=WHITE))
            if show2.get_value() > 0.5:
                a2 = a1 + np.radians(t2.get_value())
                p2 = p1 + 1.8 * np.array([np.cos(a2), np.sin(a2), 0])
                g.add(Line(p1, p2, color=GREEN, stroke_width=12), Dot(p1, radius=0.11, color=WHITE),
                      MathTex(r"\theta_2", color=GREEN, font_size=30).next_to(p1, UP, buff=0.15))
            g.add(MathTex(r"\theta_1", color=STEEL, font_size=30).move_to(base + np.array([0.85, 0.0, 0])))
            return g
        arm = always_redraw(arm_now)
        self.play(FadeIn(ped), FadeIn(arm), count.animate.set_value(1), run_time=1.0)
        self.caption("用转动关节把连杆钉在地上：只剩一个转角 θ₁", "Pin the link to the ground with a revolute joint: only θ₁ is left", wait=0)
        self.play(t1.animate.set_value(110), run_time=1.2)
        self.play(t1.animate.set_value(30), run_time=1.2)
        show2.set_value(1)
        self.play(count.animate.set_value(2), run_time=0.6)
        self.caption("再接一根连杆，多一个转角 θ₂：自由度为 2", "Add another link: one more angle θ₂, 2 DOF", wait=0)
        self.play(t2.animate.set_value(-70), run_time=1.2)
        self.play(t1.animate.set_value(70), t2.animate.set_value(40), run_time=1.5)
        self.play(t1.animate.set_value(45), t2.animate.set_value(-30), run_time=1.0)
        self.caption("开链：自由度等于各关节自由度之和", "Open chain: DOF = sum of the joints' DOF", wait=1.5)
        self.card([["自由度", "Degrees of freedom"],
                   ["平面刚体 3，空间刚体 6", "rigid body: 3 in the plane, 6 in space"],
                   MathTex(r"m = \sum_{i=1}^{n} f_i", font_size=44),
                   ["基座自由运动时，再加 3 或 6", "add 3 or 6 when the base moves freely"]])
