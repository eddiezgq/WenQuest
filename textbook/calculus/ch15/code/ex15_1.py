"""15.1 节：梯形公式与辛普森公式——关节五次多项式运动（转 90°，2 s）中电机电流 i(t) = 0.5 + 0.8α + 0.6ω（A）
按 10 Hz、5 Hz 采样，用梯形公式与辛普森公式求电荷量 Q = ∫i dt；准确值由牛顿–莱布尼茨公式给出。"""
import math

from _quad import simpson, trap
from bookout import out

T, D = 2.0, math.pi / 2


def omega(t):
    u = t / T
    return D / T * 30 * u * u * (1 - u) ** 2


def alpha(t):
    u = t / T
    return D / T ** 2 * 60 * u * (1 - u) * (1 - 2 * u)


cur = lambda t: 0.5 + 0.8 * alpha(t) + 0.6 * omega(t)
Q = 0.5 * T + 0.8 * 0 + 0.6 * D          # ∫α = ω(T) − ω(0) = 0，∫ω = Δ
rows = []
for fs in (2, 5, 10, 20):
    n = int(fs * T)
    qt, qs = trap(cur, 0, T, n), simpson(cur, 0, T, n)
    rows.append(f"| {fs} | {n + 1} | {qt:.6f} | {qt - Q:.2e} | {qs:.6f} | {qs - Q:.2e} |")
out(Q=Q, cur_tab="\n".join(rows), i_max=max(cur(k * 0.001) for k in range(2001)), i_min=min(cur(k * 0.001) for k in range(2001)))
# 单个区间上：梯形与辛普森对三次多项式的结果（辛普森准确）
f = lambda x: x ** 3 - 2 * x + 1
ex = 1 / 4 - 1 + 1
out(cub_trap=trap(f, 0, 1, 1), cub_simp=simpson(f, 0, 1, 2), cub_ex=ex)
