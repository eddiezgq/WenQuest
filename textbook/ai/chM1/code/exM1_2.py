"""算例 M1.2.1—M1.2.3：矩阵乘法的运算量、一层网络，以及结合律值多少钱（M1.2 节）。

（1）一层全连接网络就是一次矩阵乘法加一个偏置；一批样本一起算，仍是一次矩阵乘法。
（2）矩阵乘法 C(M×N) = A(M×K)·B(K×N) 的运算量是 2MNK FLOP（1 次乘加记 2 FLOP，见《符号约定》），
    访存量至少是三个矩阵的大小。两者之比就是计算强度（1.5 节），它决定这件事受算力限制还是受带宽限制。
（3）矩阵乘法满足结合律，但两种乘法顺序的运算量可以差几个数量级——这正是低秩分解（LoRA）省钱的道理。
"""
import numpy as np

from _chM1 import parts, standardize
from bookout import out
from gpus import GPUS

v = {}
# ---------- （1）一层网络：一批样本一起算
X, _, _ = standardize(parts())
B, D_IN, D_OUT = X.shape[0], X.shape[1], 3
g = np.random.default_rng(1)
W = g.normal(0, 1 / np.sqrt(D_IN), (D_IN, D_OUT))
b = g.normal(0, 0.1, D_OUT)
H = X @ W + b                                                  # (B,D_IN)·(D_IN,D_OUT) + (D_OUT,) 广播
one = X[0] @ W + b                                             # 一个样本单独算
assert np.allclose(H[0], one), "一批一起算与一个一个算必须一样"
v["B"], v["d_in"], v["d_out"] = B, D_IN, D_OUT
v["shape_H"] = list(H.shape)
v["flop_layer"] = 2 * B * D_IN * D_OUT

# ---------- （2）一层大网络的运算量、访存量与计算强度
M, K, N = 32, 4096, 4096                                       # 批 32、输入输出各 4096
W_flop = 2 * M * N * K
Q_byte = 2 * (M * K + K * N + M * N)                           # FP16：每个数 2 字节
v["M"], v["K"], v["N"] = M, K, N
v["W_GF"] = W_flop / 1e9
v["Q_MB"] = Q_byte / 1024**2
v["I"] = W_flop / Q_byte                                       # 计算强度 FLOP/B
v["I_weight"] = 2 * M                                          # 权重读一遍、被这批样本用 M 次：I ≈ 2M
h100 = GPUS["h100"]                                            # 规格表与第 1、3 章共用，不手打数字
v["bal_h100"] = h100["fp16t"] / h100["bw"]                     # P/β：这块卡的"平衡点"（1.5 节）
v["M_balance"] = v["bal_h100"] / 2                             # I ≈ 2M，所以批要到这么大才不受带宽限制
v["gpu"] = h100["name"]
v["params_layer"] = K * N

# ---------- （3）结合律：(AB)C 还是 A(BC)
A = g.normal(0, 1, (M, K))
B2 = g.normal(0, 1, (K, 8))                                    # 低秩的中间维 r = 8
C = g.normal(0, 1, (8, N))
left = (A @ B2) @ C
right = A @ (B2 @ C)
assert np.allclose(left, right, atol=1e-8), "结合律：两种顺序的结果必须一样"
v["r"] = 8
v["flop_left"] = 2 * M * 8 * K + 2 * M * N * 8                 # (AB) 再乘 C
v["flop_right"] = 2 * K * N * 8 + 2 * M * N * K                # 先把 BC 乘成 K×N，再乘 A
v["assoc_ratio"] = v["flop_right"] / v["flop_left"]
v["lora_params"] = (K + N) * 8
v["lora_pct"] = v["lora_params"] / (K * N) * 100
out(**v)
