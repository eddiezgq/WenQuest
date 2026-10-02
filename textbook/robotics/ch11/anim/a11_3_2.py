"""动画 11.3.2（配图 11.3.2）：平面 2R 臂运动时，构型空间中的点同步移动。直线路径进入灰色的构型空间障碍物时，手臂正好撞上立柱；
跨过 ±180° 的最短路径绕开了它。尺寸同程序 11.3.1：大臂 0.425 m，小臂 0.392 m，立柱圆心 (0.45, 0.35) m、半径 0.10 m。"""
from manim import *
from wq_anim import *
import numpy as np

L1, L2 = 0.425, 0.392
OC, OR = np.array([0.45, 0.35]), 0.10
KW = 2.6                                   # 工作空间：1 m 画成 3.2 个单位
BASE = np.array([-3.4, 0.35, 0.0])
CS = 4.0                                   # 构型空间正方形边长
CC = np.array([3.4, 0.45, 0.0])            # 正方形中心
TA, TB = np.radians([150.0, -60.0]), np.radians([-120.0, 60.0])


def segd(p, a, b):
    ab = b - a
    t = np.clip(np.dot(p - a, ab) / np.dot(ab, ab), 0, 1)
    return np.linalg.norm(p - (a + t * ab))


def fk(q):
    e = L1 * np.array([np.cos(q[0]), np.sin(q[0])])
    w = e + L2 * np.array([np.cos(q[0] + q[1]), np.sin(q[0] + q[1])])
    return e, w


def hit(q):
    e, w = fk(q)
    return segd(OC, np.zeros(2), e) < OR or segd(OC, e, w) < OR


def W(p):
    return BASE + KW * np.array([p[0], p[1], 0.0])


def Cpt(q):
    qq = (np.asarray(q) + np.pi) % (2 * np.pi) - np.pi
    return CC + CS / (2 * np.pi) * np.array([qq[0], qq[1], 0.0])


def arm_at(q):
    e, w = fk(q)
    col = RED if hit(q) else BLUE
    return VGroup(Line(W((0, 0)), W(e), color=col, stroke_width=12), Line(W(e), W(w), color=col, stroke_width=9),
                  Dot(W((0, 0)), radius=0.1, color=WHITE), Dot(W(e), radius=0.09, color=WHITE))


class Lesson(Base):
    def construct(self):
        self.title("11.3", "手臂在动，构型空间中的点也在动", "The arm moves, and so does a point in C-space")
        obs = Circle(radius=KW * OR, color=GREY_B, fill_color=GREY_D, fill_opacity=1).move_to(W(OC))
        sq = Square(CS, color=GREY_B, stroke_width=2).move_to(CC)
        n = 48
        cells = VGroup()
        for i in range(n):
            for j in range(n):
                q = -np.pi + (np.array([i, j]) + 0.5) * 2 * np.pi / n
                if hit(q):
                    cells.add(Square(CS / n, stroke_width=0, fill_color=GREY_C, fill_opacity=0.9).move_to(Cpt(q)))
        lab = VGroup(MathTex(r"\theta_1", font_size=30).next_to(sq, DOWN, buff=0.12),
                     MathTex(r"\theta_2", font_size=30).next_to(sq, LEFT, buff=0.12),
                     MathTex(r"-180^\circ", font_size=22).next_to(sq.get_corner(DL), DOWN, buff=0.1),
                     MathTex(r"180^\circ", font_size=22).next_to(sq.get_corner(DR), DOWN, buff=0.1))
        q = [ValueTracker(TA[0]), ValueTracker(TA[1])]
        arm = always_redraw(lambda: arm_at([q[0].get_value(), q[1].get_value()]))
        dot = always_redraw(lambda: Dot(Cpt([q[0].get_value(), q[1].get_value()]), radius=0.09,
                                        color=RED if hit([q[0].get_value(), q[1].get_value()]) else YELLOW))
        goal = Dot(Cpt(TB), radius=0.08, color=GOLD)
        self.play(FadeIn(obs), Create(sq), FadeIn(cells), Write(lab), FadeIn(arm), FadeIn(dot), FadeIn(goal), run_time=1.2)
        self.caption("右边的正方形是构型空间，灰色是会撞上立柱的构型", "Right: the C-space; grey: configurations that hit the post", wait=1.0)
        self.caption("当作平面走：θ₁ 从 150° 减到 −120°，点进入灰区时手臂撞上立柱",
                     "As if flat: θ₁ from 150° down to −120°; entering the grey band, the arm hits the post", wait=0)
        trace1 = TracedPath(lambda: Cpt([q[0].get_value(), q[1].get_value()]), stroke_color=RED, stroke_width=3)
        self.add(trace1)
        self.play(q[0].animate.set_value(TA[0] - np.radians(140)), q[1].animate.set_value(TA[1] + np.radians(62.2)), run_time=3.0, rate_func=linear)
        self.wait(0.6)
        self.play(q[0].animate.set_value(TA[0]), q[1].animate.set_value(TA[1]), FadeOut(trace1), run_time=1.0)
        self.caption("在环面上走：θ₁ 正向转 90°，跨过 180°，点从右边消失、从左边出现",
                     "On the torus: θ₁ turns +90° across 180°; the point leaves on the right and comes back on the left", wait=0)
        self.play(q[0].animate.set_value(TA[0] + np.pi / 2), q[1].animate.set_value(TB[1]), run_time=4.0, rate_func=linear)
        cut = (np.pi - TA[0]) / (np.pi / 2)
        mid = TA + cut * np.array([np.pi / 2, TB[1] - TA[1]])
        p1 = Line(Cpt(TA), CC + CS / (2 * np.pi) * np.array([np.pi, mid[1], 0]), color=GREEN, stroke_width=4)
        p2 = Line(CC + CS / (2 * np.pi) * np.array([-np.pi, mid[1], 0]), Cpt(TB), color=GREEN, stroke_width=4)
        self.play(Create(p1), Create(p2), run_time=0.8)
        self.caption("构型空间中，机器人缩成一个点，障碍物变成禁区：规划就是给点找路",
                     "In C-space the robot is a point and obstacles are forbidden regions: planning is finding a path for a point", wait=2.0)
