"""动画 12.2.1（配图 12.2.1）：指数积的空间形式。平面 3R 臂从零位出发，依次作用 e^[S3]θ3、e^[S2]θ2、e^[S1]θ1；
每一步转动所绕的点（红点）都还在零位时的位置。关节角取算例 12.2.1：(30°, 45°, −90°)。"""
from manim import *
from wq_anim import *
import numpy as np

S = 6.0
LEN = [0.425 * S, 0.392 * S, 0.1 * S]
O = np.array([-4.6, -1.6, 0])


class Lesson(Base):
    def construct(self):
        self.title("12.2", "指数积公式：从最后一个关节往前转", "Product of exponentials: outermost joint first")
        t = [ValueTracker(0.0), ValueTracker(0.0), ValueTracker(0.0)]

        def build():
            pts = planar_fk(O, [x.get_value() for x in t], LEN)
            g = VGroup(*[Line(p, q, color=STEEL, stroke_width=12 - 2 * i) for i, (p, q) in enumerate(zip(pts, pts[1:]))])
            g.add(*[Dot(p, radius=0.11, color=WHITE) for p in pts[:-1]], Dot(pts[-1], radius=0.07, color=WHITE))
            return g

        zero_pts = planar_fk(O, [0, 0, 0], LEN)
        zero = VGroup(*[DashedLine(p, q, color=GREY_B, stroke_width=3) for p, q in zip(zero_pts, zero_pts[1:])])
        arm_m = always_redraw(build)
        self.play(Create(zero), FadeIn(arm_m))
        formula = MathTex(r"T=", r"e^{[\mathcal{S}_1]\theta_1}", r"e^{[\mathcal{S}_2]\theta_2}", r"e^{[\mathcal{S}_3]\theta_3}", r"M",
                          font_size=46).to_corner(UR, buff=0.6).shift(DOWN * 0.9)
        for k in (1, 2, 3):
            formula[k].set_opacity(0.15)
        self.play(Write(formula))
        self.caption("从零位出发：T = M", "Start at home: T = M")

        steps = [(2, -90, 3, "先转关节 3：绕零位时的 q₃ 转 −90°", "First joint 3: turn −90° about q₃ where it sits at home"),
                 (1, 45, 2, "再转关节 2：关节 2 还没动过，它的轴仍在零位处", "Then joint 2: it has not moved, so its axis is still at home"),
                 (0, 30, 1, "最后转关节 1：整条手臂绕原点转 30°", "Last joint 1: the whole arm turns 30° about the origin")]
        for k, deg, f, zt, et in steps:
            mark = Dot(zero_pts[k], radius=0.16, color=RED)
            ring = Circle(radius=0.3, color=RED).move_to(zero_pts[k])
            self.caption(zt, et, wait=0)
            self.play(FadeIn(mark), Create(ring), formula[f].animate.set_opacity(1), run_time=0.8)
            self.play(t[k].animate.set_value(deg), run_time=2.4, rate_func=smooth)
            self.wait(0.6)
            self.play(FadeOut(mark), FadeOut(ring), run_time=0.4)
        tip = planar_fk(O, [30, 45, -90], LEN)[-1]
        res = MathTex(r"p=(0.566,\ 0.565)\ \mathrm{m}", color=YELLOW, font_size=36).next_to(formula, DOWN, buff=0.4)
        self.play(Write(res), Indicate(Dot(tip, color=YELLOW)))
        self.caption("从右往左读：先作用的是最外面的关节；每一步用的都是零位时的旋量轴",
                     "Read right to left: the outermost joint acts first, always with its home screw axis")
        self.card([["指数积公式（空间形式）", "Product of exponentials (space form)"],
                   MathTex(r"T(\theta)=e^{[\mathcal{S}_1]\theta_1}e^{[\mathcal{S}_2]\theta_2}\cdots e^{[\mathcal{S}_n]\theta_n}M", font_size=46),
                   ["只需要零位位姿 M 和零位时的各旋量轴", "all it needs: the home pose M and the home screw axes"]])
