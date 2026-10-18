"""动画 23.1.1（配图 23.1.3）：夹偏的 SH-301 毛坯绕竖直的主轴 z 转动（算例 23.1.4）。
毛坯：Ø50 mm × 182 mm、2.8 kg，I_t / I_a = 9.3。为看得清楚，夹偏角先画成 15°（放大），ω 竖直不变；
L = I ω 固定在毛坯上、随毛坯旋转；轴承力矩 M = ω × L 水平、跟着转。随后把夹偏角减到 0，L 与 ω 重合，M 消失。
最后给出 1° 夹偏、1200 r/min 时的数值（程序 23.1.1：2.0 N·m）。画面慢放：主轴约每 4 s 转一圈。"""
from manim import *
from wq_anim import *
import numpy as np
import math

IT_IA = 9.3                                    # I_t / I_a（算例 23.1.2）
SC = 1.0
O = np.array([-2.6, -1.1, 0.0])


def rz(a):
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1.0]])


def rx(a):
    return np.array([[1.0, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def P(p):
    return proj3(p, O, 1.25)


def blank(phi, al):
    """毛坯画成一个细长的八棱柱（半径 0.45、长 2.6，画图单位），轴线沿物体 z。"""
    R = rz(phi) @ rx(al)
    k = 8
    ang = [2 * math.pi * i / k for i in range(k)]
    top = [R @ np.array([0.45 * math.cos(a), 0.45 * math.sin(a), 1.3]) for a in ang]
    bot = [R @ np.array([0.45 * math.cos(a), 0.45 * math.sin(a), -1.3]) for a in ang]
    g = VGroup()
    for i in range(k):
        j = (i + 1) % k
        g.add(Polygon(P(bot[i]), P(bot[j]), P(top[j]), P(top[i]), stroke_width=1, color=GREY_B,
                      fill_color=GREY_D if i % 2 else GREY_C, fill_opacity=0.55))
    g.add(Polygon(*[P(p) for p in top], color=GREY_A, stroke_width=1.5, fill_color=GREY_B, fill_opacity=0.7))
    g.add(Line(P(R @ np.array([0, 0, -1.9])), P(R @ np.array([0, 0, 1.9])), color=YELLOW_E, stroke_width=2))
    return g


def L_of(phi, al):
    """L ∝ R diag(I_t, I_t, I_a) Rᵀ ẑ（I_a 取 1），长度归一到 2.2。"""
    R = rz(phi) @ rx(al)
    D = np.diag([IT_IA, IT_IA, 1.0])
    L = R @ D @ R.T @ np.array([0, 0, 1.0])
    return L / np.linalg.norm(L) * 2.2


class Lesson(Base):
    def construct(self):
        self.title("23.1", "夹偏的毛坯：动不平衡", "A tilted blank: dynamic unbalance")
        phi = ValueTracker(0.0)
        al = ValueTracker(math.radians(15))
        axis = DashedLine(P([0, 0, -2.0]), P([0, 0, 2.7]), color=GREY_B, dash_length=0.12)
        self.add(axis)
        self.add(Text("主轴 z", font=CJK, font_size=22, color=GREY_B).move_to(P([0, 0, 2.7]) + RIGHT * 0.7))

        def scene():
            f, a = phi.get_value(), al.get_value()
            g = VGroup(blank(f, a))
            g.add(Arrow(P([0, 0, 0]), P([0, 0, 2.5]), buff=0, color=BLUE, stroke_width=7, max_tip_length_to_length_ratio=0.12))
            L = L_of(f, a)
            g.add(Arrow(P([0, 0, 0]), P(L), buff=0, color=RED, stroke_width=7, max_tip_length_to_length_ratio=0.14))
            M = np.cross([0, 0, 1.0], L)
            n = np.linalg.norm(M)
            if n > 0.05:
                g.add(Arrow(P([0, 0, 0]), P(M / 2.2 * 2.0), buff=0, color=ORANGE, stroke_width=6, max_tip_length_to_length_ratio=0.16))
            return g

        self.add(always_redraw(scene))
        legend = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=BLUE, stroke_width=6), MathTex(r"\boldsymbol\omega", color=BLUE, font_size=34),
                   Text("主轴的角速度（竖直不变）", font=CJK, font_size=22, color=INK)).arrange(RIGHT, buff=0.2),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=RED, stroke_width=6), MathTex(r"\boldsymbol L = I\boldsymbol\omega", color=RED, font_size=34),
                   Text("角动量（随毛坯转）", font=CJK, font_size=22, color=INK)).arrange(RIGHT, buff=0.2),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=ORANGE, stroke_width=6), MathTex(r"\boldsymbol M = \boldsymbol\omega\times\boldsymbol L", color=ORANGE, font_size=34),
                   Text("轴承要给的力矩", font=CJK, font_size=22, color=INK)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(RIGHT, buff=0.5).shift(UP * 1.2)
        self.play(FadeIn(legend), run_time=0.8)
        info = always_redraw(lambda: Text(f"夹偏角 α = {math.degrees(al.get_value()):.0f}°（画面放大）", font=CJK, font_size=26,
                                          color=YELLOW).next_to(legend, DOWN, buff=0.5).align_to(legend, LEFT))
        self.add(info)
        self.caption("毛坯夹偏了：主轴转动时，角动量 L 偏离主轴，并跟着毛坯一起转",
                     "The blank is tilted: as the spindle turns, L leans off the axis and turns with the blank", wait=0)
        self.play(phi.animate.set_value(2 * TAU), run_time=8, rate_func=linear)
        self.caption("L 的方向不断改变，就要有力矩 M = ω × L：它水平、垂直于 L，也跟着转——轴承受到旋转的载荷",
                     "A changing L needs a moment M = ω × L: horizontal, turning with the blank, a rotating load on the bearings", wait=0)
        self.play(phi.animate.set_value(4 * TAU), run_time=8, rate_func=linear)
        self.caption("把毛坯夹正：转轴成了主轴，L 与 ω 重合，力矩消失",
                     "Clamp it straight: the spin axis becomes a principal axis, L lines up with ω, the moment vanishes", wait=0)
        self.play(phi.animate.set_value(6 * TAU), al.animate.set_value(0.0), run_time=8, rate_func=linear)
        self.play(phi.animate.set_value(7 * TAU), run_time=4, rate_func=linear)
        self.card([["动不平衡：质心在轴上，转轴却不是主轴", "Dynamic unbalance: CoM on the axis, but the axis is not principal"],
                   MathTex(r"|\boldsymbol M| = \omega^2\,|I_t - I_a|\,\sin\alpha\cos\alpha", font_size=44),
                   ["SH-301 毛坯夹偏 1°、1200 r/min：约 2.0 N·m，每秒转向 20 次", "SH-301 blank, 1° tilt, 1200 r/min: about 2.0 N·m, turning 20 times a second"]])
