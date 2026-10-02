"""1.2 节共用：零件检验数据与感知机。以下划线开头，构建时不单独运行。

数据：数字工厂某工位 30 根轴的两项检测，x₁ 为外径偏差的绝对值、x₂ 为圆度误差，都以 10 μm 为单位；
标签 +1 为合格、−1 为不合格（按工艺卡的判定）。为了教学，数据取整到 0.1，并保证两类可以用一条直线分开。
实验 1.2（lab/lab1_2.js）用的是同一组数。
"""
import numpy as np

# (x1, x2, y)
PARTS = [
    (0.2, 0.4, 1), (0.6, 0.2, 1), (0.4, 1.2, 1), (1.0, 0.6, 1), (0.2, 1.8, 1), (1.4, 0.2, 1), (0.8, 1.0, 1),
    (0.0, 0.8, 1), (1.2, 1.0, 1), (0.6, 1.6, 1), (1.6, 0.4, 1), (0.2, 2.2, 1), (1.0, 1.2, 1), (0.4, 0.6, 1),
    (1.8, 0.0, 1),
    (2.6, 0.4, -1), (2.2, 1.0, -1), (1.6, 1.6, -1), (1.0, 2.4, -1), (0.4, 3.0, -1), (2.8, 1.8, -1), (1.8, 2.6, -1),
    (0.8, 3.4, -1), (3.0, 0.6, -1), (2.4, 2.4, -1), (1.2, 3.0, -1), (0.0, 3.4, -1), (2.6, 1.2, -1), (1.4, 2.0, -1),
    (2.0, 1.6, -1),
]
XOR = [(0.0, 0.0, -1), (1.0, 1.0, -1), (0.0, 1.0, 1), (1.0, 0.0, 1)]


def augmented(data):
    """增广输入 x̃ = (x₁, x₂, 1) 与标签 y。"""
    X = np.array([[a, b, 1.0] for a, b, _ in data])
    y = np.array([c for _, _, c in data], dtype=float)
    return X, y


def perceptron(data, eta=1.0, max_epochs=1000, w0=None):
    """感知机学习规则（式 (1.2.3)），按数据的固定顺序循环。返回 (w, 更新次数, 周期数, 每次更新后的 w 列表, 是否收敛)。"""
    X, y = augmented(data)
    w = np.zeros(3) if w0 is None else np.array(w0, dtype=float)
    k, hist = 0, [w.copy()]
    for epoch in range(1, max_epochs + 1):
        mistakes = 0
        for xi, yi in zip(X, y):
            if yi * (w @ xi) <= 0:          # 判错（含恰在边界上）
                w = w + eta * yi * xi
                k += 1
                mistakes += 1
                hist.append(w.copy())
        if mistakes == 0:
            return w, k, epoch, hist, True
    return w, k, max_epochs, hist, False


def max_margin(data):
    """最大间隔的分界面（过原点的增广形式）：min ‖w‖²，约束 yᵢ w·x̃ᵢ ≥ 1；γ* = 1/‖w*‖。
    三个未知数的凸二次规划，用 SciPy 的 trust-constr 求解，再用 KKT 条件核对。"""
    from scipy.optimize import LinearConstraint, minimize
    X, y = augmented(data)
    A = y[:, None] * X
    w_start = perceptron(data)[0]
    w_start = w_start / np.min(A @ w_start)                 # 缩放成可行点
    res = minimize(lambda w: w @ w, w_start, jac=lambda w: 2 * w, hess=lambda w: 2 * np.eye(3), method="trust-constr",
                   constraints=[LinearConstraint(A, 1, np.inf)], options={"gtol": 1e-12, "xtol": 1e-14, "maxiter": 5000})
    w = res.x
    assert np.all(A @ w >= 1 - 1e-6), "infeasible"
    # KKT：w = Σ αᵢ yᵢ x̃ᵢ（αᵢ ≥ 0，只在间隔恰为 1 的支持向量上非零）
    sv = np.where(A @ w < 1 + 1e-3)[0]
    alpha, *_ = np.linalg.lstsq(A[sv].T, w, rcond=None)
    assert np.all(alpha > -1e-6) and np.allclose(A[sv].T @ alpha, w, atol=1e-4), "KKT"
    if len(sv) == 3:                                        # 三个支持向量的间隔恰为 1：解线性方程组得到精确解
        w = np.linalg.solve(A[sv], np.ones(3))
        assert np.all(A @ w >= 1 - 1e-12)
    return w, 1.0 / np.linalg.norm(w)
