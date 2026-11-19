"""第 25 章（无人机与智能物流）共用的玩具模型。

全章纪律：**不依赖任何求解器、不联网、不下载任何数据**。只用 numpy 与标准库，
A\\*、冲突搜索、分支定界、穷举下界全部自己写。

本章还有一条比别章更硬的规矩（见 `conventions/logi_facts.py` 开头与第 14 轮细则
§2.25.3、§2.25.5 修正三）：

    **没有最优解或下界作对照的“改进”不采信。**

所以这个模块里成对地提供两类函数：一类求解（启发式、优先级法、冲突搜索），
一类给真值（小规模穷举出的**已证明最优解**、大规模的**可证明下界**）。
凡打印“好了多少”，都要指明是跟哪一类比的——这正是 CVRPLIB 把“上界 UB”与
“是否已证明最优 Opt”分成两列的用意。

场地：这座车间是第 21、22 章那座减速器厂的第三次露面（21 章算停机的代价、
22 章算电价与预测误差的代价、25 章算搬运的代价）。工位名与第 21 章
`_ch21.py` 的 `STATIONS` 同源，布局（通道、货架、充电位、窄道）是本章的
**显式假设**，不取自任何企业图纸。
"""
from __future__ import annotations

import heapq
import itertools
import math
from collections import deque

import numpy as np

from logi_facts import LITTLES_LAW, MAPF_BENCHMARK

# ================================================================ 一、车间网格地图

# 符号：`#` 货架或墙（不可走）、`.` 通道、`C` 充电位（可走）、`P` 取货点、`D` 放货点。
# 第 5 行只有两个口（第 3、9 列），这是本章反复用的**窄道**：两台车对向通过就要
# 么等、要么绕（25.2 节的动画与 25.3 节的算例都用它）。
GRID_WORKSHOP = (
    "#############",
    "#C.........C#",
    "#.###.###.#.#",
    "#.###.###.#.#",
    "#...........#",
    "###.#####.###",      # 窄道：只有 (5,3) 与 (5,9) 两个口
    "#...........#",
    "#.###.###.#.#",
    "#.###.###.#.#",
    "#C.........C#",
    "#############",
)

# 小地图：只有这种规模才穷举得出**已证明最优**的多机解（算例 25.1 用它）。
GRID_SMALL = (
    "#########",
    "#.......#",
    "#.##.##.#",
    "#.......#",
    "#.##.##.#",
    "#.......#",
    "#########",
)

# 窄道地图：上下两间车间，中间一条长窄道，左右各有一条更远的旁路。
# 25.3 节“等一等还是绕一绕”的实例就建在这上面。
GRID_CORRIDOR = (
    "###########",
    "#.........#",
    "#.###.###.#",
    "#.###.###.#",
    "#.###.###.#",
    "#.###.###.#",
    "#.###.###.#",
    "#.........#",
    "###########",
)

MOVES = ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))     # 第一个是**等待动作**


def block_cells(rows: tuple[str, ...], cells) -> tuple[str, ...]:
    """把若干格子封起来（当成货架）：算例要“只许走这条道”的时候用它造对照地图。"""
    g = [list(r) for r in rows]
    for r, c in cells:
        g[r][c] = "#"
    return tuple("".join(x) for x in g)


class Grid:
    """网格地图：可走性、邻居、以及任意两点间的真实最短步数（广度优先，不是估计）。"""

    def __init__(self, rows: tuple[str, ...]):
        self.rows = tuple(rows)
        self.h = len(rows)
        self.w = len(rows[0])
        assert all(len(r) == self.w for r in rows), "地图每行长度必须一样"
        self.free = {(r, c) for r in range(self.h) for c in range(self.w)
                     if rows[r][c] != "#"}
        self.chargers = tuple(sorted((r, c) for r in range(self.h) for c in range(self.w)
                                     if rows[r][c] == "C"))
        self._dist: dict[tuple[int, int], dict] = {}

    def ok(self, cell) -> bool:
        return cell in self.free

    def neighbors(self, cell) -> list:
        """四邻域 + 等待动作（等待也占一个时间步，这一点 MAPF 的代价定义里要计）。"""
        r, c = cell
        return [(r + dr, c + dc) for dr, dc in MOVES if (r + dr, c + dc) in self.free]

    def field(self, target) -> dict:
        """从 `target` 出发的广度优先距离场（缓存）。单机最短步数的**真值**。"""
        if target not in self._dist:
            d = {target: 0}
            q = deque([target])
            while q:
                cur = q.popleft()
                for nb in self.neighbors(cur):
                    if nb != cur and nb not in d:
                        d[nb] = d[cur] + 1
                        q.append(nb)
            self._dist[target] = d
        return self._dist[target]

    def dist(self, a, b) -> float:
        return self.field(b).get(a, math.inf)


# ================================================================ 二、单机 A\*


def astar(grid: Grid, start, goal) -> list:
    """单机最短路 A\\*，启发函数取曼哈顿距离（四邻域下可采纳，不会高估）。

    返回按时间步排列的格子序列，`path[t]` 是第 t 步所在的格子。
    """
    if start == goal:
        return [start]

    def h(cell):
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

    cnt = itertools.count()
    open_q = [(h(start), next(cnt), start)]
    g = {start: 0}
    came = {}
    while open_q:
        _, _, cur = heapq.heappop(open_q)
        if cur == goal:
            path = [cur]
            while cur in came:
                cur = came[cur]
                path.append(cur)
            path.reverse()
            return path
        for nb in grid.neighbors(cur):
            if nb == cur:
                continue                      # 单机最短路不需要等待
            ng = g[cur] + 1
            if ng < g.get(nb, math.inf):
                g[nb] = ng
                came[nb] = cur
                heapq.heappush(open_q, (ng + h(nb), next(cnt), nb))
    return []


