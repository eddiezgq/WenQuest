"""动画 30.4.1（配图 30.4.1）：从任务书到工厂，再到用户的工位。
(1) 设计流程（V 字形）：左边一路往下分解（任务书 → 构型 → 尺寸与模组 → 零件设计），右边一路往上验证
    （关节测试台 → 整机标定（实验 26）→ 负载跑合（实验 28）→ 设计发布、物料清单进 ERP），每一层左右对应。
(2) 用户选型：零件库 35 台机械臂 → 负载 ≥ 5 kg 且臂展够工位：14 台 → 能与人同场：7 台；
    最重的 GR-302（成品约 11 kg）连 12.5 kg 的协作臂都只剩 4% 裕量，留给人工 + 吊具；WQ-CR5 搬其余的零件。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("30.4", "设计流程、评审与选型", "Design process, reviews and selection")
        left = [("设计任务书", "30.1"), ("构型", "30.2"), ("尺寸与模组", "30.3"), ("零件设计", "第 31～34 章")]
        right = [("关节测试台", "实验 25"), ("整机标定", "实验 26"), ("负载跑合", "实验 28"), ("设计发布、物料清单进 ERP", "数字工厂")]
        L = VGroup()
        R = VGroup()
        for i, (a, b) in enumerate(left):
            L.add(VGroup(RoundedRectangle(width=3.2, height=0.7, corner_radius=0.1, color=STEEL, fill_opacity=0.25),
                         zh(a, 22, INK)).move_to([-4.6 + 0.7 * i, 1.5 - 1.0 * i, 0]))
        for i, (a, b) in enumerate(right):
            R.add(VGroup(RoundedRectangle(width=3.6, height=0.7, corner_radius=0.1, color=GREEN, fill_opacity=0.25),
                         zh(a, 22, INK)).move_to([1.2 + 0.6 * i, -1.5 + 1.0 * i, 0]))
        for m in L:
            m[1].move_to(m[0])
        for m in R:
            m[1].move_to(m[0])
        self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.2) for m in L], lag_ratio=0.3), run_time=1.6)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in R], lag_ratio=0.3), run_time=1.6)
        pairs = [(3, 0), (2, 1), (1, 2), (0, 3)]
        links = VGroup(*[DashedLine(L[i].get_right(), R[j].get_left(), color=YELLOW, stroke_width=2) for i, j in pairs])
        self.play(Create(links), run_time=1.2)
        self.caption("左边分解，右边验证：每一层的数在右边对应的那一层上测出来，对不上就回到左边改",
                     "Decompose on the left, verify on the right; each level's numbers are measured on its partner, and a mismatch sends you back", wait=2.0)
        self.clear_stage()
        # (2) 选型的漏斗
        stages = [("零件库的机械臂", 35), ("负载 ≥ 5 kg、臂展够工位", 14), ("能与人同场（协作）", 7)]
        bars = VGroup()
        for i, (n, k) in enumerate(stages):
            w = 0.25 * k
            b = Rectangle(width=w, height=0.75, color=STEEL, fill_opacity=0.5).move_to([-1.0, 1.4 - 1.1 * i, 0])
            t = zh(f"{n}：{k} 台", 24, INK).next_to(b, RIGHT, buff=0.25)
            bars.add(VGroup(b, t))
            self.play(GrowFromCenter(b), FadeIn(t), run_time=0.7)
        dec = VGroup(zh("最重的第二级大齿轮 GR-302（成品约 11 kg）+ 夹爪：12.5 kg 的协作臂也只剩 4% 裕量", 22, RED),
                     zh("→ GR-302 留给人工 + 吊具；WQ-CR5 搬其余零件，围栏都不用", 24, YELLOW)).arrange(DOWN, aligned_edge=LEFT).move_to([0, -2.0, 0])
        fit(dec, 12.5)
        self.play(FadeIn(dec), run_time=1.0)
        self.caption("选型先算最重的件；不是每个零件都得交给机器人",
                     "Selection starts with the heaviest part; not every part has to go to the robot", wait=2.0)
        self.card([["设计流程与选型", "Design process and selection"],
                   ["V 字流程：分解、实现、逐层验证", "The V process: decompose, build, verify level by level"],
                   ["设计结果写进物料清单，成本、工时都从这里来", "The design ends up in the bill of materials, where cost and hours come from"],
                   ["选型：最重的件、够得着、能否与人同场、节拍", "Selection: heaviest part, reach, sharing space with people, cycle time"]])
