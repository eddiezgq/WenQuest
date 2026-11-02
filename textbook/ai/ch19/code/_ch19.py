"""第 19 章共用的玩具模型：平流格式与稳定性、混沌与可预报性、"越推越平"、集合与概率
评分、降尺度、遥感的划分口径，以及案例的风功率账。

**为什么全是玩具**：这一章要讲清的几件事——"为什么提高分辨率这么贵""提前多久还能信"
"自回归推进为什么会越推越平""RMSE 低为什么不等于预报好""随机像素划分为什么会高估"——
都是**数值方法与概率问题**，不是气象问题。真模式上这些量测不准（每一次都混着分辨率、
物理参数化、同化、初始场好几件事），而退到一维平流、洛伦兹系统与可控的谱模型上，每一条
都能算到底，还能与解析值核对。真模型上的对照放在两个云端 GPU 实验里。

仓库里不放任何气象或遥感数据；所有场、集合、卫星图块都由程序按规则生成。
"""
from __future__ import annotations

import numpy as np

# ================================================================ 一、平流与稳定性（19.1 节）


def advect_upwind(u0: np.ndarray, c: float, n_steps: int) -> np.ndarray:
    """一维线性平流的显式迎风格式。`c` 是库朗数 C = uΔt/Δx。

    显式格式的稳定条件是 C ≤ 1：**信息一步不能跨过一个格距**。C > 1 时解会指数放大。
    """
    u = u0.astype(float).copy()
    for _ in range(n_steps):
        u = u - c * (u - np.roll(u, 1))
    return u


def advect_semilagrangian(u0: np.ndarray, c: float, n_steps: int) -> np.ndarray:
    """半拉格朗日格式：沿轨迹回溯到上游点，再从邻格插值。

    它**不受 CFL 约束**——回溯多远都行，插值总能给出一个值。这正是 ECMWF 官方技术文档
    说它"unconditional stability allows long timesteps"、并且业务运行中库朗数大于 1 的来由。
    代价是插值本身会抹平场（下面的算例会把这件事量出来）。
    """
    n = len(u0)
    u = u0.astype(float).copy()
    idx = np.arange(n)
    for _ in range(n_steps):
        src = idx - c                      # 回溯到的上游位置（可以跨过好几个格距）
        lo = np.floor(src).astype(int)
        w = src - lo
        u = (1 - w) * u[lo % n] + w * u[(lo + 1) % n]
    return u


def cost_factor(levels_scale: bool = True, cfl_bound: bool = True) -> int:
    """水平格距减半时算力涨几倍——**这是量纲分析，不是任何业务中心的成本标度律**。

    水平两个方向各增 2 倍；垂直若按同一比例加密再增 2 倍；时间步若受 CFL 约束再增 2 倍。
    两个前提在真实业务模式上都可能不成立（见 19.1 节），所以这个函数把它们做成开关。
    """
    f = 4                                  # 水平两个方向
    if levels_scale:
        f *= 2
    if cfl_bound:
        f *= 2
    return f


# ================================================================ 二、混沌与可预报性（19.1 节）

LORENZ = dict(sigma=10.0, rho=28.0, beta=8.0 / 3.0)


def lorenz_step(s: np.ndarray, dt: float) -> np.ndarray:
    """洛伦兹系统的一步（四阶龙格库塔）。s 的形状是 (..., 3)。"""
    def f(v):
        x, y, z = v[..., 0], v[..., 1], v[..., 2]
        return np.stack([LORENZ["sigma"] * (y - x),
                         x * (LORENZ["rho"] - z) - y,
                         x * y - LORENZ["beta"] * z], -1)
    k1 = f(s); k2 = f(s + dt / 2 * k1); k3 = f(s + dt / 2 * k2); k4 = f(s + dt * k3)
    return s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + 2 * k4)


def lorenz_run(s0: np.ndarray, dt: float, n: int) -> np.ndarray:
    """跑 n 步，返回整条轨迹（含起点），形状 (n+1, ..., 3)。"""
    out = [s0]
    s = s0
    for _ in range(n):
        s = lorenz_step(s, dt)
        out.append(s)
    return np.stack(out, 0)


