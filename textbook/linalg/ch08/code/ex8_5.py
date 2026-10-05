"""8.5 节：线性代数基本定理（一）——四个子空间的维数 r、n − r、r、m − r；对随机矩阵和本章的例子矩阵验证。"""
import numpy as np
import scipy.linalg as sla

from _a import A
from bookout import out

m, n = A.shape
r = int(np.linalg.matrix_rank(A))
out(m=m, n=n, r=r, dC=sla.orth(A).shape[1], dN=sla.null_space(A).shape[1], dR=sla.orth(A.T).shape[1], dLN=sla.null_space(A.T).shape[1])
rng = np.random.default_rng(85)
B = rng.standard_normal((5, 3)) @ rng.standard_normal((3, 7))     # 5×7，秩 3
rB = int(np.linalg.matrix_rank(B))
out(rB=rB, dims=f"{sla.orth(B).shape[1]}, {sla.null_space(B).shape[1]}, {sla.orth(B.T).shape[1]}, {sla.null_space(B.T).shape[1]}")
