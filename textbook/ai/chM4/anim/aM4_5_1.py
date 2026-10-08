"""动画 M4.5.1（配图 M4.5.1）：同一段 softmax，两种写法，一种算得出一种算不出。
三个得分 1000、1001、1002，直接按定义算 softmax：先取指数——$e^{1000}$ 在双精度里已经是无穷，
分子分母都成了无穷，结果是 NaN。把每个得分先减去最大值再取指数，数值完全不变（分子分母同乘一个数），
却永远落在 0 到 1 之间。这就是 logsumexp 的全部内容，也是框架里"带 logits 的交叉熵"在做的事。
数都在动画里现算（numpy），与算例 M4.5.1 一致。"""
import numpy as np
from manim import *
from wq_anim import *

Z = np.array([1000.0, 1001.0, 1002.0])
ZS = Z - Z.max()
P = np.exp(ZS) / np.exp(ZS).sum()
BIG = "$e^{1000} = \\infty$"


class Lesson(Base):
    def construct(self):
        self.title("M4.5", "一个减法救回一个 softmax", "One subtraction saves the softmax")

        row = VGroup(*[Text(f"{z:.0f}", font_size=40, color=BLUE) for z in Z]).arrange(RIGHT, buff=1.4).move_to([0, 1.7, 0])
        self.play(FadeIn(row), run_time=0.8)
        self.caption("三个得分（logits）：1000、1001、1002。要把它们变成概率",
                     "Three logits: 1000, 1001, 1002. We want probabilities")

        # 错写法
        bad = VGroup(*[MathTex(r"e^{%d}" % z, font_size=40, color=RED) for z in Z]).arrange(RIGHT, buff=1.2).move_to([0, 0.4, 0])
        self.play(TransformFromCopy(row, bad), run_time=1.0)
        self.caption("按定义直接取指数——双精度最大约 $1.8\\times10^{308}$，$e^{1000}$ 早就超了",
                     "Exponentiate directly — but double precision tops out near $1.8\\times10^{308}$")
        inf_row = VGroup(*[MathTex(r"\infty", font_size=46, color=RED) for _ in Z]).arrange(RIGHT, buff=1.6).move_to([0, 0.4, 0])
        self.play(Transform(bad, inf_row), run_time=0.8)
        nan = MathTex(r"\frac{\infty}{\infty + \infty + \infty} = \mathrm{NaN}", font_size=48, color=RED).move_to([0, -1.1, 0])
        self.play(Write(nan), run_time=1.0)
        self.caption("分子分母都是无穷，结果是 NaN——训练日志里突然出现的 NaN，多半就是这么来的",
                     "Infinity over infinity is NaN — this is where those NaNs in the log come from")
        self.play(FadeOut(bad), FadeOut(nan), run_time=0.5)

        # 对写法
        minus = MathTex(r"z_i - \max_j z_j", font_size=44, color=GREEN).move_to([0, 0.5, 0])
        self.play(Write(minus), run_time=0.9)
        self.caption("把每个得分减去最大的那个：分子分母同乘 $e^{-\\max z}$，结果一个字都没变",
                     "Subtract the largest logit: numerator and denominator are scaled alike, the result is unchanged")
        shifted = VGroup(*[Text(f"{z:.0f}", font_size=40, color=GREEN) for z in ZS]).arrange(RIGHT, buff=1.6).move_to([0, -0.6, 0])
        self.play(TransformFromCopy(row, shifted), run_time=1.0)
        out = VGroup(*[Text(f"{p:.3f}", font_size=40, color=YELLOW) for p in P]).arrange(RIGHT, buff=1.6).move_to([0, -1.9, 0])
        self.play(TransformFromCopy(shifted, out), run_time=1.0)
        self.caption(f"指数最大只到 $e^0 = 1$，概率算得出来：{P[0]:.3f}、{P[1]:.3f}、{P[2]:.3f}",
                     f"The largest exponent is now $e^0 = 1$: {P[0]:.3f}, {P[1]:.3f}, {P[2]:.3f}")

        self.card([["数值稳定的三条", "Three rules for numerical stability"],
                   MathTex(r"\log\sum_i e^{z_i} = \max_j z_j + \log\sum_i e^{z_i - \max_j z_j}", font_size=36),
                   ["概率一律在对数域里算，连乘改成相加", "Keep probabilities in log space; turn products into sums"],
                   ["用框架的“带 logits 的交叉熵”，别自己先算 softmax 再取对数",
                    "Use the framework's cross-entropy-with-logits, never softmax-then-log"]])
