"""动画 26.4.1（配图 26.4.1）：关节摩擦。数值与算例 26.4.1 相同（示意值）：库仑摩擦 f_c = 2.0 N·m，黏性摩擦 f_v = 1.5 N·m·s/rad。
(1) 恒速试验：关节依次以 ±0.05～1.5 rad/s 匀速转动，稳定后的力矩就是摩擦力矩，一点一点画出 τ_f(θ̇)，拟合出两条直线。
(2) 真实的减速器在低速处还有斯特里贝克效应（示意：静摩擦 3.0 N·m，斯特里贝克速度 0.1 rad/s）。
(3) 速度换向时库仑摩擦力矩跳变；低通滤波（8 Hz）把跳变抹平，而模型里的 sign θ̇ 照样跳变，两者在换向附近对不上——
    这就是 26.3 节库仑摩擦估小、黏性摩擦估大的原因。演示用 θ̇ = 0.8 sin 2πt/2.5 的往复运动。"""
from manim import *
from wq_anim import *
import numpy as np
import math

FC, FV = 2.0, 1.5
FS, VS = 3.0, 0.1
SPEEDS = [0.05, 0.1, 0.2, 0.5, 1.0, 1.5]


class Lesson(Base):
    def construct(self):
        self.title("26.4", "关节摩擦：恒速试验与换向", "Joint friction: constant-speed tests and reversals")
        ax = Axes(x_range=[-1.6, 1.6, 0.5], y_range=[-4.5, 4.5, 1], x_length=6.2, y_length=4.2, tips=False,
                  axis_config=dict(color=GREY_B, stroke_width=2, include_ticks=True)).move_to([2.6, -0.3, 0])
        self.add(ax, MathTex(r"\dot\theta", font_size=28, color=MUTED).next_to(ax.x_axis.get_end(), DOWN, buff=0.1),
                 MathTex(r"\tau_f", font_size=28, color=MUTED).next_to(ax.y_axis.get_end(), LEFT, buff=0.1))
        # 左：转盘
        c = np.array([-4.3, -0.3, 0])
        disk = Circle(radius=1.1, color=STEEL, stroke_width=4)
        mark = Line(c, c + RIGHT * 1.1, color=YELLOW, stroke_width=5)
        self.add(disk.move_to(c), mark)
        val = ValueTracker(0)
        rd = always_redraw(lambda: zh(f"θ̇ = {val.get_value():+.2f} rad/s   τ = {FC * np.sign(val.get_value()) + FV * val.get_value():+.2f} N·m"
                                      if val.get_value() != 0 else "", 20, INK).move_to(c + DOWN * 1.6))
        self.add(rd)
        self.caption("恒速转动时没有惯性力；关节 1 的轴竖直，也没有重力：电机的力矩全部用来克服摩擦",
                     "At constant speed there is no inertial torque, and joint 1's vertical axis feels no gravity: the motor torque is all friction", wait=0.5)
        dots = VGroup()
        for w in SPEEDS + [-s for s in SPEEDS]:
            val.set_value(w)
            self.play(Rotate(mark, angle=0.9 * np.sign(w) * (0.5 + abs(w)), about_point=c), run_time=0.5, rate_func=linear)
            d = Dot(ax.c2p(w, FC * np.sign(w) + FV * w), radius=0.07, color=RED)
            dots.add(d)
            self.play(FadeIn(d, scale=1.5), run_time=0.2)
        val.set_value(0)
        pos = ax.plot(lambda x: FC + FV * x, x_range=[0.001, 1.55], color=BLUE, stroke_width=3)
        neg = ax.plot(lambda x: -FC + FV * x, x_range=[-1.55, -0.001], color=BLUE, stroke_width=3)
        self.play(Create(pos), Create(neg), run_time=1.0)
        self.add(MathTex(r"\tau_f = f_c\,\mathrm{sign}\,\dot\theta + f_v\dot\theta", font_size=30, color=BLUE).move_to(ax.c2p(-0.95, 3.3)))
        self.caption("两条直线：截距是库仑摩擦 f_c = 2.0 N·m，斜率是黏性摩擦 f_v = 1.5 N·m·s/rad",
                     "Two straight lines: the intercept is Coulomb friction f_c = 2.0 N·m, the slope viscous friction f_v = 1.5 N·m·s/rad", wait=2.0)
        st = ax.plot(lambda x: (FC + (FS - FC) * math.exp(-(x / VS) ** 2)) * np.sign(x) + FV * x, x_range=[0.002, 0.6], color=ORANGE, stroke_width=3)
        st2 = ax.plot(lambda x: (FC + (FS - FC) * math.exp(-(x / VS) ** 2)) * np.sign(x) + FV * x, x_range=[-0.6, -0.002], color=ORANGE, stroke_width=3)
        self.play(Create(st), Create(st2), run_time=1.2)
        self.caption("真实的减速器在很低的速度下摩擦反而更大（斯特里贝克效应，示意）：起动要先克服静摩擦",
                     "Real gearboxes show more friction at very low speed (the Stribeck effect, illustrative): breakaway needs the static friction", wait=2.5)
        self.clear_stage()
        # 换向
        ax2 = Axes(x_range=[0, 5, 1], y_range=[-4, 4, 2], x_length=10, y_length=3.8, tips=False,
                   axis_config=dict(color=GREY_B, stroke_width=2)).move_to([0, -0.2, 0])
        self.add(ax2, zh("t / s", 18, MUTED).next_to(ax2.x_axis.get_end(), DOWN, buff=0.1))
        w = lambda t: 0.8 * math.sin(2 * math.pi * t / 2.5)                     # noqa: E731
        raw = lambda t: FC * np.sign(w(t)) + FV * w(t)                         # noqa: E731
        ts = np.linspace(0, 5, 2001)
        y = np.array([raw(t) for t in ts])
        # 8 Hz 的二阶低通，前后各滤一次（零相位）
        wc = 2 * math.pi * 8
        dt = ts[1] - ts[0]

        def lp(x):
            yv, v1, out = x[0], 0.0, []
            for xi in x:
                acc = wc * wc * (xi - yv) - 1.414 * wc * v1
                v1 += acc * dt
                yv += v1 * dt
                out.append(yv)
            return np.array(out)
        yf = lp(lp(y)[::-1])[::-1]
        c_raw = ax2.plot_line_graph(ts[::4], y[::4], add_vertex_dots=False, line_color=GREY_B, stroke_width=2)
        c_f = ax2.plot_line_graph(ts[::4], yf[::4], add_vertex_dots=False, line_color=RED, stroke_width=3)
        self.play(Create(c_raw), run_time=1.5)
        self.play(Create(c_f), run_time=1.5)
        for tz in (1.25, 2.5, 3.75):
            self.add(Rectangle(width=ax2.c2p(0.12, 0)[0] - ax2.c2p(0, 0)[0], height=3.8, stroke_width=0, fill_color=ORANGE,
                               fill_opacity=0.25).move_to(ax2.c2p(tz, 0)))
        self.caption("灰线：模型里的摩擦（换向时跳变）；红线：滤波后的实测力矩。橙色处两者对不上——辨识时去掉换向附近的数据",
                     "Grey: modelled friction (jumps at reversal); red: filtered measured torque. They disagree in the orange zones, so drop data near reversals", wait=3.0)
        self.card([["关节摩擦", "Joint friction"],
                   MathTex(r"\tau_f = \big[f_c + (f_s - f_c)e^{-(\dot\theta/v_s)^2}\big]\mathrm{sign}\,\dot\theta + f_v\dot\theta", font_size=36),
                   ["恒速试验：截距是库仑摩擦，斜率是黏性摩擦", "Constant-speed tests: intercept = Coulomb, slope = viscous"],
                   ["辨识时去掉速度换向附近的数据", "Drop data near velocity reversals when identifying"]])
