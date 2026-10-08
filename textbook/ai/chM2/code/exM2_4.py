"""算例 M2.4.1—M2.4.3：凸与不凸（M2.4 节）。

凸函数好在哪：局部最低点就是全局最低点，而且判定很简单（黑塞矩阵半正定）。
深度学习的损失不凸，却照样训得动——本程序用一个最小的"不凸但好训"的例子说明为什么：
不凸的坏处是可能停在不同的点上，但只要停下来的那些点都足够好，就不碍事。
"""
import numpy as np

from _chM2 import gd, ridge_problem
from bookout import out

v = {}
# ---------- （1）判定：黑塞矩阵半正定就是凸
Xt, y, H, ev = ridge_problem()
v["ev_min"] = float(ev[0])
v["convex_ls"] = bool(ev[0] >= -1e-12)                          # 线性回归：凸
assert v["convex_ls"]

def f_nonconvex(th):                                           # 一个一维的不凸函数：两个谷底，一深一浅
    x = float(np.asarray(th).ravel()[0])
    return 0.5 * x ** 4 - 2.0 * x ** 2 + 0.3 * x


def g_nonconvex(th):
    x = float(np.asarray(th).ravel()[0])
    return np.array([2.0 * x ** 3 - 4.0 * x + 0.3])


xs = np.linspace(-2.5, 2.5, 100001)
fs = np.array([0.5 * x ** 4 - 2 * x ** 2 + 0.3 * x for x in xs])
i_glob = int(fs.argmin())
v["x_global"], v["f_global"] = float(xs[i_glob]), float(fs[i_glob])
# 另一个谷底（正半轴上的那个）
right = xs > 0
i_loc = int(np.arange(len(xs))[right][fs[right].argmin()])
v["x_local"], v["f_local"] = float(xs[i_loc]), float(fs[i_loc])
v["gap"] = v["f_local"] - v["f_global"]
v["gap_pct"] = abs(v["gap"] / v["f_global"]) * 100

# ---------- （2）初值决定停在哪个谷底
rng = np.random.default_rng(4)
starts = rng.uniform(-2.5, 2.5, 400)
ends = np.array([gd(g_nonconvex, [s], 0.05, steps=400)[-1][0] for s in starts])
v["n_start"] = len(starts)
v["to_global"] = int(np.sum(np.abs(ends - v["x_global"]) < 0.05))
v["to_local"] = int(np.sum(np.abs(ends - v["x_local"]) < 0.05))
v["to_global_pct"] = v["to_global"] / len(starts) * 100
assert v["to_global"] + v["to_local"] == len(starts), "两个谷底之外不该停在别处"

# ---------- （3）凸函数：初值无所谓
w0s = rng.normal(0, 5, (50, Xt.shape[1]))


def grad_w(w):
    return 2 * Xt.T @ (Xt @ w - y) / len(y)


eta = 2 / (float(ev[-1]) + float(ev[0]))
ends_w = np.array([gd(grad_w, w0, eta, steps=3000)[-1] for w0 in w0s])
v["n_start_cvx"] = len(w0s)
v["spread_cvx"] = float(np.abs(ends_w - ends_w[0]).max())      # 五十个不同初值，收敛到同一点
assert v["spread_cvx"] < 1e-6, "凸问题上初值不影响最终解"
v["eta_cvx"] = eta
out(**v)
