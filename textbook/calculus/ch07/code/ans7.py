"""本章“部分习题答案”中的数值。"""
import math

import numpy as np

from _traj import quintic, ur5e_links
from bookout import out

# 习题 7.1.6：θ = 0.5(1 − cos πt)，ω = 0.5π sin πt
out(e716_a=0.5 * math.pi * math.sin(math.pi * 0.25), e716_b=0.5 * math.pi)

# 习题 7.4.7：120 = 280(1 − e^(−0.02/τ))
tau = 0.02 / math.log(280 / (280 - 120))
out(e747_tau=tau, e747_a=280 / tau)

# 习题 7.5.6：肘关节中心以 0.5 m/s 上升所需的电机转速（r/min）
l1, _ = ur5e_links()
rpm = lambda th: 0.5 / (l1 * math.cos(math.radians(th))) * 101 * 60 / (2 * math.pi)
out(e756_30=rpm(30), e756_60=rpm(60), e756_85=rpm(85))

# 习题 7.8.7：限速 π rad/s、限角加速度 5 rad/s²，转过 90° 的最短时间
D, w, a = math.pi / 2, math.pi, 5.0
T_cub = max(1.5 * D / w, math.sqrt(6 * D / a))
ta = math.sqrt(D / a)                      # 三角形速度（无匀速段）
assert a * ta <= w
out(e787_cub=T_cub, e787_tra=2 * ta, e787_peak=a * ta)

# 习题 7.8.8：20 位编码器
T, Ts = 2.0, 0.001
tk = np.arange(0, T + Ts / 2, Ts)
res = {}
for bits in (17, 20):
    q = 2 * math.pi / 2**bits
    thk = np.round(quintic(tk, T, D)[0] / q) * q
    for k in (1, 5, 20):
        h = k * Ts
        est = (thk[2 * k:] - 2 * thk[k:-k] + thk[:-2 * k]) / h**2
        res[(bits, k)] = float(np.sqrt(np.mean((est - quintic(tk, T, D)[2][k:-k]) ** 2)))
out(e788_1=res[(20, 1)], e788_5=res[(20, 5)], e788_20=res[(20, 20)],
    e788_r1=res[(17, 1)] / res[(20, 1)], e788_r5=res[(17, 5)] / res[(20, 5)], e788_r20=res[(17, 20)] / res[(20, 20)])

# 习题 7.9.2、7.9.4
out(e792=1.5 * 4 / (math.pi * 9), e794_ang=6 * 800 / 100 / 3600)

# 习题 7.5.6：θ = 85° 时所需的关节角速度（°/s）
out(e756_85deg=math.degrees(0.5 / (l1 * math.cos(math.radians(85)))))
