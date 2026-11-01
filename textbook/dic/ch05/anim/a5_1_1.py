"""动画 5.1.1（配图 5.1.2）：短路电流。输入从 0 爬到 VDD 的途中，在 VTn 与 VDD − |VTp| 之间两个管子同时导通，
电流从电源经 PMOS、NMOS 直通到地。按 Veendrick 的空载近似，直通电流是较弱的那个管子的饱和电流，形如一个“帐篷”；
输入越慢，帐篷越宽，直通的电荷越多。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
VDD = 1.8
VTN = 0.55
VTP = 0.55
BETA_UA = 236.59999999999997
FO4_PS = 50.5733074229749
SC1 = 2.146417910447761
SC8 = 6.065925407925408
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
GREEN_ = "#56d364"
RED_ = "#ff7b72"


def isc(vin):
    """空载反相器的直通电流（μA）：两管中较弱者的饱和电流。"""
    a = BETA_UA / 2 * max(0.0, vin - VTN) ** 2
    b = BETA_UA / 2 * max(0.0, VDD - vin - VTP) ** 2
    return min(a, b)


class Lesson(Base):
    def construct(self):
        self.title("5.1", "短路电流：两个管子同时导通", "Short-circuit current: both transistors on")
        ax1 = Axes(x_range=[0, 400, 100], y_range=[0, VDD, 0.9], x_length=5.4, y_length=2.4, tips=False,
                   axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}).move_to([-3.3, 0.4, 0])
        ax2 = Axes(x_range=[0, 400, 100], y_range=[0, 20, 10], x_length=5.4, y_length=2.4, tips=False,
                   axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}).move_to([3.3, 0.4, 0])
        l1 = Text("Vin / V", font_size=20, color=MUTED).next_to(ax1, UP, buff=0.1)
        l2 = Text("I / μA", font_size=20, color=MUTED).next_to(ax2, UP, buff=0.1)
        x1 = Text("t / ps", font_size=20, color=MUTED).next_to(ax1.x_axis, DOWN, buff=0.35)
        x2 = Text("t / ps", font_size=20, color=MUTED).next_to(ax2.x_axis, DOWN, buff=0.35)
        band = Rectangle(width=5.4, height=2.4 * (VDD - VTP - VTN) / VDD, stroke_width=0, fill_color=ORANGE_, fill_opacity=0.18)
        band.move_to(ax1.c2p(200, (VTN + VDD - VTP) / 2))
        bl = Text("两管都导通", font_size=20, color=ORANGE_).next_to(band, LEFT, buff=0.1).shift(RIGHT * 2.0)
        self.play(Create(ax1), Create(ax2), FadeIn(l1, l2, x1, x2))
        self.play(FadeIn(band), FadeIn(bl))
        self.caption("输入在 VTn 到 VDD − |VTp| 之间时，NMOS、PMOS 都导通", "Between VTn and VDD − |VTp| both transistors conduct", wait=1.0)
        for tin, col, name in ((50, BLUE_, "50 ps"), (300, RED_, "300 ps")):
            ts = np.linspace(0, 400, 200)
            vin = np.clip(ts / tin, 0, 1) * VDD
            k = ValueTracker(0)
            ramp = always_redraw(lambda: ax1.plot_line_graph(ts[: max(2, int(k.get_value()))], vin[: max(2, int(k.get_value()))],
                                                              add_vertex_dots=False, line_color=col, stroke_width=4))
            cur = always_redraw(lambda: ax2.plot_line_graph(ts[: max(2, int(k.get_value()))], [isc(v) for v in vin[: max(2, int(k.get_value()))]],
                                                             add_vertex_dots=False, line_color=col, stroke_width=4))
            tag = Text(f"tin = {name}", font_size=22, color=col).move_to([5.4, 2.2 - (0.4 if tin > 100 else 0), 0])
            self.add(ramp, cur)
            self.play(FadeIn(tag), k.animate.set_value(200), run_time=3, rate_func=linear)
            area = ax2.get_area(ax2.plot(lambda t, tin=tin: isc(min(1, t / tin) * VDD), x_range=[0, min(400, tin)]), color=col, opacity=0.3)
            self.play(FadeIn(area))
            ramp.clear_updaters()
            cur.clear_updaters()
        self.caption("输入慢 6 倍，直通的电荷也多 6 倍：短路能量与输入转换时间成正比", "Six times slower input, six times more shoot-through charge", wait=1.5)
        self.caption(f"有负载时（仿真）：输入 1 个 FO4 约 {SC1:.0f} %，8 个 FO4 约 {SC8:.0f} %", f"With a load (simulation): about {SC1:.0f} % at 1 FO4, {SC8:.0f} % at 8 FO4", wait=1.5)
        self.card([["短路功耗", "Short-circuit power"],
                   MathTex(r"E_{sc}\approx\frac{\beta}{12}\,(V_{DD}-2V_T)^3\,t_{in}", font_size=40),
                   ["输入、输出边沿相当时只占百分之几", "Only a few percent when input and output edges match"],
                   ["VDD < VTn + |VTp| 时没有短路电流", "No short-circuit current when VDD < VTn + |VTp|"]])
