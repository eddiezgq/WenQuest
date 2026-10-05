"""动画 16.5.1（配图 16.5.1）：平面 2R 臂（0.425、0.392 m，θ₁ = 30°）的肘角 θ₂ 从 120° 减到 18°，手臂逐渐伸直。
末端同时画出速度椭圆（橙，单位关节速度能产生的末端速度）和力椭圆（红虚线，单位关节力矩能平衡的末端力）：
两者主轴相同、半轴互为倒数。伸直时速度椭圆在径向被压扁，力椭圆在径向被拉长：动不了的方向，正是最能扛力的方向。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
S = 6.0
BASE = np.array([-5.6, -2.4, 0.0])
T1 = math.radians(30)
KV, KF = 0.3, 0.02


def jac(t2):
    a, b = T1, T1 + t2
    return np.array([[-L1 * math.sin(a) - L2 * math.sin(b), -L2 * math.sin(b)], [L1 * math.cos(a) + L2 * math.cos(b), L2 * math.cos(b)]])


def scr(p):
    return BASE + S * np.array([p[0], p[1], 0.0])


def ell(J, inv, k, color, dashed):
    U, s, _ = np.linalg.svd(J)
    ax = (1 / s if inv else s) * k * S
    ang = math.atan2(U[1, 0], U[0, 0])
    e = Ellipse(width=2 * max(ax[0], 1e-3), height=2 * max(ax[1], 1e-3), color=color, stroke_width=4)
    if dashed:
        e = DashedVMobject(e, num_dashes=60)
    return e.rotate(ang)


class Lesson(Base):
    def construct(self):
        self.title("16.5", "运动与静力的对偶", "Kinetostatic duality")
        t2 = ValueTracker(math.radians(120))

        def rig():
            a, b = T1, T1 + t2.get_value()
            e = np.array([L1 * math.cos(a), L1 * math.sin(a)])
            p = e + L2 * np.array([math.cos(b), math.sin(b)])
            J = jac(t2.get_value())
            g = VGroup(Polygon(BASE + LEFT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.2, BASE + LEFT * 0.2,
                               color=GREY_B, fill_color=GREY_E, fill_opacity=1),
                       Line(scr([0, 0]), scr(e), color=STEEL, stroke_width=14), Line(scr(e), scr(p), color=STEEL, stroke_width=10),
                       Dot(scr([0, 0]), radius=0.11, color=WHITE), Dot(scr(e), radius=0.1, color=WHITE))
            v = ell(J, False, KV, ORANGE, False).move_to(scr(p))
            f = ell(J, True, KF, RED, True).move_to(scr(p))
            g.add(v, f, Dot(scr(p), radius=0.07, color=YELLOW))
            return g

        arm = always_redraw(rig)
        self.play(FadeIn(arm), run_time=0.8)
        self.caption("橙：单位关节速度能产生的末端速度；红虚线：单位关节力矩能平衡的末端力",
                     "Orange: tip velocities from unit joint speed. Red dashed: tip forces balanced by unit joint torque", wait=1.2)

        def info():
            J = jac(t2.get_value())
            s = np.linalg.svd(J, compute_uv=False)
            g = VGroup(MathTex(r"\theta_2 = %.0f^\circ" % math.degrees(t2.get_value()), font_size=36, color=YELLOW),
                       MathTex(r"\sigma_1,\ \sigma_2 = %.3f,\ %.3f\ \mathrm{m}" % (s[0], s[1]), font_size=30, color=ORANGE),
                       MathTex(r"1/\sigma_2,\ 1/\sigma_1 = %.1f,\ %.2f\ \mathrm{m^{-1}}" % (1 / s[1], 1 / s[0]), font_size=30, color=RED))
            return g.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to([3.6, 1.8, 0])

        inf = always_redraw(info)
        self.add(inf)
        self.play(t2.animate.set_value(math.radians(90)), run_time=3.0, rate_func=smooth)
        self.caption("两个椭圆的主轴方向相同，半轴互为倒数", "The two ellipses share their axes; their semi-axes are reciprocal", wait=1.0)
        self.play(t2.animate.set_value(math.radians(25)), run_time=5.0, rate_func=smooth)
        self.play(t2.animate.set_value(math.radians(18)), run_time=3.0, rate_func=smooth)
        self.caption("接近伸直：径向几乎动不了，却最能扛住沿手臂的力", "Nearly straight: hardly any radial speed, but the most radial force",
                     wait=1.6)
        self.card([["运动静力对偶", "Kinetostatic duality"],
                   MathTex(r"\mathcal V = J\dot\theta \qquad \tau = J^{\mathsf T}\mathcal F", font_size=40),
                   MathTex(r"\alpha(u)\,\beta(u) \le 1", font_size=38),
                   ["省力的方向必然费速度；沿主轴乘积为 1", "Cheap force means dear speed; product 1 on the axes"]])
