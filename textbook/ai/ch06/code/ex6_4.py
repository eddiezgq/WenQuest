"""算例 6.4.1—6.4.3：全归约的算法与代价。
（1）在 CPU 上逐步模拟环形全归约（先归约—散播、再全收集），p 块 GPU 各有一个数组，核对每块最后都得到总和，并统计每步每块发送的数据量；
（2）α–β 模型（每发一次消息延迟 α，带宽 β）下三种算法的耗时：
    朴素（都发给 0 号、加好再发回）：2(p − 1)(α + n/β)（0 号的链路是瓶颈）；
    环形：2(p − 1)α + 2(p − 1)/p · n/β；
    树形（两棵互补的二叉树，分块流水线）：约 2 log₂p · α + 2n/β（理想流水线下的近似，忽略分块带来的额外延迟；
    延迟只随 log₂p 增长；大消息时比环形略慢）。
    网络本身不做计算时，任何全归约算法每块 GPU 至少要发出 2(p − 1)/p · n 字节，环形正好达到这个下限。
（3）数据并行训练的梯度：小型 Transformer（46 MB）与 70 亿参数一级的模型（14 GB），8 块 A100（NVSwitch，每个方向 300 GB/s）。
α 取 2 μs（机器内 NVLink 上一次通信的量级，作估算用；可以用程序 6.4.1 实测的小消息耗时反推）。"""
import math

import numpy as np

from bookout import out
from gpus import NVLINK, IB


def ring_allreduce(xs):
    """xs: p 个长度相同的数组。返回每块 GPU 的结果与每步每块发送的元素数。数组切成 p 块，第 r 块 GPU 第 s 步发出第 (r − s) mod p 块。"""
    p = len(xs)
    bufs = [np.array_split(x.astype(np.float64).copy(), p) for x in xs]
    sent = []
    for s in range(p - 1):                       # 归约—散播：每步把收到的块加到自己的同一块上
        msgs = [(r, (r - s) % p, bufs[r][(r - s) % p].copy()) for r in range(p)]
        for r, c, data in msgs:
            bufs[(r + 1) % p][c] += data
        sent.append(max(len(m[2]) for m in msgs))
    for s in range(p - 1):                       # 全收集：第 r 块 GPU 此时有完整的第 (r + 1) mod p 块，沿环传下去
        msgs = [(r, (r + 1 - s) % p, bufs[r][(r + 1 - s) % p].copy()) for r in range(p)]
        for r, c, data in msgs:
            bufs[(r + 1) % p][c] = data
        sent.append(max(len(m[2]) for m in msgs))
    return [np.concatenate(b) for b in bufs], sent


rng = np.random.default_rng(6)
p, n = 8, 1000
xs = [rng.standard_normal(n) for _ in range(p)]
res, sent = ring_allreduce(xs)
total = sum(xs)
assert all(np.allclose(r, total) for r in res)
steps = len(sent)
per_gpu = sum(sent)                              # 每块 GPU 一共发出的元素数 ≈ 2(p − 1)/p · n

alpha = 2e-6
beta = NVLINK["a100"]


def t_naive(nb, p):
    return 2 * (p - 1) * (alpha + nb / beta)


def t_ring(nb, p):
    return 2 * (p - 1) * alpha + 2 * (p - 1) / p * nb / beta


def t_tree(nb, p):
    return 2 * math.log2(p) * alpha + 2 * nb / beta


small = 11_532_288 * 4
big = 7e9 * 2
tiny = 8 * 1024
rows = {}
for name, nb in (("tiny", tiny), ("small", small), ("big", big)):
    for alg, f in (("naive", t_naive), ("ring", t_ring), ("tree", t_tree)):
        rows[f"{name}_{alg}_ms"] = f(nb, p) * 1e3
naive_over_ring = t_naive(big, p) / t_ring(big, p)
busbw_ring = small / t_ring(small, p) * 2 * (p - 1) / p / 1e9
# 跨机器：16 台 × 8 块，机器之间每块 GPU 一块 NDR 网卡（50 GB/s）；层次化全归约的机器间部分按环形、带宽取网卡计
beta_ib = IB["ndr"]
t_inter = 2 * (16 - 1) * alpha + 2 * (16 - 1) / 16 * (big / 8) / beta_ib    # 每块 GPU 只负责 1/8 的数据在机器之间做环形全归约
out(p=p, n_emul=n, steps=steps, per_gpu=per_gpu, per_gpu_frac=per_gpu / n, ring_frac=2 * (p - 1) / p, alpha_us=alpha * 1e6, beta_GBs=beta / 1e9,
    small_MB=small / 1e6, big_GB=big / 1e9, tiny_KB=tiny / 1024, **rows, busbw_ring=busbw_ring, naive_over_ring=naive_over_ring, eq_MB=p * alpha * beta / 1e6, inter_ms=t_inter * 1e3,
    ib_GBs=beta_ib / 1e9)
