"""动画 12.4.1（配图 12.4.1）：指数积的第二种读法与写反次序的错误。
先“从里往外”：转关节 1，关节 2、3 的轴跟着移动，再绕新轴转——到达与空间形式相同的形态；
再演示写反次序：每次都绕零位时的点转，末端落到工作空间以外。关节角取算例 12.2.1。"""
from manim import *
from wq_anim import *
import numpy as np

S = 4.2
LEN = [0.425 * S, 0.392 * S, 0.1 * S]
O = np.array([-3.0, -1.4, 0])
TH = [30.0, 45.0, -90.0]


def rot_about(p, c, deg):
    a = np.radians(deg)
    d = p - c
    return c + np.array([d[0] * np.cos(a) - d[1] * np.sin(a), d[0] * np.sin(a) + d[1] * np.cos(a), 0])


class Lesson(Base):
    def construct(self):
        self.title("12.4", "从里往外读，以及写反次序会怎样", "Reading inside-out, and the wrong order")
        zero_pts = planar_fk(O, [0, 0, 0], LEN)
        reach = sum(LEN)
        circle = DashedVMobject(Circle(radius=reach, color=GREY_B, stroke_width=2).move_to(O), num_dashes=60)
        zero = VGroup(*[DashedLine(p, q, color=GREY_B, stroke_width=3) for p, q in zip(zero_pts, zero_pts[1:])])
        self.play(Create(circle), Create(zero))
        self.caption("虚线圆：三段连杆伸直时末端能到达的最远处", "Dashed circle: the farthest the tip can reach")

        # ---- 从里往外：关节角是相对角，planar_fk 正好就是这种读法
        t = [ValueTracker(0.0) for _ in range(3)]

        def build():
            pts = planar_fk(O, [x.get_value() for x in t], LEN)
            g = VGroup(*[Line(p, q, color=STEEL, stroke_width=11 - 2 * i) for i, (p, q) in enumerate(zip(pts, pts[1:]))])
            g.add(*[Dot(p, radius=0.1, color=RED if i > 0 else WHITE) for i, p in enumerate(pts[:-1])], Dot(pts[-1], radius=0.06))
            return g

        arm_m = always_redraw(build)
        self.add(arm_m)
        self.caption("从里往外：先转关节 1，关节 2、3 的轴（红点）跟着走", "Inside-out: turn joint 1 first; the axes of joints 2 and 3 (red) go along")
        self.play(t[0].animate.set_value(TH[0]), run_time=2)
        self.caption("再绕关节 2 的新位置转，然后关节 3", "Then turn about joint 2 where it is now, then joint 3", wait=0)
        self.play(t[1].animate.set_value(TH[1]), run_time=1.8)
        self.play(t[2].animate.set_value(TH[2]), run_time=1.5)
        good = planar_fk(O, TH, LEN)[-1]
        star = Star(n=5, outer_radius=0.16, color=YELLOW, fill_opacity=1).move_to(good)
        self.play(FadeIn(star))
        self.caption("与从外往里（空间形式）到达同一个形态", "The same configuration as outermost-first (space form)")

        # ---- 写反次序：每次都绕零位时的点转
        s = ValueTracker(0.0)
        stages = [(zero_pts[0], TH[0]), (zero_pts[1], TH[1]), (zero_pts[2], TH[2])]

        def wrong_pts():
            v = s.get_value()
            pts = [np.array(p) for p in zero_pts]
            for i, (c, a) in enumerate(stages):
                f = min(max(v - i, 0.0), 1.0)
                if f > 0:
                    pts = [rot_about(p, c, a * f) for p in pts]
            return pts

        def wrong():
            pts = wrong_pts()                    # 只画末端（最后一段和末端点）：公式只作用在 M 上
            return VGroup(Line(pts[2], pts[3], color=RED, stroke_width=7), Dot(pts[-1], radius=0.09, color=RED))

        self.play(FadeOut(arm_m), run_time=0.5)
        bad = always_redraw(wrong)
        marks = VGroup(*[Dot(p, radius=0.12, color=ORANGE) for p in zero_pts[:3]])
        path = TracedPath(lambda: wrong_pts()[-1], stroke_color=RED, stroke_width=3)
        self.add(bad, path)
        self.play(FadeIn(marks))
        self.caption("写反次序：每一步都绕零位时的点（橙色）转", "Wrong order: every turn about the home points (orange)", wait=0.5)
        for i in range(3):
            self.play(s.animate.set_value(i + 1), run_time=1.6)
        self.caption("后两次转动绕的是空中的点：那里早已没有关节，末端跑出了虚线圆",
                     "The last two turns pivot about empty space; the tip leaves the circle", wait=2)
        self.card([["次序不能写反", "Never reverse the order"],
                   MathTex(r"e^{[\mathcal{S}_1]\theta_1}e^{[\mathcal{S}_2]\theta_2}=e^{[\mathcal{S}_2']\theta_2}e^{[\mathcal{S}_1]\theta_1},\quad \mathcal{S}_2'=[\mathrm{Ad}_{E_1}]\mathcal{S}_2", font_size=40),
                   ["从外往里：轴都在零位；从里往外：每转一个关节就更新外侧各轴",
                    "outermost-first: axes stay at home; inside-out: update the outer axes after each turn"]])
