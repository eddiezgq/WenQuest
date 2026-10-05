"""动画 16.6.1（配图 16.6.1）：平面 2R 臂，L1 = √2 L2（L2 = 0.3 m）。肘角 θ2 从 30° 增到 170°，再回到 135°：
末端的速度椭圆先是扁的，在 θ2 = 135° 变成圆（各向同性，κ = 1），再变扁；右侧同步描出条件数 κ 随 θ2 的曲线。
最后对比本书的 2R 臂（0.425、0.392 m）：它的 κ 最小只能降到约 1.45。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L2 = 0.3
L1 = math.sqrt(2) * L2
S = 5.0
BASE = np.array([-5.2, -1.9, 0.0])
T1 = math.radians(20)


def jac(t2, l1=L1, l2=L2):
    a, b = T1, T1 + t2
    return np.array([[-l1 * math.sin(a) - l2 * math.sin(b), -l2 * math.sin(b)], [l1 * math.cos(a) + l2 * math.cos(b), l2 * math.cos(b)]])


def kap(t2, l1=L1, l2=L2):
    s = np.linalg.svd(jac(t2, l1, l2), compute_uv=False)
    return s[0] / max(s[1], 1e-9)


def scr(p):
    return BASE + S * np.array([p[0], p[1], 0.0])


class Lesson(Base):
    def construct(self):
        self.title("16.6", "各向同性：椭圆变成圆", "Isotropy: the ellipse becomes a circle")
        t2 = ValueTracker(math.radians(30))

        def rig():
            a, b = T1, T1 + t2.get_value()
            e = np.array([L1 * math.cos(a), L1 * math.sin(a)])
            p = e + L2 * np.array([math.cos(b), math.sin(b)])
            J = jac(t2.get_value())
            U, s, _ = np.linalg.svd(J)
            k = 0.45 * S
            ang = math.atan2(U[1, 0], U[0, 0])
            iso = s[0] / s[1] < 1.02
            el = Ellipse(width=2 * s[0] * k, height=2 * max(s[1], 1e-3) * k, color=GREEN if iso else ORANGE, stroke_width=5).rotate(ang).move_to(scr(p))
            return VGroup(Polygon(BASE + LEFT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.4 + DOWN * 0.3, BASE + RIGHT * 0.2, BASE + LEFT * 0.2,
                                  color=GREY_B, fill_color=GREY_E, fill_opacity=1),
                          Line(scr([0, 0]), scr(e), color=STEEL, stroke_width=14), Line(scr(e), scr(p), color=STEEL, stroke_width=10),
                          Dot(scr([0, 0]), radius=0.11, color=WHITE), Dot(scr(e), radius=0.1, color=WHITE), el, Dot(scr(p), radius=0.07, color=YELLOW))

        arm = always_redraw(rig)
        self.play(FadeIn(arm), run_time=0.8)
        self.caption("L₁ = √2 L₂。椭圆：单位关节速度能产生的末端速度", "L₁ = √2 L₂. Ellipse: tip velocities from unit joint speed", wait=0.8)

        ax = Axes(x_range=[20, 180, 40], y_range=[0, 1.05, 0.5], x_length=4.8, y_length=2.6, tips=False,
                  axis_config={"color": GREY_B, "stroke_width": 2, "include_ticks": False}).move_to([3.7, 0.9, 0])
        xs = np.linspace(22, 178, 157)
        c_iso = ax.plot_line_graph(xs, [1 / kap(math.radians(x)) for x in xs], line_color=ORANGE, add_vertex_dots=False, stroke_width=4)
        lab = VGroup(MathTex(r"1/\kappa", font_size=32, color=ORANGE).next_to(ax, UP, buff=0.1),
                     MathTex(r"\theta_2", font_size=30, color=GREY_B).next_to(ax, DOWN, buff=0.15))
        self.play(Create(ax), FadeIn(lab), run_time=0.8)

        def mark():
            x = math.degrees(t2.get_value())
            k = kap(t2.get_value())
            return VGroup(Dot(ax.c2p(x, 1 / k), radius=0.08, color=YELLOW),
                          MathTex(r"\theta_2 = %.0f^\circ \quad \kappa = %.2f" % (x, k), font_size=32, color=YELLOW).move_to([3.7, -1.35, 0]))

        mk = always_redraw(mark)
        self.add(mk)
        self.play(Create(c_iso), t2.animate.set_value(math.radians(170)), run_time=6.0, rate_func=linear)
        self.play(t2.animate.set_value(math.radians(135)), run_time=2.5, rate_func=smooth)
        self.caption("θ₂ = 135°：两列等长、互相垂直，椭圆成圆，κ = 1——各向同性", "At θ₂ = 135° the two columns are equal and perpendicular: a circle, κ = 1, isotropic",
                     wait=1.5)
        c_ours = ax.plot_line_graph(xs, [1 / kap(math.radians(x), 0.425, 0.392) for x in xs], line_color=BLUE, add_vertex_dots=False, stroke_width=3)
        self.play(Create(c_ours), run_time=1.5)
        self.caption("蓝线：本书的 2R 臂（0.425、0.392 m），1/κ 最大只有约 0.69，到不了 1",
                     "Blue: the book's 2R arm (0.425, 0.392 m); 1/κ peaks near 0.69 and never reaches 1", wait=1.5)
        self.card([["平面 2R 臂的各向同性", "Isotropy of the planar 2R arm"],
                   MathTex(r"JJ^{\mathsf T} = cI \iff L_1 = \sqrt2\,L_2,\ \theta_2 = \pm135^\circ", font_size=38),
                   MathTex(r"\mathrm{LCI} = 1/\kappa \in [0, 1]", font_size=38),
                   ["各方向一样灵活，误差也不被放大", "Equally agile in every direction, and errors are not amplified"]])
