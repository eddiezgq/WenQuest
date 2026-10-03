"""动画 1.1.1（配图 1.1.1）：UR5e 手臂水平伸出（上臂 0.425 m、前臂 0.392 m），先后吊起 1 kg、2 kg 零件，
再同时吊起两个，力矩柱逐段叠高（比例与叠加）；随后手臂抬起，2 kg 负载的力矩按 cos θ 减小，不与 θ 成比例。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("1.1", "比例与叠加", "Proportion and superposition")
        g, l1, l2 = 9.80665, 0.425, 0.392
        L = l1 + l2
        tau = lambda m, th=0.0: m * g * L * math.cos(th)
        S = np.array([-5.2, -0.4, 0.0])           # 肩关节
        k = 4.2                                   # 1 m 画成 4.2 格
        th = ValueTracker(0.0)

        def wrist():
            a = th.get_value()
            return S + k * L * np.array([math.cos(a), math.sin(a), 0.0])

        def arm():
            a = th.get_value()
            e = S + k * l1 * np.array([math.cos(a), math.sin(a), 0.0])
            return VGroup(Line(S, e, color=BLUE_C, stroke_width=16), Line(e, wrist(), color=BLUE_C, stroke_width=12),
                          Dot(S, radius=0.14, color=WHITE), Dot(e, radius=0.11, color=WHITE),
                          Polygon(S + [-0.35, -0.55, 0], S + [0.35, -0.55, 0], S + [0.15, -0.12, 0], S + [-0.15, -0.12, 0],
                                  color=GREY_B, fill_opacity=0.8, stroke_width=0))

        base = always_redraw(arm)
        self.play(FadeIn(base))
        dim = BraceBetweenPoints(S + [0, -0.7, 0], S + [k * L, -0.7, 0], DOWN, color=GREY_B)
        dl = MathTex(r"L = 0.817\ \mathrm{m}", font_size=30, color=GREY_B).next_to(dim, DOWN, buff=0.1)
        self.play(FadeIn(dim), FadeIn(dl))
        self.caption("UR5e 手臂水平伸出，负载挂在腕心，力臂 L = 0.817 m", "The UR5e arm held level; the load hangs at the wrist, lever arm L = 0.817 m")

        # 右侧的力矩柱：1 N·m 画成 0.12 格
        y0, sc = -2.6, 0.12
        axis = Line([2.2, y0, 0], [6.4, y0, 0], color=GREY_B)
        ylab = bi(["肩关节力矩 / (N·m)", "shoulder torque / (N·m)"], 22, GREY_B).move_to([4.3, 3.0, 0])
        self.play(Create(axis), FadeIn(ylab))

        def bar(x, m, color, bottom=0.0):
            h = sc * tau(m)
            return Rectangle(width=0.8, height=h, color=color, fill_opacity=0.75, stroke_width=1).move_to([x, y0 + sc * bottom + h / 2, 0])

        def load(m, color, dx=0.0):
            w = wrist() + np.array([dx, 0, 0])
            s = 0.3 + 0.1 * m
            box = Square(side_length=s, color=color, fill_opacity=0.85).move_to(w + [0, -0.6 - s / 2, 0])
            lab = Text(f"{m:g} kg", font_size=20, color=color).next_to(box, DOWN, buff=0.08)
            return VGroup(Line(w, w + [0, -0.6, 0], color=GREY_A, stroke_width=2), box, lab)

        m1 = load(1, YELLOW)
        b1 = bar(2.9, 1, YELLOW)
        n1 = MathTex(r"%.2f" % tau(1), font_size=28).next_to(b1, UP, buff=0.08)
        self.play(FadeIn(m1, shift=DOWN * 0.3))
        self.play(GrowFromEdge(b1, DOWN), FadeIn(n1))
        self.caption("吊 1 kg：τ₁ = mgL", "1 kg: τ1 = mgL")
        self.play(FadeOut(m1))
        m2 = load(2, ORANGE)
        b2 = bar(4.3, 2, ORANGE)
        n2 = MathTex(r"%.2f" % tau(2), font_size=28).next_to(b2, UP, buff=0.08)
        self.play(FadeIn(m2, shift=DOWN * 0.3))
        self.play(GrowFromEdge(b2, DOWN), FadeIn(n2))
        self.caption("吊 2 kg：力矩恰好加倍——比例", "2 kg: the torque exactly doubles — proportion")
        both = VGroup(load(1, YELLOW, -0.4), load(2, ORANGE, 0.4))
        self.play(FadeOut(m2), FadeIn(both, shift=DOWN * 0.3))
        b3a = bar(5.7, 1, YELLOW)
        b3b = bar(5.7, 2, ORANGE, bottom=tau(1))
        self.play(TransformFromCopy(b1, b3a))
        self.play(TransformFromCopy(b2, b3b))
        n3 = MathTex(r"%.2f" % tau(3), font_size=28).next_to(b3b, UP, buff=0.08)
        self.play(FadeIn(n3))
        self.caption("两个一起吊：力矩就是两者之和——叠加", "Both together: the torque is the sum — superposition")
        self.wait(1)

        # 手臂抬起：只留 2 kg
        self.play(FadeOut(both), FadeOut(VGroup(b1, b3a, b3b, n1, n3, dim, dl)))
        hang = always_redraw(lambda: load(2, ORANGE))
        self.add(hang)
        b2.add_updater(lambda b: b.become(Rectangle(width=0.8, height=max(1e-3, sc * tau(2, th.get_value())), color=ORANGE,
                                                     fill_opacity=0.75, stroke_width=1).move_to([4.3, y0 + sc * tau(2, th.get_value()) / 2, 0])))
        n2.add_updater(lambda n: n.become(MathTex(r"%.2f" % tau(2, th.get_value()), font_size=28).next_to(b2, UP, buff=0.08)))
        ang = always_redraw(lambda: MathTex(r"\theta = %d^\circ" % round(math.degrees(th.get_value())), font_size=32, color=GREY_A)
                            .move_to(S + [1.6, -1.5, 0]))
        self.add(ang)
        self.caption("现在让手臂抬起，与水平成 θ 角", "Now raise the arm to an angle θ above level")
        self.play(th.animate.set_value(math.radians(30)), run_time=2)
        self.wait(0.5)
        t30 = tau(2, math.radians(30))
        ghost = DashedLine([3.7, y0 + sc * (tau(2) - 2 * (tau(2) - t30)), 0], [4.9, y0 + sc * (tau(2) - 2 * (tau(2) - t30)), 0], color=RED)
        self.play(th.animate.set_value(math.radians(60)), run_time=2)
        self.play(Create(ghost))
        self.caption("抬到 60° 时力矩的减少量，不是抬到 30° 时的两倍（红虚线是“两倍”的位置）：对 θ 不成比例",
                     "The drop at 60° is not twice the drop at 30° (red dashed: where twice would be): not proportional in θ")
        self.wait(1)
        b2.clear_updaters(); n2.clear_updaters()
        self.card([["线性：比例 + 叠加", "Linear: proportion + superposition"],
                   MathTex(r"f(x+y)=f(x)+f(y),\qquad f(cx)=c\,f(x)", font_size=44),
                   ["τ = mgL cos θ 对 m 线性，对 θ 不线性", "τ = mgL cos θ is linear in m, not in θ"]])
