"""动画 33.11.1（配图 33.11.2）：轴在转，力也在转。截面上一点 P 随轴转动；方向固定的力使 P 的弯曲应力正负交替（交变应力），
随轴一起转的力（平衡块离心力）使 P 的应力不变（平均应力）；两者叠加就是平缝机上轴台阶处的应力循环。"""
from manim import *
from wq_anim import *
import numpy as np

O = np.array([-3.6, 0.2, 0])
R = 1.3


class Lesson(Base):
    def construct(self):
        self.title("33.11", "转动的轴、转动的力", "A rotating shaft under rotating loads")
        th = ValueTracker(0.0)
        sec = Circle(radius=R, color=GREY_B, fill_color=GREY_D, fill_opacity=0.6).move_to(O)
        P = always_redraw(lambda: Dot(O + R * np.array([np.cos(th.get_value() + PI / 2), np.sin(th.get_value() + PI / 2), 0]), color=YELLOW, radius=0.1))
        lp = always_redraw(lambda: Text("P", font_size=26, color=YELLOW).move_to(O + 1.3 * R * np.array([np.cos(th.get_value() + PI / 2), np.sin(th.get_value() + PI / 2), 0])))
        self.play(FadeIn(sec), FadeIn(P), FadeIn(lp))
        ax = Axes(x_range=[0, 4 * PI, PI], y_range=[-1.6, 1.6, 1], x_length=6.0, y_length=3.4, tips=False,
                  axis_config={"color": GREY_B}).move_to([3.2, 0.2, 0])
        xl = MathTex(r"\theta", font_size=30).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = MathTex(r"\sigma_P", font_size=30).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), Write(xl), Write(yl))

        # 1) 方向固定的力（同步带拉力、往复惯性力的一部分）：P 转一圈，受拉、受压各一次
        Ff = Arrow(O + UP * 2.6, O + UP * (R + 0.05), buff=0, color=C_F, stroke_width=7)
        self.play(GrowArrow(Ff))
        self.caption("方向固定的力：P 转到受拉侧、又转到受压侧——对称循环", "A force of fixed direction: P passes the tension side, then the compression side — fully reversed")
        tr1 = always_redraw(lambda: ax.plot(lambda x: np.cos(x), x_range=[0, max(th.get_value(), 0.01)], color=C_F))
        self.add(tr1)
        self.play(th.animate.set_value(2 * PI), run_time=4, rate_func=linear)
        self.play(FadeOut(Ff))

        # 2) 随轴转的力（平衡块离心力）：相对 P 不动
        def rot_arrow():
            a = th.get_value() + PI / 2 + PI
            d = np.array([np.cos(a), np.sin(a), 0])
            return Arrow(O + d * 2.6, O + d * (R + 0.05), buff=0, color=ORANGE, stroke_width=7)
        Fr = always_redraw(rot_arrow)
        self.add(Fr)
        self.caption("随轴一起转的力：相对于 P 方向不变——静应力，即平均应力", "A force turning with the shaft: fixed relative to P — a steady stress, the mean stress")
        tr2 = always_redraw(lambda: ax.plot(lambda x: -0.6 + 0 * x, x_range=[2 * PI, max(th.get_value(), 2 * PI + 0.01)], color=ORANGE))
        self.add(tr2)
        self.play(th.animate.set_value(3 * PI), run_time=2, rate_func=linear)

        # 3) 两者叠加
        Ff2 = Arrow(O + UP * 2.6, O + UP * (R + 0.05), buff=0, color=C_F, stroke_width=7)
        self.play(GrowArrow(Ff2))
        self.caption("两者同时作用：应力在平均值附近交变——要按 σa 和 σm 一起校核", "Both together: the stress alternates about a mean — check with σa and σm together")
        tr3 = always_redraw(lambda: ax.plot(lambda x: -0.6 + np.cos(x), x_range=[3 * PI, max(th.get_value(), 3 * PI + 0.01)], color=RED))
        self.add(tr3)
        self.play(th.animate.set_value(4 * PI), run_time=2, rate_func=linear)
        self.wait(1)
        self.card([["旋转轴上一点的应力", "Stress at a point of a rotating shaft"],
                   MathTex(r"\sigma_P(\theta)=\frac{M_x\cos(\theta+\varphi)+M_y\sin(\theta+\varphi)}{W}", font_size=38),
                   ["方向固定的力 → 交变应力；随轴转的力 → 平均应力。逐点算一圈，取最危险的点", "Fixed-direction loads → alternating; loads turning with the shaft → mean. Follow each point round, take the worst"]])
