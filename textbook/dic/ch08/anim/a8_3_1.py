"""动画 8.3.1（配图 8.3.1）：时钟沿推着数据走过 PI 数据通路。横轴是时间，竖线是 50 MHz 的时钟沿。
上面不插寄存器：减法、乘法、两个加法、饱和一个接一个，数据走到终点时早已过了下一个时钟沿——关键路径卡住了整个系统。
下面在乘法器后面插一级寄存器：前一级在第一个周期内走完、被寄存器收下，后一级在第二个周期内走完。数值是第 6 章综合的块延时。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
D_SUB = 3.4786
D_MUL = 11.0054
D_ADD = 7.0546999999999995
D_SAT = 0.31307947677820236
OH_NS = 0.21503770316248927
T_NS = 20.0
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
GREEN_ = "#56d364"
RED_ = "#ff7b72"


class Lesson(Base):
    def construct(self):
        self.title("8.3", "流水线：关键路径怎样卡住系统", "Pipelining: how the critical path holds back the system")
        t_max = 2 * T_NS + 2
        sx = 11.0 / t_max
        x0 = -5.6
        X = lambda t: x0 + t * sx  # noqa: E731
        edges = VGroup(*[DashedLine([X(k * T_NS), 2.6, 0], [X(k * T_NS), -3.0, 0], color=MUTED, stroke_width=1.5) for k in range(3)])
        elab = VGroup(*[Text(f"{k * T_NS:.0f} ns", font_size=16, color=MUTED).move_to([X(k * T_NS), 2.85, 0]) for k in range(3)])
        self.play(Create(edges), FadeIn(elab))
        self.caption("竖线是 50 MHz 的时钟沿，每 20 ns 一个", "Dashed lines: 50 MHz clock edges, every 20 ns", wait=0.6)

        names = [("减", D_SUB), ("乘", D_MUL), ("加", D_ADD), ("加", D_ADD), ("饱和", D_SAT)]

        def row(y, cut):
            g, t, items = VGroup(), OH_NS / 2, []
            for i, (nm, dl) in enumerate(names):
                if cut and i == 2:
                    t = T_NS + OH_NS / 2
                r = Rectangle(width=dl * sx, height=0.55, color=BLUE_, fill_opacity=0.25, stroke_width=2).move_to([X(t + dl / 2), y, 0])
                lab = Text(nm, font_size=18, color=WHITE).move_to(r)
                g.add(r, lab)
                items.append((t, t + dl))
                t += dl
            return g, items, t

        top, it_top, end_top = row(1.3, False)
        tl = Text("不插寄存器", font_size=20, color=ORANGE_).move_to([X(0) - 0.05, 2.1, 0], aligned_edge=LEFT)
        self.play(FadeIn(top), FadeIn(tl))
        dot = Dot([X(OH_NS / 2), 0.85, 0], color=ORANGE_, radius=0.11)
        self.add(dot)
        self.play(dot.animate.move_to([X(end_top), 0.85, 0]), run_time=3.0, rate_func=linear)
        miss = Text("%.1f ns 才算完，错过了 20 ns 的时钟沿" % (end_top + OH_NS / 2), font_size=20, color=RED_).move_to([X(end_top) - 1.6, 0.35, 0])
        self.play(FadeIn(miss), Indicate(top[2], color=RED_), Indicate(top[4], color=RED_))
        self.caption("关键路径一个周期走不完，整个系统只能降频", "The critical path cannot finish in one cycle; the whole chip must slow down", wait=1.0)

        bot, it_bot, end_bot = row(-1.6, True)
        bl = Text("乘法器后面插一级寄存器", font_size=20, color=GREEN_).move_to([X(0) - 0.05, -0.8, 0], aligned_edge=LEFT)
        reg = Rectangle(width=0.18, height=0.9, color=GREEN_, fill_opacity=0.9).move_to([X(T_NS), -1.6, 0])
        self.play(FadeIn(bot), FadeIn(bl), FadeIn(reg))
        d2 = Dot([X(OH_NS / 2), -2.05, 0], color=GREEN_, radius=0.11)
        self.add(d2)
        self.play(d2.animate.move_to([X(it_bot[1][1]), -2.05, 0]), run_time=1.6, rate_func=linear)
        self.play(d2.animate.move_to([X(T_NS), -2.05, 0]), run_time=0.4)
        self.caption("前一级 %.1f ns，赶在时钟沿前被寄存器收下" % (D_SUB + D_MUL + OH_NS),
                     "Stage 1 takes %.1f ns and is captured before the edge" % (D_SUB + D_MUL + OH_NS), wait=0.6)
        self.play(d2.animate.move_to([X(end_bot), -2.05, 0]), run_time=1.6, rate_func=linear)
        ok = Text("后一级 %.1f ns，第二个周期内走完" % (2 * D_ADD + D_SAT + OH_NS), font_size=20, color=GREEN_).move_to([X(end_bot) - 1.2, -2.6, 0])
        self.play(FadeIn(ok))
        self.caption("每个周期仍出一个结果，只是晚一拍", "Still one result per cycle, just one cycle later", wait=1.5)
        self.card([["流水线", "Pipelining"],
                   ["周期由最长的一级决定", "The period is set by the longest stage"],
                   ["代价：一拍延迟 + 一排触发器", "Cost: one cycle of latency + a row of flip-flops"],
                   ["反馈回路里不能插（8.3.2 节）", "Never inside a feedback loop (Section 8.3.2)"]])
