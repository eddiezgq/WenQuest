"""程序 7.8.2：torch.compile 前后（7.8 节）。小型 Transformer，单精度。
（1）训练：B = 32，T = 256，一次前向加反向的耗时；急切执行与 torch.compile（默认模式）比较，并记下第一次调用花在编译上的时间。
    用 torch.profiler 数一次前向在 GPU 上执行了多少个核函数（不计复制与清零），与算例 7.8.1 的估计对照。
（2）推理：批大小 1、长 16 个词元的一次前向（不记录梯度）——核函数都很小，启动开销占主导（6.2 节）；
    急切执行、torch.compile 默认模式、mode="reduce-overhead"（再用 CUDA 图提交，形状固定）三者比较。
torch.compile 要用 Triton 与 Python.h；编译失败时整个程序报错退出，不写半套结果。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import re
import time

import torch
from torch.profiler import ProfilerActivity, profile

import model
import prep

prep.python_headers()                                       # Triton 编译它的启动代码要 Python.h

torch.manual_seed(0)
dev = "cuda"
m = model.Tiny().to(dev)
ids = torch.randint(0, model.V, (32, model.T), device=dev)
small = torch.randint(0, model.V, (1, 16), device=dev)


def timeit(fn, reps=20):
    for _ in range(3):
        fn()
    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    ts = []
    for _ in range(reps):
        e0.record()
        fn()
        e1.record()
        e1.synchronize()
        ts.append(e0.elapsed_time(e1))
    ts.sort()
    return ts[len(ts) // 2]


def train(f):
    def go():
        loss = model.loss_fn(f(ids), ids)
        loss.backward()
    return go


def kernels(fn):
    fn()
    torch.cuda.synchronize()
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
        fn()
        torch.cuda.synchronize()
    return sum(1 for e in prof.events() if e.device_type == torch.autograd.DeviceType.CUDA and not re.match(r"(Memcpy|Memset)", e.name))


out = {"torch": torch.__version__}
out["eager_train_ms"] = timeit(train(m))
with torch.no_grad():
    out["eager_fwd_kernels"] = kernels(lambda: m(ids))
    out["eager_small_ms"] = timeit(lambda: m(small), reps=50)

cm = torch.compile(m)
t0 = time.time()
train(cm)()
torch.cuda.synchronize()
out["compile_s"] = time.time() - t0
out["compiled_train_ms"] = timeit(train(cm))
with torch.no_grad():
    cm(ids)                                                  # 不记录梯度时是另一张图，先编译好
    out["compiled_fwd_kernels"] = kernels(lambda: cm(ids))
    cm(small)
    out["compiled_small_ms"] = timeit(lambda: cm(small), reps=50)
    torch._dynamo.reset()                                   # 清掉默认模式的编译缓存，确保下面真的按 reduce-overhead 重新编译
    ro = torch.compile(m, mode="reduce-overhead", dynamic=False)
    for _ in range(3):
        ro(small)
    out["graph_small_ms"] = timeit(lambda: ro(small), reps=50)
out["train_speedup"] = out["eager_train_ms"] / out["compiled_train_ms"]
out["small_speedup"] = out["eager_small_ms"] / out["graph_small_ms"]
json.dump(out, open("out.json", "w"))
print(out)
