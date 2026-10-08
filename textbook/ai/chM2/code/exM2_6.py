"""算例 M2.6.1—M2.6.2：约束优化与拉格朗日乘子（M2.6 节）。

（1）等式约束：在"总重量固定"的约束下让方差最小——用拉格朗日乘子求解，并与网格搜索核对。
（2）不等式约束与正则化的关系：岭回归既可以写成"损失加一个 λ‖w‖²"，也可以写成
    "在 ‖w‖ ≤ t 的范围内最小化损失"，两种写法一一对应。本程序把这条对应关系算出来：
    扫一遍 λ，每个 λ 对应一个 ‖w‖，两条路径重合。
"""
import numpy as np

from _chM2 import ridge_problem
from bookout import out

v = {}
# ---------- （1）等式约束：min ½‖θ‖² s.t. aᵀθ = c
a = np.array([1.0, 2.0, 3.0])
c = 6.0
# 拉格朗日函数 ½‖θ‖² − μ(aᵀθ − c)，令梯度为零：θ = μa，代回约束得 μ = c/(aᵀa)
mu = c / (a @ a)
th_star = mu * a
v["mu"] = float(mu)
v["th_star"] = [round(float(x), 4) for x in th_star]
v["obj_star"] = float(0.5 * th_star @ th_star)
v["check"] = float(a @ th_star)                                 # 应当等于 c
assert abs(v["check"] - c) < 1e-12
# 网格搜索核对（在约束面上随机取点，没有一个比它更小）
rng = np.random.default_rng(6)
worse = 0
for _ in range(5000):
    d = rng.normal(0, 1, 3)
    d -= (a @ d) / (a @ a) * a                                  # 投到约束面的方向上（M1.4 节的投影）
    p = th_star + d * rng.uniform(0, 2)
    worse += 0.5 * p @ p > v["obj_star"] - 1e-12
v["n_try"] = 5000
assert worse == 5000, "约束面上没有比拉格朗日解更小的点"
v["grad_parallel"] = float(abs(np.dot(th_star / np.linalg.norm(th_star), a / np.linalg.norm(a))))
assert abs(v["grad_parallel"] - 1) < 1e-12, "最优点处目标的梯度与约束的梯度平行"

# ---------- （2）岭回归：罚项写法与约束写法是同一件事
Xt, y, H, ev = ridge_problem()
n, p = Xt.shape
lams = np.logspace(-4, 2, 40)
norms, losses = [], []
for lam in lams:
    w = np.linalg.solve(Xt.T @ Xt / n + lam * np.eye(p), Xt.T @ y / n)
    norms.append(float(np.linalg.norm(w)))
    losses.append(float(np.mean((Xt @ w - y) ** 2)))
norms, losses = np.array(norms), np.array(losses)
assert np.all(np.diff(norms) < 1e-12), "λ 越大，解的范数越小——这就是那条一一对应"
v["lam_small"], v["norm_small"], v["loss_small"] = float(lams[0]), norms[0], losses[0]
v["lam_big"], v["norm_big"], v["loss_big"] = float(lams[-1]), norms[-1], losses[-1]
# 取一个 λ，再用约束写法解一遍：在 ‖w‖ ≤ t 的球里最小化损失，t 取那个 λ 对应的范数
i = 20
lam_i, t_i = float(lams[i]), float(norms[i])
w_pen = np.linalg.solve(Xt.T @ Xt / n + lam_i * np.eye(p), Xt.T @ y / n)
best, best_w = 1e18, None
for _ in range(40000):                                          # 在球内随机取点，找损失最小的
    w = rng.normal(0, 1, p)
    w *= t_i / np.linalg.norm(w) * rng.uniform(0, 1) ** (1 / p)
    L = float(np.mean((Xt @ w - y) ** 2))
    if L < best:
        best, best_w = L, w
v["lam_i"], v["t_i"] = lam_i, t_i
v["loss_pen"] = float(np.mean((Xt @ w_pen - y) ** 2))
v["loss_ball"] = best
v["gap_pct"] = (v["loss_ball"] - v["loss_pen"]) / v["loss_pen"] * 100
assert v["loss_ball"] >= v["loss_pen"] - 1e-9, "罚项写法的解就是球内最优的那个"
v["n_ball"] = 40000
out(**v)
