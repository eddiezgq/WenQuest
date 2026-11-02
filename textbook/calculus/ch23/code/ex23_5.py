"""23.5 节：级数的重排。
(1) 1 + 1/3 − 1/2 + 1/5 + 1/7 − 1/4 + …（两正一负）的和是 (3/2) ln 2，与原来的 ln 2 不同；
(2) 黎曼重排定理的构造：贪心地取正项、负项，使部分和趋于指定的数（π、−1）；正负项数之比与公式 e^{2(T − ln 2)} 比较；
(3) 绝对收敛的级数重排后和不变；
(4) 浮点数的加法不满足结合律：单精度下 Σ1/k² 从大到小加与从小到大加的结果不同。"""
import math

import numpy as np

from bookout import out

# (1) 两正一负
N = 10 ** 6
s, p, q = 0.0, 1, 2                                  # 下一个奇数分母、下一个偶数分母
for _ in range(N):
    s += 1 / p; p += 2
    s += 1 / p; p += 2
    s -= 1 / q; q += 2
out(r21_sum=s, r21_formula=1.5 * math.log(2), r21_blocks=N, ln2=math.log(2))


# (2) 贪心重排
def greedy(target, n_terms):
    s, p, q, npos, nneg = 0.0, 1, 2, 0, 0
    for _ in range(n_terms):
        if s <= target:
            s += 1 / p; p += 2; npos += 1
        else:
            s -= 1 / q; q += 2; nneg += 1
    return s, npos, nneg


for name, T in (("pi", math.pi), ("m1", -1.0)):
    s, a, b = greedy(T, 2 * 10 ** 6)
    out(**{f"gr_{name}_sum": s, f"gr_{name}_pos": a, f"gr_{name}_neg": b, f"gr_{name}_ratio": a / b,
           f"gr_{name}_formula": math.exp(2 * (T - math.log(2)))})
# (3) 绝对收敛：Σ(−1)^{k+1}/k² 两正一负重排
s, p, q = 0.0, 1, 2
for _ in range(N):
    s += 1 / p ** 2; p += 2
    s += 1 / p ** 2; p += 2
    s -= 1 / q ** 2; q += 2
# 还没用到的项：大于 4N 的奇数项（正）与大于 2N 的偶数项（负），各算到 10⁷ 再加积分估计的尾巴
M = 10 ** 7
pos_tail = math.fsum(1 / p ** 2 for p in range(4 * N + 1, 2 * M, 2)) + 1 / (2 * (2 * M))
neg_tail = math.fsum(1 / q ** 2 for q in range(2 * N + 2, 2 * M, 2)) + 1 / (2 * (2 * M))
corr = s + pos_tail - neg_tail
out(ab_sum=s, ab_true=math.pi ** 2 / 12, ab_corr=corr, ab_diff=abs(corr - math.pi ** 2 / 12))
# (4) 浮点求和的顺序
n = 10 ** 6
k = np.arange(1, n + 1, dtype=np.float64)
t32 = (1.0 / k ** 2).astype(np.float32)
fw = np.float32(0.0)
for v in t32:
    fw = np.float32(fw + v)
bw = np.float32(0.0)
for v in t32[::-1]:
    bw = np.float32(bw + v)
exact = math.fsum(1.0 / k ** 2)
out(fp_fw=float(fw), fp_bw=float(bw), fp_exact=exact, fp_err_fw=abs(float(fw) - exact), fp_err_bw=abs(float(bw) - exact))
