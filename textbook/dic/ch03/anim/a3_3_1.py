"""动画 3.3.1（配图 3.3.1）：亚稳态。两个首尾相接的反相器有一个不稳定的平衡点 (VM, VM)，像立在笔尖上的铅笔。
触发器在采样的瞬间被留在它附近时，两个节点的电压差按 e^(t/τm) 增长，直到倒向某一个稳定点；初始偏离每小 10 倍，
决断时间只多 τm·ln10。波形用 ΔV(t) = ΔV0·e^(t/τm) 的饱和形式画出，τm 取本章 SKY130 仿真值。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
VDD = 1.8
VM = 0.9
TAU_M_PS = 36.83759712689491
T0_PS = 30.258009831165886
TAU_EST_PS = 27.993266680269333
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
GREEN_ = "#56d364"
RED_ = "#ff7b72"


def node(t_ps, dv0, sign=1):
    """饱和的指数分离：小信号时 V − VM ≈ ±ΔV0/2·e^(t/τm)，大信号时趋于 0 或 VDD。"""
    x = dv0 / VDD * np.exp(t_ps / TAU_M_PS)
    return VM + sign * VDD / 2 * np.tanh(x)


class Lesson(Base):
    def construct(self):
        self.title("3.3", "亚稳态：在两个稳态之间犹豫", "Metastability: hesitating between two stable states")
        # 1. 铅笔立在笔尖上
        hill = FunctionGraph(lambda x: 1.6 * np.exp(-x * x * 1.4) - 1.6, x_range=[-3.2, 3.2], color=MUTED).shift(DOWN * 0.2)
        ball = Dot(hill.get_top() + UP * 0.12, radius=0.16, color=ORANGE_)
        lab0 = Text("0", font_size=34, color=GREEN_).move_to([-3.0, -1.3, 0])
        lab1 = Text("1", font_size=34, color=GREEN_).move_to([3.0, -1.3, 0])
        self.play(Create(hill), FadeIn(ball), FadeIn(lab0, lab1))
        self.caption("两个反相器首尾相接：0 和 1 是两个谷底，中间是一个尖顶", "Two inverters in a loop: 0 and 1 are valleys, the middle is a peak", wait=0.8)
        self.caption("数据恰好在时钟沿变化，触发器被留在尖顶附近", "If data changes right at the clock edge, the flip-flop is left near the peak", wait=0.8)
        self.play(ball.animate.shift(RIGHT * 0.05), run_time=1.2, rate_func=linear)
        self.play(MoveAlongPath(ball, hill.copy().pointwise_become_partial(hill, 0.5, 0.97).shift(UP * 0.12)), run_time=1.6, rate_func=rate_functions.ease_in_quad)
        self.caption("偏一点点，就越滚越快，最后倒向一边", "A tiny offset grows faster and faster until it falls to one side", wait=1.0)
        self.clear_stage()
        # 2. 波形
        ax = Axes(x_range=[0, 500, 100], y_range=[0, VDD, 0.9], x_length=9.0, y_length=3.4, tips=False,
                  axis_config={"color": MUTED, "include_numbers": True, "font_size": 22}).move_to([0, -0.3, 0])
        xl = Text("t / ps", font_size=22, color=MUTED).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = Text("V", font_size=24, color=MUTED).next_to(ax.y_axis, UP, buff=0.1)
        mid = DashedLine(ax.c2p(0, VM), ax.c2p(500, VM), color=MUTED)
        self.play(Create(ax), FadeIn(xl, yl), Create(mid))
        offs = [(1e-2, ORANGE_, "10 mV"), (1e-3, GREEN_, "1 mV"), (1e-4, BLUE_, "0.1 mV"), (1e-5, RED_, "10 μV")]
        ts = np.linspace(0, 500, 300)
        prev = None
        for k, (dv, c, name) in enumerate(offs):
            up = ax.plot_line_graph(ts, node(ts, dv, 1), add_vertex_dots=False, line_color=c, stroke_width=4)
            dn = ax.plot_line_graph(ts, node(ts, dv, -1), add_vertex_dots=False, line_color=c, stroke_width=2.5)
            tag = Text(name, font_size=22, color=c).move_to([5.3, 1.0 - 0.42 * k, 0])
            self.play(Create(up), Create(dn), FadeIn(tag), run_time=1.6)
            t_res = TAU_M_PS * np.log(np.arctanh(0.8) * VDD / dv)
            mark = Dot(ax.c2p(t_res, VM + 0.8 * VDD / 2), color=c, radius=0.07)
            self.add(mark)
            if prev is not None and k == 1:
                br = BraceBetweenPoints(ax.c2p(prev, 1.9), ax.c2p(t_res, 1.9), direction=UP, color=WHITE)
                bt = MathTex(r"\tau_m\ln 10", font_size=30).next_to(br, UP, buff=0.05)
                self.play(GrowFromCenter(br), Write(bt))
            prev = t_res
        self.caption(f"偏离每小 10 倍，只多等 τm·ln10 ≈ {TAU_M_PS * np.log(10):.0f} ps", f"Each 10× smaller offset costs only τm·ln10 ≈ {TAU_M_PS * np.log(10):.0f} ps more", wait=1.5)
        self.caption("没有“最长”的决断时间，但等得越久，还没决断的机会越小", "There is no longest resolution time, but the chance of still waiting falls fast", wait=1.5)
        self.card([["亚稳态的决断", "Resolving metastability"],
                   MathTex(r"\Delta V(t)=\Delta V_0\,e^{t/\tau_m},\quad \tau_m\approx C/g_m", font_size=40),
                   MathTex(r"\mathrm{MTBF}=\frac{e^{t_r/\tau_m}}{T_0\,f_{clk}\,f_{data}}", font_size=40),
                   [f"SKY130 触发器：τm ≈ {TAU_M_PS:.0f} ps，T0 ≈ {T0_PS:.0f} ps", f"SKY130 flip-flop: τm ≈ {TAU_M_PS:.0f} ps, T0 ≈ {T0_PS:.0f} ps"],
                   ["异步信号先打两拍（3.3.4 节）", "Synchronize asynchronous inputs with two flip-flops (Section 3.3.4)"]])
