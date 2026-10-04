"""动画 5.2.1（配图 5.2.1）：归约树的逐级合并。共享内存中的 16 个数按顺序寻址（版本 3）求和：每一层前一半的线程把后一半的数
加到自己的位置上，4 层、15 次加法得到总和 80；每层之间要同步一次。最后演示线程束洗牌：8 个线程直接从相隔 4、2、1 的线程的寄存器取数，
不经过共享内存，也不用同步。"""
from manim import *
from wq_anim import *

VALS = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3]


class Lesson(Base):
    def construct(self):
        self.title("5.2", "归约树：一层层两两相加", "The reduction tree, level by level")
        n, w = len(VALS), 0.72
        x0 = -w * (n - 1) / 2
        boxes = VGroup(*[Square(w * 0.9, stroke_width=1.5, color=BLUE_B, fill_color=BLUE_E, fill_opacity=0.5)
                         .move_to(np.array([x0 + i * w, 1.2, 0])) for i in range(n)])
        nums = [Text(str(v), font_size=26).move_to(boxes[i]) for i, v in enumerate(VALS)]
        idx = VGroup(*[Text(str(i), font_size=16, color=GREY_B).next_to(boxes[i], UP, buff=0.12) for i in range(n)])
        self.play(FadeIn(boxes), *[FadeIn(t) for t in nums], FadeIn(idx))
        self.caption("共享内存里的 16 个数，每个线程放进一个", "16 values in shared memory, one per thread")
        vals = VALS[:]
        s = n // 2
        level = 1
        while s >= 1:
            arrows = VGroup(*[CurvedArrow(boxes[t + s].get_bottom() + DOWN * 0.05, boxes[t].get_bottom() + DOWN * 0.05,
                                          angle=-0.6 if s > 1 else -1.2, color=GOLD, stroke_width=2.5, tip_length=0.15) for t in range(s)])
            self.caption(f"第 {level} 层：前 {s} 个线程各把位置 k + {s} 的数加到位置 k 上",
                         f"Level {level}: the first {s} threads add slot k + {s} into slot k", wait=0.4)
            self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.08), run_time=1.0)
            anims = []
            for t in range(s):
                vals[t] += vals[t + s]
                new = Text(str(vals[t]), font_size=26, color=YELLOW).move_to(boxes[t])
                anims.append(Transform(nums[t], new))
            dim = [boxes[i].animate.set_fill(GREY_D, opacity=0.25) for i in range(s, 2 * s)]
            self.play(*anims, *dim, run_time=0.9)
            self.play(FadeOut(arrows), run_time=0.3)
            bar = DashedLine(np.array([x0 - 0.6, 0.45, 0]), np.array([-x0 + 0.6, 0.45, 0]), color=GREY_B)
            sync = Text("__syncthreads()", font_size=20, color=GREY_B).next_to(bar, RIGHT, buff=0.1).shift(LEFT * 1.6 + DOWN * 0.25)
            self.play(Create(bar), FadeIn(sync), run_time=0.4)
            self.play(FadeOut(bar), FadeOut(sync), run_time=0.3)
            s //= 2
            level += 1
        self.caption("4 层、15 次加法：位置 0 上是总和 80", "4 levels, 15 additions: slot 0 holds the total, 80")
        self.clear_stage()

        # 线程束洗牌：8 个线程（示意），每个线程的值在自己的寄存器里
        lanes = [3 + 5, 1 + 3, 4 + 5, 1 + 8, 5 + 9, 9 + 7, 2 + 9, 6 + 3]
        regs = VGroup(*[Circle(0.32, color=GOLD, fill_opacity=0.25).move_to(np.array([-4.2 + i * 1.2, 1.0, 0])) for i in range(8)])
        rt = [Text(str(v), font_size=24).move_to(regs[i]) for i, v in enumerate(lanes)]
        lab = VGroup(*[Text(f"lane {i}", font_size=16, color=GREY_B).next_to(regs[i], UP, buff=0.1) for i in range(8)])
        self.play(FadeIn(regs), *[FadeIn(t) for t in rt], FadeIn(lab))
        self.caption("线程束洗牌：数在各线程的寄存器里，直接从别的线程取", "Warp shuffle: values stay in registers; a thread reads another thread's register")
        vals = lanes[:]
        for off in (4, 2, 1):
            code = Text(f"v += __shfl_down_sync(mask, v, {off})", font_size=22, color=GOLD).move_to(np.array([0, -0.6, 0]))
            arrows = VGroup(*[CurvedArrow(regs[i + off].get_bottom(), regs[i].get_bottom(), angle=-0.5, color=GOLD, stroke_width=2.5, tip_length=0.15)
                              for i in range(8 - off)])
            self.play(FadeIn(code), LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.08), run_time=0.9)
            anims = []
            for i in range(8 - off):
                vals[i] += vals[i + off]
                anims.append(Transform(rt[i], Text(str(vals[i]), font_size=24, color=YELLOW).move_to(regs[i])))
            self.play(*anims, run_time=0.8)
            self.play(FadeOut(arrows), FadeOut(code), run_time=0.3)
        self.caption("3 次洗牌，lane 0 得到 80：不用共享内存，也不用 __syncthreads()",
                     "Three shuffles and lane 0 holds 80: no shared memory, no __syncthreads()")
        self.card([["归约树", "The reduction tree"],
                   ["n 个数：log₂n 层，n − 1 次加法", "n values: log₂n levels, n − 1 additions"],
                   ["顺序寻址：干活的线程连在一起，没有分化，也没有存储体冲突", "Sequential addressing: busy threads are contiguous — no divergence, no bank conflicts"],
                   ["线程束内用洗牌，线程块内用共享内存", "Shuffles within a warp, shared memory within a block"]])
