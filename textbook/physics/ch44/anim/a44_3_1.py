"""动画 44.3.1（配图 44.3.1）：无限深势阱中只有在两壁处为零的波才“装得下”，L = nλ/2；
每个驻波对应一个能级，E_n ∝ n²。势阱中的驻波就是能级。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("44.3", "势阱中的驻波就是能级", "Standing waves in a well are the energy levels")
        x0, x1, ybot = -3.0, 1.0, -2.6
        walls = VGroup(Line([x0, ybot, 0], [x0, 2.8, 0], color=GREY_B, stroke_width=8),
                       Line([x1, ybot, 0], [x1, 2.8, 0], color=GREY_B, stroke_width=8),
                       Line([x0, ybot, 0], [x1, ybot, 0], color=GREY_B, stroke_width=3))
        self.play(Create(walls))
        L = x1 - x0
        lam = ValueTracker(2.9)
        wave = always_redraw(lambda: FunctionGraph(lambda x: 0.45 * np.sin(2 * np.pi * (x - x0) / lam.get_value()),
                                                   x_range=[x0, x1], color=BLUE).shift(UP * 0.0))
        self.add(wave)
        self.caption("任意波长的波，在右壁处一般不为零：装不进去", "A wave of arbitrary wavelength is not zero at the right wall: it does not fit")
        self.play(lam.animate.set_value(2 * L), run_time=2)
        self.caption("只有 L = nλ/2 的波在两壁处都为零", "Only waves with L = nλ/2 vanish at both walls")
        self.play(FadeOut(wave))
        scale = 0.27                                     # 画面中 1 个 E1 的高度
        levels = VGroup()
        for n in (1, 2, 3):
            En = scale * n * n
            y = ybot + 0.3 + En
            lv = DashedLine([x0, y, 0], [x1, y, 0], color=ORANGE)
            w = FunctionGraph(lambda x, n=n: 0.32 * np.sin(n * np.pi * (x - x0) / L), x_range=[x0, x1], color=BLUE).shift(UP * y)
            lbl = MathTex(f"n={n}", font_size=30).next_to(lv, RIGHT, buff=0.2)
            e = MathTex(f"E_{n}={n * n}E_1" if n > 1 else "E_1", font_size=30, color=ORANGE).next_to(lbl, RIGHT, buff=0.4)
            self.play(Create(lv), Create(w), Write(lbl), Write(e), run_time=1.2)
            levels.add(lv, w, lbl, e)
        self.caption("节点越多，波长越短，动量越大，能量越高：E 与 n² 成正比",
                     "More nodes, shorter wavelength, larger momentum, higher energy: E grows as n²")
        self.caption("最低能量 E₁ 不为零：零点能", "The lowest energy E₁ is not zero: the zero-point energy")
        self.card([["无限深势阱", "Infinite square well"],
                   MathTex(r"E_n=\frac{n^2\pi^2\hbar^2}{2mL^2},\quad n=1,2,3,\dots", font_size=44),
                   ["能级就是驻波：量子化来自边界条件", "Levels are standing waves: quantisation comes from the boundary conditions"]])
