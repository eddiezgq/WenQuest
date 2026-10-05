"""15.3 节：阻尼最小二乘。

(1) 定理 15.3.1：(JᵀJ + λ²I)⁻¹Jᵀ = Jᵀ(JJᵀ + λ²I)⁻¹；用奇异值写出 Δθ；‖Δθ‖ ≤ ‖e‖/(2λ)；随机矩阵核对。
(2) 算例 15.3.1：UR5e 从接近手腕奇异的起点（θ5 = −0.5°）求算例 15.1.2 的逆解：牛顿-拉夫森法、雅可比转置法、
    阻尼最小二乘（固定 λ）与按增益比调整阻尼的 LM 法比较：第一步的关节转角、迭代次数、所得的解。
(3) 算例 15.3.2：UR5e 末端沿直线匀速移动、经过手腕奇异附近（θ5 最小 1°），分解运动速率控制每 2 ms 算一次关节速度：
    精确求逆、固定阻尼、可变阻尼的最大关节速度与跟踪误差（UR5e 关节速度上限 180°/s）。
"""
import math

import numpy as np

from _nik import (WristPath, TH_CUR, TH_STAR, W4, err_twist, jt, nr, ur_fk, ur_ik, ur_jb, ur_labels, ur_solution_index, ur_table,
                  ur_target, wrap)
from bookout import T as tr, out, vec

deg = np.degrees
rng = np.random.default_rng(153)

# ---------------------------------------------------------------- (1) 定理 15.3.1
id_err, bound_ok, svd_err = 0.0, True, 0.0
for _ in range(500):
    m, n = rng.integers(2, 7), rng.integers(2, 8)
    J = rng.normal(size=(m, n))
    if rng.random() < 0.5:                                # 一半取接近奇异的矩阵
        U, s, Vt = np.linalg.svd(J, full_matrices=False)
        s[-1] *= 1e-6
        J = U @ np.diag(s) @ Vt
    e = rng.normal(size=m)
    lam = 10 ** rng.uniform(-3, 0)
    d1 = np.linalg.solve(J.T @ J + lam ** 2 * np.eye(n), J.T @ e)
    d2 = J.T @ np.linalg.solve(J @ J.T + lam ** 2 * np.eye(m), e)
    U, s, Vt = np.linalg.svd(J, full_matrices=False)
    d3 = Vt.T @ (s / (s ** 2 + lam ** 2) * (U.T @ e))
    id_err = max(id_err, float(np.abs(d1 - d2).max() / (1 + np.abs(d1).max())))
    svd_err = max(svd_err, float(np.abs(d1 - d3).max() / (1 + np.abs(d1).max())))
    bound_ok &= np.linalg.norm(d2) <= np.linalg.norm(e) / (2 * lam) * (1 + 1e-12)
assert id_err < 1e-8 and svd_err < 1e-8 and bound_ok

# ---------------------------------------------------------------- (2) 算例 15.3.1：从接近奇异的起点出发
Td = ur_target()
table = ur_table()
Lc = 0.1
Wd = np.diag([1, 1, 1] + [1 / Lc] * 3)                    # 把 v_b 除以 L_c，各分量都以 rad 计


def dls_fixed(th0, lam, iters=500):
    th = np.array(th0, float)
    hist = []
    for k in range(iters + 1):
        V = err_twist(ur_fk(th), Td)
        hist.append((th.copy(), V))
        if np.linalg.norm(V[:3]) < 1e-12 and np.linalg.norm(V[3:]) < 1e-12:
            return th, True, hist
        J = Wd @ ur_jb(th)
        th = th + J.T @ np.linalg.solve(J @ J.T + lam ** 2 * np.eye(6), Wd @ V)
    return th, False, hist


def lm(th0, iters=200, tau=1e-3):
    """按增益比调整阻尼的 LM 法（8.5.4 节，式 (8.5.5)–(8.5.9)），残差取加权误差旋量。"""
    th = np.array(th0, float)
    hist = []
    F = lambda t: 0.5 * float(np.sum((Wd @ err_twist(ur_fk(t), Td)) ** 2))
    mu, nu = None, 2.0
    for k in range(iters + 1):
        V = err_twist(ur_fk(th), Td)
        hist.append((th.copy(), V))
        if np.linalg.norm(V[:3]) < 1e-12 and np.linalg.norm(V[3:]) < 1e-12:
            return th, True, hist
        J = Wd @ ur_jb(th)
        r = -(Wd @ V)                                     # 残差 r(θ) = −W V_b，∂r/∂θ ≈ W J_b
        A, g = J.T @ J, J.T @ r
        if mu is None:
            mu = tau * float(np.max(np.diag(A)))
        while True:
            d = -np.linalg.solve(A + mu * np.eye(6), g)
            pred = 0.5 * float(d @ (mu * d - g))
            rho = (F(th) - F(th + d)) / pred if pred > 0 else -1
            if rho > 0:
                mu *= max(1 / 3, 1 - (2 * rho - 1) ** 3)
                nu = 2.0
                break
            mu *= nu
            nu *= 2
        th = th + d
    return th, False, hist


