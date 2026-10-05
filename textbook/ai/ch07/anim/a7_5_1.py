"""动画 7.5.1（配图 7.5.1）：一行 PyTorch 代码 y = x @ w 从 Python 到 GPU 核函数的调用链。
一个小方块（这次调用）从上往下穿过七层：Python 绑定、组合算子 matmul 分解成 mm、分派器的自动微分键（顺手记下反向节点）、
CUDA 键与 ATen 的 mm、cuBLAS（挑核函数）、
运行时与驱动（把启动命令放进流的队列）。主机这一路花几到十几微秒，然后立即返回下一行 Python；
GPU 稍后才从队列里取出命令执行。最后对比：大矩阵时 GPU 的执行远长于主机的开销，主机跑在前面；小运算时反过来，GPU 等主机。"""
from manim import *
from wq_anim import *

LAYERS = [("Python：y = x @ w", "Python binding"), ("aten::matmul 分解成 aten::mm", "composite matmul → mm"),
          ("分派器：自动微分键", "dispatcher: Autograd"), ("分派器：CUDA 键 → ATen 的 mm", "dispatcher: CUDA → ATen mm"), ("cuBLAS：挑选核函数", "cuBLAS: pick a kernel"),
          ("运行时与驱动：cudaLaunchKernel", "runtime and driver"), ("GPU：核函数在 SM 上执行", "GPU: kernel on the SMs")]
COLS = [GREY_B, BLUE_D, BLUE_D, BLUE_D, GREEN_D, GOLD_D, RED_D]


class Lesson(Base):
    def construct(self):
        self.title("7.5", "一行代码的旅程", "The journey of one line of code")
        boxes = VGroup()
        for (z, e), c in zip(LAYERS, COLS):
            r = RoundedRectangle(width=6.2, height=0.6, corner_radius=0.1, stroke_color=c, fill_color=c, fill_opacity=0.25)
            t = VGroup(zh(z, 22), en(e, 15)).arrange(DOWN, buff=0.02).move_to(r)
            boxes.add(VGroup(r, t))
        boxes.arrange(DOWN, buff=0.12).shift(LEFT * 1.5 + DOWN * 0.15)
        self.play(LaggedStart(*[FadeIn(b, shift=DOWN * 0.1) for b in boxes], lag_ratio=0.12), run_time=1.6)
        self.caption("y = x @ w：x、w 在 GPU 上，要记录梯度", "y = x @ w with x, w on the GPU and requiring grad", wait=0.6)

        dot = Square(0.28, color=YELLOW, fill_opacity=0.9).next_to(boxes[0], LEFT, buff=0.25)
        self.play(FadeIn(dot))
        notes = {1: ("组合算子：二维时调用 mm", "composite: calls mm for 2-D inputs"),
                 2: ("记下反向节点 MmBackward0，保存 x、w", "record MmBackward0, save x and w"),
                 3: ("缓存分配器给出输出的显存", "the caching allocator hands out the output"),
                 4: ("按形状选一个矩阵乘法核函数", "choose a GEMM kernel for the shape"),
                 5: ("命令放进流的队列，立即返回", "queue the command and return at once")}
        clock = Integer(0, font_size=30, color=YELLOW)
        unit = zh("μs（主机，示意）", 22, YELLOW)
        VGroup(clock, unit).arrange(RIGHT, buff=0.1).to_corner(UR, buff=0.6)
        unit.add_updater(lambda u: u.next_to(clock, RIGHT, buff=0.1))
        self.play(FadeIn(clock), FadeIn(unit))
        us = [0, 2, 3, 5, 7, 10, 10]
        for i in range(1, 6):
            self.play(dot.animate.next_to(boxes[i], LEFT, buff=0.25), clock.animate.set_value(us[i]), run_time=0.6)
            if i in notes:
                n = VGroup(zh(notes[i][0], 20, INK), en(notes[i][1], 14)).arrange(DOWN, buff=0.03).next_to(boxes[i], RIGHT, buff=0.3)
                self.play(FadeIn(n, shift=LEFT * 0.1), run_time=0.4)
        self.caption("主机这一路几到十几微秒，然后 Python 立即执行下一行", "A few to tens of microseconds on the host; then Python moves on", wait=0.8)
        back = dot.copy().set_color(GREY_B)
        self.play(back.animate.next_to(boxes[0], LEFT, buff=0.25), run_time=0.6)
        self.play(dot.animate.next_to(boxes[6], LEFT, buff=0.25), run_time=0.8)
        self.play(boxes[6][0].animate.set_fill(RED_D, 0.7), run_time=0.5)
        self.caption("GPU 稍后才从队列里取出命令执行：调用是异步的", "The GPU takes the command from the queue later: calls are asynchronous")

        # 两种情形：大矩阵时 GPU 忙、主机跑在前面；小运算时 GPU 等主机
        self.clear_stage()
        self.caption("谁等谁：主机发出一次要约十微秒，GPU 执行一次要多久？", "Who waits: about ten microseconds per launch on the host versus the kernel time on the GPU", wait=0.5)
        L0, HW = -5.2, 0.6                                   # 时间轴起点；主机发出一次启动占的宽度（约 10 μs）
        for k, (lab, kw) in enumerate([(("大矩阵：每个核函数远长于一次启动", "large GEMMs: kernels much longer than a launch"), 2.2),
                                       (("小运算：每个核函数远短于一次启动", "tiny ops: kernels much shorter than a launch"), 0.06)]):
            y = 1.4 - k * 2.3
            self.play(FadeIn(bi(lab, 22).move_to([0, y + 0.75, 0])), run_time=0.4)
            self.add(zh("主机", 18, GOLD).move_to([L0 - 0.8, y, 0]), zh("GPU", 18, RED).move_to([L0 - 0.8, y - 0.45, 0]))
            host, gpu, t = VGroup(), VGroup(), L0
            for j in range(4):
                h = Rectangle(width=HW - 0.05, height=0.3, fill_color=GOLD_D, fill_opacity=0.85, stroke_width=0)
                host.add(h.move_to([L0 + j * HW + HW / 2, y, 0]))
                start = max(t, L0 + (j + 1) * HW)            # 第 j 个核函数：启动发出之后、前一个执行完之后才开始
                g = Rectangle(width=kw, height=0.3, fill_color=RED_D, fill_opacity=0.85, stroke_width=0.5)
                gpu.add(g.move_to([start + kw / 2, y - 0.45, 0]))
                t = start + kw
            self.play(LaggedStart(*[FadeIn(h) for h in host], lag_ratio=0.3),
                      LaggedStart(*[GrowFromEdge(g, LEFT) for g in gpu], lag_ratio=0.5), run_time=2.2)
        self.caption("大矩阵：主机跑在前面，开销被藏住；小运算：GPU 大部分时间在等主机", "Large GEMMs hide the overhead; tiny ops leave the GPU waiting for the host")
        self.card([["一行代码的旅程", "The journey of one line"],
                   ["Python → 分派器 → ATen → cuBLAS → 驱动 → GPU", "Python → dispatcher → ATen → cuBLAS → driver → GPU"],
                   ["主机几到十几微秒，调用异步返回", "A few to tens of microseconds on the host; the call returns asynchronously"],
                   ["小运算多时：融合、CUDA 图、torch.compile（7.8 节）", "Many tiny ops: fuse, CUDA graphs, torch.compile (Section 7.8)"]])
