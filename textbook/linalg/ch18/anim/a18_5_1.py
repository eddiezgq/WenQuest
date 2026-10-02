"""动画 18.5.1（配图 18.5.1）：极分解 A = QS——单位圆先由 S 沿 v1、v2 伸缩成椭圆，再由 Q 整体转过约 26.6°。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("18.5", "极分解：先伸缩，再转动", "Polar decomposition: stretch, then rotate")
        r5 = math.sqrt(5)
        S = r5 * np.array([[2.0, 1.0], [1.0, 2.0]])
        th = math.atan2(1.0, 2.0)
        k = 0.42
        O = np.array([0.0, -0.4, 0.0])
        s = ValueTracker(0.0)

        def M():
            x = s.get_value()
            if x <= 1:
                return (1 - x) * np.eye(2) + x * S
            a = th * (x - 1)
            Q = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
            return Q @ S

        def P(v):
            w = M() @ np.asarray(v, dtype=float)
            return O + k * np.array([w[0], w[1], 0.0])

        r2 = 1 / math.sqrt(2)

        def scene():
            g = VGroup()
            pts = [P([math.cos(a), math.sin(a)]) for a in np.linspace(0, 2 * math.pi, 121)]
            g.add(Polygon(*pts[:-1], color=YELLOW, stroke_width=4))
            flag = [[0.25, 0.15], [0.56, 0.15], [0.56, 0.27], [0.44, 0.27], [0.44, 0.36], [0.25, 0.36]]
            g.add(Polygon(*[P(q) for q in flag], color=GOLD, fill_color=GOLD, fill_opacity=0.8, stroke_width=2))
            g.add(Arrow(O, P([r2, r2]), buff=0, color=RED, stroke_width=6),
                  Arrow(O, P([r2, -r2]), buff=0, color=GREEN, stroke_width=6))
            return g

        axes = VGroup(DashedLine(O + 3.2 * np.array([-r2, -r2, 0]), O + 3.2 * np.array([r2, r2, 0]), color=GREY_B),
                      DashedLine(O + 3.2 * np.array([-r2, r2, 0]), O + 3.2 * np.array([r2, -r2, 0]), color=GREY_B))
        sc = always_redraw(scene)
        self.play(FadeIn(sc), Create(axes))
        self.caption("虚线：S 的两根伸缩轴 v₁、v₂，互相垂直", "Dashed: the stretch axes v1, v2 of S, perpendicular")
        self.play(s.animate.set_value(1.0), run_time=3)
        self.caption("S 沿 v₁ 伸长 3√5 倍、沿 v₂ 伸长 √5 倍：纯伸缩，没有转动",
                     "S stretches by 3√5 along v1 and √5 along v2: pure stretch, no turning")
        self.play(FadeOut(axes))
        self.play(s.animate.set_value(2.0), run_time=2.5)
        self.caption("Q 再把整个图形转过约 26.6°，得到 A 的作用", "Q then turns everything by about 26.6°: the action of A")
        self.wait(1)
        self.card([["极分解", "Polar decomposition"],
                   MathTex(r"A = QS,\quad Q = UV^{\mathsf T},\quad S = V\Sigma V^{\mathsf T}", font_size=46),
                   ["Q 是离 A 最近的正交矩阵", "Q is the orthogonal matrix nearest to A"]])
