"""12.1 节：面积问题与路程问题——y = x² 在 [0, 1] 下的面积：左、右矩形和夹住 1/3；
AGV 的速度数据（每 0.1 s 一个读数）求行驶距离：左矩形、右矩形、梯形累加，与真实距离比较。"""
from _agv import DIST, T, samples
from bookout import out

rows = []
for n in (4, 10, 100, 1000):
    L = sum((k / n) ** 2 for k in range(n)) / n
    R = sum((k / n) ** 2 for k in range(1, n + 1)) / n
    rows.append(f"| {n} | {L:.6f} | {R:.6f} | {R - L:.6f} |")
out(sq_tab="\n".join(rows))

out(T=T, DIST=DIST)
# 前 4 s：加速 2.4 s 后匀速，真实距离 0.5·0.5·2.4² + 1.2·1.6 = 3.36 m
t_end = 4.0
true4 = 0.5 * 0.5 * 2.4 ** 2 + 1.2 * (t_end - 2.4)
rows = []
for Ts in (0.5, 0.2, 0.1):
    ts, vs = samples(Ts=Ts)
    m = round(t_end / Ts)
    left = sum(vs[k] * Ts for k in range(m))
    right = sum(vs[k + 1] * Ts for k in range(m))
    rows.append(f"| {Ts:g} | {m} | {left:.4f} | {right:.4f} | {(left + right) / 2:.4f} |")
out(true4=true4, agv_tab="\n".join(rows))
ts, vs = samples()
total = sum((vs[k] + vs[k + 1]) / 2 * 0.1 for k in range(len(ts) - 1))   # 梯形和
out(n_samp=len(ts), total=total, total_err=total - DIST)
