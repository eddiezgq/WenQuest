"""动画 25.2.1（配图 25.2.1）：两台搬运车在窄道上，从死锁到让行。

五段：
1. 一座车间，中间一排货架只留两个口。两台搬运车各走自己的最短路——**一定会在窄道上撞**；
   两种撞法：**换位冲突**（在窄道里对穿）与**点冲突**（同一刻踩同一个格子）；
2. 按优先级让行：谁先谁后定下来就有可行解，但让的那一台要**多走**；
3. 冲突搜索：同一个实例的**已证明最优解**便宜得多——而且它与“各走各的”那个**下界**只差几步，
   这几步就是“协调”本身的价钱；
4. 四行并排的报表：代价、makespan、冲突、是不是可行解、跟谁比的；
5. 最后一句：**makespan 与 sum-of-costs 是两种成本，会给出不同的选择**——
   一个偏好“等一等”，一个偏好“绕一绕”。

渲染服务只允许 manim、wq_anim、numpy、math、random，所以地图、A\\*、优先级法与
联合空间穷举都在这里重写一遍，口径与 `code/_ch25.py` 相同（等待也算一步；
点冲突、换位冲突两种都算；sum-of-costs 逐车累加，makespan 取最后一台）。
"""
from manim import *
from wq_anim import *

# 车间网格：与算例同一座车间（`#` 货架、`.` 通道、`C` 充电位）。
# 第 5 行只有第 3、9 两个口，这就是本片讲的**窄道**。
GRID = (
    "#############",
    "#C.........C#",
    "#.###.###.#.#",
    "#.###.###.#.#",
    "#...........#",
    "###.#####.###",
    "#...........#",
    "#.###.###.#.#",
    "#.###.###.#.#",
    "#C.........C#",
    "#############",
)
H, W = len(GRID), len(GRID[0])
FREE = frozenset((r, c) for r in range(H) for c in range(W) if GRID[r][c] != "#")
GATE = (5, 9)                      # 本片用右边那个口
STEP = (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)       # 第一个是等待动作

# 两台搬运车：0 号从下半间去右上角，1 号从上半间去下半间，都要过这个口。
S0, G0 = [(6, 10), (4, 9)], [(2, 11), (8, 9)]          # 换位冲突（在窄道里对穿）
S1, G1 = [(6, 10), (3, 9)], [(2, 11), (8, 9)]          # 点冲突（同一刻踩同一格）
# 第五段用算例 25.3 的那个实例：一台近、一台远，两种成本给出不同的选择。
S2, G2 = [(4, 6), (3, 5)], [(5, 3), (9, 11)]


def nbrs(cell):
    out = []
    for dr, dc in STEP:
        nb = (cell[0] + dr, cell[1] + dc)
        if nb in FREE:
            out.append(nb)
    return out


FIELDS = {}


def field(target):
    """从 target 出发的广度优先距离场：单机最短步数的真值。"""
    if target not in FIELDS:
        d, frontier = {target: 0}, [target]
        while frontier:
            nxt = []
            for cur in frontier:
                for nb in nbrs(cur):
                    if nb != cur and nb not in d:
                        d[nb] = d[cur] + 1
                        nxt.append(nb)
            frontier = nxt
        FIELDS[target] = d
    return FIELDS[target]


def dist(a, b):
    return field(b).get(a, 10 ** 6)


def shortest(start, goal):
    """单机最短路：顺着距离场下坡走，不含等待。"""
    fld = field(goal)
    path, cur = [start], start
    while cur != goal:
        best = None
        for nb in nbrs(cur):
            if nb != cur and (best is None or fld.get(nb, 10 ** 6) < fld.get(best, 10 ** 6)):
                best = nb
        cur = best
        path.append(cur)
    return path


def at(path, t):
    """第 t 步在哪：到了目标就停在目标上。"""
    return path[t] if t < len(path) else path[-1]


