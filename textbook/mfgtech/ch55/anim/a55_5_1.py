"""动画 55.5.1（配图 55.5.2）：磨削区的温度——磨粒一颗颗划过，每一颗留下极短的温度尖峰；整个接触区像一块在工件表面移动的热板，
表面温度在约 1 ms 内升到几百摄氏度再降下来。曲线形状按 Jaeger 移动带状热源（hub/surface.py），最高温度取算例 55.5.1 的精磨值（约 334 ℃）、
粗磨值（约 441 ℃）；磨粒的温度尖峰是示意。"""
from manim import *
from wq_anim import *
import numpy as np

TH_F, TH_R = 334.0, 441.0


def k0(x):
    """修正贝塞尔函数 K0(x) = ∫₀^∞ exp(−x·cosh t) dt（x > 0），数值积分（动画服务只允许 numpy）。"""
    t = np.linspace(0, 8, 1601)
    return np.trapezoid(np.exp(-np.outer(x, np.cosh(t))), t, axis=1)


def shapes(L, Xs):
    """Jaeger 移动带状热源的表面温度形状 ∫_{X−L}^{X+L} e^(−u)·K0(|u|) du（与 hub/surface.py 相同）。"""
    u = np.linspace(-4 * L, 4 * L, 8000) + 1e-4          # 网格避开 u = 0（K0 的对数奇点，可积）
    f = np.exp(-u) * k0(np.abs(u))
    cum = np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2 * np.diff(u))])
    return np.interp(Xs + L, u, cum) - np.interp(Xs - L, u, cum)


class Lesson(Base):
    def construct(self):
        self.title("55.5", "磨削区的温度", "Temperature in the grinding zone")
        ax = Axes(x_range=[0, 6, 1], y_range=[0, 500, 100], x_length=9, y_length=3.4, tips=False,
                  axis_config={"color": MUTED}, x_axis_config={"include_ticks": False}).shift(DOWN * 0.3)
        c2p = lambda x, y: ax.c2p(x + 3, y)
        lab = VGroup(zh("沿工件表面的位置（黄色为接触区；工件向左移动）", 20, MUTED).next_to(ax, DOWN, buff=0.12),
                     zh("温度 ℃", 20, MUTED).next_to(ax, LEFT, buff=0.1).shift(UP * 1.4))
        self.play(Create(ax), FadeIn(lab))
        L = 3.0
        Xs = np.linspace(-3 * L, 3 * L, 120)
        F = shapes(L, Xs)
        zone = Rectangle(width=c2p(1, 0)[0] - c2p(-1, 0)[0], height=3.4, fill_color=YELLOW, fill_opacity=0.08, stroke_width=0)
        zone.move_to(c2p(0, 250))
        self.play(FadeIn(zone))
        self.caption("砂轮与工件只在很短的接触弧上接触：大量磨粒在这里切削、耕犁、摩擦", "Wheel and work touch only along a short arc where many grains cut, plough and rub")
        rng = np.random.default_rng(55)
        for k in range(14):
            x = rng.uniform(-1, 1)
            spike = VMobject(color=ORANGE, stroke_width=3).set_points_as_corners([c2p(u, 60 + 380 * np.exp(-((u - x) / 0.05) ** 2)) for u in np.linspace(x - 0.3, x + 0.3, 61)])
            self.play(Create(spike), run_time=0.08)
            self.play(FadeOut(spike), run_time=0.08)
        self.caption("每颗磨粒留下一个极短的温度尖峰；无数尖峰叠起来，就是接触区的温度", "Each grain leaves a brief flash; together they make the zone temperature")
        def curve(th, color):
            pts = [c2p(x / L, 20 + th * f / F.max()) for x, f in zip(Xs, F)]
            return VMobject(color=color, stroke_width=4).set_points_smoothly(pts)
        c1 = curve(TH_F, STEEL)
        t1 = zh(f"精磨 0.005 mm：约 {TH_F:.0f} ℃", 26, STEEL).move_to(c2p(1.9, 395))
        self.play(Create(c1), FadeIn(t1), run_time=1.5)
        self.caption("接触区像一块移动的热板：前方还是常温，最高温度靠近接触区后缘，离开后慢慢冷却", "A moving hot plate: cold ahead of it, hottest near its trailing edge, then slowly cooling behind")
        c2 = curve(TH_R, RED)
        t2 = zh(f"粗磨 0.01 mm：约 {TH_R:.0f} ℃", 26, RED).move_to(c2p(1.9, 480))
        self.play(Create(c2), FadeIn(t2), run_time=1.5)
        self.caption("切深加倍，接触弧变长、热量变多：温度升高约三成", "Double the infeed: a longer arc, more heat, about a third hotter")
        self.card([["θmax − θ₀ ≈ 1.13 (q/k)·√(α·lc/vw)，q = εu·vw·ap/lc", "θmax − θ₀ ≈ 1.13 (q/k)·√(α·lc/vw), q = εu·vw·ap/lc"],
                   ["每一点只受热约 1 ms：温度高、时间短", "Each point is heated for about 1 ms: very hot, very brief"]])
