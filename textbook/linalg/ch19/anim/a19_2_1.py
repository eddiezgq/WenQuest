"""动画 19.2.1：主成分是投影方差最大的方向。40 个标准化的数据点（相关系数约 0.8，像噪声与振动）；
一条过原点的直线旋转，各点向它作垂线：投影方差（红柱）与残差平方和（绿柱）此消彼长，两者之和不变（勾股定理）。
直线转到 45° 时投影方差最大、残差最小，这就是第一主成分；与它垂直的是第二主成分。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("19.2", "主成分：方差最大的方向", "Principal components: directions of largest variance")
        rng = np.random.default_rng(192)
        n, r = 40, 0.8
        Lc = np.linalg.cholesky(np.array([[1, r], [r, 1]]))
        D = rng.standard_normal((n, 2)) @ Lc.T
        D = D - D.mean(axis=0)
        D = D / D.std(axis=0, ddof=1)
        C = D.T @ D / (n - 1)
        w, V = np.linalg.eigh(C)
        s = 0.95
        O = np.array([-2.6, -0.45, 0.0])
        P = lambda x, y: O + s * np.array([x, y, 0.0])
        plane = NumberPlane(x_range=[-3.5, 3.5, 1], y_range=[-3, 3, 1], x_length=7 * s, y_length=6 * s,
                            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.5}).move_to(O)
        dots = VGroup(*[Dot(P(*d), radius=0.05, color=BLUE_B) for d in D])
        self.play(Create(plane), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.03), run_time=1.4)
        self.caption("40 台减速器的噪声与振动（标准化后），点云沿对角线方向拉长", "Noise and vibration of 40 gearboxes (standardized): the cloud is stretched along the diagonal", wait=1.0)
        ang = ValueTracker(0.0)

        def udir():
            a = np.radians(ang.get_value())
            return np.array([np.cos(a), np.sin(a)])

        line = always_redraw(lambda: Line(P(*(-3.4 * udir())), P(*(3.4 * udir())), color=YELLOW, stroke_width=4))

        def drops():
            u = udir()
            g = VGroup()
            for d in D:
                q = (d @ u) * u
                g.add(Line(P(*d), P(*q), color=GREEN, stroke_width=1.6, stroke_opacity=0.8))
                g.add(Dot(P(*q), radius=0.035, color=RED))
            return g

        perp = always_redraw(drops)
        self.play(Create(line), run_time=0.8)
        self.add(perp)
        # 右边：两根柱子
        bx, by, H = 3.2, -2.3, 1.6           # 柱底与“每单位方差”的高度
        tot = float(np.trace(C))

        def pvar():
            u = udir()
            return float(u @ C @ u)

        bar_p = always_redraw(lambda: Rectangle(width=0.8, height=max(pvar() * H, 0.01), color=RED, fill_color=RED, fill_opacity=0.8)
                              .move_to([bx, by, 0], aligned_edge=DOWN))
        bar_r = always_redraw(lambda: Rectangle(width=0.8, height=max((tot - pvar()) * H, 0.01), color=GREEN, fill_color=GREEN, fill_opacity=0.8)
                              .move_to([bx + 1.4, by, 0], aligned_edge=DOWN))
        lab_p = zh("投影方差", 22, RED).move_to([bx, by - 0.3, 0])
        lab_r = zh("残差", 22, GREEN).move_to([bx + 1.4, by - 0.3, 0])
        num_p = DecimalNumber(pvar(), num_decimal_places=2, font_size=30, color=RED)
        num_p.add_updater(lambda m: m.set_value(pvar()).next_to(bar_p, UP, buff=0.08))
        num_r = DecimalNumber(tot - pvar(), num_decimal_places=2, font_size=30, color=GREEN)
        num_r.add_updater(lambda m: m.set_value(tot - pvar()).next_to(bar_r, UP, buff=0.08))
        tl = zh("红 + 绿 = tr R = 2（不变）", 22, GREY_B).move_to([bx + 0.7, 1.75, 0])
        angn = DecimalNumber(0, num_decimal_places=0, font_size=30, unit="^\\circ", color=YELLOW).move_to([bx + 0.7, 2.25, 0])
        angn.add_updater(lambda m: m.set_value(ang.get_value()))
        angl = zh("直线方向", 22, YELLOW).next_to(angn, LEFT, buff=0.2)
        self.play(FadeIn(bar_p), FadeIn(bar_r), FadeIn(lab_p), FadeIn(lab_r), FadeIn(num_p), FadeIn(num_r), FadeIn(tl), FadeIn(angl), FadeIn(angn))
        self.caption("黄线是试探方向，红点是投影，绿线是各点到直线的距离", "Yellow: a trial direction; red: projections; green: distances to the line", wait=1.0)
        self.play(ang.animate.set_value(180), run_time=7, rate_func=linear)
        self.caption("转一圈：红柱升，绿柱就降，两者之和不变（勾股定理）", "Turning: when red rises green falls; their sum stays fixed (Pythagoras)", wait=1.0)
        a1 = float(np.degrees(np.arctan2(V[1, 1], V[0, 1])) % 180)
        self.play(ang.animate.set_value(a1), run_time=2.5)
        self.caption("投影方差最大、残差最小的方向：第一主成分 v₁", "Largest projected variance, smallest residual: the first principal component v₁", wait=1.2)
        v1 = V[:, 1] if V[0, 1] > 0 else -V[:, 1]
        v2 = np.array([-v1[1], v1[0]])
        ar1 = Arrow(P(0, 0), P(*(2 * np.sqrt(w[1]) * v1)), buff=0, color=RED, stroke_width=7, max_tip_length_to_length_ratio=0.15)
        ar2 = Arrow(P(0, 0), P(*(2.4 * np.sqrt(w[0]) * v2)), buff=0, color=GREEN, stroke_width=7, max_tip_length_to_length_ratio=0.35)
        t = np.linspace(0, 2 * np.pi, 120)
        ell = VMobject(color=GREY_B, stroke_width=2).set_points_smoothly(
            [P(*(2 * np.sqrt(w[1]) * np.cos(tt) * v1 + 2 * np.sqrt(w[0]) * np.sin(tt) * v2)) for tt in t])
        l1 = MathTex(r"\boldsymbol v_1", color=RED, font_size=34).next_to(ar1.get_end(), UR, buff=0.05)
        l2 = MathTex(r"\boldsymbol v_2", color=GREEN, font_size=34).next_to(ar2.get_end(), UL, buff=0.05)
        self.play(FadeOut(perp), GrowArrow(ar1), GrowArrow(ar2), Create(ell), FadeIn(l1), FadeIn(l2), run_time=1.6)
        eig = MathTex(r"\lambda_1 = %.2f,\ \lambda_2 = %.2f" % (w[1], w[0]), font_size=34).move_to([bx + 0.7, 1.25, 0])
        self.play(FadeIn(eig))
        self.caption("v₁、v₂ 是协方差矩阵的特征向量，柱高就是特征值 λ₁、λ₂", "v₁, v₂ are eigenvectors of the covariance matrix; the bar heights are the eigenvalues", wait=1.6)
        self.card([["主成分：投影方差最大的方向", "Principal components: directions of largest variance"],
                   ["方差最大 ⇔ 到直线的距离平方和最小", "Largest variance ⇔ smallest sum of squared distances"],
                   ["方向是协方差矩阵的特征向量，方差是特征值", "Directions: eigenvectors of the covariance; variances: eigenvalues"]])
