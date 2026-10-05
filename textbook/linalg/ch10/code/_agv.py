"""本章共用：差速 AGV 里程计标定的模拟（程序 10.7.1 与图 10.7.1 共用，保证两处的标定结果一致）。以下划线开头，构建时不单独运行。"""
import numpy as np

r_true, b_true = 0.0745, 0.412           # 实际：轮胎磨损，轮距与图纸不同
r_nom, b_nom = 0.075, 0.400              # 图纸值（1.2 节）
sd, sth = 0.001, np.radians(0.2)         # 跟踪仪：路程 1 mm、角度 0.2°


def runs(rng, n_line, n_turn):
    """直线试验：两轮转角几乎相同；原地转向试验：两轮反向。返回 (φ_R, φ_L, d, Δθ, 类别)。"""
    out_ = []
    for _ in range(n_line):
        ph = rng.uniform(20, 30)                          # rad，约走 1.5～2.2 m
        pr, pl = ph * (1 + rng.normal(scale=0.002)), ph
        out_.append((pr, pl, r_true * (pr + pl) / 2 + rng.normal(scale=sd), r_true * (pr - pl) / b_true + rng.normal(scale=sth), "line"))
    for _ in range(n_turn):
        ph = rng.uniform(15, 20) * rng.choice([-1, 1])    # 每轮 15～20 rad，车体原地转约 ±1 圈
        pr, pl = ph, -ph * (1 + rng.normal(scale=0.002))
        out_.append((pr, pl, r_true * (pr + pl) / 2 + rng.normal(scale=sd), r_true * (pr - pl) / b_true + rng.normal(scale=sth), "turn"))
    return out_


def calib(data):
    rows, y, w = [], [], []
    for pr, pl, d, dth, _ in data:
        rows.append([(pr + pl) / 2, 0.0]); y.append(d); w.append(1 / sd ** 2)
        rows.append([0.0, pr - pl]); y.append(dth); w.append(1 / sth ** 2)
    A, y, W = np.array(rows), np.array(y), np.diag(w)
    x = np.linalg.solve(A.T @ W @ A, A.T @ W @ y)
    C = np.linalg.inv(A.T @ W @ A)
    return x, C, A




def calibrated():
    """程序 10.7.1 的标定：5 次直线、5 次原地转向，固定随机种子。返回 (r̂, k̂, 协方差, 系数矩阵, 随机数发生器)。"""
    rng = np.random.default_rng(107)
    (r_hat, k_hat), C, A = calib(runs(rng, 5, 5))
    return r_hat, k_hat, C, A, rng
