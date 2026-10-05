"""12.5 节：自伴算子、正规算子、酉算子。
机器人：柔性关节的二自由度模型。电机侧转动惯量 J_m、连杆侧 J_l，减速器的扭转刚度 k，位置控制器把电机“拉”向目标的等效刚度 k_p。
M = diag(J_m, J_l)，K = [[k_p + k, −k], [−k, k]]，自由振动 M q̈ + K q = 0。A = M⁻¹K 不对称，但在 M-内积下自伴：
特征值为正实数（固有频率的平方），振型 M-正交而不（欧氏）正交；初始偏移按 M-内积直接分解到两个振型上。
正规与非正规：旋转矩阵（正规，特征值 ±i）、剪切矩阵（不正规）；酉矩阵保持内积。"""
import numpy as np

from _num import sci
from bookout import out, tex, vec

Jm, Jl, k, kp = 2.0, 1.0, 3.0e4, 6.0e4      # kg·m²，N·m/rad
M = np.diag([Jm, Jl])
K = np.array([[kp + k, -k], [-k, k]])
A = np.linalg.solve(M, K)
lam, V = np.linalg.eig(A)
idx = np.argsort(lam)
lam, V = lam[idx].real, V[:, idx].real
V = V / V[0]                                  # 第一个分量取 1
out(M=tex(M, 0), K=tex(K, 0), A=tex(A, 0), lam1=float(lam[0]), lam2=float(lam[1]), w1=float(np.sqrt(lam[0])), w2=float(np.sqrt(lam[1])),
    f1=float(np.sqrt(lam[0]) / (2 * np.pi)), f2=float(np.sqrt(lam[1]) / (2 * np.pi)),
    v1=vec(V[:, 0], 0), v2=vec(V[:, 1], 0), v1Mv2=float(V[:, 0] @ M @ V[:, 1]), v1v2=float(V[:, 0] @ V[:, 1]),
    Asym=float(np.abs(A - A.T).max()), MA_sym=float(np.abs(M @ A - (M @ A).T).max()))
# 初始偏移：电机侧转 1 mrad，连杆侧不动
q0 = np.array([1.0, 0.0])
cM = [float(V[:, j] @ M @ q0 / (V[:, j] @ M @ V[:, j])) for j in range(2)]
cE = [float(V[:, j] @ q0 / (V[:, j] @ V[:, j])) for j in range(2)]
out(q0=vec(q0, 0), c1=cM[0], c2=cM[1], recon=vec(cM[0] * V[:, 0] + cM[1] * V[:, 1], 4), cE1=cE[0], cE2=cE[1],
    reconE=vec(cE[0] * V[:, 0] + cE[1] * V[:, 1], 3))
# 自由振动的数值解与模态叠加比较
t = np.linspace(0, 0.2, 2001)
qt = np.outer(cM[0] * V[:, 0], np.cos(np.sqrt(lam[0]) * t)) + np.outer(cM[1] * V[:, 1], np.cos(np.sqrt(lam[1]) * t))
from scipy.integrate import solve_ivp
sol = solve_ivp(lambda tt, y: np.r_[y[2:], -A @ y[:2]], (0, 0.2), np.r_[q0, 0, 0], t_eval=t, rtol=1e-10, atol=1e-12)
out(ode_diff=sci(float(np.abs(sol.y[:2] - qt).max()) + 1e-30, 0))
# 正规与非正规
R = np.array([[0.0, -1], [1, 0]])
S = np.array([[1.0, 1], [0, 1]])
out(R=tex(R, 0), S=tex(S, 0), SST=tex(S @ S.T, 0), STS=tex(S.T @ S, 0))
