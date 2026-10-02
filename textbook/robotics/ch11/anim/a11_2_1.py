"""动画 11.2.1（配图 11.2.1）：四杆机构一个输入就够；五杆机构要两个输入；平行四边形加一根曲柄，公式给出 0，它照样能动。"""
from manim import *
from wq_anim import *
import numpy as np

S = 6.0                      # 1 m 画成 6 个单位


def cint(c0, r0, c1, r1, sign=1):
    d = np.linalg.norm(c1 - c0)
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = np.sqrt(max(r0 * r0 - a * a, 0.0))
    e = (c1 - c0) / d
    m = c0 + a * e
    return m + sign * h * np.array([-e[1], e[0], 0.0])


def u(t):
    return np.array([np.cos(t), np.sin(t), 0.0])


def links(pts_pairs, colors):
    g = VGroup()
    for (p, q), c in zip(pts_pairs, colors):
        g.add(Line(p, q, color=c, stroke_width=10))
    return g


def pins(pts, fixed=()):
    g = VGroup()
    for i, p in enumerate(pts):
        g.add(Dot(p, radius=0.09, color=WHITE))
        if i in fixed:
            g.add(Triangle(color=GREY_B, fill_opacity=0.4).scale(0.18).move_to(p + DOWN * 0.2))
    return g


def count(lines):
    return VGroup(*[MathTex(x, font_size=34) for x in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UR, buff=0.6).shift(DOWN * 0.8)


class Lesson(Base):
    def construct(self):
        self.title("11.2", "数自由度：一个输入还是两个", "Counting degrees of freedom")
        # ---------- 四杆机构
        O = np.array([-2.0, -1.4, 0])
        A, D = O, O + S * np.array([0.40, 0, 0])
        t = ValueTracker(1.05)

        def four():
            B = A + S * 0.15 * u(t.get_value())
            C = cint(B, S * 0.35, D, S * 0.30, 1)
            return VGroup(links([(A, B), (B, C), (C, D)], [BLUE, ORANGE, BLUE]), pins([A, B, C, D], fixed=(0, 3)))

        m4 = always_redraw(four)
        c4 = count([r"N = 4,\ J = 4", r"M = 3(4-1-4) + 4 = 1"])
        self.play(FadeIn(m4), Write(c4), run_time=0.8)
        self.caption("四杆机构：转动曲柄这一个输入，其余各杆的位置都确定了", "Four-bar: one input, the crank, fixes every link", wait=0)
        self.play(t.animate.set_value(1.05 + 2 * PI), run_time=4.0, rate_func=linear)
        self.play(FadeOut(m4), FadeOut(c4), run_time=0.4)
        # ---------- 五杆机构
        A5, E5 = O + S * np.array([0.0, 0, 0]), O + S * np.array([0.30, 0, 0])
        t1, t2 = ValueTracker(np.radians(110)), ValueTracker(np.radians(70))

        def five():
            B = A5 + S * 0.2 * u(t1.get_value())
            Dd = E5 + S * 0.2 * u(t2.get_value())
            C = cint(B, S * 0.3, Dd, S * 0.3, -1)
            return VGroup(links([(A5, B), (B, C), (C, Dd), (Dd, E5)], [BLUE, ORANGE, ORANGE, BLUE]), pins([A5, B, Dd, E5], fixed=(0, 3)),
                          Dot(C, radius=0.11, color=RED))

        m5 = always_redraw(five)
        tip = TracedPath(lambda: cint(A5 + S * 0.2 * u(t1.get_value()), S * 0.3, E5 + S * 0.2 * u(t2.get_value()), S * 0.3, -1),
                         stroke_color=RED, stroke_width=3)
        c5 = count([r"N = 5,\ J = 5", r"M = 3(5-1-5) + 5 = 2"])
        self.play(FadeIn(m5), Write(c5), run_time=0.8)
        self.add(tip)
        self.caption("五杆机构：两个输入一起变，末端才能走遍一块区域", "Five-bar: two inputs together steer the tip over an area", wait=0)
        self.play(t1.animate.set_value(np.radians(150)), run_time=1.3)
        self.play(t2.animate.set_value(np.radians(30)), run_time=1.3)
        self.play(t1.animate.set_value(np.radians(95)), t2.animate.set_value(np.radians(60)), run_time=1.3)
        self.play(FadeOut(m5), FadeOut(c5), FadeOut(tip), run_time=0.4)
        # ---------- 平行四边形加一根曲柄
        G = [O + S * np.array([x, 0, 0]) for x in (-0.15, 0.15, 0.45)]
        tp = ValueTracker(1.05)

        def para():
            e = S * 0.25 * u(tp.get_value())
            tips = [g + e for g in G]
            return VGroup(Line(tips[0], tips[2], color=ORANGE, stroke_width=10),
                          *[Line(g, g + e, color=(RED if k == 1 else BLUE), stroke_width=10) for k, g in enumerate(G)],
                          pins(G + tips, fixed=(0, 1, 2)))

        mp = always_redraw(para)
        cp = count([r"N = 5,\ J = 6", r"M = 3(5-1-6) + 6 = 0", r"\text{actual: } M = 1"])
        self.play(FadeIn(mp), Write(cp), run_time=0.8)
        self.caption("加一根等长、平行的曲柄（红）：公式说它不能动，它照样转——约束是重复的",
                     "An equal, parallel extra crank (red): the formula says rigid, yet it moves; a constraint repeats", wait=0)
        self.play(tp.animate.set_value(1.05 + 2 * PI), run_time=4.0, rate_func=linear)
        self.wait(0.5)
        self.card([["格吕布勒公式", "Grübler's formula"],
                   MathTex(r"M = m(N-1-J) + \sum_{i} f_i", font_size=46),
                   ["约束独立时成立；有重复约束时，实际自由度更大", "valid when the constraints are independent; repeated ones add freedom"]])
