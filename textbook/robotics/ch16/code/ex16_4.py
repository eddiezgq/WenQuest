"""16.4 节：可操作度椭球。

(1) 量纲问题：UR5e 在 θ* 的几何雅可比 J_g（6×6），长度单位取 m 与取 mm 时奇异值的变化，可操作度与条件数跟着变。
(2) 算例 16.4.1：θ* 处法兰盘中心的线速度椭球（J_v = J_g 的后三行）与角速度椭球（J_ω = 前三行）：半轴、方向、
    可操作度、条件数；角速度椭球的半轴恰为 √3、√2、1（三根平行轴、两根竖直轴、一根水平轴）；
    用 J_s 后三行算出的“椭球”不同（它是与 {s} 原点重合的那一点的速度）；用 J_b 后三行算出的半轴与 J_v 相同。
    定理 16.4.1 的核对：任意单位 θ̇ 的像都在椭球内；沿方向 u 的最大速度等于速度传递比 α(u)。
    竖直方向的速度传递比。
(3) 算例 16.4.2：法兰盘姿态与高度保持 θ* 的值，中心沿水平射线移动（到基座轴线的距离 ρ），可操作度 w_v、
    最小半轴 σ_min、条件数 κ_v 随 ρ 的变化；三个指标的最优位置不同；姿态保持不变时的线速度椭球（定理 16.4.2）
    包含在 J_v 的椭球之内，它的可操作度在肩部奇异处（ρ → d4）趋于零。
"""
import math

import numpy as np

from _jac import (D4, TH_STAR, ur_ik, ellipsoid, held_ellipsoid, kappa, manip, svals, trans_ratio, ur_det_factors, ur_fk, ur_jg,
                  ur_jv, ur_jw, ur_js, ur_jb, ur_radial, ur_radial_point)
from bookout import T, out, tex, vec

deg = np.degrees
rng = np.random.default_rng(164)

# ---------------------------------------------------------------- (1) 量纲：m 与 mm
Jg = ur_jg(TH_STAR)
s_m = svals(Jg)
Dmm = np.diag([1, 1, 1, 1000.0, 1000.0, 1000.0])          # 线速度改用 mm/s：后三行乘 1000
s_mm = svals(Dmm @ Jg)
w_m, w_mm = float(np.prod(s_m)), float(np.prod(s_mm))
k_m, k_mm = s_m[0] / s_m[-1], s_mm[0] / s_mm[-1]
assert abs(w_mm / w_m - 1e9) / 1e9 < 1e-9                   # det 乘 1000³（方阵：w = |det J|）
# 改单位不是整体缩放：条件数变了两个数量级以上
assert k_mm > 100 * k_m

# ---------------------------------------------------------------- (2) 算例 16.4.1：θ* 处的两个椭球
Jv, Jw = ur_jv(TH_STAR), ur_jw(TH_STAR)
sv, Uv = ellipsoid(Jv)
sw, Uw = ellipsoid(Jw)
for k in range(3):                                           # 方向的符号：取最大分量为正
    Uv[:, k] *= np.sign(Uv[np.argmax(np.abs(Uv[:, k])), k])
    Uw[:, k] *= np.sign(Uw[np.argmax(np.abs(Uw[:, k])), k])
wv, kv = manip(Jv), sv[0] / sv[-1]
ww, kw = manip(Jw), sw[0] / sw[-1]
assert abs(wv - np.prod(sv)) < 1e-14 and abs(ww - np.prod(sw)) < 1e-14
# 角速度椭球：J_ω J_ωᵀ = Σ ω_i ω_iᵀ；三根平行轴 y′、两根竖直轴（1、6）、一根水平轴（5）
y1 = np.array([math.sin(TH_STAR[0]), -math.cos(TH_STAR[0]), 0.0])
assert np.allclose(sw, [math.sqrt(3), math.sqrt(2), 1.0], atol=1e-14)
assert abs(abs(Uw[:, 0] @ y1) - 1) < 1e-14 and abs(abs(Uw[:, 1][2]) - 1) < 1e-14
a5 = Jw[:, 4]
assert abs(abs(Uw[:, 2] @ a5) - 1) < 1e-14
# J_s 的后三行：与 {s} 原点重合的那一点的速度，“椭球”不同；J_b 的后三行 = Rᵀ J_v，半轴相同
s_js = svals(ur_js(TH_STAR)[3:])
s_jb = svals(ur_jb(TH_STAR)[3:])
assert np.allclose(s_jb, sv, atol=1e-14) and np.abs(s_js - sv).max() > 0.01
# 定理 16.4.1 的核对：单位 θ̇ 的像满足 Vᵀ (J Jᵀ)⁻¹ V ≤ 1；沿 u 的最大速度 = α(u)
A = Jv @ Jv.T
worst = 0.0
for _ in range(20000):
    x = rng.normal(size=6)
    x /= np.linalg.norm(x)
    v = Jv @ x
    worst = max(worst, float(v @ np.linalg.solve(A, v)))
