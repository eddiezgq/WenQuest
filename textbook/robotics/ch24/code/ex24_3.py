"""24.3 节的计算：M(θ)、C(θ, θ̇)、g(θ) 的结构。

(1) 方程的规模：平面 n 连杆臂（一般参数 a_i、m_i、r_i、I_i）的关节力矩表达式展开后的项数，n = 2、3、4。
    写法：先由 M = Σ(m_i J_viᵀJ_vi + I_i J_ωiᵀJ_ωi) 求出质量矩阵并逐个元素化简，再由克里斯托费尔符号 (24.3.4) 写出 c，
    最后整体展开（不展开 cos(φ₁ + φ₂) 这类和角）。
(2) 书中网页版 UR5e（六关节）：M(θ) = Σ J_iᵀ 𝒢_i J_i（式 (24.3.2)）与 MuJoCo 的质量矩阵减去转子惯量逐项比较；
    ∂M/∂θ₁ = 0（定理 24.3.2 (2)）；由 M 的偏导数（中心差分）求克里斯托费尔符号和 C(θ, θ̇)，c = Cθ̇ 与 MuJoCo 的
    qfrc_bias(θ, θ̇) − qfrc_bias(θ, 0) 比较；g = ∂U/∂θ 与 qfrc_bias(θ, 0) 比较；Ṁ − 2C 反对称（定理 24.3.3）。
(3) 算例 24.3.1：书中常用的“初始姿态”θ = (−90°, −90°, 90°, −90°, −90°, 0) 的 M（不含转子惯量），特征值；
    在 10⁴ 个随机姿态下（关节 2～6 在 ±180° 内均匀分布）M 各对角元素、特征值的范围；装夹爪 + 毛坯后的变化。
(4) 算例 24.3.2：两连杆臂的另一种 C′（同样满足 c = C′φ̇），Ṁ − 2C′ 不反对称；但 φ̇ᵀ(Ṁ − 2C′)φ̇ = 0。
(5) 定理 24.3.4（线性参数化）对两连杆臂的验证：τ = Y(φ, φ̇, φ̈) π，π 为 7 个参数的组合，随机状态下与 Planar2 一致。
(6) 算例 24.3.3：电机转子的等效惯量（示意值：转子 1.0 × 10⁻⁵ kg·m²，减速比 100）；与 Menagerie 模型的 armature = 0.1 kg·m²
    同一量级。负载惯量比 M_ii(θ)/(转子等效惯量) 的范围。
(7) 习题答案。
"""
import math

import numpy as np
import sympy as sp

from _ch24 import (G0, Planar2, christoffel, dM, gravity, mass_matrix, mj_load, mjcf_text, parse_links, payload_parts, payload_xml,
                   planar_params, potential)
from bookout import out, tex

rng = np.random.default_rng(243)

# ---------------------------------------------------------------- (1) 方程的规模
def n_terms(n):
    q = sp.symbols(f"q1:{n + 1}")
    qd = sp.symbols(f"w1:{n + 1}")
    qdd = sp.symbols(f"u1:{n + 1}")
    a, m, r, I = (sp.symbols(f"{s}1:{n + 1}") for s in ("a", "m", "r", "I"))
    g = sp.symbols("g")
    M = sp.zeros(n, n)
    U = 0
    base, ang = sp.Matrix([0, 0]), 0
    for i in range(n):
        ang = ang + q[i]
        c = base + r[i] * sp.Matrix([sp.cos(ang), sp.sin(ang)])
        Jv = c.jacobian(q)
        Jw = sp.Matrix([[1 if k <= i else 0 for k in range(n)]])
        M += m[i] * Jv.T * Jv + I[i] * Jw.T * Jw
        U += m[i] * g * c[1]
        base = base + a[i] * sp.Matrix([sp.cos(ang), sp.sin(ang)])
    M = M.applyfunc(lambda e: sp.trigsimp(sp.expand(e)))
    counts = []
    for i in range(n):
        e = sum(M[i, j] * qdd[j] for j in range(n)) + sp.diff(U, q[i])
        for j in range(n):
            for k in range(n):
                e += sp.Rational(1, 2) * (sp.diff(M[i, j], q[k]) + sp.diff(M[i, k], q[j]) - sp.diff(M[j, k], q[i])) * qd[j] * qd[k]
        counts.append(len(sp.Add.make_args(sp.expand(e))))
    return counts


terms = {n: n_terms(n) for n in (2, 3, 4)}
tot_terms = {n: sum(v) for n, v in terms.items()}

# ---------------------------------------------------------------- (2) UR5e：质量矩阵、克里斯托费尔符号、重力项
import mujoco                                                           # noqa: E402

links = parse_links(mjcf_text())
mj, m, d = mj_load(mjcf_text(option='<option><flag contact="disable"/></option>'))
ARM = np.array(m.dof_armature)
assert np.allclose(ARM, 0.1)


