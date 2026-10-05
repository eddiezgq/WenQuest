"""程序 7.5.2：PyTorch 一次运算的开销与缓存分配器（7.5 节）。
（1）对一个只有 1 个数的张量连续做 N 次加法：主机上每次调用花多少时间（Python → 分派器 → ATen → 启动核函数），
    GPU 上平均每次多少时间。核函数本身几乎不花时间，两者之差说明 GPU 在等主机。三种情形：不记录梯度（torch.no_grad）、
    要记录梯度（张量 requires_grad，分派器先经过自动微分这一层）、以及用 torch.add(x, 1, out=y) 免去分配输出。
（2）缓存分配器：同样大小（64 MB）的张量，清空缓存后第一次分配（要调用 cudaMalloc）与以后各次（从缓存里取）各要多久。
（3）小型 Transformer 连续三个训练步：每步调用了几次 cudaMalloc（memory_stats 的 segment.all.allocated 的增量）、
    分配了几次张量（allocation.all.allocated 的增量）；已分配的峰值与分配器保留的显存。与程序 7.5.1 的模拟对照。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import time

import torch

import model

dev = "cuda"
N = 20000


def per_op(fn):
    for _ in range(100):
        fn()
    torch.cuda.synchronize()
    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    t = time.perf_counter()
    e0.record()
    for _ in range(N):
        fn()
    host = time.perf_counter() - t                          # 主机发出 N 次调用所花的时间（GPU 可能还在执行）
    e1.record()
    e1.synchronize()
    return host / N * 1e6, e0.elapsed_time(e1) / N * 1e3    # μs


x = torch.zeros(1, device=dev)
y = torch.empty_like(x)
xg = torch.zeros(1, device=dev, requires_grad=True)
with torch.no_grad():
    host_ng, gpu_ng = per_op(lambda: x + 1)
host_g, gpu_g = per_op(lambda: xg + 1)
with torch.no_grad():
    host_out, gpu_out = per_op(lambda: torch.add(x, 1, out=y))

# （2）分配：清空缓存后第一次与以后各次
nbytes = 64 << 20
torch.cuda.synchronize()
torch.cuda.empty_cache()
t = time.perf_counter()
a = torch.empty(nbytes, dtype=torch.uint8, device=dev)
first_us = (time.perf_counter() - t) * 1e6
del a
ts = []
for _ in range(1000):
    t = time.perf_counter()
    a = torch.empty(nbytes, dtype=torch.uint8, device=dev)
    ts.append(time.perf_counter() - t)
    del a
ts.sort()
cached_us = ts[len(ts) // 2] * 1e6

# （3）三个训练步
torch.manual_seed(0)
torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()
m = model.Tiny().to(dev)
opt = torch.optim.AdamW(m.parameters(), lr=1e-4)
ids = torch.randint(0, model.V, (32, model.T), device=dev)
segs, allocs = [], []
for it in range(3):
    s0 = torch.cuda.memory_stats()
    loss = model.loss_fn(m(ids), ids)
    loss.backward()
    opt.step()
    opt.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    s1 = torch.cuda.memory_stats()
    segs.append(s1["segment.all.allocated"] - s0["segment.all.allocated"])
    allocs.append(s1["allocation.all.allocated"] - s0["allocation.all.allocated"])
out = dict(host_ng_us=host_ng, gpu_ng_us=gpu_ng, host_g_us=host_g, gpu_g_us=gpu_g, host_out_us=host_out, gpu_out_us=gpu_out,
           first_us=first_us, cached_us=cached_us, segs_1=segs[0], segs_2=segs[1], segs_3=segs[2], allocs_1=allocs[0],
           allocs_2=allocs[1], peak_MB=torch.cuda.max_memory_allocated() / 1e6, reserved_MB=torch.cuda.memory_reserved() / 1e6,
           torch=torch.__version__)
json.dump(out, open("out.json", "w"))
print(out)
