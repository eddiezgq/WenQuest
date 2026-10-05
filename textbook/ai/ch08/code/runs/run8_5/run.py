"""程序 8.5.2：把小型 Transformer 量化到 INT8 与 INT4（8.5 节、GPU 实验 8.5 的参考结果）。A10。
（1）在熵已知的合成语言（lang.py）上训练小型 Transformer（BF16 自动混合精度，AdamW，每步一批新数据），
    记下训练后（单精度评估）的损失与熵下限 H 之差。
（2）仅权重量化：各线性层与词元嵌入（输出层与它共享）的权重分别按 INT8 逐通道、INT4 逐通道、INT4 每 128 个输入一组
    做对称量化（这里用“量化再反量化”的权重计算，结果与真正用整数存储、计算时再反量化相同），评估损失；
    同时算出各种做法下权重的字节数（INT4 分组时每组另存一个 FP16 比例）。
（3）INT8 张量核心：8192×384 乘 384×1536 的矩阵乘法，FP16（单精度累加）与 INT8（torch._int_mm，INT32 累加）的耗时。
结果写进 out.json（第 14 轮附 4.4 节）。本地试运行：WQ_DEV=cpu WQ_STEPS=30 python3 run.py。"""
import json
import os

import torch

import lang
import model

dev = os.environ.get("WQ_DEV", "cuda")
STEPS = int(os.environ.get("WQ_STEPS", "1500"))
B = 32
torch.manual_seed(0)
S = lang.Sampler(dev)
gen = torch.Generator(device=dev).manual_seed(1)
m = model.Tiny().to(dev)
opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=0.0)
sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 100) * max(0.1, 1 - s / STEPS))
amp = dict(device_type=dev, dtype=torch.bfloat16, enabled=dev == "cuda")
for step in range(STEPS):
    ids = S.batch(B, model.T, gen)
    with torch.autocast(**amp):
        loss = model.loss_fn(m(ids), ids)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0)
    opt.step()
    sched.step()
    opt.zero_grad(set_to_none=True)
    if step % 250 == 0:
        print(step, round(loss.item(), 4), flush=True)

egen = torch.Generator(device=dev).manual_seed(99)
evals = [S.batch(B, model.T, egen) for _ in range(10)]


@torch.no_grad()
def evaluate():
    return sum(model.loss_fn(m(x), x).item() for x in evals) / len(evals)


targets = [mod.weight for mod in m.modules() if isinstance(mod, torch.nn.Linear)] + [m.tok.weight]
orig = [w.detach().clone() for w in targets]


def quantize(bits, group=None):
    """对称量化再反量化。线性层的权重形状为 (输出, 输入)：逐通道 = 每一行一个比例；分组 = 每行每 group 个输入一个比例。"""
    qmax = 2 ** (bits - 1) - 1
    nbytes = 0
    for w, w0 in zip(targets, orig):
        x = w0.float()
        g = x.reshape(x.shape[0], -1, group) if group else x.reshape(x.shape[0], 1, -1)
        s = g.abs().amax(dim=-1, keepdim=True).clamp_min(1e-12) / qmax
        w.data.copy_((torch.clamp(torch.round(g / s), -qmax, qmax) * s).reshape(x.shape))
        nbytes += x.numel() * bits / 8 + s.numel() * 2
    return nbytes


def restore():
    for w, w0 in zip(targets, orig):
        w.data.copy_(w0)


out = {"H": S.H, "steps": STEPS, "torch": torch.__version__}
out["fp32_loss"] = evaluate()
out["fp32_MB"] = sum(w.numel() for w in orig) * 4 / 1e6
out["fp16_MB"] = out["fp32_MB"] / 2
for tag, bits, group in (("int8", 8, None), ("int4c", 4, None), ("int4g", 4, 128)):
    out[f"{tag}_MB"] = quantize(bits, group) / 1e6
    out[f"{tag}_loss"] = evaluate()
    out[f"{tag}_gap"] = out[f"{tag}_loss"] - out["fp32_loss"]
    restore()
out["fp32_gap_H"] = out["fp32_loss"] - S.H

if dev == "cuda":
    a16 = torch.randn(8192, 384, device=dev, dtype=torch.float16)
    b16 = torch.randn(384, 1536, device=dev, dtype=torch.float16)
    a8 = torch.randint(-127, 128, (8192, 384), device=dev, dtype=torch.int8)
    b8 = torch.randint(-127, 128, (384, 1536), device=dev, dtype=torch.int8).t().contiguous().t()   # _int_mm 要求第二个矩阵按列存放

    def timeit(fn, reps=50):
        for _ in range(5):
            fn()
        e0, e1 = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        ts = []
        for _ in range(reps):
            e0.record()
            fn()
            e1.record()
            e1.synchronize()
            ts.append(e0.elapsed_time(e1) * 1e3)
        return sorted(ts)[reps // 2]

    flop = 2 * 8192 * 384 * 1536
    out["mm16_us"] = timeit(lambda: a16 @ b16)
    out["mm16_TFs"] = flop / out["mm16_us"] / 1e6
    try:
        c8 = torch._int_mm(a8, b8)
        out["mm8_us"] = timeit(lambda: torch._int_mm(a8, b8))
        out["mm8_TFs"] = flop / out["mm8_us"] / 1e6
    except Exception as e:                                  # 没有 _int_mm 的版本：表中显示“—”
        print("torch._int_mm 不可用：", e)
        c8 = None
        out["mm8_us"] = out["mm8_TFs"] = "—"
    # 整数运算是精确的：与双精度算出的同一乘积（和远小于 2⁵³，也是精确的）逐位相同
    out["mm8_exact"] = "是" if c8 is not None and torch.equal(c8.double(), a8.double() @ b8.double()) else "否"
json.dump(out, open("out.json", "w"))
print(out)
