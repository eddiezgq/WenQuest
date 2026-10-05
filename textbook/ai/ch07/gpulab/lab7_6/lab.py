# GPU 实验 7.6 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 7.6　一次训练迭代调用了哪些核函数
# %%
import sys; sys.path.insert(0, "..")
import re
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
# %% [markdown]
# ## 1. 用 torch.profiler 记录一次训练迭代
# `model.py` 是第 2 章的小型 Transformer（批 32 × 256 个词元，单精度）。先预热三次，再记录一次完整的迭代：前向、反向、更新。
# %%
import model
from torch.profiler import ProfilerActivity, profile

torch.manual_seed(0)
m = model.Tiny().cuda()
opt = torch.optim.AdamW(m.parameters(), lr=1e-4)
ids = torch.randint(0, model.V, (32, model.T), device="cuda")


def step():
    loss = model.loss_fn(m(ids), ids)
    loss.backward()
    opt.step()
    opt.zero_grad(set_to_none=True)


for _ in range(3):
    step()
torch.cuda.synchronize()
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True) as prof:
    step()
    torch.cuda.synchronize()
prof.export_chrome_trace("trace.json")          # 可以下载后在 https://ui.perfetto.dev 打开
try:
    print(prof.key_averages().table(sort_by="device_time_total", row_limit=15))
except Exception:
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=15))
# %% [markdown]
# ## 2. 数一数核函数，矩阵乘法占了多少时间（任务 1）
# 只看 GPU 上的事件（不计复制与清零）。名字里有 gemm、cutlass、xmma 的是 cuBLAS 的矩阵乘法核函数。
# %%
kern = [e for e in prof.events() if e.device_type == torch.autograd.DeviceType.CUDA and not re.match(r"(Memcpy|Memset)", e.name)]
gemm = [e for e in kern if re.search(r"gemm|cutlass|xmma", e.name, re.I)]
us = lambda e: e.time_range.elapsed_us()
tot = sum(us(e) for e in kern)
gemm_pct = 100 * sum(us(e) for e in gemm) / tot
print(f"核函数 {len(kern)} 个，其中矩阵乘法 {len(gemm)} 个；GPU 上共 {tot / 1e3:.1f} ms，矩阵乘法占 {gemm_pct:.0f}%")
names = {}
for e in kern:
    names[e.name] = names.get(e.name, 0) + us(e)
for n, t in sorted(names.items(), key=lambda kv: -kv[1])[:10]:
    print(f"{t / 1e3:7.2f} ms  {n[:110]}")
# %% [markdown]
# ## 3. 一次迭代的耗时；允许 TF32 以后（任务 2）
# PyTorch 默认不让单精度矩阵乘法用 TF32 张量核心。打开它，看矩阵乘法核函数的名字与耗时怎样变。
# %%
def step_ms():
    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    ts = []
    for _ in range(10):
        e0.record(); step(); e1.record(); e1.synchronize()
        ts.append(e0.elapsed_time(e1))
    return sorted(ts)[5]


t_fp32 = step_ms()
torch.backends.cuda.matmul.allow_tf32 = True
t_tf32 = step_ms()
torch.backends.cuda.matmul.allow_tf32 = False
print(f"一次迭代：单精度 {t_fp32:.1f} ms，允许 TF32 {t_tf32:.1f} ms")
# %% [markdown]
# ## 4. 用 Nsight Systems 看时间线（任务 3）
# `step.py` 做同样的迭代，用 NVTX 标出“前向”“反向”“更新”三段。时间线文件 `step.nsys-rep` 下载后用 Nsight Systems 图形界面打开。
# %%
if "nsys" in env:
    try:
        wqgpu.sh("nsys profile -o step --force-overwrite true --trace=cuda,nvtx python3 step.py > /dev/null")
        print(wqgpu.sh("nsys stats --report nvtx_sum --format csv step.nsys-rep | head -20"))
    except RuntimeError as e:
        print("这台机器上 Nsight Systems 运行失败：", e)
else:
    print("这台机器上没有 nsys")
# %% [markdown]
# ## 5. 回传结果
# %%
wqgpu.submit(kernels=len(kern), gemm_kernels=len(gemm), gemm_pct=gemm_pct, gpu_ms=tot / 1e3, step_ms=t_fp32, tf32_step_ms=t_tf32)
