"""21.6 节：克罗内克积与矩阵的向量化。(1) vec(AXB) = (Bᵀ ⊗ A) vec X（vec 按列拉直）；A ⊗ B 的特征值、奇异值、逆；
(2) 西尔维斯特方程 AX + XB = C 化为 (I ⊗ A + Bᵀ ⊗ I) vec X = vec C；(3) 离散李雅普诺夫方程：AGV 沿路径的横向偏差 e 与航向偏差 φ
在反馈控制下 z_{k+1} = F z_k + w_k，稳态协方差 P 满足 P = F P Fᵀ + Q，即 (I − F ⊗ F) vec P = vec Q；与 2 万步仿真比较；
(4) 二维网格的拉普拉斯矩阵 L₂ = I ⊗ L₁ + L₁ ⊗ I（仓库地面的温度场、占据栅格地图的平滑），特征值是两两之和。"""
import math

import numpy as np
from scipy.linalg import solve_discrete_lyapunov, solve_sylvester

from bookout import out, tex, vec

rng = np.random.default_rng(21061)
vecc = lambda M: M.reshape(-1, order="F")           # 按列拉直
# (1)
A = np.array([[1.0, 2.0], [0.0, 3.0]])
B = np.array([[2.0, -1.0], [1.0, 1.0]])
X = np.array([[1.0, 0.0], [2.0, -1.0]])
lhs = vecc(A @ X @ B)
K = np.kron(B.T, A)
assert np.allclose(lhs, K @ vecc(X))
# 若按行拉直，公式变为 (A ⊗ Bᵀ) vecᵣ X
assert np.allclose((A @ X @ B).reshape(-1), np.kron(A, B.T) @ X.reshape(-1))
out(A=tex(A, 0), B=tex(B, 0), X=tex(X, 0), AXB=tex(A @ X @ B, 0), K=tex(K, 0), vX=vec(vecc(X), 0), vAXB=vec(lhs, 0))
la, lb = np.linalg.eigvals(A), np.linalg.eigvals(B)
lk = np.linalg.eigvals(np.kron(A, B))
assert all(np.min(np.abs(lk - a * b)) < 1e-9 for a in la for b in lb)
sa, sb = np.linalg.svd(A, compute_uv=False), np.linalg.svd(B, compute_uv=False)
assert np.allclose(np.sort(np.linalg.svd(np.kron(A, B), compute_uv=False)), np.sort(np.outer(sa, sb).ravel()))
assert np.allclose(np.linalg.inv(np.kron(A, B)), np.kron(np.linalg.inv(A), np.linalg.inv(B)))
out(la=", ".join(f"{z.real:g}" for z in la), lb_re=float(lb[0].real), lb_im=float(abs(lb[0].imag)))

# (2) 西尔维斯特方程
Ms = np.kron(np.eye(2), A) + np.kron(B.T, np.eye(2))
Cs = np.array([[1.0, 2.0], [3.0, 4.0]])
Xs = np.linalg.solve(Ms, vecc(Cs)).reshape(2, 2, order="F")
assert np.allclose(A @ Xs + Xs @ B, Cs) and np.allclose(Xs, solve_sylvester(A, B, Cs))
out(Xs=tex(Xs, 4), Ms=tex(Ms, 0))

# (3) AGV 横向控制的离散模型：z = (e, φ)，采样 dt = 0.05 s，车速 v = 1 m/s，反馈 ω = −k₁ e − k₂ φ
dt, v, k1, k2 = 0.05, 1.0, 4.0, 3.0
F = np.array([[1.0, v * dt], [-k1 * dt, 1 - k2 * dt]])
sig_e, sig_p = 0.002, math.radians(0.3)               # 每步的扰动：横向 2 mm、航向 0.3°（地面不平、轮子打滑）
Q = np.diag([sig_e ** 2, sig_p ** 2])
rhoF = max(abs(np.linalg.eigvals(F)))
FF = np.kron(F, F)
assert abs(max(abs(np.linalg.eigvals(FF))) - rhoF ** 2) < 1e-12
P = np.linalg.solve(np.eye(4) - FF, vecc(Q)).reshape(2, 2, order="F")
assert np.allclose(P, solve_discrete_lyapunov(F, Q)) and np.allclose(P, F @ P @ F.T + Q)
# 仿真
N = 20000
z = np.zeros(2)
Z = np.empty((N, 2))
for k in range(N):
    z = F @ z + np.array([sig_e, sig_p]) * rng.standard_normal(2)
    Z[k] = z
Pm = np.cov(Z[1000:].T)
# 迭代 P ← F P Fᵀ + Q 的收敛
Pk, its = np.zeros((2, 2)), 0
while np.linalg.norm(Pk - P) > 1e-6 * np.linalg.norm(P):
    Pk = F @ Pk @ F.T + Q
    its += 1
out(F=tex(F, 3), rhoF=float(rhoF), rho2=float(rhoF ** 2), sd_e=float(1000 * math.sqrt(P[0, 0])), sd_p=float(math.degrees(math.sqrt(P[1, 1]))),
    sd_e_sim=float(1000 * math.sqrt(Pm[0, 0])), sd_p_sim=float(math.degrees(math.sqrt(Pm[1, 1]))),
    corr=float(P[0, 1] / math.sqrt(P[0, 0] * P[1, 1])), its=its)
# 关掉反馈（开环）：ρ(F) = 1，协方差无界增长
F0 = np.array([[1.0, v * dt], [0.0, 1.0]])
out(rho0=float(max(abs(np.linalg.eigvals(F0)))))

# (4) 二维拉普拉斯：n × n 网格
n = 4
L1 = 2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1)
L2 = np.kron(np.eye(n), L1) + np.kron(L1, np.eye(n))
mu1 = np.linalg.eigvalsh(L1)
mu2 = np.sort(np.linalg.eigvalsh(L2))
pred = np.sort(np.add.outer(mu1, mu1).ravel())
assert np.allclose(mu2, pred)
out(mu1=", ".join(f"{x:.3f}" for x in mu1), mu2min=float(mu2[0]), mu2max=float(mu2[-1]), nnz=int(np.count_nonzero(L2)), N2=n * n)
# 存储与运算量：n = 100 时 L₂ 是 10⁴ 阶；直接用 kron 构造稠密矩阵要 10⁸ 个数
out(dense100=float((100 ** 2) ** 2 * 8 / 1e9), nnz100=int(5 * 100 ** 2 - 4 * 100))
