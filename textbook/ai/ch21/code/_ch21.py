"""第 21 章（智能制造与质量检测）共用的玩具模型。

全章一条纪律：**不依赖深度学习框架、不联网、不下载任何数据**。本章要讲清的几件事
——数据在哪一层丢掉、不良率怎样把指标压垮、代价怎样决定阈值、故障频率怎么算、
划分口径为什么第四次出现、剩余寿命的成绩不是均方误差、控制限不是规格限——
都是**统计与决策问题**，在合成数据上能算到底，而且每一条都能与解析值核对。

真实产线的数据不在本仓库里（也不该在），所以这里的"车间"是 `factory/plants/wenquest-gearbox.yaml`
那座厂的简化：同样的工位名、同样的工序顺序，数值全部由程序生成。
"""
from __future__ import annotations

import math

import numpy as np

# ================================================================ 一、数据链（21.1 节）
#
# 三层：传感器（毫秒级、本地时钟）、制造执行系统（工序级、车间服务器时钟）、
# 企业资源计划（订单级、公司时钟）。三层的时钟不一定对齐，而且越往上记录越稀。

STATIONS = ["带锯床", "数控车床 A", "数控车床 B", "立式加工中心", "键槽铣床",
            "滚齿机", "热处理炉", "外圆磨床", "轴承压装工位", "装配工位",
            "跑合试验台", "检验站"]


def make_batch(n_parts: int, seed: int = 0, drift_s: float = 0.0,
               mes_round_s: float = 60.0) -> dict:
    """造一个批次在三层里留下的记录。

    * 传感器层：每个零件在每个工位的**真实**开始与结束时刻（秒，连续）；
    * 制造执行系统：把时刻按 `mes_round_s` 取整（工人扫码不是实时的），并整体偏移 `drift_s`；
    * 企业资源计划：只有这个批次的开工与完工两个时刻（按天记）。

    `drift_s` 就是"两台服务器的时钟差"——本章 21.1 节要算的正是它带来的后果。
    """
    g = np.random.default_rng(seed)
    base = {"带锯床": 40, "数控车床 A": 95, "数控车床 B": 95, "立式加工中心": 140,
            "键槽铣床": 60, "滚齿机": 210, "热处理炉": 900, "外圆磨床": 120,
            "轴承压装工位": 45, "装配工位": 180, "跑合试验台": 300, "检验站": 70}
    t = 0.0
    sensor, mes = [], []
    for i in range(n_parts):
        for st in STATIONS:
            dur = base[st] * float(g.lognormal(0.0, 0.12))
            wait = float(g.exponential(18.0))
            t += wait
            sensor.append({"part": i, "station": st, "start": t, "end": t + dur})
            mes.append({"part": i, "station": st,
                        "start": math.floor((t + drift_s) / mes_round_s) * mes_round_s,
                        "end": math.ceil((t + dur + drift_s) / mes_round_s) * mes_round_s})
            t += dur
    erp = {"start_day": 0.0, "end_day": math.ceil(t / 86400.0)}
    return {"sensor": sensor, "mes": mes, "erp": erp, "n_parts": n_parts}


def cycle_time(rows: list[dict], station: str) -> float:
    """某个工位的平均加工时长（秒）。"""
    xs = [r["end"] - r["start"] for r in rows if r["station"] == station]
    return float(np.mean(xs)) if xs else float("nan")


def busy_share(rows: list[dict], station: str) -> float:
    """这个工位在"从第一件开始到最后一件结束"的时间里有多少比例在加工。"""
    xs = [r for r in rows if r["station"] == station]
    if not xs:
        return float("nan")
    span = max(r["end"] for r in xs) - min(r["start"] for r in xs)
    work = sum(r["end"] - r["start"] for r in xs)
    return float(work / span) if span > 0 else float("nan")


# ================================================================ 二、检测指标与代价（21.2 节）


def confusion(scores_good: np.ndarray, scores_bad: np.ndarray, thr: float) -> dict:
    """分数大于阈值判为"不良"。返回四格表。"""
    tp = int(np.sum(scores_bad >= thr))
    fn = int(np.sum(scores_bad < thr))
    fp = int(np.sum(scores_good >= thr))
    tn = int(np.sum(scores_good < thr))
    return {"tp": tp, "fn": fn, "fp": fp, "tn": tn}


