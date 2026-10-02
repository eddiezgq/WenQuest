"""动画 18.7.1（配图 18.7.3）：UR5e 上臂与前臂（0.425 m、0.392 m）组成的两连杆，肘关节从 90° 逐渐伸直，
腕心处的速度椭圆（0.35 m 代表 1 m/s）跟着变扁；右侧读数显示 σ1、σ2 和二者之比。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("18.7", "接近奇异位形：速度椭圆被压扁", "Near a singularity the velocity ellipse flattens")
        l1, l2 = 0.425, 0.392
        t1 = math.radians(30)
        th = ValueTracker(90.0)
        S = 5.0                                    # 1 m 画成 5 格
        O = np.array([-4.6, -2.3, 0.0])

        def J():
            t2 = math.radians(th.get_value())
            a, b = t1, t1 + t2
            return np.array([[-l1 * math.sin(a) - l2 * math.sin(b), -l2 * math.sin(b)],
                             [l1 * math.cos(a) + l2 * math.cos(b), l2 * math.cos(b)]])

        def pts():
            t2 = math.radians(th.get_value())
            j = np.array([l1 * math.cos(t1), l1 * math.sin(t1)])
            w = j + l2 * np.array([math.cos(t1 + t2), math.sin(t1 + t2)])
            return j, w

        def arm():
            j, w = pts()
            P = lambda v: O + S * np.array([v[0], v[1], 0.0])
            g = VGroup(Line(P([0, 0]), P(j), color=STEEL, stroke_width=14), Line(P(j), P(w), color=STEEL, stroke_width=10),
                       Dot(P([0, 0]), radius=0.12, color=WHITE), Dot(P(j), radius=0.1, color=WHITE))
            Jm = J()
            e = [P(w + 0.35 * (Jm @ np.array([math.cos(a), math.sin(a)]))) for a in np.linspace(0, 2 * math.pi, 121)]
            g.add(Polygon(*e[:-1], color=RED, stroke_width=4))
            return g

        def read():
            sv = np.linalg.svd(J(), compute_uv=False)
            # 读数每一帧都变，用 Text（不经过 LaTeX），渲染快得多
            return VGroup(Text("θ₂ = %.0f°" % th.get_value(), font=LATIN, font_size=30, color=YELLOW),
                          Text("σ₁ = %.3f m/s" % sv[0], font=LATIN, font_size=28),
                          Text("σ₂ = %.3f m/s" % sv[1], font=LATIN, font_size=28, color=RED),
                          Text("σ₁/σ₂ = %.1f" % (sv[0] / sv[1]), font=LATIN, font_size=28)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.7)

        a = always_redraw(arm)
        r = always_redraw(read)
        self.play(FadeIn(a), FadeIn(r))
        self.caption("红色椭圆：长度 1 rad/s 的关节速度能产生的全部腕心速度", "Red: all wrist velocities from joint speeds of 1 rad/s")
        self.play(th.animate.set_value(45.0), run_time=3)
        self.caption("肘关节伸直一些，椭圆变扁：沿手臂方向越来越难移动", "As the elbow straightens the ellipse flattens")
        self.play(th.animate.set_value(10.0), run_time=3)
        self.play(th.animate.set_value(2.0), run_time=2)
        self.caption("接近伸直时 σ₂ → 0：这就是奇异位形", "Nearly straight: σ2 → 0, a singular configuration")
        self.wait(1.5)
        self.card([["奇异位形：最小奇异值趋于零", "Singularity: the smallest singular value tends to zero"],
                   MathTex(r"\sigma_1\sigma_2 = l_1 l_2\,\lvert\sin\theta_2\rvert", font_size=48),
                   ["所需关节速度与 1/σ₂ 成正比，会突然变得很大", "Required joint speed grows like 1/σ2"]])
