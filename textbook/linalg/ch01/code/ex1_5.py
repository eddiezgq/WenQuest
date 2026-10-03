"""1.5 节：用程序检验数学归纳法证明的结论（检验不能代替证明），以及用随机试验找反例。"""
import numpy as np

from bookout import out

# 命题：对一切正整数 n，[[1, 1], [0, 1]]ⁿ = [[1, n], [0, 1]]
S = np.array([[1, 1], [0, 1]])
ok = all(np.array_equal(np.linalg.matrix_power(S, n), np.array([[1, n], [0, 1]])) for n in range(1, 101))
# 命题（假）：对一切 2×2 矩阵，AB = BA。随机找一个反例
rng = np.random.default_rng(15)
for k in range(1, 1000):
    A = rng.integers(-2, 3, (2, 2))
    B = rng.integers(-2, 3, (2, 2))
    if not np.array_equal(A @ B, B @ A):
        break
out(ind_ok=ok, ind_n=100, trial=k, A=str(A.tolist()), B=str(B.tolist()), AB=str((A @ B).tolist()), BA=str((B @ A).tolist()))

# 欧拉的例子：n² + n + 41 对 n = 0, 1, …, 39 都是质数，n = 40 时不是
def is_prime(k):
    return k > 1 and all(k % p for p in range(2, int(k ** 0.5) + 1))


first_bad = next(n for n in range(1000) if not is_prime(n * n + n + 41))
out(euler_n=first_bad, euler_v=first_bad ** 2 + first_bad + 41, euler_sqrt=int(round((first_bad ** 2 + first_bad + 41) ** 0.5)))