def doubling_time(dt: float, n: int, eps: float, seed: int, trials: int = 40) -> float:
    """误差翻倍时间：两条只差 eps 的轨迹，误差涨到 2 倍要多久（对数斜率算）。

    这就是"提前多久还能信"的来由：误差**指数**增长，所以把初始误差减小一半，只多买回
    一个翻倍时间——**提高初值精度的回报是对数的，不是线性的**。
    """
    g = np.random.default_rng(seed)
    rates = []
    for _ in range(trials):
        s0 = g.normal(0, 5, 3) + np.array([0.0, 0.0, 25.0])
        s0 = lorenz_run(s0, dt, 2000)[-1]                   # 先甩到吸引子上
        d0 = g.normal(size=3); d0 = d0 / np.linalg.norm(d0) * eps
        a = lorenz_run(s0, dt, n)
        b = lorenz_run(s0 + d0, dt, n)
        err = np.linalg.norm(a - b, axis=-1)
        sel = (err > eps) & (err < 5.0)                     # 只用还在线性增长的那一段
        if sel.sum() < 10:
            continue
        t = np.arange(len(err))[sel] * dt
        slope = np.polyfit(t, np.log(err[sel]), 1)[0]
        if slope > 0:
            rates.append(slope)
    return float(np.log(2) / np.mean(rates))


def useful_lead(dt: float, n: int, eps: float, tol: float, seed: int,
                trials: int = 60) -> float:
    """误差涨到 tol 之前，平均还能走多久（"提前多久还能信"）。"""
    g = np.random.default_rng(seed)
    times = []
    for _ in range(trials):
        s0 = lorenz_run(g.normal(0, 5, 3) + np.array([0.0, 0.0, 25.0]), dt, 2000)[-1]
        d0 = g.normal(size=3); d0 = d0 / np.linalg.norm(d0) * eps
        err = np.linalg.norm(lorenz_run(s0, dt, n) - lorenz_run(s0 + d0, dt, n), axis=-1)
        hit = np.where(err > tol)[0]
        times.append((hit[0] if len(hit) else n) * dt)
    return float(np.mean(times))


# ================================================================ 三、"越推越平"（19.2 节）
#
# 这一节的模型是一个谱玩具：场写成傅里叶分量，真实演化把每个分量乘一个相位加一点噪声。
# 要点是：**一步的均方误差最优预测，就是把每个分量乘上它自己的相关系数 ρ_k < 1。**
# 于是自回归推 n 步之后，第 k 个分量的振幅是 ρ_k^n ——高频衰减得最快，场一步步变平。
# 这不是实现上的毛病，**这就是均方误差的最优解本身**。


def spectrum(n_modes: int, slope: float = 1.6) -> np.ndarray:
    """给一个红噪声谱：低波数能量大、高波数能量小（真实大气场大致如此）。"""
    k = np.arange(1, n_modes + 1)
    return k.astype(float) ** (-slope)


def mode_correlation(n_modes: int, tau0: float = 6.0, power: float = 1.5) -> np.ndarray:
    r"""每个波数一步之后还剩多少相关：高波数的记忆短得多。

    $\\rho_k = \\exp(-1/\\tau_k)$，$\\tau_k = \\tau_0 k^{-power}$ ——这是"小尺度先失忆"的
    最简写法，与真实大气里"小尺度可预报期短"的性质一致。
    """
    k = np.arange(1, n_modes + 1)
    tau = tau0 * k.astype(float) ** (-power)
    return np.exp(-1.0 / np.maximum(tau, 1e-6))


def mse_optimal_amplitude(rho: np.ndarray, n_steps: int) -> np.ndarray:
    """自回归推 n 步之后，均方误差最优预测保留的振幅比例 ρ_k^n。"""
    return rho ** n_steps


def field_from_modes(amp: np.ndarray, phase: np.ndarray, n_x: int) -> np.ndarray:
    """把各波数的振幅与相位合成一个一维场。"""
    x = np.arange(n_x) / n_x * 2 * np.pi
    k = np.arange(1, len(amp) + 1)[:, None]
    return (amp[:, None] * np.cos(k * x[None, :] + phase[:, None])).sum(0)


def modes_truth(amp: np.ndarray, g: np.random.Generator) -> np.ndarray:
    """真值的复系数：每个波数一个复高斯，方差由谱给定。"""
    m = len(amp)
    return amp * (g.normal(size=m) + 1j * g.normal(size=m)) / np.sqrt(2)


