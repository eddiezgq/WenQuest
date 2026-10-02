"""动画 10.1.1（配图 10.1.2）：AGV 沿圆弧转弯。左：以地面为参考系，零件静止、AGV 走圆；
右：以 AGV 为参考系，AGV 静止、零件绕圆心 C 转圈（算例 10.1.1：v = 0.5 m/s，R0 = 2.0 m，零件在 (2.0, 0.5) m）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

V, R0 = 0.5, 2.0
OM = V / R0
C = np.array([0.0, R0])
P = np.array([2.0, 0.5])
S = 0.72                                     # 1 m 画成 0.72 个单位
LO = np.array([-3.6, -1.35, 0])               # 左画面中地面原点的位置
RO = np.array([3.4, -1.75, 0])                # 右画面中 AGV 的位置


def rot(a, p):
    c, s = math.cos(a), math.sin(a)
    return np.array([c * p[0] - s * p[1], s * p[0] + c * p[1]])


def L(p):
    return LO + S * np.array([p[0], p[1], 0])


def Rr(p):
    return RO + S * np.array([p[0], p[1], 0])


def car(center, ang, color=STEEL):
    body = Rectangle(width=0.32, height=0.22, color=color, fill_color=NAVY, fill_opacity=1, stroke_width=3)
    nose = Triangle(color=YELLOW, fill_color=YELLOW, fill_opacity=1).scale(0.06).rotate(-PI / 2).move_to(RIGHT * 0.12)
    return VGroup(body, nose).rotate(ang).move_to(center)


class Lesson(Base):
    def construct(self):
        self.title("10.1", "同一运动，两个参考系", "One motion, two reference frames")
        sep = DashedLine(UP * 2.4, DOWN * 2.2, color=GREY_D)
        lt = zh("以地面为参考系", 24, INK).move_to(np.array([-3.4, 2.25, 0]))
        rt = zh("以 AGV 为参考系", 24, INK).move_to(np.array([3.4, 2.25, 0]))
        self.play(Create(sep), FadeIn(lt), FadeIn(rt))
        circ = Circle(radius=S * R0, color=GREY_B, stroke_width=2).move_to(L(C))
        circ.set_stroke(opacity=0.6)
        cdot = VGroup(Cross(scale_factor=0.08, stroke_color=INK).move_to(L(C)), MathTex("C", font_size=26, color=INK).next_to(L(C), UR, buff=0.05))
        part_l = Square(0.18, color=ORANGE, fill_color=ORANGE, fill_opacity=1).move_to(L(P))
        lab_l = zh("零件（静止）", 18, ORANGE).next_to(part_l, DR, buff=0.08)
        cb = np.array([0.0, R0])
        d = float(np.linalg.norm(P - C))
        path_r = Circle(radius=S * d, color=ORANGE, stroke_width=2).move_to(Rr(cb))
        path_r.set_stroke(opacity=0.5)
        cdot_r = VGroup(Cross(scale_factor=0.08, stroke_color=INK).move_to(Rr(cb)), MathTex("C", font_size=26, color=INK).next_to(Rr(cb), UR, buff=0.05))
        agv_r = car(Rr([0, 0]), 0)
        lab_r = zh("AGV（静止）", 18, STEEL).next_to(agv_r, DOWN, buff=0.12)
        self.play(Create(circ), FadeIn(cdot), FadeIn(part_l), FadeIn(lab_l), FadeIn(cdot_r), FadeIn(agv_r), FadeIn(lab_r))
        t = ValueTracker(0.0)

        def agv_pose(tt):
            psi = OM * tt
            return C + R0 * np.array([math.sin(psi), -math.cos(psi)]), psi

        agv_l = always_redraw(lambda: car(L(agv_pose(t.get_value())[0]), agv_pose(t.get_value())[1]))
        trail = TracedPath(lambda: Rr(rot(-agv_pose(t.get_value())[1], P - agv_pose(t.get_value())[0])), stroke_color=ORANGE, stroke_width=4)
        part_r = always_redraw(lambda: Square(0.18, color=ORANGE, fill_color=ORANGE, fill_opacity=1).move_to(
            Rr(rot(-agv_pose(t.get_value())[1], P - agv_pose(t.get_value())[0]))))
        clock = always_redraw(lambda: MathTex(r"t = %.1f\ \mathrm{s}" % t.get_value(), font_size=30, color=YELLOW).move_to(np.array([0, 1.75, 0])))
        self.add(agv_l, trail, part_r, clock)
        self.caption("地面上：零件不动，AGV 以 0.5 m/s 沿半径 2 m 的圆左转", "On the ground: the part stays, the AGV turns left on a 2 m circle at 0.5 m/s", wait=0)
        self.play(t.animate.set_value(8.0), run_time=6, rate_func=linear)
        self.play(Create(path_r), run_time=0.6)
        self.caption("AGV 上看：零件绕 C 顺时针转圈，半径 |CP| = 2.5 m，速率 0.625 m/s",
                     "Seen from the AGV: the part circles C clockwise, radius 2.5 m, speed 0.625 m/s", wait=0)
        self.play(t.animate.set_value(20.0), run_time=7, rate_func=linear)
        self.wait(0.5)
        self.caption("换参考系，运动本身就变了；换坐标系，只是读数变了", "Change the reference frame and the motion changes; change the coordinates and only the numbers change")
        self.card([["参考系与坐标系", "Reference frame vs coordinates"],
                   MathTex(r"p_b(t) = R_{sb}(t)^{\mathsf T}\big(p_s - p_{sb}(t)\big)", font_size=44),
                   ["静止的零件，在转弯的 AGV 上看是在绕 C 转圈", "A part at rest circles C when seen from the turning AGV"]])
