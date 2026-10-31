"""动画 15.4.1：正定、半正定与不定。二次型 q = x² + 2bxy + y²，A = [[1, b], [b, 1]]，特征值 1 ± b，主元 1、1 − b²，det A = 1 − b²。
等值线 q = 1：b = 0 是圆；0 < b < 1 是沿 (1, −1) 方向拉长的椭圆（正定）；b = 1 是一对平行直线 x + y = ±1（半正定，det = 0）；
b > 1 是双曲线（不定）。在主轴坐标 u = (x + y)/√2、v = (x − y)/√2 下 q = (1 + b)u² + (1 − b)v²。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("15.4", "正定 → 半正定 → 不定：x² + 2bxy + y²", "Definite, semidefinite, indefinite: x² + 2bxy + y²")
        s = 0.95
        O = np.array([-2.2, -0.45, 0.0])
        Lb = 2.6                                  # 画图范围（坐标单位）
        plane = NumberPlane(x_range=[-Lb, Lb, 1], y_range=[-Lb, Lb, 1], x_length=2 * Lb * s, y_length=2 * Lb * s,
                            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.5}).move_to(O)
        self.play(Create(plane), run_time=1.0)
        b = ValueTracker(0.0)
        P = lambda x, y: O + s * np.array([x, y, 0.0])
        r2 = np.sqrt(2)

        def curve():
            bv = b.get_value()
            segs = []
            if bv < 0.999:
                t = np.linspace(0, 2 * np.pi, 721)
                u, v = np.cos(t) / np.sqrt(1 + bv), np.sin(t) / np.sqrt(1 - bv)
                pts = [np.stack([(u + v) / r2, (u - v) / r2], 1)]
            else:
                vv = np.linspace(-6, 6, 721)
                uu = np.sqrt((1 + (bv - 1) * vv ** 2) / (1 + bv))
                pts = [np.stack([(sg * uu + vv) / r2, (sg * uu - vv) / r2], 1) for sg in (1, -1)]
            for p in pts:
                inside = (np.abs(p[:, 0]) <= Lb) & (np.abs(p[:, 1]) <= Lb)
                cur = []
                for ok, q in zip(inside, p):
                    if ok:
                        cur.append(P(*q))
                    elif len(cur) > 2:
                        segs.append(cur); cur = []
                    else:
                        cur = []
                if len(cur) > 2:
                    segs.append(cur)
            g = VGroup()
            col = GREEN if bv < 0.999 else (YELLOW if bv < 1.001 else RED)
            for c in segs:
                g.add(VMobject(color=col, stroke_width=5).set_points_as_corners(c))
            return g

        cv = always_redraw(curve)
        ax1 = DashedLine(P(-Lb / r2 * 0.95, -Lb / r2 * 0.95), P(Lb / r2 * 0.95, Lb / r2 * 0.95), color=GREY_B, stroke_width=2)
        ax2 = DashedLine(P(-Lb / r2 * 0.95, Lb / r2 * 0.95), P(Lb / r2 * 0.95, -Lb / r2 * 0.95), color=GREY_B, stroke_width=2)
        self.add(cv)
        self.play(Create(ax1), Create(ax2), run_time=0.8)
        self.caption("b = 0：x² + y² = 1 是单位圆。两条虚线是 A 的特征向量方向 (1, 1)、(1, −1)",
                     "b = 0: x² + y² = 1 is the unit circle. The dashed lines are the eigenvector directions (1, 1), (1, −1)", wait=1.0)

        R = O[0] + Lb * s + 1.0
        col = lambda x: GREEN if x > 1e-3 else (YELLOW if x > -1e-3 else RED)
        specs = [(r"b =", lambda bv: bv), (r"\lambda_1 = 1+b =", lambda bv: 1 + bv), (r"\lambda_2 = 1-b =", lambda bv: 1 - bv),
                 (r"d_2 = 1-b^2 =", lambda bv: 1 - bv * bv), (r"\det A = 1-b^2 =", lambda bv: 1 - bv * bv)]
        rows = VGroup()
        for i, (lab, fn) in enumerate(specs):
            t = MathTex(lab, font_size=34)
            n = DecimalNumber(fn(0.0), num_decimal_places=2, font_size=34)
            n.next_to(t, RIGHT, buff=0.2)
            rows.add(VGroup(t, n))
        head = MathTex(r"A=\begin{pmatrix}1 & b\\ b & 1\end{pmatrix},\quad d_1 = 1", font_size=34)
        pn = VGroup(head, *rows).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to([R + 2.0, -0.2, 0])
        for i, (r, (lab, fn)) in enumerate(zip(rows, specs)):
            t, n = r
            if i:
                n.add_updater(lambda m, fn=fn, t=t: m.set_value(fn(b.get_value())).next_to(t, RIGHT, buff=0.2).set_color(col(fn(b.get_value()))))
                t.add_updater(lambda m, fn=fn: m.set_color(col(fn(b.get_value()))))
            else:
                n.add_updater(lambda m, fn=fn, t=t: m.set_value(fn(b.get_value())).next_to(t, RIGHT, buff=0.2))
        self.play(FadeIn(pn), run_time=0.6)
        self.play(b.animate.set_value(0.6), run_time=2.5, rate_func=linear)
        self.caption("b 增大：椭圆沿 (1, −1) 方向拉长，那个方向的特征值 1 − b 变小。仍然正定",
                     "As b grows the ellipse stretches along (1, −1), where the eigenvalue 1 − b shrinks. Still positive definite", wait=1.2)
        self.play(b.animate.set_value(0.95), run_time=2.0, rate_func=linear)
        self.play(b.animate.set_value(1.0), run_time=1.2, rate_func=linear)
        self.caption("b = 1：λ₂ = 0，第二个主元和行列式同时变成 0。等值线变成一对平行直线：半正定",
                     "b = 1: λ₂ = 0, and the second pivot and det A vanish together. Two parallel lines: semidefinite", wait=1.6)
        self.play(b.animate.set_value(1.5), run_time=2.5, rate_func=linear)
        self.caption("b > 1：λ₂ < 0，主元与行列式变负。等值线变成双曲线，二次型能取负值：不定",
                     "b > 1: λ₂ < 0 and the pivot and det turn negative. A hyperbola: the form takes negative values, indefinite", wait=1.6)
        self.play(b.animate.set_value(0.3), run_time=3.0, rate_func=smooth)
        self.caption("对角元始终是 1，但只有 |b| < 1 时正定：判断正定不能只看对角元",
                     "The diagonal stays 1, yet A is positive definite only for |b| < 1: the diagonal alone decides nothing", wait=1.5)
        self.card([["特征值、主元、顺序主子式同时变号", "Eigenvalues, pivots and leading minors change sign together"],
                   ["正定：等值线是椭圆；半正定：平行直线；不定：双曲线", "Definite: ellipse; semidefinite: parallel lines; indefinite: hyperbola"],
                   ["对角元都正 ≠ 正定", "Positive diagonal ≠ positive definite"]])
