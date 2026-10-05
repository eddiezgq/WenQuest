"""动画 2.3.1（配图 2.3.2、2.3.3）：电动机正反转——不互锁时两个接触器同时吸合，L1、L3 相间短路；
接触器互锁让 KM2 等 KM1 真正断开以后才吸合（先断后通）。时间取自程序 2.3.1 的测试：KM1 线圈断电后 12 ms 主触点打开，
电弧约 6 ms 后熄灭，KM2 在 31 ms 时闭合。"""
from manim import *
from wq_anim import *

XS = [-5.3, -4.7, -4.1]          # L1 L2 L3 through KM1
G = 2.2                          # KM2 sits G to the right
Y_TOP, Y_K, Y_M = 1.9, 0.3, -1.95


def pole(x, y, closed=False, color=INK):
    """One main contact: fixed end above, blade from the pivot below."""
    top = Line([x, y + 0.6, 0], [x, y + 0.25, 0], color=color)
    bot = Line([x, y - 0.25, 0], [x, y - 0.6, 0], color=color)
    blade = Line([x, y - 0.25, 0], [x, y + 0.25, 0] if closed else [x - 0.3, y + 0.2, 0], color=color, stroke_width=5)
    return VGroup(top, bot, blade)


def blade(x, y, closed, color=INK):
    return Line([x, y - 0.25, 0], [x, y + 0.25, 0] if closed else [x - 0.3, y + 0.2, 0], color=color, stroke_width=5)


