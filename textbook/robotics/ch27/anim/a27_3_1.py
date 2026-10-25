"""动画 27.3.1（配图 27.3.1）：碰撞与恢复系数。数值与算例 27.3.1、27.3.2 相同。
(1) 三个球从 0.5 m 落下，恢复系数分别为 0.88、0.57、0（MuJoCo 中 solref 的阻尼比 0.05、0.2 和默认的 1）：每次弹起的高度是上一次的 e² 倍。
(2) 碰撞中的接触力（示意，形状按 Ø10 mm 钢球撞钢板，e ≈ 0.7）：线性弹簧-阻尼器的力一碰上就跳变，分开前变成拉力（虚线，实际仿真中截掉）；
    亨特-克罗斯利模型 λ = Kδ^{3/2}(1 + cδ̇) 的力从零开始、回到零。
(3) 恢复系数与撞击速度：线性模型的 e 不变；亨特-克罗斯利模型（1 m/s 时 e = 0.8）的 e 随速度增大而减小：0.1 m/s 时 0.97，3 m/s 时 0.55。"""
from manim import *
from wq_anim import *
import numpy as np
import math

G = 9.81
H0 = 0.5
ES = [0.875, 0.573, 0.0]
ZETA = ["0.05", "0.2", "1"]


def bounce_z(e, t):
    """从 H0 落下、恢复系数 e 的球在 t 时刻的高度。"""
    v0 = math.sqrt(2 * G * H0)
    tf = math.sqrt(2 * H0 / G)
    if t < tf:
        return H0 - 0.5 * G * t * t
    t -= tf
    v = e * v0
    while v > 0.05:
        T = 2 * v / G
        if t < T:
            return v * t - 0.5 * G * t * t
        t -= T
        v *= e
    return 0.0


