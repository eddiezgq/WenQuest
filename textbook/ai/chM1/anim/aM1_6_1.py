"""动画 M1.6.1（配图 M1.6.1）：任何矩阵都把单位圆变成椭圆。
一个 2×2 的矩阵作用在单位圆上，画面上分三步看清它做了什么：先转一下（Vᵀ），再沿两个坐标轴各拉伸一次（Σ），
再转一下（U）。椭圆的两个半轴长就是两个奇异值 σ₁、σ₂，它们的比值就是这个矩阵的条件数。
矩阵与奇异值都在动画里现算（numpy），与算例 M1.6.1 用的是同一套公式。"""
import numpy as np
from manim import *
from wq_anim import *

A = np.array([[1.6, 0.9], [0.2, 1.1]])
U, S, Vt = np.linalg.svd(A)
V = Vt.T
SCALE = 1.5                                   # 画面单位：1 → 1.5


def curve(M, color=BLUE):
    t = np.linspace(0, 2 * np.pi, 241)
    pts = M @ np.c_[np.cos(t), np.sin(t)].T
    return VMobject(stroke_width=2.4, color=color).set_points_as_corners(
        [[float(x) * SCALE, float(y) * SCALE, 0] for x, y in pts.T])


def arrow(M, k, color):
    q = M @ V[:, k]
    return Arrow([0, 0, 0], [float(q[0]) * SCALE, float(q[1]) * SCALE, 0], buff=0, color=color, stroke_width=4)


class Lesson(Base):
    def construct(self):
        self.title("M1.6", "矩阵把圆变成椭圆", "A matrix turns the circle into an ellipse")

        axes = VGroup(Line([-4.2, 0, 0], [4.2, 0, 0], stroke_width=1.2, color=GREY),
                      Line([0, -2.6, 0], [0, 2.6, 0], stroke_width=1.2, color=GREY))
        self.play(Create(axes), run_time=0.6)

        shape = curve(np.eye(2))
        a1, a2 = arrow(np.eye(2), 0, RED), arrow(np.eye(2), 1, YELLOW)
        self.play(Create(shape), GrowArrow(a1), GrowArrow(a2), run_time=1.0)
        self.caption("先看单位圆，再看圆上两个互相垂直的方向（$V$ 的两列）",
                     "Start from the unit circle and two orthogonal directions (the columns of $V$)")

        for M, zh, en in ((Vt, "第一步 $V^{\\mathsf T}$：把这两个方向转到坐标轴上",
                           "Step 1, $V^{\\mathsf T}$: rotate those directions onto the axes"),
                          (np.diag(S) @ Vt, f"第二步 $\\Sigma$：沿两个坐标轴分别拉伸 {S[0]:.2f} 倍与 {S[1]:.2f} 倍",
                           f"Step 2, $\\Sigma$: stretch by {S[0]:.2f} and {S[1]:.2f} along the axes"),
                          (A, "第三步 $U$：再转一下，就是 $A$ 作用后的样子",
                           "Step 3, $U$: one more rotation — this is what $A$ does")):
            self.play(Transform(shape, curve(M)), Transform(a1, arrow(M, 0, RED)),
                      Transform(a2, arrow(M, 1, YELLOW)), run_time=1.3)
            self.caption(zh, en)

        self.caption(f"椭圆的两个半轴就是奇异值：$\\sigma_1 = {S[0]:.2f}$、$\\sigma_2 = {S[1]:.2f}$；"
                     f"它们的比 {S[0] / S[1]:.2f} 就是这个矩阵的条件数",
                     f"The semi-axes are the singular values $\\sigma_1 = {S[0]:.2f}$, $\\sigma_2 = {S[1]:.2f}$; "
                     f"their ratio {S[0] / S[1]:.2f} is the condition number")
        self.card([["奇异值分解", "Singular value decomposition"],
                   MathTex(r"A = U\Sigma V^{\mathsf T}", font_size=44),
                   ["任何矩阵：先转、再沿几个方向拉伸、再转", "Any matrix: rotate, stretch along axes, rotate"],
                   ["最大与最小的拉伸之比就是条件数", "The ratio of largest to smallest stretch is the condition number"]])
