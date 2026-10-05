"""15.2 节：雅可比转置法。

(1) 虚拟弹簧：平面 2R 臂（第 7、14 章的同一台）末端被拉向目标，关节力矩 τ = Jᵀ F；虚功 τᵀδθ = Fᵀ δp。
(2) 连续时间的雅可比转置法 θ̇ = K Jᵀ e：误差 ‖e‖ 单调减小（定理 15.2.1）。
(3) 算例 15.2.1：目标 (0.45, 0.35) m，初值 (0, 1) rad（同算例 7.3.4）。固定步长 α 的收敛条件 α < 2/σ₁²（定理 15.2.2），
    实测收敛率与 max|1 − ασᵢ²| 比较；每步取最优 α（式 (15.2.8)）；与牛顿法比较。
(4) 算例 15.2.2：UR5e 到达算例 15.1.2 的位姿，雅可比转置法（每步最优 α）在不同权重 W = diag(I, I/L_c²) 下的迭代次数，
    与加权雅可比的条件数比较；牛顿-拉夫森法只用 4 次。
(5) 奇异与够不着：雅可比转置法一步的长度有界；目标够不着时收敛到伸直指向目标的形态；手臂伸直、目标在正后方时卡住。
"""
import math

import numpy as np

from _nik import (L2R, PD2R, TH_CUR, TH_STAR, fk_planar, ik2r, jac_planar, jt, jt_planar, newton_planar, nr, ur_fk, ur_jb,
                  ur_target)
from bookout import T as tr, out, vec

deg = np.degrees

# ---------------------------------------------------------------- (1) 虚拟弹簧
th0 = np.array([0.0, 1.0])
p0 = fk_planar(th0, L2R)[:2]
e0 = PD2R - p0
k_s = 100.0                                          # 弹簧刚度 100 N/m
F = k_s * e0
J0 = jac_planar(th0, L2R)
tau = J0.T @ F
dth = np.array([1e-6, -2e-6])
vw = abs(tau @ dth - F @ (fk_planar(th0 + dth, L2R)[:2] - p0)) / abs(tau @ dth)
assert vw < 1e-5
# 转关节 2 时的力矩：只有小臂受弹簧力的力矩
r2 = p0 - np.array([L2R[0] * math.cos(th0[0]), L2R[0] * math.sin(th0[0])])
tau2_check = float(r2[0] * F[1] - r2[1] * F[0])
assert abs(tau2_check - tau[1]) < 1e-12

# ---------------------------------------------------------------- (2) 连续时间：θ̇ = K Jᵀ e，误差单调减小
th = th0.copy()
dt, Kc = 1e-3, 20.0
mono = True
errs_c = [float(np.linalg.norm(PD2R - fk_planar(th, L2R)[:2]))]
for i in range(10000):
    e = PD2R - fk_planar(th, L2R)[:2]
    th = th + dt * Kc * jac_planar(th, L2R).T @ e
    errs_c.append(float(np.linalg.norm(PD2R - fk_planar(th, L2R)[:2])))
    mono &= errs_c[-1] <= errs_c[-2] + 1e-15
assert mono
t_half = next(i for i, x in enumerate(errs_c) if x < 1e-3) * dt
end_c = errs_c[-1]

# ---------------------------------------------------------------- (3) 算例 15.2.1
sols = ik2r(*PD2R, *L2R)
ths = np.array(sols[0])                              # 肘下的一组（θ2 > 0），从 (0, 1) rad 出发收敛到它
Js = jac_planar(ths, L2R)
sv = np.linalg.svd(Js, compute_uv=False)
a_max = 2 / sv[0] ** 2
a_best = 2 / (sv[0] ** 2 + sv[1] ** 2)
kappa = sv[0] / sv[1]
rate_best = (kappa ** 2 - 1) / (kappa ** 2 + 1)
res = {}
for a in (1.0, 3.0):
    thf, k, E, _ = jt_planar(PD2R, th0, alpha=a)
    assert k is not None and np.allclose(thf, ths, atol=1e-8)
    res[a] = (k, E[-1] / E[-2], max(abs(1 - a * s ** 2) for s in sv))
    assert abs(res[a][1] - res[a][2]) < 1e-4
