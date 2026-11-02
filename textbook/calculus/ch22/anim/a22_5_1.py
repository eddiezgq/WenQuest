"""动画 22.5.1（配图 22.5.1）：同一个单摆用三种方法、同样的步长（h = 0.05 s）仿真——
显式欧拉越摆越高、最后翻过顶点一圈圈转；RK4 能量缓慢减小；辛欧拉的能量上下抖动但始终不跑。"""
from manim import *
from wq_anim import *
import numpy as np

K = 9.81 / 0.5          # g/l
H = 0.05
TT = 20.0
N = int(round(TT / H))


def simulate(kind, n=N):
    q, v = 0.6, 0.0
    qs, es = [q], [0.5 * v * v / K - np.cos(q)]
    a = lambda q: -K * np.sin(q)
    for _ in range(n):
        if kind == "eu":
            q, v = q + H * v, v + H * a(q)
        elif kind == "sy":
            v = v + H * a(q)
            q = q + H * v
        else:
            y = np.array([q, v])
            F = lambda y: np.array([y[1], a(y[0])])
            k1 = F(y); k2 = F(y + H / 2 * k1); k3 = F(y + H / 2 * k2); k4 = F(y + H * k3)
            q, v = y + H / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        qs.append(q)
        es.append(0.5 * v * v / K - np.cos(q))
    return np.array(qs), np.array(es)


