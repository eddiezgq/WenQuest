"""12.5 节：净变化与平均值——AGV 一次搬运的能耗 E = ∫P dt、平均功率、平均速度；电池能跑几趟；
五次多项式关节运动的均方根角加速度；往返运动的位移与路程。"""
import math

from _agv import DIST, M, MU, P0, T, power, v
from bookout import out

n = 200000
h = T / n
E = sum(power((k + 0.5) * h) for k in range(n)) * h            # J，中点和
out(T=T, E_J=E, E_Wh=E / 3600, P_avg=E / T, v_avg=DIST / T, m=M, P0=P0,
    P_peak=max(power(k * h) for k in range(n + 1)), trips=24 * 40 * 0.8 * 3600 / E)
# 五次多项式：α = (Δ/T²)·60 s(1 − s)(1 − 2s)，T = 2 s，Δ = π/2
Tq, D = 2.0, math.pi / 2
al = lambda t: D / Tq ** 2 * 60 * (t / Tq) * (1 - t / Tq) * (1 - 2 * t / Tq)
hq = Tq / n
ms = sum(al((k + 0.5) * hq) ** 2 for k in range(n)) * hq / Tq
mabs = sum(abs(al((k + 0.5) * hq)) for k in range(n)) * hq / Tq
out(rms_q=math.sqrt(ms), mabs_q=mabs)
# 往返：x(t) = t³ − 6t² + 9t（11.2 节），0 ≤ t ≤ 4：位移 ∫v，路程 ∫|v|
vv = lambda t: 3 * t * t - 12 * t + 9
h4 = 4 / n
out(disp=sum(vv((k + 0.5) * h4) for k in range(n)) * h4, dist=sum(abs(vv((k + 0.5) * h4)) for k in range(n)) * h4)