def mj_M(theta, thd=None):
    d.qpos[:] = theta
    d.qvel[:] = 0 if thd is None else thd
    mujoco.mj_forward(m, d)
    M = np.zeros((6, 6))
    mujoco.mj_fullM(m, d, M)
    return M, d.qfrc_bias.copy()


Mf = lambda th: mass_matrix(links, th)
Uf = lambda th: potential(links, th)
err_M = err_c = err_g = err_skew = dM1 = err_E = 0.0
for _ in range(20):
    th = rng.uniform(-math.pi, math.pi, 6)
    thd = rng.normal(size=6)
    M_mj, b0 = mj_M(th)
    _, b1 = mj_M(th, thd)
    M_ours = Mf(th)
    err_M = max(err_M, float(np.abs(M_ours - (M_mj - np.diag(ARM))).max()))
    D = dM(Mf, th)
    C = christoffel(D) @ thd
    err_c = max(err_c, float(np.abs(C @ thd - (b1 - b0)).max()))
    err_g = max(err_g, float(np.abs(gravity(Uf, th) - b0).max()))
    Md = np.tensordot(thd, D, axes=1)                                   # Ṁ = Σ_k ∂M/∂θ_k θ̇_k
    N = Md - 2 * C
    err_skew = max(err_skew, float(np.abs(N + N.T).max()))
    dM1 = max(dM1, float(np.abs(D[0]).max()))
    # MuJoCo 的动能（含转子）= ½θ̇ᵀMθ̇
    mujoco.mj_energyPos(m, d)
    mujoco.mj_energyVel(m, d)
    err_E = max(err_E, abs(d.energy[1] - 0.5 * thd @ M_mj @ thd))
assert err_M < 1e-12 and err_c < 1e-7 and err_g < 1e-7 and err_skew < 1e-7 and dM1 < 1e-8 and err_E < 1e-12

# ---------------------------------------------------------------- (3) 算例 24.3.1：初始姿态与随机姿态
HOME = np.radians([-90, -90, 90, -90, -90, 0])
M_home = Mf(HOME)
ev_home = np.linalg.eigvalsh(M_home)
ZERO = np.zeros(6)
M_zero = Mf(ZERO)
N_RAND = 10000
diag_min, diag_max = np.full(6, np.inf), np.zeros(6)
ev_min, ev_max, cond_max, cond_arm_max = np.inf, 0.0, 0.0, 0.0
diagL_max = np.zeros(6)
mjL, mL_, dL = mj_load(mjcf_text(tool=payload_xml(*payload_parts()), option='<option><flag contact="disable"/></option>'))
for _ in range(N_RAND):
    th = np.r_[0.0, rng.uniform(-math.pi, math.pi, 5)]
    M_mj, _ = mj_M(th)
    Mx = M_mj - np.diag(ARM)
    dg = np.diag(Mx)
    diag_min, diag_max = np.minimum(diag_min, dg), np.maximum(diag_max, dg)
    ev = np.linalg.eigvalsh(Mx)
    ev_min, ev_max = min(ev_min, ev[0]), max(ev_max, ev[-1])
    cond_max = max(cond_max, ev[-1] / ev[0])
    eva = np.linalg.eigvalsh(M_mj)
    cond_arm_max = max(cond_arm_max, eva[-1] / eva[0])
    dL.qpos[:] = th
    mujoco.mj_forward(mL_, dL)
    ML = np.zeros((6, 6))
    mujoco.mj_fullM(mL_, dL, ML)
    diagL_max = np.maximum(diagL_max, np.diag(ML) - ARM)
assert ev_min > 0
# M₁₁ 的上下界可以直接说明：伸直时最大、收拢时最小
M11_zero = float(M_zero[0, 0])
assert diag_max[0] >= M11_zero and abs(diag_min[5] - diag_max[5]) < 1e-12      # M₆₆ 是腕 3 绕自身轴的惯量，与姿态无关

# ---------------------------------------------------------------- (4) 算例 24.3.2：C 不唯一
P = planar_params(links, payload=payload_parts())
p, pd = np.array([0.7, -1.2]), np.array([1.5, -0.8])
h = P.hh(p[1])
Cc = P.C(p, pd)
Calt = np.array([[0.0, -h * (2 * pd[0] + pd[1])], [h * pd[0], 0.0]])   # 另一种写法
assert np.allclose(Calt @ pd, P.c(p, pd)) and np.allclose(Cc @ pd, P.c(p, pd))
Md2 = np.array([[-2 * h * pd[1], -h * pd[1]], [-h * pd[1], 0.0]])        # Ṁ（只有 φ₂ 出现在 M 中）
N_c, N_alt = Md2 - 2 * Cc, Md2 - 2 * Calt
assert np.allclose(N_c + N_c.T, 0) and not np.allclose(N_alt + N_alt.T, 0)
assert abs(pd @ N_alt @ pd) < 1e-12
N_alt_sym = N_alt + N_alt.T

