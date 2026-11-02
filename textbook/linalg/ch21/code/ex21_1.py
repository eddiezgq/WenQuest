"""21.1 节：谱半径、矩阵序列与矩阵级数；诺伊曼级数。第 3 章数字工厂三个车间的投入产出模型：
订单沿供应链一轮一轮向上游传导，总产出是诺伊曼级数 d + Cd + C²d + …；谱半径决定收敛快慢；
(I − C)⁻¹ 的元素全为正；诺伊曼级数的误差界；盖尔范德公式 ‖Aᵏ‖^{1/k} → ρ(A)。"""
import math

import numpy as np

from _num import sci
from bookout import out, tex, vec

C = np.array([[0.10, 0.30, 0.05], [0.05, 0.10, 0.40], [0.02, 0.05, 0.10]])     # 与 ex3_7.py 相同
d = np.array([50.0, 80.0, 300.0])
x = np.linalg.solve(np.eye(3) - C, d)
ev = np.linalg.eigvals(C)
rho = float(max(abs(ev)))
out(C=tex(C, 2), d=vec(d, 0), x=vec(x, 1), rho=rho, ev=", ".join(f"{z.real:.3f}" if abs(z.imag) < 1e-12 else f"{z.real:.3f}{z.imag:+.3f}\\mathrm i" for z in ev),
    n1C=float(np.linalg.norm(C, 1)), niC=float(np.linalg.norm(C, np.inf)))
# 一轮一轮：第 0 轮是订单本身，第 k 轮是第 k − 1 轮的需求引起的上游需求 Cᵏd
rounds, s, term = [], np.zeros(3), d.copy()
for k in range(30):
    s = s + term
    rounds.append((k, term.copy(), s.copy(), np.max(np.abs(x - s))))
    term = C @ term
for k in (0, 1, 2, 5):
    out(**{f"t{k}": vec(rounds[k][1], 1), f"s{k}": vec(rounds[k][2], 1), f"e{k}": float(rounds[k][3])})
k01 = next(k for k, _, _, e in rounds if e < 0.1)
out(k01=k01, ratio=float(rounds[10][3] / rounds[9][3]))
# (I − C)⁻¹ 的元素全为正：每个车间多 1 万元订单，各车间要多生产多少
Linv = np.linalg.inv(np.eye(3) - C)
assert np.all(Linv > 0)
bound = 1 / (1 - np.linalg.norm(C, 1))
out(Linv=tex(Linv, 3), nLinv1=float(np.linalg.norm(Linv, 1)), bound=float(bound))
# 盖尔范德公式：B 的谱半径 0.9，‖B‖₂ 约 1.53
B = np.array([[0.9, 1.0], [0.0, 0.9]])
for k in (1, 10, 100, 1000):
    out(**{f"g{k}": float(np.linalg.norm(np.linalg.matrix_power(B, k), 2) ** (1 / k))})
gc10 = float(np.linalg.norm(np.linalg.matrix_power(C, 10), 2) ** 0.1)
out(gc10=gc10, gc10rel=gc10 / rho - 1)
# 一个“好”的范数：用 D = diag(1, δ) 相似变换，‖D⁻¹BD‖∞ = 0.9 + δ
for dl in (1.0, 0.1, 0.01):
    D = np.diag([1.0, dl])
    out(**{f"nd{str(dl).replace('.', '')}": float(np.linalg.norm(np.linalg.inv(D) @ B @ D, np.inf))})
