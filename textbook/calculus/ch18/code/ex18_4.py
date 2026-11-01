"""18.4 节：零测集与勒贝格可积准则——康托尔集：去掉的区间总长趋于 1，剩下的点不可数、测度为零；
弹跳的球（足式机器人落地、抓取中的碰撞模型）：恢复系数 e，无穷多次弹跳在有限时间 t∞ 内完成（芝诺现象），
速度在可数个时刻跳变，仍然可积，∫|v|dt 等于总路程。"""
import math

from bookout import out

out(cantor_tab="\n".join(f"| {k} | {2 ** k:.3g} | {(2 / 3) ** k:.3e} | {1 - (2 / 3) ** k:.6f} |" for k in (1, 2, 5, 10, 20, 50)))
g, h0, e = 9.81, 0.5, 0.8
t0 = math.sqrt(2 * h0 / g)
v1 = math.sqrt(2 * g * h0)
t_inf = t0 + 2 * e * v1 / g / (1 - e)
dist = h0 + 2 * h0 * e * e / (1 - e * e)
# 弹跳时刻与 |v(t)|
times = [t0]
for k in range(1, 200):
    times.append(times[-1] + 2 * v1 * e ** k / g)


def speed(t):
    if t < t0:
        return g * t
    for k in range(1, 200):
        if t < times[k]:
            vk = v1 * e ** k
            return abs(vk - g * (t - times[k - 1]))
    return 0.0


rows = []
for n in (100, 1000, 10000):
    h = t_inf / n
    s = sum(speed((i + 0.5) * h) * h for i in range(n))
    rows.append(f"| {n} | {s:.5f} | {s - dist:+.1e} |")
out(e=e, h0=h0, t0=t0, t_inf=t_inf, dist=dist, n10=sum(1 for t in times if t < t_inf * 0.999), ball_tab="\n".join(rows),
    t_after20=t_inf - times[20])