# ================================================================ 三、多机：时空预留与冲突


def at(path: list, t: int):
    """智能体在第 t 步的位置：到了目标就**停在目标上**（代价定义据此而来）。"""
    return path[t] if t < len(path) else path[-1]


def st_astar(grid: Grid, start, goal, vcons: set = frozenset(),
             econs: set = frozenset(), horizon: int = 240) -> list:
    """时空 A\\*：在给定的**时空预留表**（约束集合）下为一台车规划，**含等待动作**。

    * `vcons`：点约束 `{(格子, 时刻)}`——这一刻不许占这个格子；
    * `econs`：边约束 `{(从, 到, 到达时刻)}`——不许在这一步做这个移动。

    代价每步 1（**等待也算一步**），所以返回路径的长度减一就是“这台车到达目标
    所需的时间步数”，与资料卡里 sum-of-costs 的定义口径一致。终点要等到最后
    一条与终点有关的约束过去之后才算真正到达，否则它会被后来的车撞下来。
    """
    # 只有**落在终点上**的约束才决定“什么时候算真正到达”：别人要在 t 时刻经过我的
    # 终点，我就得等到 t 之后才算到；拿全部约束的最大时刻当门槛，会让每台车白等到天亮。
    last = max([t for (cell, t) in vcons if cell == goal]
               + [t for (_, to, t) in econs if to == goal] + [0])
    cnt = itertools.count()

    def h(cell):
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])

    open_q = [(h(start), next(cnt), start, 0)]
    best = {(start, 0): 0}
    came: dict = {}
    while open_q:
        _, _, cell, t = heapq.heappop(open_q)
        if cell == goal and t >= last:
            path = [cell]
            key = (cell, t)
            while key in came:
                key = came[key]
                path.append(key[0])
            path.reverse()
            return path
        if t >= horizon:
            continue
        for nb in grid.neighbors(cell):
            if (nb, t + 1) in vcons or (cell, nb, t + 1) in econs:
                continue
            if best.get((nb, t + 1), math.inf) > t + 1:
                best[(nb, t + 1)] = t + 1
                came[(nb, t + 1)] = (cell, t)
                heapq.heappush(open_q, (t + 1 + h(nb), next(cnt), nb, t + 1))
    return []


def find_conflicts(paths: list, first_only: bool = False) -> list:
    """找冲突。两种冲突的口径照 MAPF 基准论文与冲突搜索论文（见 `logi_facts`）：

    * **点冲突**：两台车在同一时刻占同一个格子；
    * **边冲突（换位）**：两台车在一步之内互换位置（擦身而过，现实里就是对撞）。

    返回 `(类型, i, j, 格子或格子对, 时刻)` 的列表。
    """
    out = []
    span = max(len(p) for p in paths)
    for t in range(span):
        for i, j in itertools.combinations(range(len(paths)), 2):
            pi, pj = at(paths[i], t), at(paths[j], t)
            if pi == pj:
                out.append(("vertex", i, j, pi, t))
                if first_only:
                    return out
            if t > 0:
                qi, qj = at(paths[i], t - 1), at(paths[j], t - 1)
                if pi == qj and pj == qi and pi != pj:
                    out.append(("edge", i, j, (qi, pi), t))
                    if first_only:
                        return out
    return out


def sum_of_costs(paths: list) -> int:
    """sum-of-costs：原话 “%s”（`logi_facts.MAPF_BENCHMARK['soc_def']`）。

    照原话逐车累加“到达目标所需的时间步数”，也就是各条路径长度减一之和。
    冲突搜索论文把它叫 flowtime。
    """ % MAPF_BENCHMARK["soc_def"]
    return int(sum(len(p) - 1 for p in paths))


def makespan(paths: list) -> int:
    """makespan：原话 “%s”（`logi_facts.MAPF_BENCHMARK['makespan_def']`）。

    **最后一台**车到达目标的时刻。与 sum-of-costs 是两个不同的代价，
    最优解一般不是同一个解——25.3 节的算例就把这件事算出来。
    """ % MAPF_BENCHMARK["makespan_def"]
    return int(max(len(p) - 1 for p in paths))


def trim(paths: list) -> list:
    """把路径尾部多余的“停在目标上”的步数剪掉，使代价与定义对齐。"""
    out = []
    for p in paths:
        k = len(p) - 1
        while k > 0 and p[k] == p[k - 1]:
            k -= 1
        out.append(p[:k + 1])
    return out


def plan_independent(grid: Grid, starts: list, goals: list) -> list:
    """各车**各规划各的**：最省事，也最容易撞——冲突数由 `find_conflicts` 数出来。"""
    return [astar(grid, s, g) for s, g in zip(starts, goals)]


