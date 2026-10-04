"""程序 4.9.1：用 Numba 写 CUDA 核函数。构建机上没有 GPU，用 Numba 自带的 CUDA 模拟器（NUMBA_ENABLE_CUDASIM=1）在 CPU 上
逐个线程执行同样的核函数，核对结果；在 GPU 上运行时去掉这一行即可，代码不用改。"""
import os

os.environ.setdefault("NUMBA_ENABLE_CUDASIM", "1")

import numpy as np                                   # noqa: E402
from numba import cuda, float32                      # noqa: E402

from _ch4 import THR, gray                           # noqa: E402
from bookout import out                              # noqa: E402


@cuda.jit
def vadd(a, b, c):
    i = cuda.grid(1)                                 # 等于 blockIdx.x * blockDim.x + threadIdx.x
    if i < c.size:
        c[i] = a[i] + b[i]


@cuda.jit
def gray_mask(rgb, mask, thr):
    col, row = cuda.grid(2)                          # 二维：先 x（列）后 y（行），与 CUDA C 相同
    if row < mask.shape[0] and col < mask.shape[1]:
        # 与 C 版相同，用单精度计算（Python 的小数默认是双精度，舍入可能差一个灰度级）
        v = float32(0.299) * float32(rgb[row, col, 0]) + float32(0.587) * float32(rgb[row, col, 1]) + float32(0.114) * float32(rgb[row, col, 2])
        mask[row, col] = 1 if int(v + float32(0.5)) <= thr else 0


n = 1000
a = np.arange(n, dtype=np.float32)
b = np.ones(n, dtype=np.float32)
c = np.zeros(n, dtype=np.float32)
threads = 128
blocks = (n + threads - 1) // threads
vadd[blocks, threads](a, b, c)                       # 方括号里是启动配置：线程块数、每块线程数
assert np.array_equal(c, a + b)

# 灰度：取图像中暗斑边缘的 48×64 一小块（模拟器逐个线程执行，较慢）
from _ch4 import frame                               # noqa: E402
patch = frame()[1040:1088, 1968:2032].copy()           # 跨过暗斑下边缘的一块
mask = np.zeros(patch.shape[:2], np.uint8)
gray_mask[(4, 3), (16, 16)](patch, mask, THR)    # 4×3 个线程块（x 方向 64 列、y 方向 48 行）
ref = (gray(patch) <= THR).astype(np.uint8)
assert np.array_equal(mask, ref)
out(n=n, blocks=blocks, threads=threads, patch_px=patch.shape[0] * patch.shape[1], dark=int(mask.sum()))
