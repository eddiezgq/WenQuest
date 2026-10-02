"""动画 34.1.1（配图 34.1.1）：磁铁沿轴线穿过线圈。穿过线圈的磁感线条数（磁通量）先增后减，
电动势曲线同步画出：靠近时为负，离开时为正，在磁铁穿过线圈平面的一瞬为零。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("34.1", "磁铁穿过线圈", "A magnet passing through a coil")
        a = 0.6                                         # 线圈半径（屏幕单位）
        coil = Ellipse(width=0.35, height=2 * a, color=ORANGE, stroke_width=6).move_to(LEFT * 2.5 + UP * 0.6)
        self.play(Create(coil))
        z = ValueTracker(-4.0)                           # 磁铁到线圈平面的有向距离
        def magnet():
            x = coil.get_center()[0] + 0.55 * z.get_value()
            n = Rectangle(width=0.5, height=0.3, fill_color=RED, fill_opacity=1, stroke_width=1).move_to([x + 0.25, 0.6, 0])
            s = Rectangle(width=0.5, height=0.3, fill_color=BLUE, fill_opacity=1, stroke_width=1).move_to([x - 0.25, 0.6, 0])
            return VGroup(s, n, Text("N", font_size=20).move_to(n), Text("S", font_size=20).move_to(s))
        mag = always_redraw(magnet)
        self.add(mag)
        self.caption("磁铁从左边沿线圈的轴线匀速穿过", "The magnet moves along the coil's axis at constant speed")
        # 右侧坐标：NΦ 与 ε 随时间
        ax = Axes(x_range=[-4, 4, 2], y_range=[-1.2, 1.2, 1], x_length=5.2, y_length=3.2, tips=False,
                  axis_config={"color": GREY_B}).move_to(RIGHT * 3.4 + UP * 0.2)
        lab = VGroup(MathTex(r"\Phi", color=STEEL, font_size=30).next_to(ax, UP, buff=0.05).shift(LEFT * 1.2),
                     MathTex(r"\mathcal{E}=-N\frac{\mathrm d\Phi}{\mathrm dt}", color=ORANGE, font_size=30).next_to(ax, UP, buff=0.05).shift(RIGHT * 1.2))
        self.play(Create(ax), Write(lab))
        phi = lambda zz: 1 / (1 + zz ** 2) ** 1.5
        emf = lambda zz: 3 * zz / (1 + zz ** 2) ** 2.5 / 1.72      # 缩放到峰值约 0.5（画面高度单位）
        f_line = always_redraw(lambda: ax.plot(phi, x_range=[-4, min(z.get_value(), 4) + 1e-3], color=STEEL))
        e_line = always_redraw(lambda: ax.plot(emf, x_range=[-4, min(z.get_value(), 4) + 1e-3], color=ORANGE))
        self.add(f_line, e_line)
        self.caption("靠近时穿过线圈的磁通量增大，电动势为负", "Approaching: the flux grows and the emf is negative", wait=0)
        self.play(z.animate.set_value(0), run_time=4, rate_func=linear)
        self.caption("穿过线圈平面的一瞬，Φ 最大而变化率为零，电动势为零", "Crossing the plane: Φ is largest, its rate is zero, so is the emf", wait=0.5)
        self.caption("离开时磁通量减小，电动势反向", "Leaving: the flux falls and the emf reverses", wait=0)
        self.play(z.animate.set_value(4), run_time=4, rate_func=linear)
        self.wait(1)
        self.card([["法拉第电磁感应定律", "Faraday's law of induction"],
                   MathTex(r"\mathcal{E}=-N\frac{\mathrm d\Phi}{\mathrm dt}", font_size=48),
                   ["电动势取决于磁通量变化的快慢，而不是磁通量的大小", "The emf depends on how fast the flux changes, not on how large it is"]])
