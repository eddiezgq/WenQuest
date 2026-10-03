"""动画 3.7.1（配图 3.7.1）：线程束调度器在等待显存时切换线程束。一个调度器带 4 个线程束，
每个线程束“读一次显存，再做 4 条算术”；显存延迟取 12 个周期（为了看得清，远短于真实的约 700 个周期）。
数据由与 GPU 执行模拟器（_gpusim.py，部分 ①）相同的规则逐周期算出：贪心后取最老的调度策略。"""
from manim import *
from wq_anim import *

N, K, L, SPAN = 4, 4, 12, 48


def trace():
    """与 _gpusim.schedule(policy='gto') 同样的规则，只算 SPAN 个周期。"""
    pc, ready, cur, rows = [0] * N, [0] * N, 0, [[] for _ in range(N)]
    for c in range(SPAN):
        def can(w):
            return pc[w] == 0 or c >= ready[w]
        pick = cur if can(cur) else next((w for w in range(N) if can(w)), -1)
        for w in range(N):
            rows[w].append("I" if w == pick else ("M" if pc[w] and c < ready[w] else "R"))
        if pick >= 0:
            cur = pick
            if pc[pick] == 0:
                ready[pick], pc[pick] = c + L, 1
            else:
                pc[pick] = 0 if pc[pick] == K else pc[pick] + 1
    return rows


class Lesson(Base):
    def construct(self):
        self.title("3.7", "调度器怎样把显存延迟藏起来", "How the warp scheduler hides memory latency")
        rows = trace()
        cw, ch = 0.25, 0.5
        x0, y0 = -5.4, 1.6
        names = VGroup(*[bi([f"线程束 {w}", f"warp {w}"], size=20).move_to([x0 - 0.9, y0 - w * 0.7, 0]) for w in range(N)])
        self.play(FadeIn(names))
        self.caption("每个线程束：读一次显存，再做 4 条算术；数据要 12 个周期才回来", "Each warp: one load, then 4 arithmetic ops; data takes 12 cycles")
        clock = VGroup(bi(["周期", "cycle"], size=22), DecimalNumber(0, num_decimal_places=0, font_size=34)).arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=1.4)
        self.play(FadeIn(clock))
        busy = 0
        for c in range(SPAN):
            cells = []
            for w in range(N):
                st = rows[w][c]
                col = {"I": BLUE, "M": GOLD_E, "R": GREY_D}[st]
                cells.append(Rectangle(width=cw * 0.92, height=ch * 0.8, stroke_width=0, fill_color=col, fill_opacity=0.9)
                             .move_to([x0 + c * cw, y0 - w * 0.7, 0]))
            busy += any(rows[w][c] == "I" for w in range(N))
            self.play(*[FadeIn(r) for r in cells], run_time=0.12)
            clock[1].set_value(c + 1)
            if c == 4:
                self.caption("蓝：发射；金：等数据；灰：准备好但没轮到", "Blue: issue; gold: waiting for data; grey: ready, not picked", wait=0.8)
            if c == 9:
                self.caption("4 个线程束都在等数据：调度器只能空闲", "All 4 warps wait for data: the scheduler idles", wait=0.8)
            if c == 17:
                self.caption("线程束 0 又去读显存，调度器立刻改发线程束 1——切换没有开销", "Warp 0 loads again; the scheduler switches to warp 1 at no cost", wait=0.8)
        self.caption(f"{SPAN} 个周期里有 {busy} 个在发射指令：开头大家同时等数据，是冷启动", f"{busy} of {SPAN} cycles issue: the idle start is a cold start", wait=1.2)
        self.caption("进入稳态后每个周期都在发射：4 个线程束已够藏住 12 个周期的延迟", "In steady state every cycle issues: 4 warps hide a 12-cycle latency", wait=1.2)
        self.card([["延迟隐藏", "Latency hiding"],
                   MathTex(r"U \approx \min\!\left(1,\ \frac{n\,(k+1)}{L+k}\right)", font_size=44),
                   ["线程束越多、每次读显存后的算术越多，延迟藏得越好", "More warps and more arithmetic per load hide latency better"]])
