"""10.4 节：最小二乘与正规方程。经过 (0, 6)、(1, 0)、(2, 0) 的“最佳直线”：A x = b 无解，AᵀA x̂ = Aᵀb 给出 x̂ = (5, −3)，残差 e = (1, −2, 1) ⊥ C(A)。
机器人：工具中心点（TCP）的“定点转动”标定——工具尖端顶住一个固定点，换 8 个姿态记下法兰位姿，R_i t + p_i = q 堆成 24×6 的方程组，用最小二乘求工具偏移 t 与定点 q；
若所有姿态都绕同一根轴转，AᵀA 奇异，t 沿这根轴的分量定不出来。"""
import numpy as np

from _frac import fvec
from _num import sci
from bookout import out, tex, vec

A = np.array([[1.0, 0], [1, 1], [1, 2]])
b = np.array([6.0, 0, 0])
AtA, Atb = A.T @ A, A.T @ b
xh = np.linalg.solve(AtA, Atb)
e = b - A @ xh
out(Atb=vec(Atb, 0), xh=fvec(xh), e=fvec(e), E=float(e @ e), lst=vec(np.linalg.lstsq(A, b, rcond=None)[0], 4))
# 换一个 x，误差平方和变大
for name, x in (("E1", np.array([4.0, -2])), ("E2", np.array([6.0, -3]))):
    r = b - A @ x
    out(**{name: float(r @ r)})


def rot(axis, ang):
    k = np.asarray(axis, float) / np.linalg.norm(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K


rng = np.random.default_rng(42)
t_true = np.array([0.012, -0.005, 0.180])          # 工具尖端在法兰坐标系中的位置（m）
q_true = np.array([0.50, 0.10, 0.20])              # 固定点在基座坐标系中的位置（m）
R0 = rot([1, 0, 0], np.pi)                         # 法兰朝下


def solve(Rs, noise):
    rows, rhs = [], []
    for R in Rs:
        p = q_true - R @ t_true + rng.normal(scale=noise, size=3)
        rows.append(np.hstack([R, -np.eye(3)]))
        rhs.append(-p)
    M, y = np.vstack(rows), np.concatenate(rhs)
    return M, y


Rs = [rot(rng.normal(size=3), np.radians(rng.uniform(15, 35))) @ R0 for _ in range(8)]
M, y = solve(Rs, 1e-4)                               # 法兰位置的测量噪声 0.1 mm
sol = np.linalg.solve(M.T @ M, M.T @ y)
res = y - M @ sol
out(Mshape=f"{M.shape[0]}×{M.shape[1]}", rM=int(np.linalg.matrix_rank(M)), t_hat=vec(sol[:3] * 1000, 2), q_hat=vec(sol[3:] * 1000, 2),
    t_true=vec(t_true * 1000, 1), q_true=vec(q_true * 1000, 1), terr=float(np.linalg.norm(sol[:3] - t_true) * 1000),
    rms=float(np.sqrt(res @ res / (M.shape[0] - M.shape[1])) * 1000))
# 只绕法兰 z 轴转：AᵀA 奇异
Rz = [R0 @ rot([0, 0, 1], np.radians(a)) for a in (0, 45, 90, 135, 180, 225, 270, 315)]
M2, _ = solve(Rz, 0.0)
w = np.linalg.eigvalsh(M2.T @ M2)
out(rM2=int(np.linalg.matrix_rank(M2)), eigmin=sci(abs(float(w[0])) + 1e-18, 0), eigmax=float(w[-1]))