class Lesson(Base):
    def construct(self):
        self.title("2.3", "正反转与互锁", "Reversing and interlocking")
        # supply lines, taps to KM2, KM1 and KM2 poles, crossing back (L1 ↔ L3), motor
        lines = VGroup()
        for i, x in enumerate(XS):
            lines.add(Line([x, Y_TOP, 0], [x, Y_K + 0.6, 0], color=INK), Line([x, Y_K - 0.6, 0], [x, Y_M + 0.75, 0], color=INK))
            ty = Y_K + 1.05 - 0.15 * i
            lines.add(Line([x, ty, 0], [x + G, ty, 0], color=INK), Line([x + G, ty, 0], [x + G, Y_K + 0.6, 0], color=INK), Dot([x, ty, 0], 0.05, color=INK))
            by = Y_K - 1.2 - 0.15 * (2 - i)
            j = 2 - i
            lines.add(Line([x + G, Y_K - 0.6, 0], [x + G, by, 0], color=INK), Line([x + G, by, 0], [XS[j], by, 0], color=INK), Dot([XS[j], by, 0], 0.05, color=INK))
        names = VGroup(*[Text(n, font=LATIN, font_size=18, color=INK).move_to([x, Y_TOP + 0.25, 0]) for n, x in zip(("L1", "L2", "L3"), XS)])
        km1 = VGroup(*[pole(x, Y_K) for x in XS])
        km2 = VGroup(*[pole(x + G, Y_K) for x in XS])
        l1 = Text("KM1", font=LATIN, font_size=20, color=INK).next_to(km1, LEFT, buff=0.3)
        l2 = Text("KM2", font=LATIN, font_size=20, color=INK).next_to(km2, RIGHT, buff=0.3)
        mot = VGroup(Circle(radius=0.5, color=INK).move_to([XS[1], Y_M, 0]), Text("M\n3~", font=LATIN, font_size=18, color=INK, line_spacing=0.6).move_to([XS[1], Y_M, 0]))
        swap = Text("L1 ↔ L3", font=LATIN, font_size=18, color=MUTED).move_to([XS[1] + G, Y_K - 1.75, 0])
        self.play(Create(lines), FadeIn(names), FadeIn(km1), FadeIn(km2), FadeIn(l1), FadeIn(l2), FadeIn(mot), run_time=2)
        self.play(FadeIn(swap))
        self.caption("反转只要对调两相：KM2 把 L1 和 L3 换了位置", "Reversing only needs two phases swapped: KM2 exchanges L1 and L3")

        # forward: KM1 closes, the motor turns clockwise
        self.play(*[Transform(km1[i][2], blade(x, Y_K, True, GREEN)) for i, x in enumerate(XS)], run_time=0.5)
        arrow = Arc(radius=0.72, start_angle=PI * 0.75, angle=-PI * 0.5, color=GREEN, stroke_width=5).move_arc_center_to([XS[1], Y_M, 0]).add_tip(tip_length=0.18)
        self.play(Create(arrow), Rotate(arrow, -PI / 2, about_point=[XS[1], Y_M, 0]), run_time=1.2)
        self.caption("KM1 吸合，电动机正转", "KM1 closes: the motor runs forward", wait=1)

        # no interlock: S3 pressed, KM2 closes while KM1 is still closed
        self.caption("没有互锁：按下反转按钮，KM2 吸合，KM1 却还没断开……", "No interlock: reverse is pressed; KM2 closes while KM1 is still closed…", wait=0.8)
        self.play(*[Transform(km2[i][2], blade(x + G, Y_K, True, GREEN)) for i, x in enumerate(XS)], run_time=0.4)
        ya, yb = Y_K + 0.75, Y_K - 1.2          # L3's tap to KM2, KM2's pole 3 back to the U lead
        short = VGroup(Line([XS[0], Y_TOP, 0], [XS[0], yb, 0]), Line([XS[2], ya, 0], [XS[2] + G, ya, 0]),
                       Line([XS[2] + G, ya, 0], [XS[2] + G, yb, 0]), Line([XS[2] + G, yb, 0], [XS[0], yb, 0]),
                       Line([XS[2], Y_TOP, 0], [XS[2], ya, 0])).set_color(RED).set_stroke(width=9)
        boom = Text("L1–L3 短路！", font=CJK, font_size=34, color=RED).move_to([1.6, 1.2, 0])
        self.play(Create(short), FadeIn(boom, scale=1.4), run_time=0.8)
        self.play(Flash([XS[0], yb, 0], color=RED, flash_radius=0.6), run_time=0.6)
        self.caption("L1、L3 经两个接触器直接接通——相间短路，断路器跳闸，触点可能烧坏",
                     "L1 and L3 meet through the two contactors: a phase-to-phase short; the breaker trips, the contacts may burn")
        self.play(FadeOut(short), FadeOut(boom), FadeOut(arrow),
                  *[Transform(km1[i][2], blade(x, Y_K, False)) for i, x in enumerate(XS)],
                  *[Transform(km2[i][2], blade(x + G, Y_K, False)) for i, x in enumerate(XS)], run_time=0.8)

        # with the interlock: a timeline of the change-over
        self.play(*[Transform(km1[i][2], blade(x, Y_K, True, GREEN)) for i, x in enumerate(XS)], run_time=0.4)
        ax = NumberLine(x_range=[0, 40, 10], length=5.2, include_numbers=False, color=MUTED).move_to([3.4, -1.9, 0])
        ticks = VGroup(*[Text(str(v), font=LATIN, font_size=18, color=MUTED).next_to(ax.n2p(v), DOWN, buff=0.15) for v in (0, 10, 20, 30, 40)])
        unit = VGroup(ticks, Text("ms", font=LATIN, font_size=18, color=MUTED).next_to(ax, RIGHT, buff=0.15))
        def bar(row, t0, t1, color, label):
            y = 0.9 - row * 0.75
            r = Rectangle(width=(t1 - t0) / 40 * 5.2, height=0.32, fill_color=color, fill_opacity=0.85, stroke_width=0).move_to(
                [ax.n2p(t0)[0] + (t1 - t0) / 80 * 5.2, y, 0])
            t = Text(label, font=CJK, font_size=18, color=INK).move_to([0.25, y, 0], aligned_edge=RIGHT)
            return r, t
        b1, t1 = bar(0, 0, 12, GREEN, "KM1 主触点闭合")
        arc, ta = bar(0, 12, 18, ORANGE, "")
        b2, t2 = bar(1, 0, 12, GREEN, "KM1 辅助触点")
        b3, t3 = bar(2, 13, 40, BLUE, "KM2 线圈")
        b4, t4 = bar(3, 31, 40, GREEN, "KM2 主触点闭合")
        self.caption("有接触器互锁：KM2 的线圈串着 KM1 的常闭辅助触点", "With the contactor interlock: KM2's coil is in series with KM1's NC auxiliary contact")
        self.play(Create(ax), FadeIn(unit), FadeIn(t1), FadeIn(t2), FadeIn(t3), FadeIn(t4))
        self.play(GrowFromEdge(b1, LEFT), GrowFromEdge(b2, LEFT), run_time=0.8)
        self.play(*[Transform(km1[i][2], blade(x, Y_K, False)) for i, x in enumerate(XS)], GrowFromEdge(arc, LEFT), run_time=0.6)
        self.caption("KM1 断电 12 ms 后主触点打开，电弧再烧几毫秒；它的辅助触点这时才放 KM2 通电", "12 ms after its coil drops, KM1 opens; the arc burns a few ms more; only now does its auxiliary contact let KM2 in")
        self.play(GrowFromEdge(b3, LEFT), run_time=0.8)
        self.play(GrowFromEdge(b4, LEFT), *[Transform(km2[i][2], blade(x + G, Y_K, True, GREEN)) for i, x in enumerate(XS)], run_time=0.6)
        gap = DoubleArrow(ax.n2p(18) + UP * 0.35, ax.n2p(31) + UP * 0.35, color=RED, buff=0, stroke_width=3, tip_length=0.15)
        gl = Text("13 ms", font=LATIN, font_size=20, color=RED).next_to(gap, UP, buff=0.08)
        self.play(GrowFromCenter(gap), FadeIn(gl))
        arrow2 = Arc(radius=0.72, start_angle=PI * 0.25, angle=PI * 0.5, color=BLUE, stroke_width=5).move_arc_center_to([XS[1], Y_M, 0]).add_tip(tip_length=0.18)
        self.play(Create(arrow2), Rotate(arrow2, PI / 2, about_point=[XS[1], Y_M, 0]), run_time=1.2)
        self.caption("先断后通：两组主触点之间隔着 13 ms，电动机反转", "Break before make: 13 ms between the two sets of main contacts; the motor reverses")
        self.card([["互锁：两个接触器不许同时吸合", "Interlock: the two contactors must never close together"],
                   ["按钮互锁 + 接触器辅助触点互锁 = 双重互锁", "Button + auxiliary-contact interlock = double interlock"],
                   ["主触点熔焊时，辅助触点照样把 KM2 挡住", "If KM1's main contacts weld, its auxiliary contact still keeps KM2 out"]])
