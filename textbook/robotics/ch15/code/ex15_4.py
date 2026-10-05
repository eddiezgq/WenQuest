"""15.4 节：关节限位与多目标。

(1) Panda（零件库 B-ARM-PANDA）：在关节限位以内随机取 60 组关节角，由它们算出可达的目标位姿；从 ready 姿态出发，比较四种做法：
    不管限位的伪逆牛顿-拉夫森法（结果加减 2π 后是否在限位内）；每步截断（式 (15.4.2)）；伪逆加零空间居中项（式 (15.4.7)）；
    每步解有界的阻尼最小二乘（式 (15.4.3)）。另外对每个目标再取 5 个随机起点，统计“至多 6 次尝试”的成功率（15.5.4 节用）。
(2) 算例 15.4.1：一个目标的详细结果：不管限位时三个关节超限，截断法卡在限位上，有界的一步收敛且全部在限位以内。
(3) 定理 15.4.1 的数值核对：有界的一步 Δ 满足 gᵀΔ ≤ −(‖W J Δ‖² + λ²‖Δ‖²)/2 < 0；截断法和有界法失败时停在 f 在限位“盒子”上的驻点
    （投影梯度为零）。定理 15.4.2：零空间项不改变 J Δ。
(4) 算例 15.4.2：平面 3R 臂（14.2.5 节），主任务为末端位置 (0.75, 0.10) m，次任务为工具朝向 φ_d = 160°；φ_d 落在式 (14.2.10)
    的可行范围之外。加权最小二乘两头都差一点；任务优先级（式 (15.4.9)）保证位置精确，朝向停在可行范围的端点；梯度投影 (15.4.7) 得同一结果。
    定理 15.4.3 在随机矩阵上核对：J₁(J₂N₁)⁺ = 0，优先级解在 J₁Δ = e₁ 的解中使 ‖J₂Δ − e₂‖ 最小。
"""
import math
import time

import numpy as np

from _nik import PL, err_twist, fk_planar, ik_limits, in_limits_mod, jac_planar, joint_center_grad, panda, wrap
from bookout import T as tr, out, vec

t_start = time.time()
deg = np.degrees
fk, jb, lo, hi, ready, pa = panda()
assert np.abs(fk(ready) - pa.fk(ready)).max() < 1e-12                       # 指数积与零件库模型核对
Lc, LAM, KC = 0.3, 1e-3, 3.0
W = np.diag([1, 1, 1] + [1 / Lc] * 3)


def proj_grad(q, V, J):
    """f = ½‖W V‖² 在限位盒子上的投影梯度（梯度近似取 −Jᵀ W² V，引理 15.1.1）：在下限处只留负分量，在上限处只留正分量。"""
    g = -J.T @ W @ W @ V
    pg = g.copy()
    at_lo, at_hi = q <= lo + 1e-9, q >= hi - 1e-9
    pg[at_lo] = np.minimum(g[at_lo], 0)
    pg[at_hi] = np.maximum(g[at_hi], 0)
    return pg, g


# ---------------------------------------------------------------- (1) 统计
rng = np.random.default_rng(154)
N = 60
modes = ("free", "clamp", "center", "box")
ok = {m: [] for m in modes}
inl = {m: [] for m in modes}
its = {m: [] for m in modes}
restart = {"clamp": [], "box": []}
rand_try = {"clamp": [], "box": []}
fail_pg = {"clamp": [], "box": []}
example = None
desc_worst = -np.inf                                                        # 定理 15.4.1 (3)：max (gᵀΔ + (‖WJΔ‖² + λ²‖Δ‖²)/2)
for trial in range(N):
    qt = rng.uniform(lo, hi)
    Td = fk(qt)
    res = {}
    for m in modes:
        H = [] if m == "box" else None
        q, c, k = ik_limits(fk, jb, Td, ready, lo, hi, m, Lc=Lc, lam=LAM, kc=KC, iters=300, hist=H)
        inside = in_limits_mod(q, lo, hi)
        ok[m].append(c)
        inl[m].append(c and inside)
        if c:
            its[m].append(k)
        res[m] = (q, c)
        if m == "box":
            for qq, V, d in H:
                J = jb(qq)
                g = -J.T @ W @ W @ V
                desc_worst = max(desc_worst, float(g @ d + 0.5 * (np.linalg.norm(W @ J @ d) ** 2 + LAM ** 2 * d @ d)) / (float(np.linalg.norm(g) * np.linalg.norm(d)) + 1e-300))
        if m in ("clamp", "box") and not c:
            V = err_twist(fk(q), Td)
            pg, g = proj_grad(q, V, jb(q))
            fail_pg[m].append(float(np.linalg.norm(pg) / np.linalg.norm(g)))
    r2 = np.random.default_rng(1000 + trial)
    starts = [r2.uniform(lo, hi) for _ in range(5)]
    for m in ("clamp", "box"):
        s = res[m][1]
        for s0 in starts:
            c = ik_limits(fk, jb, Td, s0, lo, hi, m, Lc=Lc, lam=LAM)[1]
            rand_try[m].append(c)
            s = s or c
        restart[m].append(s)
    if example is None and res["free"][1] and not in_limits_mod(res["free"][0], lo, hi) and res["box"][1] and not res["clamp"][1]:
        qc = res["clamp"][0]
        if np.linalg.norm(fk(qc)[:3, 3] - Td[:3, 3]) > 0.02:
            example = (trial, qt, {m: res[m][0] for m in modes}, {m: res[m][1] for m in modes})
