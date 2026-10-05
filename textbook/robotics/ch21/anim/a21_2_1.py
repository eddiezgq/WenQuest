"""动画 21.2.1（配图 21.2.1）：侧视 X2 从悬停出发，向前飞 5 m 后停住。
位置取五次多项式 x(t) = 5(10τ³ − 15τ⁴ + 6τ⁵)，τ = t/3（3 s 走完，起止静止），高度不变。
俯仰角按式 (21.2.4)：θ = atan(ẍ/𝔤)，总推力 f = m√(ẍ² + 𝔤²)，m = 1.325 kg。画面中 1 m 画成 1.5 个单位，推力 1 N 画成 0.11 个单位。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G, M, D, TT = 9.81, 1.325, 5.0, 3.0
SC, KF = 1.5, 0.11
X0 = np.array([-4.6, -1.2, 0])


def state(t):
    u = min(max(t / TT, 0.0), 1.0)
    x = D * (10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5)
    v = D * (30 * u ** 2 - 60 * u ** 3 + 30 * u ** 4) / TT
    a = D * (60 * u - 180 * u ** 2 + 120 * u ** 3) / TT ** 2
    th = math.atan2(a, G)
    f = M * math.hypot(a, G)
    return x, v, a, th, f


class Lesson(Base):
    def construct(self):
        self.title("21.2", "要向前飞，先得低头", "To fly forward, first tip the nose down")
        gl = Line(LEFT * 6.5 + DOWN * 2.3, RIGHT * 6.5 + DOWN * 2.3, color=GREY_B, stroke_width=3)
        marks = VGroup(*[Line(np.array([X0[0] + SC * k, -2.3, 0]), np.array([X0[0] + SC * k, -2.45, 0]), color=GREY_C) for k in range(6)])
        nums = VGroup(*[Text(f"{k} m", font=CJK, font_size=18, color=MUTED).next_to(marks[k], DOWN, buff=0.08) for k in range(6)])
        self.play(Create(gl), FadeIn(marks), FadeIn(nums), run_time=0.8)
        tt = ValueTracker(0.0)

        def scene():
            x, v, a, th, f = state(tt.get_value())
            c = X0 + RIGHT * SC * x
            R = np.array([[math.cos(-th), -math.sin(-th)], [math.sin(-th), math.cos(-th)]])
            g = VGroup()
            for sx in (-1, 1):
                e = R @ np.array([sx * 0.95, 0.0])
                g.add(Line(c, c + np.r_[e, 0], color=GREY_B, stroke_width=7))
                p1 = c + np.r_[R @ np.array([sx * 0.95 - 0.38, 0.12]), 0]
                p2 = c + np.r_[R @ np.array([sx * 0.95 + 0.38, 0.12]), 0]
                g.add(Line(p1, p2, color=GREY_A, stroke_width=5))
            g.add(Ellipse(width=0.7, height=0.26, color=GREY_A, fill_color=NAVY, fill_opacity=1).rotate(-th).move_to(c))
            nose = c + np.r_[R @ np.array([0.42, 0.0]), 0]
            g.add(Dot(nose, radius=0.06, color=YELLOW))
            zb = np.r_[R @ np.array([0.0, 1.0]), 0]
            tip = c + KF * f * zb
            g.add(Arrow(c, tip, buff=0, color=BLUE, stroke_width=6, max_tip_length_to_length_ratio=0.12))
            g.add(MathTex(r"f\,z_b", color=BLUE, font_size=34).next_to(tip, UP, buff=0.05))
            g.add(DashedLine(c, c + UP * KF * M * G, color=GREY_B, stroke_width=2))
            if abs(a) > 0.4:
                g.add(Arrow(c + UP * KF * M * G, tip, buff=0, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.3))
                g.add(MathTex(r"m\ddot x", color=RED, font_size=30).next_to(c + UP * KF * M * G + RIGHT * KF * M * a / 2, DOWN if a > 0 else UP,
                                                                         buff=0.12))
            info = VGroup(
                Text(f"t = {tt.get_value():.2f} s", font=CJK, font_size=24, color=INK),
                Text(f"速度 v = {v:.2f} m/s", font=CJK, font_size=24, color=INK),
                Text(f"加速度 a = {a:+.2f} m/s²".replace("+", "+").replace("-", "−"), font=CJK, font_size=24, color=RED_B),
                Text(f"俯仰角 θ = atan(a/g) = {math.degrees(th):+.1f}°".replace("-", "−"), font=CJK, font_size=24, color=YELLOW),
                Text(f"总推力 f = {f:.2f} N", font=CJK, font_size=24, color=BLUE_B),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.45).shift(DOWN * 0.7)
            g.add(info)
            return g

        sc = always_redraw(scene)
        self.add(sc)
        self.caption("悬停：推力竖直向上，与重力平衡", "Hover: thrust straight up, balancing the weight", wait=1.0)
        self.caption("加速：机身低头，推力向前倾；它的竖直分量仍等于重力，水平分量推着机身向前",
                     "Speeding up: the nose tips down; the vertical part of the thrust still holds the weight, the horizontal part pushes",
                     wait=0)
        self.play(tt.animate.set_value(1.5), run_time=4.5, rate_func=linear)
        self.caption("中点：加速度为零，机身放平，以最高速度滑行", "Midway: zero acceleration, the body is level and coasts at top speed", wait=0)
        self.wait(1.0)
        self.caption("减速：机身抬头，推力向后倾，水平分量使机身慢下来",
                     "Slowing down: the nose comes up, the thrust leans back and brakes the motion", wait=0)
        self.play(tt.animate.set_value(TT), run_time=4.5, rate_func=linear)
        self.caption("停住：又回到悬停。倾角只由加速度决定，与速度无关",
                     "Stopped: hovering again. The tilt depends on the acceleration only, not on the speed", wait=2.0)
        self.card([["推力方向由加速度决定", "The thrust direction is set by the acceleration"],
                   MathTex(r"t = \ddot p + \mathfrak g\,\hat z = \frac fm\,z_b", font_size=46),
                   MathTex(r"f = m\,\|t\|,\qquad z_b = \frac{t}{\|t\|},\qquad \tan\alpha = \frac{a_h}{\mathfrak g}", font_size=42),
                   ["机头朝哪里（偏航角）由我们另行选择", "Where the nose points (yaw) is ours to choose"]])
