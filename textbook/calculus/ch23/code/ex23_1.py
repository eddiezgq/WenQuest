"""23.1 节：级数与部分和；几何级数。机械臂松开夹爪，零件从 0.2 m 高处落到托盘上弹跳（恢复系数 e = 0.6）：
各次弹跳的高度与时间构成几何级数，求总路程、总时间（零件停稳要多久）；部分和与余项；
固定步长（1 ms）仿真能分辨多少次弹跳（芝诺现象）。另：裂项求和 Σ1/(k(k+1))。"""
import math

from bookout import out

g, h0, e = 9.81, 0.2, 0.6
t0 = math.sqrt(2 * h0 / g)                      # 第一次落地的时间
T_total = t0 * (1 + e) / (1 - e)
D_total = h0 * (1 + e * e) / (1 - e * e)
out(bo_h0=h0, bo_e=e, bo_t0=t0, bo_T=T_total, bo_D=D_total, bo_ratio_T=(1 + e) / (1 - e))
rows = []
S = t0
for k in range(1, 9):
    S += 2 * t0 * e ** k                         # 第 k 次弹起到再落地
    rows.append(f"| {k} | {h0 * e ** (2 * k) * 1000:.3g} | {2 * t0 * e ** k * 1000:.1f} | {S:.4f} | {T_total - S:.4f} |")
out(bo_tab="\n".join(rows))
# 弹跳高度小于 0.1 mm 算停稳：需要几次
k_settle = math.ceil(math.log(1e-4 / h0) / (2 * math.log(e)))
out(bo_k_settle=k_settle, bo_T_settle=t0 + 2 * t0 * e * (1 - e ** k_settle) / (1 - e))
# 1 ms 步长的仿真：飞行时间短于 2 步（2 ms）的弹跳分辨不出
k_zeno = math.ceil(math.log(0.002 / (2 * t0)) / math.log(e))
out(bo_k_zeno=k_zeno)
# 固定步长 1 ms 的仿真（半隐式欧拉 + 碰撞时速度反向乘 e）
dt, z, v, t, bounces, last = 1e-3, h0, 0.0, 0.0, 0, None
while t < 3.0:
    v -= g * dt
    z += v * dt
    t += dt
    if z < 0 and v < 0:
        z, v = 0.0, -e * v
        bounces += 1
        last = t
    if z <= 0 and abs(v) < 1e-9:
        break
out(sim_bounces=bounces, sim_last=last)
# 裂项求和
n = 100
s = sum(1 / (k * (k + 1)) for k in range(1, n + 1))
out(tel_100=s, tel_formula=1 - 1 / (n + 1))
