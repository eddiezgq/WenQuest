"""15.3 节：合同变换与西尔维斯特惯性定理。
(1) 随机取可逆矩阵 C，B = CᵀAC 的特征值变了，但正、负、零特征值的个数不变（惯性定理）；
(2) 谱切片：柔性臂杆的集中质量模型（6 个 0.5 kg 质量，弹簧刚度 2×10⁴ N/m，一端固定，末端再挂 0.5 kg 负载），
    Kx = ω²Mx。σ = (2πf)²，K − σM 的 LDLᵀ 分解中负主元的个数 = 低于 f 的固有频率的个数（σ 处的惯性）。
    只数负主元，不求特征值，就能回答“0～40 Hz 内有几个共振频率”；再用二分法把第 2 个频率夹到 0.01 Hz。"""
import numpy as np
import scipy.linalg as sl


from bookout import out, vec


def inertia(vals, tol=1e-9):
    return int((vals > tol).sum()), int((vals < -tol).sum()), int((np.abs(vals) <= tol).sum())


A = np.array([[2.0, 2, -2], [2, 5, -4], [-2, -4, 5]]) - 4 * np.eye(3)       # 15.2 节的矩阵减去 4I：特征值 −3, −3, 6
rng = np.random.default_rng(153)
C = rng.normal(size=(3, 3))
B = C.T @ A @ C
la, lb = np.linalg.eigvalsh(A), np.linalg.eigvalsh(B)
out(lamA=vec(la, 2), lamB=vec(lb, 2), inA=str(inertia(la)), inB=str(inertia(lb)), detC=float(np.linalg.det(C)))
# 很多随机的 C：惯性从不改变
same = sum(inertia(np.linalg.eigvalsh((Ci.T @ A @ Ci))) == inertia(la) for Ci in rng.normal(size=(2000, 3, 3)))
out(trials=2000, same=int(same))
# C 奇异时：零特征值可能增多
Cs = C.copy(); Cs[:, 2] = Cs[:, 0] + Cs[:, 1]
out(inS=str(inertia(np.linalg.eigvalsh(Cs.T @ A @ Cs), 1e-8)))

# (2) 谱切片
n, m, k, mp = 6, 0.5, 2e4, 0.5
K = k * (2 * np.eye(n) - np.eye(n, k=1) - np.eye(n, k=-1))
K[-1, -1] = k
M = m * np.eye(n)
M[-1, -1] += mp
fr = np.sqrt(sl.eigh(K, M, eigvals_only=True)) / (2 * np.pi)
out(freqs=vec(fr, 1))


def pivots(S):
    """三对角对称矩阵不交换行的 LDLᵀ：主元 d_i = s_ii − s_{i,i−1}²/d_{i−1}。"""
    d = [S[0, 0]]
    for i in range(1, len(S)):
        d.append(S[i, i] - S[i, i - 1] ** 2 / d[-1])
    return np.array(d)


def count_below(f):
    s = (2 * np.pi * f) ** 2
    return int((pivots(K - s * M) < 0).sum())


f0 = 40.0
d40 = pivots(K - (2 * np.pi * f0) ** 2 * M)
out(f0=f0, d40=vec(d40 / 1e3, 1), neg40=count_below(f0), true40=int((fr < f0).sum()))
# 用计数做二分：第 2 个固有频率
lo, hi, it = 0.0, 100.0, 0
while hi - lo > 0.01:
    mid = 0.5 * (lo + hi)
    if count_below(mid) >= 2:
        hi = mid
    else:
        lo = mid
    it += 1
out(bis_lo=lo, bis_hi=hi, bis_it=it, f2=float(fr[1]))
