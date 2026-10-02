"""7.9 节：云台相机跟踪沿直线行驶的 AGV；梯子下滑（算例 7.9.1）。"""
import math

from bookout import out

# 算例 7.9.2：相机在 AGV 路线旁 d = 2 m 处，AGV 以 v = 1.5 m/s 匀速行驶；θ = arctan(x/d)
d, v = 2.0, 1.5
w_max = v / d
w_at = lambda x: v * d / (d**2 + x**2)
lim = 0.5                                  # 云台水平转动的最大角速度 rad/s
x_star = math.sqrt(v * d / lim - d**2)
out(w_max=w_max, w_max_deg=math.degrees(w_max), w_at3=w_at(3.0), lim=lim, lim_deg=math.degrees(lim), x_star=x_star, t_lost=2 * x_star / v,
    d_need=v / lim)

# 算例 7.9.1：梯子长 5 m，下端以 0.5 m/s 离墙滑开，下端离墙 3 m 时上端下滑的速度
L, xb, vb = 5.0, 3.0, 0.5
yb = math.sqrt(L**2 - xb**2)
out(ladder_y=yb, ladder_v=xb * vb / yb)
