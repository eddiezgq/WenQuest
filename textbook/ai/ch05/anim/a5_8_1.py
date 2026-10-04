"""动画 5.8.1（配图 5.8.1）：分块矩阵乘法中数据在显存、共享内存、寄存器之间的流动。画 4×4 个块的 A、B、C：
线程块负责 C 的块 (1, 2)；沿 K 方向共 4 步，每步 A 的块 (1, k) 与 B 的块 (k, 2) 从显存进入共享内存，块内的线程从共享内存取数到寄存器
做乘加，累加结果留在寄存器里；4 步之后把 C 的块写回显存。最后对比：分块后每个数从显存读进来被 T 个线程使用，显存读量降为 1/T。"""
from manim import *
from wq_anim import *

NB = 4


class Lesson(Base):
    def construct(self):
        self.title("5.8", "分块矩阵乘法：数据怎样流动", "Tiled matrix multiplication: how the data flows")
        c = 0.42

        def grid(origin, color):
            return VGroup(*[Square(c, stroke_width=1, color=GREY_B, fill_color=color, fill_opacity=0.08)
                            .move_to(origin + np.array([(j + 0.5) * c, -(i + 0.5) * c, 0])) for i in range(NB) for j in range(NB)])

        oA, oB, oC = np.array([-6.4, 0.4, 0]), np.array([-4.2, 2.7, 0]), np.array([-4.2, 0.4, 0])
        A, B, Cm = grid(oA, RED), grid(oB, BLUE), grid(oC, GOLD)
        labs = VGroup(Text("A", font_size=24).next_to(A, UP, buff=0.1), Text("B", font_size=24).next_to(B, LEFT, buff=0.1),
                      Text("C", font_size=24).next_to(Cm, DOWN, buff=0.1))
        dram = SurroundingRectangle(VGroup(A, B, Cm), color=GREY_B, buff=0.25, corner_radius=0.1)
        dram_t = zh("显存（全局内存）", 22, GREY_B).next_to(dram, DOWN, buff=0.15)
        self.play(FadeIn(A), FadeIn(B), FadeIn(Cm), FadeIn(labs), Create(dram), FadeIn(dram_t))
        self.caption("A、B、C 各切成 4×4 个块，放在显存里", "A, B and C cut into 4×4 tiles, stored in device memory")
        target = Cm[1 * NB + 2]
        self.play(target.animate.set_fill(GOLD, opacity=0.9), run_time=0.6)
        self.caption("一个线程块负责 C 的块 (1, 2)：它要用 A 的第 1 行块、B 的第 2 列块", "One thread block owns C tile (1, 2): it needs row 1 of A's tiles and column 2 of B's")

        smem = RoundedRectangle(width=3.0, height=1.6, corner_radius=0.12, color=TEAL).move_to(np.array([1.6, 1.6, 0]))
        smem_t = zh("共享内存（片上）", 22, TEAL).next_to(smem, UP, buff=0.12)
        regs = RoundedRectangle(width=3.0, height=1.2, corner_radius=0.12, color=YELLOW).move_to(np.array([1.6, -0.9, 0]))
        regs_t = zh("寄存器（每个线程的累加和）", 22, YELLOW).next_to(regs, DOWN, buff=0.12)
        acc = Square(0.9, color=GOLD, fill_color=GOLD, fill_opacity=0.15).move_to(regs)
        self.play(Create(smem), FadeIn(smem_t), Create(regs), FadeIn(regs_t), FadeIn(acc))
        reads = Integer(0, font_size=30, color=WHITE).move_to(np.array([5.3, 1.6, 0]))
        reads_t = zh("从显存读的块", 20, GREY_B).next_to(reads, UP, buff=0.1)
        self.play(FadeIn(reads), FadeIn(reads_t))
        for k in range(NB):
            a, b = A[1 * NB + k], B[k * NB + 2]
            ca, cb = a.copy().set_fill(RED, 0.8), b.copy().set_fill(BLUE, 0.8)
            self.play(a.animate.set_fill(RED, opacity=0.5), b.animate.set_fill(BLUE, opacity=0.5), run_time=0.4)
            self.play(ca.animate.move_to(smem.get_center() + LEFT * 0.6).scale(1.6),
                      cb.animate.move_to(smem.get_center() + RIGHT * 0.6).scale(1.6), reads.animate.set_value(2 * k + 2), run_time=0.9)
            if k == 0:
                self.caption("第 1 步：A 的块 (1, 0)、B 的块 (0, 2) 读进共享内存，然后 __syncthreads()",
                             "Step 1: tile (1, 0) of A and tile (0, 2) of B into shared memory, then __syncthreads()", wait=0.8)
            dots = VGroup(*[Dot(radius=0.05, color=YELLOW).move_to(smem.get_bottom() + RIGHT * (i - 2) * 0.4) for i in range(5)])
            self.play(LaggedStart(*[d.animate.move_to(acc.get_center()) for d in dots], lag_ratio=0.12), run_time=0.8)
            self.play(FadeOut(dots), acc.animate.set_fill(GOLD, opacity=0.15 + 0.2 * (k + 1)), run_time=0.4)
            if k == 0:
                self.caption("每个线程从共享内存取一行、一列，乘加的结果留在寄存器里；再同步一次，进入下一步",
                             "Each thread reads a row and a column from shared memory; sums stay in registers; sync again, next step", wait=0.8)
            self.play(FadeOut(ca), FadeOut(cb), run_time=0.3)
        self.caption("4 步之后，C 的块算完，写回显存", "After 4 steps the C tile is complete and written back")
        self.play(TransformFromCopy(acc, target), run_time=1.0)
        self.wait(0.6)
        self.caption("显存只读了 8 个块；不分块时每个元素都要从显存读一行、一列", "Only 8 tiles were read; without tiling every element reads a whole row and column")
        self.card([["共享内存分块", "Shared-memory tiling"],
                   ["每个数从显存读进来，被块内 T 个线程使用", "Each value loaded from memory is used by T threads"],
                   ["显存读量降为 1/T，计算强度约 T/4 FLOP/B", "Traffic falls to 1/T; intensity is about T/4 FLOP/B"],
                   ["再加寄存器分块：共享内存的数在寄存器里再用几次", "Add register tiling: reuse shared values again in registers"]])
