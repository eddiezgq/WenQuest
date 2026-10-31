"""15.8 节：机械臂的质量矩阵为什么一定正定；可操作度椭球。参数见 _arm2m.py（l = 0.4/0.3 m，m = 2/1 kg，均匀细杆）。
(1) M(q) = Σ (m_i J_ciᵀJ_ci + I_i j_i j_iᵀ) = J_sᵀ W J_s：与公式算出的 M 一致；各种姿态下特征值都为正、乔列斯基分解都成功；
(2) q₂ = 120° 时 m₁₂ = 0：两个关节的惯性解耦；
(3) 可操作度 w = √det(JJᵀ) = l₁l₂|sin q₂|，q₂ = ±90° 时最大；
(4) 末端的等效质量矩阵 Λ = (J M⁻¹ Jᵀ)⁻¹：沿单位方向 u 推末端，末端“感到”的质量 1/(uᵀΛ⁻¹u)；
    近奇异姿态（q₂ = 10°）沿手臂方向的等效质量远大于垂直方向；
(5) 惯量张量半正定：vᵀIv = Σ m(|r|²|v|² − (r·v)²) ≥ 0（随机点云检验；共线点云有零特征值）。"""
import numpy as np

import _arm2m as A2
from bookout import out, tex, vec

d = np.pi / 180
q1 = 30 * d
worst = np.inf
for q2 in np.linspace(-np.pi, np.pi, 721):
    M = A2.mass(q2)
    assert np.allclose(M, A2.mass_from_jac(q1, q2))
    worst = min(worst, np.linalg.eigvalsh(M)[0])
    np.linalg.cholesky(M)
M0, M90 = A2.mass(0.0), A2.mass(90 * d)
out(M0=tex(M0, 4), M90=tex(M90, 4), lamM0=vec(np.linalg.eigvalsh(M0), 4), worst=float(worst),
    lamMpi=vec(np.linalg.eigvalsh(A2.mass(np.pi)), 4))
# 叠起来的雅可比 J_s（6×2）列满秩
Js = np.vstack([A2.jac_c(q1, 0.0, 1), [[1.0, 0.0]], A2.jac_c(q1, 0.0, 2), [[1.0, 1.0]]])
out(rankJs=int(np.linalg.matrix_rank(Js)))
# (2) 解耦姿态
c = -(A2.M2 * A2.L2 ** 2 / 12 + A2.M2 * (A2.L2 / 2) ** 2) / (A2.M2 * A2.L1 * A2.L2 / 2)
q2d = np.degrees(np.arccos(c))
out(cos_dec=float(c), q2_dec=float(q2d), M120=tex(A2.mass(q2d * d), 4))
# 带 0.5 kg 负载时的解耦角
mp = 0.5
cp = -(A2.M2 * A2.L2 ** 2 / 12 + A2.M2 * (A2.L2 / 2) ** 2 + mp * A2.L2 ** 2) / (A2.M2 * A2.L1 * A2.L2 / 2 + mp * A2.L1 * A2.L2)
out(q2_dec_mp=float(np.degrees(np.arccos(cp))))
# (3) 可操作度
qs = np.linspace(0, np.pi, 181)
w = [np.sqrt(np.linalg.det(A2.jac(q1, q) @ A2.jac(q1, q).T)) for q in qs]
out(wmax=float(max(w)), wmax_at=float(np.degrees(qs[int(np.argmax(w))])), l1l2=float(A2.L1 * A2.L2),
    w_err=float(max(abs(wi - A2.L1 * A2.L2 * abs(np.sin(q))) for wi, q in zip(w, qs))))
for name, q2 in (("90", 90), ("10", 10)):
    J = A2.jac(q1, q2 * d)
    sv = np.linalg.svd(J, compute_uv=False)
    M = A2.mass(q2 * d)
    Lam = np.linalg.inv(J @ np.linalg.inv(M) @ J.T)
    le, Ve = np.linalg.eigh(Lam)
    # 沿手臂方向（基座指向末端）与垂直方向
    p = A2.points(q1, q2 * d)[2]
    ua = p / np.linalg.norm(p)
    un = np.array([-ua[1], ua[0]])
    Li = np.linalg.inv(Lam)
    out(**{f"sv_{name}": vec(sv, 3), f"lamL_{name}": vec(le, 2), f"ma_{name}": float(1 / (ua @ Li @ ua)),
           f"mn_{name}": float(1 / (un @ Li @ un)), f"ratioL_{name}": float(le[1] / le[0]), f"Lam_{name}": tex(Lam, 2)})
# (5) 惯量张量
rng = np.random.default_rng(158)
P = rng.normal(size=(500, 3)) * [0.1, 0.05, 0.02]
P -= P.mean(0)                          # 对质心
m = np.full(500, 0.002)
It = sum(mi * (r @ r * np.eye(3) - np.outer(r, r)) for mi, r in zip(m, P))
line = np.outer(rng.uniform(-0.2, 0.2, 200), [1.0, 2, 2]) / 3
Il = sum(0.005 * (r @ r * np.eye(3) - np.outer(r, r)) for r in line)
out(lamI=vec(np.linalg.eigvalsh(It) * 1e4, 3), lamIl=vec(np.linalg.eigvalsh(Il) * 1e4, 3))
