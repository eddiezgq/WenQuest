"""动画 18.2.1（配图 18.2.1）：一条序列是怎样被折起来的——接触图把搜索空间一层层收紧。

三步：
1. 一条链在格点上可以有**很多种**折法（16 个残基就有一百多万种）；
2. 每给一条**正确**的接触，还剩的折法就少一个量级；
3. 可接触信息也很脆：**四条里混进一条错的，基态直接被排除在外**。

画面上的数都是现算的。渲染服务只允许 manim、wq_anim、numpy、math、random，不能 import
章内模块，所以这里按 code/_ch18.py 的同一套做法把最小的一份重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

SEQ = "HPHPHPHHHPHPPHPH"
N = len(SEQ)
MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def enumerate_folds(n):
    """枚举全部自回避走法。用字典标记"走过没有"，不做集合的增删（渲染沙箱不让用 .remove）。"""
    out = []
    seen = {(0, 0): True, (1, 0): True}

    def rec(path):
        if len(path) == n:
            out.append(tuple(path))
            return
        x, y = path[-1]
        for dx, dy in MOVES:
            p = (x + dx, y + dy)
            if seen.get(p):
                continue
            seen[p] = True
            path.append(p)
            rec(path)
            path.pop()
            seen[p] = False

    rec([(0, 0), (1, 0)])
    return out


def contacts(path):
    pos = {p: i for i, p in enumerate(path)}
    out = {}
    for i, (x, y) in enumerate(path):
        for dx, dy in ((1, 0), (0, 1)):
            j = pos.get((x + dx, y + dy))
            if j is not None and abs(j - i) > 1:
                out[(min(i, j), max(i, j))] = True
    return frozenset(out)


def energy(path):
    return -sum(1 for i, j in contacts(path) if SEQ[i] == "H" and SEQ[j] == "H")


FOLDS = enumerate_folds(N)
CS = [contacts(f) for f in FOLDS]
ES = np.array([energy(f) for f in FOLDS])
NATIVE_IDX = int(np.argmin(ES))
NATIVE = CS[NATIVE_IDX]
NAT_PAIRS = sorted(NATIVE)


def draw(path, scale=0.42, color_h=YELLOW, color_p=BLUE):
    """把一条走法画成格点上的链。"""
    pts = np.array([[x, y, 0] for x, y in path], dtype=float) * scale
    pts -= pts.mean(0)
    g = VGroup()
    for a, b in zip(pts[:-1], pts[1:]):
        g.add(Line(a, b, stroke_width=3, color=GREY_B))
    for p, ch in zip(pts, SEQ):
        g.add(Dot(p, radius=0.085, color=color_h if ch == "H" else color_p))
    return g


class Lesson(Base):
    def construct(self):
        self.title("18.2", "一条序列怎么折起来：接触图把搜索空间一层层收紧",
                   "How a chain folds: contacts shrink the search, one at a time")

        # ---------------- 一、折法多得吓人
        picks = [FOLDS[i] for i in (3, 1200, 40000, 300000, 900000, NATIVE_IDX)]
        grid = VGroup(*[draw(p) for p in picks]).arrange_in_grid(2, 3, buff=0.9)
        fit(grid, width=10.0)
        grid.move_to([0, -0.3, 0])
        self.play(LaggedStart(*[FadeIn(m) for m in grid], lag_ratio=0.15), run_time=2.0)
        self.caption(f"{N} 个残基的一条链，在格点上有 {len(FOLDS):,} 种折法——黄点疏水、蓝点亲水",
                     f"A {N}-residue chain has {len(FOLDS):,} ways to fold; "
                     f"yellow = hydrophobic, blue = polar")
        self.caption("真蛋白的折法比这多得多，所以'全都试一遍'从一开始就不是办法",
                     "A real protein has vastly more; enumerating them was never an option")
        self.clear_stage()

        # ---------------- 二、一条接触少一个量级
        left = VGroup()
        bars = VGroup()
        counts = []
        for k in range(0, 5):
            known = set(NAT_PAIRS[:k])
            n_left = sum(1 for c in CS if known <= c)
            counts.append(n_left)
        base = counts[0]
        for k, n_left in enumerate(counts):
            h = max(0.18, 3.4 * np.log10(max(n_left, 1.2)) / np.log10(base))
            r = Rectangle(width=0.8, height=h, color=BLUE, fill_opacity=0.65)
            r.move_to([-4.2 + 1.7 * k, -1.9 + h / 2, 0])
            lab = Text(f"{n_left:,}", font_size=20).next_to(r, UP, buff=0.12)
            num = Text(f"{k}", font_size=22, color=GREY).next_to(r, DOWN, buff=0.15)
            bars.add(VGroup(r, lab, num))
        axis_zh = zh("给了几条正确的接触", size=24).move_to([0, -2.75, 0])
        self.play(LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in bars], lag_ratio=0.25),
                  *[FadeIn(b[1]) for b in bars], *[FadeIn(b[2]) for b in bars],
                  FadeIn(axis_zh), run_time=2.4)
        self.caption(f"每给一条正确的接触，还剩的折法就少一个量级："
                     f"{counts[0]:,} → {counts[1]:,} → {counts[2]:,} → {counts[3]:,} → {counts[4]:,}",
                     f"Each correct contact removes about an order of magnitude: "
                     f"{counts[0]:,} → {counts[1]:,} → {counts[2]:,} → {counts[3]:,} → {counts[4]:,}")
        self.caption("这就是共进化信息的价值——它不直接给结构，它把搜索空间砍掉",
                     "That is what co-evolution buys: not the structure itself, but a much smaller search")
        self.clear_stage()

        # ---------------- 三、错一条就全毁
        known_ok = set(NAT_PAIRS[:4])
        ok_idx = [i for i, c in enumerate(CS) if known_ok <= c]
        all_pairs = [(i, j) for i in range(N) for j in range(i + 2, N)]
        # 挑一条"看起来最像真的"错接触：它留下的折法最多，所以最不容易被发现
        best_bad, bad_idx = None, []
        for p in all_pairs:
            if p in NATIVE:
                continue
            idx = [i for i, c in enumerate(CS) if (set(NAT_PAIRS[:3]) | {p}) <= c]
            if len(idx) > len(bad_idx):
                best_bad, bad_idx = p, idx
        bad = best_bad
        lo = int(ES.min())
        ok_best = int(min(ES[i] for i in ok_idx))
        bad_best = int(min(ES[i] for i in bad_idx)) if bad_idx else 0

        gl = VGroup(*[draw(FOLDS[i], scale=0.36) for i in ok_idx[:6]]).arrange_in_grid(2, 3, buff=0.55)
        gr = VGroup(*[draw(FOLDS[i], scale=0.36) for i in bad_idx[:6]]).arrange_in_grid(2, 3, buff=0.55)
        fit(gl, width=5.0); fit(gr, width=5.0)
        gl.move_to([-3.3, -0.5, 0]); gr.move_to([3.3, -0.5, 0])
        hl = bi(("四条都对", "four correct"), size=26).next_to(gl, UP, buff=0.3)
        hr = bi(("其中一条是错的", "one of them wrong"), size=26, color=RED).next_to(gr, UP, buff=0.3)
        self.play(FadeIn(gl), FadeIn(hl), run_time=1.0)
        self.play(FadeIn(gr), FadeIn(hr), run_time=1.0)
        self.caption(f"四条都对：还剩 {len(ok_idx)} 种，其中最低能量 {ok_best}，正是基态",
                     f"All four correct: {len(ok_idx)} folds left, best energy {ok_best} — the ground state")
        self.caption(f"错一条：只剩 {len(bad_idx)} 种，最低能量只有 {bad_best}——基态被排除在外了",
                     f"One wrong: only {len(bad_idx)} left, best energy {bad_best} — "
                     f"the ground state is not among them")
        self.clear_stage()

        self.card([("接触信息又强又脆", "Contact restraints: powerful and brittle"),
                   ("一条正确的接触，把搜索空间砍掉一个量级",
                    "One correct contact cuts the search space by an order of magnitude"),
                   ("一条错的接触，把正确答案直接排除在外",
                    "One wrong contact removes the right answer altogether"),
                   ("所以比对深度要紧：浅比对给出的接触，错得比对得多",
                    "Hence alignment depth matters: a shallow alignment gets more contacts wrong than right")])
