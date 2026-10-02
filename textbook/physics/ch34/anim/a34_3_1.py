"""动画 34.3.1（配图 34.3.1）：导轨上的导体棒在磁场中运动。棒中正电荷受洛伦兹力向上，形成电流；电流又使棒受到
向左的安培力，阻碍运动。在恒力作用下，速度趋于末速度。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("34.3", "动生电动势", "Motional emf")
        top, bot, left = 1.5, -1.0, -5.0
        rails = VGroup(Line([left, top, 0], [6, top, 0], color=GREY_B, stroke_width=6),
                       Line([left, bot, 0], [6, bot, 0], color=GREY_B, stroke_width=6),
                       Line([left, bot, 0], [left, top, 0], color=GREY_B, stroke_width=6))
        R = Rectangle(width=0.35, height=0.9, color=WHITE, fill_color=BG, fill_opacity=1).move_to([left, 0.25, 0])
        crosses = VGroup(*[MathTex(r"\otimes", color=BLUE, font_size=26).move_to([x, y, 0])
                           for x in np.arange(-4.2, 6, 1.0) for y in (0.9, 0.25, -0.4)])
        self.play(Create(rails), FadeIn(R), FadeIn(crosses))
        self.caption("磁场垂直纸面向里，导体棒放在两根导轨上", "B points into the page; a rod lies across two rails")
        x = ValueTracker(-2.0)
        rod = always_redraw(lambda: Line([x.get_value(), bot - 0.2, 0], [x.get_value(), top + 0.2, 0], color="#d29922", stroke_width=12))
        self.add(rod)
        q = always_redraw(lambda: VGroup(Dot([x.get_value(), 0.25, 0], color=YELLOW, radius=0.09),
                                         Arrow([x.get_value() + 0.15, 0.25, 0], [x.get_value() + 0.15, 1.1, 0], buff=0, color=YELLOW, stroke_width=4)))
        self.play(FadeIn(q))
        self.caption("棒向右运动，棒中的正电荷受洛伦兹力 qv × B，方向沿棒向上", "The rod moves right; charges feel qv × B, up along the rod")
        v = ValueTracker(0.0)
        def tick(m, dt):
            vv = v.get_value()
            v.set_value(vv + (1.0 - vv) * 1.6 * dt)       # 趋于末速度：dv/dt = (v_t − v)/τ
            x.set_value(x.get_value() + 0.9 * v.get_value() * dt)
        driver = Mobject(); driver.add_updater(tick); self.add(driver)
        FA = always_redraw(lambda: Arrow([x.get_value() - 0.1, -0.45, 0], [x.get_value() - 0.1 - 1.4 * v.get_value(), -0.45, 0], buff=0,
                                          color=RED, stroke_width=6, max_tip_length_to_length_ratio=0.3))
        Fp = always_redraw(lambda: Arrow([x.get_value() + 0.1, -0.45, 0], [x.get_value() + 1.5, -0.45, 0], buff=0, color=WHITE, stroke_width=6))
        self.add(FA, Fp)
        num = always_redraw(lambda: MathTex(r"v/v_\mathrm t=%.2f" % v.get_value(), font_size=34).to_corner(UR, buff=0.6).shift(DOWN * 0.7))
        self.add(num)
        self.caption("恒力（白）拉棒；电流在磁场中受安培力（红），方向向左，随速度增大", "A constant pull (white); the current feels an Ampère force (red) to the left that grows with speed", wait=0)
        self.wait(3.5)
        self.caption("两力相等时速度不再增加：拉力做的功全部变成电阻中的焦耳热", "When they balance the speed stops growing: all the work becomes heat in R", wait=0)
        self.wait(2.5)
        driver.clear_updaters()
        self.card([["动生电动势", "Motional emf"],
                   MathTex(r"\mathcal{E}=BLv,\qquad v_\mathrm t=\frac{FR}{(BL)^2}", font_size=44),
                   ["机械功率 Fv 等于电功率 𝓔I", "Mechanical power Fv equals electrical power 𝓔I"]])
