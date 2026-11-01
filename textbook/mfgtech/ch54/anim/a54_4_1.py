"""动画 54.4.1（配图 54.4.2）：两顶尖车外圆，刀具从尾座走到头架，各位置的让刀量逐点画出——头架、尾座、工件弯曲三部分，合计的曲线
就是车出的形状（直径误差 = 2 × 让刀量）。数值：SH-301 精车（Ø40 × 167，背向力 52 N，头架、尾座刚度 20000 N/mm、刀架 50000 N/mm），
与细长轴（Ø20 × 500，背向力 111 N）对比；公式与 hub/accuracy.py 的 compliance_between_centers 相同。"""
from manim import *
from wq_anim import *
import numpy as np

KH, KT, KK, E_ST = 20000.0, 20000.0, 50000.0, 210000.0


def compliance(x, L, d, kh, kt, kk):
    """与 hub/accuracy.py 的 compliance_between_centers 相同（动画在动画服务里渲染，不依赖仓库代码）"""
    I = np.pi * d ** 4 / 64
    c = {"head": ((L - x) / L) ** 2 / kh, "tail": (x / L) ** 2 / kt, "tool": 1 / kk, "work": x * x * (L - x) ** 2 / (3 * E_ST * I * L)}
    c["total"] = sum(c.values())
    return c


class Lesson(Base):
    def construct(self):
        self.title("54.4", "两顶尖车削的让刀曲线", "Deflection between centres")
        for LL, d, Fp, ymax, cap in ((167.0, 40.0, 52.1, 4.0, ("SH-301 精车：工件刚，头尾架软", "SH-301 finishing: stiff work, soft centres")),
                                     (500.0, 20.0, 111.3, 200.0, ("细长轴 Ø20 × 500：工件软", "Slender shaft Ø20 × 500: soft work"))):
            ax = Axes(x_range=[0, LL, LL / 4], y_range=[0, ymax, ymax / 4], x_length=9, y_length=3.2, tips=False,
                      axis_config={"color": MUTED, "include_numbers": True, "font_size": 20}).shift(UP * 0.1)
            xl = zh("刀具位置 x / mm（左：头架，右：尾座）", 20, MUTED).next_to(ax, DOWN, buff=0.25)
            yl = zh("让刀量 / µm", 20, MUTED).next_to(ax, LEFT, buff=0.1).rotate(PI / 2)
            self.play(Create(ax), FadeIn(xl), FadeIn(yl))
            self.caption(cap[0], cap[1], wait=0.8)
            t = ValueTracker(LL)

            def curve(key, col):
                def f():
                    x1 = t.get_value()
                    xs = np.linspace(x1, LL, 60)
                    pts = [ax.c2p(x, Fp * compliance(x, LL, d, KH, KT, KK)[key] * 1000) for x in xs]
                    return VMobject(color=col, stroke_width=6 if key == "total" else 3).set_points_as_corners(pts)
                return always_redraw(f)

            cs = [curve("head", BLUE), curve("tail", ORANGE), curve("work", GREEN), curve("total", RED)]
            tool = always_redraw(lambda: Triangle(color=ORANGE, fill_opacity=1).scale(0.15).move_to(ax.c2p(t.get_value(), 0) + DOWN * 0.2))
            self.add(*cs, tool)
            self.play(t.animate.set_value(0.001), run_time=5, rate_func=linear)
            lg = VGroup(zh("头架", 20, BLUE), zh("尾座", 20, ORANGE), zh("工件弯曲", 20, GREEN), zh("合计 = 车出的形状", 20, RED)).arrange(RIGHT, buff=0.4).to_edge(UP).shift(DOWN * 0.9)
            self.play(FadeIn(lg))
            self.caption("合计的曲线就是工件的形状：两头大是鞍形，中间大是鼓形" if LL < 300 else "工件弯曲占了绝大部分：中间大，鼓形",
                         "The total curve is the shape of the work" if LL < 300 else "Bending dominates: barrel-shaped")
            self.play(*[FadeOut(m) for m in (ax, xl, yl, lg, tool, *cs)])
        self.card([["让刀量随刀具位置变化，车出的工件就有形状误差", "Deflection that varies along the cut becomes a form error"],
                   ["工件刚：鞍形（两头大）；工件细长：鼓形（中间大）；头尾架刚度不等：锥形", "Stiff work: saddle; slender work: barrel; unequal centres: taper"]])
