"""算例 9.4.1～9.4.4：最大似然与最小二乘。

9.4.1 超声测距 5 个读数（mm）：已知标准差时，似然函数的最大值在样本均值处；数值搜索与公式一致。
9.4.2 AGV 对接充电桩：激光测距（σ = 3 mm）读 152 mm，超声测距（σ = 10 mm）读 143 mm。
      加权最小二乘 = 最大似然：x̂ 与其标准差；与简单平均、只用激光比较，并以蒙特卡洛核对各估计量的标准差。
9.4.3 测力传感器标定（参照 39.5 节）：u = a + bF，噪声标准差随载荷增大 σᵢ = 0.05 + 0.002Fᵢ（mV）。
      普通最小二乘与加权最小二乘的 a、b 及其协方差矩阵；蒙特卡洛核对式 (9.4.9)，并验证加权的方差更小（定理 9.4.3）。
9.4.4 9 个超声读数中有一个多径回波造成的野值：平均值、中位数与胡伯估计（迭代重加权）的比较。
"""
import math

import numpy as np

from bookout import out, tex

rng = np.random.default_rng(904)

# ---------------------------------------------------------------- 算例 9.4.1 似然函数
zs = np.array([148.0, 155.0, 151.0, 144.0, 157.0])          # 超声读数，mm
sig_u = 10.0
mu_grid = np.linspace(120, 180, 600001)
loglik = np.array([-0.5 * np.sum((zs[:, None] - mu_grid[None, :]) ** 2, axis=0) / sig_u ** 2])[0] \
    - len(zs) * math.log(sig_u * math.sqrt(2 * math.pi))
mu_ml = mu_grid[np.argmax(loglik)]
assert abs(mu_ml - zs.mean()) < 1e-3
sig_ml = math.sqrt(np.mean((zs - zs.mean()) ** 2))          # σ 未知时的最大似然估计（除以 n）
s_unb = zs.std(ddof=1)

# ---------------------------------------------------------------- 算例 9.4.2 两个传感器
s1, s2 = 3.0, 10.0                                          # mm
z1, z2 = 152.0, 143.0
A = np.array([[1.0], [1.0]])
W = np.diag([1 / s1 ** 2, 1 / s2 ** 2])
P = np.linalg.inv(A.T @ W @ A)
xhat = (P @ A.T @ W @ np.array([z1, z2]))[0]
sig_hat = math.sqrt(P[0, 0])
w1 = (1 / s1 ** 2) / (1 / s1 ** 2 + 1 / s2 ** 2)
assert abs(xhat - (w1 * z1 + (1 - w1) * z2)) < 1e-12
sig_avg = math.sqrt(s1 ** 2 + s2 ** 2) / 2
x_true = 150.0
M = 200000
Z1 = x_true + s1 * rng.standard_normal(M)
Z2 = x_true + s2 * rng.standard_normal(M)
mc_w = np.std(w1 * Z1 + (1 - w1) * Z2, ddof=1)
mc_avg = np.std((Z1 + Z2) / 2, ddof=1)
mc_l = np.std(Z1, ddof=1)
assert abs(mc_w / sig_hat - 1) < 0.01 and abs(mc_avg / sig_avg - 1) < 0.01
# 任意权重 w 的方差 w²σ1² + (1 − w)²σ2²，在 w1 处最小
ws = np.linspace(0, 1, 100001)
vs = ws ** 2 * s1 ** 2 + (1 - ws) ** 2 * s2 ** 2
assert abs(ws[np.argmin(vs)] - w1) < 1e-4

