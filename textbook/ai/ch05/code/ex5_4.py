"""算例 5.4.1、5.4.2：直方图与原子操作的争用。三种输入——均匀随机的字节、检测相机的灰度图、全部相同的字节（最坏情形）：
一个线程束的 32 个相邻元素中，落进同一个箱的最多有几个（同一地址的原子操作要排队的轮数）、共落进几个不同的箱（线程束内先合并、
每个箱只做一次原子操作时的次数）。随机字节与 code/runs/run5_4/hist.cu 用同一个 splitmix64 生成。"""
import numpy as np

from _ch5 import gray, frame, splitmix64
from bookout import out

g = gray(frame()).ravel()
n = len(g)
inputs = {"rand": (splitmix64(np.arange(n)) % np.uint64(256)).astype(np.uint8), "cam": g, "const": np.full(n, 128, np.uint8)}
stats = {}
for k, d in inputs.items():
    w = d[: n // 32 * 32].reshape(-1, 32)[::97]                     # 抽样（与程序 4.8.1 相同）
    counts = np.array([np.bincount(r, minlength=256) for r in w])
    stats[k] = dict(maxmul=float(counts.max(axis=1).mean()), distinct=float((counts > 0).sum(axis=1).mean()))
# 均匀随机时的理论值：32 个数落进 256 个箱，不同的箱数的期望 = 256 (1 − (255/256)^32)
distinct_theory = 256 * (1 - (255 / 256) ** 32)
nbins_cam = int((np.bincount(g, minlength=256) > 0).sum())
out(rand_max=stats["rand"]["maxmul"], rand_distinct=stats["rand"]["distinct"], cam_max=stats["cam"]["maxmul"], cam_distinct=stats["cam"]["distinct"],
    const_max=stats["const"]["maxmul"], const_distinct=stats["const"]["distinct"], distinct_theory=distinct_theory, nbins_cam=nbins_cam,
    cam_saving=32 / stats["cam"]["distinct"], n_M=4 * n / 1e6)
