"""算例 2.3.1～2.3.3：小型 Transformer 中一批数据的张量形状与占用的字节数；行主序的步长；广播。

式 (2.3.2)：行主序下元素 (i₀, …, i_{r−1}) 的偏移 = Σ i_k s_k，步长 s_k = Π_{j>k} n_j。
"""
import numpy as np

from _ch2 import TINY
from bookout import out

B, T, d, h = 32, TINY["ctx"], TINY["d"], TINY["heads"]
dh = d // h
V = TINY["vocab"]

# 算例 2.3.1：一批数据经过第一层时各张量的形状（用全零数组只看形状，不做真正的计算）
ids = np.zeros((B, T), dtype=np.int64)
x = np.zeros((B, T, d), dtype=np.float32)            # 嵌入以后
qkv = np.zeros((B, T, 3 * d), dtype=np.float32)
q = qkv[..., :d].reshape(B, T, h, dh).transpose(0, 2, 1, 3)    # (B, h, T, dh)
k = qkv[..., d:2 * d].reshape(B, T, h, dh).transpose(0, 2, 1, 3)
scores = q @ k.transpose(0, 1, 3, 2)                 # (B, h, T, T)
logits_shape = (B, T, V)
assert scores.shape == (B, h, T, T)
mb = lambda shape, nbytes: int(np.prod(shape)) * nbytes / 2 ** 20
x_mb32 = mb(x.shape, 4)
scores_mb32 = mb(scores.shape, 4)
logits_mb32 = mb(logits_shape, 4)
scores_mb16 = mb(scores.shape, 2)

# 算例 2.3.2：行主序的步长（以元素为单位）
a = np.zeros((B, T, d), dtype=np.float32)
strides = tuple(s // a.itemsize for s in a.strides)
assert strides == (T * d, d, 1)
i0, i1, i2 = 3, 10, 7
offset = i0 * strides[0] + i1 * strides[1] + i2 * strides[2]
assert offset == np.ravel_multi_index((i0, i1, i2), a.shape)
at = a.transpose(0, 2, 1)                             # 只改步长，不搬数据
strides_t = tuple(s // a.itemsize for s in at.strides)
assert np.shares_memory(a, at) and not at.flags["C_CONTIGUOUS"]

# 算例 2.3.3：广播：(B, T, d) + (d,) 与 (B, T, 1) * (1, 1, d)
bias = np.arange(d, dtype=np.float32)
y = x + bias
assert y.shape == (B, T, d)
col = np.ones((B, T, 1), dtype=np.float32)
row = np.ones((1, 1, d), dtype=np.float32)
assert (col * row).shape == (B, T, d)
try:
    _ = np.zeros((B, T, d)) + np.zeros((T,))
    bad = False
except ValueError:
    bad = True
assert bad

out(B=B, T=T, d=d, h=h, dh=dh, V=V, x_mb32=x_mb32, scores_mb32=scores_mb32, scores_mb16=scores_mb16,
    logits_mb32=logits_mb32, s0=strides[0], s1=strides[1], s2=strides[2], i0=i0, i1=i1, i2=i2, offset=offset,
    st0=strides_t[0], st1=strides_t[1], st2=strides_t[2])
