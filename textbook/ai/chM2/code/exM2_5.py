"""算例 M2.5.1—M2.5.3：梯度下降收敛得多快，以及动量为什么管用（M2.5 节）。

二次损失上每一步的误差按 |1 − ηλ_j| 缩小（2.1.5 节）。由此：
（1）最优学习率是 2/(λ_min + λ_max)，这时收敛因子是 (κ−1)/(κ+1)——条件数越大越慢；
（2）要把误差降到 1/e，需要的步数与条件数成正比；
（3）加上动量，收敛因子从 (κ−1)/(κ+1) 变成 (√κ−1)/(√κ+1)：步数由 κ 降到 √κ 的量级。
本程序把这三条都算出来，并与实际跑出来的步数核对。
"""
import numpy as np

from _chM2 import gd, quad
from bookout import out

v = {}
KAPPAS = (10, 100, 1000)
v["kappas"] = list(KAPPAS)
for kap in KAPPAS:
    loss, grad, lam = quad([1.0, float(kap)])
    eta = 2 / (1.0 + kap)
    rate = (kap - 1) / (kap + 1)                                # 预测的收敛因子
    tr = gd(grad, [1.0, 1.0], eta, steps=200000)
    err = np.linalg.norm(tr, axis=1)
    k_e = int(np.argmax(err < err[0] / np.e))                   # 实际降到 1/e 用了几步
    k_pred = int(np.ceil(1 / -np.log(rate)))                    # 预测：1/ln(1/rate)
    # 带动量的最优参数（2.6 节）
    b = ((np.sqrt(kap) - 1) / (np.sqrt(kap) + 1)) ** 2
    eta_m = 4 / (1 + np.sqrt(kap)) ** 2
    rate_m = (np.sqrt(kap) - 1) / (np.sqrt(kap) + 1)
    tr_m = gd(grad, [1.0, 1.0], eta_m, steps=200000, beta=b)
    err_m = np.linalg.norm(tr_m, axis=1)
    k_m = int(np.argmax(err_m < err_m[0] / np.e))
    v[f"rate_{kap}"], v[f"k_{kap}"], v[f"kpred_{kap}"] = rate, k_e, k_pred
    v[f"ratem_{kap}"], v[f"km_{kap}"] = rate_m, k_m
    v[f"speedup_{kap}"] = k_e / max(k_m, 1)
    assert abs(k_e - k_pred) <= max(2, 0.1 * k_pred), f"κ={kap} 时实测步数应与预测相符"
    assert k_m <= k_e, f"κ={kap} 时动量不该更慢"
    if kap >= 100:
        assert k_m < k_e * 0.6, f"κ={kap} 时动量应当明显更快"
v["ratio_1000_10"] = v["k_1000"] / v["k_10"]                    # 步数大致与 κ 成正比
v["ratio_m_1000_10"] = v["km_1000"] / v["km_10"]                # 带动量则与 √κ 成正比
v["sqrt_ratio"] = np.sqrt(1000 / 10)
out(**v)
