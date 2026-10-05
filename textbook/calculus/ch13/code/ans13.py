"""第 13 章部分习题答案中的数值。"""
import math

from _agv import ETA, G, M, MU, P0, T
from bookout import out

# 13.2.4：减速时回收 60% 的机械能。减速段 v = A(T − t)，∫v dt = V·TA/2
A, V = 0.5, 1.2
TA = V / A
TC = T - 2 * TA
E_acc = (M * A + MU * M * G) * A * TA ** 2 / 2 / ETA
E_cru = MU * M * G * V * TC / ETA
E_dec = 0.6 * (-M * A + MU * M * G) * V * TA / 2
out(e1324=E_acc + E_cru + E_dec + P0 * T, e1324_dec=E_dec)
# 13.4.2（3）
out(e1342=2 * (math.e - 1 / math.e), e1342b=(math.e ** 2 + 1) / 2)
# 13.4.4、13.4.5
out(e1344=math.sqrt(10 / 7), e1345=math.sqrt(12), q=math.sqrt(120 / 7))
# 13.5.5：Δ = π/3，均方根角加速度 ≤ 8 rad/s²
D, lim = math.pi / 3, 8.0
c = 120 / 7 * D ** 2
T1 = (c / lim ** 2) ** 0.25                          # c/T⁴ = lim²
lo, hi = 0.01, 5.0                                   # 停顿 0.3 s：c/T³/(T + 0.3) = lim²
for _ in range(100):
    mid = (lo + hi) / 2
    if c / mid ** 3 / (mid + 0.3) > lim ** 2:
        lo = mid
    else:
        hi = mid
out(e1355a=T1, e1355b=hi)
# 13.6.1
out(e1361=3.2 / math.pi)
# 13.6.4
out(e1364a=math.sqrt(2 * 0.1 / 0.005), e1364b=math.sqrt(2 * 0.1 / 0.0005))
# 13.6.5
t = 100 / 1.5
dy = 0.5 * 1.5 * math.radians(0.01) * t * t
out(e1365_t=t, e1365=dy, e1365_b=0.01 * 0.05 / dy)
