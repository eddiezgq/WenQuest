"""动画 1.1.1（配图 1.1.2）：开环与闭环的小车驶向障碍物。

开环小车只按时间表前进，撞上障碍；闭环小车的扫描仪在 1.65 m 处发现障碍，反应 0.1 s 后以 0.5 m/s² 刹车，
在障碍前停住。停车距离 d = v·t_d + v²/(2a) = 1.1 m（算例 1.1.1）。
"""
from manim import *
from wq_anim import *
import numpy as np

S = 1.6                      # 1 m 画成 1.6 个单位
X0 = -5.4                    # 车头的起点
V, TD, A, RANGE, XOBS = 1.0, 0.1, 0.5, 1.65, 3.0


def front_closed(t):
    t_det = (XOBS - RANGE) / V
    tb = t_det + TD
    if t <= tb:
        return V * t
    tt = min(t - tb, V / A)
    return V * tb + V * tt - 0.5 * A * tt * tt


def front_open(t):
    return min(V * t, XOBS)


class Lesson(Base):
    def construct(self):
        self.title("1.1", "开环与闭环：小车能不能停住", "Open loop vs closed loop: can the cart stop?")
        lanes = (1.25, -1.05)
        objs = VGroup()
        for y in lanes:
            objs.add(ground(y=y - 0.05, x0=-6.6, x1=6.6))
            objs.add(cargo(0.7, label="").move_to([X0 + XOBS * S + 0.35, y + 0.3, 0]))
        tags = VGroup(bi(["开环：只按时间表前进", "open loop: follows a timetable"], 22).move_to([-3.9, lanes[0] + 1.0, 0]),
                      bi(["闭环：看着前方行驶", "closed loop: watches ahead"], 22).move_to([-3.9, lanes[1] + 1.0, 0]))
        cars = [agv(width=1.3, height=0.42), agv(width=1.3, height=0.42, color=GREEN)]
        for c, y in zip(cars, lanes):
            c.move_to([X0 - 0.65, y + 0.27, 0])
        self.play(FadeIn(objs), FadeIn(tags), *[FadeIn(c) for c in cars])
        self.caption("两台小车一样快：1.0 m/s；前方 3 m 处有障碍物", "Same speed, 1.0 m/s; an obstacle 3 m ahead")

        t = ValueTracker(0.0)
        cars[0].add_updater(lambda m: m.move_to([X0 + front_open(t.get_value()) * S - 0.65, lanes[0] + 0.27, 0]))
        cars[1].add_updater(lambda m: m.move_to([X0 + front_closed(t.get_value()) * S - 0.65, lanes[1] + 0.27, 0]))

        def ray():
            f = X0 + front_closed(t.get_value()) * S
            seen = (XOBS - front_closed(t.get_value())) <= RANGE + 1e-9
            return Line([f, lanes[1] + 0.35, 0], [min(f + RANGE * S, X0 + XOBS * S), lanes[1] + 0.35, 0],
                        color=RED if seen else YELLOW, stroke_width=4)
        beam = always_redraw(ray)
        speed = always_redraw(lambda: MathTex(r"v = %.2f\ \mathrm{m/s}" % (
            V if t.get_value() <= (XOBS - RANGE) / V + TD else max(0.0, V - A * (t.get_value() - (XOBS - RANGE) / V - TD))),
            color=GREEN, font_size=30).move_to([4.6, lanes[1] + 1.1, 0]))
        self.add(beam, speed)
        self.caption("闭环小车的扫描仪探测 1.65 m；开环小车什么也不看", "The closed-loop cart scans 1.65 m ahead; the open-loop cart looks at nothing", wait=0)
        self.play(t.animate.set_value(3.0), run_time=4.5, rate_func=linear)
        boom = VGroup(Cross(stroke_color=RED, stroke_width=8).scale(0.35).move_to([X0 + XOBS * S, lanes[0] + 0.4, 0]),
                      bi(["相撞", "collision"], 24, RED).move_to([X0 + XOBS * S + 1.6, lanes[0] + 0.5, 0]))
        self.play(FadeIn(boom, scale=1.4), run_time=0.5)
        self.play(t.animate.set_value(3.45), run_time=0.9, rate_func=linear)
        for c in cars:
            c.clear_updaters()
        gap = DoubleArrow([X0 + front_closed(3.45) * S, lanes[1] - 0.35, 0], [X0 + XOBS * S, lanes[1] - 0.35, 0],
                          buff=0, color=YELLOW, stroke_width=3, tip_length=0.15)
        stop = DoubleArrow([X0 + (XOBS - RANGE) * S, lanes[1] - 0.75, 0], [X0 + front_closed(3.45) * S, lanes[1] - 0.75, 0],
                           buff=0, color=ORANGE, stroke_width=3, tip_length=0.15)
        lab = MathTex(r"d = v\,t_d + \frac{v^2}{2a} = 0.1 + 1.0 = 1.1\ \mathrm{m}", color=ORANGE, font_size=30)\
            .next_to(stop, DOWN, buff=0.12)
        self.play(GrowFromCenter(stop), Write(lab), GrowFromCenter(gap))
        self.caption("发现障碍后又走了 1.1 m 才停住：反应 0.1 m，刹车 1.0 m", "After detection it runs 1.1 m more: 0.1 m reacting, 1.0 m braking", wait=2)
        self.card([["开环与闭环", "Open loop and closed loop"],
                   ["开环：指令只依赖时间；闭环：指令依赖测量", "open loop: commands depend on time only; closed loop: on measurements"],
                   MathTex(r"d = v\,t_d + \frac{v^2}{2a}", font_size=44),
                   ["探测距离必须大于停车距离", "the sensing range must exceed the stopping distance"]])
