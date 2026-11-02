"""动画 21.2.1（配图 21.2.1）：单摆与它的相图同步——轻推时来回摆动（闭曲线），重推时一圈圈转（波浪线），
恰在分界线上时越来越慢地爬向最高点；加上阻尼，相点螺旋地落向平衡点。"""
from manim import *
from wq_anim import *
import numpy as np

K = 9.81 / 0.5
WS = 2 * np.sqrt(K)


def traj(w0, c=0.0, T=6.0, dt=0.002):
    """四阶龙格–库塔法积分单摆方程，返回按时间插值的解函数。"""
    f = lambda y: np.array([y[1], -K * np.sin(y[0]) - c * y[1]])
    n = int(round(T / dt))
    ts = np.linspace(0, n * dt, n + 1)
    ys = np.zeros((n + 1, 2))
    ys[0] = [0.0, w0]
    for i in range(n):
        y = ys[i]
        k1 = f(y); k2 = f(y + dt / 2 * k1); k3 = f(y + dt / 2 * k2); k4 = f(y + dt * k3)
        ys[i + 1] = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return lambda t: np.array([np.interp(t, ts, ys[:, 0]), np.interp(t, ts, ys[:, 1])])


class Lesson(Base):
    def construct(self):
        self.title("21.2", "单摆的相图", "Phase portrait of a pendulum")
        piv = np.array([-4.6, 1.0, 0])
        L = 1.8
        ax = Axes(x_range=[-np.pi, 3 * np.pi, np.pi], y_range=[-12, 12, 4], x_length=7.4, y_length=4.6, tips=False,
                  axis_config={"color": GREY_B}).shift(RIGHT * 2.6 + DOWN * 0.3)
        lab = VGroup(MathTex(r"\theta", font_size=30).next_to(ax.x_axis, RIGHT, buff=0.1), MathTex(r"\omega", font_size=30).next_to(ax.y_axis, UP, buff=0.1))
        curves = VGroup()
        for E in np.linspace(-K + 2, 3 * K, 10):
            xs = np.linspace(-np.pi, 3 * np.pi, 600)
            v2 = 2 * (E + K * np.cos(xs))
            for sgn in (1, -1):
                seg = []
                for x, v in zip(xs, v2):
                    if v >= 0:
                        seg.append(ax.c2p(x, sgn * np.sqrt(v)))
                    elif len(seg) > 2:
                        curves.add(VMobject(color=GREY_C, stroke_width=1.2).set_points_as_corners(seg))
                        seg = []
                    else:
                        seg = []
                if len(seg) > 2:
                    curves.add(VMobject(color=GREY_C, stroke_width=1.2).set_points_as_corners(seg))
        sep = VGroup(*[ax.plot(lambda x, s=s: s * WS * np.abs(np.cos(x / 2)), x_range=[-np.pi, 3 * np.pi], color=RED, stroke_width=3) for s in (1, -1)])
        self.play(Create(ax), FadeIn(lab), Create(curves, lag_ratio=0.05), run_time=2)
        self.play(Create(sep))
        self.caption("相图：每条曲线是一个能量值；红线是分界线", "Each curve is one energy level; red is the separatrix", wait=0.5)
        st = {"sol": traj(0.0), "tr": ValueTracker(0.0)}
        cur = lambda: st["sol"](st["tr"].get_value())
        tip = lambda: piv + L * np.array([np.sin(cur()[0]), -np.cos(cur()[0]), 0])
        rod = always_redraw(lambda: Line(piv, tip(), color=STEEL, stroke_width=6))
        bob = always_redraw(lambda: Dot(tip(), radius=0.16, color=ORANGE))
        pt = always_redraw(lambda: Dot(ax.c2p(((cur()[0] + np.pi) % (4 * np.pi)) - np.pi, cur()[1]), radius=0.09, color=YELLOW))
        pivot = Dot(piv, color=GREY_B)
        self.add(pivot, rod, bob, pt)
        for w0, c, T, zh_, en_ in ((0.6 * WS, 0.0, 3.2, "轻推：来回摆动，相点沿闭曲线绕圈", "Gentle push: swings, a closed orbit"),
                                   (1.15 * WS, 0.0, 1.1, "重推：一圈圈转，相点沿波浪线向右", "Hard push: rotates, a wavy orbit"),
                                   (0.9999 * WS, 0.0, 3.0, "恰在分界线上：越来越慢地爬向最高点", "On the separatrix: crawls ever slower to the top"),
                                   (1.2 * WS, 0.5, 9.0, "加上阻尼：能量减小，相点螺旋地落向平衡点", "With damping: energy falls, the point spirals in")):
            st["sol"] = traj(w0, c, T)
            st["tr"] = ValueTracker(0.0)
            path = always_redraw(lambda: VMobject(color=YELLOW, stroke_width=2.5).set_points_as_corners(
                [ax.c2p(((st["sol"](t)[0] + np.pi) % (4 * np.pi)) - np.pi, st["sol"](t)[1]) for t in np.linspace(0, max(st["tr"].get_value(), 1e-3), 300)]))
            self.add(path)
            self.caption(zh_, en_, wait=0)
            self.play(st["tr"].animate.set_value(T), run_time=min(T * 1.3, 8), rate_func=linear)
            self.play(FadeOut(path), run_time=0.3)
        self.wait(0.5)
        self.play(*[FadeOut(m) for m in (ax, curves, sep, lab, rod, bob, pt, pivot)])
        self.card([["相平面", "The phase plane"],
                   MathTex(r"E=\tfrac12\omega^2-\tfrac gl\cos\theta,\qquad \dot E=-c\,\omega^2\le 0", font_size=42),
                   ["无阻尼时轨线是能量的等值线；分界线 E = g/l 分开摆动与转动；有阻尼时能量单调减小", "Undamped orbits are energy levels; E = g/l separates swinging from rotating; damping makes energy fall"]])
