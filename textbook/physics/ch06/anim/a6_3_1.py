"""动画 6.3.1（配图 6.3.2）：同样的驱动力，载货加倍，加速度减半。两辆 AGV 并排起步，速度箭头随时间增长。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("6.3", "同样的力，不同的质量", "Same force, different mass")
        ys = [0.9, -1.6]
        floors = VGroup(*[ground(y=y, x0=-6.8, x1=6.8) for y in ys])
        self.play(Create(floors))
        cars = []
        for k, y in enumerate(ys):
            car = agv(width=2.2, height=0.6)
            boxes = VGroup(*[cargo(0.55) for _ in range(k + 1)]).arrange(RIGHT, buff=0.08)
            boxes.next_to(car, UP, buff=0)
            g = VGroup(car, boxes).move_to(np.array([-5.0, y, 0]), aligned_edge=DOWN)
            cars.append(g)
            lab = MathTex(r"m_\mathrm{tot}=m" if k == 0 else r"m_\mathrm{tot}=2m", color=INK, font_size=30).move_to(np.array([1.6, y + 1.6, 0]))
            self.add(lab)
            cars[-1].lab = lab
        self.play(*[FadeIn(c) for c in cars])
        self.caption("驱动力相同：120 N；下面那辆的总质量是上面的两倍", "Same driving force, 120 N; the lower one has twice the total mass")
        forces = VGroup(*[vec(c.get_corner(DR) + LEFT * 0.5, c.get_corner(DR) + RIGHT * 0.8, C_F, r"\boldsymbol F_\mathrm d", RIGHT)
                          for c in cars])
        self.play(*[GrowArrow(f[0]) for f in forces], *[Write(f[1]) for f in forces])
        self.wait(0.5)
        self.play(FadeOut(forces))
        t = ValueTracker(0.0)
        accs = [1.0, 0.5]                   # m/s²
        scale = 1.6                         # 屏幕单位 / m
        x0 = [c.get_center()[0] for c in cars]
        for c, a, xc in zip(cars, accs, x0):
            c.add_updater(lambda m, a=a, xc=xc: m.move_to(np.array([xc + scale * 0.5 * a * t.get_value() ** 2, m.get_center()[1], 0])))
        vels = always_redraw(lambda: VGroup(*[
            Arrow(cars[k].get_top() + UP * 0.25, cars[k].get_top() + UP * 0.25 + RIGHT * (0.01 + 0.9 * accs[k] * t.get_value()),
                  buff=0, color=C_V, stroke_width=6, max_tip_length_to_length_ratio=0.3) for k in range(2)]))
        nums = always_redraw(lambda: VGroup(*[
            MathTex(r"a=%.1f\ \mathrm{m/s^2}" % accs[k], color=C_A, font_size=30).move_to(np.array([4.6, ys[k] + 1.6, 0]))
            for k in range(2)]))
        self.add(vels, nums)
        self.caption("同时起步：上面那辆的速度箭头长得快一倍", "Starting together: the upper one's velocity grows twice as fast", wait=0)
        self.play(t.animate.set_value(2.8), run_time=4, rate_func=linear)
        for c in cars:
            c.clear_updaters()
        self.wait(1)
        self.card([["牛顿第二定律", "Newton's second law"],
                   MathTex(r"\boldsymbol F = m\boldsymbol a,\qquad a=\frac{F}{m}", font_size=44),
                   ["总质量加倍，加速度减半：质量是惯性的量度", "Double the total mass, half the acceleration: mass measures inertia"]])
