"""动画 1.3.1（配图 1.3.1）：尺寸与对称。Wp = Wn 时 PMOS 弱，开关阈值偏低、上升沿慢；把 PMOS 加宽到 r 倍，
阈值回到 VDD/2，上升和下降一样快；代价是 PMOS 更大、输入电容更大。传输特性和延时用与书中相同的模型计算。"""
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
ORANGE_ = "#ffa657"
RED_ = "#ff7b72"


def ids(k, w, vov, vds):
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


def vm(wn, wp):
    x = np.sqrt(KP * wp / (KN * wn))
    return (VT + x * (VDD - VT)) / (1 + x)


def req(k, w):
    return 0.75 * VDD / (k / 2 * w / LCH * (VDD - VT) ** 2)


def fo4(wn, wp):
    c = (wn + wp) * CD + 4 * (wn + wp) * CG
    return 0.69 * req(KN, wn) * c, 0.69 * req(KP, wp) * c


class Lesson(Base):
    def construct(self):
        self.title("1.3", "尺寸与对称", "Sizing and symmetry")
        ax = Axes(x_range=[0, 1.8, 0.3], y_range=[0, 1.8, 0.3], x_length=4.6, y_length=3.6, tips=False,
                  axis_config={"color": MUTED, "include_numbers": True, "font_size": 20, "decimal_number_config": {"num_decimal_places": 1}}).move_to([-3.6, 0.1, 0])
        ratio = ValueTracker(1.0)
        vs = np.linspace(0, VDD, 181)
        vtc = always_redraw(lambda: ax.plot_line_graph(vs, [vout(v, WMIN, ratio.get_value() * WMIN) for v in vs], add_vertex_dots=False, line_color=BLUE_, stroke_width=5))
        vmd = always_redraw(lambda: Dot(ax.c2p(vm(WMIN, ratio.get_value() * WMIN), vm(WMIN, ratio.get_value() * WMIN)), color=RED_))
        half = DashedLine(ax.c2p(VDD / 2, 0), ax.c2p(VDD / 2, 1.8), color=MUTED)
        ax2 = Axes(x_range=[0, 2, 0.5], y_range=[0, 1.8, 0.9], x_length=5.2, y_length=3.0, tips=False, axis_config={"color": MUTED}).move_to([3.2, 0.1, 0])
        ref = fo4(WMIN, WMIN * R_SYM)[0]

        def wave():
            a, b = fo4(WMIN, ratio.get_value() * WMIN)
            tf, tr = 0.14 * a / ref, 0.14 * b / ref        # 时间轴按对称尺寸的延时归一
            ts = np.linspace(0, 2, 400)
            v, out = VDD, []
            dt = ts[1] - ts[0]
            for i, tt in enumerate(ts):
                hi = (tt % 1.0) < 0.5
                if i:
                    v = v * np.exp(-dt / tf) if hi else VDD - (VDD - v) * np.exp(-dt / tr)
                out.append(v)
            return ax2.plot_line_graph(ts, out, add_vertex_dots=False, line_color=ORANGE_, stroke_width=4)
        vin = ax2.plot_line_graph([0, 0.5, 0.5, 1, 1, 1.5, 1.5, 2], [1.8, 1.8, 0, 0, 1.8, 1.8, 0, 0], add_vertex_dots=False, line_color=MUTED, stroke_width=2)
        w = always_redraw(wave)
        lab = always_redraw(lambda: MathTex(rf"W_p/W_n={ratio.get_value():.2f}", font_size=36).move_to([0, 2.55, 0]))
        self.play(Create(ax), Create(ax2), Create(half), FadeIn(vin))
        self.add(vtc, vmd, w, lab)
        self.caption("Wp = Wn 时，PMOS 弱，阈值偏低，上升沿慢", "With Wp = Wn the PMOS is weaker: the threshold sits low and the rising edge is slow", wait=2.0)
        self.caption(f"加宽 PMOS 到 r = {R_SYM:.2f} 倍：VM 回到 VDD / 2", f"Widen the PMOS to r = {R_SYM:.2f} times: VM moves to VDD / 2", wait=0.2)
        self.play(ratio.animate.set_value(R_SYM), run_time=6, rate_func=smooth)
        self.wait(2.0)
        self.caption("波形上看：上升和下降变得一样快", "In the waveform: rising and falling edges now match", wait=2.0)
        a = fo4(WMIN, WMIN)
        b = fo4(WMIN, R_SYM * WMIN)
        tbl = VGroup(MathTex(rf"W_p/W_n=1:\ t_{{PHL}}={a[0]*1e12:.0f},\ t_{{PLH}}={a[1]*1e12:.0f}\ \mathrm{{ps}}", font_size=30),
                     MathTex(rf"W_p/W_n={R_SYM:.2f}:\ t_{{PHL}}=t_{{PLH}}={b[0]*1e12:.0f}\ \mathrm{{ps}}", font_size=30)).arrange(DOWN, aligned_edge=LEFT).move_to([0, -2.0, 0])
        self.play(Write(tbl), run_time=1.5)
        self.caption("代价：PMOS 更大，输入电容也更大", "The cost: a larger PMOS and a larger input capacitance", wait=2.5)
        self.card([["尺寸与对称", "Sizing and symmetry"],
                   ["对称尺寸：上升下降一样快", "Symmetric sizing: equal rise and fall"],
                   MathTex(rf"\frac{{W_p}}{{W_n}}=r=\frac{{k_n'}}{{k_p'}}\approx {R_SYM:.2f}", font_size=44),
                   MathTex(r"t_p=0.69\,R_{eq}\,C,\quad R_{eq}\approx\frac{3}{4}\frac{V_{DD}}{I_{DSAT}}", font_size=40)])
