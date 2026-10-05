"""第 12 章部分习题答案中的数值。"""
import math

from _agv import G, M, MU, ETA, P0, T, acc, v
from bookout import out

# 12.1.1：√x 在 [0, 4] 上，n = 4
xs = [0, 1, 2, 3, 4]
out(e1211_L=sum(math.sqrt(x) for x in xs[:-1]), e1211_R=sum(math.sqrt(x) for x in xs[1:]))
# 12.1.2：1/x 在 [1, 2] 上，n = 5
pts = [1 + 0.2 * k for k in range(6)]
out(e1212_L=sum(0.2 / x for x in pts[:-1]), e1212_R=sum(0.2 / x for x in pts[1:]))
# 12.4.3：sin x / x 在 [0, π/2] 上的改进下界与数值
b = math.pi / 2
n = 200000
h = b / n
si = sum(math.sin((k + 0.5) * h) / ((k + 0.5) * h) for k in range(n)) * h
out(e1243_lo=b - b ** 3 / 18, e1243_hi=b, e1243_val=si)
# 12.5.3：减速时回收 60% 的机械能


def p_regen(t):
    mech = (M * acc(t) + MU * M * G) * v(t)
    return (mech / ETA if mech >= 0 else 0.6 * mech) + P0


h = T / n
E0 = sum(max((M * acc((k + 0.5) * h) + MU * M * G) * v((k + 0.5) * h), 0) / ETA + P0 for k in range(n)) * h
E1 = sum(p_regen((k + 0.5) * h) for k in range(n)) * h
out(e1253_E=E1, e1253_pct=(E0 - E1) / E0 * 100)
# 12.5.7：运动 2 s + 静止 1 s 的均方根
Tq, D = 2.0, math.pi / 2
al = lambda t: D / Tq ** 2 * 60 * (t / Tq) * (1 - t / Tq) * (1 - 2 * t / Tq)
hq = Tq / n
ms = sum(al((k + 0.5) * hq) ** 2 for k in range(n)) * hq
out(e1257=math.sqrt(ms / 3))
