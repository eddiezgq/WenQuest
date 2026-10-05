"""动画 10.3.1（配图 10.3.1）：同一段矩阵乘法在两种架构上怎样执行。
左边是 SIMT 的 GPU：一个线程算一个输出，一个线程束（32 道）或波前（64 道）同时走同一条指令，输出一行一行地被填满；
右边是昇腾的立方单元：数据先搬进片上缓冲，一条指令吃下 16×16×16 的一整块，输出按 16×16 的方块填满，
搬入、计算、搬出三段在不同数据块上重叠进行。两边算的是同一个乘积，差别只在“谁来做乘加、数据怎样喂进去”。"""
from manim import *
from wq_anim import *

N = 8                                              # 画成 8×8 的输出矩阵（每格代表一块）


class Lesson(Base):
    def construct(self):
        self.title("10.3", "同一段矩阵乘法，两种架构", "One matrix multiply, two architectures")

        def grid(x0, color):
            g = VGroup()
            for i in range(N):
                for j in range(N):
                    sq = Square(0.42, stroke_width=1, color=GREY_B, fill_opacity=0.08, fill_color=color)
                    sq.move_to([x0 + j * 0.45, 1.6 - i * 0.45, 0])
                    g.add(sq)
            return g

        left, right = grid(-5.0, BLUE), grid(1.4, RED)
        lt = zh("GPU（SIMT）", 26).next_to(left, UP, buff=0.35)
        rt = zh("昇腾（立方单元）", 26).next_to(right, UP, buff=0.35)
        self.play(FadeIn(left), FadeIn(right), FadeIn(lt), FadeIn(rt))
        self.caption("同一个输出矩阵 C = AB：每个小格是一块输出", "The same output C = AB: each cell is a tile of the result")

        # 左：一个线程束一次推进一行
        for i in range(3):
            row = VGroup(*[left[i * N + j] for j in range(N)])
            self.play(row.animate.set_fill(BLUE, 0.75), run_time=0.45)
            if i == 0:
                self.caption("GPU：一个线程算一个输出，一个线程束的 32 道（AMD 是 64 道）一起走同一条指令",
                             "GPU: one thread per output; the 32 lanes of a warp (64 on AMD) step together", wait=0.4)
        rest = VGroup(*[left[i * N + j] for i in range(3, N) for j in range(N)])
        self.play(rest.animate.set_fill(BLUE, 0.75), run_time=0.8)

        # 右：一条立方指令填满 2×2 个格子（代表 16×16×16 的一块）
        bufs = VGroup(zh("L1 / L0A、L0B", 20), zh("立方单元 16×16×16", 20), zh("L0C（FP32 累加）", 20))
        bufs.arrange(DOWN, buff=0.28).next_to(right, DOWN, buff=0.5)
        self.play(FadeIn(bufs))
        for bi in range(4):
            r0, c0 = (bi // 2) * 4, (bi % 2) * 4
            block = VGroup(*[right[(r0 + a) * N + (c0 + b)] for a in range(4) for b in range(4)])
            self.play(Indicate(bufs[0], color=YELLOW, scale_factor=1.05), run_time=0.35)
            self.play(block.animate.set_fill(RED, 0.75), Indicate(bufs[1], color=YELLOW, scale_factor=1.05), run_time=0.5)
            self.play(Indicate(bufs[2], color=YELLOW, scale_factor=1.05), run_time=0.3)
            if bi == 0:
                self.caption("昇腾：数据先搬进片上缓冲，一条指令吃下 16×16×16 的一块，结果在 L0C 里按单精度累加",
                             "Ascend: data is moved on chip first; one instruction consumes a 16×16×16 tile, accumulating in L0C in FP32", wait=0.4)
        self.caption("搬入、计算、搬出三段在不同数据块上重叠：n 块要 n + 2 段，而不是 3n 段",
                     "CopyIn, Compute and CopyOut overlap across tiles: n tiles take n + 2 stages, not 3n")

        self.card([["同一件事，两种分工", "Same work, two divisions of labour"],
                   ["GPU：成千上万个线程，每个算一个输出；硬件靠缓存与调度隐藏延迟",
                    "GPU: thousands of threads, one output each; caches and scheduling hide latency"],
                   ["昇腾：一个大单元一次算一块；片上缓冲与流水由程序显式管理",
                    "Ascend: one big unit per tile; buffers and the pipeline are managed explicitly"],
                   ["两边都要把数据留在片上多用几次——分块是跨架构的",
                    "Both must reuse data on chip — tiling is architecture-independent"]])
