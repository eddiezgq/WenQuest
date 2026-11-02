"""动画 23.2.1（配图 23.2.1）：调和级数为什么发散——砖块悬挑越堆越远。每在最下面垫一块砖，上面整摞向外再伸出 1/(2n)，
总悬挑 Hₙ/2 没有上限，只是增长得越来越慢。"""
from manim import *
from wq_anim import *
import numpy as np

L = 1.8          # 砖长（屏幕单位）
HB = 0.34        # 砖高
EDGE = -1.6      # 桌边的 x
TOP = -2.4       # 桌面的 y
N = 10


def layout(n):
    """n 块砖时，自上而下第 j 块（j = 1..n）的右端相对桌边的伸出量（以砖长计）与高度层。"""
    res = []
    for j in range(1, n + 1):
        over = sum(1 / (2 * i) for i in range(j, n + 1))
        res.append((over, n - j))            # 层号：0 是最下面
    return res


class Lesson(Base):
    def construct(self):
        self.title("23.2", "调和级数为什么发散：砖块悬挑", "Why the harmonic series diverges: overhanging bricks")
        table = Rectangle(width=5.0, height=0.5, fill_color=GREY_D, fill_opacity=1, stroke_width=0).move_to([EDGE - 2.5, TOP - 0.25, 0])
        edge = DashedLine([EDGE, TOP, 0], [EDGE, 2.2, 0], color=GREY_B, stroke_width=1.5)
        self.play(FadeIn(table), Create(edge))
        self.caption("一样长的砖，一块块叠在桌边，最远能伸出去多少？", "Identical bricks stacked at a table edge: how far can they reach?", wait=0.5)
        colors = [ORANGE, BLUE_C]
        bricks = []

        def place(n):
            rects = []
            for j, (over, lev) in enumerate(layout(n), start=1):
                x_right = EDGE + over * L
                r = Rectangle(width=L, height=HB * 0.94, fill_color=colors[j % 2], fill_opacity=0.85, stroke_color=WHITE, stroke_width=1)
                r.move_to([x_right - L / 2, TOP + HB * (lev + 0.5), 0])
                rects.append(r)
            return rects

        lab = None
        for n in range(1, N + 1):
            new = place(n)
            total = sum(1 / (2 * i) for i in range(1, n + 1))
            txt = VGroup(MathTex(rf"n = {n}", font_size=34),
                         MathTex(rf"\text{{overhang}} = \tfrac12 H_{{{n}}} \approx {total:.3f}\,L", font_size=34)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR).shift(DOWN * 1.1 + LEFT * 0.3)
            if n == 1:
                self.play(*[FadeIn(r) for r in new], FadeIn(txt))
                self.caption("一块砖：重心恰在桌边，最多伸出半块", "One brick: centre of mass at the edge, overhang 1/2", wait=0.8)
            else:
                anims = [Transform(bricks[k], new[k]) for k in range(n - 1)] + [FadeIn(new[n - 1], shift=UP * 0.2), Transform(lab, txt)]
                self.play(*anims, run_time=0.9 if n > 3 else 1.4)
                if n == 2:
                    self.caption("在下面垫一块：上面整摞再伸出 1/4", "Slip one underneath: the stack moves out another 1/4", wait=0.6)
                if n == 3:
                    self.caption("第 n 块让总悬挑再加 1/(2n)：上面 n − 1 块的重心落在它的边上", "The n-th brick adds 1/(2n): the upper stack's centre of mass sits on its edge", wait=0.8)
                if n == 4:
                    self.caption("4 块砖：最上面一块已经完全伸出桌边", "Four bricks: the top one is entirely beyond the table", wait=1.0)
            if n == 1:
                bricks = list(new)
                lab = txt
            else:
                bricks.append(new[n - 1])
        com = Dot([EDGE, TOP + HB * N / 2, 0], color=RED, radius=0.08)
        coml = Text("整摞的重心 centre of mass", font_size=18, color=RED).next_to(com, LEFT, buff=0.15)
        self.play(FadeIn(com), FadeIn(coml))
        self.caption("整摞砖的重心正好在桌边上：再多伸一点就倒", "The whole stack's centre of mass is exactly over the edge", wait=1.0)
        self.play(*[FadeOut(m) for m in bricks + [table, edge, com, coml, lab]])
        # 悬挑与 n 的关系
        ax = Axes(x_range=[0, 6, 1], y_range=[0, 7, 1], x_length=9, y_length=4.4, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(DOWN * 0.5)
        xl = MathTex(r"\log_{10} n", font_size=28).next_to(ax.x_axis, RIGHT, buff=0.1)
        yl = MathTex(r"\tfrac12 H_n\ (\text{brick lengths})", font_size=26).next_to(ax.y_axis, UP, buff=0.1)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        xs = np.linspace(0, 6, 200)
        curve = ax.plot_line_graph(xs, [0.5 * (np.log(10 ** x) + 0.5772 + 1 / (2 * 10 ** x)) for x in xs], add_vertex_dots=False, line_color=YELLOW, stroke_width=4)
        self.play(Create(curve), run_time=2)
        pts = [(4, 1), (31, 2), (227, 3), (12367, 5)]
        dots = VGroup()
        for n_, v in pts:
            d = Dot(ax.c2p(np.log10(n_), v), color=RED)
            t = Text(f"{n_}", font_size=20, color=RED).next_to(d, UP + LEFT * 0.3, buff=0.08)
            dots.add(d, t)
        self.play(FadeIn(dots))
        self.caption("伸出 1、2、3、5 块长，分别要 4、31、227、12367 块砖", "Reaching 1, 2, 3, 5 lengths takes 4, 31, 227, 12367 bricks", wait=1.2)
        self.caption("增长极慢，却没有上限：调和级数发散", "Growth is glacial but unbounded: the harmonic series diverges", wait=1.2)
        self.play(*[FadeOut(m) for m in (ax, xl, yl, curve, dots)])
        self.card([["调和级数发散", "The harmonic series diverges"],
                   MathTex(r"\tfrac12 H_n=\tfrac12\Bigl(1+\tfrac12+\cdots+\tfrac1n\Bigr)\approx\tfrac12(\ln n+\gamma)\to\infty", font_size=40),
                   ["每一项都趋于 0，和却没有上限；悬挑只是对数式地增长", "Every term tends to 0, yet the sum is unbounded; the overhang grows only logarithmically"]])