def conflicts(paths):
    """(类型, 格子或格子对, 时刻)：点冲突 = 同刻同格；换位冲突 = 一步之内互换位置。"""
    out, span = [], max(len(p) for p in paths)
    for t in range(span):
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                pi, pj = at(paths[i], t), at(paths[j], t)
                if pi == pj:
                    out.append(("vertex", pi, t))
                if t > 0:
                    qi, qj = at(paths[i], t - 1), at(paths[j], t - 1)
                    if pi == qj and pj == qi and pi != pj:
                        out.append(("edge", (qi, pi), t))
    return out


def soc(paths):
    """sum-of-costs：逐车“到达目标所需的时间步数”之和。"""
    return int(sum(len(p) - 1 for p in paths))


def mkspan(paths):
    """makespan：最后一台车到达目标的时刻。"""
    return int(max(len(p) - 1 for p in paths))


def trim(paths):
    out = []
    for p in paths:
        k = len(p) - 1
        while k > 0 and p[k] == p[k - 1]:
            k -= 1
        out.append(p[:k + 1])
    return out


def profile(paths, starts, goals):
    """每台车的 (代价, 比最短路多绕的步数, 原地等待的步数)。"""
    out = []
    for i, p in enumerate(paths):
        moves = sum(1 for t in range(1, len(p)) if p[t] != p[t - 1])
        out.append((len(p) - 1, int(moves - dist(starts[i], goals[i])), (len(p) - 1) - moves))
    return out


def pop_min(buckets, lo):
    """桶队列：代价都是小整数，按 f 值分桶取最小，不用 heapq。"""
    while lo < len(buckets) and not buckets[lo]:
        lo += 1
    return (buckets[lo].pop(), lo) if lo < len(buckets) else (None, lo)


def st_plan(start, goal, vcons, econs, horizon):
    """时空 A\\*：在给定的时空预留表下为一台车规划，**含等待动作**（等待也算一步）。"""
    last = 0
    for cell, t in vcons:
        if cell == goal and t > last:
            last = t
    cap = horizon + 4
    buckets = [[] for _ in range(cap * 3)]
    h0 = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
    buckets[h0].append((start, 0))
    came, seen, lo = {}, {(start, 0): True}, h0
    while True:
        item, lo = pop_min(buckets, lo)
        if item is None:
            return []
        cell, t = item
        if cell == goal and t >= last:
            path, key = [cell], (cell, t)
            while key in came:
                key = came[key]
                path.append(key[0])
            path.reverse()
            return path
        if t >= horizon:
            continue
        for nb in nbrs(cell):
            if (nb, t + 1) in vcons or (cell, nb, t + 1) in econs:
                continue
            if (nb, t + 1) in seen:
                continue
            seen[(nb, t + 1)] = True
            came[(nb, t + 1)] = (cell, t)
            f = t + 1 + abs(nb[0] - goal[0]) + abs(nb[1] - goal[1])
            buckets[min(f, len(buckets) - 1)].append((nb, t + 1))


def prioritized(starts, goals, order):
    """优先级法：按给定顺序逐车规划，后面的车把前面的车当时空障碍（含它停在目标上的那段）。"""
    horizon = int(sum(dist(s, g) for s, g in zip(starts, goals)) + 2 * len(starts) + 12)
    done, out = [], {}
    for k in order:
        vcons, econs = set(), set()
        for p in done:
            for t in range(horizon + 1):
                vcons.add((at(p, t), t))
                if t > 0:
                    econs.add((at(p, t), at(p, t - 1), t))
        p = st_plan(starts[k], goals[k], vcons, econs, horizon)
        if not p:
            return []
        done.append(p)
        out[k] = p
    return [out[i] for i in range(len(starts))]


