"""算例 4.2.1～4.2.3：二维索引的计算；一帧 4K 图像的网格；在 CPU 上算出灰度与暗斑像素数，作为 GPU 结果的参照。

式 (4.2.1)：i = blockIdx.x · blockDim.x + threadIdx.x；式 (4.2.2)：线程块数 = ⌈n / b⌉；
式 (4.2.3)：col = blockIdx.x · blockDim.x + threadIdx.x，row = blockIdx.y · blockDim.y + threadIdx.y，像素 p = row · w + col。
"""
import math

import numpy as np

from _ch4 import H, THR, W, frame, gray
from bookout import out

# 算例 4.2.1：线程块 (3, 2) 中的线程 (5, 7)，线程块 16×16
bx, by, tx, ty, bdx, bdy = 3, 2, 5, 7, 16, 16
col, row = bx * bdx + tx, by * bdy + ty
p = row * W + col

# 算例 4.2.2：网格
gx, gy = math.ceil(W / 16), math.ceil(H / 16)
blocks = gx * gy
idle = gx * gy * 256 - W * H

# 算例 4.2.3：CPU 参照
rgb = frame()
y = gray(rgb)
dark = int((y <= THR).sum())
y_spot = int(y[1000, 2000])
y_min_bg = int(y[(y > THR)].min())
assert dark == 11277                                    # code/runs/run4_1/run.py 核对 GPU 结果时用的就是这个数

# 网格跨步循环：一个只启动 grid 个线程块的核函数处理任意长的数组
n_big, grid_small = 10 ** 9, 132 * 8
per_thread = math.ceil(n_big / (grid_small * 256))
out(bx=bx, by=by, tx=tx, ty=ty, col=col, row=row, p=p, W=W, H=H, gx=gx, gy=gy, blocks=blocks, idle=idle, px=W * H,
    px_M=W * H / 1e6, dark=dark, y_spot=y_spot, y_min_bg=y_min_bg, thr=THR, n_big_e="10^{9}", grid_small=grid_small,
    per_thread=per_thread)
