"""动画 3.1.1（配图 3.1.1，三维的情形）：三个平面的相对位置。前两个平面都经过竖直的 z 轴（它们的交线）。
第三个平面先是水平的，与 z 轴交于一点，三个平面交于一点（唯一解）；它竖起来、与 z 轴平行而不经过 z 轴时，
三个平面两两相交于三条平行线，围成三棱柱的侧面，没有公共点（无解）；再把它平移到经过 z 轴，三个平面交于同一条直线（无穷多解）。
画面是斜二测投影。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("3.1", "三个平面怎样相交", "How three planes meet")
        O = np.array([-0.6, -0.6, 0.0])
        s = 1.25
        P = lambda p: proj3(p, O, s)
        zhat = np.array([0.0, 0.0, 1.0])

        def patch(c, u, v, a, color, op=0.28):
            u, v = u / np.linalg.norm(u), v / np.linalg.norm(v)
            pts = [P(c + a * (i * u + j * v)) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            return Polygon(*pts, color=color, fill_opacity=op, stroke_width=1.5)

        u1, u2 = np.array([-0.6, 1.0, 0.0]), np.array([1.0, 1.2, 0.0])
        p1 = patch(np.zeros(3), u1, zhat, 1.6, BLUE)
        p2 = patch(np.zeros(3), u2, zhat, 1.6, GREEN)
        axis = DashedLine(P([0, 0, -1.8]), P([0, 0, 1.8]), color=GREY_B)
        self.play(FadeIn(p1), FadeIn(p2), Create(axis))
        self.caption("前两个平面交于一条直线（这里是 z 轴）", "The first two planes meet in a line (here the z axis)")
        phi = ValueTracker(0.0)
        off = ValueTracker(1.0)
        w = np.array([1.0, -0.6, 0.0])
        wn = np.array([0.6, 1.0, 0.0])
        wn = wn / np.linalg.norm(wn)

        def third():
            f, o = phi.get_value(), off.get_value()
            v = math.cos(f) * wn + math.sin(f) * zhat
            c = o * np.array([0.9, 0.9, 0.0]) + np.array([0, 0, 0.6]) * (1 - f / (math.pi / 2))
            g = VGroup(patch(c, w, v, 1.6, ORANGE))
            n = np.cross(w, v)
            if abs(n[2]) > 0.15:
                z = n @ c / n[2]
                g.add(Dot(P([0, 0, z]), color=RED, radius=0.09))
            return g

        t3 = always_redraw(third)
        self.play(FadeIn(t3))
        self.caption("第三个平面水平放置：与 z 轴交于一点，三个平面有唯一公共点", "A level third plane meets the z axis once: one common point")
        self.wait(0.6)
        self.caption("把第三个平面竖起来，让它与 z 轴平行", "Tilt the third plane until it is parallel to the z axis", wait=0.3)
        self.play(phi.animate.set_value(math.pi / 2), run_time=3.0)
        note = bi(["两两相交于三条平行线：没有公共点（无解）", "pairwise in three parallel lines: no common point"], 26, RED).to_corner(UR, buff=0.5).shift(DOWN * 0.7)
        self.play(FadeIn(note))
        self.wait(1.2)
        self.caption("再把它平移到经过 z 轴", "Now slide it until it contains the z axis", wait=0.3)
        self.play(FadeOut(note), off.animate.set_value(0.0), run_time=2.5)
        line = Line(P([0, 0, -1.8]), P([0, 0, 1.8]), color=RED, stroke_width=6)
        note2 = bi(["三个平面交于同一条直线（无穷多解）", "all three share one line: infinitely many solutions"], 26, RED).to_corner(UR, buff=0.5).shift(DOWN * 0.7)
        self.play(Create(line), FadeIn(note2))
        self.caption("三个平面绕同一根轴展开，像书页一样", "Three planes fanned around one axis, like pages of a book")
        self.wait(1.0)
        self.card([["三个平面：一点、无点、一条线", "Three planes: a point, nothing, or a line"],
                   ["唯一解、无解、无穷多解", "one solution, none, infinitely many"],
                   ["不会恰好有两个解", "never exactly two"]])
