"""动画 30.3.1（配图 30.3.1）：尺寸综合。
(1) 臂展不变（a2 + a3 = 0.76 m），大臂 a2 从 0.30 m 变到 0.50 m：手腕点 P4 能到的圆环 |a2 − a3| ≤ ρ ≤ a2 + a3 外圈不变、
    内圈先缩到零再长大；J1 模组的半径 5.5 cm 画成灰圈，内圈小于它时死区落在机器人自己身上；J3 的重力矩随 a3 变短而下降。
(2) 选模组：六个关节先各取够用的最小模组（M M M S S S → 实际 J1 自己 M、J2 L、J3 M、腕部 S），再按两条通用规则：
    J1 与 J2 一样（L），腕部三个一样（S）：L L M S S S。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("30.3", "尺寸综合", "Dimensional synthesis")
        sc = 3.6
        o = np.array([-3.0, -0.6, 0])
        a2 = ValueTracker(0.30)
        S = 0.76

        def ring():
            x = a2.get_value()
            ro, ri = sc * S, sc * abs(2 * x - S)
            outer = Circle(radius=ro, color=STEEL, stroke_width=2).move_to(o)
            inner = Circle(radius=max(ri, 0.001), color=RED, stroke_width=3).move_to(o)
            ann = Annulus(inner_radius=max(ri, 0.001), outer_radius=ro, color=STEEL, fill_opacity=0.15, stroke_width=0).move_to(o)
            return VGroup(ann, outer, inner)
        g = always_redraw(ring)
        mod = Circle(radius=sc * 0.055, color=GREY_B, stroke_width=2).move_to(o)
        self.add(g, mod, Dot(o, color=YELLOW, radius=0.06))
        rd = always_redraw(lambda: VGroup(
            zh(f"大臂 a2 = {a2.get_value():.2f} m，小臂 a3 = {S - a2.get_value():.2f} m", 22, INK),
            zh(f"死区半径 |a2 − a3| = {abs(2 * a2.get_value() - S) * 100:.0f} cm", 22, RED),
            zh(f"J3 最大重力矩 ≈ {56 - 99 * (a2.get_value() - 0.30):.0f} N·m", 22, BLUE)).arrange(DOWN, aligned_edge=LEFT).move_to([3.3, 1.6, 0]))
        self.add(rd)
        zc, zs = np.array([3.3, -1.4, 0]), 5.0                 # 放大看肩部：1 m = 5 格
        zoom = always_redraw(lambda: VGroup(
            Circle(radius=zs * 0.055, color=GREY_B, stroke_width=3).move_to(zc),
            Circle(radius=max(zs * abs(2 * a2.get_value() - S), 0.001), color=RED, stroke_width=3).move_to(zc),
            Dot(zc, color=YELLOW, radius=0.05)))
        self.add(zoom, zh("放大：红圈 = 死区，灰圈 = J1 模组（半径 5.5 cm）", 18, GREY_B).move_to([3.3, -0.3, 0]))
        self.play(a2.animate.set_value(0.50), run_time=4.0, rate_func=linear)
        self.play(a2.animate.set_value(0.40), run_time=1.5)
        self.caption("大臂长一点，J3 轻松一点；可死区一旦超出 J1 模组，就成了真正够不着的地方。取差 4 cm：0.40 / 0.36",
                     "A longer upper arm eases J3, but once the hole is wider than the J1 module it is truly lost; a 4 cm difference: 0.40 / 0.36", wait=2.0)
        self.clear_stage()
        # (2) 选模组
        cols = {"S": GREEN, "M": BLUE, "L": RED}
        own = ["M", "L", "M", "S", "S", "S"]
        fin = ["L", "L", "M", "S", "S", "S"]
        boxes = VGroup()
        for i, s in enumerate(own):
            b = VGroup(RoundedRectangle(width=1.4, height=1.0, corner_radius=0.12, color=cols[s], fill_opacity=0.35),
                       zh(f"J{i + 1}", 22, INK), zh(s, 30, cols[s], BOLD))
            b[1].move_to(b[0].get_top() + DOWN * 0.25)
            b[2].move_to(b[0].get_center() + DOWN * 0.12)
            b.move_to([-4.6 + 1.85 * i, 0.6, 0])
            boxes.add(b)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in boxes], lag_ratio=0.15), run_time=1.5)
        self.add(zh("每个关节：够用的最小模组（峰值、连续力矩都要够，含 1.2 倍安全系数）", 22, INK).move_to([0, 1.8, 0]))
        self.wait(1.0)
        newL = zh("L", 30, RED, BOLD).move_to(boxes[0][2])
        self.play(Transform(boxes[0][2], newL), boxes[0][0].animate.set_color(RED), run_time=0.8)
        r1 = zh("J1 与 J2 用同一种：底座模组承受整条手臂的倾覆力矩，少一种零件", 22, YELLOW).move_to([0, -0.8, 0])
        r2 = zh("腕部三个用同一种：备件通用", 22, YELLOW).move_to([0, -1.4, 0])
        self.play(FadeIn(r1), FadeIn(r2), run_time=0.8)
        self.caption("算出来的 J1 只要中模组；设计不只是算，还要看零件种类、备件和以后的大负载型号",
                     "J1 alone needs only the medium module; design also weighs part variety, spares and a later heavier model", wait=2.0)
        self.card([["尺寸综合", "Dimensional synthesis"],
                   MathTex(r"|a_2 - a_3| \le \rho_{P_4} \le a_2 + a_3", font_size=40),
                   ["a2 − a3 = 4 cm < J1 模组半径：死区落在自己身上", "a2 − a3 = 4 cm < J1 module radius: the hole lies inside the robot"],
                   ["模组 L L M S S S：J3 的连续力矩用到 97%", "Modules L L M S S S: J3's continuous torque at 97 %"]])
