"""动画 9.4.1（配图 9.4.1）：提起箱子时的功率。机械臂竖直提起 20 kg 的箱子 1.2 m，用时 1.5 s，梯形速度曲线（加速、减速各 0.3 s），
与算例 9.4.2 一致。提升力在加速段最大，速度在加速段末尾达到最大，所以功率 P = Fv 的峰值在加速段末尾；功率曲线下的面积等于 mgh。"""
from manim import *
from wq_anim import *
import numpy as np

M, H, TT, TA, G = 20.0, 1.2, 1.5, 0.3, 9.81
VMAX = H / (TT - TA)
ACC = VMAX / TA


def v(t):
    return ACC * t if t < TA else VMAX if t < TT - TA else max(0.0, ACC * (TT - t))


def a(t):
    return ACC if t < TA else 0.0 if t < TT - TA else -ACC


def y(t):
    if t < TA:
        return 0.5 * ACC * t * t
    if t < TT - TA:
        return 0.5 * ACC * TA * TA + VMAX * (t - TA)
    return H - 0.5 * ACC * (TT - t) ** 2


def P(t):
    return M * (G + a(t)) * v(t)


class Lesson(Base):
    def construct(self):
        self.title("9.4", "提起箱子要多大的功率", "How much power to lift a box")
        floor = Line(np.array([-6.6, -2.3, 0]), np.array([-2.2, -2.3, 0]), color=GREY_B)
        K = 2.6                                  # 画面单位 / m（竖直方向）
        t = ValueTracker(0.0)
        box = always_redraw(lambda: Square(side_length=0.9, color="#d29922", fill_opacity=0.85).move_to(np.array([-4.4, -1.85 + K * y(t.get_value()), 0])))
        cable = always_redraw(lambda: Line(np.array([-4.4, 2.6, 0]), np.array([-4.4, -1.4 + K * y(t.get_value()), 0]), color=GREY_A, stroke_width=4))
        force = always_redraw(lambda: Arrow(np.array([-3.6, -1.85 + K * y(t.get_value()), 0]),
                                            np.array([-3.6, -1.85 + K * y(t.get_value()) + 0.0065 * M * (G + a(t.get_value())), 0]),
                                            buff=0, color=C_F, stroke_width=6, max_tip_length_to_length_ratio=0.25))
        flab = always_redraw(lambda: MathTex("F", font_size=30, color=C_F).next_to(force, RIGHT, buff=0.1))
        self.play(Create(floor))
        self.add(cable, box, force, flab)
        ax = Axes(x_range=[0, 1.5, 0.3], y_range=[0, 300, 100], x_length=5.6, y_length=3.4,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).move_to(np.array([2.9, 0.1, 0]))
        xl = bi(["时间 t / s", "time t / s"], size=18).next_to(ax, DOWN, buff=0.2)
        yl = bi(["功率 P = Fv / W", "power P = Fv / W"], size=18).next_to(ax, UP, buff=0.1).shift(LEFT * 2.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        curve = always_redraw(lambda: ax.plot(P, x_range=[0, max(0.001, t.get_value()), 0.001], color=C_F, use_smoothing=False))
        dot = always_redraw(lambda: Dot(ax.c2p(t.get_value(), P(t.get_value())), color=C_F, radius=0.07))
        self.add(curve, dot)
        self.caption("加速段：提升力 m(g + a) 最大，速度从零增大，功率随之上升", "Speeding up: the force m(g + a) is largest and the speed grows, so the power climbs", wait=0)
        self.play(t.animate.set_value(TA), run_time=2.0, rate_func=linear)
        pk = Dot(ax.c2p(TA, P(TA - 1e-6)), color=YELLOW, radius=0.09)
        pkl = bi([f"峰值 {M * (G + ACC) * VMAX:.0f} W", f"peak {M * (G + ACC) * VMAX:.0f} W"], size=20, color=YELLOW).next_to(pk, RIGHT, buff=0.25)
        self.play(FadeIn(pk), FadeIn(pkl))
        self.caption("加速段末尾：力最大、速度也最大，功率达到峰值", "End of the speed-up: largest force and largest speed, so peak power", wait=1.0)
        self.caption("匀速段：F = mg，功率 mgv；减速段：力小于 mg，功率下降", "Cruise: F = mg, power mgv; slowing down: the force drops below mg and so does the power", wait=0)
        self.play(t.animate.set_value(TT), run_time=4.0, rate_func=linear)
        area = ax.get_area(ax.plot(P, x_range=[0, TT, 0.001], use_smoothing=False), x_range=[0, TT], color=YELLOW, opacity=0.3)
        avg = DashedLine(ax.c2p(0, M * G * H / TT), ax.c2p(TT, M * G * H / TT), color=GREY_A)
        avgl = bi([f"平均 {M * G * H / TT:.0f} W", f"average {M * G * H / TT:.0f} W"], size=18).next_to(ax.c2p(TT * 0.45, M * G * H / TT), DOWN, buff=0.15)
        self.play(FadeIn(area), Create(avg), FadeIn(avgl))
        self.caption(f"曲线下的面积 = 总功 = mgh = {M * G * H:.0f} J；电机既要给得出峰值功率，也要扛得住平均的发热", f"Area under the curve = total work = mgh = {M * G * H:.0f} J; the motor must deliver the peak and survive the average heating", wait=2.5)
        self.card([["功率", "Power"],
                   MathTex(r"P = \frac{\mathrm{d}W}{\mathrm{d}t} = \boldsymbol F\cdot\boldsymbol v, \qquad W = \int P\,\mathrm{d}t", font_size=42),
                   ["同样的功，做得越快，功率越大", "The same work done faster needs more power"],
                   ["加速运动时峰值功率可以比平均功率大得多", "With acceleration the peak can be far above the average"]])
