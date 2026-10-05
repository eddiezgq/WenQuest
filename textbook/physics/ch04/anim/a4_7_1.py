"""动画 4.7.1（配图 4.7.1）：两台龙门小车吊着同样的货物，各移动 3.0 m（最大速度 0.80 m/s、最大加速度 0.50 m/s²，绳长 1.2 m）。
上面的小车按梯形速度曲线运动，下面的按 S 形速度曲线（名义上升时间 a/j = 2.0 s）运动。梯形曲线先到，货物晃得厉害；
S 形曲线晚约 2 s 到，货物几乎不晃。摆角按单摆方程数值计算（与程序 4.7.1 相同）；导轨长度与绳长按同一比例画出。"""
from manim import *
from wq_anim import *
import numpy as np

G, LR = 9.81, 1.2
DIST, VG, AG = 3.0, 0.8, 0.5


def profile(tj):
    """与 _kin.scurve 相同的加速度曲线（tj = a/j，0 为梯形），返回 (T, a(t))。"""
    def acc(vp):
        t1 = min(tj, np.sqrt(vp * tj / AG)) if tj > 0 else 0.0
        ap = AG * t1 / tj if tj > 0 else AG
        tca = max(0.0, vp / ap - t1); ta = 2 * t1 + tca
        return t1, ap, tca, ta, vp * ta / 2
    vp = VG
    if 2 * acc(vp)[4] > DIST:
        lo, hi = 0.0, VG
        for _ in range(60):
            m = 0.5 * (lo + hi); lo, hi = (m, hi) if 2 * acc(m)[4] <= DIST else (lo, m)
        vp = lo
    t1, ap, tca, ta, da = acc(vp)
    tc = (DIST - 2 * da) / vp; T = 2 * ta + tc

    def bump(u):
        if u < 0 or u > ta:
            return 0.0
        return ap if t1 == 0 else max(0.0, min(ap * u / t1, ap, ap * (ta - u) / t1))
    return T, (lambda t: 0.0 if (t < 0 or t > T) else bump(t) - bump(t - ta - tc))


def simulate(tj, tend=11.0, h=0.002):
    """小车位置与摆角随时间的表。"""
    T, a = profile(tj)
    n = int(tend / h); ts = np.arange(n + 1) * h
    x = np.zeros(n + 1); v = 0.0; th = np.zeros(n + 1); om = 0.0
    for i in range(n):
        t = ts[i]; ai = a(t)
        f = lambda q, w, tt: (w, -(G / LR) * np.sin(q) - a(tt) / LR * np.cos(q))
        k1 = f(th[i], om, t); k2 = f(th[i] + h / 2 * k1[0], om + h / 2 * k1[1], t + h / 2)
        k3 = f(th[i] + h / 2 * k2[0], om + h / 2 * k2[1], t + h / 2); k4 = f(th[i] + h * k3[0], om + h * k3[1], t + h)
        th[i + 1] = th[i] + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); om += h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        x[i + 1] = x[i] + v * h + 0.5 * ai * h * h; v += ai * h
    return T, ts, x, th


class Lesson(Base):
    def construct(self):
        self.title("4.7", "梯形与 S 形速度曲线", "Trapezoidal and S-curve profiles")
        runs = [(0.0, BLUE, ("梯形速度曲线", "trapezoidal"), 1.7), (2.0, RED, ("S 形速度曲线", "S-curve"), -0.5)]
        sims = [simulate(tj) for tj, *_ in runs]
        X0, SC = -1.6, 1.2                      # 1 m 画成 1.2 个单位，导轨与绳长同一比例
        tr = ValueTracker(0.0)
        groups = []
        for (tj, col, name, y), (T, ts, x, th) in zip(runs, sims):
            rail = Line([X0 - 0.6, y, 0], [X0 + DIST * SC + 0.6, y, 0], color=GREY_B, stroke_width=4)
            lab = bi(name, 22).next_to(rail, LEFT, buff=0.2).shift(UP * 0.0)
            goal = DashedLine([X0 + DIST * SC, y + 0.2, 0], [X0 + DIST * SC, y - 1.7, 0], color=GREY_C)
            self.play(Create(rail), FadeIn(lab), Create(goal), run_time=0.6)

            def rig(ts=ts, x=x, th=th, y=y, col=col):
                i = min(len(ts) - 1, int(tr.get_value() / (ts[1] - ts[0])))
                px = X0 + x[i] * SC; q = th[i]
                top = np.array([px, y, 0]); bob = top + LR * SC * np.array([np.sin(q), -np.cos(q), 0])
                trolley = Rectangle(width=0.6, height=0.25, color=col, fill_color=col, fill_opacity=0.8).move_to(top + UP * 0.05)
                return VGroup(trolley, Line(top, bob, color=WHITE, stroke_width=2), Square(0.32, color="#d29922", fill_color="#5a3d0a", fill_opacity=1).move_to(bob))
            g = always_redraw(rig)
            off = always_redraw(lambda ts=ts, th=th, y=y, col=col: VGroup(
                zh("货物偏离竖直线", 18, GREY_B), MathTex(r"%+.0f\ \mathrm{mm}" % (1000 * LR * np.sin(th[min(len(ts) - 1, int(tr.get_value() / (ts[1] - ts[0])))])), font_size=28, color=col)
            ).arrange(DOWN, buff=0.08).move_to([4.6, y - 0.6, 0]))
            self.add(g, off); groups.append(g)
        clock = always_redraw(lambda: MathTex(r"t = %.1f\ \mathrm s" % tr.get_value(), font_size=30).to_edge(RIGHT, buff=0.5).shift(UP * 2.4))
        self.add(clock)
        self.caption("两台小车吊着同样的货物，各移动 3 m", "Two trolleys carry the same hanging load 3 m", wait=0)
        self.play(tr.animate.set_value(sims[0][0]), run_time=4, rate_func=linear)
        self.caption("梯形曲线先到，但货物还在大幅摆动", "The trapezoid arrives first, but the load keeps swinging hard", wait=0)
        self.play(tr.animate.set_value(sims[1][0]), run_time=2.5, rate_func=linear)
        self.caption("S 形曲线晚约 2 s 到达，货物几乎不晃", "The S-curve arrives about 2 s later with hardly any swing", wait=0)
        self.play(tr.animate.set_value(11.0), run_time=4, rate_func=linear)
        self.card([["梯形与 S 形速度曲线", "Trapezoidal and S-curve profiles"],
                   ["梯形：最快，但加速度突变，激起振动和摆动", "Trapezoid: fastest, but jumps in acceleration excite swing"],
                   ["S 形：限制加加速度，慢一点，平稳得多", "S-curve: limited jerk, a little slower, much smoother"]])
