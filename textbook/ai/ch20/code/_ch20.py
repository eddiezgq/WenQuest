"""第 20 章共用的玩具模型：候选空间的组合爆炸、晶体的图表示与它分不开的东西、
机器学习原子间势、能量准不等于性质准、训练集的划分口径、凸包与稳定性、自主实验室的闭环。

**为什么全是玩具**：这一章要讲清的几件事——"候选空间为什么大到挨个算不可能""描述子
能分辨什么""能量误差很小为什么力和声子还是错的""按帧划分为什么会让误差好出一个数量级"
"稳定是对谁而言""测量偏差为什么比噪声致命"——都是**表示、拟合与统计问题，不是材料学
问题**。真材料上这些量测不准（每一次都混着泛函、赝势、收敛参数、实验条件好几件事），
而退到一维周期晶体、解析对势与可控的响应面上，每一条都能算到底，还能与解析值核对。
真模型上的对照放在云端 GPU 实验 20.3 里，由学生自己跑。

仓库里不放任何晶体结构、第一性原理或实验数据；所有结构、能量、测量都由程序按规则生成。
"""
from __future__ import annotations

import itertools
import math

import numpy as np

# ================================================================ 一、候选空间有多大（20.1 节）


def n_compositions(n_elements: int, grid: int) -> int:
    """把成分按 1/grid 的步长撒点，`n_elements` 元体系有多少个成分点。

    这是把 grid 份额分给 n 个元素（每个至少 0 份、合计正好 grid 份）的方法数，
    即组合数 C(grid + n - 1, n - 1)。元素种类数固定时，它随元数**组合式**增长。
    """
    return math.comb(grid + n_elements - 1, n_elements - 1)


def n_candidates(n_pool: int, n_elements: int, grid: int) -> int:
    """从 `n_pool` 种元素里挑 `n_elements` 种，再按步长撒成分点，一共多少个候选。

    两处相乘：挑哪几种元素（组合数）× 每一种组合里的成分点数。这就是"组合爆炸"的全貌——
    加一元，两个因子同时变大。
    """
    return math.comb(n_pool, n_elements) * n_compositions(n_elements, grid)


def dft_years(n_calc: int, hours_each: float, n_parallel: int = 1) -> float:
    """`n_calc` 个第一性原理计算、每个 `hours_each` 小时、同时跑 `n_parallel` 个，要多少年。

    本函数只做单位换算，**不代表任何真实机器的速度**；每个算多久由调用方按资料卡给。
    """
    return n_calc * hours_each / n_parallel / 24 / 365.25


# ================================================================ 二、晶体的图表示（20.2 节）
#
# 用一维周期晶体：原子坐标是 0 … L-1 上的整数位置，周期 L。一维足够说明问题，
# 而且能把"两个不同结构给出完全相同的距离直方图"构造得干净、可验证。


def pair_distances(sites: list[int] | np.ndarray, L: int) -> np.ndarray:
    """一维周期晶体里所有原子对的距离（取周期最短距离），排好序返回。

    这正是**只看两体信息**的描述子所能看到的全部：谁离谁多远，不记谁是谁。
    """
    s = np.asarray(sites)
    d = []
    for i, j in itertools.combinations(range(len(s)), 2):
        gap = abs(int(s[i]) - int(s[j])) % L
        d.append(min(gap, L - gap))
    return np.array(sorted(d), dtype=float)


def homometric_pair(L: int = 18) -> tuple[list[int], list[int]]:
    """返回一对**同距（homometric）晶体**：两套原子位置不同，而所有原子对的距离集合完全一样。

    这不是凑出来的巧合，是晶体学里早就知道的事：由衍射得到的 Patterson 函数只含两体距离，
    所以两体信息**原则上不足以定结构**。周期 18 上的这两套位置是经典例子
    （{0,1,4,10,12,17} 与 {0,1,8,11,13,17}），互不相同、也不是彼此的平移或镜像。

    教学上的用处：任何只用"近邻距离"的描述子，对这两个结构给出一模一样的输入——
    **模型不是学不会，是看不见**。
    """
    a = [0, 1, 4, 10, 12, 17]
    b = [0, 1, 8, 11, 13, 17]
    return a, b


