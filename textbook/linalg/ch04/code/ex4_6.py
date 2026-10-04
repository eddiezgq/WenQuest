"""4.6 节：特殊矩阵——对角矩阵（缩放单位）、三角矩阵之积仍为三角矩阵、置换矩阵、稀疏矩阵的存储。"""
import numpy as np
import scipy.sparse as sp

from bookout import out, tex, vec

# 对角矩阵：把 (mm, mm, deg) 换算成 (m, m, rad)
D = np.diag([1e-3, 1e-3, np.pi / 180])
out(Dv=vec(D @ np.array([652.0, 134.0, 30.0]), 4))
# 下三角矩阵之积
L1 = np.array([[1.0, 0, 0], [2, 1, 0], [4, 3, 1]])
L2 = np.array([[2.0, 0, 0], [-1, 1, 0], [0, 5, 3]])
out(L1=tex(L1, 0), L2=tex(L2, 0), L1L2=tex(L1 @ L2, 0), lower=bool(np.allclose(np.triu(L1 @ L2, 1), 0)))
# 置换矩阵：交换第 1、3 行
P = np.eye(3)[[2, 1, 0]]
A = np.array([[1.0, 2, 3], [4, 5, 6], [7, 8, 9]])
out(P=tex(P, 0), PA=tex(P @ A, 0), AP=tex(A @ P, 0), PTP=bool(np.allclose(P.T @ P, np.eye(3))))
P2 = np.eye(3)[[1, 2, 0]]
out(P2=tex(P2, 0), P2cube=bool(np.allclose(np.linalg.matrix_power(P2, 3), np.eye(3))))
# 稀疏矩阵：n = 100000 个节点的一维杆（三对角矩阵 −1, 2, −1）
n = 100000
Lap = sp.diags([-np.ones(n - 1), 2 * np.ones(n), -np.ones(n - 1)], [-1, 0, 1], format="csr")
dense_bytes = 8 * n * n
csr_bytes = Lap.data.nbytes + Lap.indices.nbytes + Lap.indptr.nbytes
out(nnz=int(Lap.nnz), dense_gb=dense_bytes / 1e9, csr_mb=csr_bytes / 1e6, frac=Lap.nnz / n ** 2)
xv = np.ones(n)
out(lapx_end=vec((Lap @ xv)[[0, 1, n - 1]], 0))
# CSR 格式的三个数组（以 4×4 为例）
S = sp.csr_matrix(np.array([[2.0, -1, 0, 0], [-1, 2, -1, 0], [0, -1, 2, -1], [0, 0, -1, 2]]))
out(csr_data=", ".join(str(int(v)) for v in S.data), csr_idx=", ".join(map(str, S.indices)), csr_ptr=", ".join(map(str, S.indptr)))
