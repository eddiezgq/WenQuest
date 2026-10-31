"""第 15 章共用的环境与算法：小网格车间、取木棍游戏、Kuhn 扑克、AGV 调度。

**为什么全是自己写的环境**：仓库里不放棋谱、游戏 ROM 与模型权重（与第 11—14 章不放图片、
录音、手册、报告同理）。本章要讲的道理——价值从哪来、搜索值多少、自我对弈会不会转圈、
奖励写歪了会学出什么——用程序按规则生成的环境讲得一样清楚，而且每个数都能复算，
有几个还能与解析解逐位核对（取木棍游戏有必胜策略，Kuhn 扑克有闭式的纳什均衡）。

真模型、真游戏上的数字见资料卡与 15.2、15.7 节的云端实验。
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- 一、小网格车间（15.1 节）
# 一台 AGV 在 5×5 的车间里跑：从入口去取件点，再送到出口。墙挡路，地面有油污（走上去会打滑）。
# 这是一个马尔可夫决策过程：状态 = 格子，动作 = 四个方向，转移有随机性，奖励由到达与耗时决定。

SHOP = [
    "S....",
    ".##..",
    "..#o.",
    ".#...",
    "..#.G",
]
ACTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))     # 上、下、左、右
ACTION_NAMES = ("上", "下", "左", "右")
SLIP = 0.1                                        # 油污格上有这个概率滑向别处
STEP_COST = -1.0                                  # 每走一步的代价（时间）
GOAL_REWARD = 20.0


def shop_grid(rows: list[str] | None = None):
    """把车间图解析成（格子类型, 起点, 终点）。'#' 是设备或货架，'o' 是油污，'G' 是出口。"""
    rows = rows or SHOP
    g = np.array([list(r) for r in rows])
    start = tuple(np.argwhere(g == "S")[0])
    goal = tuple(np.argwhere(g == "G")[0])
    return g, start, goal


def shop_mdp(rows: list[str] | None = None, slip: float = SLIP):
    """这个车间的转移与奖励：P[s, a, s'] 与 R[s, a]。状态按行优先编号，墙不算状态。"""
    g, start, goal = shop_grid(rows)
    H, W = g.shape
    free = [(i, j) for i in range(H) for j in range(W) if g[i, j] != "#"]
    idx = {c: k for k, c in enumerate(free)}
    n, na = len(free), len(ACTIONS)
    P = np.zeros((n, na, n))
    R = np.zeros((n, na))
    for c, s in idx.items():
        if c == goal:                             # 出口是吸收态：到了就停在那里，不再有奖励
            P[s, :, s] = 1.0
            continue
        oily = g[c] == "o"
        for a, (di, dj) in enumerate(ACTIONS):
            # 主方向的概率；油污格上有 slip 的概率滑向随便一个方向
            moves = {a: 1.0 - (slip if oily else 0.0)}
            if oily:
                for b in range(na):
                    moves[b] = moves.get(b, 0.0) + slip / na
            for b, p in moves.items():
                ni, nj = c[0] + ACTIONS[b][0], c[1] + ACTIONS[b][1]
                nxt = (ni, nj) if (0 <= ni < H and 0 <= nj < W and g[ni, nj] != "#") else c
                P[s, a, idx[nxt]] += p
                R[s, a] += p * (GOAL_REWARD if nxt == goal else STEP_COST)
    return P, R, idx, g, start, goal


def value_iteration(P, R, gamma: float = 0.95, tol: float = 1e-10, max_iter: int = 10_000):
    """价值迭代：反复用贝尔曼最优方程更新，直到不再变。返回（V, 策略, 迭代次数, 每轮的变化量）。"""
    n, na, _ = P.shape
    V = np.zeros(n)
    deltas = []
    for k in range(1, max_iter + 1):
        Q = R + gamma * P @ V
        V2 = Q.max(1)
        d = float(np.abs(V2 - V).max())
        deltas.append(d)
        V = V2
        if d < tol:
            break
    return V, (R + gamma * P @ V).argmax(1), k, np.array(deltas)


def policy_eval(P, R, pi, gamma: float = 0.95):
    """给定策略，直接解线性方程组求它的价值（不迭代）。"""
    n = len(pi)
    Ppi = P[np.arange(n), pi]
    return np.linalg.solve(np.eye(n) - gamma * Ppi, R[np.arange(n), pi])


def policy_iteration(P, R, gamma: float = 0.95, max_iter: int = 1000):
    """策略迭代：评估 → 改进 → 再评估，直到策略不再变。"""
    n, na, _ = P.shape
    pi = np.zeros(n, dtype=int)
    for k in range(1, max_iter + 1):
        V = policy_eval(P, R, pi, gamma)
        pi2 = (R + gamma * P @ V).argmax(1)
        if (pi2 == pi).all():
            return V, pi, k
        pi = pi2
    return policy_eval(P, R, pi, gamma), pi, max_iter


def q_learning(P, R, gamma: float = 0.95, alpha: float = 0.2, eps0: float = 0.3,
               steps: int = 400_000, seed: int = 0, goal: int | None = None, restart: int = 60,
               every: int = 20_000):
    """表格 Q 学习：不知道 P 与 R，只能试。

    两件事让它收敛得稳：ε 随时间退火（先多试后少试，与 DQN 的做法同理，15.2 节），
    以及每隔一段时间从随机状态重开（探索性开局——否则离起点远的格子一辈子访问不到几次）。
    返回（Q, 每 every 步记一次的 Q 的贪心价值）。
    """
    g = np.random.default_rng(seed)
    n, na, _ = P.shape
    Q = np.zeros((n, na))
    s, curve = int(g.integers(n)), []
    for t in range(steps):
        eps = max(0.05, eps0 * (1 - t / steps))
        a = int(g.integers(na)) if g.random() < eps else int(Q[s].argmax())
        s2 = int(g.choice(n, p=P[s, a]))
        Q[s, a] += alpha * (R[s, a] + gamma * Q[s2].max() - Q[s, a])
        s = s2
        if (goal is not None and s == goal) or (t + 1) % restart == 0:
            s = int(g.integers(n))
        if (t + 1) % every == 0:
            curve.append(Q.max(1).copy())
    return Q, np.array(curve)


# ---------------------------------------------------------------- 二、取木棍游戏（15.3 节）
# 桌上 N 根木棍，两人轮流取 1—3 根，取到最后一根的人赢。它有必胜策略：
# 剩下的根数是 4 的倍数时，轮到谁谁输。有解析解，所以可以用来核对搜索到底搜对没有。

TAKE = (1, 2, 3)


def sticks_best(n: int) -> int | None:
    """这一步的必胜取法：取 n % 4 根（n 是 4 的倍数时无必胜取法，返回 None）。"""
    return None if n % 4 == 0 else n % 4


def sticks_rollout(n: int, g: np.random.Generator) -> float:
    """从 n 根开始双方随便取，返回 1.0 表示“此刻轮到走的这个人最后赢了”，输了返回 0.0。"""
    turn = 0                                       # 0 = 此刻这位，1 = 对手
    while n > 0:
        n -= int(g.choice([t for t in TAKE if t <= n]))
        turn ^= 1
    return 1.0 if turn == 1 else 0.0               # 取走最后一根的是上一位


def uct(n: int, sims: int, c: float = 1.4, g: np.random.Generator | None = None):
    r"""蒙特卡洛树搜索（UCT）：选择 — 扩展 — 模拟 — 回传，四步一轮，跑 sims 轮。

    每个节点记两个数：被访问了多少次、这些访问里赢了多少。选择时按
    $\bar v + c\sqrt{\ln N / n}$ 挑一个孩子——前一项是“目前看它多好”，
    后一项是“它还没怎么试过”，这就是探索与利用的平衡。
    值一律按“轮到走的这个人”的视角记，所以往回传时每层取反（1 − v）。
    """
    g = g or np.random.default_rng(0)
    N: dict[int, float] = {n: 0.0}                 # 访问次数（键是剩几根）
    Wv: dict[int, float] = {n: 0.0}                # 赢的次数（按该节点轮到走的人算）
    for _ in range(sims):
        path, s = [], n
        # 选择：沿着已经展开的节点往下走
        while s > 0:
            kids = [s - t for t in TAKE if t <= s]
            unseen = [k for k in kids if k not in N]
            if unseen:                              # 扩展：挑一个没见过的孩子
                k = int(g.choice(unseen))
                N[k], Wv[k] = 0.0, 0.0
                path.append(s)
                s = k
                break
            tot = sum(N[k] for k in kids)
            ucb = [(1 - Wv[k] / max(N[k], 1e-9)) + c * np.sqrt(np.log(tot + 1) / max(N[k], 1e-9)) for k in kids]
            path.append(s)
            s = kids[int(np.argmax(ucb))]
        # 模拟：从这里随便走到底
        v = 0.0 if s == 0 else sticks_rollout(s, g)   # 轮到自己却一根不剩，说明上一位取完了，自己输
        # 回传：每往上一层，走子的人换一个，价值取反
        N[s] = N.get(s, 0.0) + 1
        Wv[s] = Wv.get(s, 0.0) + v
        for anc in reversed(path):
            v = 1 - v
            N[anc] += 1
            Wv[anc] += v
    kids = [s_ for s_ in (n - t for t in TAKE) if s_ >= 0]
    acts = [t for t in TAKE if t <= n]
    visits = np.array([N.get(k, 0.0) for k in kids])
    wins = np.array([N.get(k, 0.0) - Wv.get(k, 0.0) for k in kids])   # 孩子那一层是对手的视角
    return acts[int(np.argmax(visits))], acts, visits, wins


# ---------------------------------------------------------------- 三、Kuhn 扑克与 CFR（15.5 节）
# 三张牌（J、Q、K）各发一张，先手可以过牌或下注，有闭式的纳什均衡：
# 先手拿最小牌虚张的概率 α ∈ [0, 1/3]，任何均衡下先手的期望收益都是 −1/18。

CARDS = ("J", "Q", "K")
KUHN_VALUE = -1 / 18                 # 任何均衡下先手的期望收益（Kuhn 1950）
PASS, BET = 0, 1
KUHN_ACTIONS = ("过", "注")


def kuhn_terminal(history: str, p0_card: int, p1_card: int):
    """这一段历史是不是终局；是的话返回先手的收益。"""
    if history in ("pp",):
        return 1 if p0_card > p1_card else -1          # 都过牌：比大小，赌注 1
    if history in ("bp",):
        return 1                                        # 先手下注、后手弃牌
    if history in ("pbp",):
        return -1                                       # 先手过、后手下注、先手弃牌
    if history in ("bb", "pbb"):
        return 2 if p0_card > p1_card else -2           # 两家都下注：赌注 2
    return None


class CFR:
    """反事实遗憾最小化（Zinkevich 等 2007）。自我对弈若干轮之后，平均策略趋于纳什均衡。"""

    def __init__(self):
        self.regret: dict[str, np.ndarray] = {}
        self.strat: dict[str, np.ndarray] = {}

    def _node(self, key: str):
        if key not in self.regret:
            self.regret[key] = np.zeros(2)
            self.strat[key] = np.zeros(2)
        return self.regret[key]

    @staticmethod
    def _match(r: np.ndarray) -> np.ndarray:
        """遗憾匹配：按正的遗憾按比例走，全不正就均匀走。"""
        pos = np.maximum(r, 0)
        s = pos.sum()
        return pos / s if s > 0 else np.ones(2) / 2

    def walk(self, cards: tuple[int, int], history: str, p0: float, p1: float) -> float:
        player = len(history) % 2
        u = kuhn_terminal(history, cards[0], cards[1])
        if u is not None:
            return u if player == 0 else -u
        key = CARDS[cards[player]] + history
        r = self._node(key)
        sigma = self._match(r)
        self.strat[key] += (p0 if player == 0 else p1) * sigma     # 按到达概率累计平均策略
        util = np.zeros(2)
        node_util = 0.0
        for a, ch in enumerate("pb"):
            if player == 0:
                util[a] = -self.walk(cards, history + ch, p0 * sigma[a], p1)
            else:
                util[a] = -self.walk(cards, history + ch, p0, p1 * sigma[a])
            node_util += sigma[a] * util[a]
        reach = p1 if player == 0 else p0                          # 反事实概率：对手让我走到这里的概率
        r += reach * (util - node_util)
        return node_util

    def run(self, iters: int = 20_000, seed: int = 0):
        """跑若干轮，返回（平均策略, 先手的平均收益）。"""
        g = np.random.default_rng(seed)
        total = 0.0
        for _ in range(iters):
            deck = g.permutation(3)
            total += self.walk((int(deck[0]), int(deck[1])), "", 1.0, 1.0)
        avg = {}
        for k, s in self.strat.items():
            avg[k] = s / s.sum() if s.sum() > 0 else np.ones(2) / 2
        return avg, total / iters

    # ---- 可利用度：对手照最优应对来打，平均每局能多赢多少

    INFOSETS = {0: ("J", "Q", "K", "Jpb", "Qpb", "Kpb"),          # 先手看得见的六种处境
                1: ("Jb", "Qb", "Kb", "Jp", "Qp", "Kp")}          # 后手的六种

    def exploitability(self, avg: dict[str, np.ndarray]) -> float:
        """两家各自被最优应对时多输的，取平均。均衡处这个数趋于零。

        最优应对**不能逐局挑**——同一个信息集里看不见对方的牌。所以这里老老实实把
        六个信息集的 2^6 = 64 种纯策略全枚举一遍，取最好的那一种，不会算高。
        """
        loss = []
        for me in (0, 1):
            best = max(self._pure_value(avg, me, k) for k in range(64))
            loss.append(best - (KUHN_VALUE if me == 0 else -KUHN_VALUE))
        return float(np.mean(loss))

    def _pure_value(self, avg, me: int, k: int) -> float:
        """我用第 k 种纯策略、对手用 avg 时，我的期望收益（枚举全部六种发牌）。"""
        pure = {h: (k >> i) & 1 for i, h in enumerate(self.INFOSETS[me])}
        total = 0.0
        for c0 in range(3):
            for c1 in range(3):
                if c0 != c1:
                    total += self._mix(avg, pure, (c0, c1), "", me) / 6
        return total

    def _mix(self, avg, pure, cards, history, me):
        player = len(history) % 2
        u = kuhn_terminal(history, cards[0], cards[1])
        if u is not None:
            return u if me == 0 else -u
        key = CARDS[cards[player]] + history
        if player == me:
            return self._mix(avg, pure, cards, history + "pb"[pure[key]], me)
        sigma = avg.get(key, np.ones(2) / 2)
        return sum(sigma[a] * self._mix(avg, pure, cards, history + ch, me) for a, ch in enumerate("pb"))


# ---------------------------------------------------------------- 四、循环克制（15.6 节）
# 三种 AGV 调度规则互相克制：最近任务优先、最久等待优先、最短作业优先。
# 它们在不同的订单结构下互有胜负，构成一个石头剪刀布式的循环——自我对弈不保证越打越强。

CYCLE = np.array([[0.0, 1.0, -1.0],
                  [-1.0, 0.0, 1.0],
                  [1.0, -1.0, 0.0]])
RULES = ("最近任务优先", "最久等待优先", "最短作业优先")


def self_play_cycle(payoff: np.ndarray = CYCLE, rounds: int = 60, seed: int = 0):
    """每一轮都针对“上一轮的对手”训练最优应对，看策略怎样转圈。返回每轮选的策略编号。"""
    g = np.random.default_rng(seed)
    cur = int(g.integers(len(payoff)))
    out = [cur]
    for _ in range(rounds - 1):
        cur = int(np.argmax(payoff[:, cur]))               # 对上一轮的对手取最优应对
        out.append(cur)
    return np.array(out)


# ---------------------------------------------------------------- 五、AGV 调度（15.8 节）
# 车间里 n 台 AGV、若干取送点。订单随机来（取件点 → 送达点）。每当有车空闲且有单在等，
# 就要决定“这台车去接哪一单”。规则基线是最近任务优先；也可以学一个价值出来。

N_STATIONS = 6
STATIONS = np.array([[0.0, 0.0], [12.0, 0.0], [24.0, 0.0],
                     [0.0, 18.0], [12.0, 18.0], [24.0, 18.0]])    # 工位坐标（米）
SPEED = 1.2                                                       # AGV 速度（米/秒）
LOAD_S = 20.0                                                     # 取放一次货的时间（秒）


def dist(a: int, b: int) -> float:
    return float(np.abs(STATIONS[a] - STATIONS[b]).sum())         # 车间里只能走直角通道


class AGVShop:
    """一个最简单的车间搬运场景：订单按泊松过程来，每台车一次运一单。

    状态里真正有用的只有几件事：这台车在哪、各单等了多久、各单要走多远。
    动作就是“这台空闲车去接等待队列里的哪一单”。
    """

    def __init__(self, n_agv: int = 3, rate: float = 1 / 45, horizon: float = 7200.0, seed: int = 0):
        self.n_agv, self.rate, self.horizon = n_agv, rate, horizon
        self.seed = seed

    def _orders(self):
        g = np.random.default_rng(self.seed)
        t, out = 0.0, []
        while t < self.horizon:
            t += g.exponential(1 / self.rate)
            if t >= self.horizon:
                break
            a = int(g.integers(N_STATIONS))
            b = int(g.integers(N_STATIONS))
            while b == a:
                b = int(g.integers(N_STATIONS))
            out.append({"t": t, "from": a, "to": b})
        return out

    def run(self, policy, seed: int | None = None):
        """按给定的策略跑一遍。policy(车位置, 候选单, 当前时刻) 返回要接的那一单在列表里的下标。"""
        if seed is not None:
            self.seed = seed
        orders = self._orders()
        free_at = np.zeros(self.n_agv)                 # 每台车什么时候空出来
        where = np.zeros(self.n_agv, dtype=int)        # 每台车空出来时在哪个工位
        pending, done, waits, empty_km = [], 0, [], 0.0
        i, t = 0, 0.0
        while i < len(orders) or pending:
            k = int(np.argmin(free_at))                # 下一台空出来的车
            t = max(free_at[k], t)
            while i < len(orders) and orders[i]["t"] <= t:   # 这之前来的单都进队列
                pending.append(orders[i])
                i += 1
            if not pending:
                if i < len(orders):
                    t = orders[i]["t"]
                    continue
                break
            j = policy(where[k], pending, t)
            o = pending.pop(j)
            go = dist(where[k], o["from"]) / SPEED           # 空驶：开过去接
            haul = dist(o["from"], o["to"]) / SPEED          # 载货
            empty_km += dist(where[k], o["from"])
            waits.append(t - o["t"] + go)                    # 这一单从下达到被送上车等了多久
            free_at[k] = t + go + LOAD_S + haul + LOAD_S
            where[k] = o["to"]
            done += 1
        makespan = float(free_at.max())                  # 最后一单送到的时刻
        return {"done": done, "wait_mean": float(np.mean(waits)), "wait_p95": float(np.percentile(waits, 95)),
                "wait_max": float(np.max(waits)), "empty_m": empty_km, "empty_per_job": empty_km / max(done, 1),
                "makespan_h": makespan / 3600, "throughput": done / (makespan / 3600),
                "overtime_min": max(0.0, makespan - self.horizon) / 60}


def nearest_policy(at: int, pending: list, t: float) -> int:
    """规则基线：谁近接谁。"""
    return int(np.argmin([dist(at, o["from"]) for o in pending]))


def oldest_policy(at: int, pending: list, t: float) -> int:
    """另一条规则：谁等得久接谁。"""
    return int(np.argmax([t - o["t"] for o in pending]))


def weighted_policy(w_dist: float, w_wait: float):
    """学出来的那一类策略长这样：按“空驶距离”与“已等时间”加权打分，取分最高的。
    15.8 节要学的就是这两个权重——它们正是奖励函数里两项的比。"""
    def pol(at: int, pending: list, t: float) -> int:
        score = [-w_dist * dist(at, o["from"]) + w_wait * (t - o["t"]) for o in pending]
        return int(np.argmax(score))
    return pol

# ---------------------------------------------------------------- 六、函数逼近会出什么事（15.2 节）
# 状态一多就记不下一张表，得用函数去拟合价值。可是"自己估自己"（自举）、"学的策略与取样的
# 策略不是同一个"（离策略）、"用函数逼近"这三件事凑在一起，可以**发散**——价值不是估不准，
# 是飞到无穷。这不是经验之谈，是有反例的：下面这个七状态的例子出自 Baird（1995）。

BAIRD_N = 7


def baird_features() -> np.ndarray:
    """Baird 反例的特征：8 个权重、7 个状态。前六个状态长一个样（权重 i 上是 2、末位是 1），
    第七个状态不同（权重 7 上是 1、末位是 2）。真实价值全是 0，用这 8 个权重当然表示得出来。"""
    X = np.zeros((BAIRD_N, 8))
    for i in range(6):
        X[i, i] = 2.0
        X[i, 7] = 1.0
    X[6, 6] = 1.0
    X[6, 7] = 2.0
    return X


def baird(steps: int = 2000, lr: float = 0.01, gamma: float = 0.99,
          target_every: int = 0, on_policy: bool = False, seed: int = 0):
    """半梯度 TD(0)：奖励全是 0，所以真实价值全是 0，权重本该待着不动。

    behaviour：六分之七的概率散开到前六个状态，七分之一走到第七个状态；
    target：永远走第七个状态。两者不一样，就是"离策略"。
    target_every>0 时把自举用的那份权重冻住，每隔这么多步再更新一次（这就是目标网络）。
    on_policy=True 时取样的策略与学的策略相同，三件事缺了一件。
    返回每一步的权重范数。
    """
    rng = np.random.default_rng(seed)
    X = baird_features()
    w = np.array([1.0, 1, 1, 1, 1, 1, 10, 1])
    wt = w.copy()
    out = []
    s = int(rng.integers(BAIRD_N))
    for t in range(steps):
        solid = rng.random() < 1 / 7 or on_policy    # 取样用的动作
        s2 = 6 if solid else int(rng.integers(6))
        rho = 1.0 if on_policy else (7.0 if solid else 0.0)   # 重要性比：目标策略只走实线
        boot = wt if target_every else w
        td = 0.0 + gamma * float(X[s2] @ boot) - float(X[s] @ w)
        w += lr * rho * td * X[s]
        if target_every and (t + 1) % target_every == 0:
            wt = w.copy()
        s = s2
        out.append(float(np.linalg.norm(w)))
    return np.array(out), w


# ---------------------------------------------------------------- 六、函数逼近与两件救命的事（15.2 节）
# 状态一多就记不下一张表，得用函数去拟合 Q。可是"自己估自己"（自举）加上"按自己的策略取样"
# （相关的数据）加上函数逼近，三件事凑在一起就可能发散。经验回放与目标网络各治其中一件。