def hc_curve(e_t=0.7, n=160):
    """亨特-克罗斯利模型的无量纲接触力（K = 1，m = 1，v = 1）。"""
    c = 8 * (1 - e_t) / (5 * e_t)
    d, dd, t, dt = 0.0, 1.0, 0.0, 2e-4
    T, F = [0.0], [0.0]
    while True:
        lam = max(d, 0) ** 1.5 * (1 + c * dd)
        dd -= lam * dt
        d += dd * dt
        t += dt
        if d <= 0 or lam < 0:
            break
        T.append(t); F.append(lam)
    k = max(1, len(T) // n)
    return np.array(T[::k]), np.array(F[::k])


def kv_curve(e_t=0.7, n=160):
    """线性弹簧-阻尼器（同样的 e，固有频率取 1）的接触力，含负的部分。"""
    z = -math.log(e_t) / math.sqrt(math.pi ** 2 + math.log(e_t) ** 2)
    wd = math.sqrt(1 - z * z)
    ts = np.linspace(0, math.pi / wd, n)
    x = np.exp(-z * ts) * np.sin(wd * ts) / wd
    xd = np.exp(-z * ts) * (np.cos(wd * ts) - z * np.sin(wd * ts) / wd)
    return ts, x + 2 * z * xd


class Lesson(Base):
    def construct(self):
        self.title("27.3", "碰撞与恢复系数", "Impact and the coefficient of restitution")
        gy = -2.0
        sc = 7.0
        self.add(Line([-6, gy, 0], [6, gy, 0], color=GREY_B, stroke_width=4))
        t = ValueTracker(0)
        balls = VGroup()
        for i, (e, z) in enumerate(zip(ES, ZETA)):
            x = -3.5 + 3.5 * i
            b = always_redraw(lambda e=e, x=x: Circle(radius=0.25, color=[BLUE, GREEN, ORANGE][ES.index(e)], fill_opacity=0.8)
                              .move_to([x, gy + 0.25 + sc * bounce_z(e, t.get_value()), 0]))
            balls.add(b)
            self.add(b, bi([f"ζ = {z}，e = {e:.2f}", f"ζ = {z}, e = {e:.2f}"], 24, YELLOW).move_to([x, 2.4, 0]))
        self.play(t.animate.set_value(2.6), run_time=6.0, rate_func=linear)
        self.caption("每次弹起的高度是上一次的 e² 倍；MuJoCo 默认的阻尼比为 1，物体落地就不弹",
                     "Each bounce reaches e² of the last; with MuJoCo's default damping ratio of 1, nothing bounces", wait=2.0)
        self.clear_stage()
        # (2) 接触力
        ax = Axes(x_range=[0, 3.5, 1], y_range=[-0.3, 1.0, 0.5], x_length=9, y_length=4, tips=False,
                  axis_config=dict(color=GREY_B, stroke_width=2, include_ticks=False)).move_to([0, 0.2, 0])
        self.add(ax, zh("t", 24, MUTED).next_to(ax.x_axis.get_end(), DOWN), zh("λ", 24, MUTED).next_to(ax.y_axis.get_end(), LEFT))
        tk, fk = kv_curve()
        th, fh = hc_curve()
        sk = 3.2 / tk[-1]
        sh = 3.2 / th[-1]
        fsk = 0.8 / fk.max()
        fsh = 0.8 / fh.max()
        pos = [ax.c2p(a * sk, max(b, 0) * fsk) for a, b in zip(tk, fk)]
        neg = [ax.c2p(a * sk, b * fsk) for a, b in zip(tk, fk) if b < 0]
        kv = VMobject(color=RED, stroke_width=5).set_points_as_corners([ax.c2p(0, 0)] + pos)
        hc = VMobject(color=GREEN, stroke_width=5).set_points_smoothly([ax.c2p(a * sh, b * fsh) for a, b in zip(th, fh)])
        self.play(Create(kv), run_time=1.5)
        if len(neg) > 1:
            self.add(DashedVMobject(VMobject(color=RED, stroke_width=3).set_points_as_corners(neg), num_dashes=12))
        self.add(bi(["线性弹簧-阻尼：一碰上就跳变", "linear spring-damper: jumps on contact"], 22, RED).move_to(ax.c2p(1.0, 0.95)))
        self.play(Create(hc), run_time=1.5)
        self.add(bi(["亨特-克罗斯利：从零开始、回到零", "Hunt–Crossley: starts and ends at zero"], 22, GREEN).move_to(ax.c2p(2.6, 0.7)))
        self.caption("线性模型的阻尼力在接触瞬间就有，分开前还会变成拉力；亨特-克罗斯利模型的力随压入量一起从零长出来",
                     "The linear model's damping force appears at once and turns into a pull before separation; Hunt–Crossley grows from zero", wait=2.5)
        self.clear_stage()
        # (3) e 与速度
        ax2 = Axes(x_range=[0, 2.0, 0.5], y_range=[0, 1.05, 0.25], x_length=8, y_length=3.8, tips=False,
                   axis_config=dict(color=GREY_B, stroke_width=2, include_ticks=False)).move_to([0, 0.1, 0])
        X = lambda v: math.log10(v) + 1.4                                  # noqa: E731  横轴：对数刻度
        self.add(ax2, zh("v", 24, MUTED).next_to(ax2.x_axis.get_end(), RIGHT), zh("e", 24, MUTED).next_to(ax2.y_axis.get_end(), LEFT))
        for v in (0.1, 1.0, 3.0):
            self.add(zh(f"{v:g} m/s", 18, MUTED).next_to(ax2.c2p(X(v), 0), DOWN, buff=0.1))
        for e in (0.5, 1.0):
            self.add(zh(f"{e:g}", 18, MUTED).next_to(ax2.c2p(0, e), LEFT, buff=0.1))
        vs = [0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 3.0]
        ev = [0.987, 0.974, 0.949, 0.926, 0.882, 0.789, 0.648, 0.547]          # 程序 27.3.1 的积分结果
        pts = [ax2.c2p(X(v), e) for v, e in zip(vs, ev)]
        self.play(Create(DashedLine(ax2.c2p(0, 0.8), ax2.c2p(2.0, 0.8), color=RED)), run_time=0.8)
        self.play(Create(VMobject(color=GREEN, stroke_width=5).set_points_smoothly(pts)), run_time=1.5)
        self.add(*[Dot(p, color=GREEN, radius=0.06) for p in pts])
        self.caption("实验中恢复系数随撞击速度增大而减小：亨特-克罗斯利模型（绿）反映了这一点，线性模型（红虚线）不能",
                     "In experiments restitution falls with impact speed; Hunt–Crossley (green) shows it, the linear model (red dashed) cannot", wait=2.5)
        self.card([["碰撞与恢复系数", "Impact and restitution"],
                   MathTex(r"e = \frac{v^+}{v^-},\qquad P = (1+e)\,\bar m\,v^-", font_size=40),
                   MathTex(r"\lambda = K\delta^{3/2}(1 + c\dot\delta),\quad c = \frac{8(1-e)}{5e\,v^-}", font_size=38),
                   ["钢件相撞：力很大、时间极短；仿真要用软化的接触去调 e", "Steel impacts: huge brief forces; simulators tune e with softened contact"]])
