"""动画 7.2.2（配图 7.2.4）：四根同样的连杆分别用欧拉法（h = 0.02 s）、RK4（h = 0.08 s，计算量与韦莱法相同）、
辛欧拉法（0.02 s）、施特默-韦莱法（0.02 s）仿真。先实时看 6 s 的摆动，再快进到 1000 s 看能量条。"""
from manim import *
from wq_anim import *
import numpy as np
import math

WN2 = 29.43


def acc(th):
    return -WN2 * math.sin(th)


def run(method, h, T):
    th, om = math.pi / 2, 0.0
    n = int(round(T / h))
    ths, oms = [th], [om]
    for _ in range(n):
        if method == "euler":
            th, om = th + h * om, om + h * acc(th)
        elif method == "rk4":
            def f(x):
                return np.array([x[1], acc(x[0])])
            x = np.array([th, om])
            k1 = f(x)
            k2 = f(x + h / 2 * k1)
            k3 = f(x + h / 2 * k2)
            k4 = f(x + h * k3)
            x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            th, om = float(x[0]), float(x[1])
        elif method == "symp":
            om = om + h * acc(th)
            th = th + h * om
        else:
            om = om + h / 2 * acc(th)
            th = th + h * om
            om = om + h / 2 * acc(th)
        ths.append(th)
        oms.append(om)
    ths, oms = np.array(ths), np.array(oms)
    E = (0.5 * oms ** 2 + WN2 * (1 - np.cos(ths))) / WN2
    return h, ths, E


METHODS = [("euler", 0.02, "欧拉法", "Euler", RED), ("rk4", 0.08, "RK4（h = 0.08 s）", "RK4 (h = 0.08 s)", BLUE),
           ("symp", 0.02, "辛欧拉法", "symplectic Euler", ORANGE), ("verlet", 0.02, "施特默-韦莱法", "Störmer–Verlet", PURPLE)]


class Lesson(Base):
    def construct(self):
        self.title("7.2", "长时间仿真中的能量", "Energy in a long simulation")
        data = {}
        for m, h, *_ in METHODS:
            data[m] = run(m, h, 1000.0 if m != "euler" else 60.0)
        t = ValueTracker(0.0)
        cells = []
        for i, (m, h, zname, ename, col) in enumerate(METHODS):
            cx = -4.8 + 3.2 * i
            pivot = np.array([cx, 1.25, 0])
            base_y = -1.75
            bar_x = cx + 0.95
            cells.append((m, pivot, base_y, bar_x, col))
            name = VGroup(zh(zname, 20, col), en(ename, 15)).arrange(DOWN, buff=0.05).move_to(np.array([cx + 0.5, base_y - 0.45, 0]))
            frame = Line(np.array([bar_x - 0.25, base_y, 0]), np.array([bar_x + 0.25, base_y, 0]), color=GREY_B)
            ref = DashedLine(np.array([bar_x - 0.3, base_y + 1.0, 0]), np.array([bar_x + 0.3, base_y + 1.0, 0]), color=WHITE,
                             stroke_width=2)
            self.add(name, frame, ref)

        def idx(m, tt):
            h, ths, E = data[m]
            return min(int(tt / h), len(ths) - 1)

        def pend(m, pivot, col):
            th = data[m][1][idx(m, t.get_value())]
            tip = pivot + 1.3 * np.array([math.sin(th), -math.cos(th), 0])
            return VGroup(Line(pivot, tip, color=col, stroke_width=9), Dot(pivot, radius=0.07, color=WHITE))

        def bar(m, base_y, bar_x, col):
            e = data[m][2][idx(m, t.get_value())]
            hgt = 1.0 * min(e, 2.6)
            r = Rectangle(width=0.4, height=max(hgt, 0.01), color=col, fill_color=col, fill_opacity=0.7, stroke_width=1)
            r.move_to(np.array([bar_x, base_y + max(hgt, 0.01) / 2, 0]))
            lab = Text("%.3f" % e if e < 9.99 else "> 10", font=LATIN, font_size=18, color=col).next_to(r, UP, buff=0.08)
            return VGroup(r, lab)

        pends = [always_redraw(lambda m=m, p=p, c=c: pend(m, p, c)) for m, p, b, x, c in cells]
        bars = [always_redraw(lambda m=m, b=b, x=x, c=c: bar(m, b, x, c)) for m, p, b, x, c in cells]
        clock = always_redraw(lambda: Text("t = %.0f s" % t.get_value(), font=LATIN, font_size=26, color=YELLOW).to_corner(UR, buff=0.45))
        note = VGroup(zh("能量条：E / E(0)，虚线为 1", 18, MUTED), en("bars: E / E(0); dashed line = 1", 14)).arrange(DOWN, buff=0.05).to_corner(UR, buff=0.45).shift(DOWN * 0.6)
        self.add(*pends, *bars, clock, note)
        self.caption("同一根连杆，从水平位置释放，四种积分方法", "One link released from horizontal, four integrators", wait=0.5)
        self.caption("实时 6 s：欧拉法的摆幅越来越大", "6 s in real time: Euler's swing keeps growing", wait=0)
        self.play(t.animate.set_value(6.0), run_time=6, rate_func=linear)
        self.play(*[FadeOut(p) for p in pends], run_time=0.4)
        for p in pends:
            p.clear_updaters()
        self.caption("快进到 1000 s：RK4 慢慢漏掉能量，辛方法的能量始终有界", "Fast-forward to 1000 s: RK4 slowly leaks energy; the symplectic ones stay bounded", wait=0)
        self.play(t.animate.set_value(1000.0), run_time=7, rate_func=linear)
        self.wait(1.2)
        self.card([["辛积分", "Symplectic integration"],
                   MathTex(r"\dot\theta_{k+1} = \dot\theta_k + h\,a(\theta_k),\qquad \theta_{k+1} = \theta_k + h\,\dot\theta_{k+1}", font_size=40),
                   ["保持相空间面积，能量误差有界、不漂移", "Phase-space area is kept; the energy error stays bounded"]])