assert example is not None
pct = lambda x: 100.0 * float(np.mean(x))
assert desc_worst < 1e-8                                                    # 定理 15.4.1 (3)：每一步都是下降方向（相对舍入误差）
pg_box = sorted(fail_pg["box"])
n_kkt_box = sum(x < 1e-6 for x in pg_box)
assert min(fail_pg["clamp"]) > 0.1                                          # 截断法停下的地方不是驻点
assert pct(inl["box"]) > pct(inl["free"]) and pct(restart["box"]) > pct(inl["box"])
p_rand = {m: pct(rand_try[m]) / 100 for m in rand_try}                      # 从一个随机起点出发的成功率
p_ready = {m: float(np.mean(ok[m])) for m in rand_try}                     # 从 ready 姿态出发的成功率
# 若各次尝试独立：ready 一次（成功率 p_ready）加 5 个随机起点（成功率 p），6 次中至少成功一次的概率
pred6 = {m: 100 * (1 - (1 - p_ready[m]) * (1 - p_rand[m]) ** 5) for m in rand_try}
n_hard = {m: int(N - sum(restart[m])) for m in rand_try}                    # 6 次全部失败的目标个数

# ---------------------------------------------------------------- (2) 算例 15.4.1
trial, qt, Q, C = example
Td = fk(qt)


def viol(q):
    return [i + 1 for i in range(7) if not in_limits_mod([q[i]], [lo[i]], [hi[i]])]


def mm(q):
    return float(np.linalg.norm(fk(q)[:3, 3] - Td[:3, 3]) * 1000)


def angle_deg(q):
    return math.degrees(float(np.linalg.norm(err_twist(fk(q), Td)[:3])))


def at_limit(q, tol=1e-6):
    return [i + 1 for i in range(7) if abs(q[i] - lo[i]) < tol or abs(q[i] - hi[i]) < tol]


def wrap_into(q):
    """把关节角加减 2π，尽量放进限位（放不进的取离区间最近的一个），用于报告。"""
    r = []
    for x, a, b in zip(q, lo, hi):
        cand = [x + 2 * math.pi * k for k in range(-4, 5)]
        r.append(min(cand, key=lambda y: 0 if a <= y <= b else min(abs(y - a), abs(y - b))))
    return np.array(r)


qf = wrap_into(Q["free"])
qc, qb, qn = Q["clamp"], Q["box"], wrap_into(Q["center"])
Vc = err_twist(fk(qc), Td)
pgc, gc = proj_grad(qc, Vc, jb(qc))
assert np.abs(fk(qb) - pa.fk(qb)).max() < 1e-9 and np.all(qb >= lo - 1e-12) and np.all(qb <= hi + 1e-12)
ex_box_k = ik_limits(fk, jb, Td, ready, lo, hi, "box", Lc=Lc, lam=LAM)[2]
ex_free_k = ik_limits(fk, jb, Td, ready, lo, hi, "free", Lc=Lc, lam=LAM)[2]
over_deg = [float(deg(max(lo[i] - qf[i], qf[i] - hi[i]))) for i in range(7) if i + 1 in viol(qf)]
norm_pos = {m: (wrap_into(Q[m]) - lo) / (hi - lo) for m in modes}          # 图 15.4.1 用

# 定理 15.4.2：零空间项不改变 J Δ
null_err = 0.0
r3 = np.random.default_rng(7)
for _ in range(200):
    q = r3.uniform(lo, hi)
    J = jb(q)
    Jp = np.linalg.pinv(J)
    z = -joint_center_grad(q, lo, hi)
    null_err = max(null_err, float(np.linalg.norm(J @ (np.eye(7) - Jp @ J) @ z)))
    gH = joint_center_grad(q, lo, hi)
    assert gH @ ((np.eye(7) - Jp @ J) @ z) <= 1e-15                        # 居中项不使 H 增大（一阶）
