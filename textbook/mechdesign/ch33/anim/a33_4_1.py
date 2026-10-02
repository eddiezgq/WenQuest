"""动画 33.4.1（配图 33.4.1）：齿轮的空间力分解到两个平面，各画一个弯矩图，再按矢量合成。"""
from manim import *
from wq_anim import *
import numpy as np

L = 8.0                       # 屏幕上两轴承的距离
A = -4.0
a = 54 / 115 * L              # 齿轮到左轴承


def tri(y0, h, color):
    pts = [[A, y0, 0], [A + a, y0 + h, 0], [A + L, y0, 0]]
    poly = Polygon(*pts, color=color, fill_color=color, fill_opacity=0.3, stroke_width=3)
    return poly


class Lesson(Base):
    def construct(self):
        self.title("33.4", "两个平面的弯矩，合成一个", "Two bending planes, one resultant")
        shaft = Line([A - 0.4, 1.6, 0], [A + L + 0.4, 1.6, 0], color=GREY_B, stroke_width=10)
        sup = VGroup(*[Triangle(color=WHITE).scale(0.18).move_to([x, 1.3, 0]) for x in (A, A + L)])
        self.play(Create(shaft), FadeIn(sup))
        Fr = vec([A + a, 2.9, 0], [A + a, 1.75, 0], C_F, r"F_\mathrm r", RIGHT)
        Ft = vec([A + a - 1.2, 2.4, 0], [A + a - 0.05, 1.7, 0], ORANGE, r"F_\mathrm t", LEFT)
        self.play(GrowArrow(Fr[0]), Write(Fr[1]), GrowArrow(Ft[0]), Write(Ft[1]))
        self.caption("齿轮对轴的力：径向力 Fr（铅垂面）和圆周力 Ft（水平面）", "Gear forces on the shaft: radial Fr (vertical plane), tangential Ft (horizontal plane)")
        # 两个平面的弯矩
        hV, hH = 0.62, 1.7
        mv = tri(-0.6, hV, BLUE)
        mh = tri(-2.8, hH, GREEN)
        lv = MathTex(r"M_V = 34.8\ \mathrm{N\cdot m}", color=BLUE, font_size=30).next_to(mv, RIGHT, buff=0.2)
        lh = MathTex(r"M_H = 95.5\ \mathrm{N\cdot m}", color=GREEN, font_size=30).next_to(mh, RIGHT, buff=0.2)
        self.play(TransformFromCopy(Fr[0], mv), Write(lv), run_time=1.5)
        self.play(TransformFromCopy(Ft[0], mh), Write(lh), run_time=1.5)
        self.caption("两个平面各是一根简支梁：弯矩图都是三角形，峰值在齿轮处", "Each plane is a simply supported beam: triangular diagrams peaking at the gear")
        self.play(FadeOut(VGroup(Fr, Ft, shaft, sup)))
        # 齿轮截面上把两个弯矩当矢量合成
        o = np.array([3.6, 1.3, 0])
        v1 = Arrow(o, o + RIGHT * hH, buff=0, color=GREEN, stroke_width=6)
        v2 = Arrow(o + RIGHT * hH, o + RIGHT * hH + UP * hV, buff=0, color=BLUE, stroke_width=6)
        vr = Arrow(o, o + RIGHT * hH + UP * hV, buff=0, color=RED, stroke_width=7)
        self.play(GrowArrow(v1), GrowArrow(v2))
        self.play(GrowArrow(vr))
        lr = MathTex(r"M=\sqrt{M_H^2+M_V^2}=101.6\ \mathrm{N\cdot m}", color=RED, font_size=32).next_to(vr, UP, buff=0.3).shift(LEFT * 1.2)
        self.play(Write(lr))
        self.caption("同一截面上，两个弯矩是互相垂直的矢量：按勾股定理合成", "At one section the two moments are perpendicular vectors: add them by Pythagoras")
        self.wait(1)
        self.card([["弯扭合成的第一步", "First step of combined loading"],
                   MathTex(r"M=\sqrt{M_H^2+M_V^2},\qquad \sigma=\frac{M}{W},\qquad \tau=\frac{T}{W_\mathrm T}", font_size=40),
                   ["各平面分别求支反力和弯矩，在每个截面上合成", "Solve each plane on its own, then combine section by section"]])
