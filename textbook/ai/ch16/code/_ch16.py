"""第 16 章共用的玩具分布、五类生成模型的最小实现，以及合成缺陷图的案例数据。

**为什么是玩具分布**：生成模型的好坏要在**分布**层面看，而真实图像的分布谁也写不出来，
只能靠 FID 这类间接指标——那正是本章要讲清楚的坑。所以本章先退到一维与二维：真分布是
已知的，于是"生成得像不像"可以用柯尔莫哥洛夫—斯米尔诺夫距离精确地量，"漏掉了哪个峰"
可以数出来，"引导强度把分布推偏了多少"可以画出来。

仓库里不放任何真实缺陷照片与模型权重；案例用的缺陷图由程序按第 11 章的办法现画。
真模型上的数字见资料卡与 16.4、16.8 节的云端实验。
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- 一、玩具分布（16.1 节）
# 三个峰，高低不同、宽窄不同：故意让其中一个峰又矮又窄，好让"模式坍塌"有东西可漏。
MIX_W = np.array([0.5, 0.35, 0.15])
MIX_MU = np.array([-2.0, 0.6, 3.2])
MIX_SD = np.array([0.45, 0.6, 0.25])


def mix_sample(n: int, seed: int = 0) -> np.ndarray:
    g = np.random.default_rng(1600 + seed)
    k = g.choice(len(MIX_W), size=n, p=MIX_W)
    return g.normal(MIX_MU[k], MIX_SD[k])


def mix_pdf(x: np.ndarray) -> np.ndarray:
    x = np.atleast_1d(x)[:, None]
    z = (x - MIX_MU) / MIX_SD
    return (MIX_W / (MIX_SD * np.sqrt(2 * np.pi)) * np.exp(-0.5 * z ** 2)).sum(1)


def mix_cdf(x: np.ndarray) -> np.ndarray:
    from math import erf
    x = np.atleast_1d(x)
    out = np.zeros_like(x, dtype=float)
    for w, mu, sd in zip(MIX_W, MIX_MU, MIX_SD):
        out += w * np.array([0.5 * (1 + erf((xi - mu) / (sd * np.sqrt(2)))) for xi in x])
    return out


def ks(samples: np.ndarray, cdf=None) -> float:
    """柯尔莫哥洛夫—斯米尔诺夫距离：经验分布与给定分布的最大差。0 是完全一致。
    cdf 不给时就比对本节那个三峰真分布。"""
    s = np.sort(samples)
    emp = np.arange(1, len(s) + 1) / len(s)
    return float(np.max(np.abs(emp - (mix_cdf if cdf is None else cdf)(s))))


def coverage(samples: np.ndarray, tol: float = 2.0) -> int:
    """生成的样本覆盖了几个峰：某个峰附近（tol 个标准差内）至少有 1% 的样本才算覆盖到。"""
    hit = 0
    for mu, sd in zip(MIX_MU, MIX_SD):
        if np.mean(np.abs(samples - mu) < tol * sd) > 0.01:
            hit += 1
    return hit


# ---------------------------------------------------------------- 二、五类模型的最小实现

def autoregressive(train: np.ndarray, bins: int = 60, n: int = 4000, seed: int = 0):
    """自回归（这里一维，就退化成"把轴切成格子、数频率"）：能精确算似然，一次采样一次前向。"""
    lo, hi = MIX_MU.min() - 4, MIX_MU.max() + 4
    edges = np.linspace(lo, hi, bins + 1)
    cnt, _ = np.histogram(train, edges)
    p = (cnt + 1) / (cnt.sum() + bins)                     # 加一平滑（M3.3 节）
    g = np.random.default_rng(seed)
    k = g.choice(bins, size=n, p=p)
    x = edges[k] + g.random(n) * (edges[1] - edges[0])
    width = edges[1] - edges[0]
    ll = float(np.mean(np.log(p[np.clip(np.digitize(train, edges) - 1, 0, bins - 1)] / width)))
    return x, ll


def flow(train: np.ndarray, knots: int = 40, n: int = 4000, seed: int = 0):
    """流模型（一维就是一个单调映射）：把均匀分布映成数据分布，映射由经验分位数给出。
    它能精确算似然（变量替换公式），采样也只要一次前向。"""
    q = np.linspace(0, 1, knots + 1)
    xs = np.quantile(train, q)
    g = np.random.default_rng(seed + 1)
    u = g.random(n)
    x = np.interp(u, q, xs)
    dens = np.gradient(q, xs)                              # dF/dx，即密度
    ll = float(np.mean(np.log(np.maximum(np.interp(train, xs, dens), 1e-12))))
    return x, ll


def vae_em(train: np.ndarray, k: int = 3, iters: int = 200, n: int = 4000, seed: int = 0,
           restarts: int = 5):
    """隐变量模型（一维高斯混合，用期望最大化拟合）：它与变分自编码器是同一个思路——
    先抽一个隐变量（哪个峰），再按条件分布生成。这里隐变量是离散的，所以后验能精确算。

    期望最大化会卡在局部最优（M3 节），所以按惯例多随机起几次、留似然最高的那一次。
    """
    g = np.random.default_rng(seed + 2)

    def _ll(w, mu, sd):
        return float(np.mean(np.log(np.maximum(
            (w / (sd * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((train[:, None] - mu) / sd) ** 2)).sum(1),
            1e-300))))

    best = None
    for _ in range(restarts):
        mu = g.choice(train, k)
        sd = np.full(k, float(train.std()))
        w = np.ones(k) / k
        for _ in range(iters):
            r = w / (sd * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ((train[:, None] - mu) / sd) ** 2)
            r /= np.maximum(r.sum(1, keepdims=True), 1e-300)
            nk = r.sum(0)
            w = nk / len(train)
            mu = (r * train[:, None]).sum(0) / nk
            sd = np.sqrt(np.maximum((r * (train[:, None] - mu) ** 2).sum(0) / nk, 1e-6))
        cur = _ll(w, mu, sd)
        if best is None or cur > best[0]:
            best = (cur, w, mu, sd)
    ll, w, mu, sd = best
    kk = g.choice(k, size=n, p=w)
    x = g.normal(mu[kk], sd[kk])
    return x, ll, (w, mu, sd)


def dirac_gan(theta0: float = 1.0, psi0: float = 1.0, lr: float = 0.1, steps: int = 400,
              reg: float = 0.0, alt: bool = False):
    """狄拉克生成对抗网络（Mescheder 等 2018 的例子）：真分布就是 0 这一个点，生成器只有一个
    参数 θ（它生成的那个点），判别器只有一个参数 ψ（线性判别 D(x) = ψx）。

    这是整个对抗训练里唯一能手算的例子，而它的结论是**不收敛**：同时走梯度时
    (θ, ψ) 绕着原点转圈，θ² + ψ² 一步也不减。给判别器加一点正则（reg > 0）才会往里收。
    返回每一步的 (θ, ψ)。
    """
    th, ps = theta0, psi0
    out_ = [(th, ps)]
    for _ in range(steps):
        # f(t) = -log(1+e^{-t}) 取非饱和目标时，梯度方向与下式同号；这里用 f(t) = t（最朴素的一版），
        # 结论一样：D 的梯度是 +θ，G 的梯度是 +ψ。
        d_ps, d_th = th, ps
        if alt:                                             # 交替更新：先动判别器，再用新的 ψ 动生成器
            ps = ps + lr * (d_ps - reg * ps)
            th = th - lr * ps
        else:                                               # 同时更新
            ps_new = ps + lr * (d_ps - reg * ps)
            th = th - lr * d_th
            ps = ps_new
        out_.append((th, ps))
    return np.array(out_)


# 环上八个峰：这是模式坍塌的标准演示。一维的单调映射没法把中间的峰整个丢掉（最多把它饿瘦），
# 二维就可以——生成器完全可以只往其中两三个峰上送点。
RING_K = 8
RING_R = 2.0
RING_SD = 0.1


def ring_sample(n: int, seed: int = 0) -> np.ndarray:
    g = np.random.default_rng(4000 + seed)
    a = 2 * np.pi * g.integers(RING_K, size=n) / RING_K
    return np.c_[RING_R * np.cos(a), RING_R * np.sin(a)] + g.normal(0, RING_SD, (n, 2))


def ring_centers() -> np.ndarray:
    a = 2 * np.pi * np.arange(RING_K) / RING_K
    return np.c_[RING_R * np.cos(a), RING_R * np.sin(a)]


def ring_coverage(x: np.ndarray, tol: float = 3.0):
    """覆盖了几个峰，以及各峰的占比。某个峰附近（tol 个标准差内）样本占比过 1/(4K) 才算覆盖。"""
    cen = ring_centers()
    d = np.linalg.norm(x[:, None, :] - cen[None, :, :], axis=2)
    near = d.min(1) < tol * RING_SD
    who = np.argmin(d, 1)
    share = np.array([float(np.mean(near & (who == k))) for k in range(RING_K)])
    return int((share > 1 / (4 * RING_K)).sum()), share


def gan_2d(train: np.ndarray, steps: int = 20_000, hid: int = 32, lr: float = 0.02, seed: int = 0,
           k_disc: int = 1, n: int = 4000, batch: int = 256, track: int = 0,
           saturating: bool = False):
    """二维生成对抗网络：生成器与判别器各是一个两层的 tanh 网络，梯度手写（第 3 章的反向传播）。
    用它演示模式坍塌——`k_disc` 调大（判别器走得多）时，生成器更容易只守住几个峰。"""
    g = np.random.default_rng(5000 + seed)

    def init(shapes):
        return [[g.normal(0, np.sqrt(2.0 / a), (a, b)), np.zeros(b)] for a, b in shapes]

    G = init([(2, hid), (hid, hid), (hid, 2)])
    D = init([(2, hid), (hid, hid), (hid, 1)])

    def fwd(net, x, last_tanh=True):
        acts = [x]
        for i, (Wm, b) in enumerate(net):
            z = acts[-1] @ Wm + b
            acts.append(np.tanh(z) if (i < len(net) - 1 or last_tanh) else z)
        return acts

    def back(net, acts, dout, last_tanh=True):
        grads = [None] * len(net)
        d = dout
        for i in range(len(net) - 1, -1, -1):
            if i < len(net) - 1 or last_tanh:
                d = d * (1 - acts[i + 1] ** 2)
            grads[i] = [acts[i].T @ d / len(d), d.mean(0)]
            d = d @ net[i][0].T
        return grads, d

    def step(net, grads, s):
        for (Wm, b), (gW, gb) in zip(net, grads):
            Wm += s * gW
            b += s * gb

    hist = []
    for t in range(steps):
        if track and t % track == 0:
            za = g.normal(size=(2000, 2))
            hist.append((t,) + (lambda c: (c[0], c[1].min()))(
                ring_coverage(fwd(G, za, last_tanh=False)[-1])))
        for _ in range(k_disc):
            real = train[g.integers(len(train), size=batch)]
            fake = fwd(G, g.normal(size=(batch, 2)), last_tanh=False)[-1]
            ar = fwd(D, real, last_tanh=False)
            af = fwd(D, fake, last_tanh=False)
            pr = 1 / (1 + np.exp(-ar[-1]))
            pf = 1 / (1 + np.exp(-af[-1]))
            gr, _ = back(D, ar, (1 - pr), last_tanh=False)      # 上升 log D(real)
            gf, _ = back(D, af, -pf, last_tanh=False)           # 上升 log(1−D(fake))
            step(D, [[a[0] + b[0], a[1] + b[1]] for a, b in zip(gr, gf)], lr)
        z = g.normal(size=(batch, 2))
        ag = fwd(G, z, last_tanh=False)
        ad = fwd(D, ag[-1], last_tanh=False)
        pf = 1 / (1 + np.exp(-ad[-1]))
        # 非饱和目标（惯例）：上升 log D(fake)；saturating 时用最早那篇论文的原始目标
        # ——下降 log(1−D(fake))，判别器一强，梯度就几乎没有了。
        _, dx = back(D, ad, (-pf if saturating else (1 - pf)), last_tanh=False)
        gg, _ = back(G, ag, dx, last_tanh=False)
        step(G, gg, lr)
    x = fwd(G, g.normal(size=(n, 2)), last_tanh=False)[-1]
    return (x, hist) if track else x


def gan_1d(train: np.ndarray, n: int = 4000, steps: int = 12_000, lr: float = 0.02, seed: int = 0,
           k_disc: int = 1, decay: float | None = 4000.0, track: int = 0):
    """一维生成对抗网络的最小实现：生成器是一个分段线性映射（把均匀噪声映到数据轴上），
    判别器是一个在若干个高斯基上的逻辑回归。两边轮流走梯度。

    它学得出大致形状，但**不保证**收敛：学习率不衰减时，KS 距离会先降后升（16.2 节的图）。
    `decay` 给定时学习率按 lr/(1+t/decay) 衰减；`track` 给定时每这么多步记一次 KS 距离。
    """
    g = np.random.default_rng(seed + 3)
    K = 12                                                  # 生成器的分段数
    knots = np.linspace(0, 1, K + 1)
    gen = np.linspace(train.min(), train.max(), K + 1)       # 生成器参数：各分段端点的值
    centers = np.linspace(MIX_MU.min() - 4, MIX_MU.max() + 4, 24)
    width = centers[1] - centers[0]

    def feat(x):
        return np.exp(-0.5 * ((x[:, None] - centers) / width) ** 2)

    w = np.zeros(len(centers))
    B = 256
    hist = []
    for t in range(steps):
        lr_t = lr if decay is None else lr / (1 + t / decay)
        if track and t % track == 0:
            u = g.random(2000)
            hist.append((t, ks(np.interp(u, knots, np.sort(gen)))))
        for _ in range(k_disc):                             # 判别器：一步梯度上升
            real = g.choice(train, B)
            u = g.random(B)
            fake = np.interp(u, knots, np.sort(gen))
            pr = 1 / (1 + np.exp(-feat(real) @ w))
            pf = 1 / (1 + np.exp(-feat(fake) @ w))
            w += lr_t * (feat(real).T @ (1 - pr) - feat(fake).T @ pf) / B
        u = g.random(B)                                     # 生成器：一步梯度下降
        idx = np.clip(np.searchsorted(knots, u) - 1, 0, K - 1)
        frac = (u - knots[idx]) / (knots[1] - knots[0])
        gs = np.sort(gen)
        fake = gs[idx] * (1 - frac) + gs[idx + 1] * frac
        pf = 1 / (1 + np.exp(-feat(fake) @ w))
        # 用"非饱和"的生成器目标（DCGAN 以来的惯例）：最大化 log D(G(z))，梯度不会在判别器
        # 很强时消失。d log D/dx = (1 − D)·d(logit)/dx。
        dlogit = -(feat(fake) * ((fake[:, None] - centers) / width ** 2)) @ w
        dfake = (1 - pf) * dlogit
        grad = np.zeros_like(gen)
        np.add.at(grad, idx, dfake * (1 - frac))
        np.add.at(grad, idx + 1, dfake * frac)
        gen += lr_t * grad / B
    u = g.random(n)
    x = np.interp(u, knots, np.sort(gen))
    return (x, w, hist) if track else (x, w)


# ---------------------------------------------------------------- 三、扩散（16.3 节）
# 前向有闭式解：x_t = sqrt(ᾱ_t)·x_0 + sqrt(1−ᾱ_t)·ε（DDPM 式 4）。
# 训练目标是从 x_t 估回那个 ε。这个玩具分布的好处是：最优的 ε 预测器**写得出来**，
#     ε*(x_t, t) = −sqrt(1−ᾱ_t) · ∇ log q_t(x_t)，
# 而 q_t 就是把每个峰的均值乘 sqrt(ᾱ_t)、方差加 1−ᾱ_t 之后的混合高斯。
# 于是"学出来的预测器离最优差多少"和"采样步数少了差多少"这两件事可以分开量。
#
# 内部统一在标准化坐标 z = (x − m)/s 上做（m、s 是真分布的均值与标准差），
# 因为 DDPM 的噪声调度是按"数据方差约为 1"设计的。

_M = float((MIX_W * MIX_MU).sum())
_S = float(np.sqrt((MIX_W * (MIX_SD ** 2 + MIX_MU ** 2)).sum() - _M ** 2))
_ZMU = (MIX_MU - _M) / _S
_ZSD = MIX_SD / _S


def schedule(T: int = 1000, beta0: float = 1e-4, beta1: float = 0.02, kind: str = "linear"):
    """噪声调度。线性调度就是 DDPM 原设定：T = 1000，β 从 1e-4 线性升到 0.02。
    余弦调度（Nichol & Dhariwal 2021）中间加噪慢、两头快；它的好处是在真实图像上测出来的，
    本章这个一维玩具上并不占优，所以正文不拿它下结论。"""
    if kind == "linear":
        beta = np.linspace(beta0, beta1, T)
        return beta, 1 - beta, np.cumprod(1 - beta)
    s = 0.008
    f = np.cos((np.arange(T + 1) / T + s) / (1 + s) * np.pi / 2) ** 2
    ab = f / f[0]
    beta = np.clip(1 - ab[1:] / ab[:-1], 1e-8, 0.999)
    return beta, 1 - beta, np.cumprod(1 - beta)


def forward(z0: np.ndarray, t: int, abar: np.ndarray, g: np.random.Generator):
    """一步跳到任意时刻 t。返回 (z_t, 用掉的那个 ε)。"""
    eps = g.normal(size=np.shape(z0))
    return np.sqrt(abar[t]) * z0 + np.sqrt(1 - abar[t]) * eps, eps


def eps_exact(z: np.ndarray, t: int, abar: np.ndarray) -> np.ndarray:
    """最优 ε 预测器（解析解）：q_t 是混合高斯，分数函数写得出来。"""
    ab = abar[t]
    mu = np.sqrt(ab) * _ZMU
    var = ab * _ZSD ** 2 + (1 - ab)
    d = z[:, None] - mu
    comp = MIX_W / np.sqrt(2 * np.pi * var) * np.exp(-0.5 * d ** 2 / var)
    tot = np.maximum(comp.sum(1), 1e-300)
    score = (comp * (-d / var)).sum(1) / tot                 # ∇ log q_t(z)
    return -np.sqrt(1 - ab) * score


def _basis(z: np.ndarray, t: int, centers, width, abar):
    """特征：一组高斯基乘上几个关于噪声水平的函数。真模型这里换成神经网络，道理一样。"""
    s = np.sqrt(1 - abar[t])
    f = np.exp(-0.5 * ((z[:, None] - centers) / width) ** 2)
    return np.c_[f, f * s, f * s ** 2, np.ones(len(z)), np.full(len(z), s)]


def diffusion_fit(train: np.ndarray, T: int = 1000, kind: str = "linear", n_feat: int = 28,
                  seed: int = 0, n_batch: int = 1200, batch: int = 512, ridge: float = 1e-4):
    """训噪声预测器：按 DDPM 的 L_simple，随机抽时刻 t、随机抽噪声，最小化 ‖ε − ε̂‖²。
    这里 ε̂ 对参数是线性的，所以这个最小二乘有闭式解，一次解完，不用迭代。"""
    g = np.random.default_rng(seed + 4)
    beta, alpha, abar = schedule(T, kind=kind)
    z = (train - _M) / _S
    centers = np.linspace(-4.5, 4.5, n_feat)
    width = centers[1] - centers[0]
    X, Y = [], []
    for _ in range(n_batch):
        t = int(g.integers(T))
        zt, eps = forward(g.choice(z, batch), t, abar, g)
        X.append(_basis(zt, t, centers, width, abar))
        Y.append(eps)
    X, Y = np.vstack(X), np.concatenate(Y)
    W = np.linalg.solve(X.T @ X + ridge * len(X) * np.eye(X.shape[1]), X.T @ Y)
    return {"W": W, "centers": centers, "width": width,
            "beta": beta, "alpha": alpha, "abar": abar, "T": T}


def eps_hat(model, z: np.ndarray, t: int) -> np.ndarray:
    return _basis(z, t, model["centers"], model["width"], model["abar"]) @ model["W"]


def diffusion_sample(model, n: int = 4000, steps: int | None = None, eta: float = 1.0,
                     seed: int = 0, exact: bool = False, guide=None):
    """反向采样。steps 为 None 时逐步走完（DDPM 算法 2）；给定 steps 时等间隔跳着走，
    η = 0 就是确定性的 DDIM。exact = True 时用解析的最优预测器，用来把"模型不够好"和
    "步数不够多"这两种误差分开。guide 给定时，用它替换 ε 的算法（无分类器引导，16.4 节）。"""
    g = np.random.default_rng(seed + 5)
    abar, beta = model["abar"], model["beta"]
    T = model["T"]
    ts = np.arange(T - 1, -1, -1) if steps is None else np.unique(
        np.linspace(T - 1, 0, steps).astype(int))[::-1]
    z = g.normal(size=n)
    for i, t in enumerate(ts):
        t = int(t)
        if guide is not None:
            e = guide(z, t)
        elif exact:
            e = eps_exact(z, t, abar)
        else:
            e = eps_hat(model, z, t)
        z0 = (z - np.sqrt(1 - abar[t]) * e) / np.sqrt(abar[t])
        z0 = np.clip(z0, -6, 6)                              # 与真实实现一样，把 x̂_0 夹住
        t_prev = int(ts[i + 1]) if i + 1 < len(ts) else -1
        ab_prev = abar[t_prev] if t_prev >= 0 else 1.0
        if t_prev < 0:
            z = z0
            break
        sig = eta * np.sqrt(max((1 - ab_prev) / (1 - abar[t]) * (1 - abar[t] / ab_prev), 0.0))
        z = np.sqrt(ab_prev) * z0 + np.sqrt(max(1 - ab_prev - sig ** 2, 0.0)) * e
        if sig > 0:
            z = z + sig * g.normal(size=n)
    return z * _S + _M


# ---------------------------------------------------------------- 四、条件与引导（16.4 节）
# 两类数据（"划痕"与"锈斑"）各有自己的分布，而且**共用一个峰**——这样"引导太强会丢掉
# 共用的那一片"才看得出来。条件模型学一个带类别的预测器，引导就是把有条件与无条件的
# 预测按 (1+w)·有条件 − w·无条件 混起来（Ho & Salimans 2022 式 6；这一版 w = 0 表示不引导）。

COND_MU = {0: np.array([-2.0, 0.6]), 1: np.array([0.6, 3.2])}
COND_W = {0: np.array([0.6, 0.4]), 1: np.array([0.35, 0.65])}
COND_SD = 0.45


def cond_sample(c: int, n: int, seed: int = 0) -> np.ndarray:
    g = np.random.default_rng(1700 + seed + 11 * c)
    k = g.choice(len(COND_MU[c]), size=n, p=COND_W[c])
    return g.normal(COND_MU[c][k], COND_SD)


def cond_pdf(c: int, x: np.ndarray) -> np.ndarray:
    x = np.atleast_1d(x)[:, None]
    z = (x - COND_MU[c]) / COND_SD
    return (COND_W[c] / (COND_SD * np.sqrt(2 * np.pi)) * np.exp(-0.5 * z ** 2)).sum(1)


def cond_cdf(c: int, x: np.ndarray) -> np.ndarray:
    from math import erf
    x = np.atleast_1d(x)
    out = np.zeros_like(x, dtype=float)
    for w, mu in zip(COND_W[c], COND_MU[c]):
        out += w * np.array([0.5 * (1 + erf((xi - mu) / (COND_SD * np.sqrt(2)))) for xi in x])
    return out


def cond_eps_exact(c: int | None, z: np.ndarray, t: int, abar: np.ndarray) -> np.ndarray:
    """条件（或无条件）的最优 ε 预测器。c = None 时是两类各占一半的无条件分布。"""
    ab = abar[t]
    if c is None:
        w = np.r_[0.5 * COND_W[0], 0.5 * COND_W[1]]
        m = np.r_[COND_MU[0], COND_MU[1]]
    else:
        w, m = COND_W[c], COND_MU[c]
    mu = np.sqrt(ab) * (m - _M) / _S
    var = ab * (COND_SD / _S) ** 2 + (1 - ab)
    d = z[:, None] - mu
    comp = w / np.sqrt(2 * np.pi * var) * np.exp(-0.5 * d ** 2 / var)
    score = (comp * (-d / var)).sum(1) / np.maximum(comp.sum(1), 1e-300)
    return -np.sqrt(1 - ab) * score


def guided(c: int, w_guide: float, abar: np.ndarray):
    """返回一个可以交给 diffusion_sample(guide=...) 的函数。"""
    def f(z, t):
        ec = cond_eps_exact(c, z, t, abar)
        eu = cond_eps_exact(None, z, t, abar)
        return (1 + w_guide) * ec - w_guide * eu
    return f


def sdedit(model, x0: np.ndarray, t0: int, steps: int = 60, seed: int = 0, guide=None):
    """按"编辑强度"改一张已有的样本（SDEdit 的做法，也就是各家界面上那个 strength 滑块）：
    先把它加噪到时刻 t0，再从那里反着去噪。t0 小 → 只微调；t0 大 → 和原来没关系了。"""
    g = np.random.default_rng(seed + 8)
    abar = model["abar"]
    z0 = (x0 - _M) / _S
    z = np.sqrt(abar[t0]) * z0 + np.sqrt(1 - abar[t0]) * g.normal(size=len(z0))
    ts = np.unique(np.linspace(t0, 0, steps).astype(int))[::-1]
    for i, t in enumerate(ts):
        t = int(t)
        e = guide(z, t) if guide is not None else eps_hat(model, z, t)
        zh = np.clip((z - np.sqrt(1 - abar[t]) * e) / np.sqrt(abar[t]), -6, 6)
        t_prev = int(ts[i + 1]) if i + 1 < len(ts) else -1
        if t_prev < 0:
            z = zh
            break
        ab_prev = abar[t_prev]
        sig = np.sqrt(max((1 - ab_prev) / (1 - abar[t]) * (1 - abar[t] / ab_prev), 0.0))
        z = np.sqrt(ab_prev) * zh + np.sqrt(max(1 - ab_prev - sig ** 2, 0.0)) * e
        z = z + sig * g.normal(size=len(z))
    return z * _S + _M


def latent_cost(res: int = 512, f: int = 8, c_lat: int = 4, patch: int = 2):
    """潜在扩散省在哪：把一张 res×res×3 的图压到 (res/f)²×c_lat 个数，再在上面做扩散。
    返回 (像素空间的数值个数, 潜空间的数值个数, 两者之比, 自注意力代价之比)。
    自注意力按词元数的平方算（第 13 章），词元是 patch×patch 的小块。"""
    px = res * res * 3
    lat = (res // f) ** 2 * c_lat
    tok_px = (res // patch) ** 2
    tok_lat = (res // f // patch) ** 2
    return px, lat, px / lat, (tok_px / tok_lat) ** 2


def video_tokens(seconds: float, fps: int = 24, res=(1920, 1080), f: int = 8,
                 patch: int = 2, t_patch: int = 2):
    """一段视频在潜空间里有多少词元：先按 f 压空间，再按 patch×patch×t_patch 切块。
    返回 (帧数, 每帧词元数, 总词元数)。自注意力的代价按总词元数的平方算。"""
    frames = int(round(seconds * fps))
    per = (res[0] // f // patch) * (res[1] // f // patch)
    return frames, per, per * frames // t_patch


def temporal_chain(model, n_frames: int, t0: int, seed: int = 0):
    """把"视频"做成一串：每一帧都从上一帧加噪再去噪（强度由 t0 定）。
    这样每帧都还落在真分布上，但相邻帧挨得近——这就是时间一致性最朴素的做法。"""
    g = np.random.default_rng(seed + 12)
    x = np.array([float(mix_sample(1, 61 + seed)[0])])
    frames = [x[0]]
    for i in range(n_frames - 1):
        x = sdedit(model, x, t0, steps=40, seed=int(g.integers(1 << 30)))
        frames.append(float(x[0]))
    return np.array(frames)


def sharpness(x: np.ndarray, c: int) -> float:
    """"像不像这一类"的一个代理：样本落在该类条件密度高处的平均对数密度。"""
    return float(np.mean(np.log(np.maximum(cond_pdf(c, x), 1e-12))))


def mode_share(x: np.ndarray, c: int, tol: float = 2.0) -> np.ndarray:
    """这一类的每个峰各占多少样本——引导调强之后，矮峰会被挤掉。"""
    return np.array([float(np.mean(np.abs(x - mu) < tol * COND_SD)) for mu in COND_MU[c]])


# ---------------------------------------------------------------- 五、分布层面的指标（16.2 节）

def frechet(a: np.ndarray, b: np.ndarray) -> float:
    """两组样本各拟合一个高斯，算它们之间的弗雷歇距离——这就是 FID 的算法，
    只是真 FID 先把图像过一遍 Inception 网络取特征，这里直接在数据上算。"""
    a, b = np.atleast_2d(a.T).T, np.atleast_2d(b.T).T
    if a.ndim == 1:
        a, b = a[:, None], b[:, None]
    m1, m2 = a.mean(0), b.mean(0)
    c1 = np.cov(a, rowvar=False).reshape(a.shape[1], a.shape[1])
    c2 = np.cov(b, rowvar=False).reshape(b.shape[1], b.shape[1])
    # 一维时 (C1 C2)^{1/2} 就是 sqrt(c1*c2)
    cov_sqrt = np.sqrt(np.maximum(c1 @ c2, 0)) if a.shape[1] == 1 else _sqrtm(c1 @ c2)
    return float(((m1 - m2) ** 2).sum() + np.trace(c1 + c2 - 2 * cov_sqrt))


def _sqrtm(m: np.ndarray) -> np.ndarray:
    vals, vecs = np.linalg.eig(m)
    return np.real(vecs @ np.diag(np.sqrt(np.maximum(np.real(vals), 0))) @ np.linalg.inv(vecs))


# ---------------------------------------------------------------- 六、水印（16.7 节）
# 一维的"内容"（几条低频正弦叠起来，像一行音频或一条扫描线）加上一串按密钥生成的 ±1。
# 检测时先做高通（相邻差分）把内容滤掉，再与密钥序列求相关——真实的图像与音频水印也是
# 这个路子：把标记放进内容本身没占满的那部分频带，这样人看不出、检测器算得出。

def content(n: int = 4096, seed: int = 0, k_max: int = 8) -> np.ndarray:
    """一段"原始内容"：k_max 条低频正弦随机叠加，再归一化到标准差 1。"""
    g = np.random.default_rng(3000 + seed)
    t = np.arange(n) / n
    x = sum(g.normal() * np.sin(2 * np.pi * k * t + g.uniform(0, 2 * np.pi))
            for k in range(1, k_max + 1))
    return x / x.std()


def _pattern(key: int, n: int) -> np.ndarray:
    return np.random.default_rng(key).choice([-1.0, 1.0], size=n)


def watermark(x: np.ndarray, key: int = 7, strength: float = 0.05) -> np.ndarray:
    """嵌水印：按密钥生成一串 ±1，按 strength（相对内容标准差）加上去。"""
    return x + strength * _pattern(key, len(x))


def detect(x: np.ndarray, key: int = 7) -> float:
    """检测：高通之后与密钥序列的相关系数。没嵌或密钥不对时在 0 附近，嵌对了接近 1。"""
    d = np.diff(x)
    p = np.diff(_pattern(key, len(x)))
    d, p = d - d.mean(), p - p.mean()
    return float(d @ p / (np.linalg.norm(d) * np.linalg.norm(p) + 1e-12))


def fp_threshold(x: np.ndarray, keys=range(1000, 1300), q: float = 95.0) -> float:
    """误报门限：拿一堆**错**密钥去测同一段信号，取相关系数绝对值的 q 分位。
    门限定在它之上，误报率就压到 (100−q)% 以下。"""
    return float(np.percentile([abs(detect(x, k)) for k in keys], q))


def attack(x: np.ndarray, kind: str, level: float, seed: int = 0) -> np.ndarray:
    """几种常见的"处理"：加噪、量化（相当于压缩）、裁剪一段、重采样。"""
    g = np.random.default_rng(seed + 9)
    if kind == "noise":
        return x + level * np.std(x) * g.normal(size=x.shape)
    if kind == "quantize":
        step = level * np.std(x)
        return np.round(x / step) * step
    if kind == "crop":
        keep = max(4, int(len(x) * (1 - level)))
        out = x.copy()
        out[keep:] = 0.0
        return out
    if kind == "resample":                                  # 下采样再插值回来
        m = max(4, int(len(x) * (1 - level)))
        idx = np.linspace(0, len(x) - 1, m)
        return np.interp(np.arange(len(x)), idx, np.interp(idx, np.arange(len(x)), x))
    raise ValueError(kind)


# ---------------------------------------------------------------- 七、案例：合成缺陷图（16.8 节）
# 缺陷图由程序按第 11 章的办法画：一块磨削表面，加上划痕/压痕/锈斑。这里只取几个统计量当特征，
# 好让"训一个检测器"这件事在几十行里跑完，同时把"合成数据有没有用"这件事量出来。

H = W = 48
KINDS = ("无缺陷", "划痕", "压痕", "锈斑")
# 车间口径：七成的件是合格的，缺陷大多很轻微（这才是难的地方——重缺陷谁都看得见）。
SEV = (0.08, 0.35)
PK = [0.7, 0.1, 0.1, 0.1]


def defect_image(kind: int, sev: float, g: np.random.Generator, plain_bg: bool = False) -> np.ndarray:
    """画一张 48×48 的表面图。plain_bg = True 时底纹的朝向与照明固定——这模拟"生成器没学会
    底纹的变化"，是合成数据最常见的一种偏差（与第 11 章的"捷径"是同一回事）。"""
    y, x = np.mgrid[0:H, 0:W].astype(float)
    # 底纹：磨削留下的平行刀纹（方向与疏密每件都不一样）+ 一点照明不匀 + 传感器噪声。
    # 刀纹的起伏比轻微缺陷还大，所以"看出缺陷"本来就不轻松——这正是案例要的难度。
    ang0 = 0.0 if plain_bg else g.uniform(0, np.pi)
    lam = 3.8 if plain_bg else g.uniform(2.6, 5.0)
    u = x * np.cos(ang0) + y * np.sin(ang0)
    img = (0.50
           + 0.050 * np.sin(2 * np.pi * u / lam + g.uniform(0, 2 * np.pi))
           + 0.018 * np.sin(2 * np.pi * u / (lam * 2.3) + g.uniform(0, 2 * np.pi))
           + (0.0 if plain_bg else 0.060 * np.cos((x / W - 0.5) * 2.0 + g.uniform(-0.4, 0.4)))
           + (0.0 if plain_bg else 0.040 * (y / H - 0.5)))
    img = img + g.normal(0, 0.012, (H, W))
    if kind == 1:                                            # 划痕：一条细长的暗线
        x0, y0 = g.uniform(6, W - 6), g.uniform(6, H - 6)
        ang, ln = g.uniform(0, np.pi), g.uniform(10, 26)
        t = np.clip(((x - x0) * np.cos(ang) + (y - y0) * np.sin(ang)) / ln, 0, 1)
        d = np.hypot(x - (x0 + t * ln * np.cos(ang)), y - (y0 + t * ln * np.sin(ang)))
        img -= 0.45 * sev * np.exp(-(d / 1.1) ** 2)
    elif kind == 2:                                          # 压痕：一个圆形的暗斑带亮边
        x0, y0, r = g.uniform(8, W - 8), g.uniform(8, H - 8), g.uniform(3, 6)
        d = np.hypot(x - x0, y - y0)
        img -= 0.40 * sev * np.exp(-(d / r) ** 2)
        img += 0.20 * sev * np.exp(-((d - r) / 1.3) ** 2)
    elif kind == 3:                                          # 锈斑：一片粗糙的亮斑
        x0, y0, r = g.uniform(8, W - 8), g.uniform(8, H - 8), g.uniform(4, 8)
        d = np.hypot(x - x0, y - y0)
        img += 0.35 * sev * np.exp(-(d / r) ** 2) * (1 + 0.5 * g.normal(0, 1, (H, W)))
    return np.clip(img, 0, 1)


