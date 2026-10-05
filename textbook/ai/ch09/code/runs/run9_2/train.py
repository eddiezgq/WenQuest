"""程序 9.2.2：用 DDP 与 FSDP 训练同一个模型（9.2 节）。由 run.py 用 torch.distributed.run（即 torchrun）启动，每块 GPU 一个进程。
用法：torchrun --nproc_per_node=P train.py {ddp|fsdp|single} {small|mid}
- small：第 2 章的小型 Transformer；mid：同样的结构放大到 d = 2048、16 层、16 个头、d_ff = 8192（约 8 亿个参数）。
- 单精度参数与 AdamW，前向与反向用 BF16 自动混合精度；每块 GPU 每步 8 条长 256 的随机序列。
- FSDP 按块（每个 Block 一个单元）包装，相当于 ZeRO-3：参数、梯度、优化器状态都切成 P 份。
进程 0 把每步耗时（中位数）、每块 GPU 的显存峰值与每秒处理的词元数写到 result_<模式>_<模型>_<P>.json。"""
import json
import os
import sys

import torch
import torch.distributed as dist

import model

mode, size = sys.argv[1], sys.argv[2]
if size == "mid":
    model.D, model.L, model.H, model.FF = 2048, 16, 16, 8192
torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))       # 先选定 GPU，再建进程组
dist.init_process_group("nccl")
rank, world = dist.get_rank(), dist.get_world_size()
torch.manual_seed(0)
m = model.Tiny().cuda()
n_params = sum(p.numel() for p in m.parameters())
if mode == "ddp":
    m = torch.nn.parallel.DistributedDataParallel(m, gradient_as_bucket_view=True)   # 梯度直接放在通信桶里，省一份显存
elif mode == "fsdp":
    from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
    try:
        from torch.distributed.fsdp.wrap import ModuleWrapPolicy
        policy = ModuleWrapPolicy({model.Block})
    except ImportError:                                     # 较老的 PyTorch
        import functools
        from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
        policy = functools.partial(transformer_auto_wrap_policy, transformer_layer_cls={model.Block})
    m = FSDP(m, auto_wrap_policy=policy, device_id=torch.cuda.current_device())
opt = torch.optim.AdamW(m.parameters(), lr=1e-4)
g = torch.Generator(device="cuda").manual_seed(rank)
ids = torch.randint(0, model.V, (8, model.T), device="cuda", generator=g)
e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
ts = []
torch.cuda.reset_peak_memory_stats()
for it in range(25):
    e0.record()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss = model.loss_fn(m(ids), ids)
    loss.backward()
    opt.step()
    opt.zero_grad(set_to_none=True)
    e1.record()
    e1.synchronize()
    if it >= 5:
        ts.append(e0.elapsed_time(e1))
peak = torch.tensor([torch.cuda.max_memory_allocated() / 1e6], device="cuda")
dist.all_reduce(peak, op=dist.ReduceOp.MAX)
if rank == 0:
    ms = sorted(ts)[len(ts) // 2]
    json.dump({"params": n_params, "ms": ms, "peak_MB": peak.item(), "tok_s": world * 8 * model.T / ms * 1e3},
              open(f"result_{mode}_{size}_{world}.json", "w"))
dist.destroy_process_group()
