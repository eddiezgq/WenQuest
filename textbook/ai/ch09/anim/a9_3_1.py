"""动画 9.3.1（配图 9.3.1）：三种并行方式怎样切分同一个 4 层的模型，放到 4 块 GPU 上。
先画出完整的模型（4 层，每层一个方块）；数据并行：模型复制 4 份，数据切成 4 份，反向后梯度全归约；
张量并行：每一层竖着切成 4 片，每块 GPU 拿每层的一片，每层算完要全归约；流水线并行：按层切，每块 GPU 一层，
微批像流水一样依次流过。最后的卡片对比三者通信什么、何时通信。"""
from manim import *
from wq_anim import *

COLS = [BLUE, RED, GREEN, GOLD]


def layers(x, w=2.2, h=0.55, color=GREY_B, opacity=0.4):
    return VGroup(*[Rectangle(width=w, height=h, color=color, fill_color=color, fill_opacity=opacity).move_to([x, 1.2 - i * 0.7, 0]) for i in range(4)])


class Lesson(Base):
    def construct(self):
        self.title("9.3", "三种并行：怎样切一个模型", "Three ways to split a model")
        full = layers(0)
        labs = VGroup(*[zh(f"第 {i + 1} 层", 18).next_to(full[i], LEFT, buff=0.2) for i in range(4)])
        self.play(FadeIn(full), FadeIn(labs))
        self.caption("一个 4 层的模型，要放到 4 块 GPU 上", "A 4-layer model to be placed on 4 GPUs")
        self.play(FadeOut(labs))

        # 数据并行
        copies = VGroup(*[layers(-4.5 + g * 3, w=1.6, color=COLS[g], opacity=0.5) for g in range(4)])
        self.play(ReplacementTransform(VGroup(*[full.copy() for _ in range(4)]), copies), FadeOut(full))
        data = VGroup(*[zh(f"数据 {g + 1}/4", 18, COLS[g]).next_to(copies[g], UP, buff=0.2) for g in range(4)])
        self.play(FadeIn(data))
        ring = VGroup(*[Arrow(copies[g].get_bottom() + DOWN * 0.1, copies[(g + 1) % 4].get_bottom() + DOWN * 0.1, buff=0.1, color=YELLOW, stroke_width=3)
                        for g in range(3)])
        self.play(Create(ring))
        self.caption("数据并行：每块 GPU 一份完整模型，各算一份数据；反向后把梯度全归约", "Data parallel: a full copy per GPU, one share of data each; all-reduce gradients after backward")
        self.clear_stage()

        # 张量并行
        slices = VGroup()
        for g in range(4):
            col = VGroup(*[Rectangle(width=0.55, height=0.55, color=COLS[g], fill_color=COLS[g], fill_opacity=0.55).move_to([-0.9 + g * 0.6, 1.2 - i * 0.7, 0])
                           for i in range(4)])
            slices.add(col)
        self.play(FadeIn(slices))
        self.play(*[slices[g].animate.shift(RIGHT * (g - 1.5) * 1.6) for g in range(4)])
        sync = VGroup(*[DashedLine(slices[0][i].get_right(), slices[3][i].get_left(), color=YELLOW) for i in range(4)])
        self.play(Create(sync))
        self.caption("张量并行：每层的矩阵切成 4 片，每块 GPU 拿每层的一片；每层算完都要全归约一次", "Tensor parallel: every layer's matrices split 4 ways; an all-reduce inside every layer")
        self.clear_stage()

        # 流水线并行
        stages = VGroup(*[Rectangle(width=1.8, height=0.8, color=COLS[g], fill_color=COLS[g], fill_opacity=0.5).move_to([-4.2 + g * 2.8, 0.3, 0]) for g in range(4)])
        names = VGroup(*[zh(f"GPU {g}：第 {g + 1} 层", 18).next_to(stages[g], UP, buff=0.15) for g in range(4)])
        self.play(FadeIn(stages), FadeIn(names))
        for k in range(3):
            mb = Dot(stages[0].get_left() + LEFT * 0.4, color=YELLOW, radius=0.12)
            self.play(FadeIn(mb, run_time=0.2))
            self.play(mb.animate.move_to(stages[3].get_right() + RIGHT * 0.4), run_time=1.6, rate_func=linear)
            self.play(FadeOut(mb, run_time=0.2))
        self.caption("流水线并行：按层切，每块 GPU 一层；微批依次流过，只在相邻两块之间传激活值", "Pipeline parallel: split by layer; micro-batches flow through, activations pass between neighbours")
        self.card([["三种并行", "Three parallelisms"],
                   ["数据并行：复制模型，切数据；每步全归约梯度", "Data: replicate the model, split the data; all-reduce gradients each step"],
                   ["张量并行：切每一层；层内频繁通信，只在机器内", "Tensor: split each layer; frequent communication, within a node"],
                   ["流水线并行：按层切；只传激活值，但有气泡", "Pipeline: split by layer; only activations move, but bubbles appear"]])
