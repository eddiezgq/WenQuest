"""动画 3.1.1（配图 3.1.2）：箭头 d 固定，坐标系 {b} 转动，d 在 {b} 中的两个分量随之变化，长度不变。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-3.9, -1.3, 0])
K = 8.0                      # 1 m 画成 8 个单位
DA = np.array([0.30, 0.20])


class Lesson(Base):
    def construct(self):
        self.title("3.1", "同一支箭头，两套分量", "One arrow, two sets of components")
        P = lambda x, y: O + K * np.array([x, y, 0])
        fa = VGroup(Arrow(O, P(0.42, 0), buff=0, color=RED, stroke_width=4, stroke_opacity=0.45),
                    Arrow(O, P(0, 0.36), buff=0, color=GREEN, stroke_width=4, stroke_opacity=0.45),
                    MathTex(r"\hat{\boldsymbol x}_a", color=RED, font_size=30).set_opacity(0.6).move_to(P(0.45, -0.02)),
                    MathTex(r"\hat{\boldsymbol y}_a", color=GREEN, font_size=30).set_opacity(0.6).move_to(P(-0.03, 0.37)))
        self.play(Create(fa), run_time=1)
        d_arrow = Arrow(O, P(*DA), buff=0, color=WHITE, stroke_width=7)
        d_lab = MathTex(r"\boldsymbol d", font_size=40).next_to(P(*DA), UR, buff=0.08)
        self.play(GrowArrow(d_arrow), Write(d_lab))
        self.caption("箭头 d 一经画出，长度和指向就确定了", "Once drawn, the arrow d has a definite length and direction")

        beta = ValueTracker(0.0)

        def frame_b():
            t = beta.get_value()
            xb = np.array([math.cos(t), math.sin(t)])
            yb = np.array([-math.sin(t), math.cos(t)])
            f1, f2 = DA @ xb, DA @ yb
            g = VGroup(Arrow(O, P(*(0.42 * xb)), buff=0, color=RED, stroke_width=6),
                       Arrow(O, P(*(0.36 * yb)), buff=0, color=GREEN, stroke_width=6),
                       MathTex(r"\hat{\boldsymbol x}_b", color=RED, font_size=32).move_to(P(*(0.47 * xb))),
                       MathTex(r"\hat{\boldsymbol y}_b", color=GREEN, font_size=32).move_to(P(*(0.41 * yb))),
                       DashedLine(P(*DA), P(*(f1 * xb)), color=RED, stroke_width=3),
                       DashedLine(P(*DA), P(*(f2 * yb)), color=GREEN, stroke_width=3),
                       Line(O, P(*(f1 * xb)), color=RED, stroke_width=10, stroke_opacity=0.55),
                       Line(O, P(*(f2 * yb)), color=GREEN, stroke_width=10, stroke_opacity=0.55))
            if t > 0.02:
                g.add(Arc(radius=0.9, start_angle=0, angle=t, arc_center=O, color=YELLOW))
            return g

        def numbers():
            t = beta.get_value()
            xb = np.array([math.cos(t), math.sin(t)])
            yb = np.array([-math.sin(t), math.cos(t)])
            f1, f2 = DA @ xb, DA @ yb
            rows = VGroup(
                MathTex(r"\beta = %d^\circ" % round(math.degrees(t)), color=YELLOW, font_size=36),
                MathTex(r"d_b = (", "%.3f" % f1, ",\\ ", "%.3f" % f2, r",\ 0)^{\mathsf T}\ \mathrm{m}", font_size=36),
                MathTex(r"|\boldsymbol d| = \sqrt{d_{b1}^2 + d_{b2}^2} = %.3f\ \mathrm{m}" % math.hypot(f1, f2), font_size=34),
                MathTex(r"d_a = (0.300,\ 0.200,\ 0)^{\mathsf T}\ \mathrm{m}", font_size=32, color=GREY_B))
            rows[1][1].set_color(RED)
            rows[1][3].set_color(GREEN)
            return rows.arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(np.array([3.3, 0.6, 0]))

        fb = always_redraw(frame_b)
        nums = always_redraw(numbers)
        self.add(fb, nums)
        self.caption("{b} 先与 {a} 重合：两套分量相同", "At first {b} coincides with {a}: the same components")
        self.caption("转动 {b}：箭头不动，投影到 {b} 轴上的长度在变", "Turn {b}: the arrow stays, its projections on the {b} axes change", wait=0)
        self.play(beta.animate.set_value(math.radians(30)), run_time=3, rate_func=smooth)
        self.caption("β = 30°：算例 3.1.1，d 几乎全落在 x_b 方向上", "β = 30°: Example 3.1.1, d lies almost along x_b")
        self.wait(1)
        self.caption("继续转动，分量可正可负，长度始终是 0.361 m", "Keep turning: components change sign, the length stays 0.361 m", wait=0)
        self.play(beta.animate.set_value(math.radians(100)), run_time=3, rate_func=smooth)
        self.play(beta.animate.set_value(math.radians(-20)), run_time=3, rate_func=smooth)
        self.play(beta.animate.set_value(math.radians(30)), run_time=2, rate_func=smooth)
        self.wait(0.5)
        self.card([["矢量与分量", "Vector and components"],
                   ["箭头 d 与坐标系无关；分量 d_a、d_b 随坐标系而变", "The arrow d is frame-free; its components d_a, d_b depend on the frame"],
                   MathTex(r"|\boldsymbol d| = \sqrt{d_a^{\mathsf T}d_a} = \sqrt{d_b^{\mathsf T}d_b}", font_size=44)])
