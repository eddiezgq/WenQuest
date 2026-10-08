"""动画 M2.5.1（配图 M2.5.1）：学习率、条件数与动量。
在一个狭长的碗（二次损失，条件数 κ = 20）上放三个球：学习率太小的爬得慢，最优学习率的走之字但很快到底，
超过上限的越跳越高冲出画面；最后加上动量，之字被抚平，步数从与 κ 成正比降到与 √κ 成正比。
轨迹都在动画里按 θ ← θ − η∇ℒ 现算（numpy），与算例 M2.5.1、图 M2.5.1 用的是同一套公式。"""
import numpy as np
from manim import *
from wq_anim import *

KAP = 20.0                                  # 条件数：λ₁ = 1、λ₂ = 20
LAM = np.array([1.0, KAP])
TH0 = np.array([1.0, 1.0])
SX, SY = 3.2, 1.9                           # 画面缩放：θ₁ 向右、θ₂ 向上


def run(eta, steps, beta=0.0):
    th, v = TH0.copy(), np.zeros(2)
    out = [th.copy()]
    for _ in range(steps):
        v = beta * v - eta * (LAM * th)
        th = th + v
        out.append(th.copy())
        if np.linalg.norm(th) > 6:
            break
    return np.array(out)


def pt(th):
    return [float(th[0]) * SX, float(th[1]) * SY, 0]


def path(tr, color):
    return VMobject(stroke_width=2.2, color=color).set_points_as_corners([pt(p) for p in tr])


class Lesson(Base):
    def construct(self):
        self.title("M2.5", "学习率、条件数与动量", "Learning rate, condition number, momentum")

        # 等高线：0.5(θ₁² + κθ₂²) = c 是一族椭圆，长短轴之比是 √κ
        bowl = VGroup(*[Ellipse(width=2 * np.sqrt(2 * c) * SX, height=2 * np.sqrt(2 * c / KAP) * SY,
                               stroke_width=1.1, color=GREY).move_to([0, 0, 0])
                        for c in (0.05, 0.2, 0.5, 1.0, 1.8)])
        self.play(Create(bowl), run_time=1.0)
        self.caption("损失的等高线是一族扁椭圆：长短轴之比是 $\\sqrt{\\kappa}$，这里 $\\kappa = 20$",
                     "The contours are flat ellipses: axis ratio $\\sqrt{\\kappa}$, here $\\kappa = 20$")

        eta_opt = 2 / (1 + KAP)
        slow = run(0.02, 40)
        opt = run(eta_opt, 40)
        div = run(0.13, 8)

        for tr, col, zh, en in ((slow, BLUE, f"学习率太小（$\\eta = 0.02$）：方向对，走得慢，{len(slow) - 1} 步还没到",
                                 "Too small: right direction, far too slow"),
                                (opt, GREEN, f"最优学习率（$\\eta = {eta_opt:.3f}$）：沿陡的方向来回跨，沿平的方向稳步前进",
                                 "Optimal: zig-zags across the steep direction, advances along the flat one"),
                                (div, RED, "超过上限（$2/\\lambda_{\\max} = 0.1$，这里取 $\\eta = 0.13$）：每一步都比上一步远，冲出画面",
                                 "Above $2/\\lambda_{\\max}$: every step lands further out")):
            p = path(tr, col)
            dot = Dot(pt(tr[0]), color=col, radius=0.07)
            self.play(Create(p), run_time=1.4)
            self.play(MoveAlongPath(dot, p), run_time=1.2)
            self.caption(zh, en)
            self.play(FadeOut(p), FadeOut(dot), run_time=0.4)

        beta = ((np.sqrt(KAP) - 1) / (np.sqrt(KAP) + 1)) ** 2
        mom = run(4 / (1 + np.sqrt(KAP)) ** 2, 40, beta=beta)
        p1, p2 = path(opt, GREEN), path(mom, YELLOW)
        self.play(Create(p1), Create(p2), run_time=1.6)
        self.caption(f"加动量（$\\beta = {beta:.2f}$）：来回的分量互相抵消，一致的方向越滚越快",
                     f"With momentum ($\\beta = {beta:.2f}$): the zig-zag cancels, the consistent direction builds up")

        self.card([["优化的三件事", "Three things about optimisation"],
                   MathTex(r"\eta < \frac{2}{\lambda_{\max}}", font_size=46),
                   ["超过这个学习率，必然发散", "Above this learning rate it must diverge"],
                   ["步数与条件数 $\\kappa$ 成正比；加动量后与 $\\sqrt{\\kappa}$ 成正比",
                    "Steps grow with $\\kappa$; with momentum, with $\\sqrt{\\kappa}$"]])