assert null_err < 1e-12

# ---------------------------------------------------------------- (3) 定理 15.4.3：随机矩阵核对
prio_err, prio_opt = 0.0, 0.0
r4 = np.random.default_rng(155)
for _ in range(300):
    n = int(r4.integers(4, 9))
    m1, m2 = int(r4.integers(1, n - 1)), int(r4.integers(1, 4))
    J1, J2 = r4.normal(size=(m1, n)), r4.normal(size=(m2, n))
    e1, e2 = r4.normal(size=m1), r4.normal(size=m2)
    J1p = np.linalg.pinv(J1)
    N1 = np.eye(n) - J1p @ J1
    A = np.linalg.pinv(J2 @ N1, rcond=1e-10)
    d = J1p @ e1 + A @ (e2 - J2 @ J1p @ e1)
    prio_err = max(prio_err, float(np.abs(J1 @ A).max()), float(np.linalg.norm(J1 @ d - e1)))
    # 与直接求“J₁Δ = e₁ 的解中使 ‖J₂Δ − e₂‖ 最小者”比较（零空间基 + 最小二乘）
    U, s, Vt = np.linalg.svd(J1)
    Z = Vt[m1:].T
    y = np.linalg.lstsq(J2 @ Z, e2 - J2 @ J1p @ e1, rcond=None)[0]
    d2 = J1p @ e1 + Z @ y
    prio_opt = max(prio_opt, abs(np.linalg.norm(J2 @ d - e2) - np.linalg.norm(J2 @ d2 - e2)))
assert prio_err < 1e-9 and prio_opt < 1e-9

# ---------------------------------------------------------------- (4) 算例 15.4.2：平面 3R 臂的两个任务
pd = np.array([0.75, 0.10])
r, beta = float(np.linalg.norm(pd)), math.atan2(pd[1], pd[0])
cmin = (r * r + PL[2] ** 2 - (PL[0] + PL[1]) ** 2) / (2 * r * PL[2])        # 式 (14.2.10)
half = math.acos(cmin)
phi_lo, phi_hi = beta - half, beta + half
phi_d = math.radians(160.0)                                                 # 工具指向左上方：超出可行范围
assert phi_d > phi_hi
th0 = np.radians([20, -40, 10])
STEP = 0.2                                                                  # 每步各关节转角不超过 0.2 rad


def tasks(th):
    x, y, phi = fk_planar(th)
    return pd - np.array([x, y]), wrap(phi_d - phi), jac_planar(th), np.ones((1, 3))


def solve_tasks(mode, w=0.1, iters=4000, lam=1e-4, mu=0.3, kp=0.1, kg=0.3, hist=None):
    """mode="weighted"：min ‖e₁ − J₁Δ‖² + w²(e₂ − J₂Δ)² + λ²‖Δ‖²（式 (15.4.8)）；mode="priority"：任务优先级 (15.4.9)，
    (J₂N₁)⁺ 用阻尼 λ₂（参数 mu）的伪逆（式 (15.4.10)），次任务误差乘增益 k_p；mode="gradient"：梯度投影 (15.4.7)，z = k_g J₂ᵀ e₂。"""
    th = th0.copy()
    for k in range(iters):
        e1, e2, J1, J2 = tasks(th)
        if hist is not None:
            hist.append((th.copy(), float(np.linalg.norm(e1)), float(fk_planar(th)[2])))
        if mode == "weighted":
            A = np.vstack([J1, w * J2])
            b = np.r_[e1, w * e2]
            parts = [np.linalg.solve(A.T @ A + lam * np.eye(3), A.T @ b)]
        else:
            J1p = np.linalg.pinv(J1)
            N1 = np.eye(3) - J1p @ J1
            if mode == "priority":
                B = J2 @ N1
                parts = [J1p @ e1, B.T @ np.linalg.solve(B @ B.T + mu * mu * np.eye(1), kp * np.array([e2]) - J2 @ J1p @ e1)]
            else:
                parts = [J1p @ e1, N1 @ (kg * J2.T @ np.array([e2]))]
        for i, p in enumerate(parts):                                       # 两部分分别限幅：缩放次任务的一步不影响主任务
            m = np.abs(p).max()
            if m > STEP:
                parts[i] = p * (STEP / m)
        d = sum(parts)
        th = th + d
        if np.linalg.norm(d) < 1e-14:
            break
    x, y, phi = fk_planar(th)
    return th, float(np.linalg.norm(pd - [x, y])), float(phi), k


