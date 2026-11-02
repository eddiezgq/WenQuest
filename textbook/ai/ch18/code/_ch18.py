"""第 18 章共用的玩具模型：结构评价指标、二维格点折叠、共进化信息、置信度的刻度、
虚拟筛选的富集与基率、分子划分口径、批次效应。

**为什么全是玩具**：这一章要讲清的几件事——"三个指标为什么会给出相反的结论""接触信息
值多少""自评分数高到底意味着什么""命中率看着高是因为阳性本来就少"——都是**几何与概率
问题**，不是生物问题。真蛋白上做不了对照实验（没有"同一个蛋白的另一种折叠"可比），而退
到二维格点与可控的模拟上，每一条都能**算到底**，还能和解析值核对。真模型上的对照放在两
个云端 GPU 实验里（ESMFold 预测一个真蛋白、图神经网络按两种划分评测）。

仓库里不放任何真实结构或化合物数据；所有坐标、序列、分子都由程序按规则生成。
"""
from __future__ import annotations

import numpy as np

# ================================================================ 一、结构评价指标（18.1 节）


def kabsch(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    """把 p 最优地叠合到 q 上（平移 + 旋转，不缩放），返回叠合后的 p。"""
    pc, qc = p - p.mean(0), q - q.mean(0)
    u, _, vt = np.linalg.svd(pc.T @ qc)
    d = np.sign(np.linalg.det(vt.T @ u.T))
    r = vt.T @ np.diag([1.0] * (p.shape[1] - 1) + [d]) @ u.T
    return pc @ r.T + q.mean(0)


def rmsd(model: np.ndarray, ref: np.ndarray) -> float:
    """叠合之后的均方根偏差（Å）。等权平均，所以少数几个大偏差就能支配它。"""
    m = kabsch(model, ref)
    return float(np.sqrt(((m - ref) ** 2).sum(1).mean()))


def gdt_ts(model: np.ndarray, ref: np.ndarray,
           cutoffs=(1.0, 2.0, 4.0, 8.0)) -> float:
    """GDT_TS = 四个距离截断下"落在截断内的残基百分比"的平均（官方定义，0—100）。

    CASP 用 LGA 做序列无关的叠合，还会为每个截断单独找最优叠合；这里用一次整体最优叠合
    近似，**所以本书的 GDT_TS 是"同一套坐标下的可比量"，不与 CASP 的数直接比**。
    """
    m = kabsch(model, ref)
    d = np.sqrt(((m - ref) ** 2).sum(1))
    return float(np.mean([100.0 * (d <= c).mean() for c in cutoffs]))


def lddt(model: np.ndarray, ref: np.ndarray, radius: float = 15.0,
         tols=(0.5, 1.0, 2.0, 4.0)) -> float:
    """lDDT：参考结构里半径 R0 之内的距离对，在模型里被"保持"的比例，四个容差取平均（0—1）。

    **不做叠合**——这是它与前两个指标的根本区别，也是本节要量的那件事：整个域摆一下，
    距离对基本没变，lDDT 几乎不扣分，而 RMSD 与 GDT_TS 会塌。
    """
    dr = np.linalg.norm(ref[:, None] - ref[None, :], axis=-1)
    dm = np.linalg.norm(model[:, None] - model[None, :], axis=-1)
    i, j = np.triu_indices(len(ref), k=2)          # 跳过相邻残基（它们的距离是化学键定死的）
    sel = dr[i, j] < radius
    if not sel.any():
        return 1.0
    diff = np.abs(dm[i, j][sel] - dr[i, j][sel])
    return float(np.mean([(diff < t).mean() for t in tols]))


def tm_score(model: np.ndarray, ref: np.ndarray) -> float:
    """TM-score：d0 随长度归一，所以随机结构对恒在 0.17 附近，与蛋白大小无关。"""
    n = len(ref)
    d0 = 1.24 * (n - 15) ** (1 / 3) - 1.8 if n > 15 else 0.5
    m = kabsch(model, ref)
    d = np.sqrt(((m - ref) ** 2).sum(1))
    return float(np.mean(1.0 / (1.0 + (d / d0) ** 2)))


def _globule(n: int, radius: float, g: np.random.Generator) -> np.ndarray:
    """一个紧实的球状结构域：在球内撒点，再按最近邻串成一条链（当 Cα 轨迹用）。"""
    p = g.normal(size=(n, 3))
    p /= np.linalg.norm(p, axis=1, keepdims=True)
    p *= (radius * g.random(n) ** (1 / 3))[:, None]
    order, left = [0], set(range(1, n))
    while left:
        last = p[order[-1]]
        nxt = min(left, key=lambda i: float(np.linalg.norm(p[i] - last)))
        order.append(nxt); left.remove(nxt)
    return p[order]


def two_domain(n_per: int = 60, gap: float = 26.0, radius: float = 9.0,
               seed: int = 0) -> np.ndarray:
    """造一个两域蛋白的 Cα 轨迹：两个紧实的球状域，中心相距 `gap`，中间一小段连接。

    尺度是照真蛋白取的：一个 60 残基的小域半径约 9 Å，两域中心相距约 26 Å。**这件事要紧**
    ——lDDT 的包含半径是 15 Å，所以 15 Å 之内的残基对绝大多数是**域内**的；域间只有界面
    附近那一小撮。这正是"整个域摆一下，lDDT 几乎不扣分"的来由。
    """
    g = np.random.default_rng(seed)
    a = _globule(n_per, radius, g)
    b = _globule(n_per, radius, g) + np.array([gap, 0.0, 0.0])
    return np.concatenate([a, b], 0)


def hinge(coords: np.ndarray, angle_deg: float, split: int | None = None) -> np.ndarray:
    """把第二个域整体绕连接处转一个角度——域内一点没变，只是两域的相对取向变了。"""
    split = len(coords) // 2 if split is None else split
    a, b = coords[:split], coords[split:]
    pivot = b[0]
    th = np.deg2rad(angle_deg)
    r = np.array([[np.cos(th), -np.sin(th), 0.0],
                  [np.sin(th), np.cos(th), 0.0],
                  [0.0, 0.0, 1.0]])
    return np.concatenate([a, (b - pivot) @ r.T + pivot], 0)


def jitter(coords: np.ndarray, sigma: float, seed: int = 1) -> np.ndarray:
    """每个残基各自抖一点——局部变差，但整体折叠还在。与 hinge 正好是相反的一种错。"""
    g = np.random.default_rng(seed)
    return coords + g.normal(0, sigma, coords.shape)


def random_chain(n: int, seed: int = 2) -> np.ndarray:
    """一条自由的随机链：用来核对"随机结构对的 TM-score 约 0.17"。"""
    g = np.random.default_rng(seed)
    step = g.normal(size=(n, 3))
    step /= np.linalg.norm(step, axis=1, keepdims=True)
    return np.cumsum(step * 3.8, 0)                 # Cα—Cα 约 3.8 Å


def rotate_chain(coords: np.ndarray, angle_deg: float, split: int | None = None) -> np.ndarray:
    """把第二条链绕**它自己的中心**转一个角度：两条链各自一点没动，中心也没动，
    变的只是它拿哪一面朝向对方——这正是复合物预测最常见的那种错（"对接对错了面"）。"""
    split = len(coords) // 2 if split is None else split
    a, b = coords[:split], coords[split:]
    c = b.mean(0)
    th = np.deg2rad(angle_deg)
    r = np.array([[np.cos(th), 0.0, np.sin(th)],
                  [0.0, 1.0, 0.0],
                  [-np.sin(th), 0.0, np.cos(th)]])
    return np.concatenate([a, (b - c) @ r.T + c], 0)


def interface(coords: np.ndarray, split: int, cut: float = 14.0) -> set[tuple[int, int]]:
    """界面接触：分属两条链、且距离小于 `cut` 的残基对。

    真实的 DockQ 按**重原子** 5 Å 判界面接触；本书只有 Cα，所以截断取 14 Å（Cα 之间隔着
    侧链，等效距离要大得多）。**这是本书的玩具口径，不与任何公开的 DockQ 数值可比。**
    """
    a, b = coords[:split], coords[split:]
    d = np.linalg.norm(a[:, None] - b[None, :], axis=-1)
    i, j = np.where(d < cut)
    return set(zip(i.tolist(), j.tolist()))


def fnat(model: np.ndarray, ref: np.ndarray, split: int, cut: float = 14.0) -> float:
    """fnat：参考复合物的界面接触，在模型里被复现了几成。DockQ 的三个成分之一。"""
    r = interface(ref, split, cut)
    if not r:
        return 1.0
    return len(interface(model, split, cut) & r) / len(r)


def chain_quality(model: np.ndarray, ref: np.ndarray, split: int) -> tuple[float, float]:
    """两条链各自的 lDDT——"每条链自己对不对"，与界面对不对是两件事。"""
    return (lddt(model[:split], ref[:split]), lddt(model[split:], ref[split:]))


def dockq_band(f: float, bands) -> str:
    """按 DockQ 的四档给一个档位名（本书只用分档，不自造 DockQ 的具体数值）。"""
    for lo, hi, name in bands:
        if lo <= f < hi:
            return name
    return bands[-1][2]


# ================================================================ 二、二维格点折叠（18.2 节）
#
# HP 模型：序列只有两种残基，H（疏水）与 P（亲水）。链走在二维方格上，不能自交。
# 能量 = −（空间相邻但序列上不相邻的 H—H 对数）。折叠问题就是找能量最低的走法。

MOVES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def fold_energy(path: tuple[tuple[int, int], ...], seq: str) -> int:
    """H—H 接触数的相反数。能量越低越好。"""
    pos = {p: i for i, p in enumerate(path)}
    e = 0
    for i, (x, y) in enumerate(path):
        if seq[i] != "H":
            continue
        for dx, dy in ((1, 0), (0, 1)):             # 每对只数一次
            j = pos.get((x + dx, y + dy))
            if j is not None and seq[j] == "H" and abs(j - i) > 1:
                e -= 1
    return e


def contacts(path: tuple[tuple[int, int], ...]) -> set[tuple[int, int]]:
    """接触图：空间相邻（格点距离 1）且序列上不相邻的残基对。"""
    pos = {p: i for i, p in enumerate(path)}
    out = set()
    for i, (x, y) in enumerate(path):
        for dx, dy in ((1, 0), (0, 1)):
            j = pos.get((x + dx, y + dy))
            if j is not None and abs(j - i) > 1:
                out.add((min(i, j), max(i, j)))
    return out


def walk(moves: tuple[int, ...]) -> tuple[tuple[int, int], ...] | None:
    """按一串方向走出一条链；自交就返回 None。"""
    x = y = 0
    path = [(0, 0)]
    seen = {(0, 0)}
    for m in moves:
        dx, dy = MOVES[m]
        x, y = x + dx, y + dy
        if (x, y) in seen:
            return None
        seen.add((x, y))
        path.append((x, y))
    return tuple(path)


def enumerate_folds(n: int) -> list[tuple[tuple[int, int], ...]]:
    """枚举长度 n 的全部自回避走法（第一步固定向右，去掉平移与一半的镜像对称）。"""
    out: list[tuple[tuple[int, int], ...]] = []

    def rec(path: list[tuple[int, int]], seen: set[tuple[int, int]]):
        if len(path) == n:
            out.append(tuple(path))
            return
        x, y = path[-1]
        for dx, dy in MOVES:
            p = (x + dx, y + dy)
            if p in seen:
                continue
            seen.add(p); path.append(p)
            rec(path, seen)
            path.pop(); seen.remove(p)

    rec([(0, 0), (1, 0)], {(0, 0), (1, 0)})
    return out


def native(seq: str, folds: list) -> tuple[int, int, tuple]:
    """全枚举求基态：返回 (最低能量, 简并度, 其中一条基态走法)。"""
    es = np.array([fold_energy(f, seq) for f in folds])
    lo = int(es.min())
    return lo, int((es == lo).sum()), folds[int(np.argmin(es))]


def unique_structures(folds: list, fold_contacts: list[set]):
    """按接触图去重。

    格点上每条走法都有一个镜像双胞胎，接触图一模一样、能量也一模一样。物理上它们是**同一
    个结构**，所以谈"基态唯不唯一"必须先按接触图去重，否则简并度永远至少是 2。
    返回 (代表走法, 对应的接触图)。
    """
    seen: dict = {}
    reps, cs = [], []
    for f, c in zip(folds, fold_contacts):
        k = frozenset(c)
        if k not in seen:
            seen[k] = len(reps)
            reps.append(f); cs.append(c)
    return reps, cs


def design_sequence(target: set, n_res: int) -> str:
    """最朴素的"反向折叠"：目标结构里接触数多的位置排 H，其余排 P。

    真方法（如 ProteinMPNN）当然复杂得多，但出发点是同一个——**让该埋起来的位置疏水**。
    本书用它来说明一件事：序列不是随便选的，按结构去挑能把成功率提上去。
    """
    deg = np.zeros(n_res, int)
    for i, j in target:
        deg[i] += 1; deg[j] += 1
    return "".join("H" if d > 0 else "P" for d in deg)


def contact_matrix(fold_contacts: list[set], n_res: int) -> np.ndarray:
    """把每条走法的接触图压成一行 0/1（上三角、跳过相邻残基），形状 (走法数, 对数)。"""
    pairs = [(i, j) for i in range(n_res) for j in range(i + 2, n_res)]
    idx = {p: k for k, p in enumerate(pairs)}
    m = np.zeros((len(fold_contacts), len(pairs)), dtype=np.int8)
    for r, cs in enumerate(fold_contacts):
        for p in cs:
            m[r, idx[p]] = 1
    return m


def all_sequences(n_res: int) -> np.ndarray:
    """全部 2^n 条 H/P 序列，H 记 1。"""
    k = np.arange(2 ** n_res)
    return ((k[:, None] >> np.arange(n_res)) & 1).astype(np.int8)


def designability(n_res: int, fold_contacts: list[set], chunk: int = 256):
    """把全部序列、全部走法过一遍，统计每条序列的基态。

    返回 (基态能量, 简并度, 基态走法编号)，长度都是 2^n_res；简并度 > 1 的序列"没有唯一
    的折法"。这件事在真蛋白上做不到（序列空间是 20^n），而在格点上能**穷尽**——于是
    "可设计性"这个概念可以被算出来，而不是被说出来。
    """
    fm = contact_matrix(fold_contacts, n_res)                 # (走法, 对)
    seqs = all_sequences(n_res)
    pairs = [(i, j) for i in range(n_res) for j in range(i + 2, n_res)]
    ii = np.array([p[0] for p in pairs]); jj = np.array([p[1] for p in pairs])
    lo = np.empty(len(seqs), np.int16)
    deg = np.empty(len(seqs), np.int32)
    arg = np.empty(len(seqs), np.int32)
    for s in range(0, len(seqs), chunk):
        blk = seqs[s:s + chunk]
        hh = (blk[:, ii] & blk[:, jj]).astype(np.int8)        # (序列, 对) 两端都是 H
        e = -(hh @ fm.T).astype(np.int16)                     # (序列, 走法)
        lo[s:s + chunk] = e.min(1)
        deg[s:s + chunk] = (e == e.min(1, keepdims=True)).sum(1)
        arg[s:s + chunk] = e.argmin(1)
    return lo, deg, arg


def survivors(fold_contacts: list[set], known: set) -> np.ndarray:
    """哪些走法**满足全部**已知接触。这就是"接触信息把搜索空间缩到多小"的直接度量。"""
    return np.array([known <= c for c in fold_contacts])


def information_curve(fold_contacts: list[set], energies: np.ndarray,
                      native_contacts: set, ks: tuple[int, ...], seed: int,
                      repeats: int = 40) -> list[tuple[int, float, float, float]]:
    """给 k 条**正确**的接触，平均下来还剩多少条走法、其中最低能量是多少、基态占多大比例。

    每个 k 随机抽 `repeats` 组接触取平均。返回 [(k, 还剩几条, 剩下里的最低能量, 基态占比%)]。
    """
    g = np.random.default_rng(seed)
    nat = sorted(native_contacts)
    lo = float(energies.min())
    rows = []
    for k in ks:
        left, best, frac = [], [], []
        for _ in range(repeats if k else 1):
            known = set(map(tuple, (np.array(nat, dtype=object)[
                g.choice(len(nat), size=k, replace=False)] if k else [])))
            sel = survivors(fold_contacts, known)
            left.append(int(sel.sum()))
            e = energies[sel]
            best.append(float(e.min()) if len(e) else float("nan"))
            frac.append(float((e == lo).mean() * 100) if len(e) else float("nan"))
        rows.append((k, float(np.mean(left)), float(np.mean(best)), float(np.mean(frac))))
    return rows


def one_wrong_contact(fold_contacts: list[set], energies: np.ndarray,
                      native_contacts: set, n_res: int, k: int, seed: int,
                      repeats: int = 40) -> tuple[float, float]:
    """k 条接触里混进**一条错的**，还剩多少条走法、还能不能找回基态（找回的比例 %）。"""
    g = np.random.default_rng(seed)
    nat = sorted(native_contacts)
    allp = [(i, j) for i in range(n_res) for j in range(i + 2, n_res)]
    wrong_pool = [p for p in allp if p not in native_contacts]
    lo = float(energies.min())
    left, ok = [], []
    for _ in range(repeats):
        take = [nat[t] for t in g.choice(len(nat), size=k - 1, replace=False)]
        bad = wrong_pool[int(g.integers(0, len(wrong_pool)))]
        sel = survivors(fold_contacts, set(take) | {bad})
        left.append(int(sel.sum()))
        e = energies[sel]
        ok.append(bool(len(e) and e.min() == lo))
    return float(np.mean(left)), float(np.mean(ok) * 100)


# ================================================================ 三、共进化：接触从哪里来（18.2 节）


def simulate_msa(n_res: int, pairs: list[tuple[int, int]], depth: int,
                 seed: int, coupling: float = 0.9, burn: int = 60) -> np.ndarray:
    """模拟一份多序列比对：每列两种状态（0/1），接触上的两列之间有耦合。

    用的是最简单的伊辛模型：能量 = −J·Σ_{(i,j)∈接触} s_i s_j（s = ±1），吉布斯采样。
    物理意思就是共进化：两个残基在空间上挨着，谁变了另一个得跟着变，否则结构散掉。

    这个模型有一个与真实情况一样的性质——**相关不等于接触**：i 和 j 接触、j 和 k 接触，
    那么 i 和 k 之间也会出现相关，尽管它们并不接触。这正是"只看两列相关"会混进假接触的
    来由（真实方法要做去卷积才分得开）。返回形状 (depth, n_res) 的 0/1 矩阵。
    """
    g = np.random.default_rng(seed)
    nb: list[list[int]] = [[] for _ in range(n_res)]
    for i, j in pairs:
        nb[i].append(j); nb[j].append(i)
    s = g.choice([-1, 1], size=n_res)
    out = np.empty((depth, n_res), dtype=int)
    for t in range(burn + depth):
        for i in range(n_res):
            h = coupling * sum(s[j] for j in nb[i])
            p = 1.0 / (1.0 + np.exp(-2.0 * h))      # P(s_i = +1)
            s[i] = 1 if g.random() < p else -1
        if t >= burn:
            out[t - burn] = (s > 0).astype(int)
    return out


def coevolution_scores(msa: np.ndarray) -> np.ndarray:
    """每一对列的互信息。深度越浅，这个估计越被噪声淹没。"""
    d, n = msa.shape
    s = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            tab = np.zeros((2, 2))
            for a in (0, 1):
                for b in (0, 1):
                    tab[a, b] = np.sum((msa[:, i] == a) & (msa[:, j] == b))
            p = tab / d
            pi, pj = p.sum(1, keepdims=True), p.sum(0, keepdims=True)
            with np.errstate(divide="ignore", invalid="ignore"):
                t = p * np.log(p / (pi * pj))
            s[i, j] = s[j, i] = float(np.nansum(t))
    return s


def indirect_demo(depth: int, seed: int, coupling: float = 0.9):
    """三个残基串成一条链：0—1 接触、1—2 接触，**0 和 2 不接触**。

    返回三对的互信息。要看的是：0 与 2 之间照样有不小的互信息——**相关不等于接触**。
    这就是为什么只看两列相关会混进假接触，而真实方法必须做一步"去卷积"。
    """
    msa = simulate_msa(3, [(0, 1), (1, 2)], depth, seed, coupling=coupling, burn=200)
    s = coevolution_scores(msa)
    return float(s[0, 1]), float(s[1, 2]), float(s[0, 2])


def contact_precision(scores: np.ndarray, truth: list[tuple[int, int]], top: int) -> float:
    """取分数最高的 top 对，看有几对是真接触。"""
    n = len(scores)
    i, j = np.triu_indices(n, k=2)
    order = np.argsort(-scores[i, j])[:top]
    picked = {(int(i[k]), int(j[k])) for k in order}
    return len(picked & set(truth)) / top


# ================================================================ 四、置信度的刻度（18.2、18.7 节）


SMOOTH = 3          # 自评分数沿序列是平滑的——相邻残基共用同一片环境


def confidence_sample(n: int, r: float, seed: int, z_shift: float = 0.0,
                      spread: float = 17.0, base: float = 70.0):
    """造一批残基：自评分数 s（当 pLDDT 用，0—100）与真实误差 e（Å），两者相关系数约为 r。

    r 取资料卡里那条拟合的 0.76。**这一节要量的就是"r = 0.76 到底意味着什么"**：
    相关性听着很高，可自评 90 分以上的残基里仍然有一撮误差大得不能用。
    """
    g = np.random.default_rng(seed)
    raw = g.normal(size=n + 2 * SMOOTH)
    ker = np.ones(2 * SMOOTH + 1) / (2 * SMOOTH + 1)
    sm = np.convolve(raw, ker, mode="same")[SMOOTH:SMOOTH + n]
    z1 = sm / (sm.std() + 1e-9) + z_shift    # 这一段"本来有多好"（沿序列平滑：相邻残基处境相近）
    z2 = r * z1 + np.sqrt(max(0.0, 1 - r * r)) * g.normal(size=n)
    score = np.clip(base + spread * z1, 1, 99)
    err = np.exp(0.75 - 0.75 * z2)           # 对数正态：误差不会是负的，而且右边拖一条长尾
    return score, err


def protein_regions(n_core: int, n_linker: int, n_tail: int, r: float, seed: int):
    """造一条分三段的蛋白：紧实的核心域、柔性连接段、末端尾巴。

    三段的自评分数分布不同（核心高、连接段中、尾巴低），但**同一条相关系数 r** 把分数与
    真实误差绑在一起。返回 (分数, 误差, 段标号 0/1/2)。
    """
    parts = ((n_core, 0.95), (n_linker, -0.60), (n_tail, -1.55))
    ss, ee, rr = [], [], []
    for k, (m, shift) in enumerate(parts):
        s, e = confidence_sample(m, r, seed + k, z_shift=shift)
        ss.append(s); ee.append(e); rr.append(np.full(m, k))
    return np.concatenate(ss), np.concatenate(ee), np.concatenate(rr)


def band_stats(score: np.ndarray, err: np.ndarray, lo: float, hi: float, bad: float):
    """某一档自评分数里：有多少残基、误差中位数多少、误差超过 bad 的占多少。"""
    sel = (score >= lo) & (score < hi)
    if not sel.any():
        return 0, float("nan"), float("nan")
    e = err[sel]
    return int(sel.sum()), float(np.median(e)), float((e > bad).mean() * 100)


# ================================================================ 五、虚拟筛选：富集与基率（18.5 节）


def library(n: int, active_frac: float, seed: int, auc: float = 0.80):
    """造一个化合物库：active_frac 的比例是真活性；打分函数的分辨能力由 auc 定。

    返回 (打分, 是否活性)。打分越高越像活性，但两堆分布是重叠的——这正是问题所在。
    """
    g = np.random.default_rng(seed)
    act = g.random(n) < active_frac
    # 两个等方差正态，均值差 d 与 AUC 的关系：AUC = Φ(d/√2)
    from math import erf, sqrt
    def phi_inv(p):
        lo, hi = -6.0, 6.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if 0.5 * (1 + erf(mid / sqrt(2))) < p:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    d = phi_inv(auc) * np.sqrt(2)
    s = g.normal(size=n) + act * d
    return s, act


def enrichment(score: np.ndarray, act: np.ndarray, frac: float) -> float:
    """EF_x% =（前 x% 里的活性比例）/（全库的活性比例）。"""
    k = max(1, int(round(len(score) * frac)))
    top = np.argsort(-score)[:k]
    base = act.mean()
    return float(act[top].mean() / base) if base > 0 else float("nan")


def hit_rate(score: np.ndarray, act: np.ndarray, n_tested: int) -> float:
    """买回来测 n_tested 个（按分数从高到低挑），命中率是多少（%）。"""
    top = np.argsort(-score)[:n_tested]
    return float(act[top].mean() * 100)


# ================================================================ 六、划分口径（18.5 节）


def molecules(n: int, n_scaffold: int, seed: int, scaffold_effect: float = 1.6,
              n_fp: int = 8, n_sub: int = 4):
    """造一批"分子"：每个分子属于一个骨架，描述符分两段。

    - **骨架指纹**（前 `n_fp` 维）：同一骨架的分子这几维几乎一样——真实的分子指纹就是这样，
      共用骨架的分子彼此看起来很像。
    - **取代基描述符**（后 `n_sub` 维）：每个分子各不相同。

    标签由**取代基**（真信号）与**骨架自身的偏置**共同决定。于是出现真实数据里的那件事：
    "这个骨架大多是活性的"是一条又好用又**不可外推**的捷径。
    """
    g = np.random.default_rng(seed)
    scaf = g.integers(0, n_scaffold, size=n)
    fp = g.normal(0, 1.0, size=(n_scaffold, n_fp))
    bias = g.normal(0, scaffold_effect, size=n_scaffold)
    sub = g.normal(size=(n, n_sub))
    x = np.concatenate([fp[scaf] + g.normal(0, 0.12, size=(n, n_fp)), sub], 1)
    w = np.array([1.0, -0.7, 0.4, 0.2])[:n_sub]
    logit = sub @ w + bias[scaf]
    y = (logit + g.normal(0, 0.6, size=n) > 0).astype(int)
    return x, y, scaf


def knn_score(x_tr: np.ndarray, y_tr: np.ndarray, x_te: np.ndarray, k: int = 5) -> np.ndarray:
    """最近邻打分：测试分子在训练集里最像的 k 个，有几个是活性的。

    这是"按类似物记忆"的最直白写法。随机划分时它好得惊人——因为测试分子在训练集里几乎
    总有同骨架的近亲；骨架划分一上，这条路就断了。
    """
    d = np.linalg.norm(x_te[:, None] - x_tr[None, :], axis=-1)
    nn = np.argsort(d, axis=1)[:, :k]
    return y_tr[nn].mean(1)


def split_random(n: int, seed: int, test_frac: float = 0.2):
    g = np.random.default_rng(seed)
    idx = g.permutation(n)
    k = int(n * test_frac)
    return idx[k:], idx[:k]


def split_scaffold(scaf: np.ndarray, seed: int, test_frac: float = 0.2):
    """按骨架划分：整个骨架要么全在训练集、要么全在测试集。"""
    g = np.random.default_rng(seed)
    groups = g.permutation(np.unique(scaf))
    test: list[int] = []
    need = int(len(scaf) * test_frac)
    for s in groups:
        if len(test) >= need:
            break
        test.extend(np.where(scaf == s)[0].tolist())
    test_set = set(test)
    train = np.array([i for i in range(len(scaf)) if i not in test_set])
    return train, np.array(sorted(test_set))


def fit_logistic(x: np.ndarray, y: np.ndarray, steps: int = 600, lr: float = 0.25):
    """一个最朴素的逻辑回归（手写梯度下降），不依赖任何机器学习库。"""
    xb = np.concatenate([x, np.ones((len(x), 1))], 1)
    w = np.zeros(xb.shape[1])
    for _ in range(steps):
        p = 1 / (1 + np.exp(-xb @ w))
        w -= lr * xb.T @ (p - y) / len(y)
    return w


def auc_score(y: np.ndarray, s: np.ndarray) -> float:
    """ROC 曲线下面积，用秩和算。"""
    order = np.argsort(s)
    ranks = np.empty(len(s), float)
    ranks[order] = np.arange(1, len(s) + 1)
    pos, neg = y.sum(), (1 - y).sum()
    if pos == 0 or neg == 0:
        return float("nan")
    return float((ranks[y == 1].sum() - pos * (pos + 1) / 2) / (pos * neg))


def predict(w: np.ndarray, x: np.ndarray) -> np.ndarray:
    xb = np.concatenate([x, np.ones((len(x), 1))], 1)
    return 1 / (1 + np.exp(-xb @ w))


# ================================================================ 七、批次效应（18.6 节）


def cells(n_per: int, n_gene: int, seed: int, batch_shift: float = 0.9,
          type_sep: float = 0.40, noise: float = 0.55,
          batch_p=(0.80, 0.50, 0.20)):
    """造两批细胞、三种类型：真实差别是细胞类型，批次只是一个整体平移。

    两件事是照真实数据取的，也正是这一节要讲的难处：
    - **类型之间本来就不那么分得开**（`type_sep` 只比噪声大一点）；
    - **批次与类型是混杂的**：`batch_p` 给出每种类型落在第 0 批的概率，三种类型各不相同，
      所以"把每一批的均值减掉"会连真实的类型差别一起减掉一部分。真实实验里两批的细胞
      组成从来不会完全一样。

    返回 (表达矩阵, 细胞类型, 批次)。
    """
    g = np.random.default_rng(seed)
    types = np.repeat([0, 1, 2], n_per)
    centers = g.normal(0, type_sep, size=(3, n_gene))
    x = centers[types] + g.normal(0, noise, size=(len(types), n_gene))
    p = np.array(batch_p)[types]
    batch = (g.random(len(types)) > p).astype(int)      # 1 表示第 1 批
    shift = g.normal(0, batch_shift, size=n_gene)
    x = x + batch[:, None] * shift
    return x, types, batch


def pca(x: np.ndarray, k: int = 2) -> np.ndarray:
    xc = x - x.mean(0)
    _, _, vt = np.linalg.svd(xc, full_matrices=False)
    return xc @ vt[:k].T


def correct_batch(x: np.ndarray, batch: np.ndarray, n_remove: int) -> np.ndarray:
    """按"去掉几个方向"来校正批次效应。

    - `n_remove = 0`：不校正。
    - `n_remove = 1`：把**批次方向**（两批均值之差的方向）投影掉。这是最常见的做法的骨架。
    - `n_remove ≥ 2`：除批次方向外，再把数据里**方差最大的那几个方向**也投影掉。

    最后这一档就是真实分析里常犯的"校正过度"：多去掉的那些方向里装着**真实的生物学差别**。
    它的危险之处在于——**批次混得更匀了**（校正的常用指标会更好看），而细胞类型被抹平了。
    """
    xc = x - x.mean(0)
    if n_remove <= 0:
        return xc
    dirs = [x[batch == 1].mean(0) - x[batch == 0].mean(0)]
    work = xc.copy()
    for _ in range(n_remove):
        d = dirs.pop(0) if dirs else None
        if d is None:                                   # 再去掉当前方差最大的那个方向
            _, _, vt = np.linalg.svd(work, full_matrices=False)
            d = vt[0]
        d = d / np.linalg.norm(d)
        work = work - np.outer(work @ d, d)
    return work


def neighbour_purity(z: np.ndarray, label: np.ndarray, k: int = 15) -> float:
    """每个点的 k 个最近邻里，标签和它一样的比例。用来量"同类聚不聚得到一起"。"""
    d = np.linalg.norm(z[:, None] - z[None, :], axis=-1)
    np.fill_diagonal(d, np.inf)
    nn = np.argsort(d, axis=1)[:, :k]
    return float((label[nn] == label[:, None]).mean())


def mixing(z: np.ndarray, batch: np.ndarray, k: int = 15) -> float:
    """每个点的 k 个最近邻里，**另一批**的比例。批次混得越匀越接近 0.5。"""
    d = np.linalg.norm(z[:, None] - z[None, :], axis=-1)
    np.fill_diagonal(d, np.inf)
    nn = np.argsort(d, axis=1)[:, :k]
    return float((batch[nn] != batch[:, None]).mean())
