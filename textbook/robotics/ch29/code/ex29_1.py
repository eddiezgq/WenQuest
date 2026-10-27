"""29.1 节的计算：物理引擎原理。

(1) 算例 29.1.1：铰接体算法（ABA，算法 29.1.1）求 UR5e 的关节角加速度，与闭式 M θ̈ = τ − c − g（第 25 章）、MuJoCo 的 qacc 核对
    （随机姿态、速度和力矩，带与不带负载）。
(2) 算例 29.1.2：数一数运算次数：ABA 与“牛顿-欧拉求 c + g、复合刚体算法求 M、楚列斯基分解解方程”，n = 6 的 UR5e 与 n 个关节的随机串联臂
    （按稠密的 6×6 矩阵运算计数）；MuJoCo 中 UR5e、Go2、G1 的质量矩阵有多少个非零元（树状结构使 M 稀疏）。
(3) 算例 29.1.3：叠放的料箱（只考虑竖直方向的刚性接触）：时间步进得到的 LCP，投影高斯-赛德尔法（PGS）的收敛速度与料箱数 N、
    顶上料箱的质量的关系，谱半径 cos²(π/2N)；每步只迭代 k 次时，冷启动与热启动 1 s 后的下沉量。
(4) 算例 29.1.4：MuJoCo 中叠放 10 个料箱，求解器取 Newton（默认）与 PGS（迭代 5、10、20、100 次），2 s 后顶上料箱的下沉量、
    最大倾角、每步的迭代次数；接触点数与约束行数。
"""
import math

import mujoco
import numpy as np

from _ch29 import (Count, aba, aba_counted, crba_counted, mjcf_text, payload_parts, payload_xml, pgs, random_chain, run_stack,
                   stack_delassus, ur_chain, ur_model, MJCF_DIR)
from bookout import out

# ---------------------------------------------------------------- (1) ABA 与 MuJoCo
rng = np.random.default_rng(29)
flags = 'contact="disable" actuation="disable"'
err_cf = err_mj = 0.0
for payload in (None, payload_parts()):
    ch = ur_chain(payload=payload)
    tool = payload_xml(*payload) if payload is not None else ""
    _, m, d = ur_model(flags=flags, tool=tool)
    for _ in range(50):
        th = rng.uniform(-math.pi, math.pi, 6)
        thd = rng.uniform(-2, 2, 6)
        tau = rng.uniform(-60, 60, 6)
        a1 = aba(ch, th, thd, tau)
        M, c, g = ch.closed_form(th, thd)
        a2 = np.linalg.solve(M, tau - c - g)
        d.qpos[:], d.qvel[:], d.qfrc_applied[:] = th, thd, tau
        mujoco.mj_forward(m, d)
        err_cf = max(err_cf, float(np.abs(a1 - a2).max()))
        err_mj = max(err_mj, float(np.abs(a1 - d.qacc).max()))
assert err_cf < 1e-10 and err_mj < 1e-9
out(aba_err_cf=err_cf, aba_err_mj=err_mj)

# ---------------------------------------------------------------- (2) 运算次数
def counts(ch, th, thd, tau):
    Count.reset()
    x1 = aba_counted(ch, th, thd, tau)
    a = (Count.mul, Count.add)
    Count.reset()
    x2, parts = crba_counted(ch, th, thd, tau)
    b = (Count.mul, Count.add)
    rel = float(np.abs(x1 - x2).max() / np.abs(x1).max())
    return a, b, parts, rel


ch = ur_chain()
th = rng.uniform(-math.pi, math.pi, 6)
thd = rng.uniform(-2, 2, 6)
tau = rng.uniform(-60, 60, 6)
a6, b6, p6, rel6 = counts(ch, th, thd, tau)
assert rel6 < 1e-12
out(aba_mul6=a6[0], aba_add6=a6[1], crba_mul6=b6[0], crba_add6=b6[1], rnea_mul6=p6[0], crb_mul6=p6[1], chol_mul6=p6[2])

