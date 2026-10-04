"""算例 5.2.1—5.2.3：归约的五个版本。
（1）在 CPU 上按线程块、线程逐个模拟程序 5.2.1 中五个核函数的下标计算与执行顺序（小数组），与 NumPy 的和核对；
（2）线程块内树形归约每一层的活动线程、线程束的利用率（SIMT 效率）与共享内存的存储体冲突（GPU 执行模拟器部分 ④）；
（3）归约 2²⁵ 个单精度数的理论耗时（A10）。"""
import numpy as np

from _ch5 import A10, A10_SM
from bookout import out
from gpusim import banks

B = 256                                             # 每个线程块的线程数（与程序 5.2.1 相同）
LEVELS = int(np.log2(B))


# ---------- （1）逐线程模拟五个核函数（float32 运算）
def tree(sm, version):
    """线程块内的树形归约：sm 是共享内存（长度 B），按版本的下标规则逐层相加（每层之间相当于一次 __syncthreads）。"""
    sm = sm.copy()
    if version == 1:                                # 交错寻址，tid % (2s) == 0 的线程工作
        s = 1
        while s < B:
            for tid in range(B):
                if tid % (2 * s) == 0:
                    sm[tid] = np.float32(sm[tid] + sm[tid + s])
            s *= 2
    elif version == 2:                              # 交错寻址，前 B/(2s) 个线程工作，k = 2·s·tid
        s = 1
        while s < B:
            for tid in range(B):
                k = 2 * s * tid
                if k < B:
                    sm[k] = np.float32(sm[k] + sm[k + s])
            s *= 2
    else:                                           # 顺序寻址：前 s 个线程工作，加上后一半
        s = B // 2
        while s > 0:
            new = sm.copy()                         # 同一层中读的位置（tid + s ≥ s）与写的位置（tid < s）不重叠
            for tid in range(s):
                new[tid] = np.float32(sm[tid] + sm[tid + s])
            sm = new
            s //= 2
    return sm[0]


def shfl_down_sum(v):
    """线程束内的洗牌归约：每轮 lane 加上 lane + off 的值（越界时 __shfl_down_sync 返回自己的值）。只有 0 号线程的结果有用。"""
    v = v.astype(np.float32).copy()
    off = 16
    while off > 0:
        shifted = np.array([v[l + off] if l + off < 32 else v[l] for l in range(32)], np.float32)
        v = (v + shifted).astype(np.float32)
        off //= 2
    return v[0]


def block_shuffle(vals):
    """版本 5 的线程块内归约：8 个线程束各自洗牌求和，0 号线程把结果写进 sm[warp]；同步后 0 号线程束再洗牌一次。"""
    sm = np.zeros(32, np.float32)
    for w in range(B // 32):
        sm[w] = shfl_down_sum(vals[32 * w: 32 * w + 32])
    lane_vals = np.array([sm[l] if l < B // 32 else 0 for l in range(32)], np.float32)
    return shfl_down_sum(lane_vals)


def run(x, version, grid=None):
    """模拟一次完整的归约：第一个核函数得到每个线程块的部分和，第二个核函数（版本 5，一个线程块）把部分和加起来。"""
    n = len(x)
    if version <= 3:
        nb = (n + B - 1) // B
        part = []
        for b in range(nb):
            sm = np.array([x[b * B + t] if b * B + t < n else 0 for t in range(B)], np.float32)
            part.append(tree(sm, version))
    else:
        nb = grid
        acc = np.zeros(nb * B, np.float32)          # 网格跨步循环：线程 g 加 x[g]、x[g + nb·B]、……
        for i in range(n):
            g = i % (nb * B)
            acc[g] = np.float32(acc[g] + x[i])
        part = [tree(acc[b * B:(b + 1) * B], 3) if version == 4 else block_shuffle(acc[b * B:(b + 1) * B]) for b in range(nb)]
    part = np.array(part, np.float32)
    acc = np.zeros(B, np.float32)                   # 第二个核函数：一个线程块，网格跨步把部分和加到 256 个线程上
    for i, v in enumerate(part):
        acc[i % B] = np.float32(acc[i % B] + v)
    return block_shuffle(acc)


rng = np.random.default_rng(5)
x = rng.integers(0, 1000, 6000).astype(np.float32) / np.float32(1000)
exact = float(np.sum(x.astype(np.float64)))
errs = [abs(float(run(x, v, grid=5)) - exact) / exact for v in range(1, 6)]
assert max(errs) < 1e-6, errs

# ---------- （2）树形归约每一层：活动线程、发出加法指令的线程束、存储体冲突
rows = []
for v in (1, 2, 3):
    levels = []
    strides = [2 ** l for l in range(LEVELS)] if v in (1, 2) else [B // 2 ** (l + 1) for l in range(LEVELS)]
    for s in strides:
        if v == 1:
            act = [t for t in range(B) if t % (2 * s) == 0]
            words = {t: [t, t + s] for t in act}
        elif v == 2:
            act = [t for t in range(B) if 2 * s * t < B]
            words = {t: [2 * s * t, 2 * s * t + s] for t in act}
        else:
            act = list(range(s))
            words = {t: [t, t + s] for t in act}
        warps = sorted({t // 32 for t in act})
        ways = max(banks([words[t][0] for t in act if t // 32 == w])["ways"] for w in warps)
        levels.append({"s": s, "active": len(act), "warps": len(warps), "ways": ways})
    issued = sum(l["warps"] for l in levels)        # 每层每个有活动线程的线程束发一次加法
    active = sum(l["active"] for l in levels)
    passes = sum(l["warps"] * l["ways"] for l in levels)   # 共享内存的读要分几次完成（按第一个操作数计）
    rows.append({"v": v, "levels": levels, "issued": issued, "eff": active / (32 * issued), "passes": passes})
v1, v2, v3 = rows

# ---------- （3）理论耗时：2^25 个单精度数，每个读一次
n = 2 ** 25
t_min_us = n * 4 / A10["bw"] * 1e6
part_v1 = n // B
sms = A10["sm"]
fit = min(A10_SM["max_blocks"], A10_SM["max_warps"] * 32 // B)   # 每个 SM 能同时驻留的 256 线程的线程块：6 个
g_blocks = sms * fit                                # 版本 4、5 的线程块个数：正好一波
g_threads = g_blocks * B
per_thread = n / g_threads
out(B=B, levels=LEVELS, n_emul=len(x), err_max=max(errs),
    v1_issued=v1["issued"], v1_eff=100 * v1["eff"], v2_issued=v2["issued"], v2_eff=100 * v2["eff"], v3_issued=v3["issued"], v3_eff=100 * v3["eff"],
    v1_l1_warps=v1["levels"][0]["warps"], v1_l1_active=v1["levels"][0]["active"],
    v2_l1_ways=v2["levels"][0]["ways"], v2_l2_ways=v2["levels"][1]["ways"], v2_l3_ways=v2["levels"][2]["ways"], v2_l4_ways=v2["levels"][3]["ways"],
    v1_passes=v1["passes"], v2_passes=v2["passes"], v3_passes=v3["passes"],
    n_M=n / 2 ** 20, MB=n * 4 / 1e6, t_min_us=t_min_us, part_v1=part_v1, sms=sms, g_blocks=g_blocks, g_threads=g_threads, per_thread=per_thread, fit=fit)