def modes_forecast(z: np.ndarray, amp: np.ndarray, rho: np.ndarray,
                   g: np.random.Generator):
    r"""预报员掌握的信息 s，以及两种做法的预报系数。

    设预报员拿到的是 $s = \rho z + \sqrt{1-\rho^2}\,\xi$（$\xi$ 与 $z$ 独立同方差），
    则**均方误差最优的估计是 $\hat z = \rho s$**——它把振幅又压了一道。另一种做法是
    $\hat z = s$：振幅对了（场看起来像真的），但均方误差一定更大。
    返回 (最优的抹平预报, 保锐的预报)。
    """
    xi = amp * (g.normal(size=len(amp)) + 1j * g.normal(size=len(amp))) / np.sqrt(2)
    s = rho * z + np.sqrt(np.maximum(0.0, 1 - rho ** 2)) * xi
    return rho * s, s


def field_from_complex(z: np.ndarray, n_x: int) -> np.ndarray:
    """把复系数合成一个一维场。"""
    k = np.arange(1, len(z) + 1)[:, None]
    x = np.arange(n_x) / n_x * 2 * np.pi
    return (np.abs(z)[:, None] * np.cos(k * x[None, :] + np.angle(z)[:, None])).sum(0)


def sharpness(field: np.ndarray) -> float:
    """锐度：相邻格点差的均方根。场越平，这个数越小。"""
    return float(np.sqrt(np.mean(np.diff(field) ** 2)))


def smooth_field(field: np.ndarray, width: int) -> np.ndarray:
    """把一个场抹平（滑动平均，周期边界）。width = 1 时原样返回。"""
    if width <= 1:
        return field.astype(float).copy()
    ker = np.ones(width) / width
    pad = np.concatenate([field[-width:], field, field[:width]])
    return np.convolve(pad, ker, mode="same")[width:width + len(field)]


def extreme_hits(forecast: np.ndarray, truth: np.ndarray, q: float = 0.95):
    """极端事件抓住没有：真值超过 q 分位的那些点，预报也判为超过的比例（命中率），
    以及预报判超过而真值没超的比例（空报率）。"""
    th_t = np.quantile(truth, q)
    th_f = np.quantile(truth, q)            # 用同一个门限，免得被预报自己的分布糊弄过去
    hit = (forecast > th_f) & (truth > th_t)
    miss = (forecast <= th_f) & (truth > th_t)
    false = (forecast > th_f) & (truth <= th_t)
    n_event = hit.sum() + miss.sum()
    return (float(hit.sum() / n_event) if n_event else float("nan"),
            float(false.sum() / max(1, (truth <= th_t).sum())))


# ================================================================ 四、集合与概率评分（19.3 节）


def crps_ensemble(members: np.ndarray, obs: np.ndarray, unbiased: bool = True) -> float:
    """集合 CRPS。`members` 形状 (M, N)，`obs` 形状 (N,)。

    两种标准估计量只差第二项的分母：**无偏用 2M(M−1)，有偏用 2M²**。这不是笔误——
    公开文献里两种都在用（资料卡第 8.2 节），**印公式必须说明用的是哪一个**。
    M = 1 时 CRPS 退化成平均绝对误差。
    """
    m = members.shape[0]
    term1 = np.abs(members - obs[None, :]).mean(0)
    if m == 1:
        return float(term1.mean())
    diff = np.abs(members[:, None, :] - members[None, :, :]).sum((0, 1))
    denom = 2 * m * (m - 1) if unbiased else 2 * m * m
    return float((term1 - diff / denom).mean())


def spread_skill(members: np.ndarray, obs: np.ndarray) -> tuple[float, float, float]:
    """(离散度, 集合均值的 RMSE, 两者之比)。校准良好的集合，这个比值应当接近 1。"""
    spread = float(np.sqrt(members.var(0, ddof=1).mean()))
    rmse = float(np.sqrt(((members.mean(0) - obs) ** 2).mean()))
    return spread, rmse, spread / rmse if rmse > 0 else float("nan")


def reliability(prob: np.ndarray, occurred: np.ndarray, n_bins: int = 10):
    """可靠性图的数据：横轴预报概率，纵轴该档里事件实际发生的频率。

    返回 [(档中心, 实际频率, 这一档有多少个样本)]。完美可靠的点落在 45° 对角线上。
    """
    edges = np.linspace(0, 1, n_bins + 1)
    rows = []
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (prob >= a) & (prob < b if b < 1 else prob <= b)
        if sel.sum() == 0:
            rows.append(((a + b) / 2, float("nan"), 0)); continue
        rows.append(((a + b) / 2, float(occurred[sel].mean()), int(sel.sum())))
    return rows


