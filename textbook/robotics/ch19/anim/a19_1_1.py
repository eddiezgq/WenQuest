"""动画 19.1.1（配图 19.1.2）：车轮的轴线与瞬心。
差速 AGV（轮距 0.26 m）的两轮转速比由相同变到相反，瞬心沿轴线从无穷远移到车体中心；
四轮车（轴距 1.2 m、轮距 0.8 m）按阿克曼条件转向，四条轴线交于一点；改为两前轮平行转向，轴线交不到一起。"""
from manim import *
from wq_anim import *
import numpy as np
import math

B_W = 0.26


def wheel_rect(c, ang, L=0.5, W=0.16, color=GREY_B):
    r = Rectangle(width=L, height=W, color=color, fill_color=GREY_D, fill_opacity=1, stroke_width=2)
    return r.rotate(ang).move_to(c)


def diff_car(scale, origin):
    body = Rectangle(width=0.32 * scale, height=0.22 * scale, color=STEEL, fill_color=NAVY, fill_opacity=1, stroke_width=3)
    wl = wheel_rect(UP * 0.13 * scale, 0, 0.1 * scale, 0.035 * scale)
    wr = wheel_rect(DOWN * 0.13 * scale, 0, 0.1 * scale, 0.035 * scale)
    caster = Circle(radius=0.02 * scale, color=GREY_B, fill_opacity=1).move_to(LEFT * 0.13 * scale)
    return VGroup(body, wl, wr, caster).shift(origin)


class Lesson(Base):
    def construct(self):
        self.title("19.1", "车轮的轴线与瞬心", "Wheel axles and the instantaneous centre")
        # ---------- 差速 AGV
        S = 6.0
        O = np.array([-3.2, -1.6, 0])
        car = diff_car(S, O)
        axle = DashedLine(O + DOWN * 1.0, O + UP * 4.2, color=RED, dash_length=0.12)
        self.play(FadeIn(car), Create(axle), run_time=1.0)
        self.caption("差速 AGV：两轮共轴，瞬心只能在这条轴线上", "Differential AGV: both wheels on one axle; the ICR must lie on it", wait=0.8)
        k = ValueTracker(0.95)                 # ω_L / ω_R

        def R_of():
            q = k.get_value()
            return B_W / 2 * (1 + q) / (1 - q)   # 式 (19.2.4)，右轮转速为 1

        def icr_dot():
            R = R_of()
            y = min(R * S, 4.0)
            return Dot(O + UP * y, radius=0.1, color=YELLOW)

        def arrows():
            q = k.get_value()
            g = VGroup()
            for y, sp in ((-0.13, 1.0), (0.13, q)):
                p = O + UP * y * S
                g.add(Arrow(p, p + RIGHT * 1.4 * sp, buff=0, color=GREEN, stroke_width=5, max_tip_length_to_length_ratio=0.3))
            return g

        dot = always_redraw(icr_dot)
        arr = always_redraw(arrows)
        lab = always_redraw(lambda: MathTex(r"R = \frac{b}{2}\,\frac{\omega_R + \omega_L}{\omega_R - \omega_L} = %.2f\ \mathrm{m}" % R_of(),
                                            font_size=34).move_to([2.6, 1.6, 0]))
        ratio = always_redraw(lambda: MathTex(r"\omega_L/\omega_R = %.2f" % k.get_value(), font_size=34, color=GREEN).move_to([2.6, 0.6, 0]))
        self.add(dot, arr, lab, ratio)
        self.caption("两轮转速越接近，瞬心越远；左轮反转时，瞬心移进两轮之间",
                     "The closer the wheel speeds, the farther the ICR; with the left wheel reversed it moves between the wheels", wait=0)
        self.play(k.animate.set_value(-1.0), run_time=4.5, rate_func=smooth)
        self.caption("两轮等速反转：瞬心在车体中心，原地转", "Equal and opposite speeds: the ICR is the centre; the AGV spins on the spot", wait=1.0)
        self.play(FadeOut(VGroup(car, axle, dot, arr, lab, ratio)), run_time=0.6)
        # ---------- 四轮车：阿克曼与平行转向
        L, W = 1.2, 0.8
        s2 = 1.6
        O2 = np.array([-1.4, -1.35, 0])
        P = lambda x, y: O2 + s2 * np.array([x, y, 0])
        body = Rectangle(width=1.8 * s2, height=1.0 * s2, color=STEEL, fill_color=NAVY, fill_opacity=0.6, stroke_width=3).move_to(P(L / 2, 0))
        rear = VGroup(wheel_rect(P(0, W / 2), 0, 0.32 * s2, 0.12 * s2), wheel_rect(P(0, -W / 2), 0, 0.32 * s2, 0.12 * s2))
        d = ValueTracker(0.0)
        par = ValueTracker(0.0)               # 0：阿克曼；1：平行

        def angles():
            di = d.get_value()
            if di < 1e-4:
                return 0.0, 0.0
            do = math.atan(1 / (1 / math.tan(di) + W / L))
            return di, (1 - par.get_value()) * do + par.get_value() * di

        def front():
            di, do = angles()
            return VGroup(wheel_rect(P(L, W / 2), di, 0.32 * s2, 0.12 * s2, YELLOW), wheel_rect(P(L, -W / 2), do, 0.32 * s2, 0.12 * s2, YELLOW))

        def lines():
            di, do = angles()
            g = VGroup(DashedLine(P(0, -0.7), P(0, 2.45), color=RED, dash_length=0.1))
            for (x, y), a in (((L, W / 2), di), ((L, -W / 2), do)):
                n = np.array([-math.sin(a), math.cos(a)])
                t = (2.45 - y) / n[1]
                g.add(DashedLine(P(x, y), P(x + t * n[0], y + t * n[1]), color=RED, dash_length=0.1))
            return g

        def icr():
            di, do = angles()
            if di < 1e-4:
                return VGroup()
            R = L / math.tan(di) + W / 2
            if R > 2.4 or par.get_value() > 0.3:
                return VGroup()
            return Dot(P(0, R), radius=0.1, color=YELLOW)

        fw = always_redraw(front)
        ln = always_redraw(lines)
        ic = always_redraw(icr)
        self.play(FadeIn(body), FadeIn(rear), run_time=0.6)
        self.add(ln, fw, ic)
        eq = MathTex(r"\cot\delta_o - \cot\delta_i = \frac{w}{L}", font_size=40).move_to([4.1, 1.5, 0])
        self.play(Write(eq), run_time=0.8)
        self.caption("阿克曼转向：内侧前轮转得多、外侧转得少，四条轴线交于一点",
                     "Ackermann steering: the inner wheel turns more, and all four axles meet at one point", wait=0)
        self.play(d.animate.set_value(math.radians(34)), run_time=3.5, rate_func=smooth)
        self.wait(0.6)
        warn = fit(bi(["平行转向：轴线交不到一起，车轮被迫侧滑", "Parallel steering: the axles miss; a wheel must slide"], 24, RED), 5.4).move_to([4.2, 0.3, 0])
        self.caption("两前轮平行转向时，前轮轴线互相平行，与后轴线交于两点",
                     "With parallel steering the front axles are parallel and cut the rear axle line at two points", wait=0)
        self.play(par.animate.set_value(1.0), FadeIn(warn), run_time=2.5)
        self.wait(1.2)
        self.card([["瞬心定理", "The ICR theorem"],
                   ["所有标准轮都不侧滑，当且仅当它们的轴线交于一点", "No standard wheel slides if and only if all their axles meet at one point"],
                   MathTex(r"\delta_m = 3 - \mathrm{rank}\,C(\beta)", font_size=44)])
