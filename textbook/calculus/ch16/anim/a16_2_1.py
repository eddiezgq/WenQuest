"""动画 16.2.1（配图 16.2.1）：祖暅原理——“幂势既同，则积不容异”。先看半球与“圆柱挖去倒圆锥”：任何高度 z 处，
一个截面是半径 √(r² − z²) 的圆，一个是外半径 r、内半径 z 的圆环，面积都是 π(r² − z²)，所以体积相等；
再看球与牟合方盖：同一高度的截面是圆与它的外切正方形，面积之比处处是 π : 4，所以体积之比也是 π : 4。"""
from manim import *
from wq_anim import *
import numpy as np

R = 1.6


class Lesson(Base):
    def construct(self):
        self.title("16.2", "祖暅原理", "Zu Geng's principle")
        # 侧视图：左半球，右圆柱挖去倒圆锥（锥顶在底面中心）
        o1 = LEFT * 4.2 + DOWN * 1.6
        o2 = LEFT * 0.4 + DOWN * 1.6
        hemi = Arc(radius=R, start_angle=0, angle=PI, color=STEEL, stroke_width=3).move_arc_center_to(o1)
        base1 = Line(o1 + LEFT * R, o1 + RIGHT * R, color=STEEL)
        cyl = Rectangle(width=2 * R, height=R, color=ORANGE, stroke_width=3).move_to(o2 + UP * R / 2)
        cone = VMobject(color=ORANGE, stroke_width=2).set_points_as_corners([o2 + UP * R + LEFT * R, o2, o2 + UP * R + RIGHT * R])
        coneF = Polygon(o2 + UP * R + LEFT * R, o2, o2 + UP * R + RIGHT * R, color=ORANGE, fill_opacity=0.12, stroke_width=0)
        l1 = Text("半球", font_size=24, color=STEEL).next_to(o1 + DOWN * 0.1, DOWN, buff=0.15)
        l2 = Text("圆柱挖去倒圆锥", font_size=24, color=ORANGE).next_to(o2 + DOWN * 0.1, DOWN, buff=0.15)
        self.play(Create(hemi), Create(base1), Create(cyl), Create(cone), FadeIn(coneF), Write(l1), Write(l2))
        z = ValueTracker(0.0)
        cut1 = always_redraw(lambda: Line(o1 + LEFT * (R + 0.3) + UP * z.get_value(), o1 + RIGHT * (R + 0.3) + UP * z.get_value(), color=RED, stroke_width=2))
        cut2 = always_redraw(lambda: Line(o2 + LEFT * (R + 0.3) + UP * z.get_value(), o2 + RIGHT * (R + 0.3) + UP * z.get_value(), color=RED, stroke_width=2))
        # 俯视截面
        c1 = RIGHT * 3.0 + UP * 1.1
        c2 = RIGHT * 3.0 + DOWN * 1.9
        disk = always_redraw(lambda: Circle(radius=max(np.sqrt(max(R * R - z.get_value() ** 2, 0)), 1e-3) * 0.55, color=STEEL, fill_opacity=0.6, stroke_width=2).move_to(c1))
        ring_o = Circle(radius=R * 0.55, color=ORANGE, fill_opacity=0.6, stroke_width=2).move_to(c2)
        ring_i = always_redraw(lambda: Circle(radius=max(z.get_value(), 1e-3) * 0.55, color=BG, fill_color=BG, fill_opacity=1, stroke_width=1).move_to(c2))
        v = always_redraw(lambda: MathTex(r"\pi(r^2-z^2)=%.2f" % (np.pi * (R * R - z.get_value() ** 2) / (R * R)), font_size=28)
                          .next_to(c1 + RIGHT * 0.9, RIGHT, buff=0.1))
        v2 = always_redraw(lambda: MathTex(r"\pi r^2-\pi z^2=%.2f" % (np.pi * (R * R - z.get_value() ** 2) / (R * R)), font_size=28)
                           .next_to(c2 + RIGHT * 0.9, RIGHT, buff=0.1))
        self.add(cut1, cut2, disk, ring_o, ring_i, v, v2)
        self.caption("同一高度 z 处切开：一个截面是圆，一个是圆环", "Cut both at height z: one section is a disk, the other a ring", wait=0.3)
        self.play(z.animate.set_value(R * 0.97), run_time=4, rate_func=there_and_back)
        self.play(z.animate.set_value(R * 0.5), run_time=1.5)
        self.caption("两个截面的面积处处相等（取 r = 1）", "The two areas agree at every height (r = 1)", wait=0.6)
        res = MathTex(r"V_{\text{hemi}}=\pi r^3-\tfrac13\pi r^3=\tfrac23\pi r^3", font_size=34).to_edge(UP, buff=1.25)
        self.play(Write(res))
        self.caption("幂势既同，则积不容异：体积也相等", "Equal sections at every height, equal volumes", wait=1.2)
        self.play(*[FadeOut(m) for m in (hemi, base1, cyl, cone, coneF, l1, l2, cut1, cut2, disk, ring_o, ring_i, v, v2, res)])
        # 第二部分：牟合方盖与球的俯视截面
        w = ValueTracker(0.0)
        cc = LEFT * 2.2 + DOWN * 0.3
        sq = always_redraw(lambda: Square(side_length=2 * np.sqrt(max(R * R - w.get_value() ** 2, 1e-4)), color=GOLD, fill_opacity=0.45, stroke_width=2).move_to(cc))
        ci = always_redraw(lambda: Circle(radius=np.sqrt(max(R * R - w.get_value() ** 2, 1e-4)), color=STEEL, fill_opacity=0.7, stroke_width=2).move_to(cc))
        cube = Square(side_length=2 * R, color=GREY_B, stroke_width=2).move_to(cc).set_stroke(opacity=0.8)
        txt = always_redraw(lambda: VGroup(
            MathTex(r"z=%.2f" % (w.get_value() / R), font_size=30),
            MathTex(r"\text{circle}:\ \pi(r^2-z^2)", font_size=30, color=STEEL),
            MathTex(r"\text{square}:\ 4(r^2-z^2)", font_size=30, color=GOLD),
            MathTex(r"\text{ratio}=\pi:4", font_size=32)).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT, buff=0.6))
        self.play(Create(cube), FadeIn(sq), FadeIn(ci), FadeIn(txt))
        self.caption("球与牟合方盖：同一高度的截面是圆和它的外切正方形", "Sphere and mouhe fanggai: a disk and its circumscribed square", wait=0.3)
        self.play(w.animate.set_value(R * 0.95), run_time=4, rate_func=there_and_back)
        self.caption("面积之比处处是 π : 4，所以体积之比也是 π : 4", "The ratio is π : 4 at every height, so the volumes are in ratio π : 4", wait=0.6)
        self.play(w.animate.set_value(R * 0.6), run_time=1.2)
        rest = MathTex(r"4r^2-4(r^2-z^2)=4z^2", font_size=32, color=GREY_A).next_to(cube, UP, buff=0.25)
        self.play(Write(rest))
        self.caption("立方体去掉牟合方盖，剩下的截面积 4z² 与两个方锥相同", "Cube minus the solid leaves 4z², the same as two square pyramids", wait=1.2)
        self.play(*[FadeOut(m) for m in (sq, ci, cube, txt, rest)])
        self.card([["祖暅原理", "Zu Geng's principle"],
                   MathTex(r"V=\int_a^bA(z)\,dz,\qquad V_{\text{mouhe}}=8r^3-\tfrac83r^3=\tfrac{16}3r^3,\qquad V_{\text{ball}}=\tfrac\pi4\cdot\tfrac{16}3r^3=\tfrac43\pi r^3", font_size=34),
                   ["截面积处处相等，体积就相等", "Equal cross-sections everywhere give equal volumes"]])