def brier(prob: np.ndarray, occurred: np.ndarray) -> float:
    """Brier 分数：预报概率与"发生/没发生"之间的均方误差。0 完全准确，1 完全不准。"""
    return float(np.mean((prob - occurred.astype(float)) ** 2))


def make_ensemble(n_members: int, n_cases: int, seed: int,
                  spread_factor: float = 1.0, bias: float = 0.0):
    """造一批集合预报与对应的实况。

    真值 = 气候态 + 一个"这一次的信号"；集合成员 = 信号 + 各自的扰动。
    `spread_factor` < 1 是**离散度不足**（集合太自信），> 1 是离散度过大。
    """
    g = np.random.default_rng(seed)
    signal = g.normal(0, 1.0, n_cases)                 # 这一次真正可预报的那部分
    noise_true = g.normal(0, 1.0, n_cases)             # 不可预报的那部分
    obs = signal + noise_true
    members = signal[None, :] + bias + spread_factor * g.normal(0, 1.0, (n_members, n_cases))
    return members, obs


# ================================================================ 五、降尺度（19.4 节）


def coarse_grain(fine: np.ndarray, factor: int) -> np.ndarray:
    """把细网格的场平均成粗网格（这就是"全球模式看到的"那一份）。"""
    n = len(fine) // factor * factor
    return fine[:n].reshape(-1, factor).mean(1)


def downscale_naive(coarse: np.ndarray, factor: int) -> np.ndarray:
    """最朴素的降尺度：把粗格的值复制到细格上。它什么细节都没加。"""
    return np.repeat(coarse, factor)


