"""动画 1.2.1（配图 1.2.1）：电压传输特性。缓慢增大输入，逐点画出输出，同时标出两个管子的工作区；
两管同时饱和处曲线几乎竖直，即开关阈值 VM；斜率为 −1 的两点定出 VIL、VIH 和噪声容限。
曲线用与书中相同的平方律模型逐点求解（参数见“数值”块）。"""
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


def ids(k, w, vov, vds):
    """平方律漏极电流（与 conventions/mos.py 相同）。"""
    if vov <= 0 or vds <= 0:
        return 0.0
    kk = k * w / LCH
    return kk * (vov * vds - vds * vds / 2) if vds < vov else kk / 2 * vov * vov


def vout(vin, wn, wp):
    lo, hi = 0.0, VDD
    for _ in range(60):
        mid = (lo + hi) / 2
        if ids(KN, wn, vin - VT, mid) - ids(KP, wp, VDD - vin - VT, VDD - mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def region(vgs, vds):
    return "off" if vgs <= VT else ("lin" if vds < vgs - VT else "sat")


class Lesson(Base):
    def construct(self):
        self.title("1.2", "电压传输特性与噪声容限", "Voltage transfer characteristic and noise margins")
        ax = Axes(x_range=[0, 1.8, 0.3], y_range=[0, 1.8, 0.3], x_length=6.0, y_length=4.0, tips=False,
                  axis_config={"color": MUTED, "include_numbers": True, "font_size": 22, "decimal_number_config": {"num_decimal_places": 1}}).shift(LEFT * 1.6 + UP * 0.35)
        xl = MathTex("V_{in}", font_size=30).next_to(ax.x_axis, DOWN, buff=0.35).align_to(ax.x_axis, RIGHT)
        yl = MathTex("V_{out}", font_size=30).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), FadeIn(xl, yl))
        wn, wp = WMIN, WMIN * R_SYM
        vs = np.linspace(0, VDD, 361)
        vo = np.array([vout(v, wn, wp) for v in vs])
        t = ValueTracker(0)
        idx = lambda: int(round(t.get_value() * 360))
        curve = always_redraw(lambda: ax.plot_line_graph(vs[: max(2, idx() + 1)], vo[: max(2, idx() + 1)],
                                                         add_vertex_dots=False, line_color=BLUE_, stroke_width=5))
        dot = always_redraw(lambda: Dot(ax.c2p(vs[idx()], vo[idx()]), color=ORANGE_, radius=0.09))
        names = {"off": "截止 off", "lin": "线性 linear", "sat": "饱和 saturation"}

        def regions():
            v, o = vs[idx()], vo[idx()]
            g = VGroup(zh(f"NMOS：{names[region(v, o)]}", 28, GREEN_), zh(f"PMOS：{names[region(VDD - v, VDD - o)]}", 28, VIOLET_),
                       MathTex(rf"V_{{in}}={v:.2f}\,\mathrm{{V}}", font_size=34)).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
            return g.move_to([4.4, 1.0, 0])
        reg = always_redraw(regions)
        self.add(curve, dot, reg)
        self.caption("缓慢增大输入，逐点画出输出", "Raise the input slowly and plot the output point by point", wait=0.2)
        self.play(t.animate.set_value(0.49), run_time=4, rate_func=linear)
        self.caption("两个管子同时饱和的地方，曲线几乎竖直：开关阈值 VM", "Where both transistors saturate the curve is almost vertical: the threshold VM", wait=0.2)
        self.play(t.animate.set_value(1), run_time=4, rate_func=linear)
        x = 1.0
        vm = (VT + x * (VDD - VT)) / (1 + x)
        vmdot = Dot(ax.c2p(vm, vm), color=RED_)
        vml = MathTex(rf"V_M={vm:.2f}\,\mathrm{{V}}", font_size=30, color=RED_).next_to(vmdot, RIGHT)
        diag = DashedLine(ax.c2p(0, 0), ax.c2p(1.8, 1.8), color=MUTED)
        self.play(Create(diag), FadeIn(vmdot, vml))
        self.wait(0.6)
        reg.clear_updaters()
        self.play(FadeOut(reg), run_time=0.3)
        step = vs[1] - vs[0]
        g = [(vo[i + 1] - vo[i - 1]) / (2 * step) for i in range(1, len(vs) - 1)]
        k = [i + 1 for i, s in enumerate(g) if s < -1]
        vil, vih = vs[k[0]], vs[k[-1]]
        vol, voh = vout(vih, wn, wp), vout(vil, wn, wp)
        self.caption("斜率为 −1 的两点定出 VIL、VIH", "The two points with slope −1 define VIL and VIH", wait=0.2)
        marks = VGroup()
        for vx, lab, col in ((vil, "V_{IL}", GREEN_), (vih, "V_{IH}", VIOLET_)):
            yo = vout(vx, wn, wp)
            marks.add(Line(ax.c2p(vx - 0.25, yo + 0.25), ax.c2p(vx + 0.25, yo - 0.25), color=col, stroke_width=4),
                      DashedLine(ax.c2p(vx, 0), ax.c2p(vx, yo), color=col),
                      MathTex(lab, font_size=28, color=col).next_to(ax.c2p(vx, yo), UR if lab == "V_{IL}" else RIGHT + UP * 0.6, buff=0.3))
        self.play(LaggedStart(*[Create(m) for m in marks], lag_ratio=0.2), run_time=2.5)
        self.caption("输入干扰小于噪声容限，输出仍是正确的逻辑值", "Noise smaller than the margin still gives the correct logic output", wait=0.2)
        band = Rectangle(width=ax.c2p(vil, 0)[0] - ax.c2p(0, 0)[0], height=4.0, fill_color=YELLOW, fill_opacity=0.15, stroke_width=0).move_to(ax.c2p(vil / 2, 0.9))
        nml = MathTex(rf"NM_L={vil - vol:.2f}\,\mathrm{{V}}", font_size=34, color=YELLOW).move_to([4.4, 0.4, 0])
        nmh = MathTex(rf"NM_H={voh - vih:.2f}\,\mathrm{{V}}", font_size=34, color=YELLOW).next_to(nml, DOWN)
        self.play(FadeIn(band), Write(nml), Write(nmh), run_time=1.5)
        self.wait(2.5)
        self.card([["电压传输特性", "Voltage transfer characteristic"],
                   ["VM 由两管强弱之比决定", "VM is set by the strength ratio of the two transistors"],
                   MathTex(r"V_M=\frac{V_{T}+x\,(V_{DD}-V_{T})}{1+x},\quad x=\sqrt{\frac{k_p'W_p}{k_n'W_n}}", font_size=40),
                   ["噪声容限 NML = VIL − VOL，NMH = VOH − VIH", "Noise margins NML = VIL − VOL, NMH = VOH − VIH"]])
