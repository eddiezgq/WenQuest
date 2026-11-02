"""动画 22.3.1：消元与填充。一个“星形”稀疏矩阵：中心节点（AGV 调度中心）与 6 个工位相连，工位之间不相连。
左边是矩阵的非零元（方块），右边是对应的图（节点 i、j 之间有边 ⇔ aᵢⱼ ≠ 0）。
第 1 步：先消去中心节点——它的所有邻居两两连边，矩阵右下角全部填满（填充 15 对）；
第 2 步：重新编号，把中心放在最后：依次消去 6 个工位，每个工位只有中心一个邻居，没有任何填充；
第 3 步：消元 = 在图上删去一个节点并把它的邻居连成团，好的排序就是让每次被删的节点邻居少。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("22.3", "消元与填充：顺序决定一切", "Elimination and fill-in: order is everything")
        n = 7
        cell = 0.42
        M0 = np.array([-4.0, 0.2, 0.0])                 # 矩阵左上角
        G0 = np.array([3.0, 0.0, 0.0])                  # 图的中心
        R = 1.9

        def sq(i, j, color, op=1.0):
            return Square(side_length=cell * 0.86, stroke_width=0, fill_color=color, fill_opacity=op).move_to(
                M0 + np.array([(j + 0.5) * cell, -(i + 0.5) * cell + n * cell / 2, 0]))

        frame = Rectangle(width=n * cell, height=n * cell, color=GREY_B, stroke_width=2).move_to(M0 + np.array([n * cell / 2, 0, 0]))
        # 第一种编号：中心为 0
        def node_pos(k, hub):
            if k == hub:
                return G0
            idx = [i for i in range(n) if i != hub].index(k)
            a = PI / 2 - 2 * PI * idx / (n - 1)
            return G0 + R * np.array([np.cos(a), np.sin(a), 0])

        def build(hub):
            mats = VGroup()
            for i in range(n):
                mats.add(sq(i, i, BLUE_C))
                if i != hub:
                    mats.add(sq(i, hub, BLUE_C), sq(hub, i, BLUE_C))
            dots = {k: Dot(node_pos(k, hub), radius=0.2, color=ORANGE if k == hub else TEAL) for k in range(n)}
            labs = VGroup(*[MathTex(str(k + 1), font_size=24, color=BLACK).move_to(dots[k]) for k in range(n)])
            edges = VGroup(*[Line(node_pos(hub, hub), node_pos(k, hub), color=GREY_B, stroke_width=3) for k in range(n) if k != hub])
            return mats, dots, labs, edges

        mats, dots, labs, edges = build(0)
        self.play(Create(frame), FadeIn(mats), Create(edges), *[FadeIn(d) for d in dots.values()], FadeIn(labs), run_time=1.5)
        self.caption("星形矩阵：中心节点 1（调度中心）与 6 个工位相连；左边是非零元，右边是图", "A star matrix: hub 1 (the dispatcher) is linked to six stations; nonzeros on the left, the graph on the right", wait=1.2)
        # 消去中心：邻居两两连边，矩阵填满
        fills, new_edges = VGroup(), VGroup()
        for i in range(1, n):
            for j in range(1, n):
                if i != j:
                    fills.add(sq(i, j, RED_C))
        for i in range(1, n):
            for j in range(i + 1, n):
                new_edges.add(Line(node_pos(i, 0), node_pos(j, 0), color=RED_C, stroke_width=2.5))
        self.play(Indicate(dots[0], color=YELLOW), run_time=0.8)
        self.play(dots[0].animate.set_color(GREY_D), run_time=0.4)
        self.play(FadeIn(fills, lag_ratio=0.02), Create(new_edges, lag_ratio=0.05), run_time=2.0)
        self.caption("先消去中心：它的 6 个邻居两两连边，右下角 30 个零全部变成非零——这就是填充",
                     "Eliminate the hub first: its six neighbours become pairwise connected and all 30 zeros fill in", wait=1.6)
        self.play(FadeOut(fills), FadeOut(new_edges), FadeOut(mats), FadeOut(edges), *[FadeOut(d) for d in dots.values()], FadeOut(labs))
        # 中心放在最后
        mats, dots, labs, edges = build(n - 1)
        self.play(FadeIn(mats), Create(edges), *[FadeIn(d) for d in dots.values()], FadeIn(labs), run_time=1.2)
        self.caption("重新编号：中心改为最后一个（7 号）", "Renumber: the hub becomes the last node (7)", wait=1.0)
        for k in range(n - 1):
            self.play(dots[k].animate.set_color(GREY_D), edges[k].animate.set_stroke(opacity=0.15), run_time=0.45)
        self.caption("依次消去 6 个工位：每个只有中心一个邻居，没有新边，一个填充也没有",
                     "Eliminate the six stations in turn: each has only the hub as neighbour; no new edges, no fill at all", wait=1.6)
        self.card([["消元 = 在图上删去节点，并把它的邻居连成团", "Elimination = delete a node and join its neighbours into a clique"],
                   ["填充的多少取决于消元的顺序", "The amount of fill depends on the elimination order"],
                   ["好的排序：先消去邻居少的节点（最小度）、最后消去“枢纽”和分隔线（嵌套剖分）", "Good orders eliminate low-degree nodes first (minimum degree) and hubs or separators last (nested dissection)"]])
