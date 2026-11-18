"""第 22 章（能源、电网与工业控制）共用的玩具模型。

全章纪律：**不依赖深度学习框架、不联网、不下载任何数据**。本章要讲清的几件事
——预测误差怎样折成调度成本、分位数为什么比点预测有用、时间序列的划分为什么要留间隔、
储能调度的最优解长什么样、学出来的策略与规则策略差在哪、安全层值多少钱——
都是**预测与决策问题**，在合成数据上能算到底，而且每一条都有可核对的参照
（调度那一步有动态规划给出的真最优解）。

这座"微网"是第 21 章那座减速器厂的延伸：白天屋顶光伏发电，车间按班次用电，
车间里有一组储能。容量、电价都是**显式假设**，写在用它们的算例里。
"""
from __future__ import annotations

import math

import numpy as np

STEPS_PER_DAY = 96          # 15 分钟一个点
DT_H = 24.0 / STEPS_PER_DAY


# ================================================================ 一、光伏与负荷（22.1 节）


def clear_sky(n_days: int = 1, peak_kw: float = 400.0, day_len: float = 12.0) -> np.ndarray:
    """晴空出力：一条半正弦，日出日落之间有出力，其余为零。"""
    t = np.arange(n_days * STEPS_PER_DAY) * DT_H % 24.0
    on = (t > (24 - day_len) / 2) & (t < (24 + day_len) / 2)
    phase = (t - (24 - day_len) / 2) / day_len * math.pi
    return np.where(on, peak_kw * np.sin(np.clip(phase, 0, math.pi)), 0.0)


def cloud_factor(n_days: int, seed: int = 0, calm: float = 0.0) -> np.ndarray:
    """云的遮挡系数（0—1）：慢变的天气型 + 快变的云团。

    `calm` 越大，这几天越接近晴天（本章用它造"不同天气型"）。
    """
    g = np.random.default_rng(seed)
    n = n_days * STEPS_PER_DAY
    slow = np.clip(0.75 + 0.25 * np.sin(np.arange(n) / (STEPS_PER_DAY * 1.7)
                                        + g.uniform(0, 6.28)), 0.35, 1.0)
    fast = np.ones(n)
    k = 0
    while k < n:
        if g.random() < 0.18:
            dur = int(g.integers(2, 10))
            fast[k:k + dur] *= float(g.uniform(0.25, 0.8))
            k += dur
        else:
            k += 1
    f = slow * fast
    return np.clip(f + calm * (1.0 - f), 0.0, 1.0)


def pv_series(n_days: int, seed: int = 0, peak_kw: float = 400.0,
              calm: float = 0.0) -> np.ndarray:
    """一段光伏出力（kW），15 分钟一个点。"""
    return clear_sky(n_days, peak_kw) * cloud_factor(n_days, seed, calm)


def load_series(n_days: int, seed: int = 0, base_kw: float = 120.0,
                shift_kw: float = 260.0) -> np.ndarray:
    """车间负荷（kW）：两班制，白班重、夜班轻，加一点随机。

    形状取自第 21 章那座减速器厂：早 8 点开机，晚 10 点收工，中间有午休的小凹。
    """
    g = np.random.default_rng(seed + 991)
    t = np.arange(n_days * STEPS_PER_DAY) * DT_H % 24.0
    day = ((t >= 8) & (t < 22)).astype(float)
    lunch = np.exp(-((t - 12.0) / 0.6) ** 2) * 0.45
    x = base_kw + shift_kw * day * (1.0 - lunch)
    x *= 1.0 + 0.04 * g.normal(0.0, 1.0, len(t))
    return np.maximum(x, 0.0)


# ================================================================ 二、预测（22.1 节）


def persistence(y: np.ndarray, horizon: int = STEPS_PER_DAY) -> np.ndarray:
    """最笨的基线：明天和今天一样。任何预测模型都要先打赢它。"""
    out = np.empty_like(y)
    out[:horizon] = y[:horizon]
    out[horizon:] = y[:-horizon]
    return out


