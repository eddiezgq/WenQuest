"""动画 8.4.1（配图 8.4.3）：AGV 在两段凸走廊中的路径。障碍函数法：t 小时，对数障碍让航点远离边界；
t 逐渐增大，“中心路径”上的点一步步逼近真正的最优路径，对偶间隙 m/t 同时缩小。"""
from manim import *
from wq_anim import *
import numpy as np
import math

U = 1.15                              # 1 m 画成 1.15 个单位
O = np.array([-5.6, -2.6, 0])
START, GOAL = np.array([0.5, 0.9]), np.array([5.3, 3.5])
NW, KX = 10, 5


def P(v):
    return O + U * np.array([v[0], v[1], 0])


def halfplanes(Pts):
    A, b = [], []
    for i in range(len(Pts)):
        p, q = np.array(Pts[i], float), np.array(Pts[(i + 1) % len(Pts)], float)
        t = q - p
        n = np.array([t[1], -t[0]]) / np.linalg.norm(t)
        A.append(n)
        b.append(n @ p)
    return np.array(A), np.array(b)


def problem():
    A1, b1 = halfplanes([(0, 0), (6, 0), (6, 1.2), (0, 1.8)])
    A2, b2 = halfplanes([(4.6, 0), (6, 0), (6, 4), (4.6, 4)])
    nv = 2 * (NW - 1)
    rows, rhs = [], []
    for i in range(1, NW):
        regs = ([(A1, b1)] if i <= KX else []) + ([(A2, b2)] if i >= KX else [])
        for Aa, bb in regs:
            for a_, b_ in zip(Aa, bb):
                r = np.zeros(nv)
                r[2 * (i - 1):2 * i] = a_
                rows.append(r)
                rhs.append(b_)
    D, dv = np.zeros((2 * NW, nv)), np.zeros(2 * NW)
    for i in range(NW):
        for k in range(2):
            if i + 1 <= NW - 1:
                D[2 * i + k, 2 * i + k] += 1
            else:
                dv[2 * i + k] += GOAL[k]
            if i >= 1:
                D[2 * i + k, 2 * (i - 1) + k] -= 1
            else:
                dv[2 * i + k] -= START[k]
    return 2 * D.T @ D, 2 * D.T @ dv, np.array(rows), np.array(rhs)


def central_points(ts):
    Q, c, A, b = problem()
    x = np.array([START + (np.array([5.3, 0.9]) - START) * i / KX if i <= KX else
                  np.array([5.3, 0.9 + (GOAL[1] - 0.9) * (i - KX) / (NW - KX)]) for i in range(1, NW)]).ravel()
    out = []
    for t in ts:
        for _ in range(100):
            s = b - A @ x
            g = t * (Q @ x + c) + A.T @ (1 / s)
            H = t * Q + A.T @ (A / (s ** 2)[:, None])
            dx = np.linalg.solve(H, -g)
            dec = float(-g @ dx)
            if dec < 1e-10:
                break
            a = 1.0
            while np.min(b - A @ (x + a * dx)) <= 0:
                a *= 0.5
            phi = lambda z: t * (0.5 * z @ Q @ z + c @ z) - np.sum(np.log(b - A @ z))
            while phi(x + a * dx) > phi(x) - 0.25 * a * dec:
                a *= 0.5
            x = x + a * dx
        out.append(np.vstack([START, x.reshape(-1, 2), GOAL]))
    return out, len(b)


