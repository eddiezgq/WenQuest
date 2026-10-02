"""动画 18.1.1（配图 18.1.1）：平面网格在 A = [[3, 0], [4, 5]] 的作用下变形，单位圆变成椭圆；
坐标轴方向 e1、e2 的像不再垂直，而 v1、v2 的像仍然垂直，正是椭圆的两根半轴。画面按 0.45 倍缩小。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("18.1", "单位圆变成椭圆", "The unit circle becomes an ellipse")
        A = np.array([[3.0, 0.0], [4.0, 5.0]])
        k = 0.45                                  # 画面缩放：1 个单位画成 0.45 格（只为放得下）
        O = np.array([1.2, -0.3, 0.0])
        t = ValueTracker(0.0)

        def M():
            s = t.get_value()
            return (1 - s) * np.eye(2) + s * A

        def P(v):
            w = M() @ np.asarray(v, dtype=float)
            return O + k * np.array([w[0], w[1], 0.0])

        def grid():
            g = VGroup()
            for i in range(-5, 6):
                c = GREY_B if i else WHITE
                g.add(Line(P([i, -5]), P([i, 5]), color=c, stroke_width=1 if i else 2, stroke_opacity=0.45 if i else 0.8))
                g.add(Line(P([-5, i]), P([5, i]), color=c, stroke_width=1 if i else 2, stroke_opacity=0.45 if i else 0.8))
            return g

        def circle():
            pts = [P([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 121)]
            return Polygon(*pts[:-1], color=YELLOW, stroke_width=4)

        r2 = 1 / math.sqrt(2)
        v1, v2 = [r2, r2], [r2, -r2]

        def arrows():
            g = VGroup(Arrow(O, P([1, 0]), buff=0, color=GREY_B, stroke_width=4),
                       Arrow(O, P([0, 1]), buff=0, color=GREY_B, stroke_width=4),
                       Arrow(O, P(v1), buff=0, color=RED, stroke_width=6),
                       Arrow(O, P(v2), buff=0, color=GREEN, stroke_width=6))
            return g

        g = always_redraw(grid)
        self.play(FadeIn(g), run_time=0.8)
        c = always_redraw(circle)
        ar = always_redraw(arrows)
        self.play(Create(c), FadeIn(ar))
        self.caption("单位圆，以及两对互相垂直的方向：灰色 e₁、e₂，红绿 v₁、v₂",
                     "The unit circle and two perpendicular pairs: grey e1, e2; red/green v1, v2")
        self.caption("现在让矩阵 A 作用在整个平面上", "Now let A act on the whole plane", wait=0.5)
        self.play(t.animate.set_value(1.0), run_time=4)
        self.caption("网格被拉伸、剪切；单位圆变成了椭圆", "The grid is stretched and sheared; the circle becomes an ellipse")
        e1, e2 = A @ [1, 0], A @ [0, 1]
        cosang = float(e1 @ e2 / (np.linalg.norm(e1) * np.linalg.norm(e2)))
        note = bi(["e₁、e₂ 的像夹角 %.0f°，不再垂直" % math.degrees(math.acos(cosang)),
                   "images of e1, e2 meet at %.0f°: no longer perpendicular" % math.degrees(math.acos(cosang))], 24, GREY_A)
        note.to_edge(LEFT, buff=0.4).shift(UP * 1.2)
        self.play(FadeIn(note))
        self.wait(1.5)
        a1, a2 = A @ v1, A @ v2
        ang = math.degrees(math.acos(float(a1 @ a2 / (np.linalg.norm(a1) * np.linalg.norm(a2)))))
        note2 = bi(["v₁、v₂ 的像夹角 %.0f°：仍然垂直" % ang, "images of v1, v2 meet at %.0f°: still perpendicular" % ang], 24, YELLOW)
        note2.next_to(note, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(note2))
        lab1 = MathTex(r"\sigma_1\boldsymbol u_1", color=RED, font_size=36).next_to(P(v1), RIGHT, buff=0.1)
        lab2 = MathTex(r"\sigma_2\boldsymbol u_2", color=GREEN, font_size=36).next_to(P(v2), RIGHT, buff=0.1)
        self.play(Write(lab1), Write(lab2))
        self.caption("它们正是椭圆的两根半轴：σ₁ = √45，σ₂ = √5", "They are the semi-axes: σ1 = √45, σ2 = √5")
        self.wait(1)
        self.card([["任何矩阵都把单位圆变成椭圆", "Every matrix maps the unit circle to an ellipse"],
                   MathTex(r"A\boldsymbol v_1=\sigma_1\boldsymbol u_1,\qquad A\boldsymbol v_2=\sigma_2\boldsymbol u_2", font_size=44),
                   ["v₁ ⟂ v₂，且 u₁ ⟂ u₂", "v1 ⟂ v2 and u1 ⟂ u2"]])
