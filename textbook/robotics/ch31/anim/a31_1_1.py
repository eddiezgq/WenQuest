"""动画 31.1.1（配图 31.1.1）：截面法。
(1) WQ-CR5 手臂水平伸直、带 5 kg：在大臂上切一刀，外侧各零件的重力（J3 模组 2 kg、小臂与罩壳、腕部模组、法兰、负载）合成截面上的剪力 V 和弯矩 M。
(2) 刀口从 J2 移到小臂末端：剪力图、弯矩图一段段长出来；J3 处剪力突降（J3 模组的重量不再在外侧）；
    弯矩图在 J2、J3 处的值 91.3、41.1 N·m 就是两个关节的重力矩（程序 31.1.1）。"""
from manim import *
from wq_anim import *
import numpy as np

# 程序 31.1.1 的结果（离 J2 的距离 m → 剪力 N、弯矩 N·m），线性近似足够画图
V_U = (131.4, 119.8)
V_F = (100.2, 91.7)
M_U = (91.3, 41.1)
M_F = (41.1, 6.5)


def shear(x):
    if x <= 0.40:
        return V_U[0] + (V_U[1] - V_U[0]) * x / 0.40
    return V_F[0] + (V_F[1] - V_F[0]) * (x - 0.40) / 0.36


def moment(x):
    """M = 端部弯矩 + 端部剪力 × 距离 + 均布自重（大臂 29.1 N/m、小臂 23.6 N/m）× 距离² / 2"""
    if x <= 0.40:
        d = 0.40 - x
        return 41.06 + 119.8 * d + 29.1 * d * d / 2
    d = 0.76 - x
    return 6.52 + 91.7 * d + 23.6 * d * d / 2


class Lesson(Base):
    def construct(self):
        self.title("31.1", "截面法：手臂里面的力", "The method of sections: forces inside the arm")
        s = 9.0                                   # 1 m = 9 格
        o = np.array([-5.6, 1.75, 0])
        X = lambda x: o + RIGHT * s * x          # noqa: E731
        up = Line(X(0), X(0.40), color=STEEL, stroke_width=16)
        fo = Line(X(0.40), X(0.76), color=GREEN, stroke_width=12)
        j2 = Circle(radius=0.32, color=BLUE, fill_opacity=0.8).move_to(X(0))
        j3 = Circle(radius=0.26, color=BLUE, fill_opacity=0.8).move_to(X(0.40))
        wrist = Line(X(0.76), X(0.86), color=ORANGE, stroke_width=10)
        tool = Line(X(0.86), X(0.86) + DOWN * 1.0, color=WHITE, stroke_width=4)
        load = Square(side_length=0.45, color=YELLOW, fill_opacity=0.7).next_to(tool, DOWN, buff=0)
        arm = VGroup(up, fo, j2, j3, wrist, tool, load)
        self.play(FadeIn(arm), run_time=1.0)
        lab = VGroup(zh("J2", 22).next_to(j2, UP, buff=0.15), zh("J3", 22).next_to(j3, UP, buff=0.15), zh("5 kg", 22, YELLOW).next_to(load, RIGHT))
        self.play(FadeIn(lab))
        # (1) 切一刀
        xc = ValueTracker(0.20)
        cut = always_redraw(lambda: DashedLine(X(xc.get_value()) + UP * 0.7, X(xc.get_value()) + DOWN * 0.7, color=RED, stroke_width=4))
        self.play(Create(cut))
        weights = VGroup(*[Arrow(X(x) + UP * 0.1, X(x) + DOWN * (0.25 + 0.012 * m * 9.81), color=C_F, buff=0, stroke_width=4)
                           for x, m in ((0.40, 2.0), (0.58, 0.86), (0.76, 2.6), (0.86, 1.55))])
        wl = Arrow(load.get_bottom(), load.get_bottom() + DOWN * 0.5, color=YELLOW, buff=0, stroke_width=5)
        self.play(LaggedStart(*[GrowArrow(a) for a in weights], GrowArrow(wl), lag_ratio=0.2), run_time=1.5)
        self.caption("截面外侧所有重力的合力 = 剪力 V，对截面的合力矩 = 弯矩 M",
                     "All the weights outside the cut add up to the shear V and, about the cut, to the bending moment M", wait=1.5)
        # (2) 刀口移动，内力图长出来
        g0 = np.array([-5.6, -0.6, 0])
        axV = Line(g0, g0 + RIGHT * s * 0.86, color=GREY_B)
        axM = Line(g0 + DOWN * 1.7, g0 + DOWN * 1.7 + RIGHT * s * 0.86, color=GREY_B)
        self.play(Create(axV), Create(axM), FadeIn(zh("剪力 V", 20, BLUE).next_to(axV, LEFT)), FadeIn(zh("弯矩 M", 20, ORANGE).next_to(axM, LEFT)))
        kV, kM = 0.008, 0.012

        def curves():
            x1 = xc.get_value()
            xs = np.linspace(0.0, max(x1, 0.001), 60)
            pv = [g0 + RIGHT * s * x + UP * kV * shear(x) for x in xs]
            pm = [g0 + DOWN * 1.7 + RIGHT * s * x + UP * kM * moment(x) for x in xs]
            return VGroup(VMobject(color=BLUE, stroke_width=4).set_points_as_corners(pv),
                          VMobject(color=ORANGE, stroke_width=4).set_points_as_corners(pm))
        cv = always_redraw(curves)
        rd = always_redraw(lambda: VGroup(zh(f"V = {shear(xc.get_value()):.1f} N", 22, BLUE),
                                          zh(f"M = {moment(xc.get_value()):.1f} N·m", 22, ORANGE)).arrange(RIGHT, buff=0.6).move_to([2.6, 3.0, 0]))
        self.add(cv, rd)
        xc.set_value(0.0)
        self.play(xc.animate.set_value(0.399), run_time=2.5, rate_func=linear)
        self.caption("到 J3：剪力少了大臂自己的重量，弯矩从 91.3 降到 41.1 N·m",
                     "At J3 the shear has lost the upper arm's own weight and M has fallen from 91.3 to 41.1 N·m", wait=1.0)
        self.play(xc.animate.set_value(0.759), run_time=2.0, rate_func=linear)
        self.caption("过了 J3，J3 模组不再在外侧，剪力突降一块；弯矩一路降到小臂末端",
                     "Past J3 the J3 module is no longer outside: the shear drops; M keeps falling to the forearm's end", wait=1.5)
        self.card([["截面法", "The method of sections"],
                   ["截面上的力 = 外侧所有重力的合力与合力矩", "Forces on a cut = resultant force and moment of everything outside"],
                   ["关节处的弯矩就是关节的重力矩：J2 91.3、J3 41.1 N·m", "The moment at a joint is its gravity torque: J2 91.3, J3 41.1 N·m"],
                   ["偏置腕还让管子受 7.0 N·m 的扭矩", "The offset wrist also twists the tubes with 7.0 N·m"]])