def feats(img: np.ndarray) -> np.ndarray:
    """几个统计量当特征：整体明暗、起伏、最暗/最亮的局部、梯度的大小与方向集中度。"""
    gy, gx = np.gradient(img)
    mag = np.hypot(gx, gy)
    k = 5
    blocks = img[:H // k * k, :W // k * k].reshape(H // k, k, W // k, k).mean((1, 3))
    return np.array([img.mean(), img.std(), blocks.min(), blocks.max(),
                     mag.mean(), mag.max(), float(np.percentile(mag, 99)),
                     float(np.mean(np.abs(gx)) / (np.mean(np.abs(gy)) + 1e-9))])


def dataset(n: int, seed: int = 0, sev_range=SEV, kinds=(0, 1, 2, 3), p=PK, plain_bg: bool = False):
    """一批图的特征与标签（0 = 合格，1 = 有缺陷）。sev_range 与 kinds 用来做"分布偏了"的对照。"""
    g = np.random.default_rng(2600 + seed)
    X, y, ks_ = [], [], []
    for _ in range(n):
        kind = int(g.choice(kinds, p=p))
        sev = float(g.uniform(*sev_range))
        X.append(feats(defect_image(kind, sev, g, plain_bg)))
        y.append(int(kind > 0))
        ks_.append(kind)
    return np.array(X), np.array(y), np.array(ks_)


def knn_score(Xtr: np.ndarray, ytr: np.ndarray, Xte: np.ndarray, k: int = 7) -> np.ndarray:
    """最近邻打分：标准化之后找 k 个最近的训练样本，看其中有缺陷的比例。
    选它当案例里的检测器，是因为它**吃数据**——样本一多就明显变好，正好用来回答
    "再补几百张合成图有没有用"。"""
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    A, B = (Xtr - mu) / sd, (Xte - mu) / sd
    d = (B ** 2).sum(1)[:, None] + (A ** 2).sum(1)[None, :] - 2 * B @ A.T
    return ytr[np.argsort(d, 1)[:, :k]].mean(1)


def logistic(X: np.ndarray, y: np.ndarray, steps: int = 4000, lr: float = 0.5, l2: float = 1e-3):
    """逻辑回归（2.2 节），这里用来当"缺陷检测器"。"""
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.c_[(X - mu) / sd, np.ones(len(X))]
    w = np.zeros(Z.shape[1])
    for _ in range(steps):
        p = 1 / (1 + np.exp(-Z @ w))
        w -= lr * (Z.T @ (p - y) / len(y) + l2 * np.r_[w[:-1], 0.0])
    return w, mu, sd


def predict(w, mu, sd, X: np.ndarray) -> np.ndarray:
    Z = np.c_[(X - mu) / sd, np.ones(len(X))]
    return 1 / (1 + np.exp(-Z @ w))


def auc(score: np.ndarray, y: np.ndarray) -> float:
    """曲线下面积：随便挑一个有缺陷的和一个合格的，前者打分更高的概率。0.5 是瞎猜。"""
    r = np.argsort(np.argsort(score)) + 1
    n1, n0 = int(y.sum()), int((1 - y).sum())
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def recall_at_fpr(score: np.ndarray, y: np.ndarray, fpr: float = 0.05) -> float:
    """把误报率压到 fpr 时能查出多少缺陷——车间定门限就是按这个来的。"""
    thr = np.quantile(score[y == 0], 1 - fpr)
    return float(np.mean(score[y == 1] > thr))
