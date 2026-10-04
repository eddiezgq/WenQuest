"""6.6 节：行列式与可逆性；乘积公式 det(AB) = det A det B——数值验证；det Aᵀ = det A；det A⁻¹ = 1/det A；
det(A + B) ≠ det A + det B；相似矩阵的行列式相同。"""
import numpy as np

from bookout import out, tex

d = np.linalg.det
A = np.array([[2.0, 1], [5, 3]])
B = np.array([[1.0, 2], [0, 1]])
C = np.array([[3.0, 1], [1, 2]])
out(dA=round(d(A)), dB=round(d(B)), dC=round(d(C)), dAC=round(d(A @ C)), dCA=round(d(C @ A)),
    dAt=round(d(A.T)), dAi=float(d(np.linalg.inv(C))), dsum=round(d(A + C)))
rng = np.random.default_rng(66)
X, Y = rng.standard_normal((5, 5)), rng.standard_normal((5, 5))
out(prod_ok=bool(np.isclose(d(X @ Y), d(X) * d(Y))), T_ok=bool(np.isclose(d(X.T), d(X))))
# 相似矩阵：det(S⁻¹ A S) = det A
S = rng.standard_normal((2, 2))
out(sim=round(float(d(np.linalg.inv(S) @ A @ S)), 10))
# 奇异：两行成比例
P = np.array([[1.0, 2], [2, 4]])
out(dP=float(d(P)))
