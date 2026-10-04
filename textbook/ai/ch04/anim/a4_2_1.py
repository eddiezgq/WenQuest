"""动画 4.2.1（配图 4.2.1）：线程块铺满一帧图像。先画出图像，再一块块铺上 16×16 的线程块（只演示左上角 6×4 块）；
放大线程块 (3, 2)，其中线程 (5, 7) 由式 (4.2.3) 算出它负责的像素：col = 3·16 + 5 = 53，row = 2·16 + 7 = 39。"""
from manim import *
from wq_anim import *


class Lesson(Base):
    def construct(self):
        self.title("4.2", "线程块怎样铺满一帧图像", "How thread blocks tile an image")
        cell = 0.9
        origin = np.array([-5.2, 2.2, 0])
        img = Rectangle(width=6 * cell, height=4 * cell, stroke_width=0, fill_color=GREY_D, fill_opacity=0.6) \
            .move_to(origin + np.array([3 * cell, -2 * cell, 0]))
        self.play(FadeIn(img))
        self.caption("一帧 3840×2160 的图像（这里只画左上角 96×64 像素）", "A 3840×2160 frame (top-left 96×64 pixels shown)")
        blocks = VGroup()
        for j in range(4):
            for i in range(6):
                sq = Square(cell, stroke_width=1.5, color=BLUE_B).move_to(origin + np.array([(i + 0.5) * cell, -(j + 0.5) * cell, 0]))
                lab = Text(f"({i},{j})", font_size=16).move_to(sq)
                blocks.add(VGroup(sq, lab))
        self.play(LaggedStart(*[FadeIn(b) for b in blocks], lag_ratio=0.06), run_time=2.2)
        self.caption("每个线程块 16×16 个线程，全图 240×135 块", "Each block has 16×16 threads; 240×135 blocks in all")
        target = blocks[2 * 6 + 3]
        self.play(target[0].animate.set_fill(BLUE, opacity=0.5), run_time=0.6)
        # 放大
        big = VGroup(*[Square(0.22, stroke_width=0.6, color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.4)
                       .move_to(np.array([1.2 + i * 0.22, 1.9 - j * 0.22, 0])) for j in range(16) for i in range(16)])
        self.play(TransformFromCopy(target[0], big), run_time=1.2)
        self.caption("放大线程块 (3, 2)：threadIdx 从 (0, 0) 到 (15, 15)", "Block (3, 2) enlarged: threadIdx from (0, 0) to (15, 15)")
        th = big[7 * 16 + 5]
        self.play(th.animate.set_fill(RED, opacity=1), run_time=0.6)
        eq = MathTex(r"\mathrm{col} = 3\cdot16 + 5 = 53", r"\quad \mathrm{row} = 2\cdot16 + 7 = 39", font_size=34).to_edge(DOWN, buff=1.5)
        self.play(Write(eq))
        dot = Dot(origin + np.array([(53 + 0.5) / 16 * cell, -(39 + 0.5) / 16 * cell, 0]), color=RED, radius=0.06)
        self.play(TransformFromCopy(th, dot), run_time=1.0)
        self.caption("线程 (5, 7) 处理第 39 行第 53 列的像素", "Thread (5, 7) handles the pixel in row 39, column 53", wait=1.2)
        self.card([["二维索引", "Two-dimensional indices"],
                   MathTex(r"\mathrm{col} = \mathrm{blockIdx.x}\cdot\mathrm{blockDim.x} + \mathrm{threadIdx.x}", font_size=34),
                   MathTex(r"\mathrm{row} = \mathrm{blockIdx.y}\cdot\mathrm{blockDim.y} + \mathrm{threadIdx.y}", font_size=34)])
