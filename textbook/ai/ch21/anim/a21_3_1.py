"""动画 21.3.1（配图 21.3.1）：轴承故障怎样写进振动信号里。

四段：
1. 滚动体一圈圈滚过外圈上的那个小坑，每滚过一次就敲一下——**敲击是等间隔的**；
2. 每一次敲击让整个座圈"当"地响一声：时域上是一串**高频衰减振荡**；
3. 直接做频谱，能量都堆在共振频率那一带，故障频率几乎看不见；
4. 取包络（把高频振荡的"外形"描出来）再做频谱，**故障频率与它的谐波一下子冒出来**。

渲染服务只允许 manim、wq_anim、numpy、math、random，所以几何与信号都在这里重算一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

N_BALLS, D_BALL, D_PITCH, RPM = 9, 7.94, 39.04, 1797.0
FS, SECONDS, CARRIER = 4000.0, 0.25, 900.0


def freqs():
    fr = RPM / 60.0
    ratio = D_BALL / D_PITCH
    return {"fr": fr, "BPFO": N_BALLS / 2.0 * fr * (1 - ratio)}


def make_signal(fault_hz, noise=0.08, seed=0):
    rng = np.random.default_rng(seed)
    n = int(FS * SECONDS)
    t = np.arange(n) / FS
    x = noise * rng.normal(0.0, 1.0, n) + 0.15 * np.sin(2 * np.pi * (RPM / 60.0) * t)
    k, period = 0, 1.0 / fault_hz
    while k * period < SECONDS:
        i0 = int(k * period * FS)
        m = min(n - i0, int(0.02 * FS))
        if m > 0:
            tt = np.arange(m) / FS
            x[i0:i0 + m] += np.exp(-260.0 * tt) * np.sin(2 * np.pi * CARRIER * tt)
        k += 1
    return t, x


def env_of(x):
    n = len(x)
    X = np.fft.fft(x)
    h = np.zeros(n)
    h[0] = 1
    if n % 2 == 0:
        h[n // 2] = 1
        h[1:n // 2] = 2
    else:
        h[1:(n + 1) // 2] = 2
    return np.abs(np.fft.ifft(X * h))


def spec(x):
    n = len(x)
    X = np.abs(np.fft.rfft(x * np.hanning(n))) / n * 2
    return np.fft.rfftfreq(n, 1.0 / FS), X


class Lesson(Base):
    def construct(self):
        F = freqs()
        self.title("21.3", "轴承故障怎样写进振动里",
                   "How a bearing fault writes itself into the vibration")

        # ---------------- 一、几何：等间隔的敲击
        self.caption("外圈上有一个小坑。滚动体每滚过它一次，就敲一下",
                     "A pit on the outer race: every ball that rolls over it strikes once",
                     wait=1.2)
        center = LEFT * 3.4
        outer = Circle(radius=1.75, color=STEEL, stroke_width=4).move_to(center)
        inner = Circle(radius=0.85, color=MUTED, stroke_width=3).move_to(center)
        pit = Dot(center + RIGHT * 1.75, radius=0.1, color=C_F)
        balls = VGroup(*[Dot(center + 1.30 * np.array([np.cos(a), np.sin(a), 0.0]),
                             radius=0.14, color=NAVY)
                         for a in np.linspace(0, TAU, N_BALLS, endpoint=False)])
        self.play(Create(outer), Create(inner), FadeIn(balls), FadeIn(pit), run_time=1.2)
        self.play(Rotate(balls, angle=TAU / N_BALLS * 3, about_point=center), run_time=1.6)
        self.caption(f"滚动体 {N_BALLS} 个，保持架转得比轴慢，"
                     f"所以外圈故障频率是轴频的 {F['BPFO'] / F['fr']:.3f} 倍",
                     "The cage turns slower than the shaft, fixing the fault frequency",
                     wait=1.8)
        tag = zh(f"BPFO = {F['BPFO']:.1f} Hz（轴频 {F['fr']:.1f} Hz）", 30, YELLOW)
        tag.next_to(outer, DOWN, buff=0.5)
        self.play(FadeIn(tag), run_time=0.6)
        self.wait(0.8)

        # ---------------- 二、时域
        t, x = make_signal(F["BPFO"])
        ax = Axes(x_range=[0, SECONDS, 0.05], y_range=[-1.6, 1.6, 1.0],
                  x_length=5.6, y_length=2.6,
                  axis_config={"include_tip": False, "color": MUTED}).to_edge(RIGHT, buff=0.7)
        curve = ax.plot_line_graph(t, x, line_color=STEEL, add_vertex_dots=False,
                                   stroke_width=2)["line_graph"]
        self.play(Create(ax), run_time=0.8)
        self.play(Create(curve), run_time=2.0)
        self.caption("每一下敲击都让座圈“当”地响一声——时域上是一串高频衰减振荡",
                     "Each strike rings the housing: a train of decaying high-frequency bursts",
                     wait=1.8)
        marks = VGroup()
        k = 1
        while k / F["BPFO"] < SECONDS:
            marks.add(DashedLine(ax.c2p(k / F["BPFO"], -1.6), ax.c2p(k / F["BPFO"], 1.6),
                                 color=C_F, stroke_width=2))
            k += 1
        self.play(Create(marks), run_time=1.0)
        self.caption(f"冲击间隔 {1000 / F['BPFO']:.1f} 毫秒，正好是 1 / BPFO",
                     "The spacing is exactly one over the fault frequency", wait=1.6)
        self.clear_stage()

        # ---------------- 三、直接做频谱：看不见
        fa, X = spec(x)
        m = fa <= 1600
        ax2 = Axes(x_range=[0, 1600, 400], y_range=[0, float(X[m].max()) * 1.15, 1],
                   x_length=10.0, y_length=2.6,
                   axis_config={"include_tip": False, "color": MUTED}).shift(UP * 0.4)
        sp = ax2.plot_line_graph(fa[m], X[m], line_color=MUTED, add_vertex_dots=False,
                                 stroke_width=2)["line_graph"]
        self.play(Create(ax2), Create(sp), run_time=1.6)
        hi = DashedLine(ax2.c2p(CARRIER, 0), ax2.c2p(CARRIER, float(X[m].max())),
                        color=STEEL, stroke_width=3)
        lo = DashedLine(ax2.c2p(F["BPFO"], 0), ax2.c2p(F["BPFO"], float(X[m].max())),
                        color=C_F, stroke_width=3)
        self.play(Create(hi), Create(lo), run_time=0.8)
        self.caption("能量都堆在共振那一带（蓝线），故障频率（红线）几乎看不见",
                     "The energy sits at the resonance; the fault frequency is invisible",
                     wait=2.0)
        self.clear_stage()

        # ---------------- 四、包络谱：一下子冒出来
        self.caption("办法是先取包络：把高频振荡的“外形”描出来，再做一次频谱",
                     "Take the envelope first, then transform again", wait=1.6)
        e = env_of(x)
        ax3 = Axes(x_range=[0, SECONDS, 0.05], y_range=[0, 1.6, 0.5],
                   x_length=10.0, y_length=2.0,
                   axis_config={"include_tip": False, "color": MUTED}).shift(UP * 1.1)
        raw = ax3.plot_line_graph(t, np.abs(x), line_color=MUTED, add_vertex_dots=False,
                                  stroke_width=1.5)["line_graph"]
        env = ax3.plot_line_graph(t, e, line_color=C_F, add_vertex_dots=False,
                                  stroke_width=3)["line_graph"]
        self.play(Create(ax3), Create(raw), run_time=1.0)
        self.play(Create(env), run_time=1.2)

        fe, E = spec(e - e.mean())
        me = fe <= 600
        ax4 = Axes(x_range=[0, 600, 100], y_range=[0, float(E[me].max()) * 1.2, 1],
                   x_length=10.0, y_length=2.0,
                   axis_config={"include_tip": False, "color": MUTED}).shift(DOWN * 1.7)
        es = ax4.plot_line_graph(fe[me], E[me], line_color=C_F, add_vertex_dots=False,
                                 stroke_width=2.5)["line_graph"]
        self.play(Create(ax4), Create(es), run_time=1.6)
        lines = VGroup()
        for k in (1, 2, 3):
            hz = k * F["BPFO"]
            if hz <= 600:
                lines.add(DashedLine(ax4.c2p(hz, 0), ax4.c2p(hz, float(E[me].max())),
                                     color=YELLOW, stroke_width=2.5))
        self.play(Create(lines), run_time=0.8)
        self.caption("故障频率与它的谐波一下子冒出来——这就是包络解调",
                     "The fault frequency and its harmonics appear at once", wait=2.0)

        self.card(["故障频率是算出来的：由滚动体个数、直径、节圆直径与转速决定",
                   "转速一变，这个频率全变——所以转速必须进模型",
                   "直接做频谱看不见它，要先取包络"], wait=3.2)
