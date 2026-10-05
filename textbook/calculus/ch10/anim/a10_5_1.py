"""动画 10.5.1（配图 10.5.1）：曲率圆——AGV 沿五次多项式换道路径行驶，每一点都有一个与路径贴合得最好的圆，
半径是曲率半径；直线段上圆无限大，弯得最急处圆最小。最后看三次多项式路径：入口处圆的半径从无穷大突然变小。"""
from manim import *
from wq_anim import *
import numpy as np

D, L = 1.0, 4.0


def lane(kind):
    if kind == "q":
        return (lambda x: D * (10 * (x / L) ** 3 - 15 * (x / L) ** 4 + 6 * (x / L) ** 5),
                lambda x: D / L * (30 * (x / L) ** 2 - 60 * (x / L) ** 3 + 30 * (x / L) ** 4),
                lambda x: D / L ** 2 * (60 * (x / L) - 180 * (x / L) ** 2 + 120 * (x / L) ** 3))
    return (lambda x: D * (3 * (x / L) ** 2 - 2 * (x / L) ** 3),
            lambda x: D / L * (6 * (x / L) - 6 * (x / L) ** 2),
            lambda x: D / L ** 2 * (6 - 12 * (x / L)))


class Lesson(Base):
    def construct(self):
        self.title("10.5", "曲率与曲率圆", "Curvature and the circle of curvature")
        ax = Axes(x_range=[-1, 5, 1], y_range=[-1.5, 2.5, 1], x_length=9, y_length=6, tips=False,
                  axis_config={"color": GREY_B}).shift(DOWN * 0.5)
        for kind, cap_cn, cap_en in (("q", "五次多项式路径：曲率圆从无穷大变小又变大，过中点（拐点）后换到另一侧", "Quintic path: the circle shrinks and grows, then switches sides after the inflection point"),
                                     ("c", "三次多项式路径：一进入弯道，曲率圆就突然变小（曲率跳变）", "Cubic path: on entry the circle suddenly becomes small (curvature jump)")):
            y, yp, ypp = lane(kind)
            path = VGroup(Line(ax.c2p(-1, 0), ax.c2p(0, 0)), ax.plot(y, x_range=[0, L], color=WHITE), Line(ax.c2p(L, D), ax.c2p(5, D)))
            path.set_color(WHITE).set_stroke(width=3)
            self.play(Create(ax), Create(path)) if kind == "q" else self.play(Create(path))
            x = ValueTracker(0.001 if kind == "q" else 0.0)

            def kap(v):
                if v <= 0 or v >= L:
                    return 0.0
                return ypp(v) / (1 + yp(v) ** 2) ** 1.5

            def circ():
                v = x.get_value()
                k = kap(v)
                if abs(k) < 0.08:
                    return VGroup()
                R = 1 / k
                nx, ny = -yp(v), 1.0
                n = np.hypot(nx, ny)
                cx, cy = v + R * nx / n, y(v) + R * ny / n
                unit = ax.x_length / 6
                return Circle(radius=abs(R) * unit, color=ORANGE, stroke_width=2).move_to(ax.c2p(cx, cy))
            c = always_redraw(circ)
            dot = always_redraw(lambda: Dot(ax.c2p(x.get_value(), y(x.get_value())), color=YELLOW, radius=0.09))
            lab = always_redraw(lambda: MathTex(r"\kappa=%.3f\ \mathrm{m^{-1}}" % abs(kap(x.get_value())), font_size=36, color=ORANGE)
                                .to_corner(UR).shift(DOWN * 1.0 + LEFT * 0.4))
            self.add(c, dot, lab)
            self.caption(cap_cn, cap_en, wait=0.2)
            self.play(x.animate.set_value(L - 0.001), run_time=7, rate_func=linear)
            for m in (c, dot, lab):
                m.clear_updaters()
            self.play(FadeOut(c), FadeOut(dot), FadeOut(lab), FadeOut(path))
        self.play(FadeOut(ax))
        self.card([["曲率", "Curvature"],
                   MathTex(r"\kappa=\frac{|y''|}{(1+y'^2)^{3/2}},\qquad v\le\sqrt{a_{\max}/\kappa}", font_size=44),
                   ["曲率圆的半径 = 1/κ；过弯车速受侧向加速度限制", "Radius of curvature = 1/κ; cornering speed limited by lateral acceleration"]])
