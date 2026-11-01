"""动画 17.4.1（配图 17.4.1）：转动惯量——把连杆分成 n 小段，每段的贡献 r²Δm 画成柱条；n 加倍，和趋于 mL²/3；
转轴移到中点，和趋于 mL²/12；两者之差正好是 m(L/2)²，这就是平行轴定理。"""
from manim import *
from wq_anim import *
import numpy as np

L = 6.0


class Lesson(Base):
    def construct(self):
        self.title("17.4", "转动惯量", "Moment of inertia")
        y0 = 1.2
        x0 = -L / 2 - 0.5
        rod = Rectangle(width=L, height=0.25, color=STEEL, fill_opacity=0.6).move_to([x0 + L / 2, y0, 0])
        ax_x = ValueTracker(x0)
        axis = always_redraw(lambda: Dot([ax_x.get_value(), y0, 0], radius=0.12, color=YELLOW))
        self.play(FadeIn(rod))
        self.add(axis)
        base = -2.4
        scale = 3.2
        bars = VGroup()
        label = None

        def make(n, axis_pos):
            g = VGroup()
            s = 0.0
            for k in range(n):
                xm = (k + 0.5) / n
                r = xm - axis_pos
                c = r * r / n
                s += c
                h = c * scale * n / 2.0 + 1e-3
                g.add(Rectangle(width=L / n * 0.8, height=h, color=ORANGE, fill_opacity=0.7, stroke_width=1)
                      .move_to([x0 + xm * L, base + h / 2, 0]))
            return g, s

        for n in (4, 8, 16):
            g, s = make(n, 0.0)
            t = MathTex(r"n=%d:\ \sum r^2\Delta m=%.4f\,mL^2" % (n, s), font_size=32).to_edge(RIGHT, buff=0.4).shift(UP * 0.2)
            if len(bars) == 0:
                self.play(Create(g), Write(t))
                self.caption("每一小段的贡献 r²Δm：离转轴越远，贡献越大", "Each piece contributes r²Δm: the farther, the more", wait=0.3)
            else:
                self.play(ReplacementTransform(bars, g), ReplacementTransform(label, t))
            bars, label = g, t
        end = MathTex(r"I_{\text{end}}=\int_0^L x^2\lambda\,dx=\tfrac13mL^2", font_size=34, color=ORANGE).to_edge(RIGHT, buff=0.4).shift(DOWN * 0.8)
        self.play(Write(end))
        self.caption("小段越分越细，和趋于积分 mL²/3", "Finer pieces: the sum tends to mL²/3", wait=0.6)
        g, s = make(16, 0.5)
        t = MathTex(r"\text{axis at centre}:\ \sum r^2\Delta m=%.4f\,mL^2" % s, font_size=32).to_edge(RIGHT, buff=0.4).shift(UP * 0.2)
        self.play(ax_x.animate.set_value(x0 + L / 2), ReplacementTransform(bars, g), ReplacementTransform(label, t), run_time=2)
        bars, label = g, t
        mid = MathTex(r"I_{\text{cm}}=\tfrac1{12}mL^2", font_size=34, color=GREEN).next_to(end, DOWN, buff=0.3)
        self.play(Write(mid))
        self.caption("转轴移到质心，转动惯量最小：mL²/12", "About the centre of mass it is smallest: mL²/12", wait=0.6)
        pa = MathTex(r"\tfrac13mL^2=\tfrac1{12}mL^2+m\left(\tfrac L2\right)^2", font_size=36, color=YELLOW).next_to(mid, DOWN, buff=0.3)
        self.play(Write(pa))
        self.caption("差正好是 m d²：平行轴定理", "The difference is exactly m d²: the parallel-axis theorem", wait=1.0)
        self.play(*[FadeOut(mm) for mm in (rod, axis, bars, label, end, mid, pa)])
        self.card([["平行轴定理", "Parallel-axis theorem"],
                   MathTex(r"I=\int r^2\,dm,\qquad I_{\text{axis}}=I_{\text{cm}}+m\,d^2", font_size=42),
                   ["绕质心的转动惯量最小；轴每离开质心 d，就加 m d²", "Smallest about the centre of mass; moving the axis by d adds m d²"]])