def plan_prioritized(grid: Grid, starts: list, goals: list,
                     order: list | None = None, horizon: int | None = None) -> list:
    """优先级法：按给定顺序逐车规划，后面的车把前面的车当**时空障碍**（含等待）。

    车间里最常见的做法：可行、快，但**不最优**，而且顺序一换结果就变。
    已规划的车到了目标就**一直停在那里**，预留要一直留到 `horizon`——不留够，
    后面的车就会在预留表过期之后从它身上压过去（这个坑踩过一次）。

    它还**不完备**：前面的车停在后面那台车的目标上，后面那台就永远到不了，
    这时照实返回空列表，不许偷偷放过冲突。
    """
    order = list(range(len(starts))) if order is None else list(order)
    if horizon is None:
        horizon = int(sum(grid.dist(s, g) for s, g in zip(starts, goals))
                      + 2 * len(starts) + 20)
    paths: dict = {}
    for k in order:
        vcons, econs = set(), set()
        for done in paths.values():
            for t in range(horizon + 1):
                vcons.add((at(done, t), t))
                if t > 0:                       # 禁止与已规划的车换位
                    econs.add((at(done, t), at(done, t - 1), t))
        p = st_astar(grid, starts[k], goals[k], vcons, econs, horizon=horizon)
        if not p:
            return []
        paths[k] = p
    return [paths[i] for i in range(len(starts))]


def cbs(grid: Grid, starts: list, goals: list, node_cap: int = 20000) -> tuple:
    """冲突搜索（CBS）：高层在冲突树上按 sum-of-costs 最小优先展开，低层用时空 A\\*。

    照冲突搜索论文的性质（`logi_facts.CBS`）：**定理 1 说它返回最优解**；
    但论文里**没有** “CBS is complete and optimal” 这句话——无解时冲突树可以
    无限增长，所以这里加了节点上限 `node_cap`，顶到上限就照实返回 `None`。

    返回 `(paths, 展开的高层节点数)`。
    """
    root_cons = [(set(), set()) for _ in starts]
    paths = [st_astar(grid, s, g) for s, g in zip(starts, goals)]
    if any(not p for p in paths):
        return None, 0
    cnt = itertools.count()
    open_q = [(sum_of_costs(paths), next(cnt), root_cons, paths)]
    expanded = 0
    while open_q:
        cost, _, cons, paths = heapq.heappop(open_q)
        expanded += 1
        if expanded > node_cap:
            return None, expanded
        conf = find_conflicts(paths, first_only=True)
        if not conf:
            return paths, expanded
        kind, i, j, where, t = conf[0]
        for who in (i, j):
            new_cons = [(set(a), set(b)) for a, b in cons]
            if kind == "vertex":
                new_cons[who][0].add((where, t))
            else:
                frm, to = where
                if who == i:
                    new_cons[who][1].add((frm, to, t))
                else:
                    new_cons[who][1].add((to, frm, t))
            p = st_astar(grid, starts[who], goals[who], new_cons[who][0], new_cons[who][1])
            if not p:
                continue
            new_paths = list(paths)
            new_paths[who] = p
            heapq.heappush(open_q, (sum_of_costs(new_paths), next(cnt), new_cons, new_paths))
    return None, expanded


# ================================================================ 四、真值：联合状态空间穷举


def optimal_joint(grid: Grid, starts: list, goals: list, metric: str = "soc",
                  node_cap: int = 400000) -> tuple:
    """在**联合状态空间**里穷举出真正的最优解（A\\*，启发函数可采纳，所以是最优）。

    状态 = 各车位置的元组，一步 = 所有车同时动一格或等待（点冲突、边冲突都剪掉）。

    * `metric="soc"`：一步的代价 = 还没“停在自己目标上”的车数；
      启发函数 = 各车到目标的最短步数之和（每车至少要走这么多步），可采纳。
    * `metric="makespan"`：一步的代价恒为 1；启发函数 = 各车最短步数的最大值，可采纳。

    这是本章的**真值**：小规模上它给出的就是“已证明最优”，不是“最好已知解”。
    规模一大它就爆炸（求最优 MAPF 是 NP-hard），所以顶到 `node_cap` 就报错，
    **不许悄悄降格成启发式**。
    """
    assert metric in ("soc", "makespan")
    n = len(starts)
    start = tuple(starts)
    goal = tuple(goals)
    fields = [grid.field(g) for g in goals]

    def h(state):
        ds = [fields[i][state[i]] for i in range(n)]
        return sum(ds) if metric == "soc" else max(ds)

    cnt = itertools.count()
    open_q = [(h(start), next(cnt), start, 0)]
    g_best = {start: 0}
    came: dict = {}
    expanded = 0
    while open_q:
        _, _, state, gc = heapq.heappop(open_q)
        if gc > g_best.get(state, math.inf):
            continue
        if state == goal:
            seq = [state]
            while state in came:
                state = came[state]
                seq.append(state)
            seq.reverse()
            paths = [[s[i] for s in seq] for i in range(n)]
            return trim(paths), gc, expanded
        expanded += 1
        if expanded > node_cap:
            raise RuntimeError(f"联合空间穷举超过 {node_cap} 个节点：这个规模穷举不了，"
                               "要改用下界，不许拿启发式当最优解")
        options = [grid.neighbors(state[i]) for i in range(n)]
        for nxt in itertools.product(*options):
            if len(set(nxt)) != n:                                   # 点冲突
                continue
            if any(nxt[i] == state[j] and nxt[j] == state[i]          # 边冲突（换位）
                   for i, j in itertools.combinations(range(n), 2)):
                continue
            if metric == "soc":
                step = sum(0 if (state[i] == goals[i] and nxt[i] == goals[i]) else 1
                           for i in range(n))
            else:
                step = 1
            ng = gc + step
            if ng < g_best.get(nxt, math.inf):
                g_best[nxt] = ng
                came[nxt] = state
                heapq.heappush(open_q, (ng + h(nxt), next(cnt), nxt, ng))
    raise RuntimeError("联合空间里无解")


