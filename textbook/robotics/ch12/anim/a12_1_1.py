"""动画 12.1.1（配图 12.1.1）：平面 3R 臂依次只转动一个关节；转动的部分绕这个关节的轴整体转动，关节以内不动。"""
from manim import *
from wq_anim import *
import numpy as np

S = 6.0                                   # 1 m 画成 6 个单位
LEN = [0.425 * S, 0.392 * S, 0.1 * S]
O = np.array([-3.4, -1.3, 0])


class Lesson(Base):
    def construct(self):
        self.title("12.1", "一个关节转动时，末端怎样运动", "Turning one joint at a time")
        t = [ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)]
        hot = ValueTracker(-1)

        def build():
            ang = [x.get_value() for x in t]
            pts = planar_fk(O, ang, LEN)
            g = VGroup()
            k = int(hot.get_value())
            for i, (p, q) in enumerate(zip(pts, pts[1:])):
                col = ORANGE if (k >= 0 and i >= k) else STEEL
                g.add(Line(p, q, color=col, stroke_width=12 - 2 * i))
            for i, p in enumerate(pts[:-1]):
                g.add(Dot(p, radius=0.12, color=YELLOW if i == k else WHITE))
            g.add(Dot(pts[-1], radius=0.07, color=WHITE))
            return g

        arm_m = always_redraw(build)
        base = Polygon(O + LEFT * 0.45 + DOWN * 0.3, O + RIGHT * 0.45 + DOWN * 0.3, O + RIGHT * 0.22, O + LEFT * 0.22,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        zero = VGroup(*[DashedLine(p, q, color=GREY_B, stroke_width=3) for p, q in
                        zip(planar_fk(O, [0, 0, 0], LEN), planar_fk(O, [0, 0, 0], LEN)[1:])])
        qlabels = VGroup(*[MathTex(f"q_{i + 1}", color=YELLOW, font_size=30).next_to(p, DOWN, buff=0.35)
                           for i, p in enumerate(planar_fk(O, [0, 0, 0], LEN)[:3])])
        self.play(FadeIn(base), Create(zero), FadeIn(arm_m), Write(qlabels))
        self.caption("零位：三个关节角都为零，三段连杆排成一直线", "Home: all joint angles zero, the links in a line")

        trace = TracedPath(lambda: planar_fk(O, [x.get_value() for x in t], LEN)[-1], stroke_color=ORANGE, stroke_width=3)
        self.add(trace)
        steps = [(2, -70, "只转关节 3：只有最外面一小段绕 q₃ 转动", "Joint 3 only: just the last link turns about q₃"),
                 (1, 45, "只转关节 2：关节 2 以外的部分绕 q₂ 整体转动", "Joint 2 only: everything beyond it turns about q₂ as one body"),
                 (0, 35, "只转关节 1：整条手臂绕 q₁ 转动", "Joint 1 only: the whole arm turns about q₁")]
        for k, deg, zt, et in steps:
            hot.set_value(k)
            self.caption(zt, et, wait=0)
            self.play(t[k].animate.set_value(deg), run_time=2.2, rate_func=smooth)
            self.wait(0.6)
            self.play(t[k].animate.set_value(0), run_time=1.4, rate_func=smooth)
        hot.set_value(-1)
        self.caption("末端走的都是圆弧：圆心在转动的那个关节的轴上，关节以内的连杆不动",
                     "The tip moves on circles about the turning joint's axis; links inside it stay put")
        self.wait(0.5)
        self.card([["关节旋量", "The joint screw"],
                   MathTex(r"\mathcal{S}=\begin{pmatrix}\hat\omega\\ -\hat\omega\times q\end{pmatrix},\qquad T=e^{[\mathcal{S}]\theta}M", font_size=44),
                   ["一个关节的运动 = 绕它的轴转过 θ", "one joint's motion = a turn θ about its axis"]])
