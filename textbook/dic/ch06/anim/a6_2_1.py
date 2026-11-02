"""动画 6.2.1（配图 6.2.1）：进位怎样走。上面是 16 位行波进位加法器，进位从最低位一位一位往上传，要 16 步；
下面是 Kogge–Stone 前缀树，每一级每一位把“已经知道的范围”向低位扩大一倍（1、2、4、8、16 位），4 级就全部知道。
数值是 SKY130 综合的 16 位、32 位延时。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
RCA16_PS = 1847.2
KS16_PS = 833.7
RCA32_PS = 3728.2
KS32_PS = 1038.6
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
GREEN_ = "#56d364"
N = 16


class Lesson(Base):
    def construct(self):
        self.title("6.2", "进位怎样走：行波与前缀树", "How the carry travels: ripple versus prefix tree")
        w = 0.62
        xs = [(N - 1 - i - (N - 1) / 2) * w for i in range(N)]
        top = VGroup(*[Square(side_length=0.5, color=MUTED).move_to([x, 1.5, 0]) for x in xs])
        bot = VGroup(*[Square(side_length=0.5, color=MUTED).move_to([x, -1.0, 0]) for x in xs])
        lt = Text("行波进位 / ripple carry", font_size=24, color=ORANGE_).move_to([0, 2.35, 0])
        lb = Text("Kogge–Stone 前缀树 / prefix tree", font_size=24, color=BLUE_).move_to([0, -0.15, 0])
        nums = VGroup(*[Text(str(i), font_size=16, color=MUTED).next_to(top[i], DOWN, buff=0.08) for i in range(N)])
        self.play(Create(top), Create(bot), FadeIn(lt, lb, nums))
        self.caption("每一位都要知道：低位来不来进位", "Every bit must learn whether a carry arrives from below", wait=0.8)
        for i in range(N):
            self.play(top[i].animate.set_fill(ORANGE_, opacity=0.8), run_time=0.18, rate_func=linear)
        self.caption(f"行波：16 步，SKY130 综合约 {RCA16_PS:.0f} ps", f"Ripple: 16 steps, about {RCA16_PS:.0f} ps in SKY130", wait=1.0)
        self.caption("前缀树：每一级把每一位“看得到”的范围加倍", "Prefix tree: each level doubles how far every bit can see", wait=0.3)
        bars = VGroup()
        for lv, span in enumerate((1, 2, 4, 8, 16)):
            new, done = VGroup(), []
            for i in range(N):
                lo = max(0, i - span + 1)
                x0, x1 = xs[i] + 0.25, xs[lo] - 0.25
                new.add(Line([x1, -1.45 - 0.0, 0], [x0, -1.45, 0], color=BLUE_, stroke_width=4).shift(DOWN * 0.13 * lv))
                if lo == 0 and i < span and i >= span // 2:
                    done.append(bot[i])
            lab = Text(f"第 {lv} 级：看得到 {span} 位 / level {lv}: sees {span} bits" if lv else "开始：只看得到自己 / start: sees itself",
                       font_size=20, color=WHITE).move_to([0, -2.45, 0])
            self.play(FadeIn(new), FadeIn(lab), *[b.animate.set_fill(GREEN_, opacity=0.8) for b in done], run_time=0.8)
            self.wait(0.5)
            self.play(FadeOut(lab), run_time=0.3)
            bars.add(new)
        self.caption(f"前缀树：log2 16 = 4 级，约 {KS16_PS:.0f} ps", f"Prefix tree: log2 16 = 4 levels, about {KS16_PS:.0f} ps", wait=1.2)
        self.caption(f"位宽加倍到 32：行波 {RCA32_PS:.0f} ps，前缀树 {KS32_PS:.0f} ps", f"At 32 bits: ripple {RCA32_PS:.0f} ps, prefix {KS32_PS:.0f} ps", wait=1.5)
        self.card([["并行前缀加法器", "Parallel-prefix adders"],
                   MathTex(r"(G,P)\circ(G',P')=(G+PG',\;PP')", font_size=40),
                   ["满足结合律 → 可以搭成 log₂n 级的树", "Associative → can be built as a tree of log₂n levels"],
                   ["代价：运算更多、连线更长（6.2.3 节）", "Cost: more operators, longer wires (Section 6.2.3)"]])
