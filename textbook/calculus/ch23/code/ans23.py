"""第 23 章部分习题答案中的数值。"""
import math

from bookout import out

g = 9.81
# 23.1.4：总时间 ≤ 0.5 s（h = 0.2 m）的恢复系数上限；h = 0.1 m、e = 0.6 的总时间
t0 = math.sqrt(2 * 0.2 / g)
c = 0.5 / t0
out(e2314_emax=(c - 1) / (c + 1), e2314_T=math.sqrt(2 * 0.1 / g) * 1.6 / 0.4)
# 23.1.5：修正量按 0.7 倍缩小，当前修正 1e-3：剩余 ≈ 1e-3·0.7/0.3；还需多少步使剩余 < 1e-6
k = 0
while 1e-3 * 0.7 ** (k + 1) / 0.3 >= 1e-6:
    k += 1
out(e2315_rem=1e-3 * 0.7 / 0.3, e2315_k=k)
# 23.2.4
out(e2324=math.fsum(1 / j for j in range(1001, 2001)), e2324_est=math.log(2) - 1 / 4000)
# 23.2.5：每层错开理论值的一半
out(e2325=sum(1 / (2 * j) for j in range(1, 11)) / 2)
# 23.3.3：Σ1/k³，n = 10 的上下界
S10 = math.fsum(1 / j ** 3 for j in range(1, 11))
out(e2333_lo=S10 + 1 / (2 * 11 ** 2), e2333_hi=S10 + 1 / (2 * 10 ** 2), e2333_true=1.2020569031595942)
# 23.3.4：k^10/2^k 从第几项起减小
k = 1
while (k + 1) ** 10 / 2 ** (k + 1) >= k ** 10 / 2 ** k:
    k += 1
out(e2334_peak=k)
# 23.4.3：cos 在 |x| ≤ π/4 的项数（1 − x²/2 + …，m 项，误差 ≤ x^{2m}/(2m)!）
x = math.pi / 4
m = 1
while x ** (2 * m) / math.factorial(2 * m) >= 2 ** -24:
    m += 1
out(e2343_m=m, e2343_bound=x ** (2 * m) / math.factorial(2 * m))
# 23.4.6
out(e2346=0.05 ** 3 / 6)
# 23.6.1：Σ1/k!，前 n 项（k = 0..n−1）的余项 ≤ 1/n! · 1/(1 − 1/(n+1))
n = 1
while 1 / math.factorial(n) * (n + 1) / n >= 1e-10:
    n += 1
out(e2361_n=n)
# 23.6.3：ln 2 的前 10 个部分和反复艾特肯加速
S, s = 0.0, []
for j in range(1, 11):
    S += (-1) ** (j + 1) / j
    s.append(S)
while len(s) >= 3:
    s = [s[i + 2] - (s[i + 2] - s[i + 1]) ** 2 / ((s[i + 2] - s[i + 1]) - (s[i + 1] - s[i])) for i in range(len(s) - 2)]
out(e2363_err=abs(s[-1] - math.log(2)))
