"""14.4 节：瑞利商与库朗–费希尔极小极大原理。
柔性臂杆的集中质量模型：三个相同的质量 m = 1 kg 用刚度 k = 10⁴ N/m 的弹簧串起来，一端固定、一端自由：
K = k[[2, −1, 0], [−1, 2, −1], [0, −1, 1]]，自由振动 m ẍ = −Kx，ω² 是 K/m 的特征值。
瑞利商 R(x) = xᵀKx/(m xᵀx) ≥ λ₁：用试探振型 (1, 2, 3)、(1, 1, 1)、静变形 (3, 5, 6) 估计最低固有频率；
随机向量检验 λ₁ ≤ R ≤ λ₃；“锁住”第三个质量（去掉最后一行一列）后的特征值与原特征值交错（柯西交错定理）。"""
import numpy as np

from _num import sci
from bookout import out, vec

k, m = 1e4, 1.0
K = k * np.array([[2.0, -1, 0], [-1, 2, -1], [0, -1, 1]])
lam = np.linalg.eigvalsh(K / m)
f = np.sqrt(lam) / (2 * np.pi)
out(lam=vec(lam, 1), f=vec(f, 2), f1=float(f[0]))
R = lambda x: float(x @ K @ x / (m * x @ x))
for name, x in (("lin", [1, 2, 3]), ("one", [1, 1, 1]), ("stat", [3, 5, 6])):
    x = np.array(x, float)
    out(**{f"R_{name}": R(x), f"f_{name}": float(np.sqrt(R(x)) / (2 * np.pi)), f"err_{name}": float(100 * (np.sqrt(R(x) / lam[0]) - 1))})
rng = np.random.default_rng(144)
vals = [R(x) for x in rng.normal(size=(100000, 3))]
out(Rmin=float(min(vals)), Rmax=float(max(vals)), lam1=float(lam[0]), lam3=float(lam[2]))
# 交错：锁住第三个质量
K2 = K[:2, :2]
mu = np.linalg.eigvalsh(K2 / m)
out(mu=vec(mu, 1), fmu=vec(np.sqrt(mu) / (2 * np.pi), 2), fmu1=float(np.sqrt(mu[0]) / (2 * np.pi)), f2=float(f[1]))
