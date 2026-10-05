"""算例 8.3.1—8.3.3：量化原理。
（1）对称量化 q = round(x / s)，s = max|x| / (2^(b−1) − 1)；非对称量化 q = round(x / s) + z，s = (max − min) / (2^b − 1)。
    一个 384 × 1536 的权重矩阵（各输出通道的尺度相差几倍，按对数正态分布；示意），INT8、INT4 量化：
    逐张量（整个矩阵一个比例）与逐通道（每个输出通道一个比例）的相对误差 ‖W − Ŵ‖ / ‖W‖。
（2）GELU 的输出（输入服从标准正态）全在 [−0.17, +∞) 上：对称量化浪费了近一半的编码，非对称量化的误差小多少（INT8）。
（3）INT8 矩阵乘法：两个量化后的矩阵按整数相乘、INT32 累加（整数运算是精确的：与双精度算出的同一乘积逐位相同），
    再乘以两个比例得到结果；与原始的浮点乘积相比，相对误差多大。"""
import numpy as np

from bookout import out

rng = np.random.default_rng(83)
din, dout = 384, 1536
ch_scale = np.exp(rng.normal(0, 0.6, dout))                    # 各输出通道的尺度
W = rng.normal(0, 0.02, (din, dout)) * ch_scale


def sym(x, bits, axis=None):
    qmax = 2 ** (bits - 1) - 1
    s = np.max(np.abs(x), axis=axis, keepdims=axis is not None) / qmax
    q = np.clip(np.round(x / s), -qmax, qmax)
    return q, s


def asym(x, bits):
    lo, hi = x.min(), x.max()
    s = (hi - lo) / (2 ** bits - 1)
    z = np.round(-lo / s)
    q = np.clip(np.round(x / s) + z, 0, 2 ** bits - 1)
    return q, s, z


rel = lambda a, b: float(np.linalg.norm(a - b) / np.linalg.norm(b) * 100)
r = {}
for bits in (8, 4):
    q, s = sym(W, bits)
    r[f"t{bits}"] = rel(q * s, W)
    q, s = sym(W, bits, axis=0)
    r[f"c{bits}"] = rel(q * s, W)

z = rng.standard_normal(1_000_000)
a = 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z ** 3)))
q, s = sym(a, 8)
err_sym = rel(q * s, a)
used_sym = len(np.unique(q))
q, s, zp = asym(a, 8)
err_asym = rel((q - zp) * s, a)
used_asym = len(np.unique(q))

# （3）INT8 矩阵乘法
X = rng.normal(0, 1, (256, din))
qx, sx = sym(X, 8)                                             # 激活：逐张量
qw, sw = sym(W, 8, axis=0)                                     # 权重：逐通道
acc = qx.astype(np.int64) @ qw.astype(np.int64)                # 整数相乘、累加（硬件用 INT32；这里的和远小于 2³¹）
assert np.abs(acc).max() < 2 ** 31
Y_int = acc * sx * sw
same = bool(np.array_equal(acc, qx @ qw))                      # 双精度下这些整数的乘积与和都是精确的
assert same
out(**r, gelu_min=float(a.min()), err_sym=err_sym, err_asym=err_asym, used_sym=used_sym, used_asym=used_asym,
    acc_max=int(np.abs(acc).max()), int8_same=same, int8_err=rel(Y_int, X @ W))
