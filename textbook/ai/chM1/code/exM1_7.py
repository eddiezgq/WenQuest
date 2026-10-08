"""算例 M1.7.1—M1.7.3：条件数——为什么有的矩阵算不准（M1.7 节）。

条件数 κ(Xt) = σ_max / σ_min 衡量"输入扰动会被放大多少倍"。它在本书里出现在三处：
解线性方程（这里）、优化的收敛速度（M2.5 节：条件数大，梯度下降就走之字）、低精度数值（第 8 章）。
本程序做三件事：（1）造一个病态的最小二乘问题，看扰动被放大多少倍；
（2）按列标准化以后条件数变成多少；（3）同一个问题用 32 位与 64 位浮点各解一遍，差多少。
"""
import numpy as np

from _chM1 import parts, standardize
from bookout import out

v = {}
X = parts()
# ---------- （1）原始数据的条件数
Xt = np.c_[np.ones(len(X)), X[:, 0], X[:, 1], X[:, 2]]          # 常数项 + 外径 + 内径 + 长度（毫米量级）
y = X[:, 4]
s = np.linalg.svd(Xt, compute_uv=False)
v["kappa_raw"] = float(s[0] / s[-1])
v["s_max"], v["s_min"] = float(s[0]), float(s[-1])

# ---------- （2）标准化之后
Z, mu, sd = standardize(X)
Xz = np.c_[np.ones(len(Z)), Z[:, 0], Z[:, 1], Z[:, 2]]
sz = np.linalg.svd(Xz, compute_uv=False)
v["kappa_std"] = float(sz[0] / sz[-1])
v["kappa_drop"] = v["kappa_raw"] / v["kappa_std"]
# 外径与内径高度相关，这本身也抬高条件数：把内径去掉再看
X2 = np.c_[np.ones(len(Z)), Z[:, 0], Z[:, 2]]
s2 = np.linalg.svd(X2, compute_uv=False)
v["kappa_drop_id"] = float(s2[0] / s2[-1])
v["corr_od_id"] = float(np.corrcoef(X[:, 0], X[:, 1])[0, 1])

# ---------- （3）扰动最坏能被放大多少：正好是条件数
def worst_amplification(Mx: np.ndarray) -> tuple[float, float]:
    """解 Mx·x = b 时，b 的相对扰动在最坏方向上被放大的倍数；返回（实测放大, 条件数）。"""
    U_, s_, Vt_ = np.linalg.svd(Mx)
    b = U_[:, 0] * s_[0]                                       # b 取在最大奇异方向：解最"短"
    x0 = np.linalg.solve(Mx, b)
    db = U_[:, -1] * 1e-8 * np.linalg.norm(b)                  # 扰动取在最小奇异方向：解变化最大
    x1 = np.linalg.solve(Mx, b + db)
    amp = (np.linalg.norm(x1 - x0) / np.linalg.norm(x0)) / (np.linalg.norm(db) / np.linalg.norm(b))
    return float(amp), float(s_[0] / s_[-1])


C_raw = Xt.T @ Xt                                                # 正规方程的系数矩阵：条件数是 $A$ 的平方
C_std = Xz.T @ Xz
v["amp_raw"], v["kappa_raw2"] = worst_amplification(C_raw)
v["amp_std"], v["kappa_std2"] = worst_amplification(C_std)
v["amp_ratio"] = v["amp_raw"] / v["amp_std"]
assert v["amp_raw"] / v["kappa_raw2"] > 0.5, "最坏方向上的放大倍数应当接近条件数"
assert abs(v["kappa_raw2"] / v["kappa_raw"] ** 2 - 1) < 0.05, "正规方程把条件数平方了"

# ---------- （4）单精度解同一个问题
w_hat = np.linalg.lstsq(Xt, y, rcond=None)[0]
wz_hat = np.linalg.lstsq(Xz, y, rcond=None)[0]
b32 = np.linalg.lstsq(Xt.astype(np.float32), y.astype(np.float32), rcond=None)[0].astype(np.float64)
v["err32_raw"] = float(np.linalg.norm(b32 - w_hat) / np.linalg.norm(w_hat) * 100)
b32z = np.linalg.lstsq(Xz.astype(np.float32), y.astype(np.float32), rcond=None)[0].astype(np.float64)
v["err32_std"] = float(np.linalg.norm(b32z - wz_hat) / np.linalg.norm(wz_hat) * 100)
v["eps32"] = float(np.finfo(np.float32).eps)
v["digits32"] = 7                                              # 单精度约 7 位十进制有效数字（第 8 章）
v["lost_raw"] = float(np.log10(v["kappa_raw"]))                # 条件数每大一个数量级，就少一位有效数字
out(**v)
