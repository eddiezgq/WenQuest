"""动画 14.5.1（配图 14.5.1）：拉伸试验。左：试样被拉长（伸长量放大画出）；右：应力—应变曲线随之画出。
先拉 Q235 钢，再拉 6061-T6 铝。曲线与程序 14.5.1 相同（E、屈服强度、抗拉强度取数字工厂材料库：
Q235 E = 206 GPa、σs = 235 MPa、σb = 440 MPa；6061-T6 E = 68.9 GPa、Rp0.2 = 276 MPa、Rm = 310 MPa）。"""
from manim import *
from wq_anim import *
import numpy as np


def q235(e):
    E, sy, su = 206000.0, 235.0, 440.0
    e_y, e_l, e_u, e_f = 1.04 * sy / E, 0.018, 0.20, 0.30
    if e <= e_y: return E * e
    if e <= e_y + 0.001: return 1.04 * sy - 0.04 * sy * (e - e_y) / 0.001
    if e <= e_l: return sy
    if e <= e_u: u = (e - e_l) / (e_u - e_l); return sy + (su - sy) * (1 - (1 - u) ** 2)
    return su - 0.20 * su * ((e - e_u) / (e_f - e_u)) ** 2


E_A, SY_A, SU_A = 68900.0, 276.0, 310.0
N_A = np.log((0.080 - SU_A / E_A) / 0.002) / np.log(SU_A / SY_A)
_s = np.linspace(0, SU_A, 4001); _e = _s / E_A + 0.002 * (_s / SY_A) ** N_A


def al(e):
    if e <= 0.080: return float(np.interp(e, _e, _s))
    return SU_A - 0.15 * SU_A * ((e - 0.080) / 0.04) ** 2


AX = dict(x_range=[0, 32, 5], y_range=[0, 500, 100], x_length=6.0, y_length=3.6, tips=False,
          axis_config=dict(include_numbers=True, font_size=22, color=GREY_B))


class Lesson(Base):
    def construct(self):
        self.title("14.5", "拉伸试验", "The tensile test")
        ax = Axes(**AX).move_to(np.array([2.6, 0.35, 0]))
        xl = MathTex(r"\varepsilon\ /\ \%", font_size=28).next_to(ax.x_axis, DOWN, buff=0.35)
        yl = MathTex(r"\sigma\ /\ \mathrm{MPa}", font_size=28).next_to(ax.y_axis, UP, buff=0.15)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        for curve, ef, col, name, cap in ((q235, 0.30, RED, ["Q235 钢", "Q235 steel"],
                                           ("钢：先是直线（弹性），然后应力不升而应变大增（屈服平台），再硬化，最后颈缩拉断", "Steel: a straight line (elastic), a plateau (yielding), hardening, then necking and fracture")),
                                          (al, 0.12, BLUE, ["6061-T6 铝", "6061-T6 aluminium"],
                                           ("铝：没有屈服平台，伸长也小得多；开头的直线要放大才看得出，斜率只有钢的三分之一", "Aluminium: no plateau and far less elongation; zoom in and its straight start has a third of the steel's slope"))):
            e = ValueTracker(0.0)
            path = always_redraw(lambda c=curve, e=e, col=col: ax.plot(lambda x: c(x / 100), x_range=[0, max(e.get_value() * 100, 1e-3), 0.01], color=col, stroke_width=4))

            def spec(e=e, ef=ef, col=col):
                ev = e.get_value(); L0 = 2.4; Lx = L0 * (1 + ev * 2.5)              # 伸长量放大画出
                eu = 0.20 if ef > 0.2 else 0.080                                  # 抗拉强度处开始颈缩
                neck = 1.0 if ev < eu else 1 - 0.55 * (ev - eu) / (ef - eu)
                top = np.array([-4.6, 1.2, 0]); bot = top + DOWN * Lx
                body = VGroup(Rectangle(width=0.5, height=Lx / 2, color=col, fill_opacity=0.4).move_to(top + DOWN * Lx / 4),
                              Rectangle(width=0.5, height=Lx / 2, color=col, fill_opacity=0.4).move_to(bot + UP * Lx / 4),
                              Rectangle(width=0.5 * neck, height=0.15, color=col, fill_opacity=0.6).move_to((top + bot) / 2))
                grips = VGroup(Rectangle(width=1.1, height=0.35, color=GREY_B, fill_opacity=0.6).move_to(top + UP * 0.17),
                               Rectangle(width=1.1, height=0.35, color=GREY_B, fill_opacity=0.6).move_to(bot + DOWN * 0.17))
                return VGroup(body, grips)

            sp = always_redraw(spec)
            nm = bi(name, size=22, color=col).move_to(np.array([-4.6, 2.2, 0]))
            self.add(path, sp); self.play(FadeIn(nm), run_time=0.5)
            self.caption(*cap, wait=0)
            self.play(e.animate.set_value(0.02), run_time=2.5, rate_func=linear)
            self.play(e.animate.set_value(ef), run_time=4.0, rate_func=linear)
            self.wait(1.0)
            done = ax.plot(lambda x, c=curve: c(x / 100), x_range=[0, ef * 100, 0.01], color=col, stroke_width=4)
            self.add(done); self.play(FadeOut(sp), FadeOut(nm), FadeOut(path), run_time=0.5)
        self.card([["应力—应变曲线", "The stress–strain curve"],
                   MathTex(r"\sigma = E\varepsilon\quad(\text{elastic})", font_size=44),
                   ["直线段的斜率是弹性模量 E；屈服后卸载就回不到原长", "the slope of the straight part is E; past yield the bar no longer springs back"],
                   ["钢有屈服平台，铝用 0.2% 偏移法定屈服强度", "steel has a yield plateau; for aluminium use the 0.2% offset"]])
