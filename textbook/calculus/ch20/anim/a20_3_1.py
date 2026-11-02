"""动画 20.3.1（配图 20.3.1）：欠阻尼、临界阻尼、过阻尼三种响应并排——三个相同的弹簧–质量块（ω_n = 10 rad/s），
阻尼比分别为 0.2、1、2，从同一位置静止释放；右边同步画出三条位移曲线。时间放慢 4 倍。"""
from manim import *
from wq_anim import *
import numpy as np

WN = 10.0


def resp(z, t):
    if z < 1:
        wd = WN * np.sqrt(1 - z * z)
        return np.exp(-z * WN * t) * (np.cos(wd * t) + z / np.sqrt(1 - z * z) * np.sin(wd * t))
    if z == 1:
        return (1 + WN * t) * np.exp(-WN * t)
    r1, r2 = -z * WN + WN * np.sqrt(z * z - 1), -z * WN - WN * np.sqrt(z * z - 1)
    return (r1 * np.exp(r2 * t) - r2 * np.exp(r1 * t)) / (r1 - r2)


def spring(x0, x1, y, n=8, amp=0.15):
    pts = [[x0, y, 0]]
    for k in range(1, 2 * n):
        pts.append([x0 + (x1 - x0) * k / (2 * n), y + (amp if k % 2 else -amp), 0])
    pts.append([x1, y, 0])
    return VMobject(color=GREY_B, stroke_width=2).set_points_as_corners(pts)


class Lesson(Base):
    def construct(self):
        self.title("20.3", "欠阻尼、临界阻尼、过阻尼", "Underdamped, critical, overdamped")
        cases = [(0.2, STEEL, "ζ = 0.2"), (1.0, GREEN, "ζ = 1"), (2.0, ORANGE, "ζ = 2")]
        ys = [1.6, 0.0, -1.6]
        wall_x, rest_x, scale = -5.3, -2.8, 1.3
        t = ValueTracker(0.0)
        objs = VGroup()
        for (z, col, lab), y in zip(cases, ys):
            wall = Line([wall_x, y - 0.5, 0], [wall_x, y + 0.5, 0], color=GREY_B, stroke_width=6)
            sp = always_redraw(lambda y=y, z=z: spring(wall_x, rest_x + scale * resp(z, t.get_value()) - 0.35, y))
            blk = always_redraw(lambda y=y, z=z, col=col: Square(0.7, color=col, fill_opacity=0.7).move_to([rest_x + scale * resp(z, t.get_value()), y, 0]))
            tx = Text(lab, font_size=24, color=col).next_to(wall, LEFT, buff=0.15)
            objs.add(wall, sp, blk, tx)
        eq_line = DashedLine([rest_x, 2.3, 0], [rest_x, -2.3, 0], color=GREY_C)
        ax = Axes(x_range=[0, 1.5, 0.5], y_range=[-0.6, 1.0, 0.5], x_length=5.6, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).to_edge(RIGHT, buff=0.4).shift(DOWN * 0.2)
        self.play(FadeIn(objs), Create(eq_line), Create(ax))
        self.caption("同样的质量块和弹簧，只改变阻尼；从同一位置静止释放", "Same mass and spring, different damping; released from rest", wait=0.3)
        curves = VGroup(*[always_redraw(lambda z=z, col=col: ax.plot(lambda s: resp(z, s), x_range=[0, max(t.get_value(), 1e-3)], color=col, stroke_width=3))
                          for z, col, _ in cases])
        self.add(curves)
        self.play(t.animate.set_value(1.5), run_time=6, rate_func=linear)
        self.caption("ζ = 0.2 来回振荡；ζ = 1 是不振荡的情形中回得最快的；ζ = 2 慢慢爬回去", "ζ = 0.2 oscillates; ζ = 1 is the fastest without oscillating; ζ = 2 creeps back", wait=1.2)
        self.play(FadeOut(objs), FadeOut(eq_line), FadeOut(ax), FadeOut(curves))
        self.card([["二阶系统的三种自由响应", "Three free responses of a second-order system"],
                   MathTex(r"\ddot x+2\zeta\omega_n\dot x+\omega_n^2x=0,\qquad r=-\zeta\omega_n\pm\omega_n\sqrt{\zeta^2-1}", font_size=40),
                   ["ζ < 1 欠阻尼（复根，振荡）；ζ = 1 临界阻尼（重根）；ζ > 1 过阻尼（两个负实根）", "ζ < 1 underdamped (complex roots); ζ = 1 critical (double root); ζ > 1 overdamped (two negative roots)"]])
