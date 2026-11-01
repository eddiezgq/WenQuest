"""动画 16.3.1：相平面上的轨线。二阶线性系统 u' = Au 的四种典型相图：稳定结点（λ = −4, −2）、鞍点（λ = −1, 3）、
稳定焦点（λ = −1 ± 4i）、中心（λ = ±2i）。每种情形从一圈初始点出发同时画出轨线，小圆点沿轨线运动；
实特征值时画出两条特征直线。稳定性只看特征值的实部：都小于 0 就趋于原点。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("16.3", "相平面上的轨线：结点、鞍点、焦点、中心", "Phase portraits: node, saddle, focus, center")
        s = 1.25
        O = np.array([-2.6, -0.5, 0.0])
        L = 2.0
        plane = NumberPlane(x_range=[-L, L, 1], y_range=[-L, L, 1], x_length=2 * L * s, y_length=2 * L * s,
                            background_line_style={"stroke_color": BLUE_E, "stroke_width": 1, "stroke_opacity": 0.5}).move_to(O)
        self.play(Create(plane), run_time=0.8)
        P = lambda x, y: O + s * np.array([x, y, 0.0])
        cases = [
            (np.array([[-3.0, 1], [1, -3]]), r"\lambda = -4,\ -2", "稳定结点：两个负实特征值，轨线直接趋于原点，最后贴着慢的特征方向",
             "Stable node: two negative real eigenvalues; paths go straight in, finally along the slow eigenvector", GREEN, True),
            (np.array([[1.0, 2], [2, 1]]), r"\lambda = -1,\ 3", "鞍点：一正一负，只有沿稳定特征方向进来的轨线趋于原点，其余都被甩出去",
             "Saddle: one positive, one negative; only paths on the stable eigenvector reach the origin", RED, False),
            (np.array([[-1.0, 4], [-4, -1]]), r"\lambda = -1 \pm 4\mathrm i", "稳定焦点：复特征值，实部 −1 < 0，转着圈（角速度 4）收进原点",
             "Stable focus: complex eigenvalues with real part −1 < 0; paths spiral in, turning at rate 4", GREEN, True),
            (np.array([[0.0, 2], [-2, 0]]), r"\lambda = \pm 2\mathrm i", "中心：纯虚特征值，实部为 0，轨线是闭合的椭圆，既不收敛也不发散",
             "Center: purely imaginary eigenvalues; closed orbits that neither shrink nor grow", YELLOW, None),
        ]
        prev = VGroup()
        for A, ev, zh_t, en_t, col, stable in cases:
            board = VGroup(MathTex(r"A=\begin{pmatrix}%g & %g\\ %g & %g\end{pmatrix}" % (A[0, 0], A[0, 1], A[1, 0], A[1, 1]), font_size=40),
                           MathTex(ev, font_size=40, color=col),
                           MathTex(r"\operatorname{tr}A = %g,\ \ \det A = %g" % (np.trace(A), round(np.linalg.det(A), 6)), font_size=34)
                           ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to([3.4, 0.2, 0])
            paths, dots = VGroup(), VGroup()
            if stable is False:
                sd, ud = np.array([1.0, -1.0]) / np.sqrt(2), np.array([1.0, 1.0]) / np.sqrt(2)   # 稳定、不稳定特征方向
                starts = [e * 2.6 * sd + o * ud for e in (1, -1) for o in (-0.6, -0.25, -0.06, 0.0, 0.06, 0.25, 0.6)]
            elif stable is None:
                starts = [np.array([r, 0.0]) for r in (0.5, 0.9, 1.3, 1.7)]
            else:
                starts = [1.9 * np.array([np.cos(t), np.sin(t)]) for t in np.linspace(0, 2 * np.pi, 13)[:-1]]
            for p0 in starts:
                lam, X = np.linalg.eig(A.astype(complex))      # 四个矩阵都可对角化：u(t) = X e^{Λt} X⁻¹ u₀
                c = np.linalg.solve(X, p0.astype(complex))
                ts = np.linspace(0, 4 if stable is not None else np.pi, 400)
                pts = np.array([(X @ (np.exp(lam * t) * c)).real for t in ts])
                pts = pts[(np.abs(pts) <= L).all(1)]
                if len(pts) < 3:
                    continue
                m = VMobject(color=col, stroke_width=3).set_points_smoothly([P(*q) for q in pts[::3]])
                paths.add(m)
                dots.add(Dot(P(*pts[0]), radius=0.06, color=WHITE))
            lines = VGroup()
            if np.all(np.abs(np.linalg.eigvals(A).imag) < 1e-12):
                w, V = np.linalg.eig(A)
                for j in range(2):
                    v = V[:, j] / np.linalg.norm(V[:, j])
                    lines.add(DashedLine(P(*(-L * 0.98 * v)), P(*(L * 0.98 * v)), color=GOLD, stroke_width=2))
            self.play(FadeOut(prev), FadeIn(board), Create(lines), run_time=0.8)
            self.play(*[Create(m) for m in paths], *[MoveAlongPath(d, m) for d, m in zip(dots, paths)], run_time=3.2, rate_func=linear)
            self.caption(zh_t, en_t, wait=1.6)
            prev = VGroup(board, paths, dots, lines)
        self.play(FadeOut(prev), run_time=0.6)
        self.caption("稳定 ⇔ 所有特征值的实部都小于 0；二阶时等价于 tr A < 0 且 det A > 0",
                     "Stable ⇔ every eigenvalue has negative real part; for 2×2: tr A < 0 and det A > 0", wait=1.5)
        self.card([["稳定性只看特征值的实部", "Stability depends only on the real parts of the eigenvalues"],
                   ["实特征值：结点或鞍点；复特征值：焦点或中心", "Real eigenvalues: node or saddle; complex: focus or center"],
                   ["Re λ < 0 收敛，Re λ > 0 发散，Re λ = 0（可对角化时）闭合", "Re λ < 0 converges, Re λ > 0 diverges, Re λ = 0 (diagonalizable) closes"]])