thf, k_near, E_near, _ = jt_planar(PD2R, th0, alpha=0.98 * a_max)
assert k_near is not None
_, k_over, E_over, TH_over = jt_planar(PD2R, th0, alpha=1.02 * a_max, iters=5000)
assert k_over is None
over_tail = float(max(E_over[-200:]))
thf, k_buss, E_buss, TH_buss = jt_planar(PD2R, th0)
assert k_buss is not None and np.allclose(thf, ths, atol=1e-8)
_, k_newt, E_newt, _ = newton_planar(PD2R, th0)
_, k_best, _, _ = jt_planar(PD2R, th0, alpha=a_best)

# ---------------------------------------------------------------- (4) 算例 15.2.2：UR5e
Td = ur_target()
_, ok_nr, h_nr = nr(ur_fk, ur_jb, Td, TH_CUR)
ur_res = {}
for Lc in (None, 0.3, 0.1):
    W = None if Lc is None else np.diag([1, 1, 1] + [1 / Lc ** 2] * 3)
    thj, ok, h = jt(ur_fk, ur_jb, Td, TH_CUR, W=W, tol_w=1e-9, tol_v=1e-9, iters=50000)
    assert ok and np.abs(thj - TH_STAR).max() < 1e-7
    Jw = ur_jb(TH_STAR) if W is None else np.diag(np.sqrt(np.diag(W))) @ ur_jb(TH_STAR)
    s = np.linalg.svd(Jw, compute_uv=False)
    ur_res[Lc] = (len(h) - 1, s[0] / s[-1])
ur_first = float(np.linalg.norm(jt(ur_fk, ur_jb, Td, TH_CUR, iters=1)[2][1][1]))     # 第一步之后的 ‖V_b‖

# ---------------------------------------------------------------- (5) 奇异与够不着
far = np.array([0.9, 0.3])
thf_far, k_far, E_far, _ = jt_planar(far, np.array([0.2, 0.5]), tol=0.0, iters=20000)
gap = float(np.linalg.norm(far) - sum(L2R))
assert abs(E_far[-1] - gap) < 1e-9 and abs(math.sin(thf_far[1])) < 1e-6
dir_err = abs(math.atan2(math.sin(thf_far[0] - math.atan2(far[1], far[0])), math.cos(thf_far[0] - math.atan2(far[1], far[0]))))
assert dir_err < 1e-6
behind = np.array([-0.3, 0.0])
_, k_stuck, E_stuck, TH_stuck = jt_planar(behind, np.array([0.0, 0.0]), iters=50)
assert k_stuck is None and abs(E_stuck[-1] - E_stuck[0]) < 1e-15
_, k_esc, E_esc, _ = jt_planar(behind, np.array([1e-6, 0.0]), tol=1e-10, iters=200000)
assert k_esc is not None
# 一步的长度有界：‖Δθ‖ ≤ α σ₁ ‖e‖
bound_ok = True
rng = np.random.default_rng(152)
for _ in range(1000):
    t = rng.uniform(-math.pi, math.pi, 2)
    e = rng.normal(size=2)
    J = jac_planar(t, L2R)
    bound_ok &= np.linalg.norm(J.T @ e) <= np.linalg.svd(J, compute_uv=False)[0] * np.linalg.norm(e) + 1e-15
assert bound_ok

out(p0=vec(p0, 4), e0=vec(e0, 4), F=vec(F, 2), tau=vec(tau, 3), tau1=tau[0], tau2=tau[1], vw=vw,
    t_half=t_half, end_c=end_c, Kc=Kc,
    sol_deg=vec(deg(ths), 2), sv1=sv[0], sv2=sv[1], a_max=a_max, a_best=a_best, kappa=kappa, rate_best=rate_best,
    k1=res[1.0][0], r1=res[1.0][1], p1=res[1.0][2], k3=res[3.0][0], r3=res[3.0][1], p3=res[3.0][2],
    a_near=0.98 * a_max, k_near=k_near, a_over=1.02 * a_max, over_tail=over_tail,
    k_buss=k_buss, k_newt=k_newt, k_best=k_best,
    k_ur_nr=len(h_nr) - 1, k_ur0=ur_res[None][0], kap_ur0=ur_res[None][1], k_ur3=ur_res[0.3][0], kap_ur3=ur_res[0.3][1],
    k_ur1=ur_res[0.1][0], kap_ur1=ur_res[0.1][1], ur_first=ur_first,
    gap=gap, far_deg=vec(deg(thf_far), 2), k_esc=k_esc)
