"""算例 5.5.1—5.5.3：卷积。
（1）直接卷积与 im2col + 矩阵乘法在小例子上结果相同；
（2）第 3 章的 3×3 卷积层（56×56，64 个通道，批大小 32）：运算量、im2col 矩阵的大小与显存搬运的代价（半精度，A10）；
（3）维诺格拉德 F(2,3) 与 F(2×2,3×3)：乘法次数，与直接计算核对。"""
import numpy as np

from _ch5 import A10
from bookout import out


def conv_direct(x, w, pad=1):
    """x: (B, C, H, W)，w: (K, C, 3, 3)，步长 1，四周补 pad 圈零。按定义逐项相加（互相关，深度学习中称卷积）。"""
    Bn, C, H, W = x.shape
    K, _, R, S = w.shape
    xp = np.pad(x, ((0, 0), (0, 0), (pad, pad), (pad, pad)))
    Ho, Wo = H + 2 * pad - R + 1, W + 2 * pad - S + 1
    y = np.zeros((Bn, K, Ho, Wo))
    for r in range(R):
        for s in range(S):
            y += np.einsum("bchw,kc->bkhw", xp[:, :, r:r + Ho, s:s + Wo], w[:, :, r, s])
    return y


def im2col(x, R=3, S=3, pad=1):
    """把每个输出位置用到的 C×R×S 个输入排成一列：返回 (C·R·S, B·Ho·Wo) 的矩阵。"""
    Bn, C, H, W = x.shape
    xp = np.pad(x, ((0, 0), (0, 0), (pad, pad), (pad, pad)))
    Ho, Wo = H + 2 * pad - R + 1, W + 2 * pad - S + 1
    cols = np.empty((C, R, S, Bn, Ho, Wo))
    for r in range(R):
        for s in range(S):
            cols[:, r, s] = xp[:, :, r:r + Ho, s:s + Wo].transpose(1, 0, 2, 3)
    return cols.reshape(C * R * S, Bn * Ho * Wo), (Bn, Ho, Wo)


rng = np.random.default_rng(5)
x = rng.standard_normal((2, 3, 8, 8))
w = rng.standard_normal((4, 3, 3, 3))
cols, (Bn, Ho, Wo) = im2col(x)
y2 = (w.reshape(4, -1) @ cols).reshape(4, Bn, Ho, Wo).transpose(1, 0, 2, 3)   # (K, C·9) × (C·9, B·Ho·Wo)
assert np.allclose(conv_direct(x, w), y2)

# （2）第 3 章算例 3.8.2 中的卷积层
Bb, C, K, H, W = 32, 64, 64, 56, 56
flop = 2 * Bb * K * H * W * C * 9
M_, K_, N_ = K, C * 9, Bb * H * W                     # 矩阵乘法的形状：权重 (K, 9C) × im2col 矩阵 (9C, B·H·W)
in_MB = Bb * C * H * W * 2 / 1e6                      # 半精度
col_MB = K_ * N_ * 2 / 1e6
blowup = col_MB / in_MB
t_tensor_us = flop / A10["fp16t"] * 1e6               # 张量核心峰值下的计算时间
t_col_us = 2 * col_MB * 1e6 / A10["bw"] * 1e6              # im2col 矩阵写一遍、读一遍
t_io_us = (2 * in_MB + K * 9 * C * 2 / 1e6) * 1e6 / A10["bw"] * 1e6   # 只读输入与权重、写输出（输出与输入一样大）

# （3）维诺格拉德 F(2,3)：两个输出、三个权重，4 次乘法（直接算 6 次）
d = rng.standard_normal(4)
g = rng.standard_normal(3)
m1 = (d[0] - d[2]) * g[0]
m2 = (d[1] + d[2]) * (g[0] + g[1] + g[2]) / 2
m3 = (d[2] - d[1]) * (g[0] - g[1] + g[2]) / 2
m4 = (d[1] - d[3]) * g[2]
y_w = np.array([m1 + m2 + m3, m2 - m3 - m4])
y_d = np.array([d[0:3] @ g, d[1:4] @ g])
assert np.allclose(y_w, y_d)
# F(2×2,3×3)：Y = Aᵀ[(G g Gᵀ) ⊙ (Bᵀ d B)]A，16 次乘法（直接算 36 次）
Bt = np.array([[1, 0, -1, 0], [0, 1, 1, 0], [0, -1, 1, 0], [0, 1, 0, -1]], float)
G = np.array([[1, 0, 0], [0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [0, 0, 1]])
At = np.array([[1, 1, 1, 0], [0, 1, -1, -1]], float)
d2 = rng.standard_normal((4, 4))
g2 = rng.standard_normal((3, 3))
Y = At @ ((G @ g2 @ G.T) * (Bt @ d2 @ Bt.T)) @ At.T
Yd = np.array([[np.sum(d2[i:i + 3, j:j + 3] * g2) for j in range(2)] for i in range(2)])
assert np.allclose(Y, Yd)
out(GFLOP=flop / 1e9, M=M_, K=K_, N=N_, in_MB=in_MB, col_MB=col_MB, blowup=blowup, t_tensor_us=t_tensor_us, t_col_us=t_col_us,
    t_io_us=t_io_us, wino1=6 / 4, wino2=36 / 16)
