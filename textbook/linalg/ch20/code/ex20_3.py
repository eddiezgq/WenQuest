"""20.3 节：条件数。第 3 章的铜合金配料：原来的三种回炉料与换成一种“几乎是 A、B 对半混合”的料 C′ 后的条件数；
成分测量误差对配料量的影响（蒙特卡罗）；右端扰动的误差界与使它取等号的方向；到最近的奇异矩阵的相对距离 = 1/κ₂；
κ(AᵀA) = κ(A)²；按列缩放（换单位）改变条件数。"""
import numpy as np

from bookout import out, tex, vec

M0 = np.array([[0.80, 0.60, 0.70], [0.15, 0.35, 0.10], [0.05, 0.05, 0.20]])    # 列：料 A、B、C（铜、锌、锡的质量分数）
M1 = M0.copy()
M1[:, 2] = [0.70, 0.24, 0.06]                                                   # 料 C′：几乎是 A、B 对半混合（0.70, 0.25, 0.05）
k0, k1 = np.linalg.cond(M0), np.linalg.cond(M1)
x_true = np.array([40.0, 30.0, 30.0])
b0, b1 = M0 @ x_true, M1 @ x_true
out(M1=tex(M1, 2), k0=float(k0), k1=float(k1), b1=vec(b1, 1), xt=vec(x_true, 0),
    k0_1=float(np.linalg.cond(M0, 1)), k1_1=float(np.linalg.cond(M1, 1)))

# 成分测量误差：每个质量分数有标准差 0.003（0.3 个百分点）的误差，用“测得的”成分配料，看配料量散布多大
rng = np.random.default_rng(2003)
res = {}
for name, M, b in (("0", M0, b0), ("1", M1, b1)):
    E = 0.003 * rng.standard_normal((2000, 3, 3))
    X = np.array([np.linalg.solve(M + Ek, b) for Ek in E])
    res[name] = X
    if name == "1":
        dA = np.median([np.linalg.norm(Ek, 2) for Ek in E]) / np.linalg.norm(M, 2)
    out(**{f"sd{name}": vec(X.std(axis=0), 1), f"neg{name}": float(100 * np.mean((X < 0).any(axis=1))),
           f"rel{name}": float(np.median(np.linalg.norm(X - x_true, axis=1) / np.linalg.norm(x_true)))})
out(dA_rel=float(dA), kdA=float(k1 * dA), bound=float(k1 * dA / (1 - k1 * dA)))                                      # 实测 ‖δA‖₂/‖A‖₂ 的中位数，及它乘 κ₂

# 右端扰动：δb 沿最小奇异值的左奇异向量时，误差放大达到 κ 倍
U, s, Vt = np.linalg.svd(M1)
db = 0.1 * U[:, 2]
dx = np.linalg.solve(M1, db)
amp = (np.linalg.norm(dx) / np.linalg.norm(x_true)) / (np.linalg.norm(db) / np.linalg.norm(b1))
bw = U[:, 0] * np.linalg.norm(b1)                                               # b 沿 u₁、δb 沿 u₃：两者同时达到最坏
xw = np.linalg.solve(M1, bw)
amp_w = (np.linalg.norm(np.linalg.solve(M1, db)) / np.linalg.norm(xw)) / (np.linalg.norm(db) / np.linalg.norm(bw))
out(dx=vec(dx, 1), amp=float(amp), amp_w=float(amp_w), s1=vec(s, 4))
# 最近的奇异矩阵：去掉最小奇异值（埃卡特–杨），相对距离 σ₃/σ₁ = 1/κ₂
Ms = M1 - s[2] * np.outer(U[:, 2], Vt[2])
out(dist=float(np.linalg.norm(M1 - Ms, 2) / np.linalg.norm(M1, 2)), inv_k=float(1 / k1), Ms=tex(Ms, 3), rankMs=int(np.linalg.matrix_rank(Ms)))
# κ(AᵀA) = κ(A)²
out(kAtA=float(np.linalg.cond(M1.T @ M1)), k1sq=float(k1 ** 2))
# 换单位：料 C′ 以吨计（第三列乘 1000），条件数变了，问题本身没有变；按列缩放到等长可以恢复
Mt = M1 * np.array([1, 1, 1000.0])
Dn = 1 / np.linalg.norm(Mt, axis=0)
out(kt=float(np.linalg.cond(Mt)), kbal=float(np.linalg.cond(Mt * Dn)))
