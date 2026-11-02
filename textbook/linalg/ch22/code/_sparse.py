"""本章共用：稀疏对称矩阵的符号消元（22.3 节）。以下划线开头，构建时不单独运行。
用“消元博弈”数填充：消去一个顶点时，它的尚未消去的邻居两两连边；nnz(L) = n + Σ（消去时的邻居数）。
排序：自然、反向卡思尔–麦基（RCM）、最小度（每步消去当前度最小的顶点，度相同取编号小的）、网格的嵌套剖分。"""
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import reverse_cuthill_mckee


def adj(A):
    A = sp.csr_matrix(A)
    n = A.shape[0]
    S = [set() for _ in range(n)]
    r, c = A.nonzero()
    for i, j in zip(r, c):
        if i != j:
            S[i].add(int(j))
    return S


def fill(A, order):
    """按 order 消元，返回 nnz(L)（含对角）、L 的非零元位置（按新编号）和乘法次数 Σ cₖ²（cₖ 为第 k 列对角以下的非零元个数）。"""
    S = adj(A)
    n = len(S)
    pos = {v: k for k, v in enumerate(order)}
    G = [set(s) for s in S]
    done = [False] * n
    nnz = n
    Lpat = []
    flops = 0
    for k, v in enumerate(order):
        nb = [u for u in G[v] if not done[u]]
        nnz += len(nb)
        flops += len(nb) ** 2
        Lpat += [(pos[u], k) for u in nb]
        for a in nb:
            for b in nb:
                if a != b:
                    G[a].add(b)
        done[v] = True
    return nnz, Lpat, flops


def min_degree(A):
    S = adj(A)
    n = len(S)
    G = [set(s) for s in S]
    alive = set(range(n))
    order = []
    while alive:
        v = min(alive, key=lambda u: (len(G[u]), u))
        nb = list(G[v])
        for a in nb:
            G[a].discard(v)
            for b in nb:
                if a != b:
                    G[a].add(b)
        alive.discard(v)
        order.append(v)
    return order


def rcm(A):
    return [int(i) for i in reverse_cuthill_mckee(sp.csr_matrix(A), symmetric_mode=True)]


def nested_dissection(m):
    """m × m 网格（编号 i·m + j）的嵌套剖分：先递归排两半，最后排中间的分隔线。"""
    def rec(r0, r1, c0, c1):
        if (r1 - r0) * (c1 - c0) <= 4:
            return [i * m + j for i in range(r0, r1) for j in range(c0, c1)]
        if r1 - r0 >= c1 - c0:
            mid = (r0 + r1) // 2
            return rec(r0, mid, c0, c1) + rec(mid + 1, r1, c0, c1) + [mid * m + j for j in range(c0, c1)]
        mid = (c0 + c1) // 2
        return rec(r0, r1, c0, mid) + rec(r0, r1, mid + 1, c1) + [i * m + mid for i in range(r0, r1)]
    return rec(0, m, 0, m)


def grid_laplacian(m):
    L1 = sp.diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=(m, m))
    I = sp.identity(m)
    return (sp.kron(I, L1) + sp.kron(L1, I)).tocsr()


def pose_graph(laps=4, per=25, every=5):
    """AGV 沿一条环形路线跑 laps 圈、每圈 per 个位姿（每个位姿一个未知数的简化模型）：
    相邻位姿之间有里程计约束；每隔 every 个位姿，与上一圈同一位置的位姿有一条回环约束。返回信息矩阵（对称正定）。"""
    n = laps * per
    A = sp.lil_matrix((n, n))
    def edge(i, j, w):
        A[i, i] += w; A[j, j] += w; A[i, j] -= w; A[j, i] -= w
    for i in range(n - 1):
        edge(i, i + 1, 1.0)
    for i in range(per, n):
        if i % every == 0:
            edge(i - per, i, 0.5)
    A[0, 0] += 1.0                                   # 固定起点
    return A.tocsr()


def arrow(n, hub_first=True):
    A = sp.lil_matrix((n, n))
    for i in range(n):
        A[i, i] = 4.0
    h = 0 if hub_first else n - 1
    for i in range(n):
        if i != h:
            A[h, i] = A[i, h] = 1.0
    A[h, h] = float(n)
    return A.tocsr()