def joint_optimal(starts, goals, metric):
    """联合状态空间里穷举出**已证明最优解**（A\\*，启发函数可采纳）。

    * metric="soc"：一步的代价 = 还没停在自己目标上的车数；启发 = 各车最短步数之和；
    * metric="makespan"：一步的代价恒为 1；启发 = 各车最短步数的最大值。
    """
    n = len(starts)
    start, goal = tuple(starts), tuple(goals)
    flds = [field(g) for g in goals]

    def h(state):
        ds = [flds[i].get(state[i], 10 ** 6) for i in range(n)]
        return sum(ds) if metric == "soc" else max(ds)

    cap = 400
    buckets = [[] for _ in range(cap)]
    buckets[min(h(start), cap - 1)].append(start)
    best, came, lo = {start: 0}, {}, min(h(start), cap - 1)
    while True:
        state, lo = pop_min(buckets, lo)
        if state is None:
            return None, None
        if state == goal:
            seq = [state]
            while state in came:
                state = came[state]
                seq.append(state)
            seq.reverse()
            return trim([[s[i] for s in seq] for i in range(n)]), best[goal]
        gc = best[state]
        opts = [nbrs(state[i]) for i in range(n)]
        stack = [()]
        for i in range(n):
            stack = [tup + (c,) for tup in stack for c in opts[i]]
        for nxt in stack:
            if len(set(nxt)) != n:
                continue                                   # 点冲突
            swap = False
            for i in range(n):
                for j in range(i + 1, n):
                    if nxt[i] == state[j] and nxt[j] == state[i]:
                        swap = True
            if swap:                                       # 换位冲突
                continue
            if metric == "soc":
                step = sum(0 if (state[i] == goals[i] and nxt[i] == goals[i]) else 1
                           for i in range(n))
            else:
                step = 1
            ng = gc + step
            if ng < best.get(nxt, 10 ** 9):
                best[nxt] = ng
                came[nxt] = state
                buckets[min(ng + h(nxt), cap - 1)].append(nxt)


# --------------------------------------------------------------- 画面


# 版面：车间画在左边，读数与报表放右边，标题在左上角、字幕在底下，互不压盖。
CELL = 0.38
X0, Y0 = -W * CELL / 2.0 - 3.2, H * CELL / 2.0 - 0.35
PANEL = 7.0                        # 右边那一栏能用的宽度


def pos(cell, dy=0.0):
    """格子中心在画面里的坐标（行从上往下数）。"""
    return np.array([X0 + (cell[1] + 0.5) * CELL,
                     Y0 - (cell[0] + 0.5) * CELL + dy, 0.0])


def board(dy=0.0):
    """画车间：货架实心、通道空心、窄道那个口圈出来。"""
    g = VGroup()
    for r in range(H):
        for c in range(W):
            if (r, c) in FREE:
                g.add(Square(CELL, color=NAVY, fill_opacity=0.0, stroke_width=1.2)
                      .move_to(pos((r, c), dy)))
            else:
                g.add(Square(CELL, color=NAVY, fill_color=NAVY, fill_opacity=1.0,
                             stroke_width=0.6).move_to(pos((r, c), dy)))
    g.add(Square(CELL * 1.02, color=YELLOW, stroke_width=3).move_to(pos(GATE, dy)))
    return g


def trace(path, color, dy=0.0):
    """一条路径画成折线（等待的那几步画不出来，所以读表看等待列）。"""
    pts = [pos(p, dy) for p in path]
    keep = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - keep[-1][0]) + abs(p[1] - keep[-1][1]) > 1e-6:
            keep.append(p)
    return VMobject(color=color, stroke_width=4).set_points_as_corners(keep) \
        if len(keep) > 1 else Dot(keep[0], radius=0.01, color=color)