def climatology(y: np.ndarray) -> np.ndarray:
    """第二个基线：每个时刻取历史同时刻的平均。"""
    m = y.reshape(-1, STEPS_PER_DAY)
    prof = m.mean(axis=0)
    return np.tile(prof, len(m))


def design_matrix(n_days: int, cloud_fc: np.ndarray) -> np.ndarray:
    """特征：晴空出力、预报的云系数、时刻的正余弦。

    这里的"预报云系数"是**带误差的气象预报**，不是真值——正是现实的样子。
    """
    cs = clear_sky(n_days)
    t = np.arange(n_days * STEPS_PER_DAY) * DT_H % 24.0
    return np.column_stack([np.ones_like(cs), cs, cs * cloud_fc,
                            np.sin(2 * np.pi * t / 24), np.cos(2 * np.pi * t / 24)])


def fit_ls(X: np.ndarray, y: np.ndarray, lam: float = 1e-6) -> np.ndarray:
    return np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)


def fit_quantile(X: np.ndarray, y: np.ndarray, q: float, steps: int = 2500,
                 lr: float = 0.02) -> np.ndarray:
    """分位数回归：最小化弹球损失。自己写梯度下降，不引框架。"""
    w = fit_ls(X, y)
    scale = np.abs(X).mean(axis=0) + 1e-9
    for _ in range(steps):
        r = y - X @ w
        g = -X.T @ np.where(r >= 0, q, q - 1.0) / len(y)
        w = w - lr * g / scale
    return w


def pinball(y: np.ndarray, pred: np.ndarray, q: float) -> float:
    r = y - pred
    return float(np.mean(np.maximum(q * r, (q - 1) * r)))