assert worst <= 1 + 1e-12
u = rng.normal(size=3)
u /= np.linalg.norm(u)
# 沿 u 方向的最大速度：max t，使 t u = J_v θ̇、‖θ̇‖ ≤ 1；最小范数解 θ̇ = J_v⁺ u t
t_best = 1 / np.linalg.norm(np.linalg.pinv(Jv) @ u)
assert abs(t_best - trans_ratio(Jv, u)) < 1e-12
assert sv[-1] - 1e-12 <= trans_ratio(Jv, u) <= sv[0] + 1e-12
az = trans_ratio(Jv, [0, 0, 1.0])                            # 竖直方向的速度传递比
ah = trans_ratio(Jv, ur_radial_point(1.0) - ur_radial_point(0.0))   # 径向（水平）

# ---------------------------------------------------------------- (3) 算例 16.4.2：径向路径
p_star = ur_fk(TH_STAR)[:3, 3]
rho_star = float(math.hypot(p_star[0], p_star[1]))
# 最大伸距：二分法找解析解刚好存在的 ρ（此处 θ3 → 0，肘部奇异）
lo_, hi_ = rho_star, 1.2
for _ in range(60):
    m = (lo_ + hi_) / 2
    Tm = ur_fk(TH_STAR)
    Tm[:3, 3] = ur_radial_point(m)
    if not ur_ik(Tm):
        hi_ = m
    else:
        lo_ = m
rho_max = lo_
q_edge = ur_radial([rho_max])[0]
assert abs(math.sin(q_edge[2])) < 1e-3                      # 伸到头时肘部伸直
rhos = np.linspace(0.20, rho_max - 1e-4, 400)
Q = ur_radial(rhos)
assert not np.isnan(Q).any()
W, SM, K, WH, KH, SH = [], [], [], [], [], []
for q in Q:
    J = ur_jv(q)
    s = svals(J)
    W.append(manip(J))
    SM.append(s[-1])
    K.append(s[0] / s[-1])
    ah_, _ = held_ellipsoid(q)
    WH.append(float(np.prod(ah_)))
    KH.append(ah_[0] / ah_[-1])
    SH.append(ah_[-1])
    # 姿态保持时的椭球在 J_v 的椭球之内：它的每个半轴端点都满足 J_v 椭球的不等式
    a_h, D_h = held_ellipsoid(q)
    for k in range(3):
        v = a_h[k] * D_h[:, k]
        assert v @ np.linalg.solve(J @ J.T, v) <= 1 + 1e-9
W, SM, K, WH, KH, SH = map(np.array, (W, SM, K, WH, KH, SH))
iw, ik, isg, iwh, ikh, ish = (int(np.argmax(W)), int(np.argmin(K)), int(np.argmax(SM)), int(np.argmax(WH)), int(np.argmin(KH)),
                              int(np.argmax(SH)))
for i in (iw, ik, isg, iwh, ikh, ish):
    assert 0 < i < len(rhos) - 1                            # 最优点都在内部
# 姿态保持时的可操作度在肩部奇异处趋于零：ρ → d4 时 r → 0
r_near = ur_radial([D4 + 0.004])[0]
wh_near = float(np.prod(held_ellipsoid(r_near)[0])) if not np.isnan(r_near[0]) else float("nan")
assert wh_near < 0.05 * WH[iwh]
f_star = ur_det_factors(TH_STAR)

out(p=vec(p_star, 4), sm=", ".join(f"{x:.4f}" for x in s_m), smm=", ".join(f"{x:.4f}" for x in s_mm), w_m=w_m, w_mm=w_mm, k_m=k_m, k_mm=k_mm,
    sv=", ".join(f"{x:.4f}" for x in sv), u1=vec(Uv[:, 0], 4), u2=vec(Uv[:, 1], 4), u3=vec(Uv[:, 2], 4), wv=wv, kv=kv,
    sw=", ".join(f"{x:.4f}" for x in sw), ww=ww, kw=kw, y1=vec(y1, 4), a5=vec(a5, 4),
    sjs=", ".join(f"{x:.4f}" for x in s_js), worst=worst, az=az, ah=ah,
    rho_star=rho_star, z_star=float(p_star[2]), rho_max=rho_max, rho0=float(rhos[0]), d4=D4,
    rw=float(rhos[iw]), w_best=float(W[iw]), t3_w=float(deg(Q[iw][2])),
    rk=float(rhos[ik]), k_best=float(K[ik]), t3_k=float(deg(Q[ik][2])),
    rs=float(rhos[isg]), s_best=float(SM[isg]),
    rwh=float(rhos[iwh]), wh_best=float(WH[iwh]), t3_wh=float(deg(Q[iwh][2])), rsh=float(rhos[ish]), sh_best=float(SH[ish]),
    sh_star=float(held_ellipsoid(TH_STAR)[0][-1]), kh_star=float(np.divide(*held_ellipsoid(TH_STAR)[0][[0, -1]])),
    ah_star=", ".join(f"{x:.4f}" for x in held_ellipsoid(TH_STAR)[0]), rkh=float(rhos[ikh]), kh_best=float(KH[ikh]),
    w_at_star=float(manip(ur_jv(TH_STAR))), wh_star=float(np.prod(held_ellipsoid(TH_STAR)[0])), wh_near=wh_near,
    k_edge=float(K[-1]), w_edge=float(W[-1]), wh_edge=float(WH[-1]), w0=float(W[0]), k0=float(K[0]))
