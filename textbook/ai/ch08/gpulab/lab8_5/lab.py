# GPU 实验 8.5 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 8.5　把小型 Transformer 量化到 INT8 和 INT4
# %%
import sys; sys.path.insert(0, "..")
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
# %% [markdown]
# ## 1. 在熵已知的合成语言上训练（约 2 分钟）
# `lang.py` 生成一种一阶马尔可夫链的“语言”：每个词元只可能接 8 个固定的后继。任何模型预测下一个词元的交叉熵都不低于它的熵 H。
# %%
import lang
import model

torch.manual_seed(0)
S = lang.Sampler("cuda")
gen = torch.Generator(device="cuda").manual_seed(1)
m = model.Tiny().cuda()
STEPS = 1000
opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=0.0)
sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 100) * max(0.1, 1 - s / STEPS))
for step in range(STEPS):
    ids = S.batch(32, model.T, gen)
    with torch.autocast("cuda", dtype=torch.bfloat16):
        loss = model.loss_fn(m(ids), ids)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0)
    opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
    if step % 200 == 0:
        print(step, round(loss.item(), 3))
egen = torch.Generator(device="cuda").manual_seed(99)
evals = [S.batch(32, model.T, egen) for _ in range(10)]


@torch.no_grad()
def evaluate():
    return sum(model.loss_fn(m(x), x).item() for x in evals) / len(evals)


fp32_loss = evaluate()
print(f"熵下限 H = {S.H:.4f}，训练后的损失 {fp32_loss:.4f}")
# %% [markdown]
# ## 2. 仅权重量化（任务 1）
# 线性层与词元嵌入的权重按对称量化再反量化。`group=None` 是逐通道（每个输出一个比例），`group=128` 是每 128 个输入一组。
# %%
targets = [mod.weight for mod in m.modules() if isinstance(mod, torch.nn.Linear)] + [m.tok.weight]
orig = [w.detach().clone() for w in targets]


def quantize(bits, group=None, per_tensor=False):
    qmax = 2 ** (bits - 1) - 1
    nbytes = 0
    for w, w0 in zip(targets, orig):
        x = w0.float()
        g = x.reshape(1, 1, -1) if per_tensor else x.reshape(x.shape[0], -1, group) if group else x.reshape(x.shape[0], 1, -1)
        s = g.abs().amax(dim=-1, keepdim=True).clamp_min(1e-12) / qmax
        w.data.copy_((torch.clamp(torch.round(g / s), -qmax, qmax) * s).reshape(x.shape))
        nbytes += x.numel() * bits / 8 + s.numel() * 2
    return nbytes / 1e6


def restore():
    for w, w0 in zip(targets, orig):
        w.data.copy_(w0)


res = {}
for tag, kw in (("int8", dict(bits=8)), ("int4c", dict(bits=4)), ("int4g", dict(bits=4, group=128)), ("int4t", dict(bits=4, per_tensor=True))):
    mb = quantize(**kw)
    res[tag] = (evaluate(), mb)
    restore()
    print(f"{tag:6s} 损失 {res[tag][0]:.4f}（比量化前高 {res[tag][0] - fp32_loss:+.4f}），权重 {mb:.1f} MB")
# %% [markdown]
# ## 3. 分组大小（任务 2）
# 把 INT4 的分组改成 32、64、256，损失与权重大小怎样变化？
# %%
for g in (32, 64, 256):
    mb = quantize(4, group=g)
    print(f"INT4，每 {g} 个一组：损失 {evaluate():.4f}，权重 {mb:.2f} MB")
    restore()
# %% [markdown]
# ## 4. INT8 张量核心（任务 3）
# 同样形状的矩阵乘法，FP16 与 INT8（`torch._int_mm`，INT32 累加）各要多久。
# %%
a16, b16 = torch.randn(8192, 384, device="cuda", dtype=torch.half), torch.randn(384, 1536, device="cuda", dtype=torch.half)
a8 = torch.randint(-127, 128, (8192, 384), device="cuda", dtype=torch.int8)
b8 = torch.randint(-127, 128, (384, 1536), device="cuda", dtype=torch.int8).t().contiguous().t()
t16 = wqgpu.bench(lambda: a16 @ b16, sync=torch.cuda.synchronize) * 1e6
try:
    t8 = wqgpu.bench(lambda: torch._int_mm(a8, b8), sync=torch.cuda.synchronize) * 1e6
except Exception as e:
    print("这个版本的 PyTorch 没有 torch._int_mm：", e)
    t8 = None                                   # 不回传这一项
print(f"FP16 {t16:.0f} μs，INT8 " + (f"{t8:.0f} μs" if t8 else "—"))
# %% [markdown]
# ## 5. 回传结果
# %%
wqgpu.submit(H=S.H, fp32_loss=fp32_loss, int8_loss=res["int8"][0], int4c_loss=res["int4c"][0], int4g_loss=res["int4g"][0],
             int4t_loss=res["int4t"][0], int4g_MB=res["int4g"][1], mm16_us=t16, mm8_us=t8)