def tradeoff_joint(grid: Grid, starts: list, goals: list, t_max: int = 30,
                   state_cap: int = 4000000) -> dict:
    """在时间展开的联合图上做**逐层动态规划**，把 makespan 与 sum-of-costs 的
    全部权衡（帕累托前沿）算出来——不是采样，是穷举。

    第 t 层记“所有车在这些位置、时刻为 t”的最小 sum-of-costs。于是：

    * `min_soc[t]`：**makespan 不超过 t** 时 sum-of-costs 最少是多少；
    * 这条曲线的最后一个值就是 sum-of-costs 的最优值，第一个有解的 t 就是 makespan 的最优值。

    两头各取一个解，正是 25.3 节要对照的“等一等”与“绕一绕”。
    """
    n = len(starts)
    start, goal = tuple(starts), tuple(goals)
    fields = [grid.field(g) for g in goals]
    layer = {start: 0}
    came = {(start, 0): None}
    best: dict[int, int] = {}
    seen = 0
    for t in range(t_max):
        if goal in layer:
            best[t] = min(best.get(t, 10 ** 9), layer[goal])
        nxt_layer: dict = {}
        for state, soc in layer.items():
            # 剪枝：剩下的路再快也走不完
            if t + max(fields[i][state[i]] for i in range(n)) > t_max:
                continue
            options = [grid.neighbors(state[i]) for i in range(n)]
            for nxt in itertools.product(*options):
                if len(set(nxt)) != n:
                    continue
                if any(nxt[i] == state[j] and nxt[j] == state[i]
                       for i, j in itertools.combinations(range(n), 2)):
                    continue
                step = sum(0 if (state[i] == goals[i] and nxt[i] == goals[i]) else 1
                           for i in range(n))
                if nxt_layer.get(nxt, 10 ** 9) > soc + step:
                    nxt_layer[nxt] = soc + step
                    came[(nxt, t + 1)] = (state, t)
        seen += len(nxt_layer)
        if seen > state_cap:
            raise RuntimeError("时间展开图太大，这个规模穷举不了")
        layer = nxt_layer
        if not layer:
            break
    if goal in layer:
        best[t_max] = min(best.get(t_max, 10 ** 9), layer[goal])
    # 单调化：makespan 放宽到 t 时，sum-of-costs 取 t 以内的最好值
    curve, run = {}, 10 ** 9
    for t in sorted(best):
        run = min(run, best[t])
        curve[t] = run

    def recover(t_goal: int) -> list:
        seq, key = [], (goal, t_goal)
        while key is not None and key in came:
            seq.append(key[0])
            key = came[key]
        seq.reverse()
        return trim([[s[i] for s in seq] for i in range(n)])

    ts = sorted(best)
    return {"curve": curve, "raw": best, "mk_min": ts[0] if ts else None,
            "soc_min": min(best.values()) if best else None,
            "paths_at": recover, "t_max": t_max}


def path_profile(grid: Grid, paths: list, starts: list, goals: list) -> list:
    """每台车的 (代价, 比最短路多走的步数, 原地等待的步数)——“等”与“绕”就是这两列。"""
    out = []
    for i, p in enumerate(paths):
        moves = sum(1 for t in range(1, len(p)) if p[t] != p[t - 1])
        waits = (len(p) - 1) - moves
        out.append((len(p) - 1, int(moves - grid.dist(starts[i], goals[i])), waits))
    return out


# ================================================================ 五、车辆路径问题：实例、启发式、最优与下界


def vrp_instance(n_cust: int, seed: int = 0, cap: float = 100.0,
                 span: float = 60.0) -> dict:
    """玩具车辆路径实例：一个仓库（下标 0）加 `n_cust` 个取送点，欧氏距离。

    坐标与需求都是**显式假设**（厂区尺度，米），不取自任何企业数据。
    """
    g = np.random.default_rng(seed + 7000)
    xy = np.vstack([[span / 2, span / 2], g.uniform(0, span, (n_cust, 2))])
    demand = np.concatenate([[0.0], g.integers(8, 34, n_cust).astype(float)])
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    return {"xy": xy, "demand": demand, "dist": d, "cap": cap, "n": n_cust}


def route_cost(inst: dict, route: list) -> float:
    """一条回路（仓库→…→仓库）的长度。"""
    d, prev, tot = inst["dist"], 0, 0.0
    for k in route:
        tot += d[prev, k]
        prev = k
    return float(tot + d[prev, 0])


def vrp_cost(inst: dict, routes: list) -> float:
    return float(sum(route_cost(inst, r) for r in routes))


