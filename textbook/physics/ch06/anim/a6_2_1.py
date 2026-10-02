"""动画 6.2.1（配图 6.2.1）：伽利略的双斜面理想实验。第二个斜面越平，小球滚得越远；放平了，就永远滚下去。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("6.2", "伽利略的双斜面", "Galileo's two inclines")
        H = 2.0
        y0 = -1.6
        start = np.array([-5.5, y0 + H, 0])
        bottom = np.array([-2.5, y0, 0])
        left = Line(start, bottom, color=INK, stroke_width=4)
        floor = Line(bottom, np.array([6.8, y0, 0]), color=INK, stroke_width=4)
        level = DashedLine(start + LEFT * 0.4, np.array([6.5, y0 + H, 0]), color=MUTED, dash_length=0.12)
        self.play(Create(left), Create(floor), Create(level))
        self.caption("小球从左边的斜面某一高度由静止滚下", "A ball rolls down from rest at some height")

        def run(slope, color, run_time):
            L = H / slope
            end = bottom + np.array([L, H, 0])
            ramp = Line(bottom, end, color=color, stroke_width=4)
            ball = Dot(start + UP * 0.12, radius=0.12, color=YELLOW)
            self.play(Create(ramp), FadeIn(ball), run_time=0.6)
            # 下坡由静止匀加速（路程 ∝ t²），上坡匀减速到静止（路程 ∝ 1 − (1 − t)²）；所用时间与坡长成正比
            down = Line(start + UP * 0.12, bottom + UP * 0.12)
            up = Line(bottom + UP * 0.12, end + UP * 0.12)
            self.play(MoveAlongPath(ball, down), rate_func=lambda t: t * t, run_time=1.2)
            self.play(MoveAlongPath(ball, up), rate_func=lambda t: 1 - (1 - t) ** 2, run_time=1.2 * up.get_length() / down.get_length())
            mark = Dot(end, radius=0.08, color=color)
            self.play(FadeIn(mark), FadeOut(ball), run_time=0.4)
            return VGroup(ramp, mark)

        a = run(1.0, BLUE, 0)
        self.caption("在右边的斜面上，它几乎回到同一高度", "On the right incline it climbs back to nearly the same height")
        b = run(0.5, GREEN, 0)
        self.caption("右边的斜面越平，小球为了回到同一高度，就要滚得越远", "The flatter the incline, the farther it rolls to regain the height")
        c = run(0.25, ORANGE, 0)
        ball = Dot(start + UP * 0.12, radius=0.12, color=YELLOW)
        self.play(FadeIn(ball), run_time=0.4)
        self.caption("如果右边放平，它永远到不了原来的高度——就永远滚下去", "If the right side is level it never regains the height: it rolls on forever", wait=0)
        down = Line(start + UP * 0.12, bottom + UP * 0.12)
        flat = Line(bottom + UP * 0.12, np.array([6.6, y0 + 0.12, 0]))
        self.play(MoveAlongPath(ball, down), rate_func=lambda t: t * t, run_time=1.2)
        # 水平面上匀速：速度等于坡底的速度 2L/1.2
        self.play(MoveAlongPath(ball, flat), rate_func=lambda t: t, run_time=flat.get_length() / (2 * down.get_length() / 1.2))
        arrow = Arrow(np.array([4.5, y0 + 0.7, 0]), np.array([6.5, y0 + 0.7, 0]), buff=0, color=C_V)
        self.play(GrowArrow(arrow), Write(MathTex(r"v=\text{const}", color=C_V, font_size=34).next_to(arrow, UP, buff=0.1)))
        self.wait(1)
        self.card([["惯性：不受外力，运动状态不变", "Inertia: without a net force, motion does not change"],
                   ["伽利略，1632 年《关于两大世界体系的对话》", "Galileo, Dialogue Concerning the Two Chief World Systems, 1632"]])
