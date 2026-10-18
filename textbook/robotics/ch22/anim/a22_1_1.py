"""动画 22.1.1（配图 22.1.1）：UR5e 的关节 1 从 A 转到 B（转过 103.43°，算例 22.1.1），俯视。
蓝色手臂按三次多项式、橙色手臂按五次多项式运动，各取不超限的最短时间 1.3436 s、1.3180 s（程序 22.1.1），放慢 4 倍播放。
右边四幅小图同步画出关节 1 的角度、速度、加速度、加加速度（三次在两端加速度跳变，加加速度为冲激，画成竖线）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

DQ = 1.8051                        # 关节 1 的转角，rad（103.43°）
T3, T5 = 1.3436, 1.3180            # 最短时间，s
A0 = math.radians(98.17)           # 起始角（俯视，从 x_s 量起，示意画法）
SLOW = 4.0
BLUE3, ORANGE5 = "#4c9be8", "#f0973a"


def s3(t, r=0):
    u = min(max(t / T3, 0.0), 1.0)
    return [3 * u * u - 2 * u ** 3, (6 * u - 6 * u * u) / T3, (6 - 12 * u) / T3 ** 2 if 0 < t < T3 else 0.0,
            -12 / T3 ** 3 if 0 < t < T3 else 0.0][r]


def s5(t, r=0):
    u = min(max(t / T5, 0.0), 1.0)
    return [10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5, 30 * u * u * (1 - u) ** 2 / T5, 60 * u * (1 - u) * (1 - 2 * u) / T5 ** 2,
            60 * (1 - 6 * u + 6 * u * u) / T5 ** 3 if 0 <= t <= T5 else 0.0][r]


class Lesson(Base):
    def construct(self):
        self.title("22.1", "点到点：三次与五次多项式", "Point to point: cubic and quintic polynomials")
        base = np.array([-4.4, -1.1, 0])
        R = 2.2
        disk = VGroup(Circle(radius=0.32, color=GREY_B, fill_color=GREY_E, fill_opacity=1).move_to(base),
                      DashedVMobject(Arc(radius=R, start_angle=A0 - PI / 2, angle=DQ, arc_center=base, color=GREY_C), num_dashes=30))
        lab_a = MathTex("A", font_size=30, color=GREY_B).move_to(base + (R + 0.35) * np.array([math.cos(A0 - PI / 2), math.sin(A0 - PI / 2), 0]))
        lab_b = MathTex("B", font_size=30, color=GREY_B).move_to(base + (R + 0.35) * np.array([math.cos(A0 - PI / 2 + DQ), math.sin(A0 - PI / 2 + DQ), 0]))
        # 右边四幅小图：角度、速度、加速度、加加速度
        specs = [(r"\theta_1-\theta_{1A}\ (\mathrm{rad})", 0, 2.0, 1.0), (r"\dot\theta_1\ (\mathrm{rad/s})", 0, 3.2, 1.0),
                 (r"\ddot\theta_1\ (\mathrm{rad/s^2})", -7, 7, 7), (r"\theta_1^{(3)}\ (\mathrm{rad/s^3})", -60, 60, 60)]
        axes = VGroup()
        for k, (name, lo, hi, step) in enumerate(specs):
            ax = Axes(x_range=[0, 1.45, 0.5], y_range=[lo, hi, step], x_length=4.6, y_length=1.05, tips=False,
                      axis_config={"stroke_width": 1.5, "color": GREY_B, "include_ticks": False})
            ax.move_to(np.array([2.9, 2.0 - 1.33 * k, 0]))
            axes.add(VGroup(ax, MathTex(name, font_size=22, color=INK).next_to(ax, LEFT, buff=0.12)))
        self.caption("UR5e 的关节 1 从 A 转到 B，转过 103°，起止都静止（俯视）",
                     "UR5e joint 1 turns 103° from A to B, starting and ending at rest (top view)", wait=0)
        self.play(FadeIn(disk), FadeIn(lab_a), FadeIn(lab_b), FadeIn(axes), run_time=1.5)
        # 完整的曲线（淡色）先画出来
        curves = VGroup()
        for k in range(4):
            ax = axes[k][0]
            for f, T, col in ((s3, T3, BLUE3), (s5, T5, ORANGE5)):
                ts = np.linspace(1e-4, T - 1e-4, 120)
                pts = [ax.c2p(t, DQ * f(t, k)) for t in ts]
                curves.add(VMobject(color=col, stroke_width=2.5, stroke_opacity=0.35).set_points_as_corners(pts))
        # 三次多项式两端的跳变：加速度竖线，加加速度用箭头表示冲激
        ax2, ax3 = axes[2][0], axes[3][0]
        jumps = VGroup(Line(ax2.c2p(0, 0), ax2.c2p(0, DQ * 6 / T3 ** 2), color=BLUE3, stroke_width=2.5),
                       Line(ax2.c2p(T3, -DQ * 6 / T3 ** 2), ax2.c2p(T3, 0), color=BLUE3, stroke_width=2.5),
                       Arrow(ax3.c2p(0, 0), ax3.c2p(0, 62), buff=0, color=BLUE3, stroke_width=3, max_tip_length_to_length_ratio=0.3),
                       Arrow(ax3.c2p(T3, 0), ax3.c2p(T3, 62), buff=0, color=BLUE3, stroke_width=3, max_tip_length_to_length_ratio=0.3))
        legend = VGroup(bi(["三次（蓝）", "cubic (blue)"], 20, BLUE3), bi(["五次（橙）", "quintic (orange)"], 20, ORANGE5)).arrange(RIGHT, buff=0.5)
        legend.move_to(np.array([-3.4, 2.0, 0]))
        self.play(Create(curves), FadeIn(legend), run_time=1.5)
        tk = ValueTracker(0.0)

        def scene():
            t = tk.get_value()
            g = VGroup()
            for f, col in ((s3, BLUE3), (s5, ORANGE5)):
                ang = A0 - PI / 2 + DQ * f(t)
                tip = base + R * np.array([math.cos(ang), math.sin(ang), 0])
                g.add(Line(base, tip, color=col, stroke_width=9), Dot(tip, radius=0.09, color=col))
                for k in range(4):
                    ax = axes[k][0]
                    tt = min(t, 1.42)
                    g.add(Dot(ax.c2p(tt, DQ * f(tt, k)), radius=0.06, color=col))
            for k in range(4):
                ax = axes[k][0]
                g.add(Line(ax.c2p(min(t, 1.42), specs[k][1]), ax.c2p(min(t, 1.42), specs[k][2]), color=GREY_C, stroke_width=1))
            g.add(Text(f"t = {t:.2f} s", font=CJK, font_size=22, color=INK).move_to(np.array([-2.2, -2.05, 0])))
            return g

        self.add(always_redraw(scene))
        self.caption("两种多项式各取不超限的最短时间：三次 1.344 s，五次 1.318 s（放慢 4 倍）",
                     "Each polynomial at its shortest time within the limits: cubic 1.344 s, quintic 1.318 s (4× slower)", wait=0)
        self.play(tk.animate.set_value(1.40), run_time=1.40 * SLOW, rate_func=linear)
        self.play(Create(jumps), run_time=1.0)
        self.caption("三次：起止时加速度跳变，加加速度为冲激；五次：加速度从零平滑升起，加加速度有界",
                     "Cubic: acceleration jumps at both ends, jerk is an impulse; quintic: acceleration rises smoothly, jerk bounded", wait=2.5)
        self.caption("路径相同，时间规律不同：θ(t) = θ_A + s(t) Δθ，六个关节共用一个 s(t)",
                     "Same path, different timing: θ(t) = θ_A + s(t) Δθ, one s(t) for all six joints", wait=2.0)
        self.card([["点到点运动的时间标度", "Time scalings for point-to-point motion"],
                   MathTex(r"s = 3\tau^2 - 2\tau^3,\qquad \max\dot s = \frac{1.5}{T},\ \ \max|\ddot s| = \frac{6}{T^2}", font_size=40),
                   MathTex(r"s = 10\tau^3 - 15\tau^4 + 6\tau^5,\qquad \max\dot s = \frac{15}{8T},\ \ \max|\ddot s| = \frac{10}{\sqrt3\,T^2}", font_size=40),
                   ["五次：两端速度、加速度都为零，加加速度有界", "Quintic: zero velocity and acceleration at both ends, bounded jerk"]])
