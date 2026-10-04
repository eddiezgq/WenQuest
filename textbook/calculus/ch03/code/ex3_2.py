"""3.2 节：数列极限的直观意义——几个典型数列的前若干项；“越来越接近”不等于“趋于”；
关节阶跃响应的误差数列与 2% 调节带（示意模型）。"""
import math

import numpy as np

from bookout import out

n = np.arange(1, 10001)
seqs = {"inv": 1 / n, "alt": (-1.0) ** n / n, "frac": (n + 1) / n, "sgn": (-1.0) ** n, "sinn": np.sin(n)}
out(inv1000=float(seqs["inv"][999]), alt1001=float(seqs["alt"][1000]), frac1000=float(seqs["frac"][999]))
# sin n 的前 10000 项：在 [−1, 1] 中到处都有，不聚向任何一个数
h, _ = np.histogram(seqs["sinn"], bins=10, range=(-1, 1))
out(sin_min_bin=int(h.min()), sin_max_bin=int(h.max()))

# 关节阶跃响应（示意模型）：目标转角 10°，控制周期 1 ms，误差 e_k = 10° · r^k cos(ωk)，r = 0.99，ω = 0.03 rad
r, w, e0 = 0.99, 0.03, 10.0
k = np.arange(0, 3001)
e = e0 * r**k * np.cos(w * k)
band = 0.02 * e0
outside = np.nonzero(np.abs(e) >= band)[0]
N = int(outside[-1]) + 1                                  # 从第 N 步起永远留在带内
first_in = int(np.nonzero(np.abs(e) < band)[0][0])        # 第一次进入带内
out(r=r, w=w, e0=e0, band=band, N_settle=N, first_in=first_in, e_first_in=float(e[first_in]),
    overshoot=float(-e.min()), t_settle_ms=N)
# 带宽更窄（0.5%）时
band2 = 0.005 * e0
N2 = int(np.nonzero(np.abs(e) >= band2)[0][-1]) + 1
out(band2=band2, N_settle2=N2)

# n^(1/n) 的前几项与 n = 10^6 处的值；ln ln n 在 n = 10^100 处的值
out(nroot5="、".join(f"{k ** (1 / k):.3f}" for k in range(1, 6)), nroot_1e6=1e6 ** 1e-6, lnln=math.log(100 * math.log(10)))
# sin n 的前四项
out(sin4="、".join(f"{math.sin(k):.2f}" for k in range(1, 5)))
