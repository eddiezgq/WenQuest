"""动画 10.4.1（配图 10.4.2）：AGV 从顶装云台相机下方驶过（俯视），相机的方位角 φ 随之变化；
右侧同步画出 φ̇(t)。先 d = 0.5 m，再 d = 0.25 m：偏距减半，峰值加倍——接近正下方时出现锁孔问题。"""
from manim import *
from wq_anim import *
import numpy as np
import math

V = 1.0
SC = 0.9
CAM = np.array([-3.3, -0.1, 0])            # 俯视图中相机（竖直轴）的位置


def top(x, y):
    return CAM + SC * np.array([x, y, 0])


class Lesson(Base):
    def construct(self):
        self.title("10.4", "云台跟踪与锁孔问题", "Gimbal tracking and the keyhole")
        cam = VGroup(Square(0.3, color=GREY_B, fill_color=GREY_E, fill_opacity=1).move_to(CAM), Dot(CAM, radius=0.05, color=WHITE))
        cam_lab = zh("云台（俯视）", 20, INK).next_to(cam, LEFT, buff=0.15)
        ax = Axes(x_range=[-3, 3, 1], y_range=[-240, 0, 60], x_length=5.4, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2}).move_to(np.array([3.5, 0.0, 0]))
        xl = MathTex(r"t\ /\ \mathrm{s}", font_size=26, color=MUTED).next_to(ax.x_axis.get_right(), UR, buff=0.05)
        yl = MathTex(r"\dot\varphi\ /\ (^\circ/\mathrm{s})", font_size=26, color=MUTED).next_to(ax.c2p(-3, -30), LEFT, buff=0.1)
        ticks = VGroup(*[MathTex(str(v), font_size=20, color=MUTED).next_to(ax.c2p(0, v), LEFT, buff=0.08) for v in (-60, -120, -180, -240)])
        lim = DashedLine(ax.c2p(-3, -90), ax.c2p(3, -90), color=WHITE, stroke_width=2)
        lim_lab = zh("限速 90°/s", 18, INK).next_to(ax.c2p(3, -90), UP, buff=0.05).shift(LEFT * 0.6)
        self.play(FadeIn(cam), FadeIn(cam_lab), Create(ax), FadeIn(xl), FadeIn(yl), FadeIn(ticks), Create(lim), FadeIn(lim_lab))

        for d, col, cap in ((0.5, ORANGE, ("偏距 d = 0.5 m：最近时方位角速度 v/d ≈ 115°/s，超过限速", "Offset d = 0.5 m: at closest the pan rate v/d ≈ 115°/s exceeds the limit")),
                            (0.25, RED, ("偏距减半：峰值加倍，峰也变窄；d 趋于 0 时方位角速度趋于无穷", "Half the offset: twice the peak, and narrower; as d → 0 the pan rate grows without bound"))):
            t = ValueTracker(-3.0)
            lane = DashedLine(top(-2.6, d), top(2.6, d), color=col, stroke_width=2)
            self.play(Create(lane), run_time=0.5)
            car = always_redraw(lambda: mobile_robot(top(V * t.get_value(), d), heading=0, size=0.35, color=col))
            sight = always_redraw(lambda: Line(CAM, top(V * t.get_value(), d), color=YELLOW, stroke_width=3))
            arc = always_redraw(lambda: Arc(radius=0.55, start_angle=0, angle=math.atan2(d, V * t.get_value()) + 1e-6, arc_center=CAM,
                                            color=YELLOW, stroke_width=3))
            val = always_redraw(lambda: MathTex(r"\varphi = %d^\circ,\quad \dot\varphi = %d^\circ/\mathrm{s}" % (
                round(math.degrees(math.atan2(d, V * t.get_value()))),
                round(math.degrees(-V * d / (V * V * t.get_value() ** 2 + d * d)))), font_size=30, color=col).move_to(np.array([-3.3, 1.9, 0])))
            dot = always_redraw(lambda: Dot(ax.c2p(t.get_value(), max(-240, math.degrees(-V * d / (V * V * t.get_value() ** 2 + d * d)))), radius=0.06, color=col))
            curve = TracedPath(dot.get_center, stroke_color=col, stroke_width=4)
            self.add(sight, arc, car, val, dot, curve)
            self.caption(*cap, wait=0)
            self.play(t.animate.set_value(3.0), run_time=7, rate_func=linear)
            self.wait(0.5)
            self.play(FadeOut(car), FadeOut(sight), FadeOut(arc), FadeOut(val), FadeOut(dot), run_time=0.3)
        self.caption("目标经过正下方附近，方位角必须急转：这就是锁孔问题", "A target passing almost beneath forces the azimuth to whip round: the keyhole problem")
        self.card([["云台的方位角速度", "Pan rate of a gimbal"],
                   MathTex(r"\dot\varphi = \frac{\boldsymbol e_\varphi\cdot\boldsymbol v}{r\sin\theta},\qquad |\dot\varphi|_{\max} = \frac{v}{d}", font_size=44),
                   ["分母 r sin θ 是目标到竖直轴的距离；它趋于零，方位角速度就趋于无穷", "r sin θ is the distance to the vertical axis; as it vanishes the pan rate blows up"]])
