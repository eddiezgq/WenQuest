"""动画 23.3.1（配图 23.3.2）：陀螺仪的进动（算例 23.3.3，示意值）。均匀圆盘 1.0 kg、半径 0.15 m，盘心离支点 l = 0.20 m，轴水平。
自转 60 rad/s 时进动角速度 Ω = m𝔤l/(I₃ω) = 2.907 rad/s；自转减半为 30 rad/s，Ω = 5.813 rad/s，加倍；不自转时轴绕支点倒下
（(I_t + m l²) φ̈ = −m𝔤 l cos φ，I_t = m r²/4，RK4 积分）。进动放慢一半播放；盘上的标记只表示在自转，转速不按比例。
L 沿轴向外，重力矩 M = l x̂ × (−m𝔤 ẑ) 水平、垂直于轴，L 的端点沿 M 的方向移动，所以轴在水平面内绕竖直线转。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G, M_, R_, L_ = 9.81, 1.0, 0.15, 0.20
I3 = 0.5 * M_ * R_ ** 2
IT = 0.25 * M_ * R_ ** 2
O = np.array([-1.6, 0.2, 0.0])
S = 9.0                                         # 1 m 画成 9 个单位


def P(p):
    return proj3(p, O, S)


def wheel(psi, phi, spin, col):
    """轴的方位角 psi（水平面内）、仰角 phi；spin：盘上标记的转角。"""
    a = np.array([math.cos(phi) * math.cos(psi), math.cos(phi) * math.sin(psi), math.sin(phi)])
    e1 = np.cross(a, [0, 0, 1.0])
    if np.linalg.norm(e1) < 1e-6:
        e1 = np.array([1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(a, e1)
    c = L_ * a
    pts = [P(c + R_ * (math.cos(t) * e1 + math.sin(t) * e2)) for t in np.linspace(0, 2 * math.pi, 48)]
    g = VGroup(Line(P([0, 0, 0]), P((L_ + 0.06) * a), color=GREY_A, stroke_width=6))
    g.add(Polygon(*pts, color=col, stroke_width=2, fill_color=col, fill_opacity=0.25))
    for k in range(3):
        t = spin + 2 * math.pi * k / 3
        g.add(Line(P(c), P(c + R_ * (math.cos(t) * e1 + math.sin(t) * e2)), color=col, stroke_width=2))
    return g, a


class Lesson(Base):
    def construct(self):
        self.title("23.3", "陀螺仪的进动", "Precession of a gyroscope")
        post = Line(P([0, 0, -0.24]), P([0, 0, 0]), color=GREY_B, stroke_width=10)
        base = Line(P([-0.08, 0, -0.24]), P([0.08, 0, -0.24]), color=GREY_B, stroke_width=10)
        self.add(post, base, Dot(P([0, 0, 0]), color=WHITE, radius=0.07))
        psi = ValueTracker(0.0)
        phi = ValueTracker(0.0)
        spin = ValueTracker(0.0)
        show_arrows = ValueTracker(1.0)
        trail = VMobject(color=BLUE_B, stroke_width=2)
        trail.set_points_as_corners([P([L_ + 0.06, 0, 0]), P([L_ + 0.06, 0, 0])])
        self.add(trail)

        def scene():
            g, a = wheel(psi.get_value(), phi.get_value(), spin.get_value(), STEEL)
            out = VGroup(g)
            if show_arrows.get_value() > 0.5:
                out.add(Arrow(P(L_ * a), P(L_ * a + 0.16 * a), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.25))
                out.add(MathTex(r"\boldsymbol L", color=RED, font_size=34).move_to(P(L_ * a + 0.2 * a)))
            m = np.cross(a, [0, 0, -1.0])
            if np.linalg.norm(m) > 1e-6:
                m = m / np.linalg.norm(m)
                out.add(Arrow(P([0, 0, 0]), P(0.14 * m), buff=0, color=ORANGE, stroke_width=6, max_tip_length_to_length_ratio=0.3))
                out.add(MathTex(r"\boldsymbol M", color=ORANGE, font_size=32).move_to(P(0.18 * m)))
            out.add(Arrow(P(L_ * a), P(L_ * a + np.array([0, 0, -0.1])), buff=0, color=GREY_B, stroke_width=4, max_tip_length_to_length_ratio=0.3))
            return out

        self.add(always_redraw(scene))
        info = VGroup(MathTex(r"\Omega = \frac{m\mathfrak g\,l}{I_3\,\omega}", font_size=42, color=WHITE)).move_to([4.2, 1.9, 0])
        self.play(FadeIn(info), run_time=0.6)

        def readout(w, Om):
            return VGroup(Text(f"自转 ω = {w:.0f} rad/s", font=CJK, font_size=26, color=STEEL),
                          Text(f"进动 Ω = {Om:.3f} rad/s", font=CJK, font_size=26, color=YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([4.2, 0.6, 0])

        r1 = readout(60, M_ * G * L_ / (I3 * 60))
        self.play(FadeIn(r1), run_time=0.5)
        self.caption("圆盘自转、轴水平。重力矩 M 水平且垂直于轴：轴不倒下，而是在水平面内绕竖直线转",
                     "The disc spins with its axle level. The gravity moment M is horizontal and normal to the axle: it does not fall, it precesses", wait=0)
        Om1 = M_ * G * L_ / (I3 * 60)
        T1 = 2 * math.pi / Om1
        trail.add_updater(lambda m: m.add_points_as_corners([P((L_ + 0.06) * np.array([math.cos(psi.get_value()), math.sin(psi.get_value()), 0]))]))
        self.play(psi.animate.set_value(2 * math.pi), spin.animate.set_value(40.0), run_time=2 * T1, rate_func=linear)
        self.caption("L 的端点沿 M 的方向移动：dL/dt = M。转得越快，L 越大，进动越慢",
                     "The tip of L moves along M: dL/dt = M. The faster the spin, the larger L and the slower the precession", wait=0)
        self.play(psi.animate.set_value(3 * math.pi), spin.animate.set_value(60.0), run_time=T1, rate_func=linear)
        trail.clear_updaters()
        self.play(FadeOut(r1), run_time=0.3)
        r2 = readout(30, M_ * G * L_ / (I3 * 30))
        self.play(FadeIn(r2), run_time=0.3)
        Om2 = M_ * G * L_ / (I3 * 30)
        self.caption("自转减半：进动加快一倍", "Halve the spin: the precession doubles", wait=0)
        self.play(psi.animate.set_value(3 * math.pi + 4 * math.pi), spin.animate.set_value(80.0), run_time=2 * 4 * math.pi / Om2, rate_func=linear)
        self.play(FadeOut(r2), FadeOut(trail), run_time=0.3)
        # 不自转：绕支点倒下
        dt = 0.002
        ph, om, phs = 0.0, 0.0, [0.0]
        while ph > -math.radians(80):
            acc = -M_ * G * L_ * math.cos(ph) / (IT + M_ * L_ * L_)
            om += acc * dt
            ph += om * dt
            phs.append(ph)
        t_fall = dt * len(phs)
        show_arrows.set_value(0.0)
        self.caption("圆盘不转：L ≈ 0，重力矩直接让轴倒下", "No spin: L ≈ 0, and the gravity moment simply tips the axle over", wait=0)
        tracker = ValueTracker(0.0)
        phi.add_updater(lambda m: m.set_value(float(np.interp(tracker.get_value(), np.arange(len(phs)) * dt, phs))))
        self.add(phi)
        self.play(tracker.animate.set_value(t_fall), run_time=max(1.5, t_fall * 3), rate_func=linear)
        phi.clear_updaters()
        self.wait(0.5)
        self.card([["陀螺仪：重力矩使角动量的方向转动", "A gyroscope: the gravity moment turns the angular momentum"],
                   MathTex(r"\boldsymbol M = \boldsymbol\Omega\times\boldsymbol L,\qquad \Omega = \frac{m\mathfrak g\,l}{I_3\,\omega}", font_size=44),
                   ["例：1 kg、半径 0.15 m 的圆盘，l = 0.2 m，自转 60 rad/s：Ω ≈ 2.9 rad/s", "Example: 1 kg disc, radius 0.15 m, l = 0.2 m, spin 60 rad/s: Ω ≈ 2.9 rad/s"]])
