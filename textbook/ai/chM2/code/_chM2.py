"""数学篇第 M2 章共用的东西：一个二次损失（用来把收敛的道理算清楚），以及一个真实一点的小回归问题。

**为什么用二次函数**：优化的几乎所有结论——学习率的上限、条件数决定收敛快慢、动量为什么管用——
在二次函数上都能算出闭式解，而在最低点附近，任何光滑的损失都近似是二次的（泰勒展开，M2.3 节）。
所以本章的算例先在二次函数上把道理算准，再到 M1 章那批零件数据的回归上验一遍。

记号与第 2 章一致：参数 θ、学习率 η、损失 ℒ、黑塞矩阵 H、条件数 κ。
"""
from __future__ import annotations

import numpy as np

from parts import parts, standardize        # 数学篇两章共用的零件数据（conventions/parts.py）


def quad(lams):
    """二次损失 ℒ(θ) = ½ Σ λ_j θ_j²：梯度是 λ⊙θ，黑塞矩阵是 diag(λ)，最低点在原点。"""
    lam = np.asarray(lams, dtype=float)

    def loss(th):
        return 0.5 * float(np.sum(lam * np.asarray(th) ** 2))

    def grad(th):
        return lam * np.asarray(th, dtype=float)

    return loss, grad, lam


def gd(grad, th0, eta, steps=200, beta=0.0):
    """梯度下降（beta > 0 时带动量，式 (2.6.3) 的写法）。返回每一步的参数轨迹。"""
    th = np.array(th0, dtype=float)
    v = np.zeros_like(th)
    out = [th.copy()]
    for _ in range(steps):
        v = beta * v - eta * grad(th)
        th = th + v
        out.append(th.copy())
        if not np.all(np.isfinite(th)) or np.linalg.norm(th) > 1e12:
            break
    return np.array(out)


def newton(grad, hess, th0, steps=20):
    """牛顿法：每步解 H Δθ = −∇ℒ。二次函数上一步到底。"""
    th = np.array(th0, dtype=float)
    out = [th.copy()]
    for _ in range(steps):
        th = th - np.linalg.solve(hess(th), grad(th))
        out.append(th.copy())
    return np.array(out)


def ridge_problem(n_feat: int = 3, seed: int = 0):
    """M1 章那批零件数据上的线性回归：用标准化后的外径、内径、长度估粗糙度。
    返回 (设计矩阵 Xt, 目标 y, 黑塞矩阵 H, 它的特征值)。损失取 ℒ(w) = ‖Xt w − y‖²/n（式 (2.2.1)）。"""
    Z, _, _ = standardize(parts(seed=seed))
    Xt = np.c_[np.ones(len(Z)), Z[:, :n_feat]]
    y = Z[:, 4]
    H = 2 * Xt.T @ Xt / len(Z)                       # ℒ 的黑塞矩阵（与 w 无关：二次问题）
    return Xt, y, H, np.linalg.eigvalsh(H)
