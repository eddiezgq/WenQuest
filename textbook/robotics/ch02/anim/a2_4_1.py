"""动画 2.4.1（配图 2.4.1）：单位圆变成椭圆。依次演示 Vᵀ 的转动、Σ 的伸缩、U 的转动，最后与 J 直接作用的结果重合。
J 为 2R 臂在 θ = (30°, 60°) 时的雅可比矩阵（算例 2.4.1），画图时按 σ1 缩放为 1。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("2.4", "奇异值分解：圆变成椭圆", "The SVD: a circle becomes an ellipse")
        l1, l2, t1, t2 = 0.425, 0.392, math.radians(30), math.radians(60)
        J = np.array([[-l1 * math.sin(t1) - l2 * math.sin(t1 + t2), -l2 * math.sin(t1 + t2)],
                      [l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l2 * math.cos(t1 + t2)]])
        U, s, Vt = np.linalg.svd(J)
        if Vt[0, 0] < 0:
            Vt[0] *= -1
            U[:, 0] *= -1
        if np.linalg.det(Vt) < 0:
            Vt[1] *= -1
            U[:, 1] *= -1
        k = 1.0 / s[0]
        S = np.diag(s) * k
        R = 2.0
        O = np.array([-1.8, -0.4, 0])
        stage = {"A": np.eye(2), "B": np.eye(2)}
        t = ValueTracker(0.0)

        def M():
            a = t.get_value()
            return (1 - a) * stage["A"] + a * stage["B"]

        def P(v):
            return O + R * np.array([v[0], v[1], 0])

        axes = VGroup(Line(P([-1.3, 0]), P([1.3, 0]), color=GREY_D), Line(P([0, -1.2]), P([0, 1.2]), color=GREY_D))
        self.add(axes)

        def shape():
            A = M()
            ell = ParametricFunction(lambda q: P(A @ np.array([math.cos(q), math.sin(q)])), t_range=[0, 2 * PI],
                                     color=YELLOW, stroke_width=4)
            V = Vt.T
            a1 = Arrow(P([0, 0]), P(A @ V[:, 0]), buff=0, color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.15)
            a2 = Arrow(P([0, 0]), P(A @ V[:, 1]), buff=0, color=BLUE, stroke_width=6, max_tip_length_to_length_ratio=0.3)
            return VGroup(ell, a1, a2)

        sh = always_redraw(shape)
        self.add(sh)
        lab = MathTex(r"v_1", r"\;\;", r"v_2", font_size=36)
        lab[0].set_color(RED)
        lab[2].set_color(BLUE)
        lab.move_to(np.array([4.3, 1.6, 0]))
        self.play(FadeIn(lab), run_time=0.5)
        self.caption("单位圆：所有长度为 1 的关节速度；红、蓝是 v₁、v₂", "Unit circle: all joint speeds of length 1; red and blue are v₁, v₂", wait=1.0)
        steps = [(Vt, r"V^{\mathsf T}", "① 乘 Vᵀ：转动，把 v₁、v₂ 转到坐标轴上", "① Vᵀ rotates v₁, v₂ onto the axes"),
                 (S @ Vt, r"\Sigma V^{\mathsf T}", "② 乘 Σ：沿坐标轴伸缩 σ₁、σ₂ 倍，圆变成椭圆", "② Σ stretches along the axes by σ₁, σ₂"),
                 (k * U @ np.diag(s) @ Vt, r"U\Sigma V^{\mathsf T}", "③ 乘 U：再转动，半轴转到 u₁、u₂ 方向", "③ U rotates the semi-axes onto u₁, u₂")]
        formula = None
        for B, tex, zh_t, en_t in steps:
            stage["A"], stage["B"] = stage["B"], B
            t.set_value(0)
            self.caption(zh_t, en_t, wait=0)
            f = MathTex(tex, font_size=44).move_to(np.array([4.3, 0.4, 0]))
            self.play(t.animate.set_value(1), FadeIn(f) if formula is None else ReplacementTransform(formula, f), run_time=2.2)
            formula = f
            self.wait(1.2)
        direct = ParametricFunction(lambda q: P(k * J @ np.array([math.cos(q), math.sin(q)])), t_range=[0, 2 * PI],
                                    color=GREEN, stroke_width=3).set_stroke(opacity=0.9)
        self.caption("与 J 直接作用的结果完全重合：J = UΣVᵀ", "It coincides with applying J directly: J = UΣVᵀ", wait=0)
        self.play(Create(direct), run_time=1.8)
        semi = VGroup(MathTex(r"\sigma_1 = %.3f" % s[0], color=RED, font_size=34), MathTex(r"\sigma_2 = %.3f" % s[1], color=BLUE, font_size=34))
        semi.arrange(DOWN, buff=0.25).move_to(np.array([4.3, -0.9, 0]))
        self.play(FadeIn(semi), run_time=0.8)
        self.wait(1.5)
        self.card([["奇异值分解 A = UΣVᵀ", "Singular value decomposition A = UΣVᵀ"],
                   ["转动 → 沿互相垂直的方向伸缩 → 转动", "rotate → stretch along perpendicular directions → rotate"],
                   ["单位圆的像是椭圆，半轴长是奇异值", "the unit circle maps to an ellipse with the singular values as semi-axes"]])
