"""11.4 节：费马原理与折射——AGV 从地毯区（速度 v₁）穿到地砖区（速度 v₂）的最短时间路径：令 T′(x) = 0，
得到 sin θ₁/v₁ = sin θ₂/v₂（斯涅耳定律）；与直线路径、“先走到最近处再拐”的路径比较；光从空气射入水中的折射角。"""
import math

from bookout import out

v1, v2 = 0.6, 1.2               # m/s：地毯、地砖
A = (0.0, 3.0)                  # 起点在地毯区（y > 0），分界线为 y = 0
B = (6.0, -2.0)                 # 终点在地砖区
T = lambda x: math.hypot(x - A[0], A[1]) / v1 + math.hypot(B[0] - x, B[1]) / v2
dT = lambda x: (x - A[0]) / (v1 * math.hypot(x - A[0], A[1])) - (B[0] - x) / (v2 * math.hypot(B[0] - x, B[1]))
lo, hi = 0.0, 6.0               # T′(0) < 0 < T′(6)，T 是凸函数，二分 T′
for _ in range(80):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if dT(mid) < 0 else (lo, mid)
xs = (lo + hi) / 2
s1 = (xs - A[0]) / math.hypot(xs - A[0], A[1])
s2 = (B[0] - xs) / math.hypot(B[0] - xs, B[1])
x_line = A[0] + (B[0] - A[0]) * A[1] / (A[1] - B[1])
out(v1=v1, v2=v2, x_star=xs, T_star=T(xs), th1=math.degrees(math.asin(s1)), th2=math.degrees(math.asin(s2)),
    r1=s1 / v1, r2=s2 / v2, x_line=x_line, T_line=T(x_line), T_perp=T(0.0))
# 光：空气 → 水，折射率 1.33，入射角 45°
out(water=math.degrees(math.asin(math.sin(math.radians(45)) / 1.33)))
