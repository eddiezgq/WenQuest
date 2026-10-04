"""动画 4.6.1（配图 4.6.1）：合并访问与非合并访问时的内存事务。一个线程束（为清楚只画 8 个线程，每个读 4 字节）：
连续读时 8 个地址落在 1 个 32 字节扇区里；跨步 6 个元素读时，8 个地址散在 6 个扇区里，要搬 6 个扇区，搬来的数据大部分用不上。"""
from manim import *
from wq_anim import *

N = 8


class Lesson(Base):
    def construct(self):
        self.title("4.6", "合并访问：一次搬运，大家共用", "Coalescing: one transfer shared by all")
        lanes = VGroup(*[Circle(0.17, color=GOLD, fill_opacity=0.9).move_to(np.array([-4.2 + i * 0.75, 2.2, 0])) for i in range(N)])
        nums = VGroup(*[Text(str(i), font_size=16, color=BLACK).move_to(c) for i, c in enumerate(lanes)])
        self.play(FadeIn(lanes), FadeIn(nums))
        self.caption("一个线程束里的线程（只画 8 个），每个要读一个 4 字节的数", "Threads of a warp (8 shown), each reading a 4-byte value")
        sector_w = 1.6
        mem = VGroup(*[Rectangle(width=sector_w, height=0.6, stroke_width=1.5, color=GREY_B).move_to(np.array([-5.2 + (k + 0.5) * sector_w, -0.6, 0]))
                       for k in range(7)])
        mtext = Text("显存：每格是一个 32 字节扇区（8 个数）", font_size=20, color=GREY_B).next_to(mem, DOWN, buff=0.25)
        self.play(Create(mem), FadeIn(mtext))

        def access(stride, label):
            arrows, moved = VGroup(), set()
            for i in range(N):
                idx = i * stride
                k, off = divmod(idx, 8)
                if k >= len(mem):
                    continue
                x = mem[k].get_left()[0] + (off + 0.5) * sector_w / 8
                arrows.add(Arrow(lanes[i].get_bottom(), np.array([x, -0.3, 0]), buff=0.05, stroke_width=2.5, color=GOLD, max_tip_length_to_length_ratio=0.08))
                moved.add(k)
            self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1), run_time=1.2)
            hl = [mem[k].animate.set_fill(BLUE, opacity=0.6) for k in sorted(moved)]
            self.play(*hl, run_time=0.8)
            cnt = Text(label.format(len(moved)), font_size=26, color=BLUE).to_edge(DOWN, buff=1.6)
            self.play(Write(cnt))
            self.wait(1.2)
            self.play(FadeOut(arrows), FadeOut(cnt), *[m.animate.set_fill(BLUE, opacity=0) for m in mem], run_time=0.6)

        self.caption("连续读：第 i 个线程读第 i 个数", "Contiguous: thread i reads element i")
        access(1, "8 个数落在 {} 个扇区：全部有用")
        self.caption("跨步读：第 i 个线程读第 6i 个数", "Strided: thread i reads element 6i")
        access(6, "跨步 6：要搬 {} 个扇区，大部分数据白搬")
        self.card([["合并访问", "Coalesced access"],
                   ["相邻的线程读相邻的地址：一个线程束只搬最少的扇区", "Adjacent threads, adjacent addresses: the fewest sectors per warp"],
                   ["有效带宽比 = 请求的字节 ÷ 搬运的字节", "Efficiency = bytes requested ÷ bytes moved"]])
