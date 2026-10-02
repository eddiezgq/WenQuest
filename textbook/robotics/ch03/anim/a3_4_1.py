"""动画 3.4.1（配图 3.4.1）：椭圆（张量）和箭头 v 固定，坐标系 {b} 转动；矢量分量 v_b 与张量分量 A_b 随之变化，
转到主轴时非对角元素为零，迹与行列式始终不变。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-3.3, -0.4, 0])
K = 1.45
TH = math.radians(25)                       # 主轴方向
RP = np.array([[math.cos(TH), -math.sin(TH)], [math.sin(TH), math.cos(TH)]])
A = RP @ np.diag([1.6, 0.6]) @ RP.T          # 张量在 {a} 中的分量
V = np.array([0.35, 1.0])                    # 一支固定的箭头


def R2(t):
    return np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])


class Lesson(Base):
    def construct(self):
        self.title("3.4", "张量不动，分量在变", "The tensor stays, its components change")
        P = lambda x: O + K * np.array([x[0], x[1], 0])
        ts = np.linspace(0, 2 * math.pi, 120)
        ell = VMobject(color=YELLOW, stroke_width=4).set_points_as_corners([P(A @ np.array([math.cos(t), math.sin(t)])) for t in ts])
        circ = DashedVMobject(Circle(radius=K, color=GREY_B).move_to(O), num_dashes=40)
        axes_a = VGroup(Arrow(P([0, 0]), P([1.9, 0]), buff=0, color=RED, stroke_width=3),
                        Arrow(P([0, 0]), P([0, 1.6]), buff=0, color=GREEN, stroke_width=3),
                        MathTex(r"\hat{\boldsymbol x}_a", color=RED, font_size=26).move_to(P([2.05, -0.2])),
                        MathTex(r"\hat{\boldsymbol y}_a", color=GREEN, font_size=26).move_to(P([-0.25, 1.75]))).set_opacity(0.4)
        self.play(FadeIn(axes_a), Create(circ), run_time=0.8)
        self.play(Create(ell), run_time=1.2)
        av = Arrow(P([0, 0]), P(V), buff=0, color=WHITE, stroke_width=6)
        self.play(GrowArrow(av), Write(MathTex(r"\boldsymbol v", font_size=36).next_to(P(V), UP, buff=0.08)))
        self.caption("单位圆经张量 A 变成椭圆：椭圆就是张量本身", "The tensor A maps the unit circle to an ellipse: the ellipse is the tensor itself")
        beta = ValueTracker(0.0)

        def frame_b():
            t = beta.get_value()
            xb, yb = R2(t)[:, 0], R2(t)[:, 1]
            return VGroup(Arrow(P([0, 0]), P(1.9 * xb), buff=0, color=RED, stroke_width=5),
                          Arrow(P([0, 0]), P(1.6 * yb), buff=0, color=GREEN, stroke_width=5),
                          MathTex(r"\hat{\boldsymbol x}_b", color=RED, font_size=30).move_to(P(2.1 * xb)),
                          MathTex(r"\hat{\boldsymbol y}_b", color=GREEN, font_size=30).move_to(P(1.8 * yb)))

        def numbers():
            t = beta.get_value()
            R = R2(t)
            Ab = R.T @ A @ R
            vb = R.T @ V
            m = MathTex(r"A_b=\begin{pmatrix}%.2f & %.2f\\ %.2f & %.2f\end{pmatrix}" % (Ab[0, 0], Ab[0, 1], Ab[1, 0], Ab[1, 1]), font_size=38)
            return VGroup(MathTex(r"\beta = %d^\circ" % round(math.degrees(t)), color=YELLOW, font_size=34), m,
                          MathTex(r"v_b = (%.2f,\ %.2f)^{\mathsf T}" % (vb[0], vb[1]), font_size=34),
                          MathTex(r"\mathrm{tr}\,A_b = %.2f,\quad \det A_b = %.2f" % (np.trace(Ab), np.linalg.det(Ab)), font_size=32, color=GREY_B)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(np.array([3.5, 0.5, 0]))

        fb = always_redraw(frame_b)
        nums = always_redraw(numbers)
        self.add(fb, nums)
        self.caption("转动 {b}：矢量分量 v_b 与张量分量 A_b 都在变", "Turn {b}: both v_b and A_b change", wait=0)
        self.play(beta.animate.set_value(math.radians(-30)), run_time=3, rate_func=smooth)
        self.caption("转到椭圆的对称轴：非对角元素为零，这就是主轴", "Along the ellipse's axes the off-diagonal entries vanish: the principal axes", wait=0)
        self.play(beta.animate.set_value(TH), run_time=3, rate_func=smooth)
        self.wait(1.2)
        self.caption("迹与行列式始终不变：它们属于张量本身", "Trace and determinant never change: they belong to the tensor", wait=0)
        self.play(beta.animate.set_value(math.radians(100)), run_time=3.5, rate_func=smooth)
        self.wait(0.5)
        self.card([["二阶张量的变换规律", "How a second-order tensor transforms"],
                   MathTex(r"A_a = R_{ab}\,A_b\,R_{ab}^{\mathsf T},\qquad A_b = R_{ab}^{\mathsf T}A_aR_{ab}", font_size=44),
                   ["迹、行列式、特征值不变；主轴上矩阵为对角", "Trace, determinant, eigenvalues invariant; diagonal on the principal axes"]])
