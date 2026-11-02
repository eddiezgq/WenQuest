"""动画 57.6.1（配图 57.6.3）：时间定额的组成（式 57.6.1、57.6.2）——SH-101 粗车：机动时间 4.73 min（各工步按切削用量算）、
辅助时间 2.90 min（装卸、测量、换刀、顶尖进退），布置工作地与休息、生理需要 α + β = 8%（0.61 min），单件时间 8.24 → 定额 8.5 min；
准备与终结 30 min 分摊到 100 件（0.30 min），单件计算时间 8.8 min。数值同程序 57.6.1。"""
from manim import *
from wq_anim import *
import numpy as np

S = 1.15                   # 1 min = 1.15 单位


class Lesson(Base):
    def construct(self):
        self.title("57.6", "一件 SH-101 粗车要多长时间", "How long one rough-turned SH-101 takes")
        x = -5.2
        y = 0.3
        parts = [(4.73, STEEL, "机动 4.73", "各工步的走刀长度 ÷（转速 × 进给量）相加", "machining: L/(n f) for each pass"),
                 (2.90, ORANGE, "辅助 2.90", "装卸两次、量 6 处、换刀对刀、顶尖进退", "handling, measuring, tool change"),
                 (0.61, MUTED, "α+β", "布置工作地 3% + 休息与生理 5%，按作业时间计", "servicing and rest 8%"),
                 (0.30, GREEN, "Tz/n", "准备与终结 30 min ÷ 批量 100", "set-up 30 min / batch 100")]
        acc = 0.0
        for k, (t, c, lab, z, e) in enumerate(parts):
            r = Rectangle(width=t * S, height=0.8, color=c, fill_opacity=0.75, stroke_width=1).move_to(np.array([x + (acc + t / 2) * S, y, 0]))
            l = zh(lab, 20, WHITE).move_to(r) if t > 1 else zh(lab, 18, c).next_to(r, UP, buff=0.1)
            self.play(GrowFromEdge(r, LEFT), FadeIn(l), run_time=0.9)
            self.caption(z, e)
            acc += t
            if k == 2:
                td = Brace(Line(np.array([x, y - 0.4, 0]), np.array([x + acc * S, y - 0.4, 0])), DOWN, color=WHITE)
                self.play(GrowFromCenter(td), FadeIn(zh("单件时间 t_d = 8.24 → 定额 8.5 min", 22, WHITE).next_to(td, DOWN, buff=0.1)))
        tc = zh("单件计算时间 t_c = 8.5 + 0.30 = 8.8 min", 24, YELLOW).move_to(np.array([0, 2.0, 0]))
        self.play(FadeIn(tc))
        self.caption("机动时间只占一半多；减少辅助时间往往比提高切削速度更有效", "Machining is only about half; cut the handling first")
        self.card([["t_d = (t_b + t_a)(1 + (α+β)/100)，t_c = t_d + T_z/n", "t_d and t_c"],
                   ["时间定额是排产、核算成本、找瓶颈的依据", "Standards drive scheduling, costing and bottlenecks"]])
