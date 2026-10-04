"""6.5 节：有限覆盖——机械臂沿轨迹运动时，每个时刻 t 都有一个“安全邻域”（半径 d(t)/K），无穷多个邻域盖住 [0, 1]；
从中挑出有限个就够了。对比：开区间 (0, 1) 被 (1/n, 1) 覆盖，却挑不出有限个。"""
import math

from _traj import K, clearance
from bookout import out

out(K=K, dmin=min(clearance(k / 10 ** 5) for k in range(10 ** 5 + 1)))

# 贪心：从 t = 0 出发，每次走到当前安全邻域的 0.9 倍半径处
t, centers = 0.0, []
while True:
    r = clearance(t) / K
    centers.append((t, r))
    if t + r > 1:
        break
    t += 0.9 * r
out(n_cover=len(centers), r_min=min(r for _, r in centers), r_max=max(r for _, r in centers))
out(cover_tab="\n".join(f"| {k + 1} | {c:.4f} | {r:.4f} |" for k, (c, r) in enumerate(centers[:6])))
# 均匀网格：步长要不超过最小的安全半径的两倍
dmin = min(clearance(k / 10 ** 5) for k in range(10 ** 5 + 1))
out(n_uniform=math.ceil(1 / (2 * dmin / K)))

# (0, 1) 被 {(1/n, 1)} 覆盖：前 N 个只盖住 (1/N, 1)
out(open_left=1 / 1000)
