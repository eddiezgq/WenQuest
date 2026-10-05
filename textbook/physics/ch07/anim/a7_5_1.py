"""动画 7.5.1（配图 7.5.1）：同一个冰球，地面上看与转台上看。转台逆时针转动，冰球从中心沿直线滑出。
左边：地面参考系，转台的辐条在转，冰球走直线；右边：随转台转动的参考系，辐条不动，冰球的轨迹向右弯。"""
from manim import *
from wq_anim import *
import numpy as np

W, V, TEND = 1.0, 0.50, 1.6          # 角速度 rad/s，冰球速度 m/s，滑到台边的时间 s
S = 2.4 / 0.8                        # 画面单位 / 米（台面半径 0.8 m 画成 2.4）
CL = np.array([-3.4, -0.5, 0])       # 左盘中心（地面上看）
CR = np.array([3.4, -0.5, 0])        # 右盘中心（转台上看）


def ground_pos(t):
    return np.array([V * t, 0.0, 0.0])


def table_pos(t):                     # 把地面坐标转到随台转动的坐标中
    x, y, _ = ground_pos(t)
    c, s = np.cos(-W * t), np.sin(-W * t)
    return np.array([c * x - s * y, s * x + c * y, 0.0])


class Lesson(Base):
    def construct(self):
        self.title("7.5", "地面上看与转台上看", "Seen from the ground and from the turntable")
        tt = ValueTracker(0.0)
        discs = VGroup(Circle(radius=2.4, color=GREY_B).move_to(CL), Circle(radius=2.4, color=GREY_B).move_to(CR))
        heads = VGroup(bi(["地面上看", "from the ground"], size=26).move_to(CL + UP * 2.95),
                       bi(["转台上看", "riding on the table"], size=26).move_to(CR + UP * 2.95))
        self.play(Create(discs), FadeIn(heads))

        def spokes(center, ang):
            return VGroup(*[Line(center, center + 2.4 * np.array([np.cos(ang + k * PI / 2), np.sin(ang + k * PI / 2), 0]),
                                 color=GREY_D, stroke_width=2) for k in range(4)])
        sl = always_redraw(lambda: spokes(CL, W * tt.get_value()))
        sr = spokes(CR, 0.0)
        arc = Arc(radius=2.65, start_angle=0.35, angle=0.8, color=BLUE).move_arc_center_to(CL).add_tip(tip_length=0.2)
        om = MathTex(r"\omega", color=BLUE, font_size=34).move_to(CL + np.array([2.2, 2.0, 0]))
        self.play(FadeIn(sl), FadeIn(sr), Create(arc), FadeIn(om))
        self.caption("转台逆时针转动；冰球几乎不受摩擦，从中心沿直线滑出", "The table turns anticlockwise; the nearly frictionless puck slides out of the centre in a straight line", wait=0.5)

        pl = always_redraw(lambda: Dot(CL + S * ground_pos(tt.get_value()), color=RED, radius=0.11))
        pr = always_redraw(lambda: Dot(CR + S * table_pos(tt.get_value()), color=RED, radius=0.11))
        trl = TracedPath(lambda: CL + S * ground_pos(tt.get_value()), stroke_color=RED, stroke_width=4)
        trr = TracedPath(lambda: CR + S * table_pos(tt.get_value()), stroke_color=RED, stroke_width=4)
        self.add(trl, trr, pl, pr)
        self.play(tt.animate.set_value(TEND), run_time=7, rate_func=linear)
        self.caption("同一个运动：地面上看是直线，转台上看向右弯", "One motion: a straight line from the ground, a curve to the right on the table", wait=1.5)

        p0 = CR + S * table_pos(0.35)
        v0 = (table_pos(0.36) - table_pos(0.34)) / 0.02
        v0 = v0 / np.linalg.norm(v0)
        right = np.array([v0[1], -v0[0], 0])
        a1 = vec(p0, p0 + 0.9 * v0, color=BLUE)
        a2 = vec(p0, p0 + 0.9 * right, color=ORANGE)
        t1 = MathTex(r"\boldsymbol v'", color=BLUE, font_size=32).next_to(p0 + 0.9 * v0, UP, buff=0.1)
        t2 = MathTex(r"-2m\,\boldsymbol\omega\times\boldsymbol v'", color=ORANGE, font_size=30).next_to(p0 + 0.9 * right, RIGHT, buff=0.1)
        self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(t1), FadeIn(t2))
        self.caption("转台上看：要解释这条弯曲的轨迹，需要一个垂直于速度的惯性力——科里奥利力", "On the table, the bend needs an inertial force perpendicular to the velocity: the Coriolis force", wait=2.5)
        self.card([["科里奥利力", "The Coriolis force"],
                   ["只在转动参考系中出现，没有施力物体", "Appears only in a rotating frame; nothing exerts it"],
                   ["垂直于相对速度，大小 2mωv′，不做功", "Perpendicular to the relative velocity, size 2mωv′, does no work"],
                   ["逆时针转动的参考系里，物体被推向运动方向的右侧", "In an anticlockwise frame, it pushes to the right of the motion"]])
