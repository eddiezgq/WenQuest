"""动画 10.4.1（配图 10.4.1；势能形状同图 10.3.2）：小球在势能曲线上运动，动能、势能此消彼长。势能取双阱形 U(x) = U0[(x/x0)² − 1]²
（与算例 10.3.2 同形，取 x0 = 1、U0 = 1 的无量纲单位）。第一次机械能 E = 2.43 U0，高于中间的峰，小球在两个阱之间来回；
第二次 E ≈ 0.68 U0，低于峰，小球只能在一个阱里来回，转折点处动能为零。右边的柱：势能 + 动能 = 机械能，始终不变。"""
from manim import *
from wq_anim import *
import numpy as np

U = lambda x: (x * x - 1) ** 2
dU = lambda x: 4 * x * (x * x - 1)
SX, SY, OX, OY = 1.55, 1.05, -2.6, -2.0      # 画面坐标 = (OX + SX x, OY + SY U)


def run(x0, T, h=1e-3):
    """m = 1：x'' = −U'(x)，半隐式欧拉法（第 8 章），步长 1 ms。"""
    x, v, out = x0, 0.0, []
    for i in range(int(T / h)):
        v -= dU(x) * h; x += v * h
        if i % 10 == 0:
            out.append((x, v))
    return out


class Lesson(Base):
    def construct(self):
        self.title("10.4", "动能与势能此消彼长", "Kinetic and potential energy trade places")
        curve = FunctionGraph(lambda s: OY + SY * U((s - OX) / SX), x_range=[OX - 1.75 * SX, OX + 1.75 * SX], color=GREY_A, stroke_width=4)
        xl = MathTex("x", font_size=30).move_to(np.array([OX + 1.85 * SX, OY - 0.25, 0]))
        ul = bi(["势能曲线 U(x)", "potential curve U(x)"], size=20).move_to(np.array([OX, OY + 3.6, 0]))
        self.play(Create(curve), FadeIn(xl), FadeIn(ul))
        # 右边的能量柱
        base = np.array([3.6, -2.0, 0]); BW, K_ = 0.7, 1.15
        frame = Rectangle(width=BW + 0.2, height=K_ * 2.6, color=GREY_B, stroke_width=1).move_to(base + np.array([0, K_ * 1.3, 0]))
        lab = VGroup(bi(["动能（上）", "kinetic (top)"], size=18, color=C_F), bi(["势能（下）", "potential (bottom)"], size=18, color=BLUE)).arrange(DOWN, buff=0.25).next_to(frame, RIGHT, buff=0.3)
        self.play(FadeIn(frame), FadeIn(lab))
        run_ = {"path": [(-1.6, 0.0)]}                 # 当前这一段的轨迹（x, v）
        idx = ValueTracker(0)

        def now():
            i = min(int(idx.get_value()), len(run_["path"]) - 1)
            return run_["path"][i]

        def ball():
            x = now()[0]
            return Dot(np.array([OX + SX * x, OY + SY * U(x) + 0.13, 0]), radius=0.13, color=YELLOW)

        def bars():
            x, v = now()
            u, k = U(x), 0.5 * v * v
            bu = Rectangle(width=BW, height=max(1e-3, K_ * u), stroke_width=0, fill_color=BLUE, fill_opacity=0.8).move_to(base + np.array([0, K_ * u / 2, 0]))
            bk = Rectangle(width=BW, height=max(1e-3, K_ * k), stroke_width=0, fill_color=C_F, fill_opacity=0.8).move_to(base + np.array([0, K_ * u + K_ * k / 2, 0]))
            return VGroup(bu, bk)

        self.add(always_redraw(ball), always_redraw(bars))
        for x0, T, cap_z, cap_e in (
                (-1.6, 9.0, "机械能高于中间的峰：小球越过峰顶，在两个阱之间来回", "Energy above the central peak: the ball crosses over and swings between both wells"),
                (-1.35, 7.0, "机械能低于峰：小球被困在一个阱里，转折点处动能为零", "Energy below the peak: the ball is trapped in one well; at the turning points its kinetic energy is zero")):
            run_["path"] = run(x0, T)
            idx.set_value(0)
            E = U(x0)
            eline = DashedLine(np.array([OX - 1.75 * SX, OY + SY * E, 0]), np.array([OX + 1.75 * SX, OY + SY * E, 0]), color=YELLOW, stroke_width=2)
            elab = MathTex("E", font_size=30, color=YELLOW).next_to(eline, RIGHT, buff=0.1)
            etop = DashedLine(base + np.array([-0.55, K_ * E, 0]), base + np.array([0.55, K_ * E, 0]), color=YELLOW, stroke_width=2)
            self.play(Create(eline), FadeIn(elab), Create(etop), run_time=0.6)
            self.caption(cap_z, cap_e, wait=0)
            self.play(idx.animate.set_value(len(run_["path"]) - 1), run_time=T, rate_func=linear)
            self.play(FadeOut(eline), FadeOut(elab), FadeOut(etop), run_time=0.4)
        self.caption("势能低处动能大，势能高处动能小；两者之和——机械能——始终不变", "Low potential means high kinetic energy and vice versa; their sum, the mechanical energy, never changes", wait=2.0)
        self.card([["机械能守恒", "Conservation of mechanical energy"],
                   MathTex(r"E = E_\mathrm{k} + U = \text{const}", font_size=46),
                   ["只有保守力做功时成立", "holds when only conservative forces do work"],
                   ["小球只能在 U(x) ≤ E 的区域里运动", "the ball can only be where U(x) ≤ E"]])
