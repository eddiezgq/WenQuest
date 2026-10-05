"""动画 4.6.1（配图 4.6.1）：最大实体要求下的动态公差带。轴承座地脚孔 Ø11 H13，位置度 Ø0.5 Ⓜ，功能量规的测销 Ø10.5。
孔越大（离最大实体越远），孔的轴线允许偏离理论位置越多：公差带从 Ø0.5 长到 Ø0.77；孔始终包得住测销。
数字与程序 4.6.1 相同。径向尺寸放大示意（0.1 mm 画成 0.3 个屏幕单位）。"""
from manim import *
from wq_anim import *

MMC, LMC, T0, VC = 11.0, 11.27, 0.5, 10.5
K = 3.0                        # 屏幕单位 / mm（只用于半径差和偏移，示意）
R_PIN = 1.4                    # 测销画成的半径
C0 = LEFT * 2.6 + DOWN * 0.55  # 理论位置（测销中心）


def r_hole(d):
    return R_PIN + K * (d - VC) / 2


def t_of(d):
    return T0 + (d - MMC)


class Lesson(Base):
    def construct(self):
        self.title("4.6", "最大实体要求：动态公差带", "Maximum material requirement: the dynamic tolerance zone")
        d = ValueTracker(MMC)
        ang = ValueTracker(0.6)
        pin = Circle(radius=R_PIN, stroke_color=GREY_B, fill_color=GREY_D, fill_opacity=0.9).move_to(C0)
        pin_lab = bi(["测销 Ø10.5", "gauge pin Ø10.5"], size=22).next_to(pin, LEFT, buff=1.3)
        self.play(FadeIn(pin), FadeIn(pin_lab))
        self.caption("功能量规：测销固定在地脚孔的理论位置上，直径等于孔的实效尺寸 11 − 0.5 = 10.5",
                     "Functional gauge: a pin at the true position, diameter = virtual condition 11 − 0.5 = 10.5")

        def axis_pt():
            e = K * t_of(d.get_value()) / 2
            return C0 + e * np.array([np.cos(ang.get_value()), np.sin(ang.get_value()), 0])

        zone = always_redraw(lambda: Circle(radius=K * t_of(d.get_value()) / 2, stroke_color=YELLOW, stroke_width=3,
                                            fill_color=YELLOW, fill_opacity=0.25).move_to(C0))
        hole = always_redraw(lambda: Circle(radius=r_hole(d.get_value()), stroke_color=STEEL, stroke_width=4).move_to(axis_pt()))
        dot = always_redraw(lambda: Dot(axis_pt(), color=STEEL, radius=0.07))
        cross = VGroup(Line(C0 + LEFT * 0.25, C0 + RIGHT * 0.25, color=WHITE, stroke_width=2),
                       Line(C0 + UP * 0.25, C0 + DOWN * 0.25, color=WHITE, stroke_width=2))
        self.play(Create(hole), FadeIn(dot), FadeIn(cross))
        self.caption("孔做到最大实体 Ø11.0：孔的轴线只能在 Ø0.5 的圆内（黄色），偏到边上时孔刚好碰到测销",
                     "Hole at MMC Ø11.0: its axis must stay in a Ø0.5 zone (yellow); at the edge the hole just touches the pin")
        self.play(FadeIn(zone))
        self.play(ang.animate.set_value(0.6 + 2 * PI), run_time=3, rate_func=linear)

        rd = always_redraw(lambda: VGroup(
            zh(f"孔径 d = {d.get_value():.2f} mm", 26, STEEL),
            zh(f"位置度公差 t = Ø{t_of(d.get_value()):.2f} mm", 26, YELLOW),
            zh(f"补偿 d − 11 = {d.get_value() - MMC:.2f} mm", 26, WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(RIGHT, buff=0.6).shift(UP * 0.6))
        self.play(FadeIn(rd))
        self.play(d.animate.set_value(LMC), run_time=3)
        self.caption("孔做大了（向最小实体 Ø11.27 走），多出来的 d − 11 补给位置度：公差带长到 Ø0.77",
                     "A larger hole (towards LMC Ø11.27) gives its extra size d − 11 to position: the zone grows to Ø0.77")
        self.play(ang.animate.set_value(0.6 + 4 * PI), run_time=3, rate_func=linear)
        self.caption("轴线在公差带边上转一圈，孔始终包得住测销：零件能装上，量规一试就知道",
                     "The axis travels round the zone edge and the hole still clears the pin: the part assembles, and the gauge shows it at once")
        self.play(d.animate.set_value(MMC), run_time=2)
        self.caption("独立原则（RFS）不管孔多大，公差带始终是 Ø0.5——会把能装上的零件判成不合格",
                     "Regardless of feature size (RFS) the zone stays Ø0.5 whatever the hole size — parts that would assemble get rejected")
        self.card([["最大实体要求 Ⓜ", "Maximum material requirement Ⓜ"],
                   ["实效尺寸 = 最大实体尺寸 − 位置度公差（孔）", "Virtual condition = MMC − position tolerance (hole)"],
                   ["孔偏离最大实体多少，位置度公差就增大多少", "The position tolerance grows by the hole's departure from MMC"],
                   ["只用在只要求能装上的地方；配合、对中的要素不用", "Use it where only assembly matters, not for fits or centering"]])
