"""动画 54.1.1（配图 54.1.4）：误差敏感方向——刀尖沿法向移动，车出的半径一样多地变；沿切向移动，半径几乎不变。
画面放大画出；右侧读数按 Ø35 外圆（R = 17.5 mm）、偏移 0.01 mm 的真实值（hub/accuracy.py diameter_error）。"""
from manim import *
from wq_anim import *
import numpy as np

R_REAL, D_REAL = 17.5, 0.01


class Lesson(Base):
    def construct(self):
        self.title("54.1", "误差敏感方向", "The error-sensitive direction")
        c0 = np.array([-2.2, -0.3, 0])
        r0 = 1.8
        dy = ValueTracker(0.0)
        dz = ValueTracker(0.0)

        def scene():
            tip = c0 + np.array([-r0 - dy.get_value(), dz.get_value(), 0])
            r = np.linalg.norm(tip - c0)
            g = VGroup(Circle(radius=r0, color=MUTED, stroke_width=2).move_to(c0),
                       Circle(radius=r, color=RED, stroke_width=3).move_to(c0),
                       Dot(c0, color=INK, radius=0.04),
                       Line(c0, tip, color=BLUE, stroke_width=2),
                       Triangle(color=ORANGE, fill_opacity=1).scale(0.18).rotate(-PI / 2).move_to(tip + np.array([-0.18, 0, 0])))
            return g

        sc = always_redraw(scene)
        self.play(FadeIn(sc))
        self.caption("车外圆：刀尖到工件轴线的距离就是车出的半径", "Turning: the distance from tool tip to axis is the radius you get")

        def readout():
            k = 0.01 / 0.6                      # 画面上 0.6 个单位代表 0.01 mm
            ry, rz = dy.get_value() * k, dz.get_value() * k
            dd = 2 * (np.hypot(R_REAL + ry, rz) - R_REAL) * 1000
            t = VGroup(zh(f"法向偏移 {ry * 1000:5.1f} µm", 26, RED),
                       zh(f"切向偏移 {rz * 1000:5.1f} µm", 26, BLUE),
                       zh(f"直径变化 {dd:7.3f} µm", 30, INK)).arrange(DOWN, aligned_edge=LEFT).move_to(np.array([3.2, 0.3, 0]))
            return t

        rd = always_redraw(readout)
        self.play(FadeIn(rd))
        self.play(dy.animate.set_value(0.6), run_time=2)
        self.caption("沿法向（y）移动 0.01 mm：直径变 0.02 mm——这是误差敏感方向", "0.01 mm along the normal (y): the diameter changes 0.02 mm — the sensitive direction")
        self.play(dy.animate.set_value(0.0), run_time=1)
        self.play(dz.animate.set_value(0.6), run_time=2)
        self.caption("沿切向（z）移动同样多：直径只变约 0.006 µm，可以不管", "The same amount along the tangent (z): only about 0.006 µm — negligible")
        self.play(dz.animate.set_value(0.0), run_time=1)
        self.card([["原始误差在误差敏感方向（加工表面的法向）上影响最大", "Errors matter most along the error-sensitive direction (the surface normal)"],
                   ["车削时敏感方向固定（水平），镗削时随镗刀转动", "In turning it is fixed (horizontal); in boring it turns with the bar"]])
