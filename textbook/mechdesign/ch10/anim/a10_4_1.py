"""动画 10.4.1（配图 10.4.1）：带孔板的应力流线与应力集中。
无限大板单向拉伸 σ，中间圆孔半径 a，用基尔施（Kirsch, 1898）的弹性力学解：
  σr = σ/2 (1 − a²/r²) + σ/2 (1 − 4a²/r² + 3a⁴/r⁴) cos 2θ，σθ = σ/2 (1 + a²/r²) − σ/2 (1 + 3a⁴/r⁴) cos 2θ，
  τrθ = −σ/2 (1 + 2a²/r² − 3a⁴/r⁴) sin 2θ。
画出最大主应力的方向线（“力流”）：远处是一条条平行的直线，靠近孔时绕过孔、在孔的上下两侧挤在一起；
再沿孔正上方的竖线画 σx / σ，孔边是 3，离开一个孔径就降到 1.07 左右。最后说明有限元网格要在孔边加密（程序 10.4.1）。"""
import math

import numpy as np
from manim import *
from wq_anim import *

A = 0.55                        # 孔半径（画面单位）
C0 = LEFT * 1.6 + UP * 0.2      # 孔心（画面）
XW, YH = 3.6, 2.0               # 板的半宽、半高


def stress(x, y):
    r2 = x * x + y * y
    r = math.sqrt(r2)
    th = math.atan2(y, x)
    a2, a4 = A * A / r2, A ** 4 / r2 ** 2
    c2, s2 = math.cos(2 * th), math.sin(2 * th)
    sr = 0.5 * (1 - a2) + 0.5 * (1 - 4 * a2 + 3 * a4) * c2
    st = 0.5 * (1 + a2) - 0.5 * (1 + 3 * a4) * c2
    tr = -0.5 * (1 + 2 * a2 - 3 * a4) * s2
    c, s = math.cos(th), math.sin(th)
    sx = sr * c * c + st * s * s - 2 * tr * s * c
    sy = sr * s * s + st * c * c + 2 * tr * s * c
    txy = (sr - st) * s * c + tr * (c * c - s * s)
    return sx, sy, txy


def dir1(x, y):
    sx, sy, txy = stress(x, y)
    ang = 0.5 * math.atan2(2 * txy, sx - sy)
    return np.array([math.cos(ang), math.sin(ang)])


def trajectory(y0):
    p = np.array([-XW, y0])
    pts = [p.copy()]
    d_prev = np.array([1.0, 0.0])
    for _ in range(2000):
        d = dir1(*p)
        if d @ d_prev < 0:
            d = -d
        p = p + 0.01 * d
        d_prev = d
        if math.hypot(*p) < A * 1.02 or p[0] > XW:
            break
        pts.append(p.copy())
    return pts


