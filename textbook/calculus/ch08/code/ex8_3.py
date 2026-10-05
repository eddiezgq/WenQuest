"""8.3 节：误差传播——NTC 热敏电阻：电阻的相对误差 0.1% 折合成温度误差；两节连杆末端位置对编码器误差的
最坏情况估计、均方根估计与蒙特卡罗模拟；测高：h = d·tan α 的相对误差与最佳仰角。"""
import math

import numpy as np

from _traj import ur5e_links
from bookout import out

# 热敏电阻：T(R) = 1/(1/T₀ + ln(R/R₀)/B)，dT = −T²/(B R)·dR，|dT| = T²/B·|dR/R|
B, R0, T0 = 3950.0, 10.0, 298.15
Rk = lambda T: R0 * math.exp(B * (1 / T - 1 / T0))          # kΩ
rows = []
for tc in (0, 25, 50, 80, 120):
    T = tc + 273.15
    # 两种误差：电阻的相对误差 0.1%；电阻的绝对误差 10 Ω（0.01 kΩ，模数转换的分辨率）
    rows.append(f"| {tc} | {Rk(T):.3f} | {T * T / B * 0.001:.4f} | {T * T / (B * Rk(T)) * 0.01:.3f} |")
out(ntc_tab="\n".join(rows))

# 两节连杆：p = (l₁cos θ₁ + l₂cos(θ₁+θ₂), l₁sin θ₁ + l₂sin(θ₁+θ₂))
l1, l2 = ur5e_links()
t1, t2 = math.radians(30), math.radians(60)
r = math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(t2))
d0 = 1e-3                                                   # 编码器误差不超过 ±0.001 rad，均匀分布
worst = (r + l2) * d0                                       # 三角不等式给出的上界
# 线性化后的精确最大值：Δp ≈ J·(e₁, e₂)，|Δp| 是凸函数，最大值在四个角点 (±δ, ±δ) 处取得
J = np.array([[-l1 * math.sin(t1) - l2 * math.sin(t1 + t2), -l2 * math.sin(t1 + t2)],
              [l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l2 * math.cos(t1 + t2)]])
lin_max = max(np.linalg.norm(J @ np.array([s1 * d0, s2 * d0])) for s1 in (-1, 1) for s2 in (-1, 1))
rms_pred = d0 * math.sqrt((r * r + l2 * l2) / 3)
rng = np.random.default_rng(83)
N = 200000
e1, e2 = rng.uniform(-d0, d0, N), rng.uniform(-d0, d0, N)
fk = lambda a, b: np.stack([l1 * np.cos(a) + l2 * np.cos(a + b), l1 * np.sin(a) + l2 * np.sin(a + b)])
dp = np.linalg.norm(fk(t1 + e1, t2 + e2) - fk(np.array(t1), np.array(t2))[:, None], axis=0)
out(r_mm=r * 1000, d0_deg=math.degrees(d0), worst_mm=worst * 1000, lin_max_mm=lin_max * 1000, rms_pred_mm=rms_pred * 1000,
    mc_max_mm=float(dp.max()) * 1000, mc_rms_mm=float(np.sqrt(np.mean(dp ** 2))) * 1000,
    mc_p99_mm=float(np.quantile(dp, 0.99)) * 1000, mc_frac_half=float(np.mean(dp > worst / 2)))

# 测高：水平距离 d = 20 m，仰角 α 的误差 ±0.5°，h = d tan α，dh/h = dα/(sin α cos α) = 2dα/sin 2α
da = math.radians(0.5)
rows = []
for a_deg in (15, 30, 45, 60, 75):
    a = math.radians(a_deg)
    h = 20 * math.tan(a)
    rows.append(f"| {a_deg} | {h:.2f} | {20 / math.cos(a) ** 2 * da:.3f} | {2 * da / math.sin(2 * a) * 100:.2f} |")
out(height_tab="\n".join(rows))
