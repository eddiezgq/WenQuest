"""动画 30.2.1（配图 30.2.1）：构型选择。
(1) 俯视看偏置腕：手臂平面和 TCP 之间横着隔了 d4 = 0.12 m。工具竖直朝下时，TCP 离 J1 轴不能近于 d4——
    TCP 往轴心靠，手臂平面就得绕到轴的另一边，转不过去；J1 轴周围留下一根半径 0.12 m 的“够不着的圆柱”。球形腕没有这个问题。
(2) 评分：六条标准各有权重，四种构型逐条加分；偏置腕六轴总分最高，主要赢在“与人同场”和“模组化”。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("30.2", "构型选择", "Choosing the configuration")
        sc = 6.0
        o = np.array([-4.5, -0.8, 0])
        self.add(Dot(o, color=YELLOW, radius=0.1), zh("J1 轴", 20, YELLOW).next_to(o, DOWN, buff=0.1))
        hole = Circle(radius=0.12 * sc, color=RED, stroke_width=2).move_to(o)
        d4 = 0.12
        r = ValueTracker(0.60)

        def arm():
            rr = r.get_value()
            rp = np.sqrt(max(rr * rr - d4 * d4, 0.0))
            ang = np.arctan2(-d4, rp)                     # 手臂平面朝 +x 方向偏一点，TCP 正好在 x 轴上
            u = np.array([np.cos(-ang), np.sin(-ang), 0])
            n = np.array([-u[1], u[0], 0])
            p_end = o + sc * rp * u
            tcp = p_end - sc * d4 * n
            g = VGroup(Line(o, p_end, color=STEEL, stroke_width=9), Line(p_end, tcp, color=GREY_B, stroke_width=6),
                       Dot(tcp, color=ORANGE, radius=0.11))
            return g
        a = always_redraw(arm)
        self.add(a)
        lab = zh("俯视：手臂平面与 TCP 横向隔着 d4 = 0.12 m", 24, INK).move_to([2.6, 2.0, 0])
        self.play(FadeIn(lab), run_time=0.6)
        self.play(r.animate.set_value(0.125), run_time=3.0, rate_func=smooth)
        self.play(Create(hole), FadeIn(zh("半径 d4 的圆柱：工具朝下时够不着", 24, RED).move_to([2.6, 1.3, 0])), run_time=0.8)
        self.caption("偏置腕把三个一样的模组直角地串起来，代价是 J1 轴周围有一根半径 d4 的圆柱够不着",
                     "The offset wrist strings three identical modules at right angles; the price is a cylinder of radius d4 around J1", wait=1.8)
        self.clear_stage()
        # (2) 评分
        crit = [("与人同场", 0.25), ("模组化", 0.20), ("工作空间", 0.20), ("逆解与编程", 0.15), ("成本", 0.10), ("刚度与精度", 0.10)]
        names = ["偏置腕六轴", "球形腕六轴", "七轴", "SCARA"]
        S = [[5, 5, 4, 4, 4, 3], [3, 2, 5, 5, 4, 4], [5, 4, 4, 2, 2, 3], [2, 3, 1, 5, 5, 5]]
        cols = [BLUE, GREEN, RED, PURPLE, "#8c564b", GOLD]
        x0, k = -3.2, 1.6
        rows = VGroup(*[zh(n, 24, INK).move_to([x0 - 1.4, 1.4 - 1.0 * i, 0]) for i, n in enumerate(names)])
        self.play(FadeIn(rows), run_time=0.5)
        leg = VGroup(*[VGroup(Square(0.2, color=c, fill_opacity=0.9), zh(f"{n} {w:.2f}", 18, INK)).arrange(RIGHT, buff=0.1)
                       for (n, w), c in zip(crit, cols)]).arrange(RIGHT, buff=0.3).move_to([0.5, -2.4, 0])
        fit(leg, 12)
        self.play(FadeIn(leg), run_time=0.5)
        left = [0.0] * 4
        for j, ((n, w), c) in enumerate(zip(crit, cols)):
            bars = []
            for i in range(4):
                L = w * S[i][j] * k
                b = Rectangle(width=L, height=0.6, color=c, fill_opacity=0.85, stroke_width=0).move_to([x0 + left[i] + L / 2, 1.4 - 1.0 * i, 0])
                left[i] += L
                bars.append(b)
            self.play(*[GrowFromEdge(b, LEFT) for b in bars], run_time=0.5)
        tot = VGroup(*[zh(f"{left[i] / k:.2f}", 24, YELLOW if i == 0 else INK).move_to([x0 + left[i] + 0.5, 1.4 - 1.0 * i, 0]) for i in range(4)])
        self.play(FadeIn(tot), run_time=0.6)
        self.caption("权重和打分是设计者的判断；写成表，判断才能拿出来讨论",
                     "Weights and scores are the designer's judgement; written as a table, the judgement can be argued", wait=2.0)
        self.card([["构型选择", "Choosing a configuration"],
                   ["偏置腕六轴：模组化、外形光滑、闭式逆解", "6-axis offset wrist: modular, smooth, closed-form inverse kinematics"],
                   ["代价：工具朝下时 J1 轴周围半径 d4 够不着", "Price: with the tool down, radius d4 around J1 is unreachable"],
                   ["SCARA 竖直行程太短，七轴贵且逆解多一维", "SCARA lacks vertical stroke; 7 axes cost more and add a redundant dimension"]])
