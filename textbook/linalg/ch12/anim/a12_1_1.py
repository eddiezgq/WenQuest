"""动画 12.1.1：换一把尺子——一般内积。W = [[2, 1], [1, 2]]，⟨x, y⟩_W = xᵀWy。u = (1, 0)、v = (−1, 2) 的点积为 −1，
看上去不垂直；但 ⟨u, v⟩_W = 0。W 内积下的“圆” xᵀWx = 2 是一个斜椭圆，v 恰好沿椭圆在 u 处的切线。
写 W = RᵀR（乔列斯基分解），换坐标 y = Rx：整个平面被拉伸，椭圆变成圆，u、v 变成互相垂直——一般的内积就是换了坐标的点积。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("12.1", "换一把尺子：一般的内积", "A different ruler: general inner products")
        s = 0.95
        O = np.array([0.0, -0.45, 0.0])
        P = lambda x: O + s * np.array([x[0], x[1], 0.0])
        W = np.array([[2.0, 1.0], [1.0, 2.0]])
        R = np.linalg.cholesky(W).T                       # W = RᵀR，R 上三角
        mk = lambda: NumberPlane(x_range=[-4, 4, 1], y_range=[-3, 3, 1], x_length=8 * s, y_length=6 * s,
                                 background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.6}).move_to(O)
        plane = mk()
        self.play(Create(plane), run_time=1.2)
        u, v = np.array([1.0, 0.0]), np.array([-1.0, 2.0])

        def arr(x, col):
            return Arrow(P((0, 0)), P(x), buff=0, color=col, stroke_width=6, max_tip_length_to_length_ratio=0.18)

        U, V = arr(u, RED), arr(v, GREEN)
        Ul = MathTex(r"\boldsymbol u", color=RED, font_size=38).next_to(P(u), DR, buff=0.12)
        Vl = MathTex(r"\boldsymbol v", color=GREEN, font_size=38).next_to(P(v), LEFT, buff=0.12)
        self.play(GrowArrow(U), GrowArrow(V), FadeIn(Ul), FadeIn(Vl))
        self.caption("用点积量：u·v = −1，u 与 v 不垂直", "Measured with the dot product: u·v = −1, not perpendicular", wait=1.0)
        t = np.linspace(0, 2 * np.pi, 241)
        # xᵀWx = 2：x = √2 R⁻¹(cos t, sin t)
        Ri = np.linalg.inv(R)
        pts = [P(np.sqrt(2) * Ri @ np.array([np.cos(a), np.sin(a)])) for a in t]
        ell = VMobject(color=GOLD, stroke_width=4).set_points_smoothly(pts)
        self.play(Create(ell), run_time=1.5)
        self.caption("换一把尺子，用 xᵀWy 代替点积：到原点“距离相等”的点组成斜椭圆", "A new ruler, xᵀWy instead of the dot product: points at equal 'distance' form a tilted ellipse", wait=1.2)
        tan = DashedLine(P(u - 0.9 * v), P(u + 0.9 * v), color=GREEN_B, stroke_width=3)
        self.play(Create(tan))
        self.caption("v 恰好沿椭圆在 u 处的切线方向：uᵀWv = 0，在这把尺子下它们垂直", "v runs along the ellipse's tangent at u: uᵀWv = 0, perpendicular under this ruler", wait=1.4)
        board = MathTex(r"W = \begin{pmatrix}2 & 1\\ 1 & 2\end{pmatrix} = R^{\mathsf T}R", font_size=34).to_corner(UR, buff=0.5).shift(DOWN * 0.9)
        self.play(FadeIn(board))
        self.caption("把 W 分解成 RᵀR，换坐标 y = Rx", "Factor W = RᵀR and change coordinates, y = Rx", wait=0.6)
        A3 = np.eye(3)
        A3[:2, :2] = R
        U2, V2 = arr(R @ u, RED), arr(R @ v, GREEN)
        Ul2 = MathTex(r"R\boldsymbol u", color=RED, font_size=38).next_to(P(R @ u), DOWN, buff=0.12)
        Vl2 = MathTex(r"R\boldsymbol v", color=GREEN, font_size=38).next_to(P(R @ v), LEFT, buff=0.12)
        circ = Circle(radius=np.sqrt(2) * s, color=GOLD, stroke_width=4).move_to(O)
        tan2 = DashedLine(P(R @ (u - 0.9 * v)), P(R @ (u + 0.9 * v)), color=GREEN_B, stroke_width=3)
        self.play(ApplyMatrix(A3, plane, about_point=O), ReplacementTransform(ell, circ), ReplacementTransform(U, U2), ReplacementTransform(V, V2),
                  ReplacementTransform(Ul, Ul2), ReplacementTransform(Vl, Vl2), ReplacementTransform(tan, tan2), run_time=2.5)
        self.play(ReplacementTransform(plane, mk()), run_time=0.8)
        sq = 0.22
        e1, e2 = (R @ u) / np.linalg.norm(R @ u), (R @ v) / np.linalg.norm(R @ v)
        mark = VMobject(color=WHITE, stroke_width=2).set_points_as_corners([P(sq * e1), P(sq * (e1 + e2)), P(sq * e2)])
        self.play(Create(mark))
        self.caption("新坐标里椭圆变成圆，Ru 与 Rv 真的垂直：(Ru)·(Rv) = uᵀWv = 0", "In the new coordinates the ellipse is a circle and Ru ⟂ Rv: (Ru)·(Rv) = uᵀWv = 0", wait=1.6)
        self.card([["内积 = 对称、线性、正定的“点积”", "An inner product: a symmetric, linear, positive definite 'dot product'"],
                   ["⟨x, y⟩ = xᵀWy，W 对称正定", "⟨x, y⟩ = xᵀWy with W symmetric positive definite"],
                   ["W = RᵀR：它就是坐标 Rx 下的点积", "W = RᵀR: it is the dot product in the coordinates Rx"]])
