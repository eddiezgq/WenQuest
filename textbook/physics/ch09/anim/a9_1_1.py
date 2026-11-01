"""动画 9.1.1（配图 9.1.2）：力—位移曲线下的面积就是功。气缸里的压缩空气推动活塞，推力随位移减小（与算例 9.1.2 一致：
缸径 50 mm，初始气柱 50 mm、0.50 MPa，另一侧大气 0.10 MPa，行程 100 mm）。右边描出 F(x)；再用矩形逼近面积，
矩形越窄，面积越接近精确的功 34.3 J。"""
from manim import *
from wq_anim import *
import numpy as np

A = np.pi * 0.05 ** 2 / 4                     # 活塞面积 m²
W_EXACT = 0.5e6 * A * 0.05 * np.log(3.0) - 0.1e6 * A * 0.1


def F(xmm):                                    # 推力 N，x 以 mm 计
    return (0.5e6 * 50 / (50 + xmm) - 0.1e6) * A


def mid_sum(n):
    h = 100 / n
    return sum(F((i + 0.5) * h) * h / 1000 for i in range(n))


class Lesson(Base):
    def construct(self):
        self.title("9.1", "曲线下的面积就是功", "The area under the curve is the work")
        # 左边：气缸与活塞
        cyl_x0 = -6.4
        S = 0.028                                # 画面单位 / mm
        body = Rectangle(width=150 * S + 0.1, height=1.3, color=GREY_B, stroke_width=3).move_to(np.array([cyl_x0 + 75 * S, 0.3, 0]))
        wall = Line(np.array([cyl_x0, -0.35, 0]), np.array([cyl_x0, 0.95, 0]), color=GREY_A, stroke_width=6)
        x = ValueTracker(0.0)
        gas = always_redraw(lambda: Rectangle(width=(50 + x.get_value()) * S, height=1.2, stroke_width=0, fill_color="#58a6ff",
                                              fill_opacity=0.15 + 0.35 * 50 / (50 + x.get_value())).move_to(
            np.array([cyl_x0 + (50 + x.get_value()) * S / 2, 0.3, 0])))
        piston = always_redraw(lambda: Rectangle(width=0.18, height=1.2, color=GREY_A, fill_color=GREY_C, fill_opacity=1).move_to(
            np.array([cyl_x0 + (50 + x.get_value()) * S + 0.09, 0.3, 0])))
        rod = always_redraw(lambda: Line(np.array([cyl_x0 + (50 + x.get_value()) * S + 0.18, 0.3, 0]),
                                         np.array([cyl_x0 + (50 + x.get_value()) * S + 1.6, 0.3, 0]), color=GREY_A, stroke_width=8))
        push = always_redraw(lambda: Arrow(np.array([cyl_x0 + (50 + x.get_value()) * S + 1.6, -0.55, 0]),
                                           np.array([cyl_x0 + (50 + x.get_value()) * S + 1.6 + F(x.get_value()) * 0.0028, -0.55, 0]),
                                           buff=0, color=C_F, stroke_width=6, max_tip_length_to_length_ratio=0.25))
        lab = bi(["压缩空气", "compressed air"], size=20).move_to(np.array([cyl_x0 + 0.75, 1.35, 0]))
        self.play(FadeIn(body), FadeIn(wall), FadeIn(lab))
        self.add(gas, piston, rod, push)
        # 右边：F–x 图
        ax = Axes(x_range=[0, 100, 20], y_range=[0, 800, 200], x_length=5.4, y_length=3.6,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).move_to(np.array([3.5, 0.2, 0]))
        xl = bi(["活塞位移 x / mm", "displacement x / mm"], size=18).next_to(ax, DOWN, buff=0.2)
        yl = bi(["推力 F / N", "force F / N"], size=18).next_to(ax, UP, buff=0.1).shift(LEFT * 1.9)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        curve = always_redraw(lambda: ax.plot(F, x_range=[0, max(0.5, x.get_value()), 0.5], color=C_F))
        dot = always_redraw(lambda: Dot(ax.c2p(x.get_value(), F(x.get_value())), color=C_F, radius=0.07))
        self.add(curve, dot)
        self.caption("气体膨胀，推动活塞；推力越来越小", "The gas expands and pushes the piston; the force keeps falling", wait=0)
        self.play(x.animate.set_value(100), run_time=5, rate_func=linear)
        self.wait(0.5)
        # 矩形逼近
        self.caption("把行程分成小段，每段上的力近似不变：功 ≈ Σ F Δx", "Cut the stroke into pieces; on each the force is nearly constant: W ≈ Σ F Δx", wait=0.5)
        boxes, num = None, None
        for n in (5, 10, 40):
            h = 100 / n
            new = VGroup(*[Polygon(ax.c2p(i * h, 0), ax.c2p((i + 1) * h, 0), ax.c2p((i + 1) * h, F((i + 0.5) * h)), ax.c2p(i * h, F((i + 0.5) * h)),
                                   stroke_color=BLUE, stroke_width=1.5 if n < 40 else 0.6, fill_color=BLUE, fill_opacity=0.3) for i in range(n)])
            txt = VGroup(zh(f"{n} 段", 24, BLUE), MathTex(rf"\Sigma F\Delta x = {mid_sum(n):.2f}\ \mathrm{{J}}", font_size=34, color=BLUE)
                         ).arrange(RIGHT, buff=0.35).move_to(np.array([-3.2, -1.8, 0]))
            if boxes is None:
                self.play(FadeIn(new), FadeIn(txt), run_time=1.0)
            else:
                self.play(ReplacementTransform(boxes, new), ReplacementTransform(num, txt), run_time=1.0)
            boxes, num = new, txt
            self.wait(1.0)
        area = ax.get_area(ax.plot(F, x_range=[0, 100, 0.5]), x_range=[0, 100], color=YELLOW, opacity=0.35)
        exact = MathTex(rf"W = \int_0^{{s}} F\,\mathrm{{d}}x = {W_EXACT:.2f}\ \mathrm{{J}}", font_size=34, color=YELLOW).move_to(np.array([-3.2, -2.45, 0]))
        self.play(FadeOut(boxes), FadeIn(area), Write(exact), run_time=1.2)
        self.caption("小段越窄，和越接近曲线下的面积：这个面积就是推力做的功", "The narrower the pieces, the closer the sum to the area under the curve: that area is the work", wait=2.5)
        self.card([["变力的功", "Work done by a varying force"],
                   MathTex(r"W = \int_{x_1}^{x_2} F(x)\,\mathrm{d}x", font_size=46),
                   ["等于力—位移曲线下的面积", "equals the area under the force–displacement curve"],
                   ["测得一组 (x, F) 数据，用梯形法求和就能算出功", "From measured (x, F) pairs, the trapezoid rule gives the work"]])
