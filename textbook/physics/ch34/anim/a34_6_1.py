"""动画 34.6.1（配图 34.6.1）：交流发电机。线圈在匀强磁场中匀速转动，穿过线圈的磁通量按余弦变化，
电动势按正弦变化：线圈平面与磁场平行时磁通量为零而电动势最大。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("34.6", "转动的线圈：交流发电机", "A rotating coil: the AC generator")
        c = LEFT * 3.5 + UP * 0.3
        field = VGroup(*[Arrow(c + LEFT * 2 + UP * y, c + RIGHT * 2 + UP * y, buff=0, color=BLUE, stroke_width=3) for y in (-1.2, -0.4, 0.4, 1.2)])
        self.play(FadeIn(field))
        th = ValueTracker(0.0)
        # 侧视：线圈是一条转动的线段（长 2），法线与磁场的夹角为 θ
        coil = always_redraw(lambda: Line(c + 1.0 * np.array([np.sin(th.get_value()), np.cos(th.get_value()), 0]),
                                          c - 1.0 * np.array([np.sin(th.get_value()), np.cos(th.get_value()), 0]), color=ORANGE, stroke_width=10))
        normal = always_redraw(lambda: Arrow(c, c + 1.3 * np.array([np.cos(th.get_value()), -np.sin(th.get_value()), 0]), buff=0, color=YELLOW, stroke_width=4))
        self.add(coil, normal)
        self.caption("磁场向右；侧面看，线圈是一条转动的线段，黄色箭头是线圈平面的法线", "B points right; seen edge-on the coil is a turning line, yellow is its normal")
        ax = Axes(x_range=[0, 4 * PI, PI], y_range=[-1.2, 1.2, 1], x_length=6, y_length=3, tips=False, axis_config={"color": GREY_B}).move_to(RIGHT * 3.2 + UP * 0.2)
        self.play(Create(ax), Write(VGroup(MathTex(r"\Phi\propto\cos\omega t", color=STEEL, font_size=28), MathTex(r"\mathcal{E}\propto\sin\omega t", color=ORANGE, font_size=28)).arrange(RIGHT, buff=0.6).next_to(ax, UP, buff=0.05)))
        fl = always_redraw(lambda: ax.plot(np.cos, x_range=[0, th.get_value() + 1e-3], color=STEEL))
        el = always_redraw(lambda: ax.plot(np.sin, x_range=[0, th.get_value() + 1e-3], color=ORANGE))
        self.add(fl, el)
        self.caption("法线与磁场平行时 Φ 最大、𝓔 为零；线圈平面与磁场平行时 Φ 为零、𝓔 最大", "Normal along B: Φ largest, 𝓔 zero; plane along B: Φ zero, 𝓔 largest", wait=0)
        self.play(th.animate.set_value(4 * PI), run_time=8, rate_func=linear)
        self.wait(0.5)
        self.card([["交流发电机", "AC generator"],
                   MathTex(r"\mathcal{E}=NBA\omega\sin\omega t", font_size=48),
                   ["电动机被外力带着转就是发电机：转动的电机总有反电动势", "A motor driven by an external torque is a generator: a running motor always has a back emf"]])
