"""动画 6.4.1（配图 6.4.1）：环形全归约中数据块的流转。4 块 GPU 排成一个环，每块的数组切成 4 块（a、b、c、d，各一种颜色）。
归约—散播 3 步：每步每块 GPU 把一块发给右邻，右邻加到自己的同一块上（格中数字是已经加进了几块 GPU 的数据）；3 步后每块 GPU 有一块完整的和。
全收集 3 步：完整的块沿环传下去。最后每块 GPU 的 4 块都是完整的和。每块 GPU 一共发出 6 次、每次 1/4 个数组，即 1.5 倍的数组长度。"""
from manim import *
from wq_anim import *

P = 4
COLS = [RED, BLUE, GREEN, GOLD]


class Lesson(Base):
    def construct(self):
        self.title("6.4", "环形全归约：每步只和邻居说话", "Ring all-reduce: talk only to your neighbour")
        R, cw = 2.2, 0.48
        centers = [np.array([R * np.cos(np.pi / 2 - 2 * np.pi * r / P), R * np.sin(np.pi / 2 - 2 * np.pi * r / P) - 0.3, 0]) for r in range(P)]
        have = [[{r} for _ in range(P)] for r in range(P)]
        cells, nums = [], []
        for r in range(P):
            row, nrow = [], []
            for c in range(P):
                sq = Square(cw, stroke_width=1, color=GREY_B, fill_color=COLS[c], fill_opacity=0.25).move_to(centers[r] + np.array([(c - 1.5) * cw, 0, 0]))
                t = Text("1", font_size=18).move_to(sq)
                row.append(sq)
                nrow.append(t)
            cells.append(row)
            nums.append(nrow)
        labels = [Text(f"GPU {r}", font_size=20, color=GREY_B).next_to(VGroup(*cells[r]), UP, buff=0.1) for r in range(P)]
        self.play(*[FadeIn(VGroup(*cells[r], *nums[r], labels[r])) for r in range(P)])
        self.caption("4 块 GPU，每块的数组切成 4 块；数字：这一块里已经加进了几块 GPU 的数据",
                     "4 GPUs, each array cut into 4 chunks; the number counts the GPUs whose data a chunk holds")

        def step(s, phase):
            moves = []
            new = [[set(x) for x in row] for row in have]
            for r in range(P):
                c = (r - s) % P if phase == "rs" else (r + 1 - s) % P
                dst = (r + 1) % P
                if phase == "rs":
                    new[dst][c] |= have[r][c]
                else:
                    new[dst][c] = set(have[r][c])
                ghost = cells[r][c].copy().set_fill(COLS[c], 0.9)
                moves.append((ghost, cells[dst][c], dst, c))
            self.play(*[g.animate.move_to(target.get_center()) for g, target, _, _ in moves], run_time=1.0)
            anims = []
            for g, target, dst, c in moves:
                k = len(new[dst][c])
                anims += [FadeOut(g), target.animate.set_fill(COLS[c], 0.25 + 0.75 * (k == P) + 0.12 * k * (k < P)),
                          Transform(nums[dst][c], Text(str(k), font_size=18, color=WHITE if k == P else GREY_A).move_to(target))]
            self.play(*anims, run_time=0.6)
            for r in range(P):
                for c in range(P):
                    have[r][c] = new[r][c]

        for s in range(P - 1):
            if s == 0:
                self.caption("归约—散播：每步每块 GPU 把一块发给右邻，右邻加到同一块上", "Reduce-scatter: each step every GPU sends one chunk right; the neighbour adds it in", wait=0.3)
            step(s, "rs")
        self.caption("3 步后，每块 GPU 都有一块完整的和（实心的格子）", "After 3 steps every GPU holds one complete chunk (solid)")
        for s in range(P - 1):
            if s == 0:
                self.caption("全收集：把完整的块沿环传下去", "All-gather: pass the complete chunks around the ring", wait=0.3)
            step(s, "ag")
        self.caption("6 步之后，每块 GPU 的每一块都是全部 4 块 GPU 的和", "After 6 steps every chunk on every GPU is the sum of all four")
        self.card([["环形全归约", "Ring all-reduce"],
                   ["2(p − 1) 步，每步所有链路同时忙碌", "2(p − 1) steps, every link busy at once"],
                   MathTex(r"T = 2(p-1)\,\alpha + \frac{2(p-1)}{p}\cdot\frac{n}{\beta}", font_size=40),
                   ["带宽项几乎与 GPU 数无关", "The bandwidth term barely depends on the GPU count"]])
