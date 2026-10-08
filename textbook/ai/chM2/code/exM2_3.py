"""算例 M2.3.1—M2.3.3：泰勒展开、黑塞矩阵与学习率的上限（M2.3 节）。

一阶泰勒展开给出梯度下降（2.1 节），二阶展开给出两件更要紧的事：
（1）学习率的上限 η < 2/λ_max——超过它必然发散，这是算出来的，不是调出来的；
（2）牛顿法：用二阶信息一步到底，代价是要解一个方程组（参数一多就用不起）。
最后在 M1 章那批零件数据的回归上验一遍：预测的上限与实测的分界线一致。
"""
import numpy as np

from _chM2 import gd, newton, quad, ridge_problem
from bookout import out

v = {}
# ---------- （1）二次展开与两种方法的轨迹
LAM = [1.0, 100.0]
loss, grad, lam = quad(LAM)
v["lam1"], v["lam2"] = LAM
v["kappa"] = LAM[1] / LAM[0]
v["eta_max"] = 2 / max(LAM)                                    # 发散的分界
v["eta_best_one"] = 1 / max(LAM)                               # 这一维上一步到位
v["eta_opt"] = 2 / (min(LAM) + max(LAM))                       # 两维都收敛最快（2.6 节）
v["rate_opt"] = (v["kappa"] - 1) / (v["kappa"] + 1)            # 最优学习率下每步的收敛因子

th0 = np.array([1.0, 1.0])
for tag, eta in (("lo", 0.005), ("opt", v["eta_opt"]), ("hi", 0.0199), ("div", 0.0201)):
    tr = gd(grad, th0, eta, steps=2000)
    v[f"eta_{tag}"] = eta
    v[f"end_{tag}"] = float(np.linalg.norm(tr[-1]))
    ks = [k for k, p in enumerate(tr) if np.linalg.norm(p) < 1e-3]
    v[f"k_{tag}"] = ks[0] if ks else -1                        # −1 表示 2000 步内没到
v["grow_div"] = v["end_div"] / float(np.linalg.norm(th0))      # 2000 步后胀大了多少倍
v["factor_div"] = abs(1 - 0.0201 * max(LAM))                   # 每步的放大因子 |1 − ηλ|
assert v["k_div"] == -1 and v["end_div"] > 1.0, "超过 2/λ_max 不会收敛，而且越走越远"
assert 0 < v["k_opt"] < v["k_lo"], "最优学习率应当比小学习率快"

# ---------- （2）牛顿法：二次函数上一步到底
tr_n = newton(grad, lambda th: np.diag(lam), th0, steps=3)
v["newton_1"] = float(np.linalg.norm(tr_n[1]))
assert v["newton_1"] < 1e-12, "二次函数上牛顿法一步到最低点"
d = 4096                                                       # 牛顿法的代价：解 d×d 的方程组
v["d_newton"] = d
v["flop_newton"] = 2 / 3 * d ** 3                              # 乔列斯基分解的量级
v["flop_gd"] = 2 * d
v["newton_ratio"] = v["flop_newton"] / v["flop_gd"]
v["mem_H_GB"] = d * d * 4 / 1e9                                # 只存黑塞矩阵就要这么多（FP32）
N_GPT3 = 175e9                                                 # 1.4 节的参数量
v["mem_H_gpt3_B"] = N_GPT3 ** 2 * 4                            # 它的黑塞矩阵有 N² 个数：根本存不下
v["mem_H_gpt3_ZB"] = v["mem_H_gpt3_B"] / 1e21                  # 换成泽字节（10²¹ 字节）

# ---------- （3）真实一点的问题：零件数据上的线性回归
Xt, y, H, ev = ridge_problem()
v["n_feat"] = Xt.shape[1]
v["lmax"], v["lmin"] = float(ev[-1]), float(ev[0])
v["kappa_real"] = float(ev[-1] / ev[0])
v["eta_max_real"] = 2 / v["lmax"]


def loss_w(w):
    r = Xt @ w - y
    return float(r @ r / len(y))


def grad_w(w):
    return 2 * Xt.T @ (Xt @ w - y) / len(y)


w0 = np.zeros(Xt.shape[1])
for tag, k in (("ok", 0.95), ("edge", 1.01)):                  # 分别取上限的 0.95 倍与 1.01 倍
    eta = k * v["eta_max_real"]
    tr = gd(grad_w, w0, eta, steps=500)
    v[f"real_{tag}_eta"] = eta
    v[f"real_{tag}_end"] = float(loss_w(tr[-1]))
assert v["real_ok_end"] < 0.3 and v["real_edge_end"] > 1e3, "上限两侧应当一个收敛、一个发散"
v["real_opt_eta"] = 2 / (v["lmax"] + v["lmin"])
tr = gd(grad_w, w0, v["real_opt_eta"], steps=500)
v["real_opt_end"] = float(loss_w(tr[-1]))
v["real_opt_k"] = int(next(k for k, p in enumerate(tr) if loss_w(p) - v["real_opt_end"] < 1e-9))
out(**v)
