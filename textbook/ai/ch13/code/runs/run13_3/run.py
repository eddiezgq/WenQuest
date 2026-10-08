"""实测：从零训练四档字符级语言模型，看损失随规模怎样下降，并把幂律拟出来（13.3、13.4 节）。

做法：同一份语料、同一套超参数，只改模型宽度与层数，训练同样多的词元（算力随参数线性涨）。
每一档记下验证损失、参数量、训练用掉的算力（按 6ND）与实际用时；最后在对数坐标上拟合
L = (N_c/N)^α，并用最小两档外推到最大一档，看外推误差有多大——这正是算例 13.4.2 在合成数据上做的事。

注意：四档模型都很小（0.1—8 百万参数），拟出的指数不该与 Kaplan 在大模型上的 0.076 相比，
它只说明“同一套设置下，损失随规模是一条直线”这件事在自己的机器上也成立。
"""
import json
import math
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from data import load

torch.manual_seed(13)
dev = "cuda"
TEXT, SRC, SHA = load()
chars = sorted(set(TEXT))
stoi = {c: i for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in TEXT], dtype=torch.long)
n_split = int(0.9 * len(data))
train, val = data[:n_split], data[n_split:]
V, T, B = len(chars), 128, 64
TOKENS = 6_000_000                                           # 每一档都训练同样多的词元
STEPS = TOKENS // (B * T)


class Block(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.att = nn.MultiheadAttention(d, h, batch_first=True)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))

    def forward(self, x, mask):
        y = self.ln1(x)
        a, _ = self.att(y, y, y, attn_mask=mask, need_weights=False)
        x = x + a
        return x + self.mlp(self.ln2(x))


class LM(nn.Module):
    def __init__(self, d, layers, heads):
        super().__init__()
        self.emb = nn.Embedding(V, d)
        self.pos = nn.Embedding(T, d)
        self.blocks = nn.ModuleList([Block(d, heads) for _ in range(layers)])
        self.ln = nn.LayerNorm(d)
        self.head = nn.Linear(d, V, bias=False)

    def forward(self, x):
        mask = torch.triu(torch.ones(x.size(1), x.size(1), device=x.device, dtype=torch.bool), 1)
        h = self.emb(x) + self.pos(torch.arange(x.size(1), device=x.device))
        for b in self.blocks:
            h = b(h, mask)
        return self.head(self.ln(h))


def batch(split, bs=B):
    src = train if split == "train" else val
    i = torch.randint(len(src) - T - 1, (bs,))
    x = torch.stack([src[j:j + T] for j in i]).to(dev)
    y = torch.stack([src[j + 1:j + T + 1] for j in i]).to(dev)
    return x, y


@torch.no_grad()
def evaluate(model, iters=40):
    model.eval()
    tot = 0.0
    for _ in range(iters):
        x, y = batch("val")
        with torch.autocast("cuda", dtype=torch.bfloat16):
            loss = F.cross_entropy(model(x).view(-1, V), y.view(-1))
        tot += loss.item()
    model.train()
    return tot / iters


out = {"_gpu": torch.cuda.get_device_name(0), "torch": torch.__version__, "corpus": SRC,
       "corpus_sha8": SHA, "vocab": V, "ctx": T, "tokens_each": TOKENS, "steps": STEPS,
       "chars_M": len(TEXT) / 1e6}
SIZES = [("xs", 64, 2, 2), ("s", 128, 4, 4), ("m", 192, 6, 6), ("l", 256, 8, 8)]
rows = []
for name, d, layers, heads in SIZES:
    model = LM(d, layers, heads).to(dev)
    n_emb = model.emb.weight.numel() + model.pos.weight.numel()
    n_all = sum(p.numel() for p in model.parameters())
    n_body = n_all - n_emb                                   # 规模定律里数的是非嵌入参数
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 1e-3, total_steps=STEPS, pct_start=0.1)
    torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(STEPS):
        x, y = batch("train")
        with torch.autocast("cuda", dtype=torch.bfloat16):
            loss = F.cross_entropy(model(x).view(-1, V), y.view(-1))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
    torch.cuda.synchronize()
    secs = time.time() - t0
    vl = evaluate(model)
    flops = 6 * n_body * TOKENS
    rows.append((n_body, vl))
    out[f"{name}_params_M"] = n_all / 1e6
    out[f"{name}_body_M"] = n_body / 1e6
    out[f"{name}_loss"] = vl
    out[f"{name}_ppl"] = math.exp(vl)
    out[f"{name}_secs"] = secs
    out[f"{name}_flops"] = flops
    out[f"{name}_tflops"] = flops / secs / 1e12               # 实际跑出来的算力
    out[f"{name}_tok_per_s"] = TOKENS / secs
    del model, opt
    torch.cuda.empty_cache()

# 幂律拟合：log L = -α log N + b
ns = np.array([r[0] for r in rows], dtype=float)
ls = np.array([r[1] for r in rows], dtype=float)
a, b = np.polyfit(np.log(ns), np.log(ls), 1)
out["alpha"] = float(-a)
out["fit_rms_pct"] = float(np.sqrt(((np.log(ls) - (a * np.log(ns) + b)) ** 2).mean())) * 100
# 用最小两档外推到最大一档
a2, b2 = np.polyfit(np.log(ns[:2]), np.log(ls[:2]), 1)
pred = float(np.exp(a2 * np.log(ns[-1]) + b2))
out["extrap_pred"] = pred
out["extrap_true"] = float(ls[-1])
out["extrap_err_pct"] = abs(pred - ls[-1]) / ls[-1] * 100
out["loss_drop"] = float(ls[0] - ls[-1])
out["params_ratio"] = float(ns[-1] / ns[0])
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
