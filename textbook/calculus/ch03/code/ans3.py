"""本章“部分习题答案”中的数值。"""
import math

import numpy as np

from bookout import out

# 习题 3.1.5：√10 的迭代步数（10 位有效数字）
r = math.sqrt(10)
def steps(x):
    for k in range(1, 100):
        x = (x + 10 / x) / 2
        if abs(x - r) < 1e-10 * r:
            return k
out(e315_10=steps(10.0), e315_1=steps(1.0), e315_100=steps(100.0))

# 习题 3.1.8：一小时 180000 次累加
out(e318_n=3600 * 50, e318_mm=0.05 * 3600 * 50)

# 习题 3.2.3：r = 0.98 的调节时间
k = np.arange(0, 3001)
e = 10 * 0.98**k * np.cos(0.03 * k)
out(e323=int(np.nonzero(np.abs(e) >= 0.2)[0][-1]) + 1, e323_est=math.log(0.02) / math.log(0.98))

# 习题 3.2.6：n^100 / 1.01^n 从哪一项起开始减小：(1 + 1/n)^100 < 1.01
n = next(n for n in range(1, 10**6) if 100 * math.log1p(1 / n) < math.log(1.01))
out(e326=n)

# 习题 3.3.7：ln n / n 的最小 N（n > N 时 < ε）；数列在 n = 3 后单调减
for k, eps in ((1, 0.1), (2, 0.01), (3, 0.001)):
    n = 3
    while math.log(n) / n >= eps:
        n += 1
    out(**{f"e337_{k}": n - 1})

# 习题 3.3.9：包络 10·0.99^k < 0.1 与实际调节时间（±0.1° 带）
kk = np.arange(0, 3001)
ee = 10 * 0.99**kk * np.cos(0.03 * kk)
env = math.log(0.01) / math.log(0.99)
out(e339_env=env, e339_N=math.floor(env), e339_true=int(np.nonzero(np.abs(ee) >= 0.1)[0][-1]) + 1)

# 习题 3.4.7
out(e347=0.05 ** (1 / 20))

# 习题 3.5.9：(3.1.1) 求距离 d = √a，x₁ = 0.5，达到 10^(−9) m 所需步数随 d 的变化
def steps_for(d):
    a, z = d * d, 0.5
    for s in range(1, 200):
        z = (z + a / z) / 2
        if abs(z - d) < 1e-9:
            return s
out(e359_1cm=steps_for(0.01), e359_1mm=steps_for(0.001), e359_far=steps_for(1.2))

# 习题 3.6.6：每分钟温差减少 4%
out(e366_disc=math.log(0.5) / math.log(0.96), e366_cont=math.log(2) / 0.04)

# 习题 3.6.7：τ = 20 ms，100 ms 时达到稳态的百分之几
for Ts in (1, 10, 25, 50):
    n = 100 // Ts
    out(**{f"e367_{Ts}": 100 * (1 - (1 - Ts / 20) ** n)})
out(e367_exact=100 * (1 - math.exp(-5)))

# 习题 3.7.6：100! 的位数
st = 0.5 * math.log10(2 * math.pi * 100) + 100 * math.log10(100 / math.e)
out(e376_st=st, e376_digits=len(str(math.factorial(100))))

# 习题 3.7.7：0.1 s × 10^9 次/s = 10^8 次
budget = 1e8
n1 = max(n for n in range(2, 100000) if n * n * math.log2(n) <= budget)
n2 = max(n for n in range(2, 200) if 1.5**n <= budget)
out(e377_a=n1, e377_b=n2)
