"""动画 3.3.1（配图 3.3.1）：同一批工作——检测工位一帧图像的 64 个小块，每块要做同样的滤波——
交给 CPU 的 4 个大核与 GPU 的 64 个小核。大核每块只用 1 个单位时间，小核要 4 个单位时间；
CPU 要 16 轮，GPU 只要 1 轮（4 个单位时间），总时间 CPU 16、GPU 4。数字只为示意，不按真实比例（算例 3.3.1 中单条通道与单个核心相差约 48 倍）：
单个小核远比大核慢，靠数量取胜。"""
from manim import *
from wq_anim import *


class Lesson(Base):
    def construct(self):
        self.title("3.3", "少数大核与成千上万个小核", "A few big cores versus thousands of small ones")
        # 工作：8×8 个小块
        tiles = VGroup(*[Square(0.32, stroke_width=1, color=GREY_B, fill_color=BLUE_E, fill_opacity=0.6) for _ in range(64)])
        tiles.arrange_in_grid(8, 8, buff=0.04).move_to(UP * 0.4)
        self.play(FadeIn(tiles), run_time=0.8)
        self.caption("一帧图像分成 64 块，每块做同样的滤波", "64 tiles of one frame, each needs the same filter")
        self.play(tiles.animate.scale(0.75).to_edge(LEFT, buff=0.6).shift(UP * 0.4), run_time=0.8)

        cpu = VGroup(*[RoundedRectangle(corner_radius=0.08, width=1.1, height=1.1, color=GOLD, fill_opacity=0.25) for _ in range(4)])
        cpu.arrange(RIGHT, buff=0.25).move_to(RIGHT * 2.2 + UP * 1.7)
        cpu_lab = bi(["CPU：4 个大核", "CPU: 4 big cores"], size=24).next_to(cpu, LEFT, buff=0.4)
        gpu = VGroup(*[Square(0.22, color=BLUE, fill_opacity=0.35, stroke_width=1) for _ in range(64)])
        gpu.arrange_in_grid(4, 16, buff=0.06).move_to(RIGHT * 2.2 + DOWN * 1.2)
        gpu_lab = bi(["GPU：64 个小核", "GPU: 64 small cores"], size=24).next_to(gpu, LEFT, buff=0.4)
        self.play(FadeIn(cpu), FadeIn(cpu_lab), FadeIn(gpu), FadeIn(gpu_lab))
        self.caption("大核快：每块 1 个单位时间；小核慢：每块 4 个单位时间（示意）", "Big core: 1 time unit per tile; small core: 4 units (schematic)")

        t_cpu = VGroup(bi(["用时", "time"], size=22, color=GOLD), DecimalNumber(0, num_decimal_places=0, font_size=34, color=GOLD)) \
            .arrange(RIGHT, buff=0.3).next_to(cpu, DOWN, buff=0.25)
        t_gpu = VGroup(bi(["用时", "time"], size=22, color=BLUE), DecimalNumber(0, num_decimal_places=0, font_size=34, color=BLUE)) \
            .arrange(RIGHT, buff=0.3).next_to(gpu, DOWN, buff=0.25)
        self.play(FadeIn(t_cpu), FadeIn(t_gpu))
        # CPU：16 轮，每轮 4 块
        for r in range(16):
            batch = VGroup(*[tiles[4 * r + i] for i in range(4)])
            self.play(batch.animate.set_fill(GOLD, opacity=0.9), *[c.animate.set_fill(GOLD, opacity=0.8) for c in cpu],
                      run_time=0.18)
            self.play(*[c.animate.set_fill(GOLD, opacity=0.25) for c in cpu], run_time=0.06)
            t_cpu[1].set_value(r + 1)
        self.caption("CPU 做了 16 轮：16 个单位时间", "The CPU needs 16 rounds: 16 time units")
        self.play(tiles.animate.set_fill(BLUE_E, opacity=0.6), run_time=0.4)
        self.play(*[g.animate.set_fill(BLUE, opacity=0.9) for g in gpu], tiles.animate.set_fill(BLUE, opacity=0.9), run_time=1.6)
        t_gpu[1].set_value(4)
        self.caption("GPU 一轮做完 64 块：4 个单位时间", "The GPU does all 64 tiles in one round: 4 time units")
        self.wait(0.6)
        self.card([["面向延迟与面向吞吐", "Latency versus throughput"],
                   ["CPU 让一件事尽快做完；GPU 让单位时间做完的事最多", "A CPU finishes one task fast; a GPU finishes the most tasks per unit time"],
                   ["前提：工作能拆成大量互不依赖的小份", "Provided the work splits into many independent pieces"]])
