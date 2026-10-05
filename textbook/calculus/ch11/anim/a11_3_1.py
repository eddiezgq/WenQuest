"""动画 11.3.1（配图 11.3.1）：梯形与 S 形速度曲线——同一次关节运动（90°），两根连杆分别按两种曲线转动；
下方的角加速度曲线上，竖线扫过：梯形曲线的加速度突跳（加加速度为冲激），S 形曲线的加速度斜坡式变化。"""
from manim import *
from wq_anim import *
import numpy as np

D, V, A, J = 90.0, 180.0, 400.0, 4000.0


def prof(kind, t):
    """返回 (θ, α)，数值积分得到。"""
    dt = 1e-4
    if kind == "t":
        ta, tv = V / A, D / V - V / A
        segs = [(ta, A), (tv, 0), (ta, -A)]
        jerk = False
    else:
        dist = lambda v: v * (v / min(A, (v * J) ** 0.5) + min(A, (v * J) ** 0.5) / J)
        Vr = V
        if dist(V) > D:
            lo, hi = 0.0, V
            for _ in range(100):
                m = (lo + hi) / 2
                lo, hi = (lo, m) if dist(m) > D else (m, hi)
            Vr = lo
        Ar = min(A, (Vr * J) ** 0.5)
        tj, ta, tv = Ar / J, max(0.0, Vr / Ar - Ar / J), max(0.0, (D - dist(Vr)) / Vr)
        segs = [(tj, J), (ta, 0), (tj, -J), (tv, 0), (tj, -J), (ta, 0), (tj, J)]
        jerk = True
    th = w = a = tt = 0.0
    for dur, val in segs:
        n = int(round(dur / dt))
        for _ in range(n):
            if tt >= t:
                return th, a
            if jerk:
                a += val * dt
            else:
                a = val
            w += a * dt
            th += w * dt
            tt += dt
    return th, 0.0


class Lesson(Base):
    def construct(self):
        self.title("11.3", "梯形与 S 形速度曲线", "Trapezoidal and S-curve profiles")
        Ts = 1.054
        tgrid = np.linspace(0, Ts, 211)
        data = {k: [prof(k, t) for t in tgrid] for k in ("t", "s")}
        ax = Axes(x_range=[0, 1.1, 0.2], y_range=[-450, 450, 200], x_length=8, y_length=2.6, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 2.0)
        cT = ax.plot_line_graph(tgrid, [p[1] for p in data["t"]], line_color=STEEL, add_vertex_dots=False, stroke_width=3)
        cS = ax.plot_line_graph(tgrid, [p[1] for p in data["s"]], line_color=ORANGE, add_vertex_dots=False, stroke_width=3)
        ylab = MathTex(r"\alpha", font_size=34).next_to(ax, LEFT)
        o1, o2 = LEFT * 3 + UP * 1.0, RIGHT * 3 + UP * 1.0
        base1 = Line(o1, o1 + RIGHT * 2.0, color=GREY_B)
        base2 = Line(o2, o2 + RIGHT * 2.0, color=GREY_B)
        k = ValueTracker(0)

        def link(o, kind, col):
            th = data[kind][int(k.get_value())][0]
            r = np.radians(th)
            return Line(o, o + 2.0 * np.array([np.cos(r), np.sin(r), 0]), color=col, stroke_width=8)
        L1 = always_redraw(lambda: link(o1, "t", STEEL))
        L2 = always_redraw(lambda: link(o2, "s", ORANGE))
        n1 = Text("梯形", font_size=26, color=STEEL).next_to(base1, DOWN)
        n2 = Text("S 形", font_size=26, color=ORANGE).next_to(base2, DOWN)
        cur = always_redraw(lambda: DashedLine(ax.c2p(tgrid[int(k.get_value())], -450), ax.c2p(tgrid[int(k.get_value())], 450), color=GREY_B))
        self.play(Create(ax), FadeIn(ylab), Create(base1), Create(base2), FadeIn(n1), FadeIn(n2))
        self.play(Create(cT), Create(cS))
        self.add(L1, L2, cur)
        self.caption("同样转 90°：梯形曲线的加速度突跳，像一记锤击", "Same 90° move: the trapezoid's acceleration jumps like a hammer blow", wait=0.2)
        self.play(k.animate.set_value(len(tgrid) - 1), run_time=6, rate_func=linear)
        self.caption("S 形曲线让加速度斜坡式变化，多用约 0.1 s，换来平稳", "The S-curve ramps the acceleration: about 0.1 s longer, much smoother", wait=0.8)
        for m in (L1, L2, cur):
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in (ax, ylab, cT, cS, base1, base2, n1, n2, L1, L2, cur)])
        self.card([["最短时间运动", "Minimum-time motion"],
                   MathTex(r"T_{\mathrm{trap}}=\frac{D}{V}+\frac{V}{A},\qquad T_{S}=\frac{D}{V}+\frac{V}{A}+\frac{A}{J}", font_size=42),
                   ["S 形公式在能达到 V、A 时成立；限制加加速度，用很少的时间换来平稳", "S-curve formula when V and A are reached; limiting jerk buys smoothness for little time"]])
