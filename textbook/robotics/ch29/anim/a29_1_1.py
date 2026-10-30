"""动画 29.1.1（配图 29.1.1）：物理引擎每一步算什么。
(1) 铰接体算法的三遍递推（平面三连杆示意）：第一遍向外传速度；第二遍从末端往里，每过一个关节，外侧的连杆可以转开，
    “推起来”的等效惯量变小（铰接体惯量）；第三遍向外求角加速度。
(2) 叠放的料箱：投影高斯-赛德尔法一遍遍地扫，接触力逼近正确值（自下而上 10、8、…、1 份重量）；每步迭代不够时，顶上的料箱慢慢下陷，
    热启动把迭代累积下去。数值与算例 29.1.3 一致：10 层、每步 10 次，冷启动 1 s 下沉约 79 mm，热启动约 0.16 mm。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("29.1", "物理引擎每一步算什么", "What a physics engine computes at every step")
        # (1) 三遍递推
        base = np.array([-5.2, -1.6, 0])
        angs, lens = [65, -35, -40], [2.0, 1.7, 1.3]
        arm = planar_arm(base, angs, lens, joint_labels=["1", "2", "3"])
        self.play(FadeIn(arm), run_time=0.8)
        pts = planar_fk(base, angs, lens)
        self.caption("已知关节角、角速度和力矩，求角加速度：这叫正动力学", "Given angles, rates and torques, find the accelerations: forward dynamics", wait=1.0)
        # 第一遍
        lab1 = zh("第一遍：向外传速度", 30, ORANGE).move_to([3.0, 2.2, 0])
        self.play(FadeIn(lab1), run_time=0.5)
        arrows = VGroup()
        for i, p in enumerate(pts[1:]):
            a = Arrow(p, p + np.array([0.35 + 0.35 * i, 0.55 + 0.25 * i, 0]), buff=0, color=C_V, stroke_width=5)
            arrows.add(a)
            self.play(GrowArrow(a), run_time=0.45)
        self.wait(0.5)
        # 第二遍
        lab2 = zh("第二遍：从末端往里，求“铰接体惯量”", 30, YELLOW).move_to([2.6, 2.2, 0])
        self.play(FadeOut(arrows), Transform(lab1, lab2), run_time=0.6)
        bars = VGroup()
        vals = [1.0, 2.1, 3.0]                     # 示意：越往里，外面挂的越多
        for k, i in enumerate(reversed(range(3))):
            p = pts[i]
            ring = Circle(radius=0.28 + 0.12 * k, color=YELLOW).move_to(p)
            b = Rectangle(width=0.35, height=vals[k], color=YELLOW, fill_opacity=0.6).move_to([2.0 + 0.7 * k, -1.8 + vals[k] / 2, 0])
            t = zh(f"𝒢ᴬ{i + 1}", 22, YELLOW).next_to(b, DOWN, buff=0.1)
            self.play(Create(ring), FadeIn(b), FadeIn(t), run_time=0.6)
            bars.add(ring, b, t)
        note = VGroup(zh("外侧的关节能转开，推起来比刚体轻：", 24), zh("𝒢ᴬᵢ = 𝒢ᵢ + Adᵀ(𝒢ᴬᵢ₊₁ − UUᵀ/D)Ad", 26, YELLOW)).arrange(DOWN, aligned_edge=LEFT).move_to([3.2, 0.9, 0])
        self.play(FadeIn(note), run_time=0.6)
        self.wait(1.2)
        # 第三遍
        lab3 = zh("第三遍：向外求角加速度", 30, RED).move_to([3.0, 2.2, 0])
        self.play(FadeOut(bars), FadeOut(note), Transform(lab1, lab3), run_time=0.6)
        for i, p in enumerate(pts[:3]):
            arc = Arc(radius=0.45, start_angle=0.3, angle=1.6, arc_center=p, color=RED, stroke_width=6).add_tip(tip_length=0.18)
            t = MathTex(r"\ddot\theta_%d" % (i + 1), color=RED, font_size=34).next_to(arc, UR, buff=0.02)
            self.play(Create(arc), FadeIn(t), run_time=0.45)
        self.caption("三遍递推，每个连杆做固定次数的运算：运算量与关节数成正比，不形成质量矩阵",
                     "Three sweeps, a fixed amount of work per link: cost grows linearly with the joints; no mass matrix", wait=2.0)
        self.clear_stage()
        # (2) 叠放的料箱
        N = 5
        boxes = VGroup(*[Rectangle(width=1.6, height=0.55, color=STEEL, fill_color=NAVY, fill_opacity=1).move_to([-4.0, -2.0 + 0.275 + 0.56 * k, 0])
                         for k in range(N)])
        self.add(Line([-5.5, -2.0, 0], [-2.5, -2.0, 0], color=GREY_B), boxes)
        self.add(zh("成品库的料箱", 24, MUTED).move_to([-4.0, 1.15, 0]))
        exact = [N - k for k in range(N)]          # 接触 k 承受上面 N − k 个料箱的重量
        lam = ValueTracker(0)
        ax = Axes(x_range=[0, N + 1, 1], y_range=[0, N + 0.5, 1], x_length=5.2, y_length=3.4, tips=False,
                  axis_config=dict(color=GREY_B, include_numbers=True, font_size=20)).move_to([2.6, -0.3, 0])
        self.play(Create(ax), run_time=0.6)
        self.add(zh("接触（自下而上）", 20, MUTED).next_to(ax, DOWN, buff=0.1), zh("力 / 份重量", 20, MUTED).next_to(ax, UP, buff=0.05).shift(LEFT * 1.6))
        for k in range(N):
            self.add(DashedLine(ax.c2p(k + 0.6, exact[k]), ax.c2p(k + 1.4, exact[k]), color=GREEN))
        # 投影高斯-赛德尔：等重料箱，A 三对角
        from numpy.linalg import solve
        A = 2 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
        A[-1, -1] = 1.0
        b = -np.ones(N)
        x = np.zeros(N)
        hist = [x.copy()]
        for it in range(40):
            for i in range(N):
                r = b[i] + A[i] @ x - A[i, i] * x[i]
                x[i] = max(0.0, -r / A[i, i])
            hist.append(x.copy())
        sol = solve(A, -b)
        sc = np.array(exact) / sol

        def bars_at(j):
            g = VGroup()
            for k in range(N):
                v = hist[j][k] * sc[k]
                g.add(Rectangle(width=0.5, height=max(ax.c2p(0, v)[1] - ax.c2p(0, 0)[1], 0.001), color=BLUE, fill_opacity=0.8)
                      .move_to(ax.c2p(k + 1, v / 2)))
            return g
        cur = bars_at(0)
        self.add(cur)
        it_lab = zh("PGS 第 0 遍", 26).move_to([4.6, 2.3, 0])
        self.add(it_lab)
        for j in (1, 2, 3, 5, 8, 12, 20, 40):
            nb = bars_at(j)
            self.play(Transform(cur, nb), Transform(it_lab, zh(f"PGS 第 {j} 遍", 26).move_to([4.6, 2.3, 0])), run_time=0.45)
        self.caption("每次只解一个接触、负的截成零：简单，但层数多了收敛很慢（迭代次数约 2.8N²）",
                     "One contact at a time, negatives clipped to zero: simple, but slow for tall stacks (about 2.8N² sweeps)", wait=1.5)
        sink = ValueTracker(0)
        self.add(always_redraw(lambda: zh(f"10 层，每步 10 次，冷启动 1 s 下沉 {sink.get_value():.0f} mm", 24, RED).move_to([-3.4, 2.3, 0])))
        self.play(sink.animate.set_value(79), boxes[-1].animate.shift(DOWN * 0.25), run_time=2.0, rate_func=linear)
        self.play(boxes[-1].animate.shift(UP * 0.25), run_time=0.6)
        self.add(zh("热启动（用上一步的解作初值）：约 0.16 mm", 24, GREEN).move_to([-3.4, 1.85, 0]))
        self.caption("迭代不够，接触力偏小，料箱就“陷”进去；热启动把每一步的迭代累积下去",
                     "Too few sweeps leave the forces too small and the box sinks; a warm start carries the iterations over", wait=2.0)
        self.card([["物理引擎的一步", "One step of a physics engine"],
                   ["正动力学：铰接体算法，三遍递推", "Forward dynamics: the articulated-body algorithm, three sweeps"],
                   MathTex(r"w = A\lambda' + b \ge 0,\quad \lambda' \ge 0,\quad w^{\mathsf T}\lambda' = 0", font_size=40),
                   ["接触：每步解一个互补问题（MuJoCo 换成软接触的凸优化）", "Contact: a complementarity problem per step (MuJoCo: a convex problem with soft contacts)"]])