th_s = TH_CUR.copy()
th_s[4] = math.radians(-0.5)                              # 手腕几乎伸直：θ5 = −0.5°
sv_s = np.linalg.svd(ur_jb(th_s), compute_uv=False)
res = {}
th, ok, h = nr(ur_fk, ur_jb, Td, th_s, iters=100)
res["nr"] = (ok, len(h) - 1, float(np.abs(deg(h[1][0] - h[0][0])).max()), ur_solution_index(th, table, 1e-8))
th, ok, h = jt(ur_fk, ur_jb, Td, th_s, W=Wd @ Wd, tol_w=1e-9, tol_v=1e-9, iters=60000)
res["jt"] = (ok, len(h) - 1, float(np.abs(deg(h[1][0] - h[0][0])).max()), ur_solution_index(th, table, 1e-6))
th, ok, h = dls_fixed(th_s, 0.05)
res["dls"] = (ok, len(h) - 1, float(np.abs(deg(h[1][0] - h[0][0])).max()), ur_solution_index(th, table, 1e-8))
th, ok, h = lm(th_s)
res["lm"] = (ok, len(h) - 1, float(np.abs(deg(h[1][0] - h[0][0])).max()), ur_solution_index(th, table, 1e-8))
assert res["dls"][0] and res["lm"][0] and res["jt"][0]
assert res["nr"][2] > 5 * res["dls"][2] and res["nr"][1] > 5 * res["dls"][1]

# ---------------------------------------------------------------- (3) 算例 15.3.2：经过手腕奇异附近的直线
P = WristPath()
th0 = P.th0
traj = P.analytic()
sp_ana = deg(np.abs(np.diff(traj, axis=0)).max(0) / P.dt)
t5_min = float(np.abs(deg(traj[:, 4])).min())
runs = {"ex": P.run("exact"), "fx": P.run("fixed", lam=0.01), "va": P.run("var", lam=0.02, eps=0.01)}


def summ(H):
    return deg(np.abs(H["dth"]).max(0)), H["ep"].max() * 1000, math.degrees(H["eo"].max()), H["ep_end"] * 1000, H["smin"].min(), H["th_end"]


ex, fx, va = summ(runs["ex"]), summ(runs["fx"]), summ(runs["va"])
assert ex[0].max() > 400 and fx[0].max() < 180 and va[0].max() < 180
labs_end = (ur_labels(ex[5]), ur_labels(fx[5]), ur_labels(va[5]))
# 可变阻尼只在奇异附近起作用：远离奇异的时间里 λ = 0
frac_damped = float(np.mean(runs["va"]["l2"] > 0))
t5_fx = deg(runs["fx"]["th"][:, 4])
cross_fx = bool(t5_fx.min() < 0 < t5_fx.max())
t5_va = deg(runs["va"]["th"][:, 4])
cross_va = bool(t5_va.min() < 0 < t5_va.max())
assert cross_fx and cross_va and not labs_end[1][2] and not labs_end[2][2]   # 两种阻尼都让手腕穿过奇异、换到“腕翻”
assert fx[0].max() > va[0].max()                                     # 可变阻尼的最大转速更低（λ_max = 0.02 > 0.01）

f1 = lambda a: f"{a:.0f}"
out(id_err=id_err, svd_err=svd_err,
    sv_s=vec(sv_s, 3), smin_s=sv_s[-1],
    nr_k=res["nr"][1], nr_step=res["nr"][2], nr_idx=res["nr"][3], nr_ok=res["nr"][0],
    jt_k=res["jt"][1], jt_step=res["jt"][2], jt_idx=res["jt"][3],
    dls_k=res["dls"][1], dls_step=res["dls"][2], dls_idx=res["dls"][3],
    lm_k=res["lm"][1], lm_step=res["lm"][2], lm_idx=res["lm"][3],
    th0_deg=vec(deg(th0), 1), t5_min=t5_min,
    sp_ana4=sp_ana[3], sp_ana6=sp_ana[5], sp_ana_max=sp_ana.max(),
    ex_sp4=ex[0][3], ex_sp6=ex[0][5], ex_ep=ex[1],
    fx_sp=fx[0].max(), fx_sp4=fx[0][3], fx_sp6=fx[0][5], fx_ep=fx[1], fx_eo=fx[2], fx_end=fx[3],
    va_sp=va[0].max(), va_ep=va[1], va_eo=va[2], va_end=va[3],
    smin0=float(runs["fx"]["smin"][0]), smin_fx=fx[4], frac_damped=100 * frac_damped, cross_fx=cross_fx, t5_end_fx=float(t5_fx[-1]), t5_end_va=float(t5_va[-1]), t5_0=float(deg(th0[4])),
    lab_ex=", ".join("A" if l[0] == "A" else "B" for l in labs_end[:1]),
    wrist_ex=tr("翻", "flipped") if not labs_end[0][2] else tr("不翻", "not flipped"),
    wrist_fx=tr("翻", "flipped") if not labs_end[1][2] else tr("不翻", "not flipped"))
