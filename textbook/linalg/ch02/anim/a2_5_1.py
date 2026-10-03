"""动画 2.5.1（配图 2.5.1）：u = (2, 0, 0) 固定，v 在 xy 平面内绕原点转动。平行四边形的面积就是 ‖u × v‖ = ‖u‖‖v‖ sin θ，
u × v 沿 z 轴：v 在 u 的逆时针一侧时指向屏幕外（+z），在顺时针一侧时指向屏幕内（−z），平行时为零。
画面是 xy 平面的俯视图，右侧的竖条表示 u × v 的 z 分量。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.5", "叉积：面积与方向", "Cross product: area and direction")
        k = 1.0
        O = np.array([-2.6, -0.3, 0.0])
        u = np.array([2.0, 0.0])
        r = 1.6

        def P(v):
            return O + k * np.array([v[0], v[1], 0.0])

        th = ValueTracker(math.radians(60))
        au = Arrow(P([0, 0]), P(u), buff=0, color=BLUE, stroke_width=7, max_tip_length_to_length_ratio=0.2)
        lu = MathTex(r"\boldsymbol u", color=BLUE, font_size=38).next_to(P(u), DOWN, buff=0.1)
        self.play(GrowArrow(au), FadeIn(lu))
        base = np.array([3.6, 0.0, 0.0])
        zaxis = VGroup(Line(base + DOWN * 2.4, base + UP * 2.6, color=GREY_B, stroke_width=1.5),
                       MathTex(r"(\boldsymbol u\times\boldsymbol v)_z", font_size=30).move_to(base + UP * 3.0))

        def scene():
            t = th.get_value()
            v = r * np.array([math.cos(t), math.sin(t)])
            z = u[0] * v[1] - u[1] * v[0]
            col = RED if z >= 0 else PURPLE_B
            g = VGroup(Polygon(P([0, 0]), P(u), P(u + v), P(v), color=YELLOW, fill_opacity=0.3, stroke_width=1.5),
                       Arrow(P([0, 0]), P(v), buff=0, color=GREEN, stroke_width=7, max_tip_length_to_length_ratio=0.2),
                       MathTex(r"\boldsymbol v", color=GREEN, font_size=38).next_to(P(v), UP if v[1] >= 0 else DOWN, buff=0.1))
            h = 0.7 * z
            if abs(h) > 0.02:
                g.add(Arrow(base, base + UP * h, buff=0, color=col, stroke_width=10, max_tip_length_to_length_ratio=0.25))
            g.add(MathTex(r"%+.2f" % z, color=col, font_size=32).next_to(base + UP * h, RIGHT, buff=0.2))
            sym = r"\odot" if z > 0.05 else (r"\otimes" if z < -0.05 else r"\cdot")
            g.add(MathTex(sym, color=col, font_size=56).move_to(P(u / 2 + v / 2)))
            return g

        g = always_redraw(scene)
        self.play(Create(zaxis), FadeIn(g))
        self.caption("平行四边形的面积 = ‖u‖‖v‖ sin θ = ‖u × v‖；⊙ 表示 u × v 指向屏幕外",
                     "Area = ‖u‖‖v‖ sin θ = ‖u × v‖; ⊙ means u × v points out of the screen")
        self.caption("垂直时面积最大：‖u × v‖ = ‖u‖‖v‖ = 3.2", "Largest when perpendicular: ‖u × v‖ = ‖u‖‖v‖ = 3.2", wait=0.8)
        self.play(th.animate.set_value(math.radians(90)), run_time=1.5)
        self.caption("平行时平行四边形被压扁，叉积为零", "Parallel: the parallelogram collapses, the cross product is zero", wait=0.8)
        self.play(th.animate.set_value(math.radians(180)), run_time=2.5)
        self.caption("v 转到 u 的顺时针一侧：u × v 指向屏幕内（⊗），z 分量为负",
                     "v on the clockwise side of u: u × v points into the screen (⊗), negative z")
        self.play(th.animate.set_value(math.radians(300)), run_time=2.5)
        self.caption("右手定则：四指从 u 弯向 v，拇指指向 u × v", "Right-hand rule: curl the fingers from u to v, the thumb gives u × v")
        self.play(th.animate.set_value(math.radians(420)), run_time=2.5)
        self.wait(0.8)
        self.card([["叉积：长度是面积，方向按右手定则", "Cross product: length = area, direction by the right-hand rule"],
                   MathTex(r"\Vert\boldsymbol u\times\boldsymbol v\Vert = \Vert\boldsymbol u\Vert\,\Vert\boldsymbol v\Vert\sin\theta,\qquad \boldsymbol v\times\boldsymbol u = -\,\boldsymbol u\times\boldsymbol v", font_size=40),
                   ["平行时叉积为零", "Zero when parallel"]])
