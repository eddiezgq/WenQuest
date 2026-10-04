"""4.7 节：矩阵乘法怎样算得快——运算量 2n³；分块（分片）乘法与普通乘法结果相同；施特拉森算法：2×2 块只需 7 次乘法，
递归后乘法次数约 n^2.81；与普通算法比较乘法次数，并检验递归施特拉森算法的误差。"""
import math

import numpy as np

from bookout import out


def blocked(A, B, bs):
    n = A.shape[0]
    C = np.zeros((n, n))
    for i in range(0, n, bs):
        for k in range(0, n, bs):
            for j in range(0, n, bs):
                C[i:i + bs, j:j + bs] += A[i:i + bs, k:k + bs] @ B[k:k + bs, j:j + bs]
    return C


def strassen(A, B, leaf=32):
    n = A.shape[0]
    if n <= leaf:
        return A @ B
    h = n // 2
    a, b, c, d = A[:h, :h], A[:h, h:], A[h:, :h], A[h:, h:]
    e, f, g, k = B[:h, :h], B[:h, h:], B[h:, :h], B[h:, h:]
    M1 = strassen(a + d, e + k, leaf)
    M2 = strassen(c + d, e, leaf)
    M3 = strassen(a, f - k, leaf)
    M4 = strassen(d, g - e, leaf)
    M5 = strassen(a + b, k, leaf)
    M6 = strassen(c - a, e + f, leaf)
    M7 = strassen(b - d, g + k, leaf)
    return np.block([[M1 + M4 - M5 + M7, M3 + M5], [M2 + M4, M1 - M2 + M3 + M6]])


rng = np.random.default_rng(47)
n = 256
A, B = rng.standard_normal((n, n)), rng.standard_normal((n, n))
C = A @ B
def sci(x):   # 7.8e-14 → 7.8\times10^{-14}
    m, e = f"{x:.1e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"


be, se = float(np.abs(blocked(A, B, 32) - C).max()), float(np.abs(strassen(A, B) - C).max())
out(block_err=be, str_err=se, block_tex=sci(be), str_tex=sci(se), flops256=2 * n ** 3)
# 2×2 的施特拉森公式（数字检验）
A2, B2 = np.array([[1.0, 2], [3, 4]]), np.array([[5.0, 6], [7, 8]])
out(s2=bool(np.allclose(strassen(A2, B2, leaf=1), A2 @ B2)))
# 乘法次数：普通 n³，完全递归的施特拉森 7^k（n = 2^k）
rows = []
for k in (1, 3, 5, 10, 13):
    n_ = 2 ** k
    rows.append((n_, n_ ** 3, 7 ** k, n_ ** 3 / 7 ** k))
out(**{f"srow{k}": f"{n_} | {a:,} | {b:,} | {r:.2f}".replace(",", " ") for (n_, a, b, r), k in zip(rows, (1, 3, 5, 10, 13))})
out(exp=math.log2(7))