table = []
for n in (1, 2, 3, 6, 12, 20, 30, 50):
    chn = random_chain(n, rng)
    a, b, parts, rel = counts(chn, rng.uniform(-3, 3, n), rng.uniform(-1, 1, n), rng.uniform(-5, 5, n))
    table.append((n, a[0], b[0], parts))
    if n <= 20:
        assert rel < 1e-8, (n, rel)
N_ = np.array([t[0] for t in table])
A_ = np.array([t[1] for t in table])
B_ = np.array([t[2] for t in table])
# ABA 的乘法次数正好是 n 的一次式；另一种是三次式（楚列斯基分解 ~n³/6）
ca = np.polyfit(N_, A_, 1)
cb = np.polyfit(N_, B_, 3)
assert np.allclose(np.polyval(ca, N_), A_) and np.allclose(np.polyval(cb, N_), B_)
out(aba_k=round(ca[0]), aba_b=round(ca[1]), crba_c3=cb[0], crba_c2=cb[1], crba_c1=cb[2], crba_c0=cb[3],
    ratio30=B_[N_ == 30][0] / A_[N_ == 30][0], ratio6=b6[0] / a6[0], ratio50=B_[N_ == 50][0] / A_[N_ == 50][0],
    chol_share30=table[6][3][2] / B_[N_ == 30][0] * 100, crb_share30=table[6][3][1] / B_[N_ == 30][0] * 100,
    ops_n=N_.tolist(), ops_aba=A_.tolist(), ops_crba=B_.tolist())


def nM(xml):
    m = mujoco.MjModel.from_xml_string(xml)
    return m.nv, m.nM


def model_text(name):
    return (MJCF_DIR / f"{name}.xml").read_text(encoding="utf-8")


