"""动画 17.3.1（配图 17.3.1）：智能体的一轮循环，以及错误怎样乘起来。

循环四步：**规划**（下一步做什么）、**调工具**（取数、改文件、跑测试）、**读结果**
（工具回了什么）、**修正**（对不对，要不要重来）。转一圈叫一步。

要紧的是第二件事：每一步都可能出错，而这些小毛病是**乘**起来的。每步出错率 $p$、走 $n$ 步，
整件事做成的概率就是 $(1-p)^n$。这不是经验规律，是把"每一步都得对"写成概率的恒等式。
于是有一条很硬的结论：**想让智能体走得更长，不能靠多试几次，得把每一步做得更准。**

画面上的数都是现算的。渲染服务只允许 manim、wq_anim、numpy、math、random，不能 import 章内模块，
所以这里按 code/_ch17.py 的同一套做法把最小的一份重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

PS = (0.01, 0.02, 0.05, 0.10)
NMAX = 60


def plain(p, n):
    return (1 - p) ** n


def steps_for(p, target=0.8):
    return np.log(target) / np.log(1 - p)


STEPS80 = {p: steps_for(p) for p in PS}
COLS = {0.01: BLUE, 0.02: GREEN, 0.05: YELLOW, 0.10: RED}


class Lesson(Base):
    def construct(self):
        self.title("17.3", "智能体：一圈一圈走，错误一步一步乘",
                   "The agent loop: errors multiply, step by step")

        # ---- 一轮循环的四步
        names = [("规划", "plan"), ("调工具", "act"), ("读结果", "observe"), ("修正", "revise")]
        subs = [("下一步做什么", "what to do next"),
                ("取数、改文件、跑测试", "fetch, edit, run tests"),
                ("工具回了什么", "what came back"),
                ("对不对，要不要重来", "right? retry?")]
        pos = [[-2.6, 1.2, 0], [2.6, 1.2, 0], [2.6, -1.2, 0], [-2.6, -1.2, 0]]
        boxes = VGroup()
        for (zh, en), (szh, sen), p in zip(names, subs, pos):
            r = RoundedRectangle(width=3.2, height=1.3, corner_radius=0.14,
                                 color=BLUE, fill_opacity=0.08).move_to(p)
            t1 = Text(zh, font_size=26).move_to(np.array(p) + np.array([0, 0.22, 0]))
            t2 = Text(szh, font_size=16, color=GREY).move_to(np.array(p) + np.array([0, -0.26, 0]))
            boxes.add(VGroup(r, t1, t2))
        self.play(*[FadeIn(b) for b in boxes], run_time=1.0)
        self.caption("智能体做事不是一次出手，是一圈一圈转：规划、调工具、读结果、修正",
                     "An agent does not answer in one shot; it loops: plan, act, observe, revise")

        arrows = VGroup()
        for i in range(4):
            a = boxes[i]
            b = boxes[(i + 1) % 4]
            arrows.add(Arrow(a.get_center(), b.get_center(), buff=1.75,
                             color=GREY, stroke_width=4, max_tip_length_to_length_ratio=0.12))
        self.play(*[GrowArrow(a) for a in arrows], run_time=1.0)
        self.caption("转一圈算一步。一件真事要转几十圈——读文件、改代码、跑测试、看报错、再改",
                     "One lap is one step. A real task takes dozens: read, edit, test, read the error, edit again")

        # ---- 每一步都可能出错
        marks = VGroup(*[Text("×", font_size=34, color=RED).move_to(
            boxes[i].get_corner(UR) + np.array([-0.18, -0.18, 0])) for i in range(4)])
        self.play(*[FadeIn(m) for m in marks], run_time=0.8)
        self.caption("每一步都可能出错：工具挑错了、参数填错了、结果读歪了。"
                     "单看一步，出错率也许只有百分之几",
                     "Every step can go wrong: wrong tool, wrong argument, misread result. "
                     "Per step that may be only a few percent")

        self.clear_stage()

        # ---- 指数衰减
        ax = Axes(x_range=[0, NMAX, 10], y_range=[0, 1.05, 0.2],
                  x_length=9.0, y_length=4.2,
                  axis_config={"include_tip": False, "color": GREY}).shift(DOWN * 0.3)
        xlab = Text("一共走几步", font_size=20).next_to(ax, DOWN, buff=0.25)
        ylab = Text("整件事做成的概率", font_size=20).rotate(PI / 2).next_to(ax, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xlab), FadeIn(ylab), run_time=0.9)
        self.caption("把每步出错率定下来，整件事做成的概率就是 $(1-p)^n$——"
                     "这是个恒等式，不用做实验",
                     "Fix the per-step error rate and the whole task succeeds with probability "
                     "$(1-p)^n$ — an identity, not an experiment")

        line80 = DashedLine(ax.c2p(0, 0.8), ax.c2p(NMAX, 0.8), color=GREY, stroke_width=2)
        t80 = Text("保住 80%", font_size=18, color=GREY).next_to(line80, UP, buff=0.08).shift(RIGHT * 3.2)
        self.play(Create(line80), FadeIn(t80), run_time=0.6)

        for p in PS:
            curve = ax.plot(lambda n, p=p: plain(p, n), x_range=[0, NMAX], color=COLS[p],
                            stroke_width=4)
            lab = Text(f"每步出错 {p * 100:.0f}%", font_size=19, color=COLS[p])
            lab.move_to(ax.c2p(NMAX * 0.82, plain(p, NMAX * 0.82) + 0.06))
            self.play(Create(curve), FadeIn(lab), run_time=0.8)
            if STEPS80[p] <= NMAX:
                d = Dot(ax.c2p(STEPS80[p], 0.8), color=COLS[p], radius=0.08)
                self.play(FadeIn(d), run_time=0.3)

        self.caption(f"每步出错 5% 时，走到第 {STEPS80[0.05]:.0f} 步就跌破 80%；"
                     f"降到 1%，能走 {STEPS80[0.01]:.0f} 步——"
                     f"出错率降到五分之一，能走的步数长五倍",
                     f"At 5% per step you drop below 80% after {STEPS80[0.05]:.0f} steps; "
                     f"at 1% you get {STEPS80[0.01]:.0f} — five times lower error buys five times the length")

        self.card([["这一节要记住的", "What to take away"],
                   ["智能体一圈一圈转，每一步的小毛病是乘起来的：成功率 $(1-p)^n$",
                    "The agent loops, and per-step errors multiply: success is $(1-p)^n$"],
                   ["想走得更长，首先得把每一步做得更准，而不是多试几次",
                    "To go further, make each step more accurate — trying more times is the weaker lever"],
                   ["救法有三种：整件事重试、每步自检、末端校验；每一种能买回多少，都算得出来",
                    "Three remedies — retry, per-step check, final verifier — and each one's value can be computed"],
                   ["校验器会把对的判成错，误判率一高就开始帮倒忙",
                    "A verifier also rejects correct results; too many false rejections and it backfires"]])
