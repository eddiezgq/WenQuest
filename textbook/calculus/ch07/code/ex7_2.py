"""7.2 节：几种函数在 0 点的差商；五次多项式运动的角速度何时最大。"""
import math

from _traj import quintic
from bookout import out

hs = [0.1, 0.01, 0.001]
# |x| 在 0 点：右差商恒为 1，左差商恒为 −1
right = [(abs(h) - 0) / h for h in hs]
left = [(abs(-h) - 0) / (-h) for h in hs]
assert right == [1, 1, 1] and left == [-1, -1, -1]
# x^(1/3) 在 0 点：差商 h^(−2/3) 无限增大（竖直切线）
cbrt = lambda x: math.copysign(abs(x) ** (1 / 3), x)
q_cbrt = [cbrt(h) / h for h in hs]
# x sin(1/x)：差商 sin(1/h) 来回摆动；x² sin(1/x)：差商 h sin(1/h) → 0
q_osc = [math.sin(1 / h) for h in hs]
q_sq = [h * math.sin(1 / h) for h in hs]
out(cb1=q_cbrt[0], cb2=q_cbrt[1], cb3=q_cbrt[2], os1=q_osc[0], os2=q_osc[1], os3=q_osc[2], sq1=q_sq[0], sq2=q_sq[1], sq3=q_sq[2])

# 7.2.4 节：Δ = 90°、T = 2 s 的五次多项式运动，角速度在 t = T/2 最大，等于 15Δ/(8T)
T, D = 2.0, math.pi / 2
w_mid = float(quintic(T / 2, T, D)[1])
assert abs(w_mid - 15 * D / (8 * T)) < 1e-12
out(w_max=w_mid, w_max_deg=math.degrees(w_mid))

# 算例 7.2.5：分段匀速指令，0–1 s 以 20°/s、1–2 s 以 40°/s 转动；t = 1 s 处的左、右导数
cmd = lambda t: 20 * t if t <= 1 else 20 + 40 * (t - 1)
h = 1e-6
out(cmd_left=round((cmd(1) - cmd(1 - h)) / h, 6), cmd_right=round((cmd(1 + h) - cmd(1)) / h, 6))
