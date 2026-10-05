"""10.6 节：最大值与最小值——腕心距离对肘关节角最敏感的姿态（|r′| 的最大值恰为 l₂）；
网格搜索与在网格最优点附近用牛顿法细化的比较（2.3 节）；障碍物到五次多项式换道路径的最近点。"""
import math

from _path import lane
from _traj import ur5e_links
from bookout import out

l1, l2 = ur5e_links()
r = lambda t: math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(t))
dr = lambda t: -l1 * l2 * math.sin(t) / r(t)
ts = math.acos(-l2 / l1)
out(t_star_deg=math.degrees(ts), dr_star=abs(dr(ts)) * 1000, l2_mm=l2 * 1000)

# 7.3 节的功率 P(t) = Iαω（这里取 I = 1 kg·m²，最大值点与 I 无关；五次多项式，T = 2 s，Δ = 90°）：网格与细化
T, D = 2.0, math.pi / 2
P = lambda t: (D / T ** 2 * 60 * (t / T) * (1 - t / T) * (1 - 2 * t / T)) * (D / T * 30 * (t / T) ** 2 * (1 - t / T) ** 2)
s_star = 0.5 - math.sqrt(7) / 14
t_true = s_star * T
rows = []
for n in (11, 101, 1001):
    grid = [T * k / (n - 1) for k in range(n)]
    tg = max(grid, key=P)
    h = 1e-5
    dP = lambda t: (P(t + h) - P(t - h)) / (2 * h)
    ddP = lambda t: (P(t + h) - 2 * P(t) + P(t - h)) / h ** 2
    tn = tg
    for _ in range(4):
        tn -= dP(tn) / ddP(tn)
    rows.append(f"| {n} | {tg:.4f} | {abs(tg - t_true):.1e} | {tn:.8f} | {abs(tn - t_true):.1e} |")
out(grid_tab="\n".join(rows), t_true=t_true, P_max=P(t_true))

# 障碍物 (2.2, 0.75) 到五次多项式换道路径（d = 1、L = 4）的最近距离：令 D(x) = (x − a)² + (y − b)² 的导数为零
y, yp, ypp = lane("quintic", 1.0, 4.0)
ax_, by_ = 2.2, 0.75
Dp = lambda x: 2 * (x - ax_) + 2 * (y(x) - by_) * yp(x)
Dpp = lambda x: 2 + 2 * yp(x) ** 2 + 2 * (y(x) - by_) * ypp(x)
x = ax_
for _ in range(30):
    x -= Dp(x) / Dpp(x)
dist = math.hypot(x - ax_, y(x) - by_)
grid_min = min(math.hypot(4 * k / 4000 - ax_, y(4 * k / 4000) - by_) for k in range(4001))
out(obs_x=x, obs_y=y(x), obs_d=dist, obs_grid=grid_min, obs_Dpp=Dpp(x))
