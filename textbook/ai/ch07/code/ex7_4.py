"""7.4.3 节与算例 7.4.1：CuTe 的布局，CUTLASS 的分块层次。
（1）布局 = 形状 + 步长：把一个（可以嵌套的）坐标映射成内存中的位置，位置 = Σ 坐标分量 × 对应的步长。
    一维的整数坐标按“第一维变得最快”（列主序的次序）展开成多维坐标。这里用几十行 Python 写出 CuTe 布局最基本的部分：
    求大小、坐标到位置、整数到坐标，以及用它描述行主序、列主序、分块存放的矩阵，和第 5 章 regtile、vec 中“线程 → 它算的元素”的对应。
    核对：分块布局与 regtile、vec 的布局都恰好把每个元素映射一次（是一一对应）。
（2）CUTLASS 的一个典型配置（半精度，张量核心）：线程块分块 128×128×32，4 个线程束各算 64×64，张量核心指令 m16n8k16，
    3 级流水线。算出每个线程束每一步发多少条指令、每个线程的累加器有多少个、共享内存要多少、线程块这一级的计算强度。"""
from itertools import product
from math import prod

from _ch7 import A10
from bookout import out


def flat(t):
    return [x for e in t for x in flat(e)] if isinstance(t, tuple) else [t]


def size(shape):
    return prod(flat(shape))


def idx2crd(i, shape):
    """一维下标 → （嵌套的）坐标，第一维变得最快。"""
    if not isinstance(shape, tuple):
        return i
    crd = []
    for s in shape:
        crd.append(idx2crd(i % size(s), s))
        i //= size(s)
    return tuple(crd)


def crd2idx(crd, shape, stride):
    """坐标 → 位置。坐标可以比形状“浅”：某一维给的是整数，就先把它按那一维的形状展开。"""
    if isinstance(shape, tuple):
        if not isinstance(crd, tuple):
            crd = idx2crd(crd, shape)
        return sum(crd2idx(c, s, d) for c, s, d in zip(crd, shape, stride))
    return crd * stride


class Layout:
    def __init__(self, shape, stride):
        self.shape, self.stride = shape, stride

    def __call__(self, *crd):
        return crd2idx(crd if len(crd) > 1 else crd[0], self.shape, self.stride)

    def __len__(self):
        return size(self.shape)

    def image(self):
        return [self(i) for i in range(len(self))]


col = Layout((4, 8), (1, 4))          # 4×8 矩阵，列主序
row = Layout((4, 8), (8, 1))          # 行主序
ok_col = col(1, 2) == 1 + 2 * 4 and col.image() == list(range(32))
ok_row = row(1, 2) == 1 * 8 + 2 and sorted(row.image()) == list(range(32))
# 8×8 矩阵，每 4×4 一块，块内列主序，块按列主序排列：行坐标 = (块内行, 第几块行)，列坐标同理
tiled = Layout(((4, 2), (4, 2)), ((1, 16), (4, 32)))
ok_tiled = sorted(tiled.image()) == list(range(64))
blk = tiled((1, 1), (2, 0))           # 第 1 块行的第 1 行（全局第 5 行）、第 0 块列的第 2 列 → 第 1 块（列主序）里的 (1, 2)
ok_blk = blk == 16 + 1 + 2 * 4

# 第 5 章 regtile：128×128 的输出块，256 个线程排成 16×16，每个线程算 8×8 个元素，第 (ty, tx) 个线程算行 ty·8 + i、列 tx·8 + j。
# 写成布局：坐标 ((i, ty), (j, tx))，输出块按行主序存放（行步长 128）
reg = Layout(((8, 16), (8, 16)), ((128, 8 * 128), (1, 8)))
ok_reg = sorted(reg.image()) == list(range(128 * 128))
# 同一个线程的 64 个元素：固定 (ty, tx) = (3, 5)
mine = sorted(reg((i, 3), (j, 5)) for i, j in product(range(8), range(8)))
ok_mine = mine[0] == 3 * 8 * 128 + 5 * 8 and mine[-1] == (3 * 8 + 7) * 128 + 5 * 8 + 7

# 第 5 章 vec：线程负责的 8 列分成相隔 64 的两组，每组 4 列：列 = j + 4·tx + 64·g（行同理）。只是改了步长与嵌套
vec = Layout(((4, 2, 16), (4, 2, 16)), ((128, 64 * 128, 4 * 128), (1, 64, 4)))
ok_vec = sorted(vec.image()) == list(range(128 * 128))

# （2）CUTLASS 的分块层次
bm, bn, bk, wm, wn = 128, 128, 32, 64, 64
im, in_, ik = 16, 8, 16
warps = (bm // wm) * (bn // wn)
mma_per_k = (wm // im) * (wn // in_) * (bk // ik)
acc = wm * wn // 32
stages = 3
smem = (bm + bn) * bk * 2 * stages
flop_step = 2 * bm * bn * bk
bytes_step = (bm + bn) * bk * 2
intensity = flop_step / bytes_step
ridge = A10["fp16t"] / A10["bw"]

out(ok=ok_col and ok_row and ok_tiled and ok_blk and ok_reg and ok_mine and ok_vec, blk=blk,
    warps=warps, threads=warps * 32, mma_per_k=mma_per_k, acc=acc, stages=stages, smem_KB=smem / 1024,
    intensity=intensity, ridge=ridge)
