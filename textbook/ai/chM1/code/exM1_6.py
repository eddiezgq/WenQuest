"""算例 M1.6.1—M1.6.3：奇异值分解、低秩近似与它在大模型里的用处（M1.6 节）。

（1）任何矩阵都能分解成"转一下、沿几个方向拉伸、再转一下"：A = U Σ Vᵀ。
（2）只留前 k 个奇异值，就得到秩 k 的最佳近似（埃卡特—杨定理）：误差正好是剩下那些奇异值的平方和开根号。
    用一张零件表面图演示：这张图的结构只有 3 个奇异值（明暗 1 个、磨削纹理 2 个），后面一长串都是噪声；
    所以留 3 个就已经把图里"真的东西"留住了，再加秩只是在拟合噪声——与过拟合是同一件事（2.7 节）。
（3）同一个道理用在网络权重上就是 LoRA：不改原来的大矩阵，只学一个秩 r 的修正量。
"""
import numpy as np

from _chM1 import surface
from bookout import out

v = {}
A = surface(96)                                                # 含噪声的图（现实里量到的）
A0 = surface(96, noise=0)                                      # 同一张图，不含噪声（用来说明结构的秩）
m, n = A.shape
U, S, Vt = np.linalg.svd(A, full_matrices=False)
v["m"], v["n"] = m, n
v["rank"] = int(np.linalg.matrix_rank(A))
v["rank0"] = int(np.linalg.matrix_rank(A0))                    # 不含噪声时的秩：结构有几层
S0 = np.linalg.svd(A0, compute_uv=False)
v["s0"] = [round(float(x), 3) for x in S0[:5]]
v["err0_3"] = float(np.sqrt((S0[3:] ** 2).sum()) / np.linalg.norm(A0, "fro")) * 100
v["s"] = [round(float(x), 3) for x in S[:6]]
v["s1"], v["s2"], v["s3"] = float(S[0]), float(S[1]), float(S[2])
v["s_ratio"] = float(S[0] / S[1])
v["fro"] = float(np.linalg.norm(A, "fro"))
assert abs(v["fro"] - float(np.sqrt((S ** 2).sum()))) < 1e-9, "F 范数等于奇异值的平方和开根号"

# ---------- 秩 k 的最佳近似：误差与埃卡特—杨定理核对
rows = {}
for k in (1, 2, 3, 5, 10, 20):
    Ak = (U[:, :k] * S[:k]) @ Vt[:k]
    err = float(np.linalg.norm(A - Ak, "fro"))
    want = float(np.sqrt((S[k:] ** 2).sum()))                  # 定理给出的误差
    assert abs(err - want) < 1e-9, "低秩近似的误差应等于剩下奇异值的平方和开根号"
    rel = err / v["fro"] * 100
    keep = k * (m + n + 1) / (m * n) * 100                     # 存 U、Σ、V 的数占原来的百分之几
    rows[k] = (rel, keep)
    v[f"err_{k}"], v[f"keep_{k}"] = rel, keep
v["noise_fro"] = float(np.linalg.norm(A - A0, "fro") / v["fro"] * 100)   # 噪声占了多少：误差降不到它以下才算正常
v["worst_1"] = float(np.abs(A - (np.outer(U[:, 0], Vt[0]) * S[0])).max())
v["worst_3"] = float(np.abs(A - (U[:, :3] * S[:3]) @ Vt[:3]).max())

# ---------- 随便换一个秩 3 的矩阵，都不会比它更好
g = np.random.default_rng(6)
A3 = (U[:, :3] * S[:3]) @ Vt[:3]
best = float(np.linalg.norm(A - A3, "fro"))
worse = 0
for _ in range(200):
    B = (g.normal(0, 0.3, (m, 3)) + U[:, :3] * S[:3]) @ (Vt[:3] + g.normal(0, 0.02, (3, n)))
    worse += float(np.linalg.norm(A - B, "fro")) > best
assert worse == 200, "埃卡特—杨：秩 3 的近似里没有比它更好的"
v["n_try"] = 200

# ---------- LoRA 的账
K = N = 4096
for r in (4, 8, 64):
    v[f"lora_{r}"] = (K + N) * r
    v[f"lora_{r}_pct"] = (K + N) * r / (K * N) * 100
v["full_params"] = K * N
v["r_breakeven"] = int(K * N / (K + N))                        # 秩多大时就不省了
out(**v)
