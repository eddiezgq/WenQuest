"""动画 15.5.1（配图 15.5.3）：平面 2R 臂（0.425、0.392 m）从 (0°, 60°) 出发，到达 (−0.45, 0.35) m（算例 15.5.2）。
先直接用牛顿法：各次迭代的手臂形态大幅跳动，最后落到 θ₂ < 0 的一支；再用延拓法：目标从起点的末端沿直线分 10 段移到终点，
每段用牛顿法从上一段的解出发，手臂连续地跟过去，留在 θ₂ > 0 的一支。"""
from manim import *
from wq_anim import *
import numpy as np
import math

L1, L2 = 0.425, 0.392
PD = np.array([-0.45, 0.35])
TH0 = np.radians([0.0, 60.0])
SC = 4.6
O = np.array([0.0, -1.6, 0.0])


def S(x, y):
    return O + SC * np.array([x, y, 0.0])


def fk(th):
    e = np.array([L1 * math.cos(th[0]), L1 * math.sin(th[0])])
    return e, e + L2 * np.array([math.cos(th[0] + th[1]), math.sin(th[0] + th[1])])


def jac(th):
    s1, c1 = math.sin(th[0]), math.cos(th[0])
    s12, c12 = math.sin(th[0] + th[1]), math.cos(th[0] + th[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


def newton(pd, th, tol=1e-12, iters=60):
    th = np.array(th, float)
    seq = [th.copy()]
    for _ in range(iters):
        e = pd - fk(th)[1]
        if np.linalg.norm(e) < tol:
            break
        th = th + np.linalg.solve(jac(th), e)
        seq.append(th.copy())
    return seq


def arm(th, color, width=1.0, opacity=1.0):
    e, p = fk(th)
    E, P = S(*e), S(*p)
    g = VGroup(Line(O, E, color=color, stroke_width=12 * width), Line(E, P, color=color, stroke_width=9 * width),
               Dot(O, radius=0.09, color=WHITE), Dot(E, radius=0.08, color=WHITE), Dot(P, radius=0.06, color=color))
    return g.set_opacity(opacity)


class Lesson(Base):
    def construct(self):
        self.title("15.5", "初值决定落到哪一支：延拓法", "The start decides the branch: continuation")
        R = L1 + L2
        reach = DashedVMobject(Circle(radius=SC * R, arc_center=O, color=GREY_B, stroke_width=2), num_dashes=60).set_stroke(opacity=0.6)
        base = Polygon(O + LEFT * 0.3 + DOWN * 0.22, O + RIGHT * 0.3 + DOWN * 0.22, O + RIGHT * 0.15, O + LEFT * 0.15,
                       color=GREY_B, fill_color=GREY_E, fill_opacity=1)
        tgt = Dot(S(*PD), radius=0.1, color=RED)
        tl = zh("目标", 22, RED).next_to(tgt, UL, buff=0.1)
        start = arm(TH0, GREY_B, 0.8)
        sl = zh("起点 θ = (0°, 60°)", 22, GREY_B).next_to(S(*fk(TH0)[1]), RIGHT, buff=0.15)
        self.play(Create(reach), FadeIn(base), FadeIn(start), FadeIn(sl), FadeIn(tgt), FadeIn(tl), run_time=1.2)
        self.caption("起点在右边，目标在左上方。直接用牛顿法会怎样？",
                     "The start is on the right, the goal up-left. What does Newton's method do directly?", wait=0.5)

        seq = newton(PD, TH0)
        ghosts = VGroup()
        cur = arm(seq[0], ORANGE)
        self.play(FadeIn(cur), run_time=0.3)
        for k, th in enumerate(seq[1:], 1):
            nxt = arm(th, ORANGE)
            g = cur.copy().set_opacity(0.18)
            ghosts.add(g)
            self.add(g)
            self.play(Transform(cur, nxt), run_time=0.45 if k < 6 else 0.2)
        t2 = math.degrees(math.atan2(math.sin(seq[-1][1]), math.cos(seq[-1][1])))
        self.caption(f"{len(seq) - 1} 次迭代：前几步大幅跳动，最后落到 θ₂ = {t2:.1f}° 的一支",
                     f"{len(seq) - 1} iterations: wild jumps at first, ending on the branch θ₂ = {t2:.1f}°", wait=1.8)
        self.play(FadeOut(ghosts), FadeOut(cur), run_time=0.6)

        p0 = fk(TH0)[1]
        path = DashedLine(S(*p0), S(*PD), color=YELLOW, stroke_width=3)
        self.caption("延拓法：把目标从起点的末端沿直线一段一段移过去，每段用上一段的解作初值",
                     "Continuation: move the goal from the start tip in short stages, each starting from the last solution", wait=0.3)
        self.play(Create(path), run_time=0.8)
        s = ValueTracker(0.0)
        state = {"th": TH0.copy()}

        def follow():
            pj = p0 + (PD - p0) * s.get_value()
            state["th"] = newton(pj, state["th"], tol=1e-10)[-1]
            return VGroup(arm(state["th"], STEEL), Dot(S(*pj), radius=0.07, color=YELLOW))

        mover = always_redraw(follow)
        self.add(mover)
        self.play(s.animate.set_value(1.0), run_time=5.0, rate_func=linear)
        t2c = math.degrees(state["th"][1])
        self.caption(f"手臂连续地跟过去，始终留在 θ₂ > 0 的一支，终点 θ₂ = {t2c:.1f}°",
                     f"The arm follows continuously and stays on the branch θ₂ > 0, ending at θ₂ = {t2c:.1f}°", wait=2.0)
        self.card([["延拓法", "Continuation"],
                   MathTex(r"T_d(s) = T_0\,e^{s[\mathcal V_0]},\qquad s = 0,\ \tfrac1N,\ \ldots,\ 1", font_size=40),
                   ["每一段的初值都离解很近；路径上不碰奇异，就留在出发时的那一支",
                    "Each stage starts close to its solution; without singularities on the way it stays on the starting branch"]])
