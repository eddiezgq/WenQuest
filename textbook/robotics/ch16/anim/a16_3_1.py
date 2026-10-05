"""动画 16.3.1（配图 16.3.1）：平面 2R 臂（0.425、0.392 m）的末端沿 30° 方向的射线以 0.1 m/s 向外伸，
手臂逐渐伸直（θ₂ → 0）。末端画出可操作度椭圆（单位关节速度所能产生的末端速度），右侧显示两个关节所需的转速：
椭圆在径向越来越扁，所需转速按 1/sin θ₂ 增大，θ₂ = 2° 时两个关节分别约需 390°/s 和 800°/s（图 16.3.1(b)）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
S = 6.0
BASE = np.array([-5.6, -2.3, 0.0])
PHI = math.radians(30)


def ik(r):
    c2 = (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    t2 = math.acos(max(-1.0, min(1.0, c2)))
    t1 = PHI - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    return t1, t2


def jac(t1, t2):
    return np.array([[-L1 * math.sin(t1) - L2 * math.sin(t1 + t2), -L2 * math.sin(t1 + t2)],
                     [L1 * math.cos(t1) + L2 * math.cos(t1 + t2), L2 * math.cos(t1 + t2)]])


def scr(p):
    return BASE + S * np.array([p[0], p[1], 0.0])


class Lesson(Base):
    def construct(self):
        self.title("16.3", "奇异：手臂伸直时径向动不了", "Singularity: a straight arm cannot move radially")
        r = ValueTracker(0.55)
        ray = DashedLine(scr([0, 0]), scr([0.86 * math.cos(PHI), 0.86 * math.sin(PHI)]), color=GREY_C, stroke_width=2)
        circ = Arc(radius=S * (L1 + L2), start_angle=0.15, angle=0.55, arc_center=BASE, color=GREY_D, stroke_width=2)
        self.play(Create(ray), Create(circ), run_time=0.8)

        def arm():
            t1, t2 = ik(r.get_value())
            a = np.array([L1 * math.cos(t1), L1 * math.sin(t1)])
            b = a + L2 * np.array([math.cos(t1 + t2), math.sin(t1 + t2)])
            g = VGroup(Polygon(BASE + LEFT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.2, BASE + LEFT * 0.2,
                               color=GREY_B, fill_color=GREY_E, fill_opacity=1),
                       Line(scr([0, 0]), scr(a), color=STEEL, stroke_width=14), Line(scr(a), scr(b), color=STEEL, stroke_width=10),
                       Dot(scr([0, 0]), radius=0.11, color=WHITE), Dot(scr(a), radius=0.1, color=WHITE), Dot(scr(b), radius=0.07, color=YELLOW))
            J = jac(t1, t2)
            w, V = np.linalg.eigh(J @ J.T)
            ax1 = max(math.sqrt(max(w[1], 0)), 1e-4) * 2.2
            ax2 = max(math.sqrt(max(w[0], 0)), 1e-4) * 2.2
            ang = math.atan2(V[1, 1], V[0, 1])
            e = Ellipse(width=2 * ax1, height=2 * ax2, color=ORANGE, stroke_width=4).rotate(ang).move_to(scr(b))
            g.add(e)
            return g

        rig = always_redraw(arm)
        self.play(FadeIn(rig), run_time=0.8)
        self.caption("橙色椭圆：单位关节速度能产生的末端速度。末端沿虚线以 0.1 m/s 向外伸",
                     "Orange ellipse: tip velocities from unit joint speeds. The tip moves out along the dashed ray at 0.1 m/s", wait=1.0)

        def bars():
            t1, t2 = ik(r.get_value())
            J = jac(t1, t2)
            v = 0.1 * np.array([math.cos(PHI), math.sin(PHI)])
            qd = np.degrees(np.linalg.solve(J, v))
            g = VGroup()
            x0, y0 = 2.2, -2.2
            g.add(Line([x0 - 0.2, y0, 0], [x0 + 3.6, y0, 0], color=GREY_B, stroke_width=2))
            for k, (val, col, nm) in enumerate(((qd[0], BLUE, r"\dot\theta_1"), (qd[1], GREEN, r"\dot\theta_2"))):
                hgt = min(3.9, 3.9 * math.log10(1 + abs(val)) / 3.2)
                x = x0 + 0.5 + 1.6 * k
                g.add(Rectangle(width=0.8, height=max(hgt, 0.02), color=col, fill_color=col, fill_opacity=0.8).move_to([x, y0 + hgt / 2, 0]))
                g.add(MathTex(nm, font_size=30, color=col).next_to([x, y0, 0], DOWN, buff=0.15))
                g.add(MathTex(r"%.0f^\circ/\mathrm{s}" % abs(val), font_size=28).next_to([x, y0 + hgt, 0], UP, buff=0.1))
            g.add(MathTex(r"\theta_2 = %.1f^\circ" % math.degrees(t2), font_size=34, color=YELLOW).move_to([-1.2, 2.2, 0]))
            return g

        bs = always_redraw(bars)
        self.play(FadeIn(bs), run_time=0.6)
        self.caption("越接近伸直，椭圆在径向越扁，所需的关节转速越大",
                     "The closer to straight, the flatter the ellipse radially, and the faster the joints must turn", wait=0.2)
        self.play(r.animate.set_value(0.80), run_time=5.0, rate_func=linear)
        self.play(r.animate.set_value(0.81688), run_time=4.0, rate_func=rate_functions.ease_out_sine)
        self.caption("θ₂ = 2°：径向 0.1 m/s 要两个关节约 390°/s 和 800°/s；伸直时根本无法产生——这就是奇异",
                     "At θ₂ = 2°, 0.1 m/s radially needs about 390°/s and 800°/s; straight, it cannot be produced at all: a singularity", wait=2.0)
        self.card([["平面 2R 臂的奇异", "Singularity of the planar 2R arm"],
                   MathTex(r"\det J = L_1L_2\sin\theta_2 = \sigma_1\sigma_2", font_size=40),
                   MathTex(r"\|\dot\theta\| \ge \frac{\|v\|}{\sigma_{\min}} \to \infty", font_size=40),
                   ["奇异处失去一个运动方向，附近需要极大的关节速度", "A direction of motion is lost at the singularity; near it, huge joint speeds are needed"]])
