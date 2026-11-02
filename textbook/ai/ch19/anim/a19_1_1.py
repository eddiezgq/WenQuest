"""动画 19.1.1（配图 19.1.1）：天气预报的两道硬墙。

三段：
1. 场在格子上一步步往前推：**一步走过一格，格子外的信息就没被用上**——显式格式的稳定
   上限（库朗数 1）是从这里来的；
2. 把时间步调大，显式格式几步之内就炸给你看；
3. 两个几乎一模一样的初值，各自往前推——误差**指数**增长，所以提高初值精度的回报是
   对数的。

渲染服务只允许 manim、wq_anim、numpy、math、random，不能 import 章内模块，所以把
code/_ch19.py 里最小的一份在这里重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

NX = 24
X0, DX, Y0 = -5.6, 0.47, -0.4
HEIGHT = 2.0


def bump(shift=0.0):
    i = np.arange(NX)
    return np.exp(-((i - 8 - shift) ** 2) / 4.0)


def upwind(u, c):
    """显式迎风一步：新值只用到自己和左邻居——这就是"信息只走得了一格"。"""
    return u - c * (u - np.roll(u, 1))


def bars(u, color=STEEL):
    g = VGroup()
    for i, val in enumerate(u):
        h = float(np.clip(val, -3, 3)) * HEIGHT
        x = X0 + i * DX
        g.add(Rectangle(width=DX * 0.82, height=max(abs(h), 0.02),
                        color=color, fill_color=color, fill_opacity=0.85,
                        stroke_width=0).move_to([x, Y0 + h / 2, 0]))
    return g


def axis_line():
    return Line([X0 - DX, Y0, 0], [X0 + NX * DX, Y0, 0], color=MUTED, stroke_width=2)


def lorenz_step(s, dt):
    x, y, z = s
    def f(v):
        a, b, c = v
        return np.array([10.0 * (b - a), a * (28.0 - c) - b, a * b - 8.0 / 3.0 * c])
    k1 = f(s); k2 = f(s + dt / 2 * k1); k3 = f(s + dt / 2 * k2); k4 = f(s + dt * k3)
    return s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + 2 * k4)


class Lesson(Base):
    def construct(self):
        self.title("19.1", "预报为什么有两道硬墙",
                   "Why forecasting runs into two hard walls")

        # ---------------- 一、一步只走得了一格
        self.caption("把大气切成格子，一个时间步只把信息送到隔壁一格",
                     "Cut the atmosphere into cells: one step moves information one cell",
                     wait=0.8)
        ax = axis_line()
        u = bump()
        bar = bars(u)
        self.play(Create(ax), FadeIn(bar), run_time=1.0)

        cell = Rectangle(width=DX, height=HEIGHT * 1.15, color=YELLOW, stroke_width=3)
        cell.move_to([X0 + 8 * DX, Y0 + HEIGHT * 0.575, 0])
        arrow = Arrow([X0 + 8 * DX, Y0 + HEIGHT * 1.25, 0],
                      [X0 + 9 * DX, Y0 + HEIGHT * 1.25, 0],
                      color=YELLOW, buff=0, stroke_width=4, max_tip_length_to_length_ratio=0.35)
        self.play(Create(cell), GrowArrow(arrow), run_time=0.8)
        self.caption("信息走得比一格还快，格子就跟不上了——这就是库朗数 1 这道坎",
                     "If information outruns one cell per step, the grid cannot keep up",
                     wait=1.6)
        self.play(FadeOut(cell), FadeOut(arrow), run_time=0.5)

        # ---------------- 二、把时间步调大，几步就炸
        for c, zh_t, en_t in ((0.8, "库朗数 0.8：稳稳地往前走",
                               "Courant 0.8: it advances smoothly"),
                              (1.4, "库朗数 1.4：同一套格式，几步就炸",
                               "Courant 1.4: the same scheme blows up in a few steps")):
            self.caption(zh_t, en_t, wait=0.6)
            u = bump()
            col = STEEL if c < 1 else C_F
            new = bars(u, col)
            self.play(Transform(bar, new), run_time=0.5)
            label = zh(f"C = {c}", 30, YELLOW).to_corner(UR, buff=0.7)
            self.play(FadeIn(label), run_time=0.4)
            for _ in range(14 if c < 1 else 22):
                u = upwind(u, c)
                self.play(Transform(bar, bars(u, col)), run_time=0.16)
            if c > 1:
                peak = float(np.max(np.abs(u)))
                warn = zh(f"22 步之后，峰值涨到原来的 {peak:,.0f} 倍", 28, C_F)
                warn.next_to(label, DOWN, buff=0.3)
                self.play(FadeIn(warn), run_time=0.5)
                self.wait(1.4)
                self.play(FadeOut(warn), run_time=0.4)
            self.play(FadeOut(label), run_time=0.3)

        self.clear_stage()

        # ---------------- 三、两个几乎一样的初值
        self.caption("第二道墙：两个几乎一模一样的初值，各自往前推",
                     "The second wall: two almost identical initial states, each marched forward",
                     wait=1.2)
        axes = Axes(x_range=[-22, 22, 10], y_range=[2, 50, 10],
                    x_length=9.0, y_length=4.2,
                    axis_config={"color": MUTED, "stroke_width": 2,
                                 "include_ticks": False}).shift(DOWN * 0.3)
        self.play(Create(axes), run_time=0.8)

        DT = 0.008
        s = np.array([1.0, 1.0, 25.0])
        for _ in range(2000):
            s = lorenz_step(s, DT)
        a = s.copy()
        b = s + np.array([1e-4, 0.0, 0.0])
        pa, pb = [a.copy()], [b.copy()]
        for _ in range(3200):
            a = lorenz_step(a, DT); b = lorenz_step(b, DT)
            pa.append(a.copy()); pb.append(b.copy())
        pa, pb = np.array(pa), np.array(pb)

        def curve(p, n, color):
            pts = [axes.c2p(float(v[0]), float(v[2])) for v in p[:n:8]]
            return VMobject(color=color, stroke_width=2.5).set_points_smoothly(pts)

        note = zh("两条初值只差 0.0001", 26, INK).to_edge(UP, buff=1.4)
        self.play(FadeIn(note), run_time=0.5)
        for n in (600, 1400, 2200, 3200):
            ca, cb = curve(pa, n, STEEL), curve(pb, n, C_F)
            if n == 600:
                self.play(Create(ca), Create(cb), run_time=1.4)
                keep_a, keep_b = ca, cb
            else:
                self.play(Transform(keep_a, ca), Transform(keep_b, cb), run_time=1.2)
        self.play(FadeOut(note), run_time=0.4)
        self.caption("差了 0.0001，照样分道扬镳——误差是指数长的",
                     "A difference of 0.0001 still ends up somewhere else entirely",
                     wait=1.8)

        self.card([
            ["两道硬墙", "Two hard walls"],
            ["一、格子：一步走不过一格", "1. The grid: one step, one cell"],
            ["二、混沌：误差指数增长", "2. Chaos: errors grow exponentially"],
            ["所以初值精度提高十倍，只多买回一个多翻倍时间",
             "So ten times better initial data buys only one more doubling time"],
        ])
