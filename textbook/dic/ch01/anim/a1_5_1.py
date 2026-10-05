"""动画 1.5.1（配图 1.5.1）：每次翻转的能量。充电时电源送出 CV²，一半存进电容、一半在 PMOS 上变成热；
放电时电容里的 ½CV² 在 NMOS 上变成热；每秒 αfN 次 0→1 翻转，P = αCV²fN；降压的效果与代价。"""
from manim import *
from wq_anim import *
import numpy as np

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
VIOLET_ = "#d2a8ff"


class Lesson(Base):
    def construct(self):
        self.title("1.5", "功耗：每次翻转的能量", "Power: the energy of every transition")
        supply = VGroup(Rectangle(width=2.0, height=0.9, color=BLUE_), zh("电源 Supply", 22, BLUE_)).move_to([-4.6, 1.2, 0])
        pm = VGroup(Rectangle(width=1.4, height=0.8, color=VIOLET_), zh("PMOS", 24, VIOLET_)).move_to([-1.6, 1.2, 0])
        capb = VGroup(Rectangle(width=1.2, height=2.0, color=WHITE), zh("C", 28)).move_to([1.4, 1.0, 0])
        nm = VGroup(Rectangle(width=1.4, height=0.8, color=GREEN_), zh("NMOS", 24, GREEN_)).move_to([4.4, 1.2, 0])
        arrows = VGroup(Arrow(supply.get_right(), pm.get_left(), color=MUTED), Arrow(pm.get_right(), capb.get_left(), color=MUTED),
                        Arrow(capb.get_right(), nm.get_left(), color=MUTED))
        self.play(FadeIn(supply, pm, capb, nm), Create(arrows))
        fill = Rectangle(width=1.1, height=0.01, fill_color=ORANGE_, fill_opacity=0.8, stroke_width=0).move_to(capb[0].get_bottom() + UP * 0.06)
        self.add(fill)
        self.caption("充电：电源送出 CV²，一半存在电容里，一半在 PMOS 上变成热", "Charging: the supply delivers CV², half is stored, half is burnt in the PMOS", wait=0.2)
        heat1 = VGroup(MathTex(r"\tfrac12 CV^2", font_size=32, color=RED_), zh("热 heat", 22, RED_)).arrange(RIGHT, buff=0.12).next_to(pm, DOWN)
        store = MathTex(r"\tfrac12 CV^2", font_size=32, color=ORANGE_).next_to(capb, DOWN)
        draw = MathTex(r"CV^2", font_size=32, color=BLUE_).next_to(supply, DOWN)
        self.play(fill.animate.stretch_to_fit_height(1.8, about_edge=DOWN), Write(draw), Write(heat1), Write(store), run_time=2.5)
        self.wait(0.8)
        self.caption("放电：电容里的 ½CV² 在 NMOS 上变成热", "Discharging: the stored ½CV² is burnt in the NMOS", wait=0.2)
        heat2 = VGroup(MathTex(r"\tfrac12 CV^2", font_size=32, color=RED_), zh("热 heat", 22, RED_)).arrange(RIGHT, buff=0.12).next_to(nm, DOWN)
        self.play(fill.animate.stretch_to_fit_height(0.01, about_edge=DOWN), Write(heat2), FadeOut(store), run_time=2.5)
        self.wait(0.6)
        self.caption("每秒 αfN 次 0→1 翻转：P = αCV²fN", "αfN rising (0→1) transitions per second: P = αCV²fN", wait=0.2)
        eq = MathTex(rf"P={ALPHA:g}\times {C_GATE_FF:g}\,\mathrm{{fF}}\times({VDD:g}\,\mathrm{{V}})^2\times {F_MHZ:g}\,\mathrm{{MHz}}\times {N_GATES:.0f}={P_HI_MW:.2f}\,\mathrm{{mW}}",
                     font_size=32).move_to([0, -1.1, 0])
        self.play(Write(eq), run_time=2.0)
        self.wait(1.5)
        self.caption(f"电压从 {VDD:g} V 降到 {V_LOW:g} V：功耗降到 {100 * P_LO_MW / P_HI_MW:.0f}%",
                     f"Lower the supply from {VDD:g} V to {V_LOW:g} V: power drops to {100 * P_LO_MW / P_HI_MW:.0f}%", wait=0.2)
        base = [-2.5, -2.4, 0]
        b1 = Rectangle(width=1.0, height=1.2, fill_color=BLUE_, fill_opacity=0.8, stroke_width=0).move_to(base, aligned_edge=DOWN)
        b2 = Rectangle(width=1.0, height=1.2, fill_color=GREEN_, fill_opacity=0.8, stroke_width=0).move_to([base[0] + 1.6, base[1], 0], aligned_edge=DOWN)
        self.play(FadeOut(eq), FadeIn(b1, b2))
        l1 = MathTex(rf"{VDD:g}\,\mathrm{{V}}:\ {P_HI_MW:.2f}\,\mathrm{{mW}}", font_size=28).next_to(b1, LEFT)
        self.play(b2.animate.stretch_to_fit_height(1.2 * P_LO_MW / P_HI_MW, about_edge=DOWN), FadeIn(l1), run_time=2)
        l2 = MathTex(rf"{V_LOW:g}\,\mathrm{{V}}:\ {P_LO_MW:.2f}\,\mathrm{{mW}}", font_size=28).next_to(b2, RIGHT)
        self.play(FadeIn(l2))
        self.wait(2.5)
        self.card([["功耗", "Power"],
                   ["降压最省电，但门会变慢", "Lowering VDD saves the most power, but slows the gates"],
                   MathTex(r"P_{dyn}=\alpha\,C\,V_{DD}^2\,f\,N", font_size=48),
                   ["α：每个时钟一个门输出由 0 变 1 的概率", "α: probability that a gate output rises 0→1 in a clock cycle"]])
