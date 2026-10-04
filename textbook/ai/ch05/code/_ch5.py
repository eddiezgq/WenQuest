"""第 5 章共用。以下划线开头，构建时不单独运行。

- frame()、gray()：检测相机的合成测试图与灰度化，与第 4 章 _ch4.py、程序 4.2.1（gray.cu）的规则完全相同（这里抄一份，
  因为各章的程序互不导入）；
- splitmix64()：与 code/runs/ 中 CUDA 程序生成测试数据的规则相同的伪随机数；
- A10：实测所用的显卡（云端 basic 档）的规格，取自 conventions/gpus.py；另加数据手册上的 TF32 张量核心峰值。
"""
import numpy as np

from gpus import GPUS

W, H, THR = 3840, 2160, 40

A10 = dict(GPUS["a10"])
A10["tf32t"] = 62.5e12        # TF32 张量核心，稠密（计入稀疏为 125 TFLOP/s；NVIDIA A10 数据手册）
# A10 是计算能力 8.6：每个 SM 65 536 个 32 位寄存器、最多 48 个线程束（1536 个线程）、16 个线程块、共享内存最多 100 KB
# （CUDA C++ Programming Guide，“Compute Capabilities”）
A10_SM = dict(regs=65536, max_warps=48, max_blocks=16, smem=100 * 1024)


def frame():
    """RGB 各 8 位的一帧：渐变底色，中心在（第 1000 行，第 2000 列）、半径 60 像素的暗斑。"""
    r, c = np.mgrid[0:H, 0:W]
    spot = (r - 1000) ** 2 + (c - 2000) ** 2 < 60 * 60
    rgb = np.empty((H, W, 3), np.uint8)
    rgb[..., 0] = np.where(spot, 20, 120 + c % 100)
    rgb[..., 1] = np.where(spot, 25, 130 + r % 80)
    rgb[..., 2] = np.where(spot, 30, 140)
    return rgb


def gray(rgb):
    """Y = 0.299 R + 0.587 G + 0.114 B，单精度计算，加 0.5 取整。"""
    f = rgb.astype(np.float32)
    v = np.float32(0.299) * f[..., 0] + np.float32(0.587) * f[..., 1] + np.float32(0.114) * f[..., 2]
    return (v + np.float32(0.5)).astype(np.uint8)


def splitmix64(i):
    """第 i 个伪随机数（64 位无符号），i 可以是 NumPy 数组。与 CUDA 程序中的 splitmix64(i) 逐位相同。"""
    with np.errstate(over="ignore"):
        z = np.asarray(i, dtype=np.uint64) * np.uint64(0x9E3779B97F4A7C15) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        return z ^ (z >> np.uint64(31))


def uniform(i):
    """(0, 1] 上的均匀分布：取高 53 位。"""
    return ((splitmix64(i) >> np.uint64(11)).astype(np.float64) + 1.0) / 2.0 ** 53
