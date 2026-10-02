"""动画 8.2.1（配图 8.2.1）：在约束直线 2x + y = 20 上移动一点，看面积 S = xy 的梯度 ∇S 与约束的梯度 ∇h：
不平行时，沿直线还能让 S 增大；二者平行的那一点，就是约束下的最优点 (5, 10)。"""
from manim import *
from wq_anim import *
import numpy as np
import math

U = 0.25                             # 1 m 画成 0.25 个单位
O = np.array([-3.4, -2.75, 0])


def P(x, y):
    return O + U * np.array([x, y, 0])


class Lesson(Base):
    def construct(self):
        self.title("8.2", "约束下的最优点：两个梯度平行", "The constrained optimum: two gradients are parallel")
        axes = VGroup(Arrow(P(0, 0), P(12, 0), buff=0, color=GREY_B, stroke_width=3),
                      Arrow(P(0, 0), P(0, 21.5), buff=0, color=GREY_B, stroke_width=3),
                      MathTex("x", font_size=30).next_to(P(12, 0), RIGHT, buff=0.1),
                      MathTex("y", font_size=30).next_to(P(0, 21.5), RIGHT, buff=0.1))
        hyp = VGroup()
        for S in (20, 35, 50, 65, 80):
            xs = np.linspace(S / 21, 11.5, 80)
            hyp.add(VMobject(color=BLUE_C if S == 50 else GREY_C, stroke_width=3 if S == 50 else 2).set_points_smoothly([P(x, S / x) for x in xs]))
        line = Line(P(0, 20), P(10, 0), color=WHITE, stroke_width=4)
        lab = MathTex(r"2x + y = 20", font_size=30).next_to(P(0, 20), LEFT, buff=0.15)
        self.play(Create(axes), Create(hyp), run_time=1.5)
        self.caption("灰色曲线：面积 S = xy 的等高线，越往右上越大", "Grey curves: level curves of the area S = xy, larger to the upper right")
        self.play(Create(line), Write(lab))
        self.caption("篱笆只有 20 m：只能在这条直线上选点", "Only 20 m of fence: we must stay on this line")

        xv = ValueTracker(1.5)

        def scene():
            x = xv.get_value()
            y = 20 - 2 * x
            gS = np.array([y, x])
            gS = gS / np.linalg.norm(gS) * 1.6
            gh = np.array([2.0, 1.0]) / math.sqrt(5) * 1.1
            p = P(x, y)
            return VGroup(Arrow(p, p + np.array([gS[0], gS[1], 0]), buff=0, color=YELLOW, stroke_width=6, max_tip_length_to_length_ratio=0.2),
                          Arrow(p, p + np.array([gh[0], gh[1], 0]), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.25),
                          Dot(p, color=WHITE, radius=0.08))

        def panel():
            x = xv.get_value()
            y = 20 - 2 * x
            gS = np.array([y, x])
            ang = math.degrees(math.acos(min(1.0, gS @ np.array([2, 1]) / (np.linalg.norm(gS) * math.sqrt(5)))))
            return VGroup(MathTex(r"x = %.2f\ \mathrm{m},\ y = %.2f\ \mathrm{m}" % (x, y), font_size=32),
                          MathTex(r"S = xy = %.1f\ \mathrm{m^2}" % (x * y), font_size=32, color=BLUE_C),
                          MathTex(r"\angle(\nabla S, \nabla h) = %.1f^\circ" % ang, font_size=32, color=YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(np.array([3.6, 1.2, 0]))

        sc = always_redraw(scene)
        pn = always_redraw(panel)
        leg = VGroup(MathTex(r"\nabla S", color=YELLOW, font_size=32), MathTex(r"\nabla h", color=RED, font_size=32)).arrange(RIGHT, buff=0.6).move_to(np.array([3.6, -0.6, 0]))
        self.play(FadeIn(sc), FadeIn(pn), FadeIn(leg))
        self.caption("两个梯度不平行时，沿直线朝某个方向走，S 还会增大", "While the gradients are not parallel, moving along the line still increases S", wait=0)
        self.play(xv.animate.set_value(8.5), run_time=4, rate_func=there_and_back_with_pause)
        self.caption("在 (5, 10) 处二者平行：等高线与直线相切，S 最大", "At (5, 10) they are parallel: the level curve touches the line and S is largest", wait=0)
        self.play(xv.animate.set_value(5.0), run_time=2.5)
        self.wait(1.5)
        eq = MathTex(r"\nabla S = \lambda\,\nabla h:\ \ (y, x) = \lambda\,(2, 1)", font_size=36).move_to(np.array([3.6, -1.6, 0]))
        self.play(Write(eq))
        self.caption("λ = 5：多 1 m 篱笆，面积约多 5 m²", "λ = 5: one more metre of fence adds about 5 m² of area")
        self.wait(1)
        self.card([["拉格朗日乘子法", "Lagrange multipliers"],
                   MathTex(r"\nabla f(x^*) + \lambda\,\nabla h(x^*) = 0,\qquad h(x^*) = 0", font_size=44),
                   ["约束下的最优点：目标函数的梯度与约束的梯度平行", "at a constrained optimum the gradients of the objective and the constraint are parallel"]])
