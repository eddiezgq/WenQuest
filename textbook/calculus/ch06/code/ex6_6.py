"""6.6 节：闭区间上连续函数性质的应用——用有限次采样“证明”整段轨迹安全：
d(t) 的利普希茨常数为 K，若在中点处 d(m) − s > K·(区间长)/2，则整个区间上 d > s。
等距采样会漏掉窄的危险窗口；自适应二分检查要么给出安全证明，要么找到碰撞时刻。"""
import math

import numpy as np

from _traj import K, OBS, clearance
from bookout import out

s = 0.05                                   # 安全距离 / m
OBS2 = (0.176, 0.634)                      # 第二个障碍：离轨迹更近
out(s_mm=s * 1000, K=K)

for name, o in (("a", OBS), ("b", OBS2)):
    g = lambda t: clearance(t, o) - s
    grid = [g(k / 10) for k in range(11)]
    out(**{f"grid_{name}": min(grid) * 1000})                     # 等距 11 点的最小裕量 / mm
    tt = np.linspace(0, 1, 200001)
    dd = np.array([g(x) for x in tt])
    out(**{f"true_{name}": float(dd.min()) * 1000, f"tmin_{name}": float(tt[dd.argmin()])})
    # 自适应二分检查
    stack, evals, hit, leaves = [(0.0, 1.0)], 0, None, 0
    while stack and hit is None:
        a, b = stack.pop()
        m = (a + b) / 2
        gm = g(m)
        evals += 1
        if gm <= 0:
            hit = m
        elif gm > K * (b - a) / 2:
            leaves += 1
        else:
            stack += [(m, b), (a, m)]
    out(**{f"evals_{name}": evals, f"leaves_{name}": leaves, f"hit_{name}": hit if hit is not None else -1})
    # 等距采样的保守证明需要的点数：步长 h，要求每个采样点的裕量 > K h / 2
    gmin = float(dd.min())
    if gmin > 0:
        out(**{f"h_need_{name}": 2 * gmin / K, f"n_need_{name}": math.ceil(K / (2 * gmin)), f"n_need_{name}1": math.ceil(K / (2 * gmin)) + 1})