def same_up_to_symmetry(a: list[int], b: list[int], L: int) -> bool:
    """两套位置是不是只差一个平移或镜像（那样就不算两个不同结构了）。"""
    sa = tuple(sorted(x % L for x in a))
    for mirror in (1, -1):
        for shift in range(L):
            cand = tuple(sorted((mirror * x + shift) % L for x in b))
            if cand == sa:
                return True
    return False


def neighbor_graph(sites: list[int] | np.ndarray, L: int, cutoff: float) -> list[tuple[int, int, float]]:
    """按截断半径建图：距离不超过 `cutoff` 的原子对连一条边，边上带距离。

    截断半径是**人定的**，一改图就变——这是 20.2 节要让读者亲手感觉到的事。
    """
    s = np.asarray(sites)
    edges = []
    for i, j in itertools.combinations(range(len(s)), 2):
        gap = abs(int(s[i]) - int(s[j])) % L
        d = min(gap, L - gap)
        if d <= cutoff:
            edges.append((i, j, float(d)))
    return edges


def edge_histogram(sites: list[int] | np.ndarray, L: int, cutoff: float) -> np.ndarray:
    """截断半径以内的边长直方图（按整数距离计数）。两体描述子看到的就是这个。"""
    h = np.zeros(int(cutoff) + 1)
    for _, _, d in neighbor_graph(sites, L, cutoff):
        h[int(round(d))] += 1
    return h


def angle_feature(sites: list[int] | np.ndarray, L: int) -> np.ndarray:
    """一维里的"三体"特征：每个原子看它两侧最近邻的间距之比，排序后返回。

    一维没有真正的键角，但"相邻两段的长短搭配"扮演同样的角色：它是**三体**信息。
    同距的两个结构在这里就分开了——所以补上三体项是有用的，不是摆设。
    """
    s = np.sort(np.asarray(sites) % L)
    n = len(s)
    feats = []
    for i in range(n):
        left = (s[i] - s[(i - 1) % n]) % L
        right = (s[(i + 1) % n] - s[i]) % L
        lo, hi = sorted((float(left), float(right)))
        feats.append(lo / hi if hi else 0.0)
    return np.array(sorted(feats))


# ================================================================ 三、机器学习原子间势（20.3 节）
#
# 真值用一个解析对势（Lennard-Jones）：这样"精确答案"随时可得，拟合得好不好、
# 由它导出的性质对不对，都能一条条核。


LJ = {"eps": 1.0, "sigma": 1.0, "rcut": 2.6}

# 全章共用的径向基：24 个高斯、宽 0.09。各算例都用这一套，数字才能跨节比较。
BASIS = {"n": 24, "lo": 0.8, "hi": 2.6, "width": 0.09}


def basis_centers() -> np.ndarray:
    return np.linspace(BASIS["lo"], BASIS["hi"], BASIS["n"])


def lj_pair(r: np.ndarray | float) -> np.ndarray:
    """Lennard-Jones 对势能（截断处平移到零，免得能量跳变）。"""
    r = np.asarray(r, dtype=float)
    e, s, rc = LJ["eps"], LJ["sigma"], LJ["rcut"]
    u = 4 * e * ((s / r) ** 12 - (s / r) ** 6)
    ucut = 4 * e * ((s / rc) ** 12 - (s / rc) ** 6)
    return np.where(r < rc, u - ucut, 0.0)


def lj_force_pair(r: np.ndarray | float) -> np.ndarray:
    """对势的径向力 −du/dr（正值表示相斥）。"""
    r = np.asarray(r, dtype=float)
    e, s, rc = LJ["eps"], LJ["sigma"], LJ["rcut"]
    f = 24 * e * (2 * (s / r) ** 12 - (s / r) ** 6) / r
    return np.where(r < rc, f, 0.0)


