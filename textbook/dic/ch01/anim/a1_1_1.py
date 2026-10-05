"""动画 1.1.1（配图 1.1.1）：CMOS 反相器的开关模型。输入为 0 时 PMOS 导通，负载电容经 PMOS 充电到 VDD；
输入为 1 时 NMOS 导通，电容经 NMOS 放电；稳态时总有一个管子截止，电源到地没有直流通路。"""
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

GREEN_ = "#56d364"
ORANGE_ = "#ffa657"
RED_ = "#ff7b72"


def switch(top, bot, closed, color):
    """开关符号：闭合为直线，断开为斜线。"""
    a, b = np.array(top), np.array(bot)
    m1, m2 = a + (b - a) * 0.3, a + (b - a) * 0.7
    blade = Line(m1, m2 if closed else m2 + RIGHT * 0.45, color=color, stroke_width=6)
    return VGroup(Line(a, m1, color=color, stroke_width=5), blade, Line(m2, b, color=color, stroke_width=5))


class Lesson(Base):
    def construct(self):
        self.title("1.1", "MOSFET 开关与 CMOS 反相器", "MOSFET switches and the CMOS inverter")
        x = -1.0
        vdd = Line([x - 1, 2.3, 0], [x + 1, 2.3, 0], color=MUTED)
        gnd = Line([x - 1, -2.3, 0], [x + 1, -2.3, 0], color=MUTED)
        lv = zh("VDD", 24, MUTED).next_to(vdd, RIGHT)
        lg = zh("GND", 24, MUTED).next_to(gnd, RIGHT)
        out = Dot([x, 0, 0], color=WHITE)
        wire = Line([x, 0, 0], [x + 3.0, 0, 0], color=WHITE)
        cap_top = Line([x + 2.6, -0.6, 0], [x + 3.4, -0.6, 0], color=WHITE)
        cap_bot = cap_top.copy().shift(DOWN * 0.25)
        cap = VGroup(Line([x + 3.0, 0, 0], [x + 3.0, -0.6, 0], color=WHITE), cap_top, cap_bot,
                     Line([x + 3.0, -0.85, 0], [x + 3.0, -2.3, 0], color=WHITE), Line([x + 2.6, -2.3, 0], [x + 3.4, -2.3, 0], color=MUTED))
        lc = zh("C", 26).next_to(cap_top, RIGHT)
        self.play(Create(vdd), Create(gnd), FadeIn(lv, lg), Create(wire), Create(cap), FadeIn(lc, out))

        def stage(vin):
            p = switch([x, 2.3, 0], [x, 0, 0], vin == 0, GREEN_ if vin == 0 else MUTED)
            n = switch([x, 0, 0], [x, -2.3, 0], vin == 1, GREEN_ if vin == 1 else MUTED)
            lp = zh("PMOS", 24, GREEN_ if vin == 0 else MUTED).next_to(p, LEFT, buff=0.3)
            ln = zh("NMOS", 24, GREEN_ if vin == 1 else MUTED).next_to(n, LEFT, buff=0.3)
            li = bi([f"输入 = {vin}", f"input = {vin}"], 28, YELLOW).move_to([-5.2, 0, 0])
            return VGroup(p, n, lp, ln, li)

        def flow(points):
            path = VMobject().set_points_as_corners(points)
            dots = VGroup(*[Dot(radius=0.07, color=ORANGE_) for _ in range(6)])
            for i, d in enumerate(dots):
                d.move_to(path.point_from_proportion(i / 6))
            self.play(LaggedStart(*[MoveAlongPath(d, path, rate_func=linear) for d in dots], lag_ratio=0.15), run_time=2.5)
            return dots

        s0 = stage(0)
        self.play(FadeIn(s0))
        self.caption("输入为 0：PMOS 导通，电容经 PMOS 充电到 VDD", "Input 0: the PMOS is on and charges the load capacitor to VDD", wait=0.5)
        dots = flow([[x, 2.3, 0], [x, 0, 0], [x + 3.0, 0, 0], [x + 3.0, -0.6, 0]])
        vlab = zh(f"Vout = {VDD:.1f} V", 26, ORANGE_).move_to([x + 1.6, 0.4, 0])
        self.play(FadeOut(dots), FadeIn(vlab))
        self.wait(0.8)
        s1 = stage(1)
        self.play(ReplacementTransform(s0, s1))
        self.caption("输入为 1：NMOS 导通，电容经 NMOS 放电到地", "Input 1: the NMOS is on and discharges the capacitor to ground", wait=0.5)
        dots = flow([[x + 3.0, -0.6, 0], [x + 3.0, 0, 0], [x, 0, 0], [x, -2.3, 0]])
        v0 = zh("Vout = 0 V", 26, ORANGE_).move_to([x + 1.6, 0.4, 0])
        self.play(FadeOut(dots), Transform(vlab, v0))
        self.wait(0.6)
        self.caption("稳态时总有一个管子截止：电源到地没有直流通路", "In steady state one transistor is always off: no DC path from VDD to ground", wait=0.3)
        cross = Cross(Line([x, 2.3, 0], [x, -2.3, 0]), stroke_color=RED_, stroke_width=5).scale(0.25).move_to([x + 0.7, 1.15, 0])
        self.play(Create(cross), run_time=0.8)
        self.wait(1.5)
        self.caption("只有翻转的瞬间才有电流：这就是 CMOS 省电的原因", "Current flows only while switching: that is why CMOS saves power", wait=2.5)
        self.card([["CMOS 反相器", "The CMOS inverter"],
                   ["静态时总有一个管子截止，没有直流功耗", "One transistor is always off in steady state: no static power"],
                   ["线性区的 NMOS 相当于电阻 Ron", "In the linear region the NMOS acts as a resistor Ron"],
                   MathTex(r"R_{on}\approx\frac{1}{k_n'\frac{W}{L}(V_{DD}-V_{T})}", font_size=46)])