class Lesson(Base):
    def construct(self):
        self.title("25.2", "两台车在窄道上：从死锁到让行",
                   "Two AGVs in a doorway: from deadlock to giving way")

        lb = int(sum(dist(s, g) for s, g in zip(S0, G0)))
        ind = [shortest(s, g) for s, g in zip(S0, G0)]
        cf = conflicts(ind)
        ind1 = [shortest(s, g) for s, g in zip(S1, G1)]
        cf1 = conflicts(ind1)
        pri = trim(prioritized(S0, G0, [0, 1]))
        opt, opt_cost = joint_optimal(S0, G0, "soc")

        # ---------------- 一、各走各的一定撞
        self.caption("一座车间，中间一排货架只留两个口。两台搬运车各走自己的最短路",
                     "One hall, one doorway: each AGV takes its own shortest path",
                     wait=1.4)
        bd = board()
        self.play(Create(bd), run_time=1.2)
        d0 = Dot(pos(S0[0]), radius=CELL * 0.33, color=STEEL)
        d1 = Dot(pos(S0[1]), radius=CELL * 0.33, color=C_F)
        m0 = Square(CELL * 0.6, color=STEEL, stroke_width=3).move_to(pos(G0[0]))
        m1 = Square(CELL * 0.6, color=C_F, stroke_width=3).move_to(pos(G0[1]))
        lab = VGroup(zh(f"0 号车要走 {dist(S0[0], G0[0])} 步（蓝）", 24, STEEL),
                     zh(f"1 号车要走 {dist(S0[1], G0[1])} 步（红）", 24, C_F),
                     zh("黄圈就是那个口；方框是各自的目标", 24, MUTED),
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        lab = fit(lab, PANEL).next_to(bd, RIGHT, buff=0.35)
        self.play(FadeIn(d0), FadeIn(d1), Create(m0), Create(m1), FadeIn(lab), run_time=1.0)
        self.play(Create(trace(ind[0], STEEL)), Create(trace(ind[1], C_F)), run_time=1.2)
        self.caption("两条最短路都要穿这个口——它们要在口子里对穿",
                     "Both shortest paths cross the doorway, in opposite directions",
                     wait=1.6)
        for t in range(1, 3):
            self.play(d0.animate.move_to(pos(at(ind[0], t))),
                      d1.animate.move_to(pos(at(ind[1], t))), run_time=0.7)
        flash = Square(CELL * 1.1, color=YELLOW, fill_color=C_F, fill_opacity=0.35,
                       stroke_width=4).move_to(pos(GATE))
        self.play(FadeIn(flash), run_time=0.5)
        self.caption(f"换位冲突：一步之内两台车互换了位置（第 {cf[0][2]} 步，就在口子上）"
                     f"——现实里这就是对撞",
                     "An edge (swap) conflict: the two exchange places in one step — a head-on crash",
                     wait=2.0)
        self.play(FadeOut(flash), run_time=0.4)
        self.caption("把 1 号车挪远一格，撞法就换了一种",
                     "Move the second AGV one cell further back and the conflict changes kind",
                     wait=1.2)
        self.play(d0.animate.move_to(pos(S1[0])), d1.animate.move_to(pos(S1[1])), run_time=0.8)
        for t in range(1, 3):
            self.play(d0.animate.move_to(pos(at(ind1[0], t))),
                      d1.animate.move_to(pos(at(ind1[1], t))), run_time=0.7)
        flash2 = Square(CELL * 1.1, color=YELLOW, fill_color=C_F, fill_opacity=0.35,
                        stroke_width=4).move_to(pos(GATE))
        self.play(FadeIn(flash2), run_time=0.5)
        self.caption(f"点冲突：同一刻两台车踩同一个格子（第 {cf1[0][2]} 步）。"
                     f"两种冲突都要查——只查一种，另一种就漏过去了",
                     "A vertex conflict: both occupy the same cell at the same tick. "
                     "Both kinds have to be checked",
                     wait=2.2)
        self.clear_stage()

        # ---------------- 二、按优先级让行：可行，但要多走
        self.caption("最省事的办法：定个先后。谁优先谁照走，另一台把它当障碍让开",
                     "The cheapest fix: fix an order. The first keeps its plan, the second gives way",
                     wait=1.6)
        bd = board()
        d0 = Dot(pos(S0[0]), radius=CELL * 0.33, color=STEEL)
        d1 = Dot(pos(S0[1]), radius=CELL * 0.33, color=C_F)
        self.play(Create(bd), FadeIn(d0), FadeIn(d1), run_time=1.0)
        self.play(Create(trace(pri[0], STEEL)), Create(trace(pri[1], C_F)), run_time=1.2)
        for t in range(1, mkspan(pri) + 1):
            self.play(d0.animate.move_to(pos(at(pri[0], t))),
                      d1.animate.move_to(pos(at(pri[1], t))), run_time=0.34)
        prof = profile(pri, S0, G0)
        gap = (soc(pri) / opt_cost - 1) * 100
        box = VGroup(
            zh(f"可行：冲突 {len(conflicts(pri))} 处", 24, INK),
            zh(f"总行程 sum-of-costs = {soc(pri)} 步，makespan = {mkspan(pri)} 步", 24, INK),
            zh(f"让行的那台多绕了 {prof[1][1]} 步、等了 {prof[1][2]} 步", 24, YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        box = fit(box, PANEL).next_to(bd, RIGHT, buff=0.35)
        self.play(FadeIn(box), run_time=1.0)
        self.caption(f"让行是可行的，代价是让的那一台要多走——这个实例上比最优贵 {gap:.1f}%；"
                     f"算例里四台车时是 12.1%—66.7%（二十四种顺序全试过）",
                     f"Giving way works, but the one that yields pays for it: "
                     f"+{gap:.0f}% over the optimum here, and 12.1%—66.7% in the chapter's "
                     f"four-AGV case",
                     wait=2.4)
        self.clear_stage()

        # ---------------- 三、冲突搜索：穷举证明的最优
        self.caption("换一种做法：谁都不先定，只在撞上的那一刻加一条约束，再分两支往下搜",
                     "Instead: fix no order, add one constraint at the conflict and branch",
                     wait=1.8)
        bd = board()
        d0 = Dot(pos(S0[0]), radius=CELL * 0.33, color=STEEL)
        d1 = Dot(pos(S0[1]), radius=CELL * 0.33, color=C_F)
        self.play(Create(bd), FadeIn(d0), FadeIn(d1), run_time=1.0)
        self.play(Create(trace(opt[0], STEEL)), Create(trace(opt[1], C_F)), run_time=1.2)
        for t in range(1, mkspan(opt) + 1):
            self.play(d0.animate.move_to(pos(at(opt[0], t))),
                      d1.animate.move_to(pos(at(opt[1], t))), run_time=0.34)
        po = profile(opt, S0, G0)
        box = VGroup(
            zh(f"总行程 {opt_cost} 步——穷举证明的最优，不是“最好已知解”", 24, YELLOW),
            zh(f"下界（各走各的、不管撞不撞）：{lb} 步", 24, MUTED),
            zh(f"协调的代价 = {opt_cost - lb} 步（算例里四台车时是 5 步）", 24, INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        box = fit(box, PANEL).next_to(bd, RIGHT, buff=0.35)
        self.play(FadeIn(box), run_time=1.0)
        self.caption(f"这一台只侧身让了 {po[0][1]} 步，另一台一步没停。"
                     f"“下界”不是解，“已证明最优”才是——两者不许混为一谈",
                     "One steps aside, the other never stops. A lower bound is not a solution, "
                     "and a proven optimum is not a best-known one",
                     wait=2.4)
        self.clear_stage()

        # ---------------- 四、报表：四行并排
        self.caption("成绩要这么报：代价、makespan、冲突、是不是可行解、跟谁比的",
                     "Report it in five columns: cost, makespan, conflicts, feasible, compared with what",
                     wait=1.6)
        rows = [("各走各的（独立最短路）", soc(ind), mkspan(ind), len(cf), "不可行", "= 下界"),
                ("按优先级让行", soc(pri), mkspan(pri), len(conflicts(pri)), "可行",
                 f"+{gap:.1f}% 对最优"),
                ("冲突搜索 / 穷举", opt_cost, mkspan(opt), len(conflicts(opt)), "可行",
                 "已证明最优")]
        head = zh("每一行的五列：总行程 / makespan / 冲突 / 可行 / 跟谁比", 24, MUTED)
        lines = [head]
        for name, a, b, c, ok, cmp_ in rows:
            col = C_F if ok == "不可行" else (YELLOW if "最优" in cmp_ else INK)
            lines.append(zh(f"{name}：{a} 步 / {b} 步 / {c} 处 / {ok} / {cmp_}", 26, col))
        tab = fit(VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.22), 12.6)
        self.play(LaggedStart(*[FadeIn(m) for m in lines], lag_ratio=0.3), run_time=2.0)
        self.caption("第一行最便宜，可它不是解——便宜是因为它会撞。"
                     "所以“比独立规划多花了多少”，问的就是“协调要花多少”",
                     "The cheapest row is not a solution at all: it is cheap because it crashes",
                     wait=2.4)
        self.play(FadeOut(tab), run_time=0.6)

        # ---------------- 五、两种成本会给出不同的选择
        self.caption("最后一件事：“总行程”与“最后一台几点到”是两种成本，"
                     "它们会给出不同的选择",
                     "One last thing: sum-of-costs and makespan are two different costs",
                     wait=1.8)
        p_soc, c_soc = joint_optimal(S2, G2, "soc")
        p_mk, c_mk = joint_optimal(S2, G2, "makespan")
        bd = board()
        e0 = Dot(pos(S2[0]), radius=CELL * 0.33, color=STEEL)
        e1 = Dot(pos(S2[1]), radius=CELL * 0.33, color=C_F)
        self.play(Create(bd), FadeIn(e0), FadeIn(e1), run_time=1.0)
        note = VGroup(zh(f"一台只要走 {dist(S2[0], G2[0])} 步（近）", 24, STEEL),
                      zh(f"一台要走 {dist(S2[1], G2[1])} 步（远）", 24, C_F),
                      zh("近的那台有富余时间，远的那台没有", 24, MUTED),
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        note = fit(note, PANEL).next_to(bd, RIGHT, buff=0.35)
        self.play(FadeIn(note), run_time=0.8)
        t_soc = trace(p_soc[0], STEEL)
        t_soc1 = trace(p_soc[1], C_F)
        self.play(Create(t_soc), Create(t_soc1), run_time=1.2)
        pw = profile(p_soc, S2, G2)
        self.caption(f"按 sum-of-costs 最优（{c_soc} 步）：让远的那台原地等 "
                     f"{sum(x[2] for x in pw)} 步，一步不绕——等只记在等的那台头上",
                     f"The sum-of-costs optimum ({c_soc}) waits: a wait is charged only to the one waiting",
                     wait=2.2)
        self.play(FadeOut(t_soc), FadeOut(t_soc1), run_time=0.5)
        t_mk = trace(p_mk[0], STEEL)
        t_mk1 = trace(p_mk[1], C_F)
        self.play(Create(t_mk), Create(t_mk1), run_time=1.2)
        pd = profile(p_mk, S2, G2)
        self.caption(f"按 makespan 最优（{c_mk} 步）：让近的那台绕 "
                     f"{sum(max(x[1], 0) for x in pd)} 步——它反正早到，绕路对它是白送的",
                     f"The makespan optimum ({c_mk}) takes a detour instead: "
                     f"the early one has time to spare",
                     wait=2.4)
        self.caption(f"同一个实例、同一套算法，两种成本一个说“等”、一个说“绕”，"
                     f"总行程差 {soc(p_mk) - c_soc} 步",
                     "Same instance, same algorithm: one cost says wait, the other says detour",
                     wait=2.0)

        self.card(["窄道上的让行，不是算法问题，是报表问题",
                   "两种冲突都要查：同刻同格（点），与一步之内对穿（换位）",
                   "优先级让行可行但不最优；冲突搜索最优，可要花搜索的工夫",
                   "报“好了多少”，先说清跟已证明最优比，还是跟下界比——两者不是一回事",
                   "在意最后一台几点下线就报 makespan（该绕），在意总行程总电耗就报 "
                   "sum-of-costs（该等）"], wait=3.4)
