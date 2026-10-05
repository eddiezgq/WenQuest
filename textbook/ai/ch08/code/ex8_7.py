"""算例 8.7.1：两个融合核函数省下多少显存流量（单精度，A10 的 600 GB/s）。
（1）注意力的“缩放 + 因果掩码 + softmax”：S 有 B·h·T² 个数（B = 32，h = 6，T = 256）。急切执行三个核函数各读写一遍：6 遍；
    融合后读一遍写一遍：2 遍。（PyTorch 急切执行的掩码 masked_fill 还要读掩码，掩码只有 T² 个布尔值，忽略。）
（2）“残差加法 + 层归一化”：N = B·T·d 个数（d = 384）。急切执行：加法读 x、r 写 s，层归一化读 s 写 y，共 5 遍；
    融合：读 x、r，写 s、y，共 4 遍——残差流 s 本身后面还要用，必须写回，所以只省一遍。"""
from _ch8 import A10
from bookout import out

B, h, T, d = 32, 6, 256, 384
S = B * h * T * T * 4
N = B * T * d * 4
us = lambda b: b / A10["bw"] * 1e6
out(S_MB=S / 1e6, attn_eager_us=us(6 * S), attn_fused_us=us(2 * S), attn_ratio=3.0,
    N_MB=N / 1e6, ln_eager_us=us(5 * N), ln_fused_us=us(4 * N), ln_ratio=5 / 4)