# ---------------------------------------------------------------- (5) 两连杆臂的线性参数化
def Y_planar(a1, p, pd, pdd):
    """τ = Y π，π = (J₁ + J₂ + m₂a₁² + 转子₁, J₂, m₁r₁ + m₂a₁, m₁s₁, m₂r₂, m₂s₂, 转子₂)：7 个参数组合。
    a₁ 是已知的几何尺寸，不算惯性参数：β = a₁(m₂r₂ cos φ₂ − m₂s₂ sin φ₂)，h = a₁(m₂r₂ sin φ₂ + m₂s₂ cos φ₂)。"""
    c2, s2_ = math.cos(p[1]), math.sin(p[1])
    c1, s1_ = math.cos(p[0]), math.sin(p[0])
    c12, s12 = math.cos(p[0] + p[1]), math.sin(p[0] + p[1])
    g = G0
    v1 = 2 * pd[0] * pd[1] + pd[1] ** 2
    y1 = [pdd[0], pdd[1], g * c1, -g * s1_,
          a1 * (c2 * (2 * pdd[0] + pdd[1]) - s2_ * v1) + g * c12,
          a1 * (-s2_ * (2 * pdd[0] + pdd[1]) - c2 * v1) - g * s12,
          0.0]
    y2 = [0.0, pdd[0] + pdd[1], 0.0, 0.0,
          a1 * (c2 * pdd[0] + s2_ * pd[0] ** 2) + g * c12,
          a1 * (-s2_ * pdd[0] + c2 * pd[0] ** 2) - g * s12,
          pdd[1]]
    return np.array([y1, y2])


def pi_planar(P):
    return np.array([P.J1 + P.J2 + P.m2 * P.a1 ** 2 + P.arm[0], P.J2, P.m1 * P.r1 + P.m2 * P.a1, P.m1 * P.s1,
                     P.m2 * P.r2, P.m2 * P.s2, P.arm[1]])


err_Y = 0.0
for _ in range(50):
    par = rng.uniform(0.1, 2.0, 9)
    Q = Planar2(par[0], par[1], par[2], rng.uniform(-0.2, 0.2), par[3], par[4], par[5], rng.uniform(-0.2, 0.2), par[6],
                arm=(par[7], par[8]))
    x = rng.normal(size=6)
    err_Y = max(err_Y, float(np.abs(Y_planar(Q.a1, x[:2], x[2:4], x[4:]) @ pi_planar(Q) - Q.tau(x[:2], x[2:4], x[4:])).max()))
assert err_Y < 1e-12
# 这 7 列线性无关：随机取 50 个状态叠起来的 100×7 矩阵满秩
Ys = np.vstack([Y_planar(0.425, *(rng.normal(size=(3, 2)))) for _ in range(50)])
assert np.linalg.matrix_rank(Ys) == 7
n_pi = len(pi_planar(P))

# ---------------------------------------------------------------- (6) 算例 24.3.3：转子等效惯量
J_rotor, N_gear = 1.0e-5, 100
J_refl = N_gear ** 2 * J_rotor
assert abs(J_refl - 0.1) < 1e-12
ratio_min = diag_min / ARM
ratio_max = diag_max / ARM
ratioL_max = diagL_max / ARM

# ---------------------------------------------------------------- (7) 习题答案
# 习题 24.3.4：初始姿态下关节 1 推动的惯量（含转子）与零位之比
r_home_zero = (M_home[0, 0] + ARM[0]) / (M_zero[0, 0] + ARM[0])

out(terms2=tot_terms[2], terms3=tot_terms[3], terms4=tot_terms[4], terms4_1=terms[4][0],
    err_M=err_M, err_c=err_c, err_g=err_g, err_skew=err_skew, dM1=dM1, err_E=err_E,
    M_home=tex(M_home, 3), ev_home_min=ev_home[0], ev_home_max=ev_home[-1], M11_home=M_home[0, 0], M11_zero=M11_zero,
    M22_home=M_home[1, 1], M66_home=M_home[5, 5],
    N_rand=N_RAND, d_min1=diag_min[0], d_max1=diag_max[0], d_min2=diag_min[1], d_max2=diag_max[1], d_min3=diag_min[2],
    d_max3=diag_max[2], d_min6=diag_min[5], d_max6=diag_max[5], ev_min=ev_min, ev_max=ev_max, cond_max=cond_max, cond_arm_max=cond_arm_max,
    dL_max1=diagL_max[0], dL_max2=diagL_max[1],
    h_ex=h, N_alt_12=N_alt_sym[0, 1],
    err_Y=err_Y, n_pi=n_pi,
    arm_mj=float(ARM[0]), d_ratio1=float(diag_max[0] / diag_min[0]),
    J_rotor=J_rotor, N_gear=N_gear, J_refl=J_refl, ratio_min1=ratio_min[0], ratio_max1=ratio_max[0],
    ratio_min6=ratio_min[5], ratio_max6=ratio_max[5], ratioL_max1=ratioL_max[0],
    r_home_zero=r_home_zero)
