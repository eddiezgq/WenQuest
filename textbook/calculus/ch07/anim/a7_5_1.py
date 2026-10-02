"""动画 7.5.1（配图 7.5.1）：电机小齿轮带动大齿轮（画面中减速比取 6，以便看清；UR5e 实际约 100），大齿轮带动上臂；
三个变化率读数 dθ_m/dt、dθ/dθ_m = 1/N、dy/dθ = l₁cos θ 相乘等于肘关节中心的上升速度；上臂竖直时上升速度为零。"""
from manim import *
from wq_anim import *
import numpy as np
import math


def gear(r, n, color):
    pts = []
    for k in range(4 * n):
        a = 2 * math.pi * k / (4 * n)
        rr = r * (1.0 if k % 4 in (0, 1) else 0.86)
        pts.append([rr * math.cos(a), rr * math.sin(a), 0])
    g = VGroup(Polygon(*pts, color=color, stroke_width=3, fill_opacity=0.15, fill_color=color))
    g.add(Line(ORIGIN, [r * 0.8, 0, 0], color=color, stroke_width=4))
    return g


class Lesson(Base):
    def construct(self):
        self.title("7.5", "链式法则：变化率逐级相乘", "Chain rule: rates multiply stage by stage")
        N, l1 = 6.0, 2.2
        wm = 3.0                                     # motor angular speed in the picture, rad/s
        th = ValueTracker(math.radians(10))          # joint angle θ
        cj = np.array([-3.4, -1.6, 0])               # reducer output = joint axis; the arm turns with it
        cm = cj + np.array([-2.1, 0, 0])             # motor pinion, meshing with the output gear (radii 0.3 + 1.8)
        small = gear(0.3, 8, ORANGE).move_to(cm)
        big = gear(1.8, 48, STEEL).move_to(cj)       # 48 : 8 teeth = 6 : 1, the ratio N of the picture
        base = cj

        def link():
            t = th.get_value()
            tip = base + l1 * np.array([math.cos(t), math.sin(t), 0])
            return VGroup(Line(base, tip, color=STEEL, stroke_width=12), Dot(base, color=WHITE, radius=0.1),
                          Dot(tip, color=YELLOW, radius=0.1),
                          DashedLine(tip, [tip[0], base[1] - 0.2, 0], color=GREY_B, stroke_width=2))

        arm = always_redraw(link)
        self.play(FadeIn(small), FadeIn(big), FadeIn(arm))
        self.caption("电机（橙）转得快，经减速器（蓝）带动关节转得慢", "The motor (orange) spins fast; the reducer (blue) turns the joint slowly", wait=0.5)
        last = {"t": th.get_value()}

        def spin(m, rate):
            def upd(mob, dt):
                mob.rotate(rate * dt, about_point=mob.get_center())
            return upd

        small.add_updater(spin(small, -wm))          # pinion clockwise ...
        big.add_updater(spin(big, wm / N))           # ... output gear and arm counter-clockwise, N times slower

        def readouts():
            t = th.get_value()
            r1 = zh("dθ_m/dt = %.1f rad/s" % wm, 24, ORANGE)
            r2 = zh("dθ/dθ_m = 1/N = 1/%d" % N, 24, STEEL)
            r3 = zh("dy/dθ = l₁cos θ = %.2f" % (l1 * math.cos(t)), 24, WHITE)
            r4 = zh("dy/dt = %.3f" % (l1 * math.cos(t) * wm / N), 28, YELLOW)
            return VGroup(r1, r2, r3, r4).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UR, buff=0.5).shift(DOWN * 1.0)

        rd = always_redraw(readouts)
        self.play(FadeIn(rd))
        self.play(th.animate.set_value(math.radians(60)), run_time=(math.radians(50)) / (wm / N), rate_func=linear)
        self.caption("三个读数相乘，就是肘关节中心上升的速度", "The product of the three readings is the rising speed of the elbow")
        self.play(th.animate.set_value(math.radians(90)), run_time=(math.radians(30)) / (wm / N), rate_func=linear)
        small.clear_updaters()
        big.clear_updaters()
        self.caption("上臂竖直时 cos θ = 0：关节照样转，肘关节中心那一瞬间却不上升", "Arm vertical: cos θ = 0, so the elbow does not rise at that instant")
        self.wait(1)
        self.card([["复合函数的变化率是各级变化率之积", "The rate of a composite is the product of the rates"],
                   MathTex(r"\frac{dy}{dt}=\frac{dy}{d\theta}\cdot\frac{d\theta}{d\theta_m}\cdot\frac{d\theta_m}{dt}", font_size=48),
                   ["（画面中减速比取 6，UR5e 实际约 100）", "(ratio 6 in the picture; about 100 on the UR5e)"]])
