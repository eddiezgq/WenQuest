"""3.8 节：消元需要多少次运算——逐次数出来，与公式 n³/3 + n²/2 − 5n/6（消元的乘除法）对照。"""
from bookout import out
from _elim import count_ops

rows = []
for n in (2, 3, 10, 100, 1000):
    mul, add = count_ops(n)
    elim_mul = n ** 3 / 3 + n ** 2 / 2 - 5 * n / 6
    back = n * (n + 1) / 2
    rows.append((n, mul, add, elim_mul + back, n ** 3 / 3))
def sci(c):
    if c < 1e4:
        return f"{c:.4g}"
    e = int(f"{c:e}".split("e")[1])
    return f"${c / 10 ** e:.3f}\\times10^{{{e}}}$"


out(**{f"row{n}": f"{m} | {a} | {int(round(f))} | {sci(c)}" for n, m, a, f, c in rows})
m3, a3 = count_ops(3)
out(m3=m3, a3=a3, ratio1000=count_ops(1000)[0] / (1000 ** 3 / 3))
# 规模估算：n = 10000，乘加各约 n³/3 次，合计约 2n³/3 次浮点运算
n = 10000
out(flops=f"{2 * n ** 3 / 3 / 1e11:.1f}\\times10^{{11}}", sec=f"{2 * n ** 3 / 3 / 1e11:.1f}")


def solve_counting(A, b):
    """真正做一遍不选主元的消元与回代（浮点数），每做一次运算计数一次。"""
    A = [list(map(float, r)) for r in A]
    b = list(map(float, b))
    n, mul, add = len(A), 0, 0
    for k in range(n - 1):
        for i in range(k + 1, n):
            l = A[i][k] / A[k][k]; mul += 1
            for j in range(k + 1, n):
                A[i][j] -= l * A[k][j]; mul += 1; add += 1
            b[i] -= l * b[k]; mul += 1; add += 1
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = b[i]
        for j in range(i + 1, n):
            s -= A[i][j] * x[j]; mul += 1; add += 1
        x[i] = s / A[i][i]; mul += 1
    return x, mul, add


import numpy as np

rng = np.random.default_rng(38)
ok = True
for n in (2, 3, 10, 40):
    A = rng.standard_normal((n, n)) + n * np.eye(n)
    b = rng.standard_normal(n)
    x, m, a = solve_counting(A, b)
    ok = ok and (m, a) == count_ops(n) and np.allclose(A @ np.array(x), b)
out(real_ok=bool(ok))
