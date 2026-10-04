"""3.4 节：收敛数列的性质与运算——一阶低通滤波的输出数列；“先设极限存在”的陷阱；
√(n+1) − √n 的两种算法；有理分式数列。"""
import math

import numpy as np

from bookout import out

# 一阶数字低通滤波：y_k = α y_{k−1} + (1 − α) x，输入为常数 x = 5（V），α = 0.9，y_0 = 0
alpha, x = 0.9, 5.0
y = [0.0]
for _ in range(200):
    y.append(alpha * y[-1] + (1 - alpha) * x)
out(alpha=alpha, xin=x, y10=y[10], y50=y[50], y200=y[200])
# 误差 x − y_k = α^k (x − y_0)
assert all(abs((x - y[k]) - alpha**k * x) < 1e-12 for k in range(201))
k1 = next(k for k in range(201) if abs(x - y[k]) < 0.01 * x)
out(k1pct=k1)

# 陷阱：a_{n+1} = 2 a_n，a_1 = 1。若“设极限为 L”，得 L = 2L，L = 0，但数列是 1, 2, 4, …
a = [1]
for _ in range(9):
    a.append(2 * a[-1])
out(dbl="、".join(map(str, a[:6])))

# √(n+1) − √n：直接相减与有理化 1/(√(n+1) + √n)
for k in (4, 8, 12, 16):
    n = 10.0**k
    out(**{f"d{k}": math.sqrt(n + 1) - math.sqrt(n), f"r{k}": 1 / (math.sqrt(n + 1) + math.sqrt(n))})

n = 1e12
out(rel12=abs((math.sqrt(n + 1) - math.sqrt(n)) * (math.sqrt(n + 1) + math.sqrt(n)) - 1))

# 有理分式：(3n² − 2n + 1)/(5n² + 4) → 3/5
f = lambda n: (3 * n * n - 2 * n + 1) / (5 * n * n + 4)
out(f10=f(10), f1000=f(1000))
# n 项之和：每项 1/n → 0，但 n 个 1/n 之和是 1
out(sum_n=sum(1 / 1000 for _ in range(1000)))
