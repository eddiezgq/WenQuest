"""动画 5.2.1（配图 5.2.1）：抛体运动是水平匀速与竖直自由落体的合成。三个零件同时出发：一个水平抛出，一个从同一高度自由落下，
一个在地面上以相同的水平速度匀速滑动（“影子”）。每隔相同时间留下一个像：抛出的零件始终与自由落体等高，与影子水平位置相同。"""
from manim import *
from wq_anim import *
import numpy as np

G = 9.81
H, VX = 1.2, 1.5                               # 出手高度 m，水平速度 m/s
SC = 3.0                                        # 1 m 画成 3 个单位
O = np.array([-4.5, -2.6, 0])                   # 地面上出手点的正下方


def P(x, y):
    return O + SC * np.array([x, y, 0])


class Lesson(Base):
    def construct(self):
        self.title("5.2", "抛体运动 = 水平匀速 + 竖直自由落体", "Projectile = uniform horizontal + free fall")
        floor = Line(P(-0.3, 0), P(3.0, 0), color=GREY_B, stroke_width=3)
        tf = np.sqrt(2 * H / G)
        self.play(Create(floor))
        tr = ValueTracker(0.0)
        proj = always_redraw(lambda: Dot(P(VX * tr.get_value(), H - 0.5 * G * tr.get_value() ** 2), color=BLUE, radius=0.11))
        drop = always_redraw(lambda: Dot(P(0, H - 0.5 * G * tr.get_value() ** 2), color=ORANGE, radius=0.11))
        shadow = always_redraw(lambda: Dot(P(VX * tr.get_value(), 0), color=GREEN, radius=0.11))
        lines = always_redraw(lambda: VGroup(
            DashedLine(P(0, H - 0.5 * G * tr.get_value() ** 2), P(VX * tr.get_value(), H - 0.5 * G * tr.get_value() ** 2), color=GREY_B, stroke_width=2),
            DashedLine(P(VX * tr.get_value(), 0), P(VX * tr.get_value(), H - 0.5 * G * tr.get_value() ** 2), color=GREY_B, stroke_width=2)))
        self.add(lines, proj, drop, shadow)
        legend = VGroup(bi(["蓝：水平抛出", "blue: thrown horizontally"], 22), bi(["橙：同时自由落下", "orange: dropped at the same moment"], 22),
                        bi(["绿：地面上以同样水平速度滑动", "green: sliding on the floor at the same speed"], 22)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(RIGHT, buff=0.4).shift(UP * 1.0)
        self.play(FadeIn(legend))
        self.caption("三个零件同时出发", "Three parts start together", wait=0)
        marks = VGroup()
        n = 5
        for k in range(1, n + 1):
            t = tf * k / n
            self.play(tr.animate.set_value(t), run_time=0.7, rate_func=linear)
            marks.add(Dot(P(VX * t, H - 0.5 * G * t * t), color=BLUE, radius=0.06, fill_opacity=0.5),
                      Dot(P(0, H - 0.5 * G * t * t), color=ORANGE, radius=0.06, fill_opacity=0.5),
                      Dot(P(VX * t, 0), color=GREEN, radius=0.06, fill_opacity=0.5))
            self.add(marks)
        self.caption("抛出的零件始终与自由落下的零件等高：竖直方向就是自由落体", "The thrown part stays level with the dropped one: vertically it is free fall", wait=1.5)
        self.caption("又始终在影子的正上方：水平方向是匀速运动", "and always right above its shadow: horizontally the motion is uniform", wait=1.5)
        path = ParametricFunction(lambda t: P(VX * t, H - 0.5 * G * t * t), t_range=[0, tf], color=BLUE, stroke_width=3)
        self.play(Create(path))
        self.caption("两者合起来，轨迹是一条抛物线", "Together they trace a parabola", wait=1.5)
        self.card([["抛体运动", "Projectile motion"],
                   ["水平方向：匀速，x = v₀ cos θ · t", "Horizontal: uniform, x = v₀ cos θ · t"],
                   ["竖直方向：加速度 g，与水平运动互不影响", "Vertical: acceleration g, independent of the horizontal motion"]])
