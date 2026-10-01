"""动画 4.1.1（配图 4.1.1）：零件绕 O 转过 30°，角点 P 沿圆弧移至 P′；坐标系 {a} 不动。"""
from manim import *
from wq_anim import *
import numpy as np
import math

S = 9.0                     # 1 m 画成 9 个单位


class Lesson(Base):
    def construct(self):
        self.title("4.1", "零件绕吸盘中心转动", "A part rotating about the suction cup")
        O = np.array([-0.5, -0.6, 0])
        axes = VGroup(Arrow(O + LEFT * 3.2, O + RIGHT * 3.6, buff=0, color=RED, stroke_width=4),
                      Arrow(O + DOWN * 2.0, O + UP * 2.9, buff=0, color=GREEN, stroke_width=4),
                      MathTex("x", color=RED).next_to(O + RIGHT * 3.6, DR, buff=0.05),
                      MathTex("y", color=GREEN).next_to(O + UP * 2.9, UL, buff=0.05),
                      MathTex("O", color=INK, font_size=30).next_to(O, DL, buff=0.08))
        part = Rectangle(width=0.4 * S, height=0.2 * S, color=STEEL, fill_color=NAVY, fill_opacity=0.75).move_to(O)
        P0 = O + np.array([0.2, 0.1, 0]) * S
        dot = Dot(P0, color=YELLOW, radius=0.08)
        lab = MathTex("P", color=YELLOW).next_to(dot, UR, buff=0.05)
        axes.set_z_index(2)
        self.play(Create(axes), FadeIn(part), FadeIn(dot), Write(lab))
        self.caption("角点 P 在 {a} 中的分量：(0.2, 0.1) m", "Corner P: (0.2, 0.1) m in {a}")

        r = np.linalg.norm(P0 - O)
        phi = math.atan2(0.1, 0.2)
        radius = Line(O, P0, color=INK, stroke_width=3)
        rlab = MathTex("r", color=INK, font_size=32).move_to(O + (P0 - O) * 0.5 + np.array([0.0, 0.25, 0]))
        self.play(Create(radius), Write(rlab))
        self.caption("转动时，P 到 O 的距离 r 保持不变", "The distance r stays the same while turning")

        theta = ValueTracker(0.0)
        ghost = part.copy().set_fill(opacity=0.15).set_stroke(opacity=0.4)
        self.add(ghost)
        trace = always_redraw(lambda: Arc(radius=r, start_angle=phi, angle=theta.get_value() + 1e-6, arc_center=O,
                                          color=ORANGE, stroke_width=5))
        self.add(trace)
        part.add_updater(lambda m: m.become(Rectangle(width=0.4 * S, height=0.2 * S, color=STEEL, fill_color=NAVY,
                                                         fill_opacity=0.75).move_to(O).rotate(theta.get_value(), about_point=O)))
        dot.add_updater(lambda m: m.move_to(O + r * np.array([math.cos(phi + theta.get_value()), math.sin(phi + theta.get_value()), 0])))
        radius.add_updater(lambda m: m.put_start_and_end_on(O, dot.get_center()))
        lab.add_updater(lambda m: m.next_to(dot, UR, buff=0.05))
        rlab.add_updater(lambda m: m.move_to(O + (dot.get_center() - O) * 0.55 + rotate_vector(dot.get_center() - O, PI / 2) / np.linalg.norm(dot.get_center() - O) * 0.3))
        angle = always_redraw(lambda: VGroup(
            Arc(radius=0.9, start_angle=phi, angle=theta.get_value() + 1e-6, arc_center=O, color=YELLOW, stroke_width=4),
            MathTex(r"\theta=%d^\circ" % round(math.degrees(theta.get_value())), color=YELLOW, font_size=40)
            .to_corner(UR, buff=0.6)))
        self.add(angle)
        self.caption("零件绕 O 转过 30°，P 沿圆弧走到 P′", "The part turns 30° about O; P moves along an arc to P′", wait=0)
        self.play(theta.animate.set_value(math.radians(30)), run_time=3, rate_func=smooth)
        self.wait(0.5)
        for m in (part, dot, radius, lab, rlab):
            m.clear_updaters()
        self.play(Transform(lab, MathTex("P'", color=YELLOW).next_to(dot, UR, buff=0.05)))
        self.caption("坐标系 {a} 没有动；转动的是零件", "Frame {a} stays fixed; the part rotates")
        res = MathTex(r"P'=(0.12321,\ 0.18660)\ \mathrm{m}", color=YELLOW, font_size=36).to_corner(UR, buff=0.6).shift(DOWN * 0.9)
        self.play(Write(res))
        self.wait(1)
        self.card([["主动转动", "Active rotation"],
                   MathTex(r"x'=r\cos(\varphi+\theta),\quad y'=r\sin(\varphi+\theta)", font_size=38),
                   ["距离不变，方位角增加 θ", "distance unchanged, direction angle increased by θ"]])