def downscale_learned(coarse: np.ndarray, factor: int, amp: float, seed: int,
                      slope: float = 1.6) -> np.ndarray:
    r""""学出来的"降尺度：在插值的基础上**补上一份统计上像样的小尺度细节**。

    关键在于：这份细节是**凭统计生成的**，不是从粗场里推出来的——同一个粗场配不同的细场，
    它给出的细节是一样的。所以它能把**统计**做对，**不能**保证某一个点上的值是对的。
    19.4 节会把这件事量出来。
    """
    g = np.random.default_rng(seed)
    n = len(coarse) * factor
    base = np.interp(np.arange(n), np.arange(len(coarse)) * factor + factor / 2, coarse,
                     period=n)
    k = np.arange(1, n // 2)
    a = amp * k.astype(float) ** (-slope / 2)
    ph = g.uniform(0, 2 * np.pi, len(k))
    x = np.arange(n) / n * 2 * np.pi
    detail = (a[:, None] * np.cos(k[:, None] * x[None, :] + ph[:, None])).sum(0)
    return base + detail


def same_coarse_variant(fine: np.ndarray, factor: int, seed: int,
                        slope: float = 1.0) -> np.ndarray:
    """造一个**粗场完全相同、细节不同**的另一个细场。

    做法：保留原场的块平均，把块内的起伏换成另一份随机细节（先减掉它自己的块平均，
    保证块平均一点不变）。于是两个细场在粗网格上**一模一样**，在细网格上却不一样——
    这正是"粗场定不住细节"的构造性证明。
    """
    n = len(fine)
    base = np.repeat(coarse_grain(fine, factor), factor)
    other = fine_field(n, seed, slope=slope)
    detail = other - np.repeat(coarse_grain(other, factor), factor)   # 块平均为 0
    return base + detail


def fine_field(n: int, seed: int, slope: float = 1.6) -> np.ndarray:
    """一个有小尺度细节的"真实"细网格场。"""
    g = np.random.default_rng(seed)
    k = np.arange(1, n // 2)
    a = k.astype(float) ** (-slope / 2)
    ph = g.uniform(0, 2 * np.pi, len(k))
    x = np.arange(n) / n * 2 * np.pi
    return (a[:, None] * np.cos(k[:, None] * x[None, :] + ph[:, None])).sum(0)


# ================================================================ 六、遥感的划分口径（19.5 节）


def satellite_tile(n: int, seed: int, patch: int = 8, noise: float = 0.5,
                   block_effect: float = 1.6, class_sep: float = 0.45):
    """造一张"卫星图"：地物是成片的（空间自相关），每个像素有几维特征与一个类别。

    两件事是照真实影像取的：
    - **类别成片**：相邻像素几乎总是同一类；
    - **每一片还有自己的"局地条件"**（光照、土壤、传感器状态……），所以同一片里的像素
      彼此**比同类的远处像素更像**。

    第二条才是随机像素划分会高估的真正来由：测试像素在训练集里有一个紧挨着的、连局地
    条件都一样的孪生兄弟。把整片扣出来，这条路就断了。
    返回 (特征, 类别, 每个像素属于哪个区块)。
    """
    g = np.random.default_rng(seed)
    n_block = n // patch
    block_class = g.integers(0, 3, (n_block, n_block))
    cls = np.repeat(np.repeat(block_class, patch, 0), patch, 1)
    centers = g.normal(0, class_sep, (3, 4))
    local = g.normal(0, block_effect, (n_block, n_block, 4))          # 每一片的局地条件
    local = np.repeat(np.repeat(local, patch, 0), patch, 1)
    feat = centers[cls] + local + g.normal(0, noise, (n, n, 4))
    bid = np.repeat(np.repeat(np.arange(n_block * n_block).reshape(n_block, n_block),
                              patch, 0), patch, 1)
    return feat.reshape(-1, 4), cls.reshape(-1), bid.reshape(-1)


def split_pixels(n: int, seed: int, test_frac: float = 0.3):
    """按像素随机划分——相邻像素会被分到两边，于是测试集里的像素在训练集里有近邻。"""
    g = np.random.default_rng(seed)
    idx = g.permutation(n); cut = int(n * test_frac)
    return idx[cut:], idx[:cut]


def split_blocks(bid: np.ndarray, seed: int, test_frac: float = 0.3):
    """按区块划分——整块要么全在训练集、要么全在测试集。"""
    g = np.random.default_rng(seed)
    blocks = g.permutation(np.unique(bid))
    need = int(len(bid) * test_frac)
    test: list[int] = []
    for b in blocks:
        if len(test) >= need:
            break
        test.extend(np.where(bid == b)[0].tolist())
    ts = set(test)
    return np.array([i for i in range(len(bid)) if i not in ts]), np.array(sorted(ts))


def knn_classify(x_tr: np.ndarray, y_tr: np.ndarray, x_te: np.ndarray, k: int = 5,
                 chunk: int = 2000) -> np.ndarray:
    """最近邻分类（分块算，省内存）。它正是"按类似物记忆"的那一类模型。"""
    out = []
    for s in range(0, len(x_te), chunk):
        d = np.linalg.norm(x_te[s:s + chunk, None] - x_tr[None, :], axis=-1)
        nn = np.argsort(d, axis=1)[:, :k]
        lab = y_tr[nn]
        out.append(np.array([np.bincount(r, minlength=3).argmax() for r in lab]))
    return np.concatenate(out)


# ================================================================ 七、案例：风功率（19.6 节）

WIND = dict(cut_in=3.0, rated=11.0, cut_out=25.0, rated_power=1.0)


def power_curve(v: np.ndarray) -> np.ndarray:
    r"""风功率曲线：切入风速以下不发电，额定以上恒定，切出以上停机。

    额定以下按 $P \\propto v^3$ ——这是风功率与风速的三次方关系（$P = \\frac12\\rho A v^3 C_p$）。
    **本书的切入/额定/切出取的是常见量级，不代表任何一台具体机组。**
    """
    v = np.asarray(v, dtype=float)
    p = np.zeros_like(v)
    mid = (v >= WIND["cut_in"]) & (v < WIND["rated"])
    p[mid] = WIND["rated_power"] * ((v[mid] ** 3 - WIND["cut_in"] ** 3) /
                                    (WIND["rated"] ** 3 - WIND["cut_in"] ** 3))
    p[(v >= WIND["rated"]) & (v < WIND["cut_out"])] = WIND["rated_power"]
    return p


def power_error(v_true: np.ndarray, v_err: float) -> np.ndarray:
    """风速差 v_err 时，发电量差多少（占额定功率的比例）。"""
    return power_curve(v_true + v_err) - power_curve(v_true)


def wind_cases(n: int, seed: int, mean: float = 8.0, k: float = 2.0) -> np.ndarray:
    """一批风速（威布尔分布，风资源评估的常用假设；形状参数 k=2 即瑞利分布）。"""
    g = np.random.default_rng(seed)
    lam = mean / 0.8862                     # k=2 时 E[v] = λ·Γ(1.5) ≈ 0.8862 λ
    return lam * (-np.log(1 - g.random(n))) ** (1 / k)
