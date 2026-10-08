"""算例 M2.1.1—M2.1.3：导数、偏导与梯度（M2.1 节）。

（1）导数是"变化率"，也是"用直线代替曲线"：在一点附近，函数被它的切线逼近，差是高阶小量。
（2）梯度的每个分量是一个偏导数；梯度指向上升最快的方向，负梯度指向下降最快的方向——
    这一条由柯西—施瓦茨不等式给出（2.1 节用过它，这里把它算出来看）。
（3）数值梯度与解析梯度要对得上：这是写反向传播时最该做的一次检查（2.5 节）。
"""
import numpy as np

from _chM2 import quad
from bookout import out

v = {}
# ---------- （1）切线逼近：差是二阶小量
f = lambda x: x ** 3 - 2 * x + 1                      # noqa: E731
df = lambda x: 3 * x ** 2 - 2                         # noqa: E731
x0 = 1.0
v["err_1"], v["err_2"], v["err_3"] = [abs(f(x0 + h) - (f(x0) + df(x0) * h)) for h in (1e-1, 1e-2, 1e-3)]
v["ratio_12"] = v["err_1"] / v["err_2"]               # h 缩小 10 倍，误差缩小约 100 倍（二阶）
v["ratio_23"] = v["err_2"] / v["err_3"]

# ---------- （2）梯度指向最陡：在所有同样长的方向里，负梯度下降得最多
loss, grad, lam = quad([1.0, 100.0])
th = np.array([1.0, 1.0])
g = grad(th)
v["g"] = [round(float(a), 2) for a in g]
v["gnorm"] = float(np.linalg.norm(g))
step = 1e-3
rng = np.random.default_rng(1)
best_dir, best_drop = None, -1e18
for _ in range(20000):
    d = rng.normal(0, 1, 2)
    d /= np.linalg.norm(d)
    drop = loss(th) - loss(th + step * d)
    if drop > best_drop:
        best_drop, best_dir = drop, d
drop_grad = loss(th) - loss(th - step * g / np.linalg.norm(g))
v["drop_best"], v["drop_grad"] = best_drop, drop_grad
v["cos_best_grad"] = float(abs(best_dir @ (-g / np.linalg.norm(g))))
assert drop_grad >= best_drop - 1e-12, "没有哪个方向比负梯度下降得更多"
v["n_dir"] = 20000
# 沿坐标轴走呢
v["drop_axis1"] = loss(th) - loss(th + step * np.array([-1.0, 0.0]))
v["drop_axis2"] = loss(th) - loss(th + step * np.array([0.0, -1.0]))

# ---------- （3）数值梯度核对解析梯度
def num_grad(fun, x, h=1e-5):
    """中心差分：误差是 O(h²)，比前向差分 O(h) 准得多。"""
    x = np.asarray(x, dtype=float)
    out_ = np.zeros_like(x)
    for i in range(len(x)):
        e = np.zeros_like(x)
        e[i] = h
        out_[i] = (fun(x + e) - fun(x - e)) / (2 * h)
    return out_


ng = num_grad(loss, th)
v["num_g"] = [round(float(a), 4) for a in ng]
v["grad_err"] = float(np.abs(ng - g).max() / np.abs(g).max())
assert v["grad_err"] < 1e-8, "数值梯度与解析梯度应当一致到这个量级"
# 步长太小反而更差：舍入误差开始主导（第 8 章）
v["err_h3"] = float(np.abs(num_grad(loss, th, 1e-3) - g).max())
v["err_h5"] = float(np.abs(num_grad(loss, th, 1e-5) - g).max())
v["err_h9"] = float(np.abs(num_grad(loss, th, 1e-9) - g).max())
out(**v)
