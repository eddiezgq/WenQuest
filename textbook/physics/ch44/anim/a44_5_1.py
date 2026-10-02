"""动画 44.5.1（配图 44.5.3）：高斯波包射向势垒，一部分反射、一部分隧穿。克兰克–尼科尔森法求解含时薛定谔方程
（与程序 44.5.1 相同的参数：E = 0.2 eV、σ = 6 nm，势垒高 0.3 eV、宽 1 nm），透过的概率约 0.13。"""
from manim import *
from wq_anim import *
import numpy as np

C, HB = 0.0380998212, 0.6582119569      # ħ²/(2mₑ) eV·nm²，ħ eV·fs


def cn_frames(N=2000, Lb=200.0, steps=620, dt=0.5, every=10):
    dx = Lb / (N + 1)
    x = (np.arange(N) + 1) * dx
    V = np.where((x >= 100) & (x < 101), 0.3, 0.0)
    k0 = np.sqrt(0.2 / C)
    psi = (2 * np.pi * 36) ** -0.25 * np.exp(-((x - 60) / 12) ** 2 + 1j * k0 * x)
    r, off = dt / (2 * HB), -C / dx ** 2
    d = 2 * C / dx ** 2 + V
    a = 1j * r * off                     # 三对角矩阵 (1 + i r H) 的副对角元
    diag = 1 + 1j * r * d
    cp = np.zeros(N, complex); den = np.zeros(N, complex)   # 托马斯算法的前向系数，只算一次
    den[0] = diag[0]; cp[0] = a / den[0]
    for i in range(1, N):
        den[i] = diag[i] - a * cp[i - 1]; cp[i] = a / den[i]
    frames = []
    for s in range(steps):
        if s % every == 0:
            frames.append(np.minimum(np.abs(psi) ** 2, 0.075))     # 碰撞时干涉峰很高，画面上截在纵轴上限
        Hp = d * psi
        Hp[:-1] += off * psi[1:]; Hp[1:] += off * psi[:-1]
        b = psi - 1j * r * Hp
        y = np.zeros(N, complex); y[0] = b[0] / den[0]
        for i in range(1, N):
            y[i] = (b[i] - a * y[i - 1]) / den[i]
        for i in range(N - 2, -1, -1):
            y[i] -= cp[i] * y[i + 1]
        psi = y
    trans = np.sum(np.abs(psi[x > 101]) ** 2) * dx
    return x, frames, trans


class Lesson(Base):
    def construct(self):
        self.title("44.5", "波包穿越势垒", "A wave packet meets a barrier")
        x, frames, T = cn_frames()
        ax = Axes(x_range=[0, 200, 50], y_range=[0, 0.075, 0.025], x_length=11, y_length=3.6, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.7)
        bar = Rectangle(width=ax.x_length / 200 * 1.0, height=ax.y_length, fill_color=GREY_B, fill_opacity=0.7,
                        stroke_width=0).move_to(ax.c2p(100.5, 0), aligned_edge=DOWN)
        vlab = VGroup(zh("势垒 0.3 eV", 22, GREY_B), en("barrier 0.3 eV", 16)).arrange(DOWN, buff=0.05).next_to(bar, UP, buff=0.1)
        xl = MathTex(r"x/\mathrm{nm}", font_size=28).next_to(ax.x_axis, DOWN, buff=0.15).align_to(ax.x_axis, RIGHT)
        yl = MathTex(r"|\Psi|^2", font_size=28, color=PURPLE_B).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), FadeIn(bar), FadeIn(vlab), FadeIn(xl), FadeIn(yl))
        k = ValueTracker(0)
        sel = slice(None, None, 1)
        curve = always_redraw(lambda: ax.plot_line_graph(x[sel], frames[int(k.get_value())][sel], add_vertex_dots=False,
                                                         line_color=PURPLE_B, stroke_width=3))
        self.add(curve)
        self.caption("波包的平均能量 0.2 eV，低于势垒", "The packet's mean energy, 0.2 eV, is below the barrier")
        self.play(k.animate.set_value(len(frames) - 1), run_time=9, rate_func=linear)
        tr = VGroup(zh(f"透过的概率约 {T:.2f}", 26, YELLOW), en(f"transmitted probability about {T:.2f}", 18)).arrange(DOWN, buff=0.05).to_corner(UR).shift(DOWN * 1.3)
        self.play(FadeIn(tr))
        self.caption("大部分反射回去，一小部分隧穿过势垒：经典粒子做不到", "Most is reflected, a small part tunnels through: a classical particle cannot")
        self.card([["隧道效应", "Tunnelling"],
                   MathTex(r"T\approx\frac{16E(V_0-E)}{V_0^2}\,\mathrm{e}^{-2\kappa a}", font_size=46),
                   ["透射系数随势垒宽度指数地减小", "The transmission falls exponentially with the barrier width"]])
