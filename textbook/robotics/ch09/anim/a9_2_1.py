"""动画 9.2.1（配图 9.2.3）：不确定性椭圆。
第一段：关节角误差 (δθ₁, δθ₂) 的点云是圆形（两关节独立、标准差相同），经雅可比矩阵 J 变成末端误差的椭圆点云。
第二段：2R 臂（L = 0.425、0.392 m）由 θ₂ = 100° 逐渐伸直到 8°，末端的 95% 椭圆（放大 100 倍）越来越扁，长轴垂直于手臂。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
SIG = math.radians(0.1)
C95 = math.sqrt(-2 * math.log(0.05))


def jac(t1, t2):
    s1, c1, s12, c12 = math.sin(t1), math.cos(t1), math.sin(t1 + t2), math.cos(t1 + t2)
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


class Lesson(Base):
    def construct(self):
        self.title("9.2", "不确定性椭圆", "The uncertainty ellipse")
        rng = np.random.default_rng(921)
        w = rng.standard_normal((2, 260))

        # ---------------- 第一段：圆形点云 → 椭圆点云
        left = np.array([-3.6, -0.1, 0])
        right = np.array([2.4, -0.1, 0])
        axL = VGroup(Line(left + LEFT * 2, left + RIGHT * 2, color=GREY_D), Line(left + DOWN * 1.8, left + UP * 1.8, color=GREY_D),
                     MathTex(r"\delta\theta_1", font_size=30).next_to(left + RIGHT * 2, DOWN, buff=0.1),
                     MathTex(r"\delta\theta_2", font_size=30).next_to(left + UP * 1.8, RIGHT, buff=0.1))
        axR = VGroup(Line(right + LEFT * 2.6, right + RIGHT * 2.6, color=GREY_D), Line(right + DOWN * 1.8, right + UP * 1.8, color=GREY_D),
                     MathTex(r"\delta x", font_size=30).next_to(right + RIGHT * 2.6, DOWN, buff=0.1),
                     MathTex(r"\delta y", font_size=30).next_to(right + UP * 1.8, RIGHT, buff=0.1))
        k_in = 0.55                                     # 关节空间：1σ 画成 0.55 个单位
        dotsL = VGroup(*[Dot(left + k_in * np.array([w[0, i], w[1, i], 0]), radius=0.03, color=YELLOW) for i in range(w.shape[1])])
        circ = Circle(radius=k_in * C95, color=YELLOW, stroke_width=3).move_to(left)
        self.play(Create(axL), FadeIn(dotsL), Create(circ), run_time=1.5)
        self.caption("两个关节角的误差：独立、标准差相同，点云是圆的", "Joint-angle errors: independent, equal spread, a round cloud")

        J = jac(math.radians(30), math.radians(60))
        k_out = 0.55 / 0.75                             # 末端：把 J 的典型尺度画成同样大小
        P = J @ w
        tgt = VGroup(*[Dot(right + k_out * np.array([P[0, i], P[1, i], 0]), radius=0.03, color=BLUE) for i in range(w.shape[1])])
        lam, V = np.linalg.eigh(J @ J.T)
        A = V @ np.diag(np.sqrt(lam))
        ell = ParametricFunction(lambda t: right + k_out * C95 * np.array([A[0, 0] * math.cos(t) + A[0, 1] * math.sin(t),
                                                                           A[1, 0] * math.cos(t) + A[1, 1] * math.sin(t), 0]),
                                 t_range=[0, 2 * PI], color=BLUE, stroke_width=4)
        arrow = Arrow(left + RIGHT * 2.1, right + LEFT * 2.7, buff=0.1, color=WHITE, stroke_width=4)
        jl = MathTex(r"J", font_size=40).next_to(arrow, UP, buff=0.05)
        self.play(Create(axR), GrowArrow(arrow), Write(jl), run_time=1.0)
        self.caption("每个点乘以雅可比矩阵 J：δp = J δθ", "Each point is multiplied by the Jacobian: δp = J δθ", wait=0)
        self.play(TransformFromCopy(dotsL, tgt), TransformFromCopy(circ, ell), run_time=2.5)
        form = MathTex(r"\Sigma_p = J\,\Sigma_\theta\,J^{\mathsf T}", font_size=40, color=BLUE).move_to(right + UP * 1.4 + RIGHT * 2.2)
        self.play(Write(form))
        self.caption("圆变成斜着的椭圆：末端误差有方向，x、y 负相关", "The circle becomes a tilted ellipse: the tip error has a direction", wait=1.2)
        self.clear_stage()

        # ---------------- 第二段：手臂逐渐伸直
        base = np.array([-3.2, -2.0, 0])
        S = 4.0                                          # 1 m 画成 4 个单位
        MAG = 100 * S                                     # 椭圆放大 100 倍
        t2 = ValueTracker(100.0)
        t1 = 30.0

        def scene():
            a2 = t2.get_value()
            g = planar_arm(base, [t1, a2], [L1 * S, L2 * S], color=STEEL)
            th1, th2 = math.radians(t1), math.radians(a2)
            tip = base + S * np.array([L1 * math.cos(th1) + L2 * math.cos(th1 + th2), L1 * math.sin(th1) + L2 * math.sin(th1 + th2), 0])
            Jt = jac(th1, th2)
            lam, V = np.linalg.eigh(SIG ** 2 * Jt @ Jt.T)
            lam = np.maximum(lam, 0)
            pts = [tip + MAG * C95 * np.r_[V @ np.diag(np.sqrt(lam)) @ np.array([math.cos(t), math.sin(t)]), 0]
                   for t in np.linspace(0, 2 * PI, 80)]
            e = Polygon(*pts, color=BLUE, stroke_width=4, fill_color=BLUE, fill_opacity=0.25)
            ratio = math.sqrt(lam[1] / max(lam[0], 1e-30))
            txt = VGroup(MathTex(r"\theta_2 = %d^\circ" % round(a2), font_size=36),
                         VGroup(bi(["长短轴之比", "axis ratio"], 24, BLUE), MathTex(r"= %.1f" % ratio, font_size=34, color=BLUE)).arrange(RIGHT, buff=0.15)
                         ).arrange(DOWN, aligned_edge=LEFT)
            txt.to_corner(UR, buff=0.6).shift(DOWN * 0.8)
            return VGroup(g, e, txt)

        sc = always_redraw(scene)
        self.add(sc)
        note = zh("椭圆放大 100 倍", 22, MUTED).to_corner(UR, buff=0.6).shift(DOWN * 2.3)
        self.add(note)
        self.caption("关节角各有 0.1° 的误差：末端的 95% 椭圆", "0.1° on each joint: the tip's 95% ellipse", wait=0.8)
        self.caption("手臂逐渐伸直，椭圆越来越扁", "As the arm straightens, the ellipse flattens", wait=0)
        self.play(t2.animate.set_value(8), run_time=5, rate_func=smooth)
        self.caption("接近伸直：沿手臂方向几乎没有误差，误差全部垂直于手臂", "Nearly straight: almost no error along the arm, all across it", wait=1.5)
        sc.clear_updaters()
        self.card([["不确定性传播", "Uncertainty propagation"],
                   MathTex(r"\Sigma_p \approx J\,\Sigma_\theta\,J^{\mathsf T}", font_size=44),
                   ["椭圆主轴沿 Σₚ 的特征向量，半轴为 c√λᵢ", "Axes along the eigenvectors of Σₚ, semi-axes c√λᵢ"]])
