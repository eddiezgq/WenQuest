"""22.3 节：稀疏矩阵。(1) 一个 5 阶矩阵的 COO、CSR 存储；稀疏矩阵乘向量的运算量与非零元个数成正比；
(2) 箭形矩阵：中心节点排在前面时消元填满整个矩阵，排在最后时一个填充也没有；
(3) 仓库地面 30 × 30 网格的拉普拉斯矩阵：自然排序、RCM、最小度、嵌套剖分四种排序下乔列斯基因子的非零元个数；
(4) AGV 位姿图（跑 4 圈、每圈 25 个位姿，每隔 5 个位姿有一条回环约束）的信息矩阵：同样比较四种排序（嵌套剖分除外）；
(5) 存储：100 × 100 网格，稠密与 CSR 各要多少字节；与 SciPy 的 splu 相互核对。"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import splu

from _num import sci
from _sparse import arrow, fill, grid_laplacian, min_degree, nested_dissection, pose_graph, rcm
from bookout import out, tex

# (1) 存储格式
A = np.array([[4, 0, 0, 1, 0], [0, 3, 0, 0, 2], [0, 0, 5, 0, 0], [1, 0, 0, 6, 0], [0, 2, 0, 0, 7]], dtype=float)
S = sp.csr_matrix(A)
C = sp.coo_matrix(A)
out(A=tex(A, 0), nnz=int(S.nnz), coo_r=", ".join(str(i) for i in C.row), coo_c=", ".join(str(i) for i in C.col),
    coo_v=", ".join(f"{v:g}" for v in C.data), csr_ptr=", ".join(str(i) for i in S.indptr), csr_idx=", ".join(str(i) for i in S.indices),
    csr_val=", ".join(f"{v:g}" for v in S.data))
x = np.arange(1.0, 6.0)
y = np.zeros(5)
for i in range(5):                                   # CSR 乘向量：逐行扫描非零元
    for p in range(S.indptr[i], S.indptr[i + 1]):
        y[i] += S.data[p] * x[S.indices[p]]
assert np.allclose(y, A @ x)
out(Ax=", ".join(f"{v:g}" for v in y))

# (2) 箭形矩阵
n = 10
f_first, _, _ = fill(arrow(n, True), list(range(n)))
f_last, _, _ = fill(arrow(n, False), list(range(n)))
out(arrow_n=n, arrow_nnzA=int((arrow(n).nnz + n) // 2), arrow_first=f_first, arrow_last=f_last, arrow_full=n * (n + 1) // 2)

# (3) 30 × 30 网格（乘法次数按 Σ cₖ² 数）
m = 30
G = grid_laplacian(m)
N = m * m
orders = {"nat": list(range(N)), "rcm": rcm(G), "md": min_degree(G), "nd": nested_dissection(m)}
full = {k: fill(G, o) for k, o in orders.items()}
res = {k: v[0] for k, v in full.items()}
lowA = (G.nnz + N) // 2                               # A 的下三角（含对角）非零元个数
for k, v in res.items():
    out(**{f"g_{k}": v, f"g_{k}_ratio": v / lowA, f"g_{k}_fl": sci(full[k][2], 1)})
out(g_N=N, g_lowA=lowA, g_dense=N * (N + 1) // 2)
# 与 SciPy 的超节点 LU（对称模式、不选主元）核对：自然排序时 nnz(L) 应相同
lu = splu(G.tocsc(), permc_spec="NATURAL", diag_pivot_thresh=0.0, options={"SymmetricMode": True})
assert lu.L.nnz == res["nat"]
for spec in ("MMD_AT_PLUS_A",):
    lu2 = splu(G.tocsc(), permc_spec=spec, diag_pivot_thresh=0.0, options={"SymmetricMode": True})
    out(g_superlu_mmd=int(lu2.L.nnz))

# (4) 位姿图
P = pose_graph()
NP = P.shape[0]
ordp = {"nat": list(range(NP)), "rcm": rcm(P), "md": min_degree(P)}
rp = {k: fill(P, o)[0] for k, o in ordp.items()}
out(p_n=NP, p_lowA=int((P.nnz + NP) // 2), p_nat=rp["nat"], p_rcm=rp["rcm"], p_md=rp["md"], p_dense=NP * (NP + 1) // 2,
    p_loops=int(sum(1 for i in range(25, NP) if i % 5 == 0)))

# (5) 存储：100 × 100 网格
G100 = grid_laplacian(100)
Nb = G100.shape[0]
out(st_dense=float(Nb * Nb * 8 / 1e6), st_csr=float((G100.nnz * (8 + 4) + (Nb + 1) * 4) / 1e6), st_nnz=int(G100.nnz))
