"""动画 6.6.1（配图 6.6.1）：潘索的约化。两个不共面的力 f₁、f₂ 先平移到原点 O，得到合力 f 和对 O 的力矩 m_O；
再把参考点移到中心轴上，力矩中垂直于 f 的部分消失，只剩与 f 平行的力偶矩 m = h f：一个力旋量。"""
from manim import *
from wq_anim import *
import numpy as np

O = np.array([-0.9, -0.55, 0])
SC = 10.0
K = 0.012                                      # 力的箭头：每牛顿 0.012 m
P1, F1 = np.array([0.2, 0, 0]), np.array([0, 0, -10.0])
P2, F2 = np.array([0, 0, 0.3]), np.array([0, 10.0, 0])
FR = F1 + F2
MO = np.cross(P1, F1) + np.cross(P2, F2)
H = MO @ FR / (FR @ FR)
Q = np.cross(FR, MO) / (FR @ FR)
MC = H * FR                                    # 中心轴上的力矩
KM = 0.05                                      # 力矩的箭头：每牛·米 0.05 m


def P(x):
    return proj3(x, O, SC)


def arrow(a, b, color, w=6):
    return Arrow(P(a), P(b), buff=0, color=color, stroke_width=w, max_tip_length_to_length_ratio=0.2)


def lab(tex, x, color, d=UR):
    return MathTex(tex, color=color, font_size=34).next_to(P(x), d, buff=0.08)


class Lesson(Base):
    def construct(self):
        self.title("6.6", "力旋量：力系总可以化为一个螺旋", "Wrenches: any force system reduces to a screw")
        axes = VGroup(*[Arrow(P([0, 0, 0]), P(e), buff=0, color=c, stroke_width=4) for e, c in
                        (([0.12, 0, 0], RED), ([0, 0.12, 0], GREEN), ([0, 0, 0.12], BLUE))], MathTex("O", font_size=30).next_to(P([0, 0, 0]), DL, buff=0.05))
        self.add(axes)
        a1, a2 = arrow(P1, P1 + K * F1, GREY_B), arrow(P2, P2 + K * F2, GREY_B)
        l1, l2 = lab("f_1", P1 + K * F1, GREY_B, DR), lab("f_2", P2 + K * F2, GREY_B, UR)
        self.play(GrowArrow(a1), GrowArrow(a2), FadeIn(l1), FadeIn(l2))
        self.caption("两个力不在同一平面内，不能合成为一个力", "Two forces not in one plane cannot be combined into a single force")
        fo = arrow([0, 0, 0], K * FR, ORANGE, 7)
        mo = arrow([0, 0, 0], KM * MO, BLUE_C, 7)
        self.play(TransformFromCopy(VGroup(a1, a2), fo), run_time=1.5)
        lmo, lf = lab("m_O", KM * MO, BLUE_C, UP), lab("f", K * FR, ORANGE, RIGHT)
        self.play(GrowArrow(mo), FadeIn(lmo), FadeIn(lf))
        self.caption("移到原点：合力 f，加上对原点的力矩 m_O；两者一般不平行", "At the origin: resultant f plus moment m_O, generally not parallel")
        axis = DashedLine(P(Q - 0.25 * FR / np.linalg.norm(FR)), P(Q + 0.3 * FR / np.linalg.norm(FR)), color=YELLOW, stroke_width=4)
        self.play(Create(axis))
        self.caption("中心轴：q = f × m_O / |f|²。把参考点移到轴上……", "Central axis: q = f × m_O / |f|². Move the reference point onto it…")
        u = FR / np.linalg.norm(FR)
        fq = arrow(Q, Q + K * FR, ORANGE, 7)
        mq = arrow(Q - 0.2 * u, Q - 0.2 * u + KM * MC * 2.5, BLUE_C, 9)
        self.play(ReplacementTransform(fo, fq), ReplacementTransform(mo, mq), FadeOut(lmo), FadeOut(lf), run_time=2)
        self.play(FadeIn(lab("f", Q + K * FR, ORANGE, RIGHT)), FadeIn(lab("m = h f", Q - 0.2 * u, BLUE_C, LEFT)))
        self.caption("力矩只剩与 f 平行的部分 m = h f：力旋量，节距 h = 0.1 m", "Only the part along f is left, m = h f: a wrench of pitch h = 0.1 m")
        self.wait(2.5)
        self.card([["潘索定理", "Poinsot's theorem"],
                   ["任何力系都等价于沿某一根轴的力，加上绕这根轴的力偶", "Any force system is a force along some axis plus a couple about that axis"],
                   MathTex(r"\mathcal F = (m,\ f) = (q\times f + h f,\ f),\qquad h = \frac{m\cdot f}{|f|^2}", font_size=44)])
