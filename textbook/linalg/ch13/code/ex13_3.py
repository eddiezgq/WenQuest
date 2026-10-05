"""13.3 节：迹、行列式与特征值的关系。
tr A = λ₁ + … + λₙ，det A = λ₁⋯λₙ：随机 4×4 矩阵检验；A = [[4, −5], [2, −3]] 手算检验。
机器人：旋转矩阵的特征值是 1、e^{±iθ}，所以 tr R = 1 + 2cos θ，转角 θ = arccos((tr R − 1)/2)；
R = [[0, 0, 1], [1, 0, 0], [0, 1, 0]] 的迹为 0，转角 120°。一般的旋转（绕轴 (1, 2, 2)/3 转 40°，用罗德里格斯公式构造）由迹反求转角。
投影矩阵的特征值只有 0 和 1，迹等于秩（10.3 节的预告）。"""
import numpy as np

from _num import sci
from bookout import out, vec

rng = np.random.default_rng(133)
A = rng.normal(size=(4, 4))
w = np.linalg.eigvals(A)
out(tr4=float(np.trace(A)), sum4=float(np.sum(w).real), det4=float(np.linalg.det(A)), prod4=float(np.prod(w).real),
    imag4=sci(float(abs(np.sum(w).imag) + abs(np.prod(w).imag)) + 1e-30, 0), ncomplex=int(np.sum(np.abs(w.imag) > 1e-12)))
# 旋转
def rodrigues(k, th):
    k = np.asarray(k, float) / np.linalg.norm(k)
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * Kx + (1 - np.cos(th)) * Kx @ Kx
R = rodrigues([1, 2, 2], np.radians(40))
th = np.degrees(np.arccos((np.trace(R) - 1) / 2))
wR = np.linalg.eigvals(R)
out(trR=float(np.trace(R)), thR=float(th), absR=", ".join(f"{abs(z):.4f}" for z in wR),
    argR=float(np.degrees(np.max(np.angle(wR)))))
# 由 R − Rᵀ 求转轴方向（θ ≠ 0, π）
ax = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * np.sin(np.radians(th)))
out(axis=vec(ax, 4), axis_true=vec(np.array([1, 2, 2]) / 3, 4))
# 投影矩阵
P = np.ones((3, 3)) / 3
out(eigP=", ".join(f"{abs(x) if abs(x) < 1e-9 else x:.0f}" for x in np.sort(np.linalg.eigvalsh(P))), trP=float(np.trace(P)), rankP=int(np.linalg.matrix_rank(P)))
