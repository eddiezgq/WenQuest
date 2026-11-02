"""动画 23.5.1：高斯–牛顿法的几何意义。三个 UWB 基站测出到 AGV 的距离，AGV 应在三个圆的交点附近（距离有误差，三圆不严格交于一点）。
第 1 步：从一个猜测点出发，把每个圆在“猜测点所在射线”与圆的交点处换成切线——这就是把距离方程线性化；
第 2 步：三条切线不交于一点，取到三条直线距离平方和最小的点（线性最小二乘）作为新的估计；
第 3 步：在新的点重新线性化，重复；两三步后估计点停在三圆“最接近相交”的地方。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("23.5", "高斯–牛顿法：用直线代替圆，一步步逼近", "Gauss–Newton: replace circles by lines, step by step")
        s = 0.08
        O = np.array([-1.4, -0.95, 0.0])
        P = lambda v: O + s * np.array([v[0], v[1], 0.0])
        anchors = np.array([[0.0, 0.0], [30.0, 0.0], [12.0, 26.0]])
        p_true = np.array([20.0, 9.0])
        d = np.linalg.norm(anchors - p_true, axis=1) + np.array([0.6, -0.5, 0.4])
        cols = (BLUE_C, GREEN_C, ORANGE)
        circles = VGroup(*[Circle(radius=s * di, color=c, stroke_width=2.5).move_to(P(a)) for a, di, c in zip(anchors, d, cols)])
        dots = VGroup(*[Triangle(color=c, fill_opacity=1).scale(0.12).move_to(P(a)) for a, c in zip(anchors, cols)])
        self.play(FadeIn(dots), Create(circles), run_time=1.5)
        self.caption("三个基站测出距离：AGV 应在三个圆上；距离有误差，三个圆不严格交于一点",
                     "Three anchors measure ranges: the AGV lies on three circles, which do not quite meet because of errors", wait=1.2)
        p = np.array([6.0, 18.0])
        cur = Dot(P(p), color=RED, radius=0.08)
        self.play(FadeIn(cur))
        for it in range(3):
            lines = VGroup()
            for a, di, c in zip(anchors, d, cols):
                u = (p - a) / np.linalg.norm(p - a)
                foot = a + di * u
                tdir = np.array([-u[1], u[0]])
                lines.add(Line(P(foot - 9 * tdir), P(foot + 9 * tdir), color=c, stroke_width=3))
            self.play(Create(lines), run_time=1.0)
            if it == 0:
                self.caption("在猜测点处线性化：每个圆换成它在“射线交点”处的切线", "Linearize at the guess: each circle becomes its tangent line where the ray meets it", wait=1.2)
            diff = p - anchors
            rr = np.linalg.norm(diff, axis=1)
            J = diff / rr[:, None]
            pn = p + np.linalg.lstsq(J, d - rr, rcond=None)[0]
            new = Dot(P(pn), color=RED, radius=0.08)
            self.play(TransformFromCopy(cur, new), Create(Line(P(p), P(pn), color=RED, stroke_width=2)), run_time=1.0)
            if it == 0:
                self.caption("三条直线的最小二乘“交点”就是新的估计：一个线性最小二乘问题", "The least-squares ‘intersection’ of the three lines is the new estimate: a linear least-squares problem", wait=1.4)
            self.play(FadeOut(lines), run_time=0.5)
            cur, p = new, pn
        self.caption("重复几次，估计点停在三个圆“最接近相交”的地方：非线性最小二乘的解", "After a few repeats the estimate settles where the circles come closest to meeting: the nonlinear least-squares solution", wait=1.4)
        self.card([["高斯–牛顿法", "Gauss–Newton method"],
                   ["每一步：在当前点线性化 r(p + δ) ≈ r(p) − Jδ，解线性最小二乘求 δ", "Each step: linearize r(p + δ) ≈ r(p) − Jδ and solve a linear least-squares problem for δ"],
                   ["离解近、残差小时收敛很快；初值差时加阻尼（列文伯格–马夸特）", "Fast near a small-residual solution; add damping (Levenberg–Marquardt) for poor starts"]])
