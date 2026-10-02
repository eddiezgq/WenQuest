"""动画 11.2.2（配图 11.2.2c）：本内特机构。四个转动关节组成的空间单回路，公式给出 −2，满足 a/sinα = b/sinβ 时却能连续运动。
尺寸与程序 11.2.1 相同：a = 0.3 m，α = 30°，β = 60°，b = a sinβ / sinα。"""
from manim import *
from wq_anim import *
import numpy as np

AL, BE, AA = np.radians(30), np.radians(60), 0.3
BB = AA * np.sin(BE) / np.sin(AL)
K = np.sin((BE + AL) / 2) / np.sin((BE - AL) / 2)
SC = 7.5
O = np.array([-2.2, -1.0, 0.0])


def dh(t, a, al):
    ct, st, ca, sa = np.cos(t), np.sin(t), np.cos(al), np.sin(al)
    return np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, 0], [0, 0, 0, 1.0]])


def frames(t1):
    t2 = 2 * np.arctan(K / np.tan(t1 / 2))
    th = [t1, t2, -t1, -t2]
    T, out = np.eye(4), []
    for k in range(4):
        out.append(T.copy())
        T = T @ dh(th[k], [AA, BB][k % 2], [AL, BE][k % 2])
    return out


def P(p):
    # 先把机构绕竖直轴转一下，便于观看
    c, s = np.cos(0.6), np.sin(0.6)
    q = np.array([c * p[0] - s * p[1], s * p[0] + c * p[1], p[2]])
    return proj3(q, O, SC)


def draw(t1):
    fr = frames(t1)
    g = VGroup()
    cols = [BLUE, ORANGE, BLUE, ORANGE]
    for k in range(4):
        g.add(Line(P(fr[k][:3, 3]), P(fr[(k + 1) % 4][:3, 3]), color=cols[k], stroke_width=10))
    for k in range(4):
        zk, qk = fr[k][:3, 2], fr[k][:3, 3]
        g.add(Line(P(qk - 0.14 * zk), P(qk + 0.14 * zk), color=RED, stroke_width=5))
        g.add(Dot(P(qk), radius=0.07, color=WHITE))
    return g


class Lesson(Base):
    def construct(self):
        self.title("11.2", "本内特机构：公式说 −2，它却能动", "The Bennett linkage: formula −2, yet it moves")
        t = ValueTracker(0.5)
        m = always_redraw(lambda: draw(t.get_value()))
        info = VGroup(MathTex(r"N = 4,\ J = 4,\ f_i = 1", font_size=34),
                      MathTex(r"M = 6(4-1-4) + 4 = -2", font_size=34),
                      MathTex(r"\frac{a}{\sin\alpha} = \frac{b}{\sin\beta}", font_size=40, color=YELLOW)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        info.to_corner(UR, buff=0.6).shift(DOWN * 0.9)
        self.play(FadeIn(m), Write(info[:2]), run_time=1.0)
        self.caption("四个转动关节连成空间四边形，红线是四根转轴；一般情况下它是刚硬的",
                     "Four revolute joints close a spatial loop (red: the axes); in general it is rigid", wait=1.0)
        self.play(Write(info[2]), run_time=0.8)
        self.caption("本内特（1903）：对边等长、扭角相等，且 a/sinα = b/sinβ 时，它能连续运动",
                     "Bennett (1903): equal opposite links and twists with a/sin α = b/sin β, and it moves", wait=0)
        self.play(t.animate.set_value(2.6), run_time=5.0, rate_func=smooth)
        self.play(t.animate.set_value(0.5), run_time=4.0, rate_func=smooth)
        self.caption("几何条件让 6 个闭环方程中的 3 个自动满足：秩为 3，自由度 4 − 3 = 1",
                     "The geometry makes 3 of the 6 loop equations redundant: rank 3, freedom 4 − 3 = 1", wait=2.0)
        self.card([["过约束机构", "Overconstrained mechanism"],
                   MathTex(r"M_{\mathrm{inst}} = n - \mathrm{rank}\,(\mathcal{S}_1\ \cdots\ \mathcal{S}_n) \ \ge\ M", font_size=44),
                   ["格吕布勒公式只是下界", "Grübler's count is only a lower bound"]])
