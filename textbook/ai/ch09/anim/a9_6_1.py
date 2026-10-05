"""动画 9.6.1（配图 9.6.1）：FlashAttention 的分块计算与在线 softmax。
一个 Q 块（几行）依次与 K、V 的各块相遇：每到一块，算出一小块分数，更新这几行的最大值 m、和 ℓ 与输出的累加；
新的最大值更大时，旧的累加乘以 e^(m − m′) 修正。因果掩码下，对角线右上方的块直接跳过。整个分数矩阵从不写回显存。"""
from manim import *
from wq_anim import *

NB = 6


class Lesson(Base):
    def construct(self):
        self.title("9.6", "FlashAttention：一块一块地算注意力", "FlashAttention: attention one tile at a time")
        grid = VGroup()
        for i in range(NB):
            for j in range(NB):
                sq = Square(0.62, stroke_width=1, color=GREY_B, fill_opacity=0.0 if j > i else 0.12, fill_color=GREY_B)
                sq.move_to([-3.6 + j * 0.66, 1.9 - i * 0.66, 0])
                grid.add(sq)
        self.play(FadeIn(grid))
        self.caption("N × N 的分数矩阵：标准实现要把它整个写进显存；右上方被因果掩码掩掉", "The N × N score matrix: the standard way writes all of it to memory; the upper right is masked")
        row = 3
        stats = VGroup(zh("m（每行最大值）", 20), zh("ℓ（每行的和）", 20), zh("O（输出的累加）", 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.3).shift(RIGHT * 3.2 + UP * 0.6)
        self.play(FadeIn(stats))
        hl = SurroundingRectangle(VGroup(*[grid[row * NB + j] for j in range(NB)]), color=BLUE, buff=0.03)
        self.play(Create(hl))
        for j in range(row + 1):
            cell = grid[row * NB + j]
            self.play(cell.animate.set_fill(BLUE, 0.7), run_time=0.5)
            flash = Indicate(stats, color=YELLOW, scale_factor=1.05)
            self.play(flash, run_time=0.5)
            if j == 1:
                self.caption("每读入一块 K、V：算这一小块分数，更新 m、ℓ 与 O；最大值变大时，旧的 ℓ、O 乘以 e^(m − m′)",
                             "For each K, V tile: compute a tile of scores, update m, ℓ and O; if the max grows, rescale the old ℓ and O by e^(m − m′)", wait=0.5)
        skip = VGroup(*[grid[row * NB + j] for j in range(row + 1, NB)])
        self.play(skip.animate.set_stroke(GREY_D), run_time=0.4)
        self.caption("对角线右边的块整个跳过；这几行算完，O 除以 ℓ 写回——分数矩阵从未写进显存",
                     "Tiles right of the diagonal are skipped; the rows finish, O / ℓ is written back — the scores never touched memory")
        self.card([["FlashAttention", "FlashAttention"],
                   MathTex(r"m' = \max(m, x_j),\quad \ell' = \ell\, e^{m - m'} + e^{x_j - m'}", font_size=38),
                   ["分块读 Q、K、V，在片上算 softmax", "Tile Q, K, V and do softmax on chip"],
                   ["显存流量从 O(N²) 降到 O(N²d²/M)，M 为片上存储的大小", "Memory traffic drops from O(N²) to O(N²d²/M), M = on-chip memory"]])
