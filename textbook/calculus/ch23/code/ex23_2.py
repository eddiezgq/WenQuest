"""23.2 节：收敛级数的性质；调和级数。H_n 与 ln n + γ；H_n 超过 10、20 所需的项数；
砖块（或机械臂码放的箱子）悬挑：n 块最多伸出 H_n/2 个块长；单精度累加调和级数会在何处停住不动。"""
import math

import numpy as np

from bookout import out

gamma = 0.5772156649015329
rows = []
for n in (10, 100, 1000, 10 ** 4, 10 ** 6):
    H = math.fsum(1 / k for k in range(1, n + 1))
    rows.append(f"| {n} | {H:.6f} | {math.log(n):.6f} | {H - math.log(n):.6f} | {H - math.log(n) - gamma:.2e} |")
out(h_tab="\n".join(rows), h_gamma=gamma)
# H_n > M 的最少项数：n ≈ e^{M − γ}
for M in (10, 20, 100):
    out(**{f"h_n{M}": math.exp(M - gamma)})
H, n = 0.0, 0
while H <= 10:
    n += 1
    H += 1 / n
out(h_n10_exact=n)
# 悬挑：n 块砖，最多伸出 H_n / 2 块长；伸出 1、2、3 块长各需要几块
need = {}
H, k = 0.0, 0
for target in (1, 2, 3):
    while H / 2 <= target:
        k += 1
        H += 1 / k
    need[target] = k
out(st_n1=need[1], st_n2=need[2], st_n3=need[3], st_over4=sum(1 / k for k in range(1, 5)) / 2,
    st_over10=sum(1 / k for k in range(1, 11)) / 2)
# 单精度累加：加上 1/n 已不改变和的时候
s = np.float32(0.0)
n = 0
while True:
    n += 1
    t = np.float32(s + np.float32(1.0 / n))
    if t == s:
        break
    s = t
out(f32_n=n, f32_sum=float(s), f32_true=math.log(n) + gamma)
