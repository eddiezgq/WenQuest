"""7.5.3 节与算例 7.5.1：张量的步长视图；显存缓存分配器（报告的显存以 10⁶ 字节为 1 MB，与全章一致）。
（1）一个张量 = 一块存储 + 形状 + 步长 + 起点。转置、切片、改形状只改后三者，不搬数据；元素 (i, j, …) 在存储中的位置是
    起点 + Σ 下标 × 步长。这里用几行 Python 写一个最小的张量，与 NumPy 逐元素核对，并检验“转置之后不再连续、批量矩阵乘法前要复制”。
（2）PyTorch 的缓存分配器（简化，规则按 PyTorch 2.x 的 CUDACachingAllocator）：
    - 请求的大小向上取整到 512 字节的倍数；不超过 1 MB 的走“小块池”，否则走“大块池”；
    - 池里有合适的空闲块（取够用的最小一块）就直接用，多余的部分切下来留在池里（小块池剩余不少于 512 B、大块池剩余超过 1 MB 才切）；
    - 没有才向驱动要一整段（cudaMalloc）：小块池每次要 2 MB；大块池不到 10 MB 的请求每次要 20 MB，更大的向上取整到 2 MB 的倍数；
    - 释放时块回到池里，与同一段中相邻的空闲块合并，不还给驱动（除非调用 torch.cuda.empty_cache()）。
    用第 2 章小型 Transformer 一个训练步的激活（_ch7.saved_activations）模拟三个训练步：前向依次分配各层保存的张量，
    反向逐层倒序释放，每层另有一块与该层最大张量同样大的临时梯度。数一数每步调用了几次 cudaMalloc。"""
import numpy as np

from _ch7 import L, saved_activations, saved_head
from bookout import out


class Tensor:
    def __init__(self, storage, shape, stride, offset=0):
        self.storage, self.shape, self.stride, self.offset = storage, tuple(shape), tuple(stride), offset

    @staticmethod
    def arange(*shape):
        st, s = [], 1
        for n in reversed(shape):
            st.insert(0, s)
            s *= n
        return Tensor(list(range(s)), shape, st)

    def __getitem__(self, idx):
        return self.storage[self.offset + sum(i * s for i, s in zip(idx, self.stride))]

    def transpose(self, a, b):
        sh, st = list(self.shape), list(self.stride)
        sh[a], sh[b], st[a], st[b] = sh[b], sh[a], st[b], st[a]
        return Tensor(self.storage, sh, st, self.offset)

    def narrow(self, dim, start, length):                  # 切片 x[..., start:start+length, ...]
        sh = list(self.shape)
        sh[dim] = length
        return Tensor(self.storage, sh, self.stride, self.offset + start * self.stride[dim])

    def is_contiguous(self):
        s = 1
        for n, st in zip(reversed(self.shape), reversed(self.stride)):
            if n != 1 and st != s:
                return False
            s *= n
        return True

    def numpy(self):
        return np.array([self[i] for i in np.ndindex(*self.shape)]).reshape(self.shape)


x = Tensor.arange(2, 3, 4)                                  # 形状 (2, 3, 4)，步长 (12, 4, 1)
ref = np.arange(24).reshape(2, 3, 4)
xt = x.transpose(1, 2)                                      # (2, 4, 3)，步长 (12, 1, 4)：同一块存储
xs = x.narrow(2, 1, 2)                                      # x[:, :, 1:3]
ok_view = (np.array_equal(xt.numpy(), ref.transpose(0, 2, 1)) and np.array_equal(xs.numpy(), ref[:, :, 1:3])
           and xt.storage is x.storage and x.is_contiguous() and not xt.is_contiguous() and not xs.is_contiguous())


# ---------------------------------------------------------------- 缓存分配器
MB = 1 << 20                                                # 分配器的各个门槛按 2 的幂（MiB）


class Caching:
    def __init__(self):
        self.free = {"small": [], "large": []}              # [(段号, 起点, 大小)]
        self.blocks = {}                                    # 句柄 → (池, 段号, 起点, 大小)
        self.segments = []                                  # 每段的大小
        self.mallocs = 0
        self.allocated = self.peak = 0
        self.next = 0

    @staticmethod
    def round(n):
        return max(512, (n + 511) // 512 * 512)

    def malloc(self, n):
        n = self.round(n)
        pool = "small" if n <= MB else "large"
        fits = [b for b in self.free[pool] if b[2] >= n]
        if fits:
            blk = min(fits, key=lambda b: b[2])
            self.free[pool].remove(blk)
        else:
            seg = 2 * MB if pool == "small" else 20 * MB if n < 10 * MB else (n + 2 * MB - 1) // (2 * MB) * (2 * MB)
            self.segments.append(seg)
            self.mallocs += 1
            blk = (len(self.segments) - 1, 0, seg)
        sid, start, sz = blk
        rest = sz - n
        if (rest >= 512) if pool == "small" else (rest > MB):
            self.free[pool].append((sid, start + n, rest))
            sz = n
        h = self.next
        self.next += 1
        self.blocks[h] = (pool, sid, start, sz)
        self.allocated += sz
        self.peak = max(self.peak, self.allocated)
        return h

    def release(self, h):
        pool, sid, start, sz = self.blocks.pop(h)
        self.allocated -= sz
        fl = self.free[pool]
        for b in [b for b in fl if b[0] == sid and (b[1] + b[2] == start or start + sz == b[1])]:   # 与相邻的空闲块合并
            fl.remove(b)
            start, sz = min(start, b[1]), sz + b[2]
        fl.append((sid, start, sz))


def step(alloc, nbytes):
    saved = []
    for _ in range(L):                                      # 前向：各层保存的张量依次分配，留到反向
        saved.append([alloc.malloc(nbytes(e)) for _, e in saved_activations()])
    head = [alloc.malloc(nbytes(e)) for _, e in saved_head()]
    for h in head:
        alloc.release(h)
    for hs in reversed(saved):                              # 反向：每层一块临时梯度，用完与该层的激活一起释放
        g = alloc.malloc(nbytes(max(e for _, e in saved_activations())))
        for h in hs:
            alloc.release(h)
        alloc.release(g)


A = Caching()
per = []
for it in range(3):
    m0 = A.mallocs
    step(A, lambda e: 4 * e)
    per.append(A.mallocs - m0)
reqs = (len(saved_activations()) + 1) * L + len(saved_head())
out(ok_view=ok_view, xt_stride=str(xt.stride), reqs=reqs, mallocs_1=per[0], mallocs_2=per[1], mallocs_3=per[2],
    peak_MB=A.peak / 1e6, reserved_MB=sum(A.segments) / 1e6, waste_pct=100 * (sum(A.segments) - A.peak) / sum(A.segments))
