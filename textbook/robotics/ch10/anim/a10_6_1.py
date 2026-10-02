"""动画 10.6.1（配图 10.6.3）：转台以 Ω = 0.5 rad/s 逆时针转动，小球从中心以 0.6 m/s 沿地面上的固定方向滚出（无摩擦）。
左：地面上看，直线匀速；右：转台上看，轨迹向右弯曲。右画面同时画出相对速度 v_rel 和 −2Ω × v_rel（科氏偏转的方向）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

OM, V0, RT = 0.5, 0.6, 1.5
S = 1.25
LC = np.array([-3.5, -0.2, 0])
RC = np.array([3.5, -0.2, 0])


def rot(a, p):
    c, s = math.cos(a), math.sin(a)
    return np.array([c * p[0] - s * p[1], s * p[0] + c * p[1], 0.0])


def table(center, ang):
    g = VGroup(Circle(radius=S * RT, color=GREY_B, fill_color="#26313b", fill_opacity=1, stroke_width=2).move_to(center))
    for k in range(4):
        e = rot(ang + k * PI / 2, np.array([1.0, 0, 0]))
        g.add(DashedLine(center, center + S * RT * e, color=GREY_B, stroke_width=2))
    g.add(Dot(center + S * RT * 0.85 * rot(ang + 0.4, np.array([1.0, 0, 0])), radius=0.07, color=YELLOW))
    return g


class Lesson(Base):
    def construct(self):
        self.title("10.6", "转台上的科氏偏转", "Coriolis deflection on a turntable")
        lt = zh("地面上看", 24, INK).move_to(LC + UP * 2.3)
        rt = zh("转台上看", 24, INK).move_to(RC + UP * 2.3)
        self.play(FadeIn(lt), FadeIn(rt))
        t = ValueTracker(0.0)
        left_tab = always_redraw(lambda: table(LC, OM * t.get_value()))
        right_tab = table(RC, 0.0)
        om = VGroup(Arc(radius=S * RT + 0.25, start_angle=-0.9, angle=0.9, arc_center=LC, color=WHITE, stroke_width=3).add_tip(tip_length=0.18),
                    MathTex(r"\Omega", font_size=32).move_to(LC + (S * RT + 0.55) * np.array([math.cos(-0.45), math.sin(-0.45), 0])))
        self.add(left_tab)
        self.play(FadeIn(right_tab), FadeIn(om))
        ballL = always_redraw(lambda: Dot(LC + S * np.array([V0 * t.get_value(), 0, 0]), radius=0.11, color=ORANGE))
        ballR = always_redraw(lambda: Dot(RC + S * rot(-OM * t.get_value(), np.array([V0 * t.get_value(), 0, 0])), radius=0.11, color=ORANGE))
        trL = TracedPath(ballL.get_center, stroke_color=ORANGE, stroke_width=4)
        trR = TracedPath(ballR.get_center, stroke_color=ORANGE, stroke_width=4)

        def arrows():
            tt = t.get_value()
            p = rot(-OM * tt, np.array([V0 * tt, 0, 0]))
            vrel = rot(-OM * tt, np.array([V0, 0, 0])) + np.cross([0, 0, -OM], p)       # 相对速度：对 p(t) 求导
            cor = -2 * np.cross([0, 0, OM], vrel)
            P = RC + S * p
            return VGroup(Arrow(P, P + 1.1 * vrel, buff=0, color=C_V, stroke_width=5, max_tip_length_to_length_ratio=0.25),
                          MathTex(r"\boldsymbol v_{\mathrm{rel}}", font_size=26, color=C_V).move_to(P + 1.1 * vrel + 0.3 * vrel / np.linalg.norm(vrel)),
                          Arrow(P, P + 1.1 * cor, buff=0, color=C_A, stroke_width=5, max_tip_length_to_length_ratio=0.25),
                          MathTex(r"-2\boldsymbol\Omega\times\boldsymbol v_{\mathrm{rel}}", font_size=24, color=C_A).move_to(P + 1.1 * cor + 0.45 * cor / np.linalg.norm(cor)))

        arr = always_redraw(arrows)
        self.add(trL, trR, ballL, ballR, arr)
        self.caption("小球不受水平力：在地面上看，它沿直线匀速滚动", "No horizontal force: seen from the ground the ball rolls straight at constant speed", wait=0)
        self.play(t.animate.set_value(1.2), run_time=6, rate_func=linear)
        self.caption("在转台上看，它的轨迹不断向右弯：这就是科氏偏转", "Seen on the table its path keeps bending right: the Coriolis deflection", wait=0)
        self.play(t.animate.set_value(2.5), run_time=7, rate_func=linear)
        self.wait(1)
        self.card([["加速度合成定理", "Composition of accelerations"],
                   MathTex(r"\boldsymbol a_{\mathrm{abs}} = \boldsymbol a_{\mathrm{tr}} + \boldsymbol a_{\mathrm{rel}} + 2\,\boldsymbol\Omega\times\boldsymbol v_{\mathrm{rel}}", font_size=46),
                   ["小球 a_abs = 0，所以在转台上 a_rel = −a_tr − 2Ω × v_rel：向外，并向右偏", "The ball has a_abs = 0, so on the table a_rel = −a_tr − 2Ω × v_rel: outward and to the right"]])
