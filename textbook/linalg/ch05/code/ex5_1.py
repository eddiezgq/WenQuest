"""5.1 节：逆矩阵——2×2 的逆、验证 AA⁻¹ = A⁻¹A = I；AGV 的两个矩阵互为逆；奇异矩阵；(AB)⁻¹ = B⁻¹A⁻¹；相机内参矩阵的逆把像素变回光线方向。"""
import numpy as np

from bookout import out, tex, vec

A = np.array([[2.0, 1.0], [5.0, 3.0]])
Ai = np.linalg.inv(A)
out(A=tex(A, 0), Ai=tex(Ai, 0), I1=bool(np.allclose(A @ Ai, np.eye(2)) and np.allclose(Ai @ A, np.eye(2))))
# 解 Ax = b 用逆：x = A⁻¹ b
b = np.array([1.0, 2.0])
out(x=vec(Ai @ b, 0))
# AGV：车体速度 → 轮速（4.2 节）与轮速 → 车体速度（4.4 节）互为逆
r, wb = 0.075, 0.40
W = np.array([[1 / r, -wb / (2 * r)], [1 / r, wb / (2 * r)]])
K = np.array([[r / 2, r / 2], [-r / wb, r / wb]])
out(W=tex(W, 4), K=tex(K, 4), KW=tex(K @ W, 0), Kinv=tex(np.linalg.inv(K), 4))
# 奇异矩阵：两列共线，Px = 0 有非零解，没有逆
P = np.array([[1.0, 2.0], [2.0, 4.0]])
out(P=tex(P, 0), Pnull=vec(P @ np.array([2.0, -1.0]), 0), rankP=int(np.linalg.matrix_rank(P)))
# (AB)⁻¹ = B⁻¹A⁻¹ ≠ A⁻¹B⁻¹
B = np.array([[1.0, 2.0], [0.0, 1.0]])
ABi = np.linalg.inv(A @ B)
out(B=tex(B, 0), ABi=tex(ABi, 0), BiAi=tex(np.linalg.inv(B) @ Ai, 0), AiBi=tex(Ai @ np.linalg.inv(B), 0),
    rev=bool(np.allclose(ABi, np.linalg.inv(B) @ Ai)))
# 相机：K⁻¹ 把像素 (u, v, 1) 变成光线方向；乘以深度 Z 回到三维点
Kc = np.array([[800.0, 0, 320], [0, 800.0, 240], [0, 0, 1]])
Kci = np.linalg.inv(Kc)
ray = Kci @ np.array([370.0, 215.0, 1.0])
out(Kc=tex(Kc, 0), Kci=tex(Kci, 5), ray=vec(ray, 5), P3=vec(1.6 * ray, 2))
