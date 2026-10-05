"""GPU 实验 7.6：给 Nsight Systems 记录用的一次训练迭代。前向、反向、更新各用 NVTX 标出一段，时间线上一眼就能找到。
用法：nsys profile -o step --trace=cuda,nvtx python3 step.py"""
import torch

import model

dev = "cuda"
torch.manual_seed(0)
m = model.Tiny().to(dev)
opt = torch.optim.AdamW(m.parameters(), lr=1e-4)
ids = torch.randint(0, model.V, (32, model.T), device=dev)
for it in range(4):                                       # 前 3 次是预热，第 4 次是要看的那一次
    rng = torch.cuda.nvtx.range
    with rng(f"迭代 {it}"):
        with rng("前向"):
            loss = model.loss_fn(m(ids), ids)
        with rng("反向"):
            loss.backward()
        with rng("更新"):
            opt.step()
            opt.zero_grad(set_to_none=True)
torch.cuda.synchronize()
print("loss", loss.item())
