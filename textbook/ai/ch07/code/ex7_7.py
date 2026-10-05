"""算例 7.7.1：融合的“加偏置 + GELU”值不值得自己写。前馈网络第一层的输出 X（B·T × d_ff = 8192 × 1536，单精度）。
不融合（PyTorch 的写法 F.gelu(x + b)）：前向两个核函数，加法读 X 写 Z，GELU 读 Z 写 Y；反向 GELU 的反向读 dY 与 Z、写 dZ，
偏置的梯度对 dZ 按列求和（读一遍 dZ）；加法对 x 的梯度就是 dZ 本身，不用算。
融合：前向一个核函数读 X 写 Y；反向一个核函数读 dY 与 X、写 dX，偏置的梯度同样对 dX 按列求和。
两种写法为反向保存的都是一个 N 个数的张量（不融合存 Z，融合存 X），显存一样。
另核对 GELU（tanh 近似，与 2.9 节相同）的导数公式：与数值差分比较。"""
import numpy as np

from _ch7 import A10, B, F, T
from bookout import out

N = B * T * F
el = 4
unf_f, fus_f = 4 * N * el, 2 * N * el
unf_b, fus_b = 4 * N * el, 4 * N * el
us = lambda b: b / A10["bw"] * 1e6

c = np.sqrt(2 / np.pi)


def gelu(x):
    return 0.5 * x * (1 + np.tanh(c * (x + 0.044715 * x ** 3)))


def dgelu(x):
    u = np.tanh(c * (x + 0.044715 * x ** 3))
    return 0.5 * (1 + u) + 0.5 * x * (1 - u * u) * c * (1 + 3 * 0.044715 * x * x)


x = np.linspace(-6, 6, 1201)
h = 1e-5
err = float(np.max(np.abs((gelu(x + h) - gelu(x - h)) / (2 * h) - dgelu(x))))
out(N=N, MB=N * el / 1e6, unf_f_us=us(unf_f), fus_f_us=us(fus_f), unf_b_us=us(unf_b), fus_b_us=us(fus_b),
    speed_f=unf_f / fus_f, speed_all=(unf_f + unf_b) / (fus_f + fus_b), dgelu_err=err, a=0.044715)
