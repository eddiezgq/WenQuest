"""10.6 节：加权最小二乘。(a) 激光测距（σ = 1 cm）与超声测距（σ = 5 cm）各测 3 次，求墙的距离：普通平均与按 1/σ² 加权；
(b) 相机跟踪远去的 AGV，双目相机的深度误差随距离的平方增大（σ_i ∝ x_i²），拟合速度直线：普通最小二乘与加权最小二乘的估计值离散程度（蒙特卡罗 2000 次）；
(c) 参数的协方差 (AᵀWA)⁻¹ 与实测离散程度一致。"""
import numpy as np

from bookout import out, vec

rng = np.random.default_rng(66)
d_true = 1.500
lid = d_true + rng.normal(scale=0.01, size=3)
ult = d_true + rng.normal(scale=0.05, size=3)
z = np.r_[lid, ult]
w = np.r_[np.full(3, 1 / 0.01 ** 2), np.full(3, 1 / 0.05 ** 2)]
ols, wls = z.mean(), (w @ z) / w.sum()
out(lid=vec(lid * 100, 1), ult=vec(ult * 100, 1), ols=ols * 100, wls=wls * 100,
    s_ols=float(np.sqrt((3 * 0.01 ** 2 + 3 * 0.05 ** 2) / 36)) * 100, s_wls=float(1 / np.sqrt(w.sum())) * 100)
# (b) AGV 以 0.8 m/s 远离相机，起点 2 m；每 0.5 s 测一次位置，共 12 次；双目相机的深度误差与距离的平方成正比：σ = 0.005 x²（m）
t = np.arange(12) * 0.5
x_true = 2.0 + 0.8 * t
sig = 0.005 * x_true ** 2
A = np.column_stack([np.ones_like(t), t])
W = np.diag(1 / sig ** 2)
est_o, est_w = [], []
for _ in range(2000):
    x = x_true + rng.normal(size=t.size) * sig
    est_o.append(np.linalg.solve(A.T @ A, A.T @ x))
    est_w.append(np.linalg.solve(A.T @ W @ A, A.T @ W @ x))
est_o, est_w = np.array(est_o), np.array(est_w)
C_w = np.linalg.inv(A.T @ W @ A)
Ai = np.linalg.solve(A.T @ A, A.T)
C_o = Ai @ np.diag(sig ** 2) @ Ai.T
out(sv_o=float(est_o[:, 1].std()), sv_w=float(est_w[:, 1].std()), mv_o=float(est_o[:, 1].mean()), mv_w=float(est_w[:, 1].mean()),
    cv_w=float(np.sqrt(C_w[1, 1])), cv_o=float(np.sqrt(C_o[1, 1])), sig0=float(sig[0]), sig11=float(sig[-1]))