nv_ur, nM_ur = nM(mjcf_text())
nv_go, nM_go = nM(model_text("go2"))
nv_g1, nM_g1 = nM(model_text("g1"))
assert nM_ur == nv_ur * (nv_ur + 1) // 2
out(nv_ur=nv_ur, nM_ur=nM_ur, nv_go=nv_go, nM_go=nM_go, dense_go=nv_go * (nv_go + 1) // 2,
    nv_g1=nv_g1, nM_g1=nM_g1, dense_g1=nv_g1 * (nv_g1 + 1) // 2, fill_g1=nM_g1 / (nv_g1 * (nv_g1 + 1) / 2) * 100)

# ---------------------------------------------------------------- (3) 叠放的料箱：PGS
H, G0 = 0.002, 9.81
M_BOX = 8.0


def stack_lcp(N, top=M_BOX):
    ms = np.full(N, M_BOX)
    ms[-1] = top
    J, A = stack_delassus(ms)
    b = J @ np.full(N, -H * G0)                          # v = 0 时的“自由”速度 −h𝔤 对应的间隙变化率
    return ms, J, A, b


def iters_to(N, top=M_BOX, tol=1e-3):
    ms, J, A, b = stack_lcp(N, top)
    lam_ex = np.linalg.solve(A, -b)                     # 静止时全部接触都受力，LCP 的解满足 Aλ + b = 0
    assert np.allclose(lam_ex, H * G0 * np.cumsum(ms[::-1])[::-1])
    _, hist = pgs(A, b, iters=20000)
    k = next(i + 1 for i, x in enumerate(hist) if np.abs(x - lam_ex).max() < tol * lam_ex.max())
    Dl = np.tril(A)
    rho = float(max(abs(np.linalg.eigvals(np.eye(N) - np.linalg.solve(Dl, A)))))
    return k, rho


pgs_rows = []
for N in (2, 5, 10, 20):
    k, rho = iters_to(N)
    kh, rhoh = iters_to(N, top=10 * M_BOX)
    assert abs(rho - math.cos(math.pi / (2 * N)) ** 2) < 1e-10
    pgs_rows.append((N, k, rho, kh, rhoh, math.log(1e3) / -math.log(rho)))
out(pgs_N=[r[0] for r in pgs_rows], pgs_k=[r[1] for r in pgs_rows], pgs_rho=[r[2] for r in pgs_rows],
    pgs_kh=[r[3] for r in pgs_rows], pgs_est=[r[5] for r in pgs_rows],
    k10=pgs_rows[2][1], k20=pgs_rows[3][1], k10h=pgs_rows[2][3], rho10=pgs_rows[2][2], k5=pgs_rows[1][1], k2=pgs_rows[0][1],
    k20h=pgs_rows[3][3], k5h=pgs_rows[1][3])


def stepping(N, k, warm, T=1.0):
    ms, J, A, _ = stack_lcp(N)
    v = np.zeros(N)
    x = np.zeros(N)
    lam = np.zeros(N)
    for _ in range(int(round(T / H))):
        b = J @ (v - H * G0)
        lam, _ = pgs(A, b, lam0=lam if warm else None, iters=k)
        v = v - H * G0 + J.T @ lam / ms
        x = x + H * v
    return -x[-1]


sink = {(N, k, w): stepping(N, k, w) for N in (5, 10) for k in (5, 10, 20) for w in (False, True)}
out(sink_cold_10_10_mm=sink[(10, 10, False)] * 1000, sink_warm_10_10_mm=sink[(10, 10, True)] * 1000,
    sink_cold_10_5_mm=sink[(10, 5, False)] * 1000, sink_warm_10_5_mm=sink[(10, 5, True)] * 1000,
    sink_cold_10_20_mm=sink[(10, 20, False)] * 1000, sink_cold_5_10_mm=sink[(5, 10, False)] * 1000,
    sink_warm_5_10_mm=sink[(5, 10, True)] * 1000)

# ---------------------------------------------------------------- (4) MuJoCo 中叠放 10 个料箱
NS = 10
mj_rows = {}
for solver, it in (("Newton", 100), ("CG", 100), ("PGS", 5), ("PGS", 10), ("PGS", 20), ("PGS", 100)):
    mj_rows[(solver, it)] = run_stack(NS, solver, it)
m = mujoco.MjModel.from_xml_string(__import__("_ch29").stack_xml(NS))
d = mujoco.MjData(m)
mujoco.mj_forward(m, d)
for _ in range(10):
    mujoco.mj_step(m, d)
out(ncon10=int(d.ncon), nefc10=int(d.nefc), nv10=int(m.nv),
    nt_drop_mm=mj_rows[("Newton", 100)][0] * 1000, nt_it=mj_rows[("Newton", 100)][2], nt_itmax=mj_rows[("Newton", 100)][3],
    cg_it=mj_rows[("CG", 100)][2],
    p5_drop_mm=mj_rows[("PGS", 5)][0] * 1000, p5_tilt=math.degrees(mj_rows[("PGS", 5)][1]),
    p10_drop_mm=mj_rows[("PGS", 10)][0] * 1000, p10_tilt=math.degrees(mj_rows[("PGS", 10)][1]),
    p20_drop_mm=mj_rows[("PGS", 20)][0] * 1000, p20_tilt=math.degrees(mj_rows[("PGS", 20)][1]),
    p100_drop_mm=mj_rows[("PGS", 100)][0] * 1000, p100_it=mj_rows[("PGS", 100)][2], p100_itmax=mj_rows[("PGS", 100)][3],
    nt_tilt=math.degrees(mj_rows[("Newton", 100)][1]))
assert mj_rows[("PGS", 5)][1] > 10 * mj_rows[("Newton", 100)][1]

# ---------------------------------------------------------------- 习题
# 29.1.2：两个料箱、顶上的重 10 倍，PGS 的谱半径（答案用公式 ρ = m_t/(m_t + m_b)·…，这里直接算）
k2h, rho2h = iters_to(2, top=10 * M_BOX)
out(ex_rho2h=rho2h, ex_k2h=k2h)