# ---------------------------------------------------------------- 算例 9.4.3 标定直线
F = np.array([0.0, 20, 40, 60, 80, 100])                   # 标准力，N
a0, b0 = 0.3, 0.2                                           # 真实零点 mV、灵敏度 mV/N
sig_i = 0.05 + 0.002 * F                                    # 各点噪声的标准差，mV
u = a0 + b0 * F + sig_i * rng.standard_normal(len(F))       # 这一次标定的读数
Ad = np.column_stack([np.ones_like(F), F])
Wd = np.diag(1 / sig_i ** 2)
ols = np.linalg.solve(Ad.T @ Ad, Ad.T @ u)
wls = np.linalg.solve(Ad.T @ Wd @ Ad, Ad.T @ Wd @ u)
C_wls = np.linalg.inv(Ad.T @ Wd @ Ad)                       # 式 (9.4.9)
Lo = np.linalg.solve(Ad.T @ Ad, Ad.T)
C_ols = Lo @ np.diag(sig_i ** 2) @ Lo.T                     # 普通最小二乘的真实协方差（式 (9.2.5)）
# 两种算法：正规方程与“各行除以 σᵢ 后的普通最小二乘”（QR）
Aw = Ad / sig_i[:, None]
uw = u / sig_i
assert np.allclose(np.linalg.lstsq(Aw, uw, rcond=None)[0], wls, atol=1e-12)
# 蒙特卡洛：重复标定 20 万次
K = 200000
U = a0 + b0 * F[None, :] + sig_i[None, :] * rng.standard_normal((K, len(F)))
est_w = np.linalg.solve(Ad.T @ Wd @ Ad, Ad.T @ Wd @ U.T)
est_o = Lo @ U.T
Cw_mc = np.cov(est_w)
Co_mc = np.cov(est_o)
assert np.allclose(Cw_mc, C_wls, rtol=0.03, atol=1e-12) and np.allclose(Co_mc, C_ols, rtol=0.03, atol=1e-12)
assert np.all(np.linalg.eigvalsh(C_ols - C_wls) > -1e-15)   # 定理 9.4.3：差为半正定
assert abs(est_w.mean(axis=1)[1] - b0) < 1e-4                 # 无偏

# ---------------------------------------------------------------- 算例 9.4.4 野值
zr = np.array([150.0, 148, 153, 151, 149, 152, 147, 150, 236])
mean_r = zr.mean()
med_r = float(np.median(zr))
k_h = 1.345                                                 # 胡伯函数的阈值（以噪声标准差为单位）
c = k_h * 2.0                                               # 噪声标准差取 2 mm
m = med_r
for _ in range(100):                                        # 迭代重加权
    r = zr - m
    wgt = np.where(np.abs(r) <= c, 1.0, c / np.maximum(np.abs(r), 1e-12))
    m_new = np.sum(wgt * zr) / np.sum(wgt)
    if abs(m_new - m) < 1e-12:
        break
    m = m_new
hub = m
# 核对：胡伯估计满足 Σ ψ(zᵢ − m) = 0
psi = np.clip(zr - hub, -c, c)
assert abs(psi.sum()) < 1e-9
w_out = c / abs(zr[-1] - hub)
mean_clean = zr[:-1].mean()
# 中位数是绝对偏差之和的最小点
grid = np.linspace(140, 160, 200001)
lad = np.abs(zr[:, None] - grid[None, :]).sum(axis=0)
assert abs(grid[np.argmin(lad)] - med_r) < 1e-3

out(
    zs=", ".join(f"{v:.0f}" for v in zs), mu_ml=mu_ml, zbar=zs.mean(), sig_ml=sig_ml, s_unb=s_unb,
    s1=s1, s2=s2, z1=z1, z2=z2, w1=w1, w2=1 - w1, xhat=xhat, sig_hat=sig_hat, sig_avg=sig_avg, avg=(z1 + z2) / 2,
    mc_w=mc_w, mc_avg=mc_avg, mc_l=mc_l, M=M,
    F=", ".join(f"{v:.0f}" for v in F), u=", ".join(f"{v:.3f}" for v in u), sig_list=", ".join(f"{v:.2f}" for v in sig_i),
    a_ols=ols[0], b_ols=ols[1], a_wls=wls[0], b_wls=wls[1],
    sa_wls=math.sqrt(C_wls[0, 0]), sb_wls=math.sqrt(C_wls[1, 1]), sa_ols=math.sqrt(C_ols[0, 0]), sb_ols=math.sqrt(C_ols[1, 1]),
    sa_wmc=math.sqrt(Cw_mc[0, 0]), sb_wmc=math.sqrt(Cw_mc[1, 1]), sa_omc=math.sqrt(Co_mc[0, 0]), sb_omc=math.sqrt(Co_mc[1, 1]),
    rho_ab=C_wls[0, 1] / math.sqrt(C_wls[0, 0] * C_wls[1, 1]), K=K,
    k_h=k_h, zr=", ".join(f"{v:.0f}" for v in zr), mean_r=mean_r, med_r=med_r, hub=hub, c=c, w_out=w_out, mean_clean=mean_clean,
)
