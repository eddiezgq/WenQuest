"""动画 8.6.1（配图 8.6.1）：转动单元体，看应力分量随方向变化，莫尔圆同步画出。
应力状态取算例 8.5.1 / 8.6.1 的危险点（SH-301 齿轮位表面，额定转矩）：σx = 16.2 MPa、σy = 0、τxy = 27.9 MPa；
主应力 σ₁ = 37.1 MPa、σ₃ = −20.9 MPa，σ₁ 方向与轴线成 36.9°（程序 8.6.1）。"""
import math

from manim import *
from wq_anim import *

SX, SY, TXY = 16.171, 0.0, 27.852
C, R = (SX + SY) / 2, math.hypot((SX - SY) / 2, TXY)
TH1 = 0.5 * math.degrees(math.atan2(2 * TXY, SX - SY))
EL_C = LEFT * 4.2 + UP * 0.6          # 单元体中心
MO_C = RIGHT * 2.8 + UP * 0.3         # 莫尔圆圆心（画面坐标）
K = 1.75 / R                             # MPa → 画面长度


def rot(th):
    """转过 th 度的面上：σx′、τx′y′"""
    t = math.radians(th)
    s = C + (SX - SY) / 2 * math.cos(2 * t) + TXY * math.sin(2 * t)
    tau = -(SX - SY) / 2 * math.sin(2 * t) + TXY * math.cos(2 * t)
    return s, tau


class Lesson(Base):
    def construct(self):
        self.title("8.6", "转动单元体，莫尔圆同步画出", "Rotate the element; Mohr's circle follows")
        th = ValueTracker(0.0)
        axes = VGroup(Line(MO_C + LEFT * (R * K + 0.35), MO_C + RIGHT * (R * K + 0.35), stroke_width=2, color=GREY_B),
                      Line(MO_C + LEFT * C * K + UP * 2.0, MO_C + LEFT * C * K + DOWN * 2.0, stroke_width=2, color=GREY_B))
        circle = Circle(radius=R * K, color=BLUE, stroke_width=4).move_to(MO_C)
        lab_s = Text("σ", font_size=26, color=GREY_A).move_to(MO_C + RIGHT * (R * K + 0.5) + UP * 0.25)
        lab_t = Text("τ↓", font_size=26, color=GREY_A).move_to(MO_C + LEFT * C * K + DOWN * 2.0 + RIGHT * 0.35)

        def element():
            t = th.get_value()
            sq = Square(side_length=1.4, color=WHITE, fill_color="#26344a", fill_opacity=1).rotate(math.radians(t)).move_to(EL_C)
            s, tau = rot(t)
            n = np.array([math.cos(math.radians(t)), math.sin(math.radians(t)), 0])
            tv = np.array([-n[1], n[0], 0])
            grp = VGroup(sq)
            sy_ = 2 * C - s                       # y′ 面上的正应力 σy′ = σx + σy − σx′

            def normal(base, out, val, col):
                """拉为正：箭头从面向外；压：箭头从外面指向面"""
                L = 0.04 * abs(val)
                if L < 0.02:
                    return
                a, b = (base, base + out * L) if val > 0 else (base + out * L, base)
                grp.add(Arrow(a, b, buff=0, color=col, stroke_width=5, max_tip_length_to_length_ratio=0.3))

            for sgn in (1, -1):
                bx = EL_C + sgn * n * 0.7         # x′ 面
                by = EL_C + sgn * tv * 0.7        # y′ 面
                normal(bx, sgn * n, s, RED)
                normal(by, sgn * tv, sy_, ORANGE)
                if abs(tau) > 0.5:
                    grp.add(Arrow(bx - sgn * tv * 0.02 * tau, bx + sgn * tv * 0.02 * tau, buff=0, color=GREEN, stroke_width=4,
                                  max_tip_length_to_length_ratio=0.25))
                    grp.add(Arrow(by - sgn * n * 0.02 * tau, by + sgn * n * 0.02 * tau, buff=0, color=GREEN, stroke_width=4,
                                  max_tip_length_to_length_ratio=0.25))
            return grp

        def point():
            s, tau = rot(th.get_value())
            p = MO_C + RIGHT * (s - C) * K + DOWN * tau * K          # τ 向下为正（与图 8.6.1 一致）
            return VGroup(Line(MO_C, p, color=YELLOW, stroke_width=3), Dot(p, color=YELLOW, radius=0.09))

        def readout_box():
            t = th.get_value()
            s, tau = rot(t)
            return VGroup(Text(f"θ = {t:5.1f}°", font_size=24, color=YELLOW),
                          Text(f"σx′ = {s:6.1f} MPa", font_size=24, color=RED),
                          Text(f"σy′ = {2 * C - s:6.1f} MPa", font_size=24, color=ORANGE),
                          Text(f"τx′y′ = {(0.0 if abs(tau) < 0.05 else tau):6.1f} MPa", font_size=24, color=GREEN)).arrange(DOWN, aligned_edge=LEFT).move_to(EL_C + DOWN * 2.1)

        el, pt, rd = always_redraw(element), always_redraw(point), always_redraw(readout_box)
        self.play(FadeIn(el), FadeIn(rd))
        self.caption("轴表面的一点：沿轴线方向有弯曲正应力 σx，同时有扭转切应力 τ", "A point on the shaft surface: bending stress σx along the axis plus torsional shear τ")
        self.play(Create(axes), FadeIn(lab_s), FadeIn(lab_t), Create(circle), FadeIn(pt))
        self.caption("把 x 面上的 (σx, τxy) 画在 σ–τ 平面上，以 (σx+σy)/2 为圆心画圆——莫尔圆", "Plot (σx, τxy) of the x face in the σ–τ plane and draw a circle centered at (σx+σy)/2 — Mohr's circle", wait=1.5)
        self.play(th.animate.set_value(TH1), run_time=3)
        self.caption(f"单元体转过 {TH1:.1f}°，点在圆上转过两倍的角度，到达最右端：切应力为零，正应力最大——主应力 σ₁ = {C + R:.1f} MPa",
                     f"Turn the element by {TH1:.1f}°: the point travels twice that angle to the right end — zero shear, maximum normal stress σ₁ = {C + R:.1f} MPa", wait=2.5)
        self.play(th.animate.set_value(TH1 + 45), run_time=2)
        self.caption(f"再转 45°（圆上 90°）：切应力最大，等于圆的半径 {R:.1f} MPa", f"Another 45° (90° on the circle): the shear stress is maximum, equal to the radius {R:.1f} MPa", wait=2)
        self.play(th.animate.set_value(TH1 + 90), run_time=2)
        self.caption(f"转到 {TH1 + 90:.1f}°：最小主应力 σ₃ = {C - R:.1f} MPa，与 σ₁ 的方向垂直", f"At {TH1 + 90:.1f}°: the minimum principal stress σ₃ = {C - R:.1f} MPa, perpendicular to σ₁", wait=2)
        self.play(th.animate.set_value(180), run_time=2.5)
        self.caption("转半圈，单元体回到原来的样子，点在圆上正好转了一整圈", "Half a turn brings the element back; the point has gone once round the circle", wait=1.5)
        self.card([["莫尔圆：一点在各个方向上的应力", "Mohr's circle: the stresses at a point in every direction"],
                   ["单元体转 θ，圆上转 2θ", "turn the element by θ, the point moves 2θ"],
                   ["圆与 σ 轴的交点是主应力，半径是最大切应力", "where it meets the σ axis: principal stresses; radius: max shear"],
                   ["强度理论用的就是主应力（第 10 章）", "strength theories use the principal stresses (Chapter 10)"]])