def vrp_greedy(inst: dict) -> list:
    """最近邻贪心 + 装不下就回仓库：车间调度室手上最常见的那一版。"""
    d, dem, cap = inst["dist"], inst["demand"], inst["cap"]
    left = set(range(1, inst["n"] + 1))
    routes = []
    while left:
        route, load, cur = [], 0.0, 0
        while True:
            cand = [k for k in left if load + dem[k] <= cap + 1e-9]
            if not cand:
                break
            k = min(cand, key=lambda k: d[cur, k])
            route.append(k)
            load += dem[k]
            left.discard(k)
            cur = k
        routes.append(route)
    return routes


def vrp_optimal(inst: dict) -> tuple:
    """**穷举出真正的最优解**：枚举全部客户次序 + 对每个次序按容量做最优切分。

    任何可行解的若干条回路都能首尾相接成一个客户次序，而动态规划切分在这个次序上
    找的是最好的切法，所以“全部次序 × 最优切分”覆盖了全部可行解——
    这是**已证明最优**，不是最好已知解。规模一大就不能用（n! 增长），
    所以 `n_cust` 超过 9 直接报错。
    """
    n = inst["n"]
    if n > 9:
        raise RuntimeError(f"{n} 个点穷举不了（n! 爆炸），这个规模只能跟下界比")
    d = [[float(x) for x in row] for row in inst["dist"]]      # 纯 Python 更快
    dem = [float(x) for x in inst["demand"]]
    cap = inst["cap"]
    best_cost, best_routes = math.inf, None
    for perm in itertools.permutations(range(1, n + 1)):
        f = [0.0] + [math.inf] * n
        back = [0] * (n + 1)
        for j in range(1, n + 1):
            load, inner, tail = 0.0, 0.0, d[perm[j - 1]][0]
            for i in range(j - 1, -1, -1):          # 这一条回路覆盖 perm[i..j-1]
                k = perm[i]
                load += dem[k]
                if load > cap + 1e-9:
                    break
                if i < j - 1:
                    inner += d[k][perm[i + 1]]
                seg = d[0][k] + inner + tail
                if f[i] + seg < f[j]:
                    f[j] = f[i] + seg
                    back[j] = i
        if f[n] < best_cost - 1e-12:
            routes, j = [], n
            while j > 0:
                i = back[j]
                routes.append(list(perm[i:j]))
                j = i
            best_cost, best_routes = f[n], routes[::-1]
    return float(best_cost), best_routes


def vrp_lower_bound(inst: dict) -> float:
    """**可证明的下界**：每个客户两条最便宜的邻边之半求和。

    任何可行解里每个客户恰好连两条边。把每条边的费用在两个端点之间各记一半，
    则“客户端记到的一半”之和不超过全长（连仓库的那些边只被记了一半），
    再把实际的两条边换成最便宜的两条，只会更小。所以这个数**不可能超过最优值**。

    另附一个车数下界 `ceil(总需求 / 载重)`，用来说明“为什么至少要跑这么多趟”。
    """
    d, dem, cap = inst["dist"], inst["demand"], inst["cap"]
    n = inst["n"]
    lb = 0.0
    for i in range(1, n + 1):
        e = sorted(d[i, k] for k in range(n + 1) if k != i)
        lb += (e[0] + e[1]) / 2.0
    return float(lb)


def vrp_min_vehicles(inst: dict) -> int:
    """装箱下界：总需求除以载重向上取整——车数不可能比这个少。"""
    return int(math.ceil(float(inst["demand"].sum()) / inst["cap"] - 1e-9))


# ================================================================ 六、排队论与离散事件仿真（25.7 节）


def erlang_c_wait(lam: float, mu: float, k: int) -> float:
    """M/M/k 的平均排队等待时间（Erlang C）。本节的“估算”就用它，自己写，不引库。

    它与利特尔法则一起用：`L = λW`（`logi_facts.LITTLES_LAW`），
    而利特尔法则的适用条件是论文摘要里写死的三条——
    %s
    三条里只要有一条不成立（例如系统接近饱和、不平稳），下面的估算就开始失真。
    """ % "；".join(LITTLES_LAW["conditions"])
    a = lam / mu
    rho = a / k
    if rho >= 1.0:
        return math.inf
    s = sum(a ** i / math.factorial(i) for i in range(k))
    last = a ** k / math.factorial(k)
    p_wait = last / (1 - rho) / (s + last / (1 - rho))
    return p_wait / (k * mu - lam)


def littles_law(lam: float, w: float) -> float:
    """利特尔法则：L = λW（公式原文 `logi_facts.LITTLES_LAW['formula']`）。"""
    assert LITTLES_LAW["formula"] == "L = λW"
    return lam * w


def service_sample(rng, mean: float, cv2: float) -> float:
    """服务时间抽样：`cv2` 是平方变异系数。

    `cv2 == 1` 给指数分布（M/M/k 的假设）；`cv2 > 1` 用两点超指数分布，
    均值不变而方差变大——**这正是估算开始不准的第二个原因**（第一个是接近饱和）。
    """
    if abs(cv2 - 1.0) < 1e-9:
        return float(rng.exponential(mean))
    p = 0.5 * (1 - math.sqrt((cv2 - 1) / (cv2 + 1)))
    m1 = mean / (2 * p) if rng.random() < p else mean / (2 * (1 - p))
    return float(rng.exponential(m1))


