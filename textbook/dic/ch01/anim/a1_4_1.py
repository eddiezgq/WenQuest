"""动画 1.4.1（配图 1.4.1）：反相器链。最小反相器直接驱动 10 pF，RC 很大、边沿很慢；插入逐级放大的反相器链，
每级的负载约为本级输入电容的 4 倍，每级都很快，总延时从几十纳秒降到零点几纳秒。"""
from manim import *
from wq_anim import *
import numpy as np
import math

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
VDD = 1.8
VT = 0.55
KN = 8.45e-05
KP = 3.48e-05
WMIN = 0.42
LCH = 0.15
CG = 1.25e-15
CD = 1.97e-15
R_SYM = 2.42816091954023
NB = 6
GAMMA = 1.576
FOPT = 4.02218945944076
F_TOT = 5556.220811878818
NOPT4 = 6.219944109905776
T1_NS = 50.40820781233451
TN_PS = 314.78755035299287
P_HI_MW = 1.62
P_LO_MW = 0.72
V_LOW = 1.2
N_GATES = 10000.0
ALPHA = 0.1
C_GATE_FF = 5.0
F_MHZ = 100.0
# </数值>

BLUE_ = "#58a6ff"
GREEN_ = "#56d364"
ORANGE_ = "#ffa657"
RED_ = "#ff7b72"


def inv(size, color=BLUE_):
    tri = Polygon([-0.6 * size, size, 0], [-0.6 * size, -size, 0], [0.7 * size, 0, 0], color=color, stroke_width=4)
    bub = Circle(radius=0.08 + 0.04 * size, color=color, stroke_width=4).next_to(tri, RIGHT, buff=0)
    return VGroup(tri, bub)


class Lesson(Base):
    def construct(self):
        self.title("1.4", "传播延时与反相器链", "Propagation delay and the inverter chain")
        one = inv(0.25).move_to([-4.5, 1.2, 0])
        load = Rectangle(width=0.4, height=1.4, fill_color=ORANGE_, fill_opacity=0.8, stroke_width=0).move_to([4.8, 1.2, 0])
        ll = MathTex(r"C_L=10\,\mathrm{pF}", font_size=30, color=ORANGE_).next_to(load, UP)
        wire = Line(one.get_right(), load.get_left(), color=MUTED)
        self.play(FadeIn(one), Create(wire), FadeIn(load, ll))
        self.caption("最小反相器直接驱动 10 pF：RC 很大，边沿很慢", "A minimum inverter driving 10 pF directly: huge RC, very slow edge", wait=0.2)
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1.8, 0.9], x_length=8, y_length=2.2, tips=False, axis_config={"color": MUTED}).move_to([0, -1.4, 0])
        slow = ax.plot(lambda x: 1.8 * (1 - np.exp(-x * 1.2)), x_range=[0, 1], color=RED_, stroke_width=4)
        tl = MathTex(rf"t\approx{T1_NS:.0f}\,\mathrm{{ns}}", font_size=34, color=RED_).next_to(ax, RIGHT, buff=0.2).shift(UP * 0.5)
        self.play(Create(ax), Create(slow, run_time=3, rate_func=linear), Write(tl))
        self.wait(0.8)
        self.caption("插入逐级放大的反相器链，每级的负载约为本级输入电容的 4 倍", "Insert a tapered chain: each stage drives about 4× its own input capacitance", wait=0.2)
        n = int(NB)
        f = F_TOT ** (1 / n)
        stages = VGroup(*[inv(0.18 + 0.12 * i) for i in range(n)]).arrange(RIGHT, buff=0.35).move_to([0, 1.2, 0])
        labels = VGroup(*[MathTex(rf"\times{f**i:.0f}" if f ** i >= 10 else rf"\times{f**i:.1f}", font_size=22, color=MUTED).next_to(s, DOWN, buff=0.15) for i, s in enumerate(stages)])
        right = stages.get_right()[0] + 0.6
        self.play(FadeOut(wire), ReplacementTransform(one, stages[0]), LaggedStart(*[GrowFromCenter(s) for s in stages[1:]], lag_ratio=0.2),
                  FadeIn(labels), load.animate.move_to([right, 1.2, 0]), ll.animate.next_to([right, 1.9, 0], UP, buff=0.05), run_time=2.5)
        for s in stages:
            self.play(s.animate.set_color(GREEN_), run_time=0.4)
        self.wait(1.0)
        fast = ax.plot(lambda x: 1.8 * (1 - np.exp(-x * 60)), x_range=[0, 1], color=GREEN_, stroke_width=4)
        self.play(Create(fast), run_time=1.0)
        self.caption("每级都很快，总延时从几十纳秒降到零点几纳秒", "Each stage is fast: the total drops from tens of ns to a few tenths of a ns", wait=0.2)
        tf_ = VGroup(zh(f"{n} 级", 26, GREEN_), MathTex(rf"t\approx{TN_PS:.0f}\,\mathrm{{ps}}", font_size=34, color=GREEN_)).arrange(RIGHT, buff=0.15).next_to(tl, DOWN, buff=0.3)
        self.play(Write(tf_))
        self.wait(2.5)
        self.card([["反相器链", "The inverter chain"],
                   ["经验公式：每级扇出约 4", "Rule of thumb: fan-out about 4 per stage"],
                   MathTex(rf"F=\frac{{C_L}}{{C_{{in}}}}\approx{F_TOT:.0f},\quad N\approx\frac{{\ln F}}{{\ln 4}}\approx{NOPT4:.1f}", font_size=40),
                   MathTex(rf"f(\ln f-1)=\gamma\approx{GAMMA:.2f}\ \Rightarrow\ f\approx{FOPT:.1f},\ N={n}", font_size=40)])
