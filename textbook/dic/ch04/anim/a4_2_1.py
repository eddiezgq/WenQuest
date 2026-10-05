"""动画 4.2.1（配图 4.2.1）：信号在分布式 RC 线上“扩散”而不是“传播”。1 mm 的 met2 线一端接阶跃电压，
把线切成 40 段数值求解：电压沿线像热量沿铁棒一样慢慢渗过去，远端的 50 % 时刻约为 0.38RC；
把电阻、电容各集中成一个，50 % 时刻是 0.69RC，高估了将近一倍。"""
from manim import *
from wq_anim import *
import numpy as np

# <数值>  由 _sync.py 从 textbook/dic/conventions/mos.py 写入，不要手改
RW_1MM = 892.8571428571428
CW_1MM_FF = 77.97
# </数值>

BLUE_ = "#58a6ff"
ORANGE_ = "#ffa657"
GREEN_ = "#56d364"


def ladder(n=40, T=2.0, steps=400):
    """归一化：总 R = 1、总 C = 1，时间以 RC 为单位；后向欧拉。返回 t 与各节点电压。"""
    N = n + 1
    C = np.full(N, 1.0 / n); C[0] = 1e-6 + 0.5 / n; C[-1] = 0.5 / n
    G = np.zeros((N, N))
    for i in range(n):
        g = n
        G[i, i] += g; G[i + 1, i + 1] += g; G[i, i + 1] -= g; G[i + 1, i] -= g
    G[0, 0] += 1e4                                   # 近似理想电压源
    b = np.zeros(N); b[0] = 1e4
    dt = T / steps
    A = np.linalg.inv(np.diag(C) / dt + G)
    v = np.zeros(N); out = [v.copy()]
    for _ in range(steps):
        v = A @ (C / dt * v + b)
        out.append(v.copy())
    return np.linspace(0, T, steps + 1), np.array(out)


class Lesson(Base):
    def construct(self):
        self.title("4.2", "分布式 RC 线：扩散而不是传播", "A distributed RC wire: diffusion, not propagation")
        rc = RW_1MM * CW_1MM_FF * 1e-15 * 1e12
        info = MathTex(rf"1\,\mathrm{{mm\ met2}}:\ R={RW_1MM:.0f}\,\Omega,\ C={CW_1MM_FF:.0f}\,\mathrm{{fF}},\ RC\approx{rc:.0f}\,\mathrm{{ps}}", font_size=32).move_to([0, 2.5, 0])
        self.play(Write(info))
        ts, V = ladder()
        n = V.shape[1] - 1
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1, 0.5], x_length=8.5, y_length=3.4, tips=False,
                  axis_config={"color": MUTED}).move_to([0, -0.3, 0])
        xl = Text("x / L", font_size=22, color=MUTED).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = MathTex(r"V/V_{DD}", font_size=26, color=MUTED).next_to(ax.y_axis, UP, buff=0.1)
        half = DashedLine(ax.c2p(0, 0.5), ax.c2p(1, 0.5), color=MUTED)
        self.play(Create(ax), FadeIn(xl, yl), Create(half))
        k = ValueTracker(0)
        xs = np.linspace(0, 1, n + 1)
        prof = always_redraw(lambda: ax.plot_line_graph(xs, V[int(k.get_value())], add_vertex_dots=False, line_color=BLUE_, stroke_width=5))
        tl = always_redraw(lambda: MathTex(rf"t={ts[int(k.get_value())]:.2f}\,RC", font_size=34).move_to([4.6, 1.5, 0]))
        self.add(prof, tl)
        self.caption("一端加上阶跃电压：电压沿线一点一点渗过去", "Step the near end: the voltage seeps along the wire", wait=0.2)
        i38 = int(np.argmax(V[:, -1] >= 0.5))
        self.play(k.animate.set_value(i38), run_time=5, rate_func=linear)
        dot = Dot(ax.c2p(1, 0.5), color=ORANGE_)
        lab = MathTex(r"t_{50}\approx 0.38\,RC", font_size=34, color=ORANGE_).next_to(dot, UP + LEFT, buff=0.15)
        self.play(FadeIn(dot), Write(lab))
        self.caption("远端到 50 %：约 0.38RC", "The far end reaches 50 % at about 0.38RC", wait=1.5)
        self.play(k.animate.set_value(len(ts) - 1), run_time=4, rate_func=linear)
        self.caption("集总模型（R、C 各一个）给出 0.69RC，高估了近一倍", "A lumped model gives 0.69RC, nearly twice too long", wait=2.0)
        self.caption("线长加倍，R、C 都加倍：延时变成四倍", "Double the length: R and C both double, the delay quadruples", wait=2.0)
        self.card([["分布式 RC 线", "Distributed RC wire"],
                   MathTex(r"t_{50}\approx 0.38\,R_wC_w\quad(\text{lumped: }0.69\,RC)", font_size=40),
                   MathTex(r"R_wC_w\propto L^2", font_size=40),
                   ["长线要分段加中继器（4.3 节）", "Long wires need repeaters (Section 4.3)"]])