def metrics(c: dict) -> dict:
    """由四格表算出常印的几个指标。分母为 0 时按惯例取 0。"""
    tp, fn, fp, tn = c["tp"], c["fn"], c["fp"], c["tn"]
    n = tp + fn + fp + tn
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    return {"accuracy": (tp + tn) / n if n else 0.0,
            "precision": prec, "recall": rec,
            "f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0,
            "fpr": fp / (fp + tn) if fp + tn else 0.0}


def sample_scores(n: int, defect_rate: float, sep: float = 2.2, seed: int = 0,
                  sigma_bad: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """造一批零件的检测分数：好件 N(0,1)，坏件 N(sep, sigma_bad²)。

    `sep` 就是这个检测器的本事（两类分开多远），它**不随不良率变**——
    本章要说明的正是：同一个检测器，不良率一变，印出来的指标就变。
    """
    g = np.random.default_rng(seed)
    n_bad = int(round(n * defect_rate))
    good = g.normal(0.0, 1.0, n - n_bad)
    bad = g.normal(sep, sigma_bad, n_bad)
    return good, bad


def cost_of(c: dict, cost_miss: float, cost_false: float) -> float:
    """一批零件的总代价：漏检一个赔 cost_miss，误判一个花 cost_false（复检/报废）。"""
    return c["fn"] * cost_miss + c["fp"] * cost_false


def best_threshold(good: np.ndarray, bad: np.ndarray, cost_miss: float,
                   cost_false: float, grid: np.ndarray | None = None) -> tuple[float, float]:
    """扫一遍阈值，返回（总代价最小的阈值，那时的代价）。"""
    if grid is None:
        grid = np.linspace(-3.0, 6.0, 901)
    best, best_cost = float(grid[0]), float("inf")
    for thr in grid:
        cost = cost_of(confusion(good, bad, float(thr)), cost_miss, cost_false)
        if cost < best_cost:
            best, best_cost = float(thr), float(cost)
    return best, best_cost


def per_part(scores: np.ndarray, views: int, how: str = "max") -> np.ndarray:
    """一个零件拍 `views` 张图：把图片级的分数合成零件级的分数。

    ``max``：任何一张判为不良，这个零件就是不良（产线常用，也最容易把误判放大）；
    ``mean``：取平均（更稳，但漏检会变多）。
    """
    n = len(scores) // views * views
    m = scores[:n].reshape(-1, views)
    return m.max(axis=1) if how == "max" else m.mean(axis=1)


# ================================================================ 三、振动与轴承故障频率（21.3 节）
#
# 滚动轴承的几何决定了四个特征频率。它们是解析式，算例要与频谱里找到的峰对上。


def bearing_freqs(n_balls: int, d_ball: float, d_pitch: float, rpm: float,
                  contact_deg: float = 0.0) -> dict:
    """四个特征频率（Hz）。f_r 是轴频，其余按标准几何公式。

    BPFO 外圈、BPFI 内圈、BSF 滚动体、FTF 保持架。
    """
    fr = rpm / 60.0
    ratio = d_ball / d_pitch * math.cos(math.radians(contact_deg))
    return {"fr": fr,
            "BPFO": n_balls / 2.0 * fr * (1 - ratio),
            "BPFI": n_balls / 2.0 * fr * (1 + ratio),
            "BSF": d_pitch / (2 * d_ball) * fr * (1 - ratio ** 2),
            "FTF": fr / 2.0 * (1 - ratio)}


def bearing_signal(fs: float, seconds: float, fault_hz: float, rpm: float,
                   carrier_hz: float = 3200.0, noise: float = 0.35,
                   decay: float = 900.0, seed: int = 0) -> np.ndarray:
    """合成一段带局部故障的振动：每隔 1/fault_hz 来一次冲击，冲击激起一段衰减振荡。

    这正是教科书里"故障信号被高频共振调制"的样子——**所以要用包络谱才看得见故障频率**。
    """
    g = np.random.default_rng(seed)
    n = int(fs * seconds)
    t = np.arange(n) / fs
    x = noise * g.normal(0.0, 1.0, n)
    x += 0.25 * np.sin(2 * np.pi * (rpm / 60.0) * t)          # 不平衡：轴频分量
    period = 1.0 / fault_hz
    k = 0
    while k * period < seconds:
        i0 = int(k * period * fs)
        m = min(n - i0, int(0.004 * fs))
        if m > 0:
            tt = np.arange(m) / fs
            amp = 1.0 * (1.0 + 0.1 * float(g.normal()))
            x[i0:i0 + m] += amp * np.exp(-decay * tt) * np.sin(2 * np.pi * carrier_hz * tt)
        k += 1
    return x


def spectrum(x: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """单边幅值谱。"""
    n = len(x)
    w = np.hanning(n)
    X = np.abs(np.fft.rfft(x * w)) / n * 2
    f = np.fft.rfftfreq(n, 1.0 / fs)
    return f, X


def envelope(x: np.ndarray) -> np.ndarray:
    """包络：用希尔伯特变换的幅值（这里用 FFT 自己实现，不引 scipy）。"""
    n = len(x)
    X = np.fft.fft(x)
    h = np.zeros(n)
    h[0] = 1
    if n % 2 == 0:
        h[n // 2] = 1
        h[1:n // 2] = 2
    else:
        h[1:(n + 1) // 2] = 2
    return np.abs(np.fft.ifft(X * h))


def peak_near(f: np.ndarray, X: np.ndarray, target: float, window: float) -> tuple[float, float]:
    """在 target ± window 里找最高的峰，返回（频率，幅值）。"""
    m = (f >= target - window) & (f <= target + window)
    if not np.any(m):
        return float("nan"), 0.0
    i = int(np.argmax(X[m]))
    return float(f[m][i]), float(X[m][i])


# ================================================================ 四、划分口径（21.3 节，第四次）


def make_runs(n_machines: int = 8, per_machine: int = 8, seconds: float = 0.5,
              fs: float = 12000.0, seed: int = 0) -> list[dict]:
    """造若干台机床、每台按时间先后采集若干次。

    现场数据的三条特点这里都有：
    * **同一台机床的几次采集彼此很像**（同一个共振频率、同一档底噪）——随机划分会把它们分到两边；
    * **故障是慢慢长出来的**：每台机床有自己的起病时刻，之后冲击一次比一次重；
    * **越往后坏的越多**：所以"拿过去训、拿未来测"比随机划分难，而这才是现场的问法。
    """
    g = np.random.default_rng(seed)
    runs = []
    for m in range(n_machines):
        carrier = 2400.0 + 420.0 * (m % 5)                  # 这台机床的共振频率
        noise = 0.30 + 0.05 * (m % 3)
        never = (m % 4 == 0)                                # 四分之一的机床一直没坏
        onset = per_machine if never else int(g.integers(1, per_machine - 1))
        for k in range(per_machine):
            rpm = 1750.0 + 20.0 * float(g.normal())
            n = int(fs * seconds)
            t = np.arange(n) / fs
            if k < onset:
                x = noise * g.normal(0.0, 1.0, n) + 0.25 * np.sin(2 * np.pi * rpm / 60.0 * t)
                fault = 0
            else:
                sev = 0.35 + 0.65 * (k - onset) / max(1, per_machine - onset)   # 越往后越重
                hz = bearing_freqs(9, 7.94, 39.04, rpm)["BPFO"]
                x = sev * bearing_signal(fs, seconds, hz, rpm, carrier_hz=carrier,
                                         noise=noise / max(sev, 1e-6) * sev,
                                         seed=int(g.integers(1 << 30)))
                fault = 1
            runs.append({"machine": m, "run": k, "t": int(k), "fault": fault,
                         "x": x, "rpm": rpm, "fs": fs, "onset": onset})
    return runs


def features(run: dict, n_band: int = 12) -> np.ndarray:
    """一条信号的特征：几个频带的能量 + 均方根 + 峭度（都是车间里真用的量）。"""
    f, X = spectrum(run["x"], run["fs"])
    edges = np.linspace(0, run["fs"] / 2, n_band + 1)
    band = [float(np.sum(X[(f >= edges[i]) & (f < edges[i + 1])] ** 2)) for i in range(n_band)]
    x = run["x"]
    rms = float(np.sqrt(np.mean(x ** 2)))
    kurt = float(np.mean((x - x.mean()) ** 4) / (np.var(x) ** 2 + 1e-12))
    return np.array(band + [rms, kurt], dtype=float)


def split_runs(runs: list[dict], how: str, seed: int = 0,
               test_frac: float = 0.25) -> tuple[list[dict], list[dict]]:
    """三种划分：``random`` 按采集随机、``machine`` 按机床、``time`` 按时间（后面的留作测试）。"""
    g = np.random.default_rng(seed)
    if how == "random":
        idx = g.permutation(len(runs))
        cut = max(1, int(len(runs) * test_frac))
        return [runs[i] for i in idx[cut:]], [runs[i] for i in idx[:cut]]
    if how == "machine":
        ms = sorted({r["machine"] for r in runs})
        held = set(g.permutation(ms)[:max(1, int(round(len(ms) * test_frac)))].tolist())
        return [r for r in runs if r["machine"] not in held], [r for r in runs if r["machine"] in held]
    if how == "time":
        ts = sorted({r["t"] for r in runs})
        cut = ts[max(1, int(len(ts) * (1 - test_frac)))]
        return [r for r in runs if r["t"] < cut], [r for r in runs if r["t"] >= cut]
    raise ValueError(how)


def logistic_fit(X: np.ndarray, y: np.ndarray, steps: int = 4000, lr: float = 0.25,
                 l2: float = 1e-3) -> np.ndarray:
    """最简单的逻辑回归（梯度下降，自己写，不引框架）。特征先标准化。"""
    X = np.column_stack([np.ones(len(X)), X])
    w = np.zeros(X.shape[1])
    for _ in range(steps):
        p = 1.0 / (1.0 + np.exp(-X @ w))
        grad = X.T @ (p - y) / len(y) + l2 * np.r_[0.0, w[1:]]
        w -= lr * grad
    return w


def logistic_acc(w: np.ndarray, X: np.ndarray, y: np.ndarray) -> float:
    p = 1.0 / (1.0 + np.exp(-np.column_stack([np.ones(len(X)), X]) @ w))
    return float(np.mean((p >= 0.5).astype(float) == y))


def standardize(train: np.ndarray, test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """**用训练集的均值方差去标准化测试集**（用全体的就是另一种泄漏）。"""
    mu, sd = train.mean(axis=0), train.std(axis=0) + 1e-9
    return (train - mu) / sd, (test - mu) / sd


# ================================================================ 五、退化与维护决策（21.3、21.8 节）


def degradation(n_steps: int, rate: float, noise: float, seed: int = 0,
                start: float = 0.0) -> np.ndarray:
    """一台设备的退化曲线：单调上升 + 测量噪声。到 1.0 算失效。"""
    g = np.random.default_rng(seed)
    inc = np.abs(g.normal(rate, rate * 0.35, n_steps))
    true = start + np.cumsum(inc)
    return true + noise * g.normal(0.0, 1.0, n_steps)


def first_cross(x: np.ndarray, thr: float) -> int | None:
    """第一次越过阈值的位置；一直没越过返回 None。"""
    idx = np.nonzero(x >= thr)[0]
    return int(idx[0]) if len(idx) else None


def maintenance_cost(fleet: list[np.ndarray], thr: float, fail_at: float = 1.0,
                     cost_plan: float = 1.0, cost_fail: float = 12.0,
                     cost_early: float = 0.02) -> dict:
    """一队设备按同一个报警阈值做维护，算总代价。

    * 报警后按计划停机：花 `cost_plan`；
    * 没报警就失效（或报警太晚）：花 `cost_fail`（含意外停机与连带损失）；
    * 报得太早：每提前一个周期浪费 `cost_early`（剩余寿命白扔）。
    """
    plan = fail = survived = 0
    waste = 0.0
    leads = []
    for x in fleet:
        t_fail = first_cross(x, fail_at)
        t_alarm = first_cross(x, thr)
        if t_fail is None:                       # 到期还没坏：既没停机也没失效
            if t_alarm is not None:              # 但报过警就得按计划停一次（而且是白停）
                plan += 1
                waste += cost_early * (len(x) - 1 - t_alarm)
                leads.append(len(x) - 1 - t_alarm)
            else:
                survived += 1
            continue
        if t_alarm is None or t_alarm >= t_fail:
            fail += 1
            leads.append(0)
        else:
            plan += 1
            lead = t_fail - t_alarm
            leads.append(lead)
            waste += cost_early * lead
    total = plan * cost_plan + fail * cost_fail + waste
    return {"n": len(fleet), "planned": plan, "failed": fail, "survived": survived,
            "early_waste": float(waste), "total": float(total),
            "lead_mean": float(np.mean(leads)) if leads else 0.0,
            "lead_min": int(np.min(leads)) if leads else 0}


# ================================================================ 六、控制图与过程能力（21.5 节）


def xbar_limits(groups: np.ndarray, a2: float) -> dict:
    """均值-极差图的控制限。groups 是 (子组数, 子组大小)。"""
    means = groups.mean(axis=1)
    ranges = groups.max(axis=1) - groups.min(axis=1)
    xbb, rb = float(means.mean()), float(ranges.mean())
    return {"center": xbb, "ucl": xbb + a2 * rb, "lcl": xbb - a2 * rb, "rbar": rb}


A2 = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483}     # 标准系数表（常用子组大小）
D3 = {2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0}
D4 = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004}
D2 = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534}     # Rbar/d2 用来估 sigma


def capability(mu: float, sigma: float, lsl: float, usl: float) -> dict:
    """过程能力指数。Cp 只看宽度，Cpk 还看偏心——两者的差就是"中心偏了多少"。"""
    cp = (usl - lsl) / (6 * sigma)
    cpk = min((usl - mu) / (3 * sigma), (mu - lsl) / (3 * sigma))
    return {"cp": float(cp), "cpk": float(cpk)}


def out_of_spec_ppm(mu: float, sigma: float, lsl: float, usl: float) -> float:
    """超出规格的比例（百万分之几），按正态分布算。"""
    def phi(z):
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return float((phi((lsl - mu) / sigma) + 1.0 - phi((usl - mu) / sigma)) * 1e6)


def run_chart(n_groups: int, n_sub: int, shift_at: int | None = None,
              shift: float = 0.0, spread: float = 1.0, seed: int = 0,
              mu: float = 0.0, sigma: float = 1.0) -> np.ndarray:
    """造一段过程数据：前面稳定，shift_at 之后均值漂移 shift 个标准差、方差乘 spread。"""
    g = np.random.default_rng(seed)
    out = np.empty((n_groups, n_sub))
    for i in range(n_groups):
        m = mu + (shift * sigma if shift_at is not None and i >= shift_at else 0.0)
        s = sigma * (spread if shift_at is not None and i >= shift_at else 1.0)
        out[i] = g.normal(m, s, n_sub)
    return out


def alarms(groups: np.ndarray, lim: dict) -> np.ndarray:
    """哪些子组报警（只用最基本的一条判据：均值出界）。"""
    means = groups.mean(axis=1)
    return (means > lim["ucl"]) | (means < lim["lcl"])


# ================================================================ 七、工艺参数优化（21.4 节）
#
# 与 20.5 节的闭环同一套想法，换到切削参数上，但**多了产线的三条约束**：
# 一次只能动一点点（工人要跟得上、设备要稳得住）、试出来的废品是真花钱的、
# 一个班只有有限次试验。


def cut_rate(speed: float, feed: float) -> float:
    """产出速度（越大越好，归一化到 0—1 附近）。切得快、进给大，产出就高。"""
    return float(speed * feed)


def cut_quality(speed: float, feed: float) -> float:
    """表面质量（越大越好，1 是满分）。切削速度有一个最舒服的区间，进给越大越差。

    这是个**造出来的玩具曲面**，不代表任何真实材料或刀具。
    """
    s = math.exp(-((speed - 0.62) / 0.26) ** 2)
    f = math.exp(-((feed - 0.28) / 0.30) ** 2)
    return float(0.5 + 0.5 * s * f)


def cut_scrap(speed: float, feed: float) -> bool:
    """这一组参数会不会直接做出废品（质量低于合格线）。"""
    return cut_quality(speed, feed) < 0.72


def cut_objective(speed: float, feed: float) -> float:
    """车间真正要的：在不出废品的前提下产出最大。出废品的点按 0 计。"""
    return 0.0 if cut_scrap(speed, feed) else cut_rate(speed, feed)


def search_parameters(method: str, budget: int, seed: int = 0, step: float = 0.08,
                      start=(0.45, 0.18)) -> dict:
    """在切削参数上试 `budget` 次。三种办法：

    * ``free``：不管约束，在整个参数空间里随机试（研究所的做法）；
    * ``ofat``：一次只动一个因素、走一小步（车间几十年的做法）；
    * ``trust``：代理模型 + **信赖域**——只在当前点附近 `step` 的范围里提议（本章推荐）。

    返回找到的最好点、试坏了多少件、以及每一步的轨迹。
    """
    g = np.random.default_rng(seed)
    cur = np.array(start, dtype=float)
    best, best_val = cur.copy(), cut_objective(*cur)
    scrap = 0
    traj = [cur.copy()]
    tried: list[np.ndarray] = []
    vals: list[float] = []

    for t in range(budget):
        if method == "free":
            nxt = g.uniform(0.05, 0.95, 2)
        elif method == "ofat":
            k = t % 2
            nxt = cur.copy()
            nxt[k] = float(np.clip(cur[k] + (step if (t // 2) % 2 == 0 else -step), 0.05, 0.95))
        elif method == "trust":
            if len(tried) < 4:
                nxt = np.clip(cur + g.normal(0.0, step, 2), 0.05, 0.95)
            else:
                cand = np.clip(cur + g.normal(0.0, step, (24, 2)), 0.05, 0.95)
                X = np.array(tried)
                y = np.array(vals)
                mean, sigma = kernel_mean_sigma(X, y, cand, ls=0.18)
                nxt = cand[int(np.argmax(mean + 1.0 * sigma))]
        else:
            raise ValueError(method)
        val = cut_objective(*nxt)
        if cut_scrap(*nxt):
            scrap += 1
        tried.append(np.asarray(nxt, dtype=float))
        vals.append(val)
        if val > best_val:
            best, best_val = np.asarray(nxt, dtype=float).copy(), val
        if method in ("ofat", "trust") and val >= cut_objective(*cur):
            cur = np.asarray(nxt, dtype=float).copy()      # 只往不变差的方向挪
        traj.append(cur.copy())
    return {"best": best, "best_val": float(best_val), "scrap": scrap,
            "traj": np.array(traj), "tried": np.array(tried), "vals": np.array(vals)}


def kernel_mean_sigma(X: np.ndarray, y: np.ndarray, Q: np.ndarray, ls: float = 0.18,
                      lam: float = 1e-3) -> tuple[np.ndarray, np.ndarray]:
    """高斯核岭回归的均值，外加"离已测点有多远"当不确定度（与 20.5 节同一套）。"""
    def k(A, B):
        d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
        return np.exp(-d2 / (2 * ls ** 2))

    K = k(X, X) + lam * np.eye(len(X))
    alpha = np.linalg.solve(K, y)
    Kq = k(Q, X)
    return Kq @ alpha, np.sqrt(np.maximum(1.0 - Kq.max(axis=1) ** 2, 0.0))


def best_feasible(grid: int = 201) -> tuple[float, float, float]:
    """网格扫出"不出废品的前提下产出最大"的那个点（用来当真值）。"""
    ax = np.linspace(0.05, 0.95, grid)
    best, bs, bf = -1.0, 0.0, 0.0
    for s in ax:
        for f in ax:
            val = cut_objective(float(s), float(f))
            if val > best:
                best, bs, bf = val, float(s), float(f)
    return bs, bf, best
