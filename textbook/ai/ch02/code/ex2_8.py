"""算例 2.8.1～2.8.4：卷积层的输出尺寸与 AlexNet 第一层；卷积与全连接的参数量；用 im2col 把卷积变成矩阵乘法并与直接卷积核对；
循环网络中梯度随时间步的衰减。

式 (2.8.2)：输出尺寸 ⌊(H + 2p − k)/s⌋ + 1；L 层 3×3 卷积（步长 1）的感受野 2L + 1（2.8.2 节）。
"""
import numpy as np

from bookout import out


def out_size(H, k, s, p):
    return (H + 2 * p - k) // s + 1


# 算例 2.8.1：AlexNet 第一层，k = 11，s = 4
exact224 = (224 - 11) / 4 + 1
o227 = out_size(227, 11, 4, 0)
o224p2 = out_size(224, 11, 4, 2)
exact224p2 = (224 + 4 - 11) / 4 + 1

# 算例 2.8.2：参数量：卷积层 vs 把同样的输入和输出用全连接相连
conv_params = 96 * (11 * 11 * 3) + 96
fc_params = (224 * 224 * 3) * (55 * 55 * 96)
ratio = fc_params / conv_params
# 两层 3×3 与一层 5×5（输入、输出通道都为 C）
C = 256
p33 = 2 * 9 * C * C
p55 = 25 * C * C

# 算例 2.8.3：im2col
rng = np.random.default_rng(0)
Cin, H, W, Cout, k, s = 3, 9, 9, 4, 3, 2
x = rng.normal(size=(Cin, H, W))
w = rng.normal(size=(Cout, Cin, k, k))
Ho, Wo = out_size(H, k, s, 0), out_size(W, k, s, 0)
direct = np.zeros((Cout, Ho, Wo))
for o in range(Cout):
    for i in range(Ho):
        for j in range(Wo):
            direct[o, i, j] = np.sum(w[o] * x[:, i * s:i * s + k, j * s:j * s + k])
cols = np.array([x[:, i * s:i * s + k, j * s:j * s + k].ravel() for i in range(Ho) for j in range(Wo)])   # (Ho·Wo, Cin·k·k)
via_mm = (cols @ w.reshape(Cout, -1).T).T.reshape(Cout, Ho, Wo)
assert np.allclose(direct, via_mm)
# AlexNet 第一层的 im2col 矩阵尺寸（单张图）
M1, K1, N1 = 55 * 55, 11 * 11 * 3, 96
col_bytes = M1 * K1 * 4
in_bytes = 227 * 227 * 3 * 4
blowup = col_bytes / in_bytes

# 算例 2.8.4：循环网络：同一个矩阵连乘 T 次
T = 50
rho = 0.9
decay = rho ** T
Q, _ = np.linalg.qr(rng.normal(size=(64, 64)))
Wr = rho * Q                                        # 正交矩阵乘以 0.9：每乘一次，任何向量的长度都缩小到 0.9 倍
g = rng.normal(size=64)
g0 = np.linalg.norm(g)
for _ in range(T):
    g = Wr.T @ g
measured = np.linalg.norm(g) / g0
assert abs(measured - decay) < 1e-12

out(exact224=exact224, o227=o227, o224p2=o224p2, exact224p2=exact224p2, conv_params=conv_params, fc_params_e=f"{fc_params:.2e}".replace("e+", "\\times10^{") + "}",
    ratio_e=f"{ratio:.1e}".replace("e+0", "\\times10^{").replace("e+", "\\times10^{") + "}", C=C, p33=p33, p55=p55,
    Ho=Ho, Wo=Wo, M1=M1, K1=K1, N1=N1, col_mb=col_bytes / 2 ** 20, in_mb=in_bytes / 2 ** 20, blowup=blowup,
    T=T, rho=rho, decay=decay, measured=measured)
