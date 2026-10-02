"""动画 8.3.1（配图 8.3.1）：二次规划 min ½‖JΔ − e‖²，|Δ_i| ≤ 0.1 rad 的有效集法。
从 Δ = 0 出发朝无约束的最小点走，撞上边界 Δ₂ = −0.1 后把它加入工作集，沿边界找到最小点；
最后检查 KKT 条件：−∇q 沿起作用约束的外法向，乘子 μ ≥ 0。再与“截断”的做法比较。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
TH = np.array([0.0, math.pi / 2])
PD = np.array([0.5, 0.4])
U = 13.0                                  # 1 rad 画成 13 个单位
O = np.array([-2.4, 0.6, 0])


def P(v):
    return O + U * np.array([v[0], v[1], 0])


def sci(e):
    m, x = ("%.2e" % e).split("e")
    return r"%s\times 10^{%d}" % (m, int(x))


def setup():
    t1, t12 = TH[0], TH[0] + TH[1]
    J = np.array([[-L1 * math.sin(t1) - L2 * math.sin(t12), -L2 * math.sin(t12)], [L1 * math.cos(t1) + L2 * math.cos(t12), L2 * math.cos(t12)]])
    tip = np.array([L1 * math.cos(t1) + L2 * math.cos(t12), L1 * math.sin(t1) + L2 * math.sin(t12)])
    e = PD - tip
    return J.T @ J, -J.T @ e, np.linalg.solve(J, e)


class Lesson(Base):
    def construct(self):
        self.title("8.3", "有效集法与 KKT 条件", "The active-set method and the KKT conditions")
        Q, c, dfree = setup()
        q = lambda d: 0.5 * d @ Q @ d + c @ d
        qmin = q(dfree)
        lam, V = np.linalg.eigh(Q)
        ell = VGroup()
        for lv in (2e-5, 1e-4, 2.5e-4, 5e-4):
            pts = [P(dfree + V @ (np.array([math.cos(a), math.sin(a)]) * np.sqrt(2 * lv / lam))) for a in np.linspace(0, 2 * math.pi, 90)]
            ell.add(VMobject(color=GREY_B, stroke_width=2).set_points_smoothly(pts))
        sq = Polygon(P([-0.1, -0.1]), P([0.1, -0.1]), P([0.1, 0.1]), P([-0.1, 0.1]), color=BLUE_C, fill_color=BLUE_E, fill_opacity=0.35, stroke_width=3)
        sql = bi(["可行域 |Δᵢ| ≤ 0.1 rad", "feasible set |Δᵢ| ≤ 0.1 rad"], 22, BLUE_C).next_to(sq, UP, buff=0.1)
        self.play(FadeIn(sq), FadeIn(sql), Create(ell), run_time=1.5)
        free = Dot(P(dfree), color=WHITE, radius=0.08)
        fl = bi(["无约束的最小点", "unconstrained minimum"], 20, WHITE).next_to(free, RIGHT, buff=0.15)
        self.play(FadeIn(free), FadeIn(fl))
        self.caption("椭圆是 q(Δ) 的等高线；无约束的最小点在可行域外", "Ellipses: level curves of q(Δ); the unconstrained minimum lies outside", wait=1.2)

        x0 = np.zeros(2)
        a = 0.1 / abs(dfree[1])
        x1 = a * dfree
        d1 = -(Q[0, 1] * (-0.1) + c[0]) / Q[0, 0]
        x2 = np.array([d1, -0.1])
        dot = Dot(P(x0), color=ORANGE, radius=0.08)
        self.play(FadeIn(dot))
        self.caption("第 1 步：工作集为空，朝无约束最小点走", "Step 1: empty working set; head for the unconstrained minimum", wait=0)
        self.play(dot.animate.move_to(P(x1)), Create(DashedLine(P(x0), P(x1), color=ORANGE)), run_time=1.5)
        edge = Line(P([-0.1, -0.1]), P([0.1, -0.1]), color=RED, stroke_width=7)
        self.play(Create(edge))
        self.caption("撞上边界 Δ₂ = −0.1：把这条约束加入工作集", "Blocked by Δ₂ = −0.1: add this constraint to the working set")
        self.caption("第 2 步：只在这条边上找 q 的最小点", "Step 2: minimise q along this edge only", wait=0)
        self.play(dot.animate.move_to(P(x2)), run_time=1.5)
        g = Q @ x2 + c
        mu = g[1]
        star = Star(n=5, outer_radius=0.17, color=RED, fill_opacity=1).move_to(P(x2))
        self.play(FadeIn(star))
        ng = -g / np.linalg.norm(g) * 0.075
        arr = Arrow(P(x2), P(x2 + ng), buff=0, color=YELLOW, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        al = MathTex(r"-\nabla q = \mu_4\,a_4", color=YELLOW, font_size=32).next_to(arr, LEFT, buff=0.15)
        self.play(GrowArrow(arr), Write(al))
        kkt = VGroup(MathTex(r"\mu_4 = %.4f \ge 0" % mu, font_size=32, color=YELLOW),
                     MathTex(r"a_4 = (0, -1)^{\mathsf T}", font_size=30)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(np.array([4.2, 1.6, 0]))
        self.play(FadeIn(kkt))
        self.caption("KKT：−∇q 沿起作用约束的外法向，乘子非负——再往外推就离开可行域", "KKT: −∇q points along the outward normal, μ ≥ 0: going further would leave the feasible set")
        clip = np.clip(dfree, -0.1, 0.1)
        cd = Square(0.16, color=ORANGE, fill_opacity=1).move_to(P(clip))
        cmp = VGroup(MathTex(r"q(\Delta^*) - q_{\min} = %s" % sci(q(x2) - qmin), font_size=28, color=RED),
                     MathTex(r"q(\Delta_{\rm clip}) - q_{\min} = %s" % sci(q(clip) - qmin), font_size=28, color=ORANGE)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(kkt, DOWN, buff=0.5)
        self.play(FadeIn(cd), FadeIn(cmp))
        self.caption("只把超限的分量截断（橙色方块）不是最优：二次规划还会让关节 1 反向补偿", "Clipping (orange square) is not optimal: the QP also turns joint 1 back to compensate")
        self.wait(1)
        self.card([["KKT 条件", "The KKT conditions"],
                   MathTex(r"\nabla q(x^*) + \sum_i \mu_i a_i = 0,\quad \mu_i \ge 0,\quad \mu_i\,(a_i^{\mathsf T}x^* - b_i) = 0", font_size=40),
                   ["只有起作用的约束有正的乘子", "only active constraints carry positive multipliers"]])
