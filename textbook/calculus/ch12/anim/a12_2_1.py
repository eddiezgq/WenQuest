"""动画 12.2.1（配图 12.2.1）：左、右、中点黎曼和——同一条曲线下，三种矩形和随分点增多（n = 4、8、16、32、64）一起逼近同一个面积。"""
from manim import *
from wq_anim import *
import numpy as np

F = lambda x: 0.6 + 0.9 * x - 0.25 * x * x + 0.35 * np.sin(2.2 * x)
EXACT = None


def riemann(n, rule):
    h = 3.0 / n
    k = np.arange(n)
    pts = {"L": k * h, "R": (k + 1) * h, "M": (k + 0.5) * h}[rule]
    return float(np.sum(F(pts)) * h)


class Lesson(Base):
    def construct(self):
        self.title("12.2", "黎曼和", "Riemann sums")
        xs = np.linspace(0, 3, 200001)
        exact = float(np.sum((F(xs[1:]) + F(xs[:-1])) / 2 * np.diff(xs)))
        axs, curves, labels = [], [], []
        names = (("L", "左", "left", STEEL), ("R", "右", "right", ORANGE), ("M", "中点", "midpoint", GREEN))
        for i, (rule, cn, en, col) in enumerate(names):
            ax = Axes(x_range=[0, 3, 1], y_range=[0, 2.5, 1], x_length=3.6, y_length=2.6, tips=False,
                      axis_config={"color": GREY_B}).shift(LEFT * 4.3 + RIGHT * 4.3 * i + UP * 0.6)
            g = ax.plot(F, x_range=[0, 3], color=WHITE, stroke_width=2.5)
            t = Text(cn, font_size=26, color=col).next_to(ax, UP, buff=0.1)
            axs.append(ax)
            curves.append(g)
            labels.append(t)
        self.play(*[Create(a) for a in axs], *[Create(g) for g in curves], *[FadeIn(t) for t in labels])
        rects = [VGroup() for _ in range(3)]
        vals = [VGroup() for _ in range(3)]
        for n in (4, 8, 16, 32, 64):
            new_r, new_v = [], []
            for i, (rule, cn, en, col) in enumerate(names):
                ax = axs[i]
                h = 3.0 / n
                grp = VGroup()
                for k in range(n):
                    x = {"L": k * h, "R": (k + 1) * h, "M": (k + 0.5) * h}[rule]
                    y = F(x)
                    r = Polygon(ax.c2p(k * h, 0), ax.c2p((k + 1) * h, 0), ax.c2p((k + 1) * h, y), ax.c2p(k * h, y),
                                stroke_width=1 if n <= 16 else 0.4, color=col, fill_color=col, fill_opacity=0.35)
                    grp.add(r)
                new_r.append(grp)
                s = riemann(n, rule)
                new_v.append(MathTex(r"n=%d:\ %.4f" % (n, s), font_size=30, color=col).next_to(ax, DOWN, buff=0.35))
            if n == 4:
                self.play(*[FadeIn(r) for r in new_r], *[Write(v) for v in new_v])
            else:
                self.play(*[ReplacementTransform(rects[i], new_r[i]) for i in range(3)],
                          *[ReplacementTransform(vals[i], new_v[i]) for i in range(3)], run_time=1.2)
            rects, vals = new_r, new_v
            if n == 4:
                self.caption("左、右、中点：每个小矩形的高取在不同的位置", "Left, right, midpoint: heights taken at different points", wait=0.4)
            self.wait(0.5)
        ex = MathTex(r"\int_0^3 f(x)\,dx\approx %.4f" % exact, font_size=36, color=YELLOW).to_edge(DOWN).shift(UP * 0.9)
        self.play(Write(ex))
        self.caption("分点越多，三种和越接近，极限就是定积分；中点和收敛得最快", "More points: the three sums close in on the integral; the midpoint sum is fastest", wait=0.8)
        self.play(*[FadeOut(m) for m in (*axs, *curves, *labels, *rects, *vals, ex)])
        self.card([["定积分", "The definite integral"],
                   MathTex(r"\int_a^b f(x)\,dx=\lim_{\lambda\to 0}\sum_{i=1}^{n} f(\xi_i)\,\Delta x_i", font_size=44),
                   ["无论怎样取点，分得足够细时黎曼和都趋于同一个数", "However the points are chosen, fine enough sums approach the same number"]])
