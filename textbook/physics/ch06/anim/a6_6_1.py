"""动画 6.6.1（配图 6.6.1）：隔离法。把 AGV 牵引的两辆料车逐个“剥”出来，画出每个隔离体受的水平力。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("6.6", "隔离法：一次只看一个物体", "Isolation: one body at a time")
        y = 0.6
        fl = ground(y=y, x0=-6.8, x1=6.8)

        def wagon(name):
            body = RoundedRectangle(width=1.7, height=0.5, corner_radius=0.05, color=GREY_B, fill_color=GREY_D, fill_opacity=1)
            w = VGroup(*[Circle(0.12, color=GREY_B, stroke_width=2) for _ in range(2)]).arrange(RIGHT, buff=1.1).next_to(body, DOWN, buff=0)
            return VGroup(body, w, zh(name, 22, INK).move_to(body))

        c2, c1 = wagon("2"), wagon("1")
        A = agv(width=2.2, height=0.6, label="AGV")
        train = VGroup(c2, c1, A).arrange(RIGHT, buff=0.25).move_to(np.array([-0.5, y, 0]), aligned_edge=DOWN)
        hooks = VGroup(Line(c2.get_right() + DOWN * 0.05, c1.get_left() + DOWN * 0.05, color=INK, stroke_width=5),
                       Line(c1.get_right() + DOWN * 0.05, A.get_left() + DOWN * 0.1, color=INK, stroke_width=5))
        acc = vec(np.array([4.6, y + 1.3, 0]), np.array([5.8, y + 1.3, 0]), C_A, r"\boldsymbol a", RIGHT)
        self.play(Create(fl), FadeIn(train), Create(hooks), GrowArrow(acc[0]), Write(acc[1]))
        self.caption("AGV 牵引两辆料车，一起以加速度 a 起步", "An AGV tows two carts; all speed up with acceleration a")
        yb = -1.7
        targets = [np.array([-5.3, yb, 0]), np.array([-1.3, yb, 0]), np.array([3.9, yb, 0])]
        cols = [GREEN, BLUE]
        # 第二辆车
        self.play(c2.copy().animate.move_to(targets[0]), run_time=1.0)
        e = targets[0] + RIGHT * 0.85
        t2 = vec(e, e + RIGHT * 0.7, cols[0], r"F_{\mathrm T2}", UP, 30)
        self.play(GrowArrow(t2[0]), Write(t2[1]))
        self.caption("隔离第二辆车：水平方向只有挂钩 2 向前拉它", "Cart 2 alone: only coupler 2 pulls it forward")
        # 第一辆车
        self.play(c1.copy().animate.move_to(targets[1]), run_time=1.0)
        l, r = targets[1] + LEFT * 0.85, targets[1] + RIGHT * 0.85
        t2b = vec(l, l + LEFT * 0.7, cols[0], r"F_{\mathrm T2}", UP, 30)
        t1 = vec(r, r + RIGHT * 1.2, cols[1], r"F_{\mathrm T1}", UP, 30)
        self.play(GrowArrow(t2b[0]), Write(t2b[1]), GrowArrow(t1[0]), Write(t1[1]))
        self.caption("第一辆车：前面被挂钩 1 拉，后面被挂钩 2 往回拉", "Cart 1: pulled ahead by coupler 1, held back by coupler 2")
        # AGV
        self.play(A.copy().animate.move_to(targets[2]), run_time=1.0)
        l = targets[2] + LEFT * 1.1
        t1b = vec(l, l + LEFT * 1.2, cols[1], r"F_{\mathrm T1}", UP, 30)
        F = vec(targets[2] + DOWN * 0.6, targets[2] + DOWN * 0.6 + RIGHT * 2.0, C_F, r"F_\mathrm d", RIGHT, 30)
        self.play(GrowArrow(t1b[0]), Write(t1b[1]), GrowArrow(F[0]), Write(F[1]))
        self.caption("AGV：地面给的驱动力向前，挂钩 1 向后拉", "AGV: the floor drives it forward; coupler 1 holds it back")
        eqs = VGroup(MathTex(r"F_{\mathrm T2}=m_2a", font_size=32), MathTex(r"F_{\mathrm T1}-F_{\mathrm T2}=m_1a", font_size=32),
                     MathTex(r"F_\mathrm d-F_{\mathrm T1}=m_0a", font_size=32)).arrange(RIGHT, buff=0.9).to_edge(DOWN, buff=1.3)
        self.play(Write(eqs))
        self.caption("每个隔离体各写一个方程，三个方程三个未知数", "One equation per body: three equations, three unknowns")
        self.wait(1)
        self.card([["隔离法", "Isolation method"],
                   MathTex(r"a=\frac{F_\mathrm d}{m_0+m_1+m_2},\quad F_{\mathrm T1}=(m_1+m_2)a,\quad F_{\mathrm T2}=m_2a", font_size=38),
                   ["相加，内力两两抵消，得到整体法", "Add them: internal forces cancel in pairs, giving the whole-system equation"]])
