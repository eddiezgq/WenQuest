"""动画 26.2.1（配图 26.2.2）：激励得好不好，决定参数估得准不准。用一个最简单的例子：单个转动关节带一根摆杆（示意值），
τ = J θ̈ + mgl sin θ，两个待辨识的参数 J = 0.5 kg·m²、mgl = 10 N·m，力矩的测量噪声 σ = 0.5 N·m，每 0.02 s 一个数据。
左：小幅慢摆 θ = 0.1 sin 2t（sin θ ≈ θ，θ̈ ≈ −4θ，两列几乎成比例）；右：大幅、两种频率叠加的运动 θ = 1.2 sin 1.3t + 0.5 sin 4.1t。
下方是两个参数的最小二乘估计（点）和 95% 置信椭圆 σ²(XᵀX)⁻¹（χ² = 5.99），随数据增加而变化；十字是真值。"""
from manim import *
from wq_anim import *
import numpy as np
import math

J, MGL, SIG = 0.5, 10.0, 0.5
DT = 0.02
rng = np.random.default_rng(1)


def motion(kind, t):
    if kind == 0:
        return 0.1 * math.sin(2 * t), -0.4 * math.sin(2 * t)
    q = 1.2 * math.sin(1.3 * t) + 0.5 * math.sin(4.1 * t)
    a = -1.2 * 1.69 * math.sin(1.3 * t) - 0.5 * 16.81 * math.sin(4.1 * t)
    return q, a


def data(kind, N):
    X, y = [], []
    for k in range(N):
        q, a = motion(kind, k * DT)
        X.append([a, math.sin(q)])
        y.append(J * a + MGL * math.sin(q) + rng.normal(0, SIG))
    return np.array(X), np.array(y)


NMAX = 500
D = [data(0, NMAX), data(1, NMAX)]


def estimate(kind, n):
    X, y = D[kind][0][:n], D[kind][1][:n]
    A = X.T @ X
    p = np.linalg.solve(A, X.T @ y)
    return p, SIG ** 2 * np.linalg.inv(A)


class Lesson(Base):
    def construct(self):
        self.title("26.2", "激励轨迹：动得“丰富”，参数才估得准", "Excitation: rich motion gives accurate parameters")
        centers = [np.array([-3.4, 1.35, 0]), np.array([3.4, 1.35, 0])]
        heads = [["小幅慢摆", "small, slow swing"], ["大幅、两种频率", "large, two frequencies"]]
        for c, hd in zip(centers, heads):
            self.add(bi(hd, 20, INK).move_to(c + UP * 0.8 + (LEFT if c[0] < 0 else RIGHT) * 1.6))
            self.add(Dot(c, radius=0.07, color=WHITE))
        # 参数平面：J 横轴 0.3～0.7，mgl 纵轴 8～12
        boxes = [np.array([-3.4, -1.05, 0]), np.array([3.4, -1.05, 0])]
        W, H = 4.0, 1.9
        for b in boxes:
            self.add(Rectangle(width=W, height=H, color=GREY_B, stroke_width=1.5).move_to(b))
            self.add(MathTex("J", font_size=26, color=MUTED).next_to(b + RIGHT * W / 2 + DOWN * H / 2, RIGHT, buff=0.08))
            self.add(MathTex("mgl", font_size=26, color=MUTED).next_to(b + LEFT * W / 2 + UP * H / 2, UP, buff=0.05))
            tx = b + np.array([(J - 0.5) / 0.4 * W, (MGL - 10) / 4 * H, 0])
            self.add(Line(tx + LEFT * 0.15, tx + RIGHT * 0.15, color=YELLOW, stroke_width=3),
                     Line(tx + DOWN * 0.15, tx + UP * 0.15, color=YELLOW, stroke_width=3))
        tk = ValueTracker(2)

        def to_box(b, p):
            return b + np.array([(p[0] - 0.5) / 0.4 * W, (p[1] - 10) / 4 * H, 0])

        def scene():
            n = int(tk.get_value())
            g = VGroup()
            for kind in (0, 1):
                q, _ = motion(kind, (n - 1) * DT)
                c = centers[kind]
                tip = c + 0.85 * np.array([math.sin(q), -math.cos(q), 0])
                g.add(Line(c, tip, color=STEEL, stroke_width=8), Dot(tip, radius=0.12, color="#d29922"))
                if n >= 3:
                    p, Cv = estimate(kind, n)
                    w, V = np.linalg.eigh(Cv)
                    pts = []
                    for a in np.linspace(0, 2 * math.pi, 60):
                        d = V @ (np.sqrt(5.99 * np.maximum(w, 0)) * np.array([math.cos(a), math.sin(a)]))
                        pp = to_box(boxes[kind], p + d)
                        pp[0] = min(max(pp[0], boxes[kind][0] - W / 2), boxes[kind][0] + W / 2)
                        pp[1] = min(max(pp[1], boxes[kind][1] - H / 2), boxes[kind][1] + H / 2)
                        pts.append(pp)
                    g.add(Polygon(*pts, color=BLUE, stroke_width=2, fill_color=BLUE, fill_opacity=0.15))
                    e = to_box(boxes[kind], p)
                    e[0] = min(max(e[0], boxes[kind][0] - W / 2), boxes[kind][0] + W / 2)
                    e[1] = min(max(e[1], boxes[kind][1] - H / 2), boxes[kind][1] + H / 2)
                    g.add(Dot(e, radius=0.07, color=RED))
                    g.add(zh(f"J = {p[0]:.3f}   mgl = {p[1]:.2f}", 18, INK).move_to(boxes[kind] + UP * (H / 2 + 0.22)))
            g.add(zh(f"数据 {n} 个（{n * DT:.1f} s）", 20, MUTED).move_to([0, 0.6, 0]))
            return g

        self.add(always_redraw(scene))
        self.caption("同样的噪声、同样多的数据：左边的置信椭圆又细又长，右边很快缩成一个小圆",
                     "Same noise, same amount of data: the left ellipse stays long and thin, the right one quickly shrinks to a small disc", wait=0)
        self.play(tk.animate.set_value(NMAX), run_time=9, rate_func=linear)
        self.wait(0.8)
        self.caption("小幅慢摆时 θ̈ ≈ −4θ ≈ −4 sin θ：两列几乎成比例，只能定出 mgl − 4J 这个组合",
                     "In the small slow swing θ̈ ≈ −4θ ≈ −4 sin θ: the two columns are nearly proportional, so only mgl − 4J is pinned down", wait=2.5)
        X0, X1 = D[0][0], D[1][0]
        c0, c1 = np.linalg.cond(X0), np.linalg.cond(X1)
        self.caption(f"回归矩阵的条件数：左边约 {c0:.0f}，右边约 {c1:.1f}。激励轨迹设计就是让条件数尽量小",
                     f"Condition numbers of the regressors: about {c0:.0f} on the left, {c1:.1f} on the right. Exciting-trajectory design makes it small", wait=2.5)
        self.card([["激励轨迹", "Exciting trajectories"],
                   MathTex(r"\tau = Y(\theta,\dot\theta,\ddot\theta)\,\pi,\qquad \mathrm{Cov}(\hat\pi) = \sigma^2 (W^{\mathsf T}W)^{-1}", font_size=40),
                   ["动得“丰富”：各列不成比例，条件数小", "Rich motion: columns not proportional, small condition number"],
                   ["同样的噪声，置信区域小得多", "Same noise, a much smaller confidence region"]])
