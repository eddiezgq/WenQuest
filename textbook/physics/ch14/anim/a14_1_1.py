"""动画 14.1.1（配图 14.1.1）：支点移动，力矩平衡怎样变化。长 1.00 m、1.0 kg 的均匀杆，左端挂 6.0 kg，右端挂 2.0 kg（与算例 14.1.1 一致）。
支点从中点慢慢向左移，显示各力对支点的力矩和合力矩；合力矩不为零时杆向一边倾斜（画面上的倾角只表示方向，不按比例），
支点到达 x = 0.278 m（整体重心的正下方）时合力矩为零，杆水平平衡。"""
from manim import *
from wq_anim import *
import numpy as np

G, LB, MB, ML, MR = 9.81, 1.00, 1.0, 6.0, 2.0
X0 = (MB * LB / 2 + MR * LB) / (ML + MB + MR)
S = 7.0                                                          # 画面单位 / m
Y = 0.3


def mnet(x):
    return G * (ML * x - MB * (LB / 2 - x) - MR * (LB - x))       # 正：左端下沉


class Lesson(Base):
    def construct(self):
        self.title("14.1", "支点移动，力矩平衡怎样变化", "Moving the fulcrum")
        xf = ValueTracker(0.5)

        def scene_():
            x = xf.get_value(); M = mnet(x)
            tilt = np.clip(M / 40.0, -1, 1) * 0.18                       # 倾角只示意方向
            piv = np.array([(x - 0.5) * S, Y, 0])
            u = np.array([np.cos(tilt), np.sin(tilt), 0])
            left = piv - u * x * S; right = piv + u * (LB - x) * S
            beam = Line(left, right, color=GREY_B, stroke_width=8)
            tri = Triangle(color=WHITE, fill_opacity=0.6).scale(0.25).move_to(piv + DOWN * 0.28)
            wl = Square(0.75, color=RED, fill_opacity=0.6).move_to(left + DOWN * 0.75)
            wr = Square(0.45, color=BLUE, fill_opacity=0.6).move_to(right + DOWN * 0.6)
            ropes = VGroup(Line(left, wl.get_top(), color=GREY_B), Line(right, wr.get_top(), color=GREY_B))
            lab = VGroup(MathTex(r"6.0\ \mathrm{kg}", font_size=26).move_to(wl), MathTex(r"2.0\ \mathrm{kg}", font_size=24).next_to(wr, DOWN, buff=0.1))
            return VGroup(beam, tri, ropes, wl, wr, lab)

        self.add(always_redraw(scene_))

        def panel():
            x = xf.get_value()
            rows = [rf"x = {x:.3f}\ \mathrm m",
                    rf"M_{{6\,\mathrm{{kg}}}} = {G * ML * x:.1f}\ \mathrm{{N\cdot m}}",
                    rf"M_{{\mathrm{{rod}}}} + M_{{2\,\mathrm{{kg}}}} = -{G * (MB * (LB / 2 - x) + MR * (LB - x)):.1f}\ \mathrm{{N\cdot m}}",
                    rf"\sum M = {mnet(x):+.1f}\ \mathrm{{N\cdot m}}"]
            g_ = VGroup(*[MathTex(r, font_size=30) for r in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
            g_[3].set_color(YELLOW if abs(mnet(x)) < 0.05 else WHITE)
            return g_.to_corner(UR, buff=0.6).shift(DOWN * 0.6)

        self.add(always_redraw(panel))
        self.caption("支点在中点：左边 6 kg 的力矩大，左端下沉", "Fulcrum at the middle: the 6 kg side wins and the left end drops", wait=1.5)
        self.caption("支点向左移：左边的力臂变短，右边的变长", "Move the fulcrum left: the left lever arm shrinks, the right one grows", wait=0)
        self.play(xf.animate.set_value(X0), run_time=5, rate_func=smooth)
        self.caption("支点在整体重心的正下方时，合力矩为零，杆平衡", "With the fulcrum right under the overall centre of gravity, the net torque is zero", wait=1.5)
        self.play(xf.animate.set_value(0.15), run_time=2.5, rate_func=smooth)
        self.caption("再往左，右端反而下沉", "Further left, the right end drops instead", wait=1.0)
        self.play(xf.animate.set_value(X0), run_time=2.0, rate_func=smooth)
        self.card([["力矩平衡", "Balance of torques"],
                   MathTex(r"\sum \vec F = 0,\qquad \sum M = 0", font_size=46),
                   ["对任何一点取矩，合力矩都为零", "the net torque vanishes about every point"],
                   ["支点在整体重心正下方，杆才平衡", "the beam balances with the fulcrum under the overall CG"]])
