"""动画 9.4.1（配图 9.4.1）：串联与并联刚度，最弱的一环决定整体。
三根弹簧串联，刚度 10、10、1（相对值）：同一个力下，软的那根伸长是硬的 10 倍，占总伸长的 5/6；
把两根硬弹簧再加硬一倍，总伸长几乎不变；把软的加硬一倍，总伸长差不多减半。并联时位移相同，力按刚度分摊。
最后联系 9.4 节：UR5e 带 5 kg 时，肩关节减速器一环占末端下垂的一半以上（程序 9.4.1）。"""
import numpy as np

from manim import *
from wq_anim import *

Y0 = UP * 0.4
X0 = LEFT * 5.6


def spring(a, b, coils=7, amp=0.22, color=WHITE, width=4):
    a, b = np.array(a), np.array(b)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0], 0])
    pts = [a, a + u * 0.15]
    m = 2 * coils
    for i in range(m):
        t = 0.15 + (L - 0.3) * (i + 0.5) / m
        pts.append(a + u * t + n * amp * (1 if i % 2 == 0 else -1))
    pts += [b - u * 0.15, b]
    return VMobject(color=color, stroke_width=width).set_points_as_corners(pts)


class Lesson(Base):
    def construct(self):
        self.title("9.4", "串联与并联：最弱的一环决定整体", "Series and parallel: the weakest link governs")
        k = [ValueTracker(10.0), ValueTracker(10.0), ValueTracker(1.0)]
        F = ValueTracker(0.0)
        base_len = [2.0, 2.0, 2.0]
        cols = [BLUE, GREEN, RED]
        names = [("连杆", "link"), ("轴承", "bearing"), ("减速器", "reducer")]
        SCALE = 1.5                                   # 伸长 = F/k × SCALE

        def series():
            grp = VGroup(Rectangle(width=0.25, height=1.6, color=GREY_B, fill_color=GREY_D, fill_opacity=1).move_to(X0 + Y0 + LEFT * 0.12))
            x = X0 + Y0
            for i in range(3):
                L = base_len[i] + F.get_value() / k[i].get_value() * SCALE
                nx = x + RIGHT * L
                grp.add(spring(x, nx, color=cols[i]))
                grp.add(Dot(nx, radius=0.07, color=WHITE))
                grp.add(Text(f"k = {k[i].get_value():.0f}", font_size=20, color=cols[i]).next_to((x + nx) / 2, UP, buff=0.32))
                grp.add(Text(f"{names[i][0]} {names[i][1]}", font_size=16, color=GREY_A).next_to((x + nx) / 2, DOWN, buff=0.32))
                x = nx
            if F.get_value() > 0.05:
                grp.add(Arrow(x, x + RIGHT * 0.9, buff=0, color=YELLOW, stroke_width=5))
            tot = sum(F.get_value() / k[i].get_value() for i in range(3))
            soft = F.get_value() / k[2].get_value()
            txt = f"总伸长 total = {tot:.2f}" + (f"   减速器占 reducer share {soft / tot * 100:.0f}%" if tot > 0 else "")
            grp.add(Text(txt, font_size=22, color=YELLOW).move_to(DOWN * 1.3))
            return grp

        s = always_redraw(series)
        self.play(FadeIn(s))
        self.caption("三根弹簧串联：力依次通过每一根，伸长相加", "Three springs in series: the force passes through each, extensions add")
        self.play(F.animate.set_value(1.0), run_time=2)
        self.caption("同一个力下，刚度只有十分之一的那根，伸长是别的 10 倍，占了总伸长的 5/6",
                     "Under the same force the spring with a tenth of the stiffness stretches 10× as much — 5/6 of the total", wait=2)
        self.play(k[0].animate.set_value(20.0), k[1].animate.set_value(20.0), run_time=2)
        self.caption("把两根硬的再加硬一倍：总伸长几乎没变", "Make the two stiff ones twice as stiff: the total hardly changes", wait=2)
        self.play(k[0].animate.set_value(10.0), k[1].animate.set_value(10.0), k[2].animate.set_value(2.0), run_time=2)
        self.caption("只把最软的那根加硬一倍：总伸长差不多减半——加强最弱的一环", "Double only the softest: the total nearly halves — strengthen the weakest link", wait=2)
        self.play(FadeOut(s))

        # 并联
        kp = [3.0, 1.0]
        d = ValueTracker(0.0)

        def parallel():
            grp = VGroup(Rectangle(width=0.25, height=2.4, color=GREY_B, fill_color=GREY_D, fill_opacity=1).move_to(X0 + Y0 + LEFT * 0.12))
            xe = X0 + Y0 + RIGHT * (3.0 + d.get_value())
            for i, (dy, c) in enumerate(((UP * 0.6, BLUE), (DOWN * 0.6, RED))):
                grp.add(spring(X0 + Y0 + dy, xe + dy, color=c))
                grp.add(Text(f"k = {kp[i]:.0f}   F{i + 1} = {kp[i] * d.get_value() / SCALE:.1f}", font_size=20, color=c).next_to(xe + dy, RIGHT, buff=0.3))
            grp.add(Line(xe + UP * 0.8, xe + DOWN * 0.8, color=WHITE, stroke_width=6))
            return grp

        p = always_redraw(parallel)
        self.play(FadeIn(p))
        self.caption("并联：两根弹簧位移相同，刚度相加", "In parallel: equal displacement, stiffnesses add")
        self.play(d.animate.set_value(0.6), run_time=2)
        self.caption("力按刚度分摊：硬的那根分到 3/4——超静定结构里，越刚的地方受力越大（9.3 节）",
                     "The force divides by stiffness: the stiff one takes 3/4 — in an indeterminate structure the stiffer part carries more (Section 9.3)", wait=2)
        self.play(FadeOut(p))
        self.card([["串联：柔度相加，1/k = Σ 1/kᵢ", "series: compliances add, 1/k = Σ 1/kᵢ"],
                   ["并联：刚度相加，k = Σ kᵢ", "parallel: stiffnesses add, k = Σ kᵢ"],
                   ["关节折算到末端的刚度是 K/x²", "a joint referred to the tip: K/x²"],
                   ["UR5e 带 5 kg：肩关节减速器一环占末端下垂的一半以上", "UR5e with 5 kg: the shoulder reducer alone gives over half the tip sag"]])
