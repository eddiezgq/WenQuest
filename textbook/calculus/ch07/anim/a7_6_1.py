"""动画 7.6.1（配图 7.6.1）：y = eˣ 在 (1, e) 处的切线三角形（横 0.5、纵 0.5e）沿 y = x 翻折，成为 y = ln x 在 (e, 1) 处的切线三角形
（横 0.5e、纵 0.5），斜率变为倒数 1/e；再看 y = x³ 在原点的水平切线，翻折后成为 ∛x 的竖直切线。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("7.6", "反函数：斜率取倒数", "Inverse functions: slopes turn into reciprocals")
        ax = Axes(x_range=[-2, 4.5, 1], y_range=[-2, 4.5, 1], x_length=6.5, y_length=6.5, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.4 + LEFT * 1.5)
        diag = DashedLine(ax.c2p(-2, -2), ax.c2p(4.5, 4.5), color=GREY_B)
        f = ax.plot(np.exp, x_range=[-2, 1.5], color=STEEL, stroke_width=4)
        self.play(Create(ax), Create(diag), Create(f))
        e = math.e
        tri = VGroup(Line(ax.c2p(1, e), ax.c2p(1.5, e), color=YELLOW, stroke_width=4),
                     Line(ax.c2p(1.5, e), ax.c2p(1.5, e + 0.5 * e), color=ORANGE, stroke_width=4),
                     Line(ax.c2p(0.7, e - 0.3 * e), ax.c2p(1.6, e + 0.6 * e), color=RED, stroke_width=3))
        self.play(Create(tri))
        lab = zh("斜率 = 纵 / 横 = e", 26, INK).to_corner(UR, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(lab))
        self.caption("eˣ 在 (1, e) 处的切线：横走 0.5，纵升 0.5e，斜率 e", "Tangent of eˣ at (1, e): across 0.5, up 0.5e, slope e")
        grp = VGroup(f.copy(), tri.copy())
        M = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
        O = ax.c2p(0, 0)
        self.play(grp.animate.apply_function(lambda p: O + M @ (p - O)), run_time=3)
        lab2 = zh("翻折后：横与纵对调，斜率 = 1/e", 26, YELLOW).next_to(lab, DOWN, buff=0.2).align_to(lab, RIGHT)
        self.play(FadeIn(lab2))
        self.caption("沿 y = x 翻折：得到 ln x，切线的横与纵对调", "Folding over y = x gives ln x; across and up swap")
        self.wait(1)
        self.play(*[FadeOut(m) for m in (f, tri, grp, lab, lab2)])
        g = ax.plot(lambda x: x ** 3, x_range=[-1.3, 1.3], color=STEEL, stroke_width=4)
        flat = Line(ax.c2p(-1.2, 0), ax.c2p(1.2, 0), color=RED, stroke_width=4)
        self.play(Create(g), Create(flat))
        self.caption("y = x³ 在原点的切线是水平的：斜率 0", "y = x³ has a horizontal tangent at 0: slope 0")
        grp2 = VGroup(g.copy(), flat.copy())
        self.play(grp2.animate.apply_function(lambda p: O + M @ (p - O)), run_time=3)
        self.caption("翻折后变成竖直切线：1/0 不存在，∛x 在 0 处不可导", "It folds into a vertical tangent: 1/0 does not exist")
        self.wait(1)
        self.card([["反函数的导数是原函数导数的倒数", "The inverse's derivative is the reciprocal"],
                   MathTex(r"\frac{dx}{dy}=\frac{1}{dy/dx}\qquad (f'(x_0)\ne 0)", font_size=48)])
