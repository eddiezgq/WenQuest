"""算例 5.3.1—5.3.3：前缀和。
（1）希利斯—斯蒂尔扫描与布莱洛赫扫描的加法次数与步数，与 NumPy 的 cumsum 核对；
（2）在 CPU 上按线程束、线程块逐个模拟程序 5.3.1 的三段式扫描（线程束内 __shfl_up_sync，线程块之间递归扫描各块的和再加回），核对结果；
（3）三段式扫描与单遍扫描的显存搬运量；
（4）流压缩：用排他前缀和把测试图中的暗斑像素收集成一个列表。"""
import numpy as np

from _ch5 import A10, THR, frame, gray
from bookout import out


def hillis_steele(x):
    """每一步每个位置加上相隔 d 的位置（d = 1, 2, 4, …）。返回包含式前缀和、加法次数、步数。"""
    y, adds, steps, d = x.copy(), 0, 0, 1
    while d < len(y):
        y[d:] = y[d:] + y[:-d]                      # 右边是这一步开始前的旧值（同一步中所有位置同时更新）
        adds += len(y) - d
        steps += 1
        d *= 2
    return y, adds, steps


def blelloch(x):
    """上扫（建和树）+ 下扫（分发前缀），得到排他前缀和。n 须为 2 的幂。返回结果、加法次数、步数。"""
    n = len(x)
    a, adds, steps = x.copy(), 0, 0
    d = 1
    while d < n:                                    # 上扫：a[k + 2d − 1] += a[k + d − 1]
        idx = np.arange(0, n, 2 * d)
        a[idx + 2 * d - 1] += a[idx + d - 1]
        adds += len(idx)
        steps += 1
        d *= 2
    a[n - 1] = 0
    d = n // 2
    while d >= 1:                                   # 下扫：左子 ← 父，右子 ← 父 + 左子
        idx = np.arange(0, n, 2 * d)
        left = a[idx + d - 1].copy()
        a[idx + d - 1] = a[idx + 2 * d - 1]
        a[idx + 2 * d - 1] += left
        adds += len(idx)
        steps += 1
        d //= 2
    return a, adds, steps


x16 = np.array([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3])
hs16, hs_adds16, hs_steps16 = hillis_steele(x16)
bl16, bl_adds16, bl_steps16 = blelloch(x16)
assert (hs16 == np.cumsum(x16)).all() and (bl16 == np.cumsum(x16) - x16).all()
n_big = 2 ** 20
xb = np.arange(n_big) % 7
_, hs_adds, hs_steps = hillis_steele(xb)
_, bl_adds, bl_steps = blelloch(xb)

# ---------- （2）模拟程序 5.3.1
B = 1024


def warp_scan(v):
    """__shfl_up_sync 的包含式扫描：lane ≥ d 的线程加上 lane − d 的值（d = 1, 2, 4, 8, 16）。"""
    v = v.copy()
    for d in (1, 2, 4, 8, 16):
        up = np.concatenate([v[:d], v[:-d]])        # lane < d 时 __shfl_up_sync 返回自己的值，但不加
        v = np.where(np.arange(32) >= d, v + up, v)
    return v


def scan_blocks(x, n):
    nb = (n + B - 1) // B
    y, sums = np.zeros(n, np.int64), np.zeros(nb, np.int64)
    for b in range(nb):
        v = np.array([x[b * B + t] if b * B + t < n else 0 for t in range(B)], np.int64)
        v = np.concatenate([warp_scan(v[32 * w:32 * w + 32]) for w in range(B // 32)])
        ws = warp_scan(v[31::32])                   # 每个线程束的最后一个线程把本线程束的和写进 ws；0 号线程束扫描 ws
        v[32:] += np.repeat(ws[:-1], 32)            # 第 w 个线程束加上前 w 个线程束的和
        m = min(B, n - b * B)
        y[b * B:b * B + m] = v[:m]
        sums[b] = v[B - 1]
    return y, sums


def scan(x, n, launches):
    nb = (n + B - 1) // B
    y, sums = scan_blocks(x, n)
    launches.append(("scan_blocks", nb))
    if nb == 1:
        return y
    sums = scan(sums, nb, launches)
    for b in range(1, nb):                          # add_offsets
        y[b * B:(b + 1) * B] += sums[b - 1]
    launches.append(("add_offsets", nb))
    return y


xs = (np.arange(1_100_000) * 2654435761 % 4).astype(np.int64)
L = []
assert (scan(xs, len(xs), L) == np.cumsum(xs)).all()
levels = sum(1 for k, _ in L if k == "scan_blocks")

# ---------- （3）显存搬运量（以输入的字节数为单位）
n = 2 ** 24
nb1 = n // B
three_phase = (2 + 2 * (1 / B) + 2 * (1 / B ** 2)) + 2   # scan_blocks 读写各一遍（加各级的和），add_offsets 读写各一遍
single_pass = 2
t_min_us = n * 4 * 2 / A10["bw"] * 1e6

# ---------- （4）流压缩：暗斑像素的坐标列表
g = gray(frame()).ravel()
flag = (g < THR).astype(np.int64)
pos = np.cumsum(flag) - flag                        # 排他前缀和 = 每个暗像素在输出列表中的位置
count = int(flag.sum())
lst = np.zeros(count, np.int64)
lst[pos[flag == 1]] = np.nonzero(flag)[0]
assert (lst == np.nonzero(flag)[0]).all()
out(hs_adds16=hs_adds16, hs_steps16=hs_steps16, bl_adds16=bl_adds16, bl_steps16=bl_steps16,
    n_big_log=20, hs_adds_M=hs_adds / 1e6, hs_steps=hs_steps, bl_adds_M=bl_adds / 1e6, bl_steps=bl_steps, seq_adds_M=(n_big - 1) / 1e6,
    hs_ratio=hs_adds / (n_big - 1), B=B, n_emul=len(xs), levels_emul=levels, launches_emul=len(L),
    n_M=n / 2 ** 20, nb1=nb1, three_phase=three_phase, single_pass=single_pass, t_min_us=t_min_us,
    dark=count, px_M=len(g) / 1e6, first_dark=int(lst[0]), first_row=int(lst[0]) // 3840, first_col=int(lst[0]) % 3840)