def simulate_queue(lam: float, mu: float, k: int, n_jobs: int = 60000,
                   cv2: float = 1.0, seed: int = 0) -> dict:
    """离散事件仿真：k 台搬运车、一个任务队列，自己写事件队列，不引仿真库。

    返回平均停留时间 W、平均在制品数 L（按时间加权）、以及实测利用率。
    """
    rng = np.random.default_rng(seed + 31)
    free = [0.0] * k                      # 每台车下一次空闲的时刻
    t = 0.0
    w_sum, busy_area, n_in = 0.0, 0.0, 0
    events = []                           # (时刻, +1 进入 / -1 离开)
    for _ in range(n_jobs):
        t += float(rng.exponential(1.0 / lam))
        i = min(range(k), key=lambda j: free[j])
        begin = max(t, free[i])
        dur = service_sample(rng, 1.0 / mu, cv2)
        free[i] = begin + dur
        w_sum += begin + dur - t
        events.append((t, 1))
        events.append((begin + dur, -1))
    events.sort()
    prev = events[0][0]
    for tt, delta in events:
        busy_area += n_in * (tt - prev)
        n_in += delta
        prev = tt
    span = events[-1][0] - events[0][0]
    return {"w": w_sum / n_jobs, "l": busy_area / span,
            "rho": lam / (k * mu), "span": span}


def simulate_queue_shift(lam_hi: float, lam_lo: float, period: float, mu: float, k: int,
                         n_jobs: int = 200000, cv2: float = 1.0, seed: int = 0) -> dict:
    """同一个系统，但到达率**按班次来回变**（忙一阵、闲一阵），平均到达率不变。

    这是为了把利特尔法则的第二个条件——“相应随机过程严格平稳”——**违反掉**看看后果。
    稀释抽样（thinning）生成到达：按最大速率抽，再按当下速率的比例接受。
    """
    rng = np.random.default_rng(seed + 77)
    lam_max = max(lam_hi, lam_lo)
    free = [0.0] * k
    t = 0.0
    w_sum, n_acc = 0.0, 0
    events = []
    while n_acc < n_jobs:
        t += float(rng.exponential(1.0 / lam_max))
        lam_now = lam_hi if (t % period) < period / 2 else lam_lo
        if rng.random() > lam_now / lam_max:
            continue
        i = min(range(k), key=lambda j: free[j])
        begin = max(t, free[i])
        dur = service_sample(rng, 1.0 / mu, cv2)
        free[i] = begin + dur
        w_sum += begin + dur - t
        events.append((t, 1))
        events.append((begin + dur, -1))
        n_acc += 1
    events.sort()
    area, n_in, prev = 0.0, 0, events[0][0]
    for tt, delta in events:
        area += n_in * (tt - prev)
        n_in += delta
        prev = tt
    span = events[-1][0] - events[0][0]
    return {"w": w_sum / n_acc, "l": area / span, "lam_mean": n_acc / span,
            "span": span}


# ================================================================ 七、车队仿真：吞吐、死锁与充电（25.4、25.7 节，案例 25.5）

# 车队参数：**全部是显式假设**，照 `logi_facts.WAREHOUSE_ASSUMED` 的纪律，
# 不取自任何厂家样本（ISO 3691-4 的停车距离与速度要求本次核不到，一个数都不印）。
FLEET = {
    "battery_full": 240,       # 满电能走多少步
    "charge_rate": 10,         # 充电位上每步回多少
    "deadline": 70,            # 任务从发布到完成的时限（步），超了算一次超时
    "stuck_steps": 5,          # 连续被堵这么多步算一次死锁（要人工或重规划才能解）
    "recover_steps": 40,       # 一次死锁要停这么多步才解开（重规划或人工介入的代价）
    "zone_radius": 0,          # 区域联锁半径：0 = 不联锁（只停那一台车）
    "task_every": 1,           # 平均多少步发布一个新任务（取 1 = 活永远有，瓶颈在车队）
}