hp = []
thp, epp, phip, kp = solve_tasks("priority", hist=hp)
thg, epg, phig, kg = solve_tasks("gradient")
assert epp < 1e-10 and abs(phip - phi_hi) < 1e-6 and epg < 1e-10 and abs(phig - phi_hi) < 1e-6
# 增益过大时次任务的一步在端点附近来回越过（与定理 15.2.2 同理），主任务也被拖累
_, ep_big, phi_big, k_big = solve_tasks("priority", mu=0.02, kp=1.0)
assert ep_big > 1e-3
hw = []
weighted = {}
for w in (0.01, 0.1, 1.0):
    th_w, ep_w, phi_w, _ = solve_tasks("weighted", w=w, hist=hw if w == 0.1 else None)
    weighted[w] = (th_w, ep_w, phi_w)
    assert ep_w > 1e-4 and phi_w < phi_d
thw, epw, phiw = weighted[0.1]
# 端点处腕点在 2R 外圆上（θ₂ = 0）；J₂N₁ 在那里趋于零：算法奇异
wx, wy = pd[0] - PL[2] * math.cos(phip), pd[1] - PL[2] * math.sin(phip)
reach_gap = abs(math.hypot(wx, wy) - (PL[0] + PL[1]))
assert reach_gap < 1e-6
J1 = jac_planar(thp)
n1 = np.linalg.svd(J1)[2][-1]
j2n_end = abs(float(np.ones(3) @ n1))
J1s = jac_planar(th0)
j2n_start = abs(float(np.ones(3) @ np.linalg.svd(J1s)[2][-1]))
assert j2n_end < 1e-5 < j2n_start

out(N=N, free_conv=pct(ok["free"]), free_in=pct(inl["free"]), clamp=pct(ok["clamp"]), center_conv=pct(ok["center"]), center_in=pct(inl["center"]),
    box=pct(ok["box"]), it_free=float(np.median(its["free"])), it_clamp=float(np.median(its["clamp"])), it_center=float(np.median(its["center"])),
    it_box=float(np.median(its["box"])), clamp_r=pct(restart["clamp"]), box_r=pct(restart["box"]),
    p1_clamp=100 * p_rand["clamp"], p1_box=100 * p_rand["box"], pred6_clamp=pred6["clamp"], pred6_box=pred6["box"],
    fail_pg_clamp=min(fail_pg["clamp"]), n_fail_box=len(fail_pg["box"]), n_kkt_box=n_kkt_box, n_cyc_box=len(fail_pg["box"]) - n_kkt_box, n_hard_box=n_hard["box"], n_hard_clamp=n_hard["clamp"], n_fail_clamp=len(fail_pg["clamp"]), desc_worst=desc_worst, null_err=null_err, prio_err=prio_err, kc=KC,
    lo_deg=vec(deg(lo), 0), hi_deg=vec(deg(hi), 0), ready_deg=vec(deg(ready), 0),
    qt=vec(deg(qt), 1), qf=vec(deg(qf), 1), qc=vec(deg(qc), 1), qb=vec(deg(qb), 1), qn=vec(deg(qn), 1),
    viol_f=tr("、", ", ").join(map(str, viol(qf))), over_f=tr("、", ", ").join(f"{x:.0f}°" for x in over_deg),
    viol_n=tr("、", ", ").join(map(str, viol(qn))) or tr("无", "none"), center_ok=bool(C["center"]),
    clamp_mm=mm(qc), clamp_deg=angle_deg(qc), at_lim_c=tr("、", ", ").join(map(str, at_limit(qc))),
    at_lim_b=tr("、", ", ").join(map(str, at_limit(qb))) or tr("无", "none"), pg_c=float(np.linalg.norm(pgc) / np.linalg.norm(gc)),
    k_box_ex=ex_box_k, k_free_ex=ex_free_k, box_mm=mm(qb),
    phi_lo=math.degrees(phi_lo), phi_hi=math.degrees(phi_hi), phi_d=math.degrees(phi_d), r=r, beta=math.degrees(beta),
    epw_mm=epw * 1000, phiw=math.degrees(phiw), epw1_mm=weighted[0.01][1] * 1000, phiw1=math.degrees(weighted[0.01][2]),
    epw3_mm=weighted[1.0][1] * 1000, phiw3=math.degrees(weighted[1.0][2]),
    epp=epp, phip=math.degrees(phip), thp=vec(deg(thp), 2), thw=vec(deg(thw), 2), kp=kp, kg=kg,
    th0=vec(deg(th0), 0), reach_gap=reach_gap, j2n_end=j2n_end, j2n_start=j2n_start, ep_big_mm=ep_big * 1000, phi_big=math.degrees(phi_big), runtime=time.time() - t_start)
