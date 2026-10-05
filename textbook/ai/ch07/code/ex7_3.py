"""算例 7.3.1、7.3.2：cuDNN 的卷积算法与数据布局。卷积层与算例 5.5.1 相同：B = 32，C = K = 64，56×56，3×3，步长 1，补零 1 圈。
（1）各种算法纸面上的代价：乘法次数与要额外占用的显存（工作区）。
    隐式矩阵乘法：乘法与直接卷积相同，不要工作区；显式矩阵乘法（im2col）：工作区是 im2col 矩阵；
    维诺格拉德 F(2×2,3×3)、F(4×4,3×3)：每块输出用 (m+2)² 次乘法；工作区放变换后的输入与输出（粗估，按每块 (m+2)² 个数）；
    快速傅里叶变换：每张图补零到 64×64（线性卷积要 56 + 2 + 3 − 1 = 60 ≥ 58，取 2 的幂），频域里逐点复数相乘，
    工作区放变换后的输入、卷积核与输出（实数变换只存一半的频率）。
（2）NCHW 与 NHWC：张量核心的卷积要求通道在最内层（NHWC）。若网络其余部分是 NCHW，每层前后各转换一次，要读写多少。"""
import numpy as np

from _ch7 import A10
from bookout import out

Bn, C, K, H, W, R = 32, 64, 64, 56, 56, 3
P = H * W
flop = 2 * Bn * K * P * C * R * R
mul_direct = Bn * K * P * C * R * R
x_el, y_el = Bn * C * P, Bn * K * P


def wino(m):
    """F(m×m, 3×3)：每 m×m 块输出、每对 (输入通道, 输出通道) 做 (m+2)² 次乘法；变换后的输入有 B·C·块数·(m+2)² 个数，输出同理。"""
    tiles = Bn * (H // m) * (W // m)
    mul = tiles * K * C * (m + 2) ** 2
    ws = tiles * (C + K) * (m + 2) ** 2
    return mul, ws


w2, w2ws = wino(2)
w4, w4ws = wino(4)
N = 64
freq = N * (N // 2 + 1)                                    # 实数二维变换只存一半的频率
fft_mul = Bn * K * C * freq * 4                            # 每个复数乘法 4 次实数乘法
fft_tr = (Bn * C + K * C + Bn * K) * 5 * N * N * np.log2(N)   # 每张图一次二维变换，约 5N²log₂N 次运算
fft_ws = (Bn * C + K * C + Bn * K) * freq * 2              # 复数：两个数

t_tensor = flop / A10["fp16t"] * 1e6
t_io = (x_el + y_el) * 2 / A10["bw"] * 1e6
t_conv_layout = 2 * (x_el + y_el) * 2 / A10["bw"] * 1e6    # 输入转成 NHWC、输出转回 NCHW：各读一遍写一遍（半精度）

MB = lambda el, b=2: el * b / 1e6                          # 半精度
out(GFLOP=flop / 1e9, t_tensor_us=t_tensor, t_io_us=t_io,
    gemm_ws_MB=MB(Bn * P * C * R * R), x_MB=MB(x_el),
    w2_ratio=mul_direct / w2, w2_ws_MB=MB(w2ws, 4), w4_ratio=mul_direct / w4, w4_ws_MB=MB(w4ws, 4),
    fft_ratio=mul_direct / fft_mul, fft_tr_GFLOP=fft_tr / 1e9, fft_ws_MB=MB(fft_ws, 4),
    t_layout_us=t_conv_layout, layout_ratio=t_conv_layout / t_tensor)
