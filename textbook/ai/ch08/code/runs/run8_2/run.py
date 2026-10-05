"""程序 8.2.2：混合精度训练的速度与显存（8.2 节）。小型 Transformer，B = 32，T = 256，AdamW，A10。
数据取自 8.5 节的合成语言（lang.py），8 批轮流使用。四种做法各训练 200 步：单精度；单精度但矩阵乘法允许 TF32；
自动混合精度 FP16（torch.autocast + GradScaler 损失缩放）；自动混合精度 BF16（不需要损失缩放）。
记录一步的耗时（中位数）、显存峰值，以及 200 步后的损失（四者应相近）。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json

import torch

import lang
import model

dev = "cuda"
B = 32
S = lang.Sampler(dev)                                       # 与程序 8.5.2 相同的合成语言（lang.py）


def run(mode, steps=200):
    torch.manual_seed(0)
    torch.backends.cuda.matmul.allow_tf32 = mode == "tf32"
    torch.backends.cudnn.allow_tf32 = mode == "tf32"
    m = model.Tiny().to(dev)
    opt = torch.optim.AdamW(m.parameters(), lr=3e-4)
    scaler = (torch.amp.GradScaler("cuda", enabled=mode == "fp16") if hasattr(torch.amp, "GradScaler")
              else torch.cuda.amp.GradScaler(enabled=mode == "fp16"))       # 较老的 PyTorch
    dtype = {"fp16": torch.float16, "bf16": torch.bfloat16}.get(mode)
    g = torch.Generator(device=dev).manual_seed(1)
    batches = [S.batch(B, model.T, g) for _ in range(8)]   # 8 批合成语言的数据轮流使用（数据生成不计入耗时）
    e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    ts = []
    torch.cuda.reset_peak_memory_stats()
    for it in range(steps):
        e0.record()
        ids = batches[it % len(batches)]
        with torch.autocast("cuda", dtype=dtype, enabled=dtype is not None):
            loss = model.loss_fn(m(ids), ids)
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        opt.zero_grad(set_to_none=True)
        e1.record()
        e1.synchronize()
        if it >= 10:
            ts.append(e0.elapsed_time(e1))
    ts.sort()
    r = {f"{mode}_ms": ts[len(ts) // 2], f"{mode}_peak_MB": torch.cuda.max_memory_allocated() / 1e6, f"{mode}_loss": loss.item()}
    if mode == "fp16":
        r["fp16_scale_log2"] = float(torch.log2(torch.tensor(scaler.get_scale())))
    del m, opt
    torch.cuda.empty_cache()
    return r


out = {"torch": torch.__version__, "bf16_supported": torch.cuda.is_bf16_supported()}
for mode in ("fp32", "tf32", "fp16", "bf16"):
    out.update(run(mode))
out["speed_tf32"] = out["fp32_ms"] / out["tf32_ms"]
out["speed_fp16"] = out["fp32_ms"] / out["fp16_ms"]
out["speed_bf16"] = out["fp32_ms"] / out["bf16_ms"]
json.dump(out, open("out.json", "w"))                       # 先写结果；损失是否相近只提醒，不中断
if not all(abs(out[f"{k}_loss"] / out["fp32_loss"] - 1) < 0.2 for k in ("tf32", "fp16", "bf16")):
    print("提醒：四种做法 200 步后的损失相差超过 20%", out)
print(out)
