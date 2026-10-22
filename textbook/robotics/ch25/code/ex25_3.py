"""25.3 节的计算：闭式动力学方程。

(1) 书中 UR5e 在算例 25.1.1 的时刻：把各连杆的量排成长矢量，𝒲 是严格下三角块矩阵，𝒲ⁿ = 0，
    ℒ = (I − 𝒲)⁻¹ = I + 𝒲 + … + 𝒲ⁿ⁻¹，ℒ 的 (i, j) 块是 [Ad_{T_ij}]；ℒ𝒜 的第 i 个块行是连杆 i 的物体雅可比（与第 24 章的 J_i 比较）。
(2) M(θ) 的四种算法：闭式 𝒜ᵀℒᵀ𝒢ℒ𝒜（式 (25.3.6)）；n 次递推（θ̇ = 0、无重力、θ̈ = e_j）；第 24 章的 ΣJᵀ𝒢J；MuJoCo 的 mj_fullM。
    c、g 的闭式（式 (25.3.7)、(25.3.8)）与递推比较。
(3) 算例 25.3.1：先用递推算出上下料动作所需的力矩 τ(t)，再把它当作输入，用正动力学 θ̈ = M⁻¹(τ − c − g) 积分（RK4，Δt = 1 ms），
    看能不能回到原来的轨迹；同样的力矩加到 MuJoCo 模型上（关掉执行器，积分器 RK4），两者比较。
(4) 习题答案。
"""
import numpy as np

from _ch25 import (adjoint, body_jacobians, cell_move, inv, mass_matrix, mjcf_text, parse_links, payload_parts, payload_xml,
                   mj_load, quintic, rk4_step, ur_chain)
from bookout import out

thA, thB, T_move = cell_move()
ch0 = ur_chain()
n = ch0.n
t1 = 0.40
q, qd, qdd = quintic(thA, thB, T_move, t1)
Z = np.zeros(n)

# ---------------------------------------------------------------- (1) 𝒲、ℒ 与雅可比
A, G, W, L = ch0.stacked(q, qd)
Wp = np.linalg.matrix_power(W, n)
err_nil = float(np.abs(Wp).max())
S = sum(np.linalg.matrix_power(W, k) for k in range(n))
err_series = float(np.abs(S - L).max())
# ℒ 的 (i, j) 块 = [Ad_{T_ij}]，T_ij = T_{i,i−1} … T_{j+1,j}
err_blocks = 0.0
for i in range(n):
    for j in range(i + 1):
        Tij = np.eye(4)
        for k in range(i, j, -1):
            Tij = Tij @ ch0.T_rel(k, q[k])
        err_blocks = max(err_blocks, float(np.abs(L[6 * i:6 * i + 6, 6 * j:6 * j + 6] - adjoint(Tij)).max()))
links = parse_links(mjcf_text())
_, J24 = body_jacobians(links, q)
J24 = [J for Lk, J in zip(links, J24) if Lk.axis is not None]
err_jac = max(float(np.abs(Ja - Jb).max()) for Ja, Jb in zip(ch0.jacobians(q), J24))
assert err_nil == 0 and err_series < 1e-12 and err_blocks < 1e-12 and err_jac < 1e-12
nz_W = int(np.count_nonzero(np.abs(W) > 1e-14))
nz_L = int(np.count_nonzero(np.abs(L) > 1e-14))

# ---------------------------------------------------------------- (2) M、c、g 的几种算法
M_cf, c_cf, g_cf = ch0.closed_form(q, qd)
M_rn = np.column_stack([ch0.rnea(q, Z, np.eye(n)[j], Vd0=np.zeros(6)) for j in range(n)])
M_24 = mass_matrix(links, q) + np.diag(ch0.arm)
mj, m, d = mj_load(mjcf_text(option='<option><flag contact="disable"/></option>'))
d.qpos[:] = q
mj.mj_forward(m, d)
M_mj = np.zeros((n, n))
mj.mj_fullM(m, d, M_mj)
err_M = max(float(np.abs(M_cf - X).max()) for X in (M_rn, M_24, M_mj))
c_rn = ch0.rnea(q, qd, Z, Vd0=np.zeros(6))
g_rn = ch0.rnea(q, Z, Z)
err_cg = max(float(np.abs(c_cf - c_rn).max()), float(np.abs(g_cf - g_rn).max()))
assert err_M < 1e-12 and err_cg < 1e-12

# ---------------------------------------------------------------- (3) 算例 25.3.1：逆动力学 → 正动力学
pl = payload_parts()
ch = ur_chain(payload=pl)
DT = 1e-3
N = int(round(T_move / DT))
dt = T_move / N


def tau_of(t):
    return ch.rnea(*quintic(thA, thB, T_move, t))


def fd(th, thd, tau):
    M, c, g = ch.closed_form(th, thd)
    return np.linalg.solve(M, tau - c - g)


x = np.r_[thA, Z]
t = 0.0
err_path = 0.0
for k in range(N):
    # RK4 的四个点用各自时刻的力矩（t、t + Δt/2、t + Δt）
    tau_a, tau_m, tau_b = tau_of(t), tau_of(t + dt / 2), tau_of(t + dt)
    f = lambda xx, tau: np.r_[xx[n:], fd(xx[:n], xx[n:], tau)]   # noqa: E731
    k1 = f(x, tau_a)
    k2 = f(x + dt / 2 * k1, tau_m)
    k3 = f(x + dt / 2 * k2, tau_m)
    k4 = f(x + dt * k3, tau_b)
    x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    t += dt
    err_path = max(err_path, float(np.abs(x[:n] - quintic(thA, thB, T_move, t)[0]).max()))
err_end = float(np.abs(x[:n] - thB).max())
v_end = float(np.abs(x[n:]).max())
# MuJoCo：关掉执行器，把力矩作为 qfrc_applied，积分器 RK4；力矩在每步开始时给（零阶保持）
xml = mjcf_text(tool=payload_xml(*pl),
                option=f'<option timestep="{dt!r}" integrator="RK4"><flag contact="disable" actuation="disable"/></option>')
mjp, mp, dp = mj_load(xml)
mp.jnt_limited[:] = 0
dp.qpos[:] = thA
dp.qvel[:] = 0
for k in range(N):
    dp.qfrc_applied[:] = tau_of(k * dt + dt / 2)
    mjp.mj_step(mp, dp)
err_mj_end = float(np.abs(dp.qpos - thB).max())

# ---------------------------------------------------------------- (4) 习题答案
# 习题 25.3.3：M 的第 j 列用一次递推，c + g 再用一次：共 n + 1 次
n_calls = n + 1

out(err_nil=err_nil, err_series=err_series, err_blocks=err_blocks, err_jac=err_jac, nz_W=nz_W, nz_L=nz_L, size=6 * n,
    err_M=err_M, err_cg=err_cg, M11=M_cf[0, 0], M66=M_cf[5, 5],
    dt_ms=dt * 1000, N_steps=N, err_path=np.degrees(err_path), err_end=np.degrees(err_end), v_end=v_end,
    err_mj_end=np.degrees(err_mj_end), n_calls=n_calls)
