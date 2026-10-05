"""算例 9.3.1、9.3.2：张量并行（梅加特龙的切法）。
（1）前馈网络 Y = GELU(X·W₁)·W₂ 在 t 块 GPU 上：W₁ 按列切（每块 GPU 得到 d_ff/t 列，GELU 逐元素，各自算），W₂ 按行切，
    各块算出的部分和相加（一次全归约）就是 Y。用 NumPy 在 t = 4 时与不切分的结果核对；注意力按头切分同理。
（2）通信量：每层前向两次全归约（注意力一次、前馈网络一次），反向再两次；每次全归约的数据是 b·s·d 个半精度数。
    7B 模型、b·s = 4096 个词元、t = 8：每层每一步通信多少，经 NVLink（A100，300 GB/s）与经 InfiniBand NDR（50 GB/s）
    各要多久，与这一层的计算时间（按 A100 半精度峰值的 50%）相比。这就是张量并行只在一台机器内使用的原因。"""
import numpy as np

from _ch9 import A100, BIG, IB, NVLINK
from bookout import out

rng = np.random.default_rng(93)
n, d, dff, t = 64, 32, 128, 4
X = rng.normal(size=(n, d))
W1, W2 = rng.normal(size=(d, dff)) / np.sqrt(d), rng.normal(size=(dff, d)) / np.sqrt(dff)
gelu = lambda z: 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z ** 3)))
Y = gelu(X @ W1) @ W2
parts = [gelu(X @ W1[:, k * dff // t:(k + 1) * dff // t]) @ W2[k * dff // t:(k + 1) * dff // t] for k in range(t)]
ok = bool(np.allclose(sum(parts), Y, rtol=1e-12, atol=1e-12))

d7, L, tok, tp = BIG["d"], BIG["L"], 4096, 8
msg = tok * d7 * 2                                     # 一次全归约的数据（字节）
per_layer = 4 * msg * 2 * (tp - 1) / tp                 # 每层每步 4 次全归约，环形算法每块 GPU 发出 2(t−1)/t 倍
flop_layer = 6 * tok * (4 * d7 * d7 + 3 * d7 * BIG["dff"]) / tp   # 每块 GPU 这一层的训练运算量（不计注意力矩阵）
t_comp = flop_layer / (A100["fp16t"] * 0.5)
out(ok=ok, msg_MB=msg / 1e6, per_layer_MB=per_layer / 1e6, t_nvl_ms=per_layer / NVLINK["a100"] * 1e3,
    t_ib_ms=per_layer / IB["ndr"] * 1e3, t_comp_ms=t_comp * 1e3)