class Lesson(Base):
    def construct(self):
        self.title("10.4", "带孔板：力流绕过孔，孔边应力升到 3 倍", "Plate with a hole: the force flow bends round, the edge stress triples")
        plate = Rectangle(width=2 * XW, height=2 * YH, color=GREY_B, fill_color="#26344a", fill_opacity=1).move_to(C0)
        hole = Circle(radius=A, color=WHITE, fill_color=BLACK, fill_opacity=1).move_to(C0)
        arrows = VGroup(*[Arrow(C0 + RIGHT * (XW + 0.05) + UP * y, C0 + RIGHT * (XW + 0.6) + UP * y, buff=0, color=YELLOW, stroke_width=3)
                          for y in np.linspace(-YH + 0.25, YH - 0.25, 7)] +
                        [Arrow(C0 + LEFT * (XW + 0.05) + UP * y, C0 + LEFT * (XW + 0.6) + UP * y, buff=0, color=YELLOW, stroke_width=3)
                         for y in np.linspace(-YH + 0.25, YH - 0.25, 7)])
        self.play(FadeIn(plate), FadeIn(hole), FadeIn(arrows))
        self.caption("一块板两头受拉，中间开一个圆孔", "A plate pulled at both ends, with a round hole in the middle")
        lines = VGroup()
        for y0 in np.linspace(-YH + 0.12, YH - 0.12, 15):
            pts = trajectory(y0)
            if len(pts) < 5:
                continue
            ln = VMobject(color=BLUE, stroke_width=2).set_points_smoothly([C0 + RIGHT * q[0] + UP * q[1] for q in pts[::6]])
            lines.add(ln)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.08), run_time=4)
        self.caption("最大主应力的方向线（“力流”）：远处平行，到孔附近绕过去，在孔的上下两侧挤在一起",
                     "Lines of the largest principal stress (the force flow): parallel far away, bending round the hole and crowding above and below it", wait=2)
        # 孔正上方的 σx / σ
        ys = np.linspace(A, YH, 80)
        base = C0 + RIGHT * 4.6 + DOWN * YH
        ax = VGroup(Line(base, base + UP * 2 * YH, color=GREY_B), Line(base, base + RIGHT * 1.9, color=GREY_B))
        K = 0.6
        curve = VMobject(color=RED, stroke_width=4).set_points_smoothly(
            [base + RIGHT * K * stress(0.0, y)[0] + UP * (y - A) * 2 * YH / (YH - A) for y in ys])
        lbl3 = Text("3σ", font_size=22, color=RED).next_to(base + RIGHT * K * 3, UP, buff=0.1)
        lbl1 = Text("σ", font_size=22, color=GREY_A).next_to(base + RIGHT * K * 1 + UP * 2 * YH, UP, buff=0.1)
        tick1 = DashedLine(base + RIGHT * K, base + RIGHT * K + UP * 2 * YH, color=GREY_B, stroke_width=1.5)
        mark = DashedLine(C0 + UP * A, C0 + UP * YH, color=RED, stroke_width=2)
        lb0 = Text("孔边 hole edge", font_size=14, color=GREY_A).next_to(base, DOWN, buff=0.08)
        lbu = Text("↑ 离孔边的距离", font_size=14, color=GREY_A).next_to(base + UP * YH, LEFT, buff=0.08)
        self.play(Create(mark), Create(ax), Create(tick1), FadeIn(lbl1), FadeIn(lb0), FadeIn(lbu))
        self.play(Create(curve), FadeIn(lbl3), run_time=2)
        self.caption("沿孔正上方这条线看 σx：孔边是远处的 3 倍——理论应力集中系数 Kt = 3；离开一个孔径，就差不多回到 σ",
                     "Along the line above the hole: σx at the edge is 3 times the remote value — Kt = 3; one diameter away it is nearly back to σ", wait=2.5)
        # 有限元：孔边网格粗细
        coarse = RegularPolygon(n=8, radius=A, color=ORANGE, stroke_width=3).move_to(C0).rotate(PI / 8)
        fine = RegularPolygon(n=32, radius=A, color=GREEN, stroke_width=3).move_to(C0)
        self.play(Create(coarse))
        self.caption("有限元：孔边的网格太粗，孔被“切成”多边形，峰值也被抹平", "FE: too coarse a mesh turns the hole into a polygon and smears the peak", wait=1.5)
        self.play(ReplacementTransform(coarse, fine))
        self.caption("孔边加密，峰值收敛到 3；尖角没有确定的峰值，越加密越大（程序 10.4.1）",
                     "Refine at the hole and the peak converges to 3; a sharp corner has no definite peak — it keeps rising (Program 10.4.1)", wait=2)
        self.card([["孔、圆角、键槽：力流被挤，局部应力升高", "holes, fillets, keyseats: the flow crowds, local stress rises"],
                   ["Kt = 最大应力 / 名义应力；圆孔 Kt = 3", "Kt = peak / nominal; round hole Kt = 3"],
                   ["有限元：在应力集中处加密网格，看结果收敛没有", "FE: refine where stress concentrates and check convergence"],
                   ["静载：塑性材料局部屈服可以重新分布，脆性材料不行", "static: ductile parts redistribute by local yielding, brittle ones cannot"]])