def chain_distances(x: np.ndarray, L: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """一维周期链里所有原子对的距离，连同它们的下标。"""
    n = len(x)
    ii, jj, dd = [], [], []
    for i in range(n):
        for j in range(i + 1, n):
            d = x[j] - x[i]
            d -= L * round(d / L)                      # 周期最短像
            ii.append(i); jj.append(j); dd.append(d)
    return np.array(ii), np.array(jj), np.array(dd)


def lj_energy_forces(x: np.ndarray, L: float) -> tuple[float, np.ndarray]:
    """精确的总能量与每个原子受的力（一维周期链）。"""
    ii, jj, dd = chain_distances(x, L)
    r = np.abs(dd)
    energy = float(np.sum(lj_pair(r)))
    f = np.zeros(len(x))
    fr = lj_force_pair(r) * np.sign(dd)                # 作用在 j 上、沿 +dd 方向
    for i, j, fij in zip(ii, jj, fr):
        f[j] += fij
        f[i] -= fij
    return energy, f


def sample_configs(n_cfg: int, n_atoms: int, L: float, amp: float = 0.12,
                   seed: int = 0) -> list[np.ndarray]:
    """训练用的构型：在等间距晶格上**小幅扰动**，不是均匀随机撒点。

    这一条不是为了好看。均匀随机会把两个原子叠到一起，Lennard-Jones 的 r⁻¹² 立刻给出
    天文数字，最小二乘被一条样本带跑。真实的机器学习势训练集同样来自平衡附近的构型
    （晶格、松弛轨迹、分子动力学快照），**覆盖的就是平衡附近那一小块**——这也正是
    20.3 节"外推到没见过的构型会崩"的根源。
    """
    g = np.random.default_rng(seed)
    lat = np.arange(n_atoms) * (L / n_atoms)
    return [np.sort((lat + g.uniform(-amp, amp, n_atoms)) % L) for _ in range(n_cfg)]


def strained_configs(n_cfg: int, n_atoms: int, a_lo: float, a_hi: float,
                     amp: float = 0.06, seed: int = 0) -> list[tuple[np.ndarray, float]]:
    """**带均匀应变**的训练构型：晶格常数在 [a_lo, a_hi] 之间取，盒子跟着变，再小幅扰动。

    为什么要单独有这一类：只在一个固定盒子里扰动，训练集覆盖的是"体积不变"的那一片；
    而平衡间距、体弹模量、声子都要沿**均匀伸缩**这条路问问题。那条路上没有训练数据，
    拟合的势在那里就是无约束外推——这不是"算错了"，是**在没有定义的地方问了问题**。
    真实的机器学习势训练集同样要特意加入不同体积、不同应变的构型。
    """
    g = np.random.default_rng(seed)
    out = []
    for _ in range(n_cfg):
        a = g.uniform(a_lo, a_hi)
        box = n_atoms * a
        x = np.sort((np.arange(n_atoms) * a + g.uniform(-amp, amp, n_atoms)) % box)
        out.append((x, box))
    return out


def gaussian_basis(r: np.ndarray, centers: np.ndarray, width: float) -> np.ndarray:
    """径向高斯基：机器学习势里"对称函数"最朴素的一种。

    每个原子对按它的距离在若干个高斯上留下一份贡献，把它们加起来就是体系的特征——
    这保证了**置换不变**（换原子编号结果不变）与**平移、镜像不变**。
    """
    r = np.asarray(r, dtype=float)[:, None]
    return np.exp(-((r - centers[None, :]) ** 2) / (2 * width ** 2))


def featurize(x: np.ndarray, L: float, centers: np.ndarray, width: float) -> np.ndarray:
    """一个构型的特征向量：所有原子对在径向高斯上的总贡献。"""
    _, _, dd = chain_distances(x, L)
    r = np.abs(dd)
    keep = r < LJ["rcut"]
    return gaussian_basis(r[keep], centers, width).sum(0)


def featurize_forces(x: np.ndarray, L: float, centers: np.ndarray, width: float) -> np.ndarray:
    """特征对每个原子坐标的负导数，形状 (原子数, 基函数数)。

    有了它，**力也能进拟合**：力是能量的导数，而线性模型的导数仍是线性的，
    所以能量与力可以放进同一个最小二乘里。这是机器学习势的关键一步。
    """
    ii, jj, dd = chain_distances(x, L)
    r = np.abs(dd)
    keep = r < LJ["rcut"]
    ii, jj, dd, r = ii[keep], jj[keep], dd[keep], r[keep]
    g = gaussian_basis(r, centers, width)                       # (对数, 基数)
    dg_dr = -g * (r[:, None] - centers[None, :]) / width ** 2   # ∂g/∂r
    out = np.zeros((len(x), len(centers)))
    for k, (i, j, d) in enumerate(zip(ii, jj, dd)):
        s = np.sign(d)
        out[j] -= dg_dr[k] * s          # F = −∂E/∂x
        out[i] += dg_dr[k] * s
    return out


def fit_potential(frames: list[tuple[np.ndarray, float]], L: float, centers: np.ndarray,
                  width: float, force_weight: float = 0.0,
                  force_data: list[np.ndarray] | None = None, ridge: float = 1e-8) -> np.ndarray:
    """最小二乘拟一个线性机器学习势。`force_weight > 0` 时把力一起放进拟合。"""
    A, b = [], []
    for k, (x, e) in enumerate(frames):
        A.append(featurize(x, L, centers, width))
        b.append(e)
        if force_weight > 0 and force_data is not None:
            A.append(force_weight * featurize_forces(x, L, centers, width))
            b.append(force_weight * force_data[k])
    A = np.vstack([a if a.ndim == 2 else a[None, :] for a in A])
    b = np.concatenate([np.atleast_1d(v) for v in b])
    G = A.T @ A + ridge * np.eye(A.shape[1])
    return np.linalg.solve(G, A.T @ b)


def predict_energy(w: np.ndarray, x: np.ndarray, L: float, centers: np.ndarray, width: float) -> float:
    return float(featurize(x, L, centers, width) @ w)


def predict_forces(w: np.ndarray, x: np.ndarray, L: float, centers: np.ndarray, width: float) -> np.ndarray:
    return featurize_forces(x, L, centers, width) @ w


def verlet(x0: np.ndarray, v0: np.ndarray, L: float, dt: float, n_steps: int,
           force_fn, mass: float = 1.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """速度 Verlet 积分。返回末态位置、末态速度，以及每一步的总能量。

    总能量应当守恒——**它守不住的程度，就是这个势"不像个势"的程度**。
    """
    x, v = x0.copy(), v0.copy()
    e_tot = []
    e, f = force_fn(x)
    for _ in range(n_steps):
        v_half = v + 0.5 * dt * f / mass
        x = (x + dt * v_half) % L
        e, f = force_fn(x)
        v = v_half + 0.5 * dt * f / mass
        e_tot.append(e + 0.5 * mass * float(np.sum(v ** 2)))
    return x, v, np.array(e_tot)


# ================================================================ 四、能量准不等于性质准（20.3—20.4 节）


def phonon_omega(energy_fn, x_eq: np.ndarray, L: float, mass: float = 1.0,
                 h: float = 1e-4) -> np.ndarray:
    """在平衡构型上取能量的二阶导（动力学矩阵），返回声子频率。

    声子要的是能量曲面的**曲率**。能量本身差一点点无所谓，曲率差一点点，频率就偏。
    """
    n = len(x_eq)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            xpp = x_eq.copy(); xpp[i] += h; xpp[j] += h
            xpm = x_eq.copy(); xpm[i] += h; xpm[j] -= h
            xmp = x_eq.copy(); xmp[i] -= h; xmp[j] += h
            xmm = x_eq.copy(); xmm[i] -= h; xmm[j] -= h
            H[i, j] = (energy_fn(xpp) - energy_fn(xpm) - energy_fn(xmp) + energy_fn(xmm)) / (4 * h * h)
    H = 0.5 * (H + H.T)
    vals = np.linalg.eigvalsh(H / mass)
    return np.sqrt(np.maximum(vals, 0.0))


def relax(x0: np.ndarray, L: float, force_fn, step: float = 1e-3,
          n_iter: int = 4000, max_move: float = 0.02) -> tuple[np.ndarray, list[np.ndarray]]:
    """最速下降做结构松弛，返回末态与**整条轨迹**。

    轨迹是机器学习势训练数据的主要来源，也正是划分口径出问题的地方：
    同一条轨迹上相邻的帧几乎一样（20.4 节）。
    """
    x = x0.copy()
    traj = [x.copy()]
    for _ in range(n_iter):
        _, f = force_fn(x)
        dx = np.clip(step * f, -max_move, max_move)   # 限位：两个原子一旦靠近，r⁻¹² 的力能
        x = (x + dx) % L                              # 一步把坐标甩到无穷去（会出 NaN）
        traj.append(x.copy())
    return x, traj


# ================================================================ 五、训练集的划分口径（20.4 节）


def make_trajectories(n_sys: int, n_atoms: int, L: float, seed: int = 0,
                      n_frames: int = 12) -> list[dict]:
    """造若干个"体系"，每个体系给一条松弛轨迹（若干帧）。

    每个体系有自己的"成分"（这里用原子质量/相互作用强度的一个标签代替），同一成分下
    有几个不同的起始构型。于是三种划分口径都能试：按帧、按体系、按成分。
    """
    g = np.random.default_rng(seed)
    systems = []
    for k in range(n_sys):
        comp = k % max(1, n_sys // 3)                       # 成分标签：几个体系共用一个成分
        # 起点用**扰动过的晶格**，不是均匀随机：随机会把原子叠在一起，松弛第一步就崩
        lat = np.arange(n_atoms) * (L / n_atoms)
        x0 = np.sort((lat + g.uniform(-0.18, 0.18, n_atoms)) % L)
        scale = 1.0 + 0.04 * comp                            # 不同成分：势稍有不同

        def force_fn(x, scale=scale):
            e, f = lj_energy_forces(x, L)
            return e * scale, f * scale

        # **帧取在收敛附近、而且取密**：真实的结构松弛轨迹就是这样——绝大多数帧挤在
        # 收敛那一头，彼此只差千分之几。正是这件事让"按帧随机划分"变成泄漏。
        _, traj = relax(x0, L, force_fn, step=2e-4, n_iter=1200)
        frames = traj[-n_frames * 2::2]
        rows = []
        for x in frames:
            e, f = force_fn(x)
            rows.append({"x": x, "e": e, "f": f})
        systems.append({"sys": k, "comp": comp, "frames": rows})
    return systems


def split_frames(systems: list[dict], how: str, seed: int = 0,
                 test_frac: float = 0.25) -> tuple[list, list]:
    """三种划分口径。

    * ``frame``：所有帧混在一起随机划分——**同一条轨迹的相邻帧会分到两边**；
    * ``system``：整个体系要么全训练、要么全测试；
    * ``composition``：整个成分（含它下面所有体系）要么全训练、要么全测试。
    """
    g = np.random.default_rng(seed)
    flat = [(s["sys"], s["comp"], fr) for s in systems for fr in s["frames"]]
    if how == "frame":
        idx = g.permutation(len(flat))
        cut = int(len(flat) * test_frac)
        test = [flat[i] for i in idx[:cut]]
        train = [flat[i] for i in idx[cut:]]
        return train, test
    key = {"system": 0, "composition": 1}[how]
    groups = sorted({row[key] for row in flat})
    gp = g.permutation(groups)
    n_test = max(1, int(round(len(groups) * test_frac)))
    held = set(gp[:n_test].tolist())
    train = [r for r in flat if r[key] not in held]
    test = [r for r in flat if r[key] in held]
    return train, test


def energy_mae(w: np.ndarray, rows: list, L: float, centers: np.ndarray, width: float) -> float:
    """每个原子的能量平均绝对误差（材料界印的就是这个口径）。"""
    errs = [abs(predict_energy(w, fr["x"], L, centers, width) - fr["e"]) / len(fr["x"])
            for _, _, fr in rows]
    return float(np.mean(errs))


def force_mae(w: np.ndarray, rows: list, L: float, centers: np.ndarray, width: float) -> float:
    errs = [np.abs(predict_forces(w, fr["x"], L, centers, width) - fr["f"]).mean()
            for _, _, fr in rows]
    return float(np.mean(errs))


# ================================================================ 六、凸包与稳定性（20.4 节）


def convex_hull_lower(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """二维点集的**下凸包**（成分 x，形成能 y），按 x 排序返回顶点。

    材料里的"稳定"就是落在这条下凸包上。用叉积做单调链，点不多时足够且没有依赖。
    """
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    hull: list[tuple[float, float]] = []
    for p in pts:
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) <= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull


def hull_energy_at(hull: list[tuple[float, float]], x: float) -> float:
    """下凸包在成分 x 处的高度（线性插值）。"""
    for (x1, y1), (x2, y2) in zip(hull[:-1], hull[1:]):
        if x1 - 1e-12 <= x <= x2 + 1e-12:
            t = 0.0 if x2 == x1 else (x - x1) / (x2 - x1)
            return y1 + t * (y2 - y1)
    return hull[0][1] if x <= hull[0][0] else hull[-1][1]


def hull_distance(points: list[tuple[float, float]], extra: list[tuple[float, float]] | None = None
                  ) -> dict[tuple[float, float], float]:
    """每个点到下凸包的距离（eV/atom）。`extra` 是额外加进参考集的相。

    **这是本节的要点**：距离是对**参考集**算的。参考集里多一个相，别人的距离就变——
    原来落在包上（距离 0，"稳定"）的点可能一下子变成正距离（"不稳定"）。
    """
    ref = list(points) + list(extra or [])
    hull = convex_hull_lower(ref)
    return {p: p[1] - hull_energy_at(hull, p[0]) for p in points}


# ================================================================ 七、自主实验室的闭环（20.5 节）


def response_surface(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """要找最大值的那个二维"性质"面（越大越好）。两个局部峰，全局峰在 (0.72, 0.35) 附近。"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    main = np.exp(-(((a - 0.72) / 0.18) ** 2 + ((b - 0.35) / 0.22) ** 2))
    decoy = 0.72 * np.exp(-(((a - 0.22) / 0.16) ** 2 + ((b - 0.78) / 0.18) ** 2))
    return main + decoy


def measure(a: float, b: float, noise: float, bias: float, g: np.random.Generator) -> float:
    """做一次"实验"：真值加上随机噪声，再加上一个**系统偏差**。

    偏差这里取成随成分漂移的形式（越靠右越高估）——它不像噪声能靠多测几次抹平，
    而是把整张面**拧歪**，于是闭环会一路爬到错的地方去。
    """
    truth = float(response_surface(np.array([a]), np.array([b]))[0])
    return truth + noise * g.normal() + bias * (a - 0.5)


def kernel_ridge(X: np.ndarray, y: np.ndarray, Xq: np.ndarray, ls: float = 0.18,
                 lam: float = 1e-3) -> tuple[np.ndarray, np.ndarray]:
    """高斯核岭回归，返回查询点上的均值与一个"离已测点有多远"的不确定度代理。

    这是贝叶斯优化里代理模型最简单的一种。不确定度用"到最近已测点的核距离"代替，
    够用来演示"探索—利用"，而且不引入任何依赖。
    """
    def k(A, B):
        d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
        return np.exp(-d2 / (2 * ls ** 2))

    K = k(X, X) + lam * np.eye(len(X))
    alpha = np.linalg.solve(K, y)
    Kq = k(Xq, X)
    mean = Kq @ alpha
    sigma = np.sqrt(np.maximum(1.0 - Kq.max(axis=1) ** 2, 0.0))
    return mean, sigma


def closed_loop(strategy: str, budget: int, noise: float = 0.0, bias: float = 0.0,
                seed: int = 0, n_grid: int = 41, kappa: float = 1.5) -> dict:
    """自主实验室的闭环：提议 → 做实验 → 回填 → 再提议，一共做 `budget` 次。

    三种策略：``grid`` 按网格挨个试、``random`` 随机试、``bayes`` 用代理模型挑
    （均值 + kappa × 不确定度，即上置信界）。返回找到的最好点与它的**真值**——
    注意**判据要用真值**：被偏差带偏的闭环自己以为找到了好东西，所以不能拿测量值当成绩。
    """
    g = np.random.default_rng(seed)
    ax = np.linspace(0, 1, n_grid)
    AA, BB = np.meshgrid(ax, ax)
    cand = np.column_stack([AA.ravel(), BB.ravel()])
    tried: list[int] = []
    ys: list[float] = []

    for t in range(budget):
        if strategy == "grid":
            step = max(1, len(cand) // budget)
            nxt = (t * step) % len(cand)
        elif strategy == "random":
            nxt = int(g.integers(len(cand)))
        elif strategy == "bayes":
            if len(tried) < 3:
                nxt = int(g.integers(len(cand)))
            else:
                X = cand[tried]
                mean, sigma = kernel_ridge(X, np.array(ys), cand)
                score = mean + kappa * sigma
                score[tried] = -np.inf
                nxt = int(np.argmax(score))
        else:
            raise ValueError(strategy)
        if nxt in tried:                                     # 别把预算浪费在重复点上
            free = [i for i in range(len(cand)) if i not in tried]
            nxt = int(g.choice(free))
        tried.append(nxt)
        ys.append(measure(cand[nxt, 0], cand[nxt, 1], noise, bias, g))

    best_by_measure = int(np.argmax(ys))
    pick = cand[tried[best_by_measure]]
    truth_of_pick = float(response_surface(np.array([pick[0]]), np.array([pick[1]]))[0])
    truth_best = float(response_surface(AA.ravel(), BB.ravel()).max())
    return {"n": budget, "pick": pick, "truth_of_pick": truth_of_pick,
            "truth_best": truth_best, "regret": truth_best - truth_of_pick,
            "believed": float(ys[best_by_measure])}
