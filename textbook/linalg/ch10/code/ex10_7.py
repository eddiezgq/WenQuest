"""10.7 节：传感器标定。(a) 差速 AGV 的里程计：轮半径 r 与轮距 b。每次试验记下左右轮转过的角度 φ_R、φ_L（编码器），
用激光跟踪仪测出走过的路程 d 与航向变化 Δθ；d = r(φ_R + φ_L)/2，Δθ = (r/b)(φ_R − φ_L) 对 (r, k = r/b) 是线性的，
两类测量单位与精度不同，用加权最小二乘一起求解，再得 b = r/k。(b) 三轴加速度计的六面法标定：读数 m = M a + o，
M（3×3，含刻度与轴间耦合）与零偏 o 共 12 个未知数，六个朝向给出 18 个方程。"""
import numpy as np

from bookout import out, tex, vec

from _agv import b_nom, b_true, calib, calibrated, r_nom, r_true, runs

r_hat, k_hat, C, A, rng = calibrated()
b_hat = r_hat / k_hat


def sb(x, C):
    """b = r/k 的标准差（一阶误差传播）。"""
    gr = np.array([1 / x[1], -x[0] / x[1] ** 2])
    return float(np.sqrt(gr @ C @ gr))


out(r_hat=r_hat * 1000, b_hat=b_hat * 1000, sr=float(np.sqrt(C[0, 0])) * 1e6, sb=sb((r_hat, k_hat), C) * 1000, Ashape=f"{A.shape[0]}×{A.shape[1]}")
# 只做直线试验：两轮转角几乎相同，k 那一列很小，b 几乎定不出来
x0, C0, A0 = calib(runs(rng, 5, 0))
out(sb0=sb(x0, C0) * 1000, b0=x0[0] / x0[1] * 1000)
# 检验：沿 5 m 直线再原地转 360°，用图纸值与标定值预测，与真实比较
prL = 5.0 / r_true
turn = 2 * np.pi * b_true / (2 * r_true)                  # 原地转一圈每个轮转过的角度
for name, (rr, bb) in (("nom", (r_nom, b_nom)), ("cal", (r_hat, b_hat))):
    out(**{f"{name}_d": (rr * prL - 5.0) * 1000, f"{name}_th": float(np.degrees(rr * 2 * turn / bb - 2 * np.pi))})
# (b) 加速度计：真实 M、o；六个朝向（±x、±y、±z 朝上）
g = 9.81
M_true = np.array([[1.020, 0.004, -0.006], [0.003, 0.980, 0.005], [-0.004, 0.002, 1.010]])
o_true = np.array([0.05, -0.03, 0.08])
G = [np.array(v) * g for v in ([1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1])]
rows, y = [], []
for a in G:
    m = M_true @ a + o_true + rng.normal(scale=0.01, size=3)
    for i in range(3):
        row = np.zeros(12)
        row[3 * i:3 * i + 3] = a
        row[9 + i] = 1.0
        rows.append(row); y.append(m[i])
A2, y2 = np.array(rows), np.array(y)
x2 = np.linalg.lstsq(A2, y2, rcond=None)[0]
M_hat, o_hat = x2[:9].reshape(3, 3), x2[9:]
out(A2shape=f"{A2.shape[0]}×{A2.shape[1]}", rA2=int(np.linalg.matrix_rank(A2)), M_hat=tex(M_hat, 4), o_hat=vec(o_hat, 3),
    Merr=float(np.abs(M_hat - M_true).max()), oerr=float(np.abs(o_hat - o_true).max()))
# 标定后：任一姿态下的重力读数修正为 M̂⁻¹(m − ô)，模长应为 g
a = np.array([0.3, -0.5, 0.81]); a = a / np.linalg.norm(a) * g
m = M_true @ a + o_true
out(raw=float(np.linalg.norm(m)), corr=float(np.linalg.norm(np.linalg.solve(M_hat, m - o_hat))),
    raw_err=float(np.linalg.norm(m - a)), corr_err=float(np.linalg.norm(np.linalg.solve(M_hat, m - o_hat) - a)))
