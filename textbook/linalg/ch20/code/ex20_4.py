"""20.4 节：浮点数与舍入误差。IEEE 754 的半精度、单精度、双精度（以及 bfloat16）的参数；0.1 实际存的是什么；
机器人控制器用单精度累加时钟（每 1 ms 加 0.001 s）会在几小时后变快、停走；24 位定点数存 0.1 的截断误差累积
（1991 年爱国者导弹事故）；一百万个 0.001 的求和：逐个相加、补偿求和（卡亨）、成对求和；相减抵消。"""
import math
from decimal import Decimal

import numpy as np

from _num import sci
from bookout import out

# (1) 三种格式的参数
rows = []
for name, t in (("half", np.float16), ("single", np.float32), ("double", np.float64)):
    fi = np.finfo(t)
    out(**{f"eps_{name}": sci(float(fi.eps), 2), f"max_{name}": sci(float(fi.max), 2), f"tiny_{name}": sci(float(fi.smallest_normal), 2),
           f"dig_{name}": float(-math.log10(float(fi.eps) / 2)), f"mant_{name}": int(fi.nmant) + 1})
# bfloat16：8 位指数（与单精度相同）、8 位有效位（含隐含的一位）
out(eps_bf=sci(2.0 ** -7, 2), max_bf=sci((2 - 2.0 ** -7) * 2.0 ** 127, 2), tiny_bf=sci(2.0 ** -126, 2), dig_bf=float(-math.log10(2.0 ** -8)))

# (2) 0.1 实际存的值
d01 = Decimal(0.1)
s01 = Decimal(float(np.float32(0.1)))
out(d01=str(d01)[:30], s01=str(s01)[:20], hex01=(0.1).hex(), err01=sci(float(d01 - Decimal("0.1")), 1), err01s=sci(float(s01 - Decimal("0.1")), 1),
    sum3=repr(0.1 + 0.2))

# (3) 单精度时钟：每 1 ms 加 0.001。同一个二进制数量级 [2ᵉ, 2ᵉ⁺¹) 内，相邻浮点数的间距 ulp 不变，每次实际加上的是 round(0.001/ulp)·ulp
dt32 = float(np.float32(0.001))


def inc_in_binade(e):
    ulp = 2.0 ** (e - 23)
    return round(dt32 / ulp) * ulp


# 先用逐步相加核对前 20 s
t = np.float32(0.0)
for _ in range(20000):
    t = np.float32(t + np.float32(0.001))
t20 = float(t)
# 再按数量级“跳着”算：真实时间（步数 × 1 ms）与时钟读数
clock, steps, table = 0.0, 0, []
e = -10
while True:
    while 2.0 ** (e + 1) <= clock:
        e += 1
    inc = inc_in_binade(e) if clock >= 2.0 ** e else None
    if clock < 1.0:                     # 前 1 秒逐步相加
        c = np.float32(clock)
        c = np.float32(c + np.float32(0.001))
        clock = float(c); steps += 1
        continue
    if inc == 0:
        break
    n = math.ceil((2.0 ** (e + 1) - clock) / inc)
    table.append((e, inc, steps * 1e-3, clock))
    clock += n * inc; steps += n
stall_clock, stall_real = clock, steps * 1e-3
for e_, inc_, real_, clock_ in table:
    if e_ == 13:
        out(r13=real_ / 3600, inc13=1000 * inc_)
    if e_ == 14:
        out(r14=real_ / 3600, inc14=1000 * inc_, c14=clock_)
out(t20=t20, err20=sci(abs(t20 - 20.0), 1), stall_clock=stall_clock, stall_h=stall_real / 3600, stall_ch=stall_clock / 3600)
# 1 小时、4 小时时的读数误差
def clock_at(real_s):
    clock, steps, e = 0.0, 0, -10
    target = round(real_s * 1000)
    while steps < target:
        while 2.0 ** (e + 1) <= clock:
            e += 1
        if clock < 1.0:
            clock = float(np.float32(np.float32(clock) + np.float32(0.001))); steps += 1; continue
        inc = inc_in_binade(e)
        if inc == 0:
            return clock
        n = min(math.ceil((2.0 ** (e + 1) - clock) / inc), target - steps)
        clock += n * inc; steps += n
    return clock


e1, e4 = clock_at(3600) - 3600, clock_at(4 * 3600) - 4 * 3600
out(err1h=e1, err4h=e4, slow1h=-e1, slow4h=-e4, rate_slow=100 * (1 - inc_in_binade(12) / dt32))

# (4) 24 位定点数存 0.1（小数点后 23 位，截断）：每 0.1 s 少算 9.5×10⁻⁸ s
x01 = math.floor(0.1 * 2 ** 23) / 2 ** 23
e01 = 0.1 - x01
ticks = 100 * 3600 * 10
out(e01=sci(e01, 1), drift100=e01 * ticks, miss=1676 * e01 * ticks)

# (5) 一百万个 0.001 求和（真值 1000）
N = 10 ** 6
v = np.full(N, 0.001, dtype=np.float32)
naive = np.float32(0.0)
for x in v:
    naive = np.float32(naive + x)
s_k, c_k = np.float32(0.0), np.float32(0.0)
for x in v:                                   # 卡亨补偿求和
    y = np.float32(x - c_k)
    tt = np.float32(s_k + y)
    c_k = np.float32(np.float32(tt - s_k) - y)
    s_k = tt
pair = float(np.sum(v, dtype=np.float32))     # NumPy 用成对求和
exact = float(N) * float(np.float32(0.001))
out(naive=float(naive), kahan=float(s_k), pair=pair, exact32=exact, dsum=float(np.sum(np.full(N, 0.001))))

# (6) 相减抵消：(1 − cos x)/x² 在 x 很小时应接近 1/2
xs = 1e-8
f_naive = (1 - math.cos(xs)) / xs ** 2
f_good = 2 * math.sin(xs / 2) ** 2 / xs ** 2
out(fn=f_naive, fg=f_good)
# 大数加小数：单精度里 10⁸ + 1 = 10⁸
big = np.float32(1e8)
out(ulp1e8=float(np.spacing(big)), add1=float(np.float32(big + np.float32(1)) - big))
