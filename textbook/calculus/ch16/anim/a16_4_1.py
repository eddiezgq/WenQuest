"""动画 16.4.1（配图 16.4.1）：弧长——在曲线 y = x²（0 ≤ x ≤ 1）上取分点，连成内接折线；分点加倍时折线变长，
长度趋于弧长 ∫₀¹ √(1 + 4x²) dx ≈ 1.4789；放大一小段，弧与弦几乎重合，ds² = dx² + dy²。"""
from manim import *
from wq_anim import *
import numpy as np

EX = np.sqrt(5) / 2 + np.arcsinh(2) / 4


def plen(n):
    xs = np.linspace(0, 1, n + 1)
    return float(np.sum(np.hypot(np.diff(xs), np.diff(xs ** 2))))


class Lesson(Base):
    def construct(self):
        self.title("16.4", "弧长", "Arc length")
        ax = Axes(x_range=[0, 1.05, 0.5], y_range=[0, 1.05, 0.5], x_length=5.2, y_length=5.2, tips=False,
                  axis_config={"color": GREY_B}).shift(LEFT * 3.0 + DOWN * 0.3)
        g = ax.plot(lambda x: x * x, x_range=[0, 1], color=STEEL, stroke_width=4)
        self.play(Create(ax), Create(g))
        poly = None
        vals = []
        for n in (1, 2, 4, 8, 16):
            xs = np.linspace(0, 1, n + 1)
            pts = [ax.c2p(x, x * x) for x in xs]
            newp = VGroup(VMobject(color=ORANGE, stroke_width=3, fill_opacity=0).set_points_as_corners(pts), *[Dot(p, radius=0.05, color=ORANGE) for p in pts])
            newv = MathTex(r"n=%d:\ \ L_n=%.5f" % (n, plen(n)), font_size=34, color=ORANGE).to_edge(RIGHT, buff=0.8).shift(UP * (1.6 - 0.55 * (n.bit_length() - 1)))
            if poly is None:
                self.play(Create(newp), Write(newv))
            else:
                self.play(FadeOut(poly), Create(newp), Write(newv), run_time=1.0)
            poly = newp
            vals.append(newv)
            if n == 2:
                self.caption("内接折线：分点加倍，折线只会变长", "Inscribed polyline: doubling the points can only lengthen it", wait=0.3)
        ex = MathTex(r"L=\int_0^1\sqrt{1+4x^2}\,dx=%.5f" % EX, font_size=34, color=STEEL).to_edge(RIGHT, buff=0.8).shift(DOWN * 1.6)
        self.play(Write(ex))
        self.caption("折线长度增大，趋于弧长：弧长定义为折线长度的上确界", "The lengths increase to the arc length, their supremum", wait=0.8)
        # 放大一小段
        x0, dx = 0.6, 0.12
        p0, p1 = ax.c2p(x0, x0 ** 2), ax.c2p(x0 + dx, (x0 + dx) ** 2)
        corner = ax.c2p(x0 + dx, x0 ** 2)
        tri = VGroup(Line(p0, corner, color=YELLOW), Line(corner, p1, color=YELLOW), Line(p0, p1, color=RED, stroke_width=4))
        lab = VGroup(MathTex("dx", font_size=30, color=YELLOW).next_to(Line(p0, corner), DOWN, buff=0.1),
                     MathTex("dy", font_size=30, color=YELLOW).next_to(Line(corner, p1), RIGHT, buff=0.1),
                     MathTex("ds", font_size=30, color=RED).next_to(Line(p0, p1).get_center(), UL, buff=0.1))
        self.play(FadeOut(poly), Create(tri), Write(lab))
        self.caption("取一小段：弧与弦几乎一样长，ds² = dx² + dy²", "On a short piece, arc ≈ chord: ds² = dx² + dy²", wait=1.0)
        self.play(*[FadeOut(m) for m in (ax, g, tri, lab, ex, *vals)])
        self.card([["弧长公式", "Arc length"],
                   MathTex(r"L=\int_a^b\sqrt{1+f'(x)^2}\,dx=\int_\alpha^\beta\sqrt{x'(t)^2+y'(t)^2}\,dt", font_size=40),
                   ["弧长是内接折线长度的上确界", "Arc length is the supremum of inscribed polyline lengths"]])
