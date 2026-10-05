"""8.5 节：数值微分——五次多项式关节运动（7.1 节算例 7.1.2）在 t₀ = 0.5 s 的角速度：前向差商、中心差商、复步长法的误差；
误差模型与最佳步长；理查森外推；由 17 位编码器读数估计角速度：步长的折中。"""
import math

import numpy as np

from _traj import quintic
from bookout import out

T, D, t0 = 2.0, math.radians(90), 0.5
th = lambda t: D * (10 * (t / T) ** 3 - 15 * (t / T) ** 4 + 6 * (t / T) ** 5)
thc = lambda z: D * (10 * (z / T) ** 3 - 15 * (z / T) ** 4 + 6 * (z / T) ** 5)          # 复数自变量也适用
_, w, a, j = quintic(np.array([t0]), T, D)
w, a, j = float(w[0]), float(a[0]), float(j[0])
eps = np.finfo(float).eps
out(w_true=w, eps=eps)
rows = []
for k in range(1, 13):
    h = 10.0 ** (-k)
    fw = (th(t0 + h) - th(t0)) / h
    ce = (th(t0 + h) - th(t0 - h)) / (2 * h)
    cs = thc(complex(t0, h)).imag / h
    rows.append(f"| $10^{{-{k}}}$ | {abs(fw - w):.1e} | {abs(ce - w):.1e} | {abs(cs - w):.1e} |")
out(err_tab="\n".join(rows))
# 误差模型：前向 E ≈ |θ″|h/2 + 2ε|θ|/h，中心 E ≈ |θ‴|h²/6 + ε|θ|/h
f0 = th(t0)
hf = 2 * math.sqrt(eps * abs(f0) / abs(a))
hc = (3 * eps * abs(f0) / abs(j)) ** (1 / 3)
out(theta0=f0, a0=a, j0=j, h_fwd=hf, h_cen=hc, E_fwd=abs(a) * hf / 2 + 2 * eps * abs(f0) / hf, E_cen=abs(j) * hc ** 2 / 6 + eps * abs(f0) / hc)
# 实测最佳
hs = 10.0 ** np.linspace(-12, -1, 221)
ef = [abs((th(t0 + h) - th(t0)) / h - w) for h in hs]
ec = [abs((th(t0 + h) - th(t0 - h)) / (2 * h) - w) for h in hs]
out(h_fwd_obs=float(hs[int(np.argmin(ef))]), E_fwd_obs=float(min(ef)), h_cen_obs=float(hs[int(np.argmin(ec))]), E_cen_obs=float(min(ec)))

# 理查森外推：R(h) = [4 D⁰_{h/2} − D⁰_h]/3
D0 = lambda h: (th(t0 + h) - th(t0 - h)) / (2 * h)
rows = []
for h in (0.2, 0.1, 0.05, 0.025):
    rich = (4 * D0(h / 2) - D0(h)) / 3
    rows.append(f"| {h:g} | {abs(D0(h) - w):.2e} | {abs(rich - w):.2e} |")
out(rich_tab="\n".join(rows))

# 编码器：17 位，量化间隔 q = 2π/2¹⁷；1 ms 采样；用后向差商 (θ_k − θ_{k−m})/(m T_s) 估计角速度
q = 2 * math.pi / 2 ** 17
Ts = 1e-3
t = np.arange(0, T + Ts / 2, Ts)
meas = np.round(th(t) / q) * q
wt = quintic(t, T, D)[1]
rows, best = [], (1e9, 0)
for m in (1, 2, 5, 10, 20, 50, 100):
    est = (meas[m:] - meas[:-m]) / (m * Ts)
    e = est - wt[m:]
    rms = float(np.sqrt(np.mean(e[(t[m:] > 0.2) & (t[m:] < 1.8)] ** 2)))
    if rms < best[0]:
        best = (rms, m)
    rows.append(f"| {m} | {rms:.4f} |")
out(q_urad=q * 1e6, enc_tab="\n".join(rows), enc_best_m=best[1], enc_best=best[0])
# 误差模型：|α|h/2（截断）+ q/(√6·h)（量化误差的均方根：两个独立的均匀误差之差，标准差 q/√6，再除以 h）
amax = float(np.sqrt(np.mean(quintic(t[(t > 0.2) & (t < 1.8)], T, D)[2] ** 2)))      # 角加速度的均方根
out(alpha_rms=amax, h_star_ms=math.sqrt(2 * q / (math.sqrt(6) * amax)) * 1000)
