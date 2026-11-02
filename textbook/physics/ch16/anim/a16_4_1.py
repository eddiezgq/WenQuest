"""动画 16.4.1（配图 16.4.1）：流线与流管。理想流体绕圆柱稳定流动（流函数 ψ = U(r − a²/r) sin θ，与算例 16.4.2 一致）。
先画流线，再让一串小颗粒顺着流线走：流线挤在一起的地方（圆柱上下两侧）颗粒走得快；标出一根流管，流体不会穿过管壁，
管细的地方流得快，Av 不变。"""
from manim import *
from wq_anim import *
import numpy as np

U, A = 1.0, 1.0
S = 1.45                                                         # 画面单位 / 长度单位
C = np.array([0, -0.3, 0])


def vel(x, y):
    r2 = x * x + y * y
    return U * (1 - A * A * (x * x - y * y) / r2 ** 2), -U * A * A * 2 * x * y / r2 ** 2


def streamline(y0, x0=-4.2, x1=4.2, n=900):
    x, y, pts = x0, y0, []
    dt = (x1 - x0) / n
    for _ in range(4 * n):
        pts.append(C + S * np.array([x, y, 0]) / 1.0 * 0.95)
        u, v = vel(x, y); sp = np.hypot(u, v)
        x += dt * u / sp; y += dt * v / sp
        if x > x1: break
    return pts


class Lesson(Base):
    def construct(self):
        self.title("16.4", "流线与流管", "Streamlines and flow tubes")
        cyl = Circle(radius=A * S * 0.95, color=GREY_B, fill_opacity=0.6).move_to(C)
        ys = [0.08, 0.3, 0.6, 0.95, 1.4, 1.9]
        lines = VGroup(*[VMobject(color=BLUE_D, stroke_width=2).set_points_smoothly(streamline(s * y0)) for y0 in ys for s in (1, -1)])
        self.play(FadeIn(cyl))
        self.caption("流线：线上每一点的切线方向就是那里流体的速度方向", "Streamlines: the tangent at each point gives the flow direction there", wait=0)
        self.play(Create(lines), run_time=3)
        t1, t2 = streamline(0.3), streamline(0.6)
        tube = Polygon(*(t1[::6] + t2[::6][::-1]), color=RED, fill_opacity=0.25, stroke_width=0)
        self.caption("相邻两条流线围成流管：流体不会穿过管壁", "Two neighbouring streamlines bound a flow tube: no fluid crosses its wall", wait=0)
        self.play(FadeIn(tube), run_time=1.5); self.wait(1.0)
        t = ValueTracker(0.0)
        seeds = [(-4.2 + 0.7 * k, s * y0) for k in range(12) for y0 in (0.3, 0.6, 0.95, 1.4) for s in (1, -1) if np.hypot(-4.2 + 0.7 * k, y0) > 1.15]

        TT = np.arange(0, 6.0001, 0.02)
        tracks = []
        for p0 in seeds:                                          # 预先算好每个颗粒的轨迹
            x, y = p0; tr = []
            for _ in TT:
                tr.append((x, y)); u, v = vel(x, y); x += u * 0.02; y += v * 0.02
                if x > 4.2: x -= 8.4
            tracks.append(np.array(tr))

        def advect(k, T):
            i = min(int(round(T / 0.02)), len(TT) - 1)
            return tracks[k][i]

        dots = always_redraw(lambda: VGroup(*[Dot(C + S * 0.95 * np.array([*advect(k, t.get_value()), 0]), radius=0.045, color=YELLOW) for k in range(len(seeds))]))
        self.add(dots)
        self.caption("流线挤在一起的地方流得快：圆柱上下两侧，流速是来流的 2 倍", "Where streamlines crowd together the flow is fast: beside the cylinder it reaches twice the oncoming speed", wait=0)
        self.play(t.animate.set_value(6.0), run_time=7, rate_func=linear)
        self.card([["连续性方程", "The continuity equation"],
                   MathTex(r"A_1v_1 = A_2v_2", font_size=48),
                   ["不可压缩流体在流管里，截面小的地方流速大", "in a flow tube of incompressible fluid, a narrow section means fast flow"],
                   ["流线越密，流速越大", "the denser the streamlines, the faster the flow"]])
