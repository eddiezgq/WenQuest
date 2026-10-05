"""动画 7.1.1（配图 7.1.1）：静摩擦到动摩擦。拉力从零慢慢增大，零件盒不动，静摩擦力等于拉力；
达到最大静摩擦力 μ_s F_N 时盒子开始滑动，摩擦力降到动摩擦力 μ_k F_N。右边同时画出摩擦力—拉力图。"""
from manim import *
from wq_anim import *
import numpy as np

FS, FK, FMAX = 8.83, 6.87, 12.0      # 最大静摩擦力、动摩擦力、拉力的最大值（N），与图 7.1.1 一致（m = 2.0 kg，μ_s = 0.45，μ_k = 0.35）
K = 0.16                             # 力箭头：画面单位 / N


def friction(F):
    return F if F <= FS else FK


class Lesson(Base):
    def construct(self):
        self.title("7.1", "静摩擦与动摩擦", "Static and kinetic friction")
        floor = Line(np.array([-6.6, -1.6, 0]), np.array([-0.6, -1.6, 0]), color=GREY_B)
        shift = ValueTracker(0.0)
        box = always_redraw(lambda: Square(side_length=1.1, color="#d29922", fill_opacity=0.85).move_to(np.array([-4.6 + shift.get_value(), -1.05, 0])))
        self.play(Create(floor), FadeIn(box))
        ax = Axes(x_range=[0, 12, 2], y_range=[0, 12, 2], x_length=4.8, y_length=3.5, axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).move_to(np.array([3.5, 0.1, 0]))
        xl = bi(["拉力 / N", "pull / N"], size=20).next_to(ax, DOWN, buff=0.25)
        yl = bi(["摩擦力 / N", "friction / N"], size=20).next_to(ax, UP, buff=0.15).shift(LEFT * 1.6)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        F = ValueTracker(0.0)
        pull = always_redraw(lambda: Arrow(np.array([-4.05 + shift.get_value(), -1.05, 0]), np.array([-4.05 + shift.get_value() + K * F.get_value() + 0.01, -1.05, 0]),
                                           buff=0, color=BLUE, stroke_width=6, max_tip_length_to_length_ratio=0.3))
        fric = always_redraw(lambda: Arrow(np.array([-4.6 + shift.get_value(), -1.6, 0]), np.array([-4.6 + shift.get_value() - K * friction(F.get_value()) - 0.01, -1.6, 0]),
                                           buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.3))
        curve = always_redraw(lambda: ax.plot(lambda x: friction(x), x_range=[0, max(0.05, F.get_value()), 0.02], color=RED, use_smoothing=False, discontinuities=[FS]))
        dot = always_redraw(lambda: Dot(ax.c2p(F.get_value(), friction(F.get_value())), color=RED, radius=0.07))
        self.add(pull, fric, curve, dot)
        self.caption("拉力慢慢增大，盒子不动：静摩擦力随拉力增大，与拉力大小相等", "The pull grows, the box stays: static friction grows with it and matches it", wait=0)
        self.play(F.animate.set_value(FS - 0.01), run_time=5, rate_func=linear)
        mark = DashedLine(ax.c2p(0, FS), ax.c2p(FS, FS), color=GREY_B)
        lab = MathTex(r"\mu_\mathrm{s}F_\mathrm{N}", font_size=30).next_to(ax.c2p(0, FS), LEFT, buff=0.1)
        self.play(Create(mark), FadeIn(lab))
        self.caption("拉力达到最大静摩擦力，盒子开始滑动", "When the pull reaches the maximum static friction, the box starts to slide", wait=0)
        self.play(F.animate.set_value(FS + 0.01), run_time=0.3)
        lab2 = MathTex(r"\mu_\mathrm{k}F_\mathrm{N}", font_size=30).next_to(ax.c2p(FMAX, FK), UP, buff=0.12)
        self.play(F.animate(rate_func=linear).set_value(10.5), shift.animate(rate_func=rate_functions.ease_in_quad).set_value(2.0), FadeIn(lab2), run_time=3)   # 拉力大于动摩擦力，盒子加速
        self.caption("滑动以后，摩擦力降为动摩擦力，几乎不随拉力和速度变化", "Once sliding, friction drops to the kinetic value, nearly independent of pull and speed", wait=2.0)
        self.card([["静摩擦与动摩擦", "Static and kinetic friction"],
                   ["静摩擦力“需要多少给多少”，但有上限：最大静摩擦力", "Static friction gives what is needed, up to a limit: the maximum static friction"],
                   ["滑动时为动摩擦力，一般比最大静摩擦力小", "While sliding it is the kinetic friction, usually smaller than the maximum static friction"],
                   ["所以起动比维持滑动更费力", "So starting a slide takes more force than keeping it going"]])