def run_fleet(grid: Grid, n_agv: int, steps: int = 1200, seed: int = 0,
              policy: str = "threshold", low_thr: float = 0.18,
              idle_thr: float = 0.75, cfg: dict = FLEET) -> dict:
    """一座车间、`n_agv` 台搬运车跑 `steps` 步，返回吞吐、冲突、死锁与超时。

    走法：每台车按自己目标的广度优先距离场下坡；下一格被占就退而求其次（这就是“绕”），
    都不行就等（这就是“等”）。先到先得按车号定优先级——**顺序一换结果就变**，
    这也是优先级法的老毛病。连续被堵 `stuck_steps` 步算一次**死锁**，
    要停 `recover_steps` 步重规划或等人来解（这是**显式假设**：死锁不是免费的，
    这一条正是“车加多了反而更慢”的来源）。

    充电策略两种：
    * `threshold`：电量掉到 `low_thr` 以下才去充（车间里最常见）；
    * `opportunistic`：没任务可做而电量低于 `idle_thr` 就顺便去充（机会充电）。

    报表四个数一起给：**吞吐、冲突、死锁、超时**——按本章口径，报成绩必须连
    “失败的那一列”一起报。
    """
    rng = np.random.default_rng(seed + 90001)
    cells = sorted(grid.free)
    aisle = [c for c in cells if c not in grid.chargers]

    pos = [cells[int(rng.integers(len(cells)))] for _ in range(n_agv)]
    for i in range(n_agv):                            # 不让两台车同格开局
        while pos.count(pos[i]) > 1:
            pos[i] = cells[int(rng.integers(len(cells)))]
    batt = [float(cfg["battery_full"]) * float(rng.uniform(0.55, 1.0)) for _ in range(n_agv)]
    target = [None] * n_agv                           # 当前要去的格子
    phase = ["idle"] * n_agv                          # idle / pick / drop / charge
    job = [None] * n_agv                              # (发布时刻, 取货点, 放货点)
    stuck = [0] * n_agv
    recover = [0] * n_agv                             # 还要停几步才从死锁里出来

    pending: deque = deque()
    done, overdue, conflicts, deadlocks, charge_steps, stranded = 0, 0, 0, 0, 0, 0
    was_flat = [False] * n_agv                        # 这台车是不是已经在半路耗光了
    served_w = []

    for t in range(steps):
        if rng.random() < 1.0 / cfg["task_every"]:
            p = aisle[int(rng.integers(len(aisle)))]
            d = aisle[int(rng.integers(len(aisle)))]
            if p != d:
                pending.append((t, p, d))

        # ---- 派活与充电决策
        for i in range(n_agv):
            frac = batt[i] / cfg["battery_full"]
            if phase[i] == "charge":
                continue
            need = frac < low_thr
            if policy == "opportunistic" and phase[i] == "idle" and not pending:
                need = need or frac < idle_thr
            if need and phase[i] in ("idle", "pick"):
                if phase[i] == "pick" and job[i] is not None:
                    pending.appendleft(job[i])        # 还没取货，任务退回队列
                    job[i] = None
                phase[i] = "charge"
                target[i] = min(grid.chargers, key=lambda c: grid.dist(pos[i], c))
                continue
            if phase[i] == "idle" and pending:
                job[i] = pending.popleft()
                phase[i] = "pick"
                target[i] = job[i][1]

        # ---- 移动（按车号的优先级，先到先占）
        taken = {}
        order = sorted(range(n_agv), key=lambda i: (phase[i] == "idle", i))
        nxt = list(pos)
        for i in order:
            if recover[i] > 0:                        # 还在死锁恢复里，站着不动
                recover[i] -= 1
                taken[pos[i]] = i
                continue
            if target[i] is None or pos[i] == target[i] or batt[i] <= 0:
                taken[pos[i]] = i
                continue
            fld = grid.field(target[i])
            cand = sorted((c for c in grid.neighbors(pos[i]) if c != pos[i]),
                          key=lambda c: fld.get(c, 10 ** 6))
            moved = False
            for k, c in enumerate(cand):
                if c in taken:
                    continue
                if any(nxt[j] == pos[i] and pos[j] == c for j in range(n_agv) if j != i):
                    continue                                     # 换位冲突
                if k > 0:
                    conflicts += 1                               # 第一选择被占：绕了
                nxt[i] = c
                taken[c] = i
                batt[i] -= 1.0
                moved = True
                break
            if not moved:
                conflicts += 1
                stuck[i] += 1
                taken[pos[i]] = i
                if stuck[i] >= cfg["stuck_steps"]:
                    deadlocks += 1
                    stuck[i] = 0
                    recover[i] = cfg["recover_steps"]            # 停下来重规划/等人解
                    if cfg.get("zone_radius", 0):
                        # 区域联锁（**显式假设**）：一处卡住，附近这一片一起停一会儿。
                        # 车间里带区域控制的搬运系统就是这么兜安全的，代价是堵一处停一片。
                        for j in range(n_agv):
                            if j != i and (abs(pos[j][0] - pos[i][0])
                                           + abs(pos[j][1] - pos[i][1])) <= cfg["zone_radius"]:
                                recover[j] = max(recover[j], cfg["recover_steps"])
            else:
                stuck[i] = 0
        pos = nxt

        # ---- 在半路耗光电的车：**这是报表上最该有的那一列**（要人去拖）
        for i in range(n_agv):
            if batt[i] <= 0 and pos[i] not in grid.chargers:
                if not was_flat[i]:
                    stranded += 1
                    was_flat[i] = True
            elif batt[i] > 0:
                was_flat[i] = False

        # ---- 到站
        for i in range(n_agv):
            if target[i] is not None and pos[i] == target[i]:
                if phase[i] == "pick":
                    phase[i] = "drop"
                    target[i] = job[i][2]
                elif phase[i] == "drop":
                    done += 1
                    w = t - job[i][0]
                    served_w.append(w)
                    if w > cfg["deadline"]:
                        overdue += 1
                    job[i], target[i], phase[i] = None, None, "idle"
                elif phase[i] == "charge":
                    batt[i] = min(cfg["battery_full"], batt[i] + cfg["charge_rate"])
                    charge_steps += 1
                    if batt[i] >= cfg["battery_full"] - 1e-9:
                        target[i], phase[i] = None, "idle"
    # 还压在队列里、已经超时的任务也要算进去
    overdue += sum(1 for (tt, _, _) in pending if steps - tt > cfg["deadline"])
    return {"n_agv": n_agv, "done": done, "overdue": overdue, "conflicts": conflicts,
            "deadlocks": deadlocks, "charge_steps": charge_steps, "stranded": stranded,
            "backlog": len(pending),
            "mean_wait": float(np.mean(served_w)) if served_w else float("nan"),
            "throughput": done / steps * 100.0}


# ================================================================ 八、无人机巡检：航迹与电量（25.1、25.6 节）