def coverage(y: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> float:
    """区间实际盖住了多少（%）。名义 90% 的区间，实际常常不是 90%。"""
    return float(np.mean((y >= lo) & (y <= hi))) * 100


def interval_width(lo: np.ndarray, hi: np.ndarray) -> float:
    return float(np.mean(hi - lo))


# ================================================================ 三、划分口径（22.1 节，第五次）


def split_time(n: int, test_frac: float = 0.25, gap: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """按时间划分，中间留 `gap` 个点的间隔。

    留间隔是为了**切断窗口重叠带来的泄漏**：特征里用到了前后若干点时，
    紧挨着分界的那些样本在两边都出现过。
    """
    cut = int(n * (1 - test_frac))
    return np.arange(0, max(0, cut - gap)), np.arange(cut, n)


def split_random(n: int, test_frac: float = 0.25, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    g = np.random.default_rng(seed)
    idx = g.permutation(n)
    cut = int(n * (1 - test_frac))
    return idx[:cut], idx[cut:]


# ================================================================ 四、电价与调度成本（22.2 节）


def tou_price(n_days: int, peak: float = 1.05, flat: float = 0.62,
              valley: float = 0.28) -> np.ndarray:
    """分时电价（元/kWh）：峰、平、谷三段。数值是**显式假设**，不代表任何地区的真实电价。"""
    t = np.arange(n_days * STEPS_PER_DAY) * DT_H % 24.0
    p = np.full(len(t), flat)
    p[(t >= 8) & (t < 11)] = peak
    p[(t >= 18) & (t < 21)] = peak
    p[(t < 7) | (t >= 23)] = valley
    return p


def imbalance_cost(actual: np.ndarray, planned: np.ndarray, price: np.ndarray,
                   up: float = 1.6, down: float = 0.5) -> float:
    """偏差成本：实际与申报计划不符要结算，而**两个方向的价钱不一样**。

    少发（actual < planned）按 `up` 倍电价买电补上；多发按 `down` 倍电价贱卖。
    这正是"同样的均方根误差，成本可以差几倍"的来源。
    """
    d = actual - planned
    short = np.maximum(-d, 0.0)
    over = np.maximum(d, 0.0)
    return float(np.sum(short * price * up + over * price * down) * DT_H)


# ================================================================ 五、储能调度（22.2、22.6 节）

BATTERY = {"cap_kwh": 600.0, "p_max_kw": 150.0, "eta": 0.93,
           "soc_min": 0.15, "soc_max": 0.95, "soc0": 0.5}


def dispatch_cost(pv: np.ndarray, load: np.ndarray, price: np.ndarray,
                  charge: np.ndarray, bat: dict = BATTERY,
                  tol: float = 1e-3) -> tuple[float, np.ndarray, int]:
    """给定充放电计划，算电费、荷电状态轨迹与**越界次数**。

    `charge` > 0 表示充电，< 0 表示放电。物理系统不会让荷电状态真的出界：
    电池管理系统会把功率压回可行范围（本函数照此计费）。**被压回去的次数就是越界次数**——
    在真设备上，这是报警、跳闸或寿命损耗，不是免费的。
    """
    soc = bat["soc0"] * bat["cap_kwh"]
    lo, hi = bat["soc_min"] * bat["cap_kwh"], bat["soc_max"] * bat["cap_kwh"]
    viol = 0
    socs = np.empty(len(charge))
    cost = 0.0
    for i, c in enumerate(charge):
        want = float(np.clip(c, -bat["p_max_kw"], bat["p_max_kw"]))
        room_up = (hi - soc) / (bat["eta"] * DT_H)
        room_dn = (soc - lo) * bat["eta"] / DT_H
        c = float(np.clip(want, -room_dn, room_up))
        if abs(c - want) > tol:
            viol += 1                                 # 要不是电池管理系统拦着，这一步就出界了
        grid = load[i] - pv[i] + c                    # 正=从电网买，负=上网
        cost += (grid * price[i] if grid > 0 else grid * price[i] * 0.35) * DT_H
        soc += (c * bat["eta"] if c > 0 else c / bat["eta"]) * DT_H
        soc = float(np.clip(soc, lo, hi))
        socs[i] = soc
    return cost, socs, viol


def optimal_dispatch(pv: np.ndarray, load: np.ndarray, price: np.ndarray,
                     bat: dict = BATTERY, n_soc: int = 61) -> tuple[float, np.ndarray]:
    """动态规划求最优充放电（把荷电状态离散成 n_soc 档）。**这是本章的真值**。"""
    n = len(pv)
    lo, hi = bat["soc_min"] * bat["cap_kwh"], bat["soc_max"] * bat["cap_kwh"]
    grid_soc = np.linspace(lo, hi, n_soc)
    step = grid_soc[1] - grid_soc[0]
    INF = 1e18
    V = np.zeros((n + 1, n_soc))
    A = np.zeros((n, n_soc), dtype=int)
    moves = np.arange(-bat["p_max_kw"], bat["p_max_kw"] + 1e-9, bat["p_max_kw"] / 10)
    for i in range(n - 1, -1, -1):
        best = np.full(n_soc, INF)
        arg = np.zeros(n_soc, dtype=int)
        for mi, c in enumerate(moves):
            d_soc = (c * bat["eta"] if c > 0 else c / bat["eta"]) * DT_H
            nxt = grid_soc + d_soc
            ok = (nxt >= lo - 1e-6) & (nxt <= hi + 1e-6)
            j = np.clip(np.round((nxt - lo) / step).astype(int), 0, n_soc - 1)
            grid = load[i] - pv[i] + c
            step_cost = (grid * price[i] if grid > 0 else grid * price[i] * 0.35) * DT_H
            tot = np.where(ok, step_cost + V[i + 1][j], INF)
            upd = tot < best
            best = np.where(upd, tot, best)
            arg = np.where(upd, mi, arg)
        V[i] = best
        A[i] = arg
    s = int(np.clip(np.round((bat["soc0"] * bat["cap_kwh"] - lo) / step), 0, n_soc - 1))
    plan = np.empty(n)
    for i in range(n):
        c = moves[A[i, s]]
        plan[i] = c
        d_soc = (c * bat["eta"] if c > 0 else c / bat["eta"]) * DT_H
        s = int(np.clip(np.round((grid_soc[s] + d_soc - lo) / step), 0, n_soc - 1))
    return float(V[0, s if False else int(np.clip(np.round((bat["soc0"] * bat["cap_kwh"] - lo) / step), 0, n_soc - 1))]), plan


def rule_dispatch(pv: np.ndarray, load: np.ndarray, price: np.ndarray,
                  bat: dict = BATTERY) -> np.ndarray:
    """车间里最常见的规则：谷电充、峰电放、有余电就存起来。"""
    hi_p = np.quantile(price, 0.75)
    lo_p = np.quantile(price, 0.25)
    out = np.zeros(len(pv))
    for i in range(len(pv)):
        surplus = pv[i] - load[i]
        if surplus > 0:
            out[i] = min(surplus, bat["p_max_kw"])
        elif price[i] <= lo_p:
            out[i] = bat["p_max_kw"] * 0.6
        elif price[i] >= hi_p:
            out[i] = -bat["p_max_kw"]
    return out


def safe_layer(charge: np.ndarray, pv: np.ndarray, load: np.ndarray,
               bat: dict = BATTERY, margin: float = 0.0) -> np.ndarray:
    """安全层：把计划投影到"不会越界"的范围里。**学不出来的那一层，要写出来。**

    `margin` 是**额外留出来的余量**（占总容量的比例）：真设备的效率与可用容量都与标称值
    不一样，只按标称值投影，等于把余量全交给电池管理系统去兜。留余量要花钱——
    这笔钱就是安全层的价钱，算例会把它算出来。
    """
    soc = bat["soc0"] * bat["cap_kwh"]
    lo = (bat["soc_min"] + margin) * bat["cap_kwh"]
    hi = (bat["soc_max"] - margin) * bat["cap_kwh"]
    soc = float(np.clip(soc, lo, hi))
    out = np.empty(len(charge))
    for i, c in enumerate(charge):
        c = float(np.clip(c, -bat["p_max_kw"], bat["p_max_kw"]))
        room_up = (hi - soc) / (bat["eta"] * DT_H)
        room_dn = (soc - lo) * bat["eta"] / DT_H
        c = float(np.clip(c, -room_dn, room_up))
        out[i] = c
        soc += (c * bat["eta"] if c > 0 else c / bat["eta"]) * DT_H
        soc = float(np.clip(soc, lo, hi))
    return out


# ================================ 四、约束下的连续控制：机房冷却（22.3 节）

HALL = {
    "c_th": 1200.0,        # 机房热容（kWh/℃），显式假设
    "ua": 9.0,             # 与室外的换热系数（kW/℃）
    "t_max": 27.0,         # 冷通道温度上限（℃），超过就算越界
    "t_min": 18.0,         # 低于这个温度是白花钱
    "t0": 23.0,            # 初始温度（℃）
    "cool_max": 750.0,     # 冷机最大制冷量（kW）
}


def it_load(n_days: int, seed: int = 0, base_kw: float = 260.0,
            peak_kw: float = 230.0) -> np.ndarray:
    """机房的 IT 热负荷（kW）：白天忙、夜里闲，偶尔来一波批量作业。"""
    g = np.random.default_rng(seed + 4201)
    t = np.arange(n_days * STEPS_PER_DAY) * DT_H % 24.0
    shape = 0.5 + 0.5 * np.sin((t - 9.0) / 24.0 * 2 * math.pi)
    x = base_kw + peak_kw * shape
    for _ in range(n_days * 2):                      # 批量作业：突然加载，持续一两小时
        i = int(g.integers(0, n_days * STEPS_PER_DAY))
        w = int(g.integers(4, 10))
        x[i:i + w] += peak_kw * 0.55
    x *= 1.0 + 0.03 * g.normal(0.0, 1.0, len(t))
    return np.maximum(x, 0.0)


def ambient(n_days: int, seed: int = 0, mean_c: float = 24.0,
            swing_c: float = 7.0) -> np.ndarray:
    """室外温度（℃）：日变化 + 几天尺度的慢变化。"""
    g = np.random.default_rng(seed + 613)
    t = np.arange(n_days * STEPS_PER_DAY) * DT_H
    daily = -np.cos((t % 24.0 - 3.0) / 24.0 * 2 * math.pi)
    slow = np.convolve(g.normal(0, 1, len(t) + 400), np.ones(400) / 400, "same")[:len(t)]
    return mean_c + swing_c * 0.5 * daily + 3.0 * slow * 4.0


def cop(t_amb: np.ndarray | float, cop0: float = 5.6, k: float = 0.085):
    """冷机能效比：室外越热，同样的制冷量越费电。**这是本节省电空间的来源**。"""
    return np.maximum(cop0 - k * (np.asarray(t_amb) - 20.0), 1.6)


def run_hall(policy, n_days: int, seed: int = 0, hall: dict = HALL,
             gain: float = 1.0, safety: bool = False) -> dict:
    """把一个控制策略放进机房跑一遍，返回电耗、越界次数与温度轨迹。

    `policy(t_now, t_amb, q_it, k)` 返回制冷量（kW）。`gain` 是**真实设备与仿真的差别**：
    真实冷机的制冷量比仿真里标称的少一点（gain < 1）。`safety` 打开时，
    外面那层会在温度快要越界前把制冷量顶到最大——**学不出来的那一层，要写出来**。
    """
    q = it_load(n_days, seed)
    amb = ambient(n_days, seed)
    n = len(q)
    t_now = hall["t0"]
    temps = np.empty(n)
    kwh = 0.0
    viol = 0
    over = 0.0
    for k in range(n):
        u = float(policy(t_now, amb[k], q[k], k))
        if safety:
            # 预测下一步的温度：要越界就顶到最大
            nxt = t_now + (q[k] - u * gain + hall["ua"] * (amb[k] - t_now)) / hall["c_th"] * DT_H
            if nxt > hall["t_max"] - 0.3:
                u = hall["cool_max"]
        u = float(np.clip(u, 0.0, hall["cool_max"]))
        kwh += u / float(cop(amb[k])) * DT_H
        t_now += (q[k] - u * gain + hall["ua"] * (amb[k] - t_now)) / hall["c_th"] * DT_H
        temps[k] = t_now
        if t_now > hall["t_max"]:
            viol += 1
            over += (t_now - hall["t_max"]) * DT_H
    return {"kwh": kwh, "viol": viol, "over_degh": over, "temps": temps,
            "amb": amb, "q": q, "t_max": hall["t_max"]}


def setpoint_policy(setpoint: float, kp: float = 240.0, hall: dict = HALL):
    """规则控制：盯住一个设定温度，差多少补多少（比例控制）。"""
    def f(t_now, t_amb, q_it, k):
        return q_it + hall["ua"] * (t_amb - t_now) + kp * (t_now - setpoint)
    return f


def learned_policy(setpoint: float, kp: float, lead: float, hall: dict = HALL):
    """“学出来的”策略：同样的结构，但多用了两件仿真里学到的事——

    设定温度可以贴着上限走（省电），而且可以**借室外温度提前动**（lead）。
    参数由算例在仿真里搜出来，不是手写的。
    """
    def f(t_now, t_amb, q_it, k):
        return (q_it + hall["ua"] * (t_amb - t_now) + kp * (t_now - setpoint)
                + lead * (t_amb - 24.0))
    return f