class Lesson(Base):
    def construct(self):
        self.title("22.5", "仿真里的单摆为什么会越摆越高", "Why a simulated pendulum swings ever higher")
        ts = np.arange(N + 1) * H
        meth = (("eu", "显式欧拉", "explicit Euler", RED), ("rk4", "RK4", "RK4", BLUE), ("sy", "辛欧拉", "symplectic Euler", GREEN))
        data = {k: simulate(k) for k, *_ in meth}
        tr = ValueTracker(0.0)
        Lr = 1.0
        objs = []
        for j, (k, zh, en, col) in enumerate(meth):
            piv = np.array([-4.2 + 4.2 * j, 1.35, 0])
            qs = data[k][0]
            tip = lambda piv=piv, qs=qs: piv + Lr * np.array([np.sin(np.interp(tr.get_value(), ts, qs)), -np.cos(np.interp(tr.get_value(), ts, qs)), 0])
            rod = always_redraw(lambda piv=piv, tip=tip, col=col: Line(piv, tip(), color=col, stroke_width=5))
            bob = always_redraw(lambda tip=tip, col=col: Dot(tip(), radius=0.13, color=col))
            ring = Circle(radius=Lr, color=GREY_D, stroke_width=1).move_to(piv)
            name = Text(zh, font_size=24, color=col).move_to(piv + np.array([-1.45, 0.75, 0]))
            objs += [ring, Dot(piv, color=GREY_B, radius=0.05), rod, bob, name]
        ax = Axes(x_range=[0, TT, 5], y_range=[-1, 2, 1], x_length=10.5, y_length=2.6, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(DOWN * 1.55)
        xl = Text("t / s", font_size=20).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = MathTex(r"E/(mgl)", font_size=26).next_to(ax.y_axis, UP, buff=0.05)
        top = DashedLine(ax.c2p(0, 1), ax.c2p(TT, 1), color=GREY_C, stroke_width=1.5)
        topl = Text("翻过顶点 over the top", font_size=16, color=GREY_C).next_to(ax.c2p(TT, 1), UP + LEFT * 0.1, buff=0.05).shift(LEFT * 1.2)
        self.play(*[FadeIn(o) for o in objs], Create(ax), FadeIn(xl), FadeIn(yl), Create(top), FadeIn(topl), run_time=1.5)
        self.caption("同一个单摆、同样的步长 h = 0.05 s，三种方法", "One pendulum, the same step h = 0.05 s, three methods", wait=0.8)

        def curve(k, col):
            def make():
                t = max(tr.get_value(), H)
                m = int(t / H) + 1
                pts = [ax.c2p(ts[i], float(np.clip(data[k][1][i], -1, 2))) for i in range(m)]
                return VMobject(color=col, stroke_width=3).set_points_as_corners(pts if len(pts) > 1 else pts * 2)
            return always_redraw(make)
        curves = [curve(k, col) for k, _, _, col in meth]
        self.add(*curves)
        self.caption("显式欧拉：每一步能量都多一点，越摆越高", "Explicit Euler: a little energy gained every step", wait=0)
        self.play(tr.animate.set_value(4.0), run_time=6, rate_func=linear)
        self.caption("翻过顶点后一圈圈转；另外两种方法的能量看上去不变", "Over the top it spins; the other two look constant", wait=0)
        self.play(tr.animate.set_value(TT), run_time=10, rate_func=linear)
        self.wait(0.8)
        self.play(*[FadeOut(m) for m in objs + curves + [ax, xl, yl, top, topl]])
        # 放大近一百倍看 2000 s：RK4 慢慢漂走，辛欧拉上下抖动但不漂
        n2 = 40000
        e_rk = simulate("rk4", n2)[1]
        e_sy = simulate("sy", n2)[1]
        ax2 = Axes(x_range=[0, 2000, 500], y_range=[-0.03, 0.03, 0.01], x_length=10.5, y_length=4.6, tips=False,
                   axis_config={"color": GREY_B, "font_size": 20}, x_axis_config={"include_numbers": True},
                   y_axis_config={"include_numbers": True, "decimal_number_config": {"num_decimal_places": 2}}).shift(DOWN * 0.4)
        yl2 = MathTex(r"\Delta E/(mgl)", font_size=26).next_to(ax2.y_axis, UP, buff=0.05)
        xl2 = Text("t / s", font_size=20).next_to(ax2.x_axis, RIGHT, buff=0.1)
        self.play(Create(ax2), FadeIn(yl2), FadeIn(xl2))
        self.caption("把能量误差放大近一百倍，算 2000 s", "Zoom in about 100× and run for 2000 s", wait=0.3)
        w = 200                                       # 每 10 s 取一段的最大、最小值
        tw = np.arange(n2 // w) * w * H + w * H / 2
        d_sy = (e_sy[1:] - e_sy[0]).reshape(-1, w)
        band = Polygon(*[ax2.c2p(t, v) for t, v in zip(tw, d_sy.max(axis=1))] + [ax2.c2p(t, v) for t, v in zip(tw[::-1], d_sy.min(axis=1)[::-1])],
                       color=GREEN, fill_opacity=0.35, stroke_width=1)
        d_rk = (e_rk[1:] - e_rk[0])[w - 1::w]
        rk = VMobject(color=BLUE, stroke_width=4).set_points_as_corners([ax2.c2p(t, v) for t, v in zip(tw, d_rk)])
        l1 = Text("辛欧拉 symplectic Euler", font_size=20, color=GREEN).move_to(ax2.c2p(1000, 0.026))
        l2 = Text("RK4", font_size=22, color=BLUE).next_to(ax2.c2p(2000, d_rk[-1]), DOWN, buff=0.15).shift(LEFT * 0.4)
        self.play(Create(rk), FadeIn(band), run_time=4, rate_func=linear)
        self.play(FadeIn(l1), FadeIn(l2))
        self.caption("RK4 每步误差极小，但一直朝一个方向漂；辛欧拉误差大些，却始终有界", "RK4 errors are tiny but drift one way; symplectic errors are larger yet stay bounded", wait=2)
        self.play(*[FadeOut(m) for m in (ax2, yl2, xl2, band, rk, l1, l2)])
        self.card([["守恒与辛积分", "Conservation and symplectic integration"],
                   MathTex(r"\text{Euler: }\det=1+h^2\omega^2>1,\qquad \text{symplectic: }\det=1", font_size=40),
                   ["显式欧拉每步把相空间的面积放大，能量越来越大；辛方法保持面积，能量误差长期有界",
                    "Explicit Euler inflates phase-space area each step; symplectic methods keep it, so energy error stays bounded"]])
