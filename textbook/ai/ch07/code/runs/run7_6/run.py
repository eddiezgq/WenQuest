"""程序 7.6.2：小型 Transformer 一个训练步的显存与时间（7.6 节）。B = 32，T = 256，单精度，AdamW。
（1）用 torch.autograd.graph.saved_tensors_hooks 截住前向时为反向保存的每一个张量，按存储去重相加（不计参数本身），
    与算例 7.6.1 的逐项估算对照；同时记下前向结束时显存比开始时多了多少（torch.cuda.memory_allocated）。
（2）一个完整训练步（前向、反向、更新）的显存峰值与耗时，不重计算与重计算（每层用 torch.utils.checkpoint）各一次。
（3）用 torch.profiler 数一个训练步在 GPU 上执行了多少个核函数，矩阵乘法类的核函数（名字里有 gemm、cutlass、xmma 的）占 GPU 时间的多少。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import gc
import json
import re

import torch

import model

torch.manual_seed(0)
dev = "cuda"
B = 32
MB = 1e6


def make(ckpt):
    m = model.Tiny(checkpoint=ckpt).to(dev)
    opt = torch.optim.AdamW(m.parameters(), lr=1e-4)
    return m, opt


ids = torch.randint(0, model.V, (B, model.T), device=dev)


def step(m, opt):
    loss = model.loss_fn(m(ids), ids)
    loss.backward()
    opt.step()
    opt.zero_grad(set_to_none=True)
    return loss


def measure(ckpt):
    m, opt = make(ckpt)
    for _ in range(3):                                      # 预热：AdamW 的状态在第一步时创建
        step(m, opt)
    torch.cuda.synchronize()
    base = torch.cuda.memory_allocated()                    # 参数 + AdamW 状态（梯度已清成 None）
    params = {p.untyped_storage().data_ptr() for p in m.parameters()}
    saved = {}

    def pack(t):
        s = t.untyped_storage()
        if s.device.type == "cuda" and s.data_ptr() not in params:
            saved[s.data_ptr()] = s.nbytes()
        return t

    torch.cuda.reset_peak_memory_stats()
    with torch.autograd.graph.saved_tensors_hooks(pack, lambda t: t):
        loss = model.loss_fn(m(ids), ids)
    torch.cuda.synchronize()
    after_fwd = torch.cuda.memory_allocated()
    loss.backward()
    opt.step()
    opt.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    peak = torch.cuda.max_memory_allocated()
    t0, t1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    ms = []
    for _ in range(10):
        t0.record()
        step(m, opt)
        t1.record()
        t1.synchronize()
        ms.append(t0.elapsed_time(t1))
    ms.sort()
    r = dict(base_MB=base / MB, saved_MB=sum(saved.values()) / MB, n_saved=len(saved), fwd_MB=(after_fwd - base) / MB,
             peak_MB=peak / MB, step_ms=ms[len(ms) // 2], reserved_MB=torch.cuda.memory_reserved() / MB)
    return r, m, opt


from torch.profiler import ProfilerActivity, profile   # noqa: E402

plain, m, opt = measure(False)
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    step(m, opt)
    torch.cuda.synchronize()
del m, opt                                                  # 先释放这一套参数与 AdamW 状态，再测重计算，峰值才可比
gc.collect()
torch.cuda.empty_cache()
ckpt, _, _ = measure(True)
out = {k: v for k, v in plain.items()}
out.update({"ckpt_" + k: v for k, v in ckpt.items()})
out["extra_pct"] = 100 * (ckpt["step_ms"] / plain["step_ms"] - 1)
kern = [e for e in prof.events() if e.device_type == torch.autograd.DeviceType.CUDA and not re.match(r"(Memcpy|Memset)", e.name)]
gemm = [e for e in kern if re.search(r"gemm|cutlass|xmma", e.name, re.I)]
us = lambda e: e.time_range.elapsed_us()                # 核函数在 GPU 上执行的时间
tot = sum(us(e) for e in kern)
out.update(kernels=len(kern), gemm_kernels=len(gemm), gemm_pct=100 * sum(us(e) for e in gemm) / tot, gpu_ms=tot / 1e3,
           torch=torch.__version__)
json.dump(out, open("out.json", "w"))
print(out)
