"""动画 33.10.1（配图 33.10.2）：关节输出轴扭转一个很小的角度，经过近 1 m 的手臂放大成末端的偏移；
空心轴把材料放到外圈，同样的质量扭转刚度大得多。"""
from manim import *
from wq_anim import *
import numpy as np

J = np.array([-5.0, -1.2, 0])       # 关节
L = 8.4                              # 屏幕上的工作半径


class Lesson(Base):
    def construct(self):
        self.title("33.10", "扭转一点点，末端偏很多", "A tiny twist, a large tool deflection")
        th = ValueTracker(0.0)
        hub = Circle(radius=0.45, color=GREY_B, fill_color=GREY_D, fill_opacity=1).move_to(J)
        arm0 = Line(J, J + RIGHT * L, color=GREY_C, stroke_width=4).set_opacity(0.5)
        arm = always_redraw(lambda: Line(J, J + L * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0]),
                                         color="#d29922", stroke_width=14))
        tool = always_redraw(lambda: Dot(J + L * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0]), color=YELLOW, radius=0.12))
        self.play(FadeIn(hub), FadeIn(arm0), FadeIn(arm), FadeIn(tool))
        self.caption("J2 的输出轴传递力矩 T，扭转角 θ = Σ TLi /(GJi)", "J2's output shaft carries the torque T and twists by θ = Σ TLi /(GJi)")
        self.play(th.animate.set_value(0.08), run_time=2)
        br = always_redraw(lambda: BraceBetweenPoints(J + RIGHT * L, J + L * np.array([np.cos(th.get_value()), np.sin(th.get_value()), 0]), direction=RIGHT))
        d = MathTex(r"\delta=\theta R", font_size=36, color=YELLOW).move_to(J + RIGHT * (L + 1.1) + UP * 0.35)
        self.play(FadeIn(br), Write(d))
        self.caption("末端偏移 δ = θR：工作半径接近 1 m，扭转角被放大近千倍（图中放大画出）",
                     "Tool deflection δ = θR: with a reach near 1 m the twist is magnified about a thousand times (drawn exaggerated)")
        self.wait(1)
        self.play(FadeOut(VGroup(br, d)), th.animate.set_value(0.0))
        # 实心轴与空心轴：同样的截面积
        c1, c2 = np.array([-2.5, 2.0, 0]), np.array([2.5, 2.0, 0])
        solid = Circle(radius=0.8, color=GREY_B, fill_color=BLUE_D, fill_opacity=0.8).move_to(c1)
        r_o, r_i = 1.2, np.sqrt(1.2 ** 2 - 0.8 ** 2)
        ring = Annulus(inner_radius=r_i, outer_radius=r_o, color=BLUE_D, fill_opacity=0.8).move_to(c2)
        self.play(FadeIn(solid), FadeIn(ring))
        t1 = MathTex(r"J_1", font_size=34).next_to(solid, DOWN)
        t2 = MathTex(r"J_2=%.1f\,J_1" % ((r_o ** 4 - r_i ** 4) / 0.8 ** 4), font_size=34).next_to(ring, DOWN)
        self.play(Write(t1), Write(t2))
        self.caption("截面积（质量）相同：空心轴把材料放到外圈，扭转刚度大得多，中间还能走线",
                     "Same area (same mass): the hollow shaft puts material outside — much stiffer, with room for cables")
        self.wait(1)
        self.card([["机器人关节轴：刚度设计", "Robot joint shafts: designed for stiffness"],
                   MathTex(r"\delta=R\sum_i\frac{T L_i}{G J_i}\le[\delta],\qquad J=\frac{\pi(D^4-d^4)}{32}", font_size=40),
                   ["按末端偏移定直径，再校核强度、急停和疲劳", "Size by tool deflection, then check strength, emergency stops and fatigue"]])