# **显式假设**，照本章口径（c）与 `logi_facts` 的纪律：
# 这里的续航、巡航速度、每点悬停时间全部是本书自己设的工况参数，
# **计算里一个厂家标称值都没用**。厂家标称值（M350 的 55 min、M4 的 200 g 载重等）
# 连标称条件一起记在 `logi_facts.DRONE_M350` / `DRONE_M4` 里，只在正文作对照——
# 标称条件是“约 8 m/s 平飞、无载重、无风、放电到 0%”，拿它当巡检工况直接算就是错的。
DRONE_ASSUMED = {
    "cruise_ms": 8.0,          # 巡航速度（m/s）
    "endurance_s": 10 * 60,    # 一块电池**可用**的飞行时间（s）——已扣掉返航与安全余量
    "hover_s": 60.0,           # 每个巡检点悬停拍照/盘库的时间（s）
    "swap_s": 240.0,           # 换电池/落地重启的时间（s）
    "payload_kg": 0.8,         # 挂载重量（kg），只用于正文说明，不进任何计算
    "note": "全部为本书显式假设，不取自任何厂家标称值；厂家标称值见 logi_facts，只作对照",
}


def inspect_instance(n_pts: int, seed: int = 0, span: float = 900.0) -> dict:
    """厂区巡检实例：起降点（下标 0）加 `n_pts` 个巡检点，坐标单位米。"""
    g = np.random.default_rng(seed + 5100)
    xy = np.vstack([[0.0, 0.0], g.uniform(-span / 2, span / 2, (n_pts, 2))])
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    return {"xy": xy, "dist": d, "n": n_pts}


def leg_time(inst: dict, trip: list, cfg: dict = DRONE_ASSUMED) -> float:
    """一趟航线（起降点→若干巡检点→起降点）耗的电池时间（s）：飞行 + 悬停。"""
    return route_cost({"dist": inst["dist"]}, trip) / cfg["cruise_ms"] \
        + cfg["hover_s"] * len(trip)


def inspect_greedy(inst: dict, cfg: dict = DRONE_ASSUMED,
                   battery: bool = True) -> list:
    """最近邻启发式：顺手飞最近的点；电量不够回去换电，就开新的一趟。"""
    d = inst["dist"]
    left = set(range(1, inst["n"] + 1))
    trips = []
    while left:
        trip, cur = [], 0
        while True:
            cand = sorted(left, key=lambda k: d[cur, k])
            pick = None
            for k in cand:
                if not battery or leg_time(inst, trip + [k], cfg) <= cfg["endurance_s"]:
                    pick = k
                    break
            if pick is None:
                break
            trip.append(pick)
            left.discard(pick)
            cur = pick
        if not trip:
            raise RuntimeError("有巡检点一趟都飞不到：电量假设与厂区尺度不相容")
        trips.append(trip)
    return trips


def inspect_optimal(inst: dict, cfg: dict = DRONE_ASSUMED,
                    battery: bool = True) -> tuple:
    """**穷举出真正的最优**：全部巡检次序 × 按电量的最优切分（同 `vrp_optimal` 的道理）。"""
    n = inst["n"]
    if n > 8:
        raise RuntimeError(f"{n} 个巡检点穷举不了，这个规模只能跟下界比")
    d = [[float(x) for x in row] for row in inst["dist"]]
    cruise, hover, budget = cfg["cruise_ms"], cfg["hover_s"], cfg["endurance_s"]
    best, best_trips = math.inf, None
    for perm in itertools.permutations(range(1, n + 1)):
        f = [0.0] + [math.inf] * n
        back = [0] * (n + 1)
        for j in range(1, n + 1):
            inner, tail = 0.0, d[perm[j - 1]][0]
            for i in range(j - 1, -1, -1):
                k = perm[i]
                if i < j - 1:
                    inner += d[k][perm[i + 1]]
                seg = d[0][k] + inner + tail
                if battery and seg / cruise + hover * (j - i) > budget:
                    continue              # 这一趟电量不够，但更短的 i 也许够，不能 break
                if f[i] + seg < f[j]:
                    f[j] = f[i] + seg
                    back[j] = i
        if f[n] < best - 1e-12:
            trips, j = [], n
            while j > 0:
                i = back[j]
                trips.append(list(perm[i:j]))
                j = i
            best, best_trips = f[n], trips[::-1]
    return float(best), best_trips


def inspect_lower_bound(inst: dict) -> float:
    """巡检航程的**可证明下界**：每个巡检点两条最便宜的邻边之半求和（同 VRP 的道理）。

    它与电量无关，所以也是**加了电量约束之后**那个问题的下界——
    约束只会把解推坏，不会让它更短。
    """
    d, n = inst["dist"], inst["n"]
    lb = 0.0
    for i in range(1, n + 1):
        e = sorted(d[i, k] for k in range(n + 1) if k != i)
        lb += (e[0] + e[1]) / 2.0
    return float(lb)


def inspect_length(inst: dict, trips: list) -> float:
    return float(sum(route_cost({"dist": inst["dist"]}, t) for t in trips))


def inspect_mission_time(inst: dict, trips: list, cfg: dict = DRONE_ASSUMED) -> float:
    """整趟任务的总时间（s）：各趟的飞行 + 悬停，加上趟与趟之间的换电时间。"""
    return float(sum(leg_time(inst, t, cfg) for t in trips)
                 + cfg["swap_s"] * max(0, len(trips) - 1))
