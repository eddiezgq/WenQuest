"""算例 1.6.1、1.6.2：向量加法核函数的线程数与耗时下限；三代 GPU 的算力与带宽增长。

式 (1.6.1)：i = blockIdx.x × blockDim.x + threadIdx.x；式 (1.6.2)：线程块数 = ⌈n / b⌉。
"""
import math

from _ch1 import HW, gtx580_peak
from bookout import out

# 算例 1.6.1：n = 5×10^7 个单精度数的向量加法 c = a + b
n = 5 * 10 ** 7
b = 256
blocks = math.ceil(n / b)
threads = blocks * b
idle = threads - n
W = n                                    # 每个元素一次加法
Q = 3 * 4 * n                            # 读 a、b，写 c，各 4 字节
I = W / Q
P32 = HW["h100"]["P_fp32"]
bw = HW["h100"]["bw"]
t_comp = W / P32
t_mem = Q / bw

# 算例 1.6.2：GTX 580（2010）→ H100（2022）
P580 = gtx580_peak()
bw580 = HW["gtx580"]["bw"]
years = HW["h100"]["year"] - HW["gtx580"]["year"]
r_fp32 = P32 / P580
r_tensor = HW["h100"]["P_fp16"] / P580
r_bw = bw / bw580
g_fp32 = r_fp32 ** (1 / years)
g_tensor = r_tensor ** (1 / years)
g_bw = r_bw ** (1 / years)
bal580 = P580 / bw580
bal_h32 = P32 / bw
bal_h16 = HW["h100"]["P_fp16"] / bw

out(n_e="5\\times10^{7}", b=b, blocks=blocks, idle=idle, I=I, t_comp_us=t_comp * 1e6, t_mem_us=t_mem * 1e6, Q_GB=Q / 1e9,
    P580_T=P580 / 1e12, bw580=bw580 / 1e9, years=years, r_fp32=r_fp32, r_tensor=r_tensor, r_bw=r_bw,
    g_fp32=g_fp32, g_tensor=g_tensor, g_bw=g_bw, bal580=bal580, bal_h32=bal_h32, bal_h16=bal_h16,
    P_a100_32=HW["a100"]["P_fp32"] / 1e12, P_a100_16=HW["a100"]["P_fp16"] / 1e12, bw_a100=HW["a100"]["bw"] / 1e12,
    P_h32=P32 / 1e12, P_h16=HW["h100"]["P_fp16"] / 1e12, bw_h=bw / 1e12)
