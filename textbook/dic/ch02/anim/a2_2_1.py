"""动画 2.2.1：串联的 NMOS 为什么慢。一个导通的 NMOS 给负载电容放电，时间常数 RC；两个同样的管子串联，电阻加倍，
放电慢一倍；把两个管子都加宽一倍，串联电阻回到 R，放电又和一个管子一样快，代价是每个输入的栅电容加倍。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
R_SYM = 2.42816091954023
GAMMA = 1.576
TAU_PS = 9.069818404407263
R_N_K = 7.303465765004228
C_FO4_FF = 10.035598275862068
CINV_FF = 1.7997844827586205
G_NAND3 = 1.5834031852472759
P_NAND3 = 4.728
B_DEC = 4.0
H_DEC = 16.0
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
RED_ = "#ff7b72"
GREEN_ = "#56d364"


def switch(w=1.0, color=BLUE_):
    """一个 NMOS 当作开关：竖线是沟道，宽度画成线条粗细。"""
    body = Line(UP * 0.45, DOWN * 0.45, color=color, stroke_width=6 * w)
    gate = Line(LEFT * 0.35 + UP * 0.35, LEFT * 0.35 + DOWN * 0.35, color=color, stroke_width=4)
    return VGroup(body, gate)


class Lesson(Base):
    def construct(self):
        self.title("2.2", "串联的管子为什么慢", "Why series transistors are slow")
        tau1 = 0.69 * R_N_K * 1e3 * C_FO4_FF * 1e-15 * 1e12        # ps
        ax = Axes(x_range=[0, 4 * tau1, tau1], y_range=[0, 1.8, 0.9], x_length=6.0, y_length=3.2, tips=False,
                  axis_config={"color": MUTED}).move_to([2.6, -0.4, 0])
        xl = Text("t", font_size=24, color=MUTED).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = MathTex(r"V_{out}", font_size=28, color=MUTED).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), FadeIn(xl, yl))

        def curve(R, color):
            return ax.plot(lambda t: 1.8 * np.exp(-t / (R * tau1 / 0.69)), x_range=[0, 4 * tau1], color=color, stroke_width=4)

        # 一个管子
        s1 = switch().move_to([-4.2, 0.2, 0])
        c = Rectangle(width=0.6, height=0.12, color=ORANGE_, fill_opacity=1).move_to([-4.2, 1.2, 0])
        lab1 = MathTex(r"R", font_size=34, color=BLUE_).next_to(s1, RIGHT)
        self.play(FadeIn(s1, c, lab1))
        self.caption("一个导通的 NMOS 给负载电容放电", "One conducting NMOS discharges the load capacitor", wait=0.2)
        k1 = curve(1.0, BLUE_)
        self.play(Create(k1, run_time=2.0, rate_func=linear))
        self.wait(0.6)
        # 两个串联
        s2 = VGroup(switch(), switch()).arrange(DOWN, buff=0.15).move_to([-4.2, 0.0, 0])
        lab2 = MathTex(r"R+R=2R", font_size=34, color=RED_).next_to(s2, RIGHT)
        self.play(ReplacementTransform(s1, s2), ReplacementTransform(lab1, lab2))
        self.caption("两个同样的管子串联：电阻加倍，放电慢一倍", "Two identical transistors in series: twice the resistance, half the speed", wait=0.2)
        k2 = curve(2.0, RED_)
        self.play(Create(k2, run_time=2.0, rate_func=linear))
        self.wait(0.8)
        # 加宽一倍
        s3 = VGroup(switch(2.0), switch(2.0)).arrange(DOWN, buff=0.15).move_to([-4.2, 0.0, 0])
        lab3 = MathTex(r"\tfrac{R}{2}+\tfrac{R}{2}=R", font_size=34, color=GREEN_).next_to(s3, RIGHT)
        self.play(ReplacementTransform(s2, s3), ReplacementTransform(lab2, lab3))
        self.caption("两个管子都加宽一倍：串联电阻回到 R", "Widen both by 2×: the series resistance is back to R", wait=0.2)
        k3 = curve(1.0, GREEN_)
        self.play(Create(k3, run_time=2.0, rate_func=linear))
        self.wait(0.6)
        cap = MathTex(r"C_{in}\ \text{per input}:\ 2\times", font_size=32, color=ORANGE_).move_to([-3.6, -2.3, 0])
        self.play(Write(cap))
        self.caption("代价：每个输入的栅电容也加倍，前一级要更用力地驱动", "The cost: each input's gate capacitance doubles too", wait=2.0)
        self.card([["等效反相器尺寸", "Equivalent-inverter sizing"],
                   ["n 个管子串联：每个加宽 n 倍", "n transistors in series: widen each n times"],
                   ["并联：每个管子单独够强（最坏情况只有一个导通）", "In parallel: each one strong enough on its own"],
                   MathTex(rf"g_{{\mathrm{{NAND}}n}}=\frac{{n+r}}{{1+r}},\quad r\approx{R_SYM:.2f}", font_size=40)])
