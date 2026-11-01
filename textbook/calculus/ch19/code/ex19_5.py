"""19.5 节：可化简的方程。水面机器人渡河（船头始终对准码头）：齐次方程的解、最大下漂距离与到达时间；
无人机减速滑行（14.4 节）：伯努利方程的解 v(t) 与滑行距离；UR5e 上臂松开制动后自由下摆：全微分方程（能量积分）。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

# 渡河：码头在原点，船从 (a, 0) 出发，水流沿 +y，船速 s，水速 w，k = w/s
a, sp, wv = 50.0, 2.0, 1.0
k = wv / sp
y = lambda x: a / 2 * ((x / a) ** (1 - k) - (x / a) ** (1 + k))
xm = a * ((1 - k) / (1 + k)) ** (1 / (2 * k))
out(bt_a=a, bt_s=sp, bt_w=wv, bt_k=k, bt_xm=xm, bt_ym=y(xm), bt_T=a * sp / (sp * sp - wv * wv), bt_T0=a / sp)


def boat(t, z):
    x, yy = z
    r = math.hypot(x, yy)
    return [-sp * x / r, -sp * yy / r + wv]


ev = lambda t, z: math.hypot(*z) - 1e-3
ev.terminal = True
s = solve_ivp(boat, (0, 100), [a, 0.0], rtol=1e-10, atol=1e-10, events=ev, dense_output=True)
ts = np.linspace(0, s.t_events[0][0], 4001)
Z = s.sol(ts)
out(bt_T_num=float(s.t_events[0][0]), bt_ym_num=float(Z[1].max()),
    bt_check=float(np.max(np.abs(Z[1][Z[0] > 0.5] - y(Z[0][Z[0] > 0.5])))))
# k = 1：水速等于船速，到不了码头，最终停在码头下游 a/2 处
out(bt_k1_lim=a / 2)

# 无人机：m v′ = −(c1 v + c2 v²)，伯努利方程，z = 1/v
m, c1, c2, v0 = 1.5, 0.3, 0.05, 10.0
v = lambda t: c1 * v0 * math.exp(-c1 * t / m) / (c1 + c2 * v0 * (1 - math.exp(-c1 * t / m)))
xdist = lambda t: m / c2 * math.log(1 + c2 * v0 / c1 * (1 - math.exp(-c1 * t / m)))
t1 = m / c1 * math.log(v0 * (c1 + c2 * 1.0) / (1.0 * (c1 + c2 * v0)))    # 减到 1 m/s 的时间（14.4 节）
out(dr_v2=v(2.0), dr_t1=t1, dr_v_t1=v(t1), dr_x1=xdist(t1), dr_xinf=m / c2 * math.log(1 + c2 * v0 / c1))
s = solve_ivp(lambda t, z: [z[1], -(c1 * z[1] + c2 * z[1] ** 2) / m], (0, t1), [0, v0], rtol=1e-10, atol=1e-12)
out(dr_x1_num=float(s.y[0, -1]))

# UR5e 上臂从水平位置松开制动，自由下摆（不计摩擦）：I ω²/2 − m g d sin θ = 0
g, mu, d, I_arm = 9.81, 8.393, 0.2125, 0.5129
I_rot = 137e-7 * 101 ** 2                       # 19.4 节：RE 40 转子经减速比 101 折算到关节
out(sw_m=mu, sw_d=d, sw_I=I_arm, sw_w=math.sqrt(2 * mu * g * d / I_arm), sw_w_rot=math.sqrt(2 * mu * g * d / (I_arm + I_rot)), sw_I_rot=I_rot, sw_I_tot=I_arm + I_rot,
    sw_v_tip=math.sqrt(2 * mu * g * d / I_arm) * 0.425)
