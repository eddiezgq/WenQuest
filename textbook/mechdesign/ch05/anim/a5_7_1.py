"""动画 5.7.1（配图 5.7.2）：同一根小臂管换成钢、铝合金、碳纤维——同尺寸时比挠度和质量，同刚度时比质量；再加上最小壁厚。
数据与程序 5.7.1 相同：长 392 mm，外径 75 mm，末端 65 N（腕部 2.63 kg + 负载 4 kg），允许挠度 0.10 mm；
E、ρ 取数字工厂材料库（钢、铝）和程序 5.5.1 的碳纤维层合板；最小壁厚为本书设定。挠度在画面上放大。"""
import math

from manim import *
from wq_anim import *

L, D, F, G = 0.392, 0.075, 65.0, 9.81
DELTA = 0.10e-3
MATS = [("45 钢", "steel", 210e9, 7850, 1.0, GREY_B), ("6061 铝合金", "6061 Al", 68.9e9, 2700, 1.5, BLUE), ("碳纤维层合板", "CFRP", 52.76e9, 1560, 1.0, GREEN)]


def defl(E, t):
    I = math.pi * D ** 3 * t / 8
    return F * L ** 3 / (3 * E * I)


def t_req(E, rho):
    return (F * L ** 3 / 3) / (math.pi * D / 8 * (DELTA * D * D * E - rho * G * L ** 4))


def mass(rho, t):
    return rho * math.pi * D * t * L


class Lesson(Base):
    def construct(self):
        self.title("5.7", "同一根小臂：钢、铝合金还是碳纤维", "One forearm: steel, aluminum or carbon fiber")
        ys = [1.6, 0.0, -1.6]
        wall = VGroup(*[Rectangle(width=0.25, height=0.9, fill_color=GREY_D, fill_opacity=1, stroke_width=0).move_to([-5.3, y, 0]) for y in ys])
        self.play(FadeIn(wall))
        mag = ValueTracker(0.0)          # 画面上的挠度放大系数（随动画增大）

        def beam(y, d_m, color, thick):
            def f():
                pts = []
                for k in range(31):
                    x = k / 30
                    w = d_m * (3 * x * x - x ** 3) / 2 * mag.get_value()          # 悬臂的挠曲线形状
                    pts.append([-5.15 + 7.5 * x, y - w, 0])
                return VMobject(stroke_color=color, stroke_width=thick).set_points_smoothly(pts)
            return always_redraw(f)

        t0 = 1.5e-3
        beams, labels = VGroup(), VGroup()
        for (zn, en_, E, rho, tmin, c), y in zip(MATS, ys):
            d = defl(E, t0)
            beams.add(beam(y, d * 1000 * 1.2 / 0.1, c, 10))          # 0.1 mm 画成 1.2 个单位
            labels.add(bi([f"{zn}：挠度 {d * 1000:.3f} mm，质量 {mass(rho, t0):.2f} kg", f"{en_}: {d * 1000:.3f} mm, {mass(rho, t0):.2f} kg"], size=22, color=c)
                       .move_to([-1.3, y + 0.5, 0]))
        self.play(*[Create(b) for b in beams], run_time=1.2)
        self.caption("同样的管子（外径 75 mm、壁厚 1.5 mm），末端挂着腕部和 4 kg 负载（这一幕不计自重）", "Same tube (OD 75 mm, wall 1.5 mm), wrist and 4 kg payload at the end (self-weight ignored here)")
        self.play(mag.animate.set_value(1.0), run_time=2)
        self.play(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.3))
        self.caption("尺寸相同：钢最硬，可也最重——挠度和 1/E 成正比，质量和 ρ 成正比", "Same size: steel is stiffest but heaviest — deflection goes as 1/E, mass as ρ", wait=2)
        self.play(FadeOut(labels))
        # 同刚度：各自取挠度正好 0.10 mm 的壁厚
        labels2 = VGroup()
        for (zn, en_, E, rho, tmin, c), y in zip(MATS, ys):
            t = t_req(E, rho)
            labels2.add(bi([f"{zn}：壁厚 {t * 1000:.2f} mm，质量 {mass(rho, t):.3f} kg", f"{en_}: wall {t * 1000:.2f} mm, {mass(rho, t):.3f} kg"], size=22, color=c)
                        .move_to([-1.3, y + 0.5, 0]))
        self.play(*[FadeOut(b) for b in beams])
        same = VGroup(*[beam(y, 1.2, c, 6) for (_, _, _, _, _, c), y in zip(MATS, ys)])
        self.play(*[Create(b) for b in same])
        self.play(LaggedStart(*[FadeIn(l) for l in labels2], lag_ratio=0.3))
        self.caption("改壁厚，让三根管的挠度（计入自重）都正好是 0.10 mm：钢和铝合金几乎一样重，碳纤维最轻——比的是 E/ρ", "Change the walls so all three deflect exactly 0.10 mm: steel and aluminum weigh about the same, CFRP is lightest — it is E/ρ that counts", wait=2.5)
        self.play(FadeOut(labels2))
        labels3 = VGroup()
        for (zn, en_, E, rho, tmin, c), y in zip(MATS, ys):
            t = max(t_req(E, rho), tmin / 1000)
            labels3.add(bi([f"{zn}：最小壁厚 {tmin:.1f} mm → 质量 {mass(rho, t):.3f} kg", f"{en_}: min wall {tmin:.1f} mm → {mass(rho, t):.3f} kg"], size=22, color=c)
                        .move_to([-1.3, y + 0.5, 0]))
        self.play(LaggedStart(*[FadeIn(l) for l in labels3], lag_ratio=0.3))
        self.caption("可钢管只要 0.38 mm 厚，做不出来、也不耐碰；按最小壁厚 1 mm，钢反而最重", "But the steel wall would be only 0.38 mm — not makeable or robust; at the 1 mm minimum steel becomes the heaviest", wait=2.5)
        self.card([["选材看性能指数，也看约束", "Select by index, and by constraints"],
                   ["外径固定、壁厚自由：比 E/ρ", "Fixed OD, free wall: compare E/ρ"],
                   ["形状固定、尺寸自由：比 E^(1/2)/ρ", "Fixed shape, free size: compare E^(1/2)/ρ"],
                   ["工艺约束（最小壁厚）会改变排序", "Process limits (minimum wall) change the ranking"]])
