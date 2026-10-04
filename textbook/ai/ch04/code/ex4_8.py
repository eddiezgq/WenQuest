"""算例 4.8.1、4.8.2：数据竞争——两个线程同时“读—加一—写”，有一次加法丢失；暗斑检测的直方图与原子操作的争用。"""
import numpy as np

from _ch4 import frame, gray
from bookout import out

# 算例 4.8.1：两个线程把同一个计数器加 1，指令交错：A 读、B 读、A 写、B 写
counter = 5
a_reg = counter
b_reg = counter
counter = a_reg + 1
counter = b_reg + 1
lost = 7 - counter                                  # 应得 7

# 算例 4.8.2：灰度直方图（256 个箱）。同一个线程束 32 个相邻像素有几个落进同一个箱——原子加法要排队的次数
y = gray(frame()).ravel()
hist = np.bincount(y, minlength=256)
warps = y[: (len(y) // 32) * 32].reshape(-1, 32)
same_bin = np.array([np.max(np.bincount(w, minlength=256)) for w in warps[::97]])   # 抽样
mean_serial = float(same_bin.mean())
blocks = 132 * 4                                     # 网格跨步：每个 SM 4 个线程块，每个线程处理许多像素
global_atomics = len(y)
private_atomics = blocks * 256                      # 每个线程块先在共享内存里统计，最后各把 256 个箱加到全局
out(counter=counter, lost=lost, bins_used=int((hist > 0).sum()), top_bin=int(hist.argmax()), top_count=int(hist.max()),
    px=len(y), mean_serial=mean_serial, global_atomics_M=global_atomics / 1e6, private_atomics_M=private_atomics / 1e6,
    reduce=global_atomics / private_atomics, blocks=blocks)
