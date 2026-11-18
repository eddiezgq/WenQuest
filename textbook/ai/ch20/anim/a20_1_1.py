"""动画 20.1.1（配图 20.1.1）：晶体怎样变成一张图，以及这张图是谁定的。

四段：
1. 一排周期排列的原子——**周期边界**：最右边那个的邻居绕回到最左边；
2. 画一个**截断半径**，半径内连边——半径一变，图就完全不是同一张；
3. 两个**不同**的结构，所有原子对的距离一模一样：两体描述子看不见差别，
   补上三体（相邻两段的长短搭配）才分得开；
4. 接一段分子动力学：原子在势场里动起来，图随之不停重连——模型每一步都得重算。

渲染服务只允许 manim、wq_anim、numpy、math、random，不能 import 章内模块，
所以 code/_ch20.py 里要用到的那一点点在这里重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

L = 18                      # 周期
X0, SCALE, Y0 = -6.2, 0.70, 0.2
A_SITES = [0, 1, 4, 10, 12, 17]
B_SITES = [0, 1, 8, 11, 13, 17]


def px(u):
    """把周期坐标摆到画面上。"""
    return np.array([X0 + float(u) * SCALE, Y0, 0.0])


def sep(i, j):
    """周期最短像距离。"""
    d = abs(i - j) % L
    return min(d, L - d)


def dots(sites, color=STEEL, r=0.17):
    return VGroup(*[Dot(px(s), radius=r, color=color) for s in sites])


def rail(y=Y0):
    return Line([X0 - 0.6, y, 0], [X0 + L * SCALE + 0.2, y, 0],
                color=MUTED, stroke_width=2)


def bonds(sites, cutoff, color=YELLOW, width=3.0):
    """截断半径以内的边。绕回去的那几条画成弧，提醒它们走的是周期边界。"""
    g = VGroup()
    for a in range(len(sites)):
        for b in range(a + 1, len(sites)):
            d = sep(sites[a], sites[b])
            if d > cutoff:
                continue
            direct = abs(sites[a] - sites[b])
            if direct == d:
                g.add(Line(px(sites[a]), px(sites[b]), color=color, stroke_width=width))
            else:
                g.add(ArcBetweenPoints(px(sites[a]), px(sites[b]), angle=-TAU / 3,
                                       color=C_F, stroke_width=width))
    return g


def lj_force(x, box):
    """一维周期链上的 Lennard-Jones 力（只为动画好看，参数与算例一致的量级）。"""
    n = len(x)
    f = np.zeros(n)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = x[j] - x[i]
            d -= box * round(d / box)
            r = abs(d)
            if r < 1e-6 or r > 2.6:
                continue
            fr = 24 * (2 / r ** 13 - 1 / r ** 7)
            f[i] -= fr * np.sign(d)
    return f


class Lesson(Base):
    def construct(self):
        self.title("20.1", "晶体怎样变成一张图",
                   "How a crystal becomes a graph")

        # ---------------- 一、周期边界
        self.caption("晶体是周期的：一个胞里的原子，连同它在左右各个像里的副本",
                     "A crystal is periodic: atoms in one cell plus their periodic images",
                     wait=1.0)
        line = rail()
        atoms = dots(A_SITES)
        self.play(Create(line), FadeIn(atoms), run_time=1.0)

        ghost = VGroup(*[Dot(px(s - L), radius=0.13, color=NAVY) for s in A_SITES[-2:]],
                       *[Dot(px(s + L), radius=0.13, color=NAVY) for s in A_SITES[:2]])
        self.play(FadeIn(ghost), run_time=0.6)
        loop = ArcBetweenPoints(px(A_SITES[-1]), px(A_SITES[0]), angle=-TAU / 3,
                                color=C_F, stroke_width=3.5)
        self.play(Create(loop), run_time=0.8)
        self.caption("最右边那个的邻居绕回到最左边——周期边界不是装饰，它决定谁是邻居",
                     "The rightmost atom's neighbour wraps around to the left",
                     wait=1.6)
        self.play(FadeOut(ghost), FadeOut(loop), run_time=0.5)

        # ---------------- 二、截断半径一变，图就变
        self.caption("连边的规矩只有一条：距离小于截断半径就连",
                     "One rule for edges: connect whatever is closer than the cutoff",
                     wait=1.0)
        prev = bonds(A_SITES, 2)
        tag = zh("截断半径 2", 30, YELLOW).to_corner(UR, buff=0.7)
        self.play(Create(prev), FadeIn(tag), run_time=1.0)
        self.wait(0.8)

        for rc in (4, 6, 8):
            new = bonds(A_SITES, rc)
            new_tag = zh(f"截断半径 {rc}", 30, YELLOW).to_corner(UR, buff=0.7)
            self.play(Transform(prev, new), Transform(tag, new_tag), run_time=0.9)
            self.wait(0.5)
        n2, n8 = len(bonds(A_SITES, 2)), len(bonds(A_SITES, 8))
        self.caption(f"同一个晶体，截断从 2 到 8，边数从 {n2} 变成 {n8}——"
                     f"喂进模型的根本不是同一张图",
                     "Same crystal, different cutoff, a different graph goes into the model",
                     wait=2.0)
        self.play(FadeOut(prev), FadeOut(tag), run_time=0.5)
        self.clear_stage()

        # ---------------- 三、两个结构，距离一模一样
        self.caption("再看一件更要命的事：两个不同的结构，所有原子对的距离完全相同",
                     "Worse: two different structures with identical pair distances",
                     wait=1.2)
        top, bot = Y0 + 1.3, Y0 - 1.3
        la = Line([X0 - 0.6, top, 0], [X0 + L * SCALE + 0.2, top, 0],
                  color=MUTED, stroke_width=2)
        lb = Line([X0 - 0.6, bot, 0], [X0 + L * SCALE + 0.2, bot, 0],
                  color=MUTED, stroke_width=2)
        da = VGroup(*[Dot(px(s) + UP * 1.3, radius=0.17, color=STEEL) for s in A_SITES])
        db = VGroup(*[Dot(px(s) + DOWN * 1.3, radius=0.17, color=C_F) for s in B_SITES])
        name_a = zh("结构甲", 26, STEEL).next_to(la, LEFT, buff=0.15)
        name_b = zh("结构乙", 26, C_F).next_to(lb, LEFT, buff=0.15)
        self.play(Create(la), Create(lb), FadeIn(da), FadeIn(db),
                  FadeIn(name_a), FadeIn(name_b), run_time=1.2)

        counts = {}
        for sites in (A_SITES, B_SITES):
            key = tuple(sorted(sep(sites[i], sites[j])
                               for i in range(len(sites)) for j in range(i + 1, len(sites))))
            counts.setdefault(key, 0)
            counts[key] += 1
        same = len(counts) == 1
        txt = zh("两套距离：" + " ".join(str(d) for d in sorted(counts)[0]), 26, INK)
        txt.next_to(lb, DOWN, buff=0.8)
        self.play(FadeIn(txt), run_time=0.8)
        self.caption("两边数出来的距离，一个不多一个不少" if same else "（构造有误）",
                     "The two multisets of distances agree exactly", wait=1.8)
        self.caption("任何只看两体距离的描述子，对它们给出一模一样的输入——"
                     "模型不是学不会，是看不见",
                     "Any descriptor built only on pair distances sees them as the same",
                     wait=2.2)
        self.caption("补上三体信息（相邻两段的长短搭配），两者立刻分开",
                     "Add three-body information and they separate at once", wait=1.8)

        for sites, y, col in ((A_SITES, 1.3, STEEL), (B_SITES, -1.3, C_F)):
            tri = VGroup()
            for k in range(len(sites)):
                p, q, r = sites[k], sites[(k + 1) % len(sites)], sites[(k + 2) % len(sites)]
                tri.add(Line(px(p) + UP * y, px(q) + UP * y, color=col, stroke_width=3))
                tri.add(Line(px(q) + UP * y, px(r) + UP * y, color=YELLOW, stroke_width=2))
            self.play(Create(tri), run_time=0.9)
        self.wait(1.2)
        self.clear_stage()

        # ---------------- 四、动起来：图每一步都要重连
        self.caption("最后：原子不是钉死的。跑一段分子动力学，边随时在变",
                     "Finally: atoms move. Run molecular dynamics and the edges keep changing",
                     wait=1.2)
        line2 = rail()
        box = 12.0
        x = np.arange(10) * 1.2 + np.array([0.06, -0.05, 0.04, -0.03, 0.02,
                                            0.05, -0.04, 0.03, -0.02, 0.01])
        v = np.zeros(10)
        dt = 2e-3

        def to_screen(xs):
            return VGroup(*[Dot(np.array([X0 + float(u) / box * L * SCALE, Y0, 0.0]),
                                radius=0.16, color=STEEL) for u in xs])

        def md_bonds(xs, cutoff=1.6):
            g = VGroup()
            for i in range(len(xs)):
                for j in range(i + 1, len(xs)):
                    d = xs[j] - xs[i]
                    d -= box * round(d / box)
                    if abs(d) <= cutoff:
                        pa = np.array([X0 + float(xs[i]) / box * L * SCALE, Y0, 0.0])
                        pb = np.array([X0 + float(xs[j]) / box * L * SCALE, Y0, 0.0])
                        if abs(xs[i] - xs[j]) == abs(d):
                            g.add(Line(pa, pb, color=YELLOW, stroke_width=3))
            return g

        pts, bnd = to_screen(x), md_bonds(x)
        self.play(Create(line2), FadeIn(pts), Create(bnd), run_time=1.0)
        f = lj_force(x, box)
        for _ in range(26):
            for _ in range(40):
                vh = v + 0.5 * dt * f
                x = (x + dt * vh) % box
                f = lj_force(x, box)
                v = vh + 0.5 * dt * f
            self.play(Transform(pts, to_screen(x)), Transform(bnd, md_bonds(x)),
                      run_time=0.16)

        self.card(["每一步都要重新连边、重新算一遍能量与力",
                   "所以势必须算得又快又像——这正是机器学习势要解决的事"], wait=3.0)
