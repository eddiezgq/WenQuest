"""动画 13.5.1（配图 13.5.1）：相邻两轴接近平行时，DH 的公垂线怎样突变。
轴 i+1 在两轴所在的平面内偏转 ε：两轴相交于 d = −a cot ε 处，ε → 0 时交点跑到无穷远；ε 变号时 d 从 −∞ 跳到 +∞。
哈亚蒂的做法取轴 i+1 与 {i−1} 的 xy 平面的交点，a 与 β = ε 都连续变化。a = 0.425 m（UR5e 大臂）。"""
from manim import *
from wq_anim import *
import numpy as np

A = 0.425
SC = 4.0
X0 = -2.6          # 轴 i 在屏幕上的 x
Y0 = 0.2           # {i−1} 的原点在屏幕上的 y（z = 0）
YMIN, YMAX = -2.6, 2.2


def S(x, z):
    return np.array([X0 + SC * x, Y0 + SC * z, 0.0])


class Lesson(Base):
    def construct(self):
        self.title("13.5", "接近平行的两根轴：DH 参数的突变", "Nearly parallel axes: the DH parameters jump")
        eps = ValueTracker(0.0)            # 度

        axis_i = Line(S(0, -0.68), S(0, 0.42), color=GREY_B, stroke_width=5)
        lab_i = zh("轴 i", 22, GREY_B).next_to(axis_i.get_top(), LEFT, buff=0.15)
        frame0 = VGroup(Arrow(S(0, 0), S(0.12, 0), buff=0, color=RED, stroke_width=5),
                        Arrow(S(0, 0), S(0, 0.12), buff=0, color=BLUE, stroke_width=5))
        lab_f = MathTex(r"\{i-1\}", font_size=28).next_to(S(0, 0), LEFT, buff=0.15)
        plane_line = DashedLine(S(-0.15, 0), S(0.75, 0), color=GREY_D, stroke_width=2)
        self.play(Create(axis_i), FadeIn(lab_i), FadeIn(frame0), FadeIn(lab_f), Create(plane_line))

        def axis_n():
            e = np.radians(eps.get_value())
            d = np.array([np.sin(e), np.cos(e)])
            p0, p1 = np.array([A, 0]) + (-0.68 / max(np.cos(e), 0.2)) * d, np.array([A, 0]) + (0.42 / max(np.cos(e), 0.2)) * d
            return Line(S(*p0), S(*p1), color=WHITE, stroke_width=5)

        ax_n = always_redraw(axis_n)
        lab_n = zh("轴 i+1", 22, WHITE).move_to(S(A + 0.2, 0.42))
        self.add(ax_n, lab_n)

        def dh_marks():
            e = np.radians(eps.get_value())
            g = VGroup()
            if abs(e) < 1e-6:            # 平行：取 d = 0 的公垂线
                g.add(DashedLine(S(0, 0), S(A, 0), color=YELLOW, stroke_width=5), Dot(S(A, 0), color=YELLOW, radius=0.09))
                return g
            zc = -A / np.tan(e)
            y = Y0 + SC * zc
            if YMIN < y < YMAX:
                g.add(Dot(S(0, zc), color=YELLOW, radius=0.11))
            else:                        # 交点在画面外：在边缘画箭头
                g.add(Arrow([X0, Y0 - 0.5 if zc < 0 else Y0 + 0.5, 0], [X0, YMIN + 0.3 if zc < 0 else YMAX - 0.3, 0],
                            color=YELLOW, buff=0, stroke_width=4))
            txt = MathTex(r"d_i = %.1f\ \mathrm{m},\quad a_i = 0" % zc, color=YELLOW, font_size=34)
            g.add(txt.move_to([3.3, 1.6, 0]))
            return g

        dh = always_redraw(dh_marks)
        self.add(dh)
        self.caption("两轴平行：公垂线有无穷多条，DH 取 d = 0 的一条", "Parallel axes: infinitely many normals; DH takes the one with d = 0")
        self.play(eps.animate.set_value(30.0), run_time=2.5)
        self.caption("轴 i+1 一偏转，两轴就在某处相交：a 突然变成 0，{i} 的原点跑到交点",
                     "Tilt axis i+1 and the axes meet: a drops to 0, the origin of {i} jumps to the crossing")
        self.play(eps.animate.set_value(3.0), run_time=3.0, rate_func=smooth)
        self.play(eps.animate.set_value(0.5), run_time=1.5)
        self.caption("ε 越小，交点越远：ε = 0.01° 时 d ≈ −2435 m", "The smaller ε, the farther the crossing: d ≈ −2435 m at ε = 0.01°")
        self.play(eps.animate.set_value(-0.5), run_time=0.8, rate_func=linear)
        self.caption("向另一侧偏转：d 从 −∞ 跳到 +∞——参数随几何不连续", "Tilt the other way: d jumps from −∞ to +∞; the parameters are not continuous")

        # 哈亚蒂：与 xy 平面的交点
        def hayati():
            e = np.radians(eps.get_value())
            g = VGroup(Dot(S(A, 0), color=GREEN, radius=0.1),
                       MathTex(r"\text{Hayati: } a = 0.425\ \mathrm{m},\ \beta = %.1f^\circ" % eps.get_value(), color=GREEN, font_size=32).move_to([3.3, 0.7, 0]))
            return g

        hy = always_redraw(hayati)
        self.play(FadeIn(hy))
        self.caption("哈亚蒂：取轴 i+1 与 xy 平面的交点（绿点），a 不变，多一个转角 β = ε",
                     "Hayati: use where axis i+1 crosses the xy plane (green): a stays, an extra angle β = ε")
        self.play(eps.animate.set_value(8.0), run_time=2.0)
        self.play(eps.animate.set_value(-8.0), run_time=2.0)
        self.wait(0.5)
        self.card([["DH 在平行轴处不连续", "DH is discontinuous at parallel axes"],
                   MathTex(r"d_i = -a\cot\varepsilon \approx -\frac{a}{\varepsilon}\quad(\varepsilon \to 0)", font_size=40),
                   ["标定时改用哈亚蒂参数或指数积：参数随轴连续变化", "For calibration use Hayati parameters or the PoE: they vary continuously"]])