class Lesson(Base):
    def construct(self):
        self.title("8.4", "障碍函数法的中心路径", "The central path of the barrier method")
        floor = Polygon(P([0, 0]), P([6, 0]), P([6, 4]), P([0, 4]), color=GREY_D, fill_color="#2a2620", fill_opacity=1, stroke_width=1)
        shelf = Polygon(P([0, 1.8]), P([4.6, 1.34]), P([4.6, 4]), P([0, 4]), color=GREY_B, fill_color="#6b6253", fill_opacity=1, stroke_width=1)
        sl = bi(["货架（障碍）", "shelves (obstacle)"], 22, WHITE).move_to(P([2.2, 3.0]))
        r1 = Polygon(P([0, 0]), P([6, 0]), P([6, 1.2]), P([0, 1.8]), color=BLUE_C, fill_opacity=0.18, stroke_width=3)
        r2 = Polygon(P([4.6, 0]), P([6, 0]), P([6, 4]), P([4.6, 4]), color=PURPLE_B, fill_opacity=0.18, stroke_width=3)
        l1 = MathTex("R_1", color=BLUE_C, font_size=30).move_to(P([0.35, 0.25]))
        l2 = MathTex("R_2", color=PURPLE_B, font_size=30).move_to(P([5.75, 3.75]))
        self.play(FadeIn(floor), FadeIn(shelf), FadeIn(sl))
        self.play(Create(r1), Create(r2), FadeIn(l1), FadeIn(l2))
        self.caption("可通行区域不是凸的；把它拆成两个凸区域 R₁、R₂", "The free space is not convex; split it into two convex regions R₁ and R₂")
        ends = VGroup(Square(0.18, color=WHITE, fill_opacity=1).move_to(P(START)), Star(n=5, outer_radius=0.15, color=WHITE, fill_opacity=1).move_to(P(GOAL)))
        self.play(FadeIn(ends))
        self.caption("航点 x₁…x₅ 在 R₁ 中，x₅…x₉ 在 R₂ 中：相邻航点间的线段一定可通行", "Waypoints x₁…x₅ lie in R₁, x₅…x₉ in R₂: every segment is then collision-free")
        ts = list(np.geomspace(0.3, 3e4, 26))
        paths, m = central_points(ts)
        k = ValueTracker(0.0)

        def path_at():
            u = k.get_value()
            i = min(int(u), len(paths) - 2)
            s = u - i
            Pk = (1 - s) * paths[i] + s * paths[i + 1]
            g = VGroup(VMobject(color=YELLOW, stroke_width=4).set_points_as_corners([P(p) for p in Pk]))
            for p in Pk[1:-1]:
                g.add(Dot(P(p), color=YELLOW, radius=0.06))
            return g

        def panel():
            u = k.get_value()
            i = min(int(u), len(ts) - 2)
            s = u - i
            t = math.exp((1 - s) * math.log(ts[i]) + s * math.log(ts[i + 1]))
            return VGroup(MathTex(r"t = %s" % (("%.1f" % t) if t < 100 else ("%.0f" % t)), font_size=32),
                          MathTex(r"m/t = %.2g" % (m / t), font_size=32, color=YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(np.array([5.4, 1.2, 0]))

        pa = always_redraw(path_at)
        pn = always_redraw(panel)
        self.play(FadeIn(pa), FadeIn(pn))
        self.caption("t 小：对数障碍把航点推离所有边界", "Small t: the log barrier keeps the waypoints away from every edge", wait=1.0)
        self.caption("t 增大：路径沿中心路径滑向最优解，贴住拐角", "Growing t: the path slides along the central path and hugs the corner", wait=0)
        self.play(k.animate.set_value(len(paths) - 1.001), run_time=7, rate_func=linear)
        self.wait(0.8)
        self.caption("最优路径：起点—拐角—终点两段直线；离最优值不超过 m/t", "The optimum: two straight legs via the corner; within m/t of the optimal value")
        self.wait(1)
        self.card([["障碍函数法", "The barrier method"],
                   MathTex(r"\min_x\ t\,f(x) - \sum_{i=1}^{m}\log\big(b_i - a_i^{\mathsf T}x\big),\qquad f(x^*(t)) - p^* \le \frac{m}{t}", font_size=40),
                   ["凸问题：局部最优就是全局最优，算法有收敛保证", "a convex problem: every local optimum is global, and the method is guaranteed to converge"]])
