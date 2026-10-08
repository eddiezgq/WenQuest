# GPU 实验 13.3 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 13.3　从零训练一个字符级小语言模型
# 四档大小、同一份语料、同样多的训练词元。要看的不是“模型多好”，而是**损失随规模下降得有多规律**，
# 以及用小模型外推大模型准不准——13.4 节的规模定律，在自己的机器上做一遍。
# %%
import sys; sys.path.insert(0, "..")
import json, math, time
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
import wqgpu
env = wqgpu.check(("gpu", "torch"))
dev = "cuda"
print(torch.cuda.get_device_name(0), torch.__version__)
# %% [markdown]
# ## 1. 语料与划分（任务 1）
# 用公开的 Tiny Shakespeare（约 110 万字符）；机器连不上网时退回程序生成的小语言。
# 字符级的词表只有几十个符号，所以嵌入层很小，“非嵌入参数”与总参数几乎一样——这正好省去一个麻烦。
# %%
import urllib.request, hashlib, random
URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
try:
    TEXT = urllib.request.urlopen(URL, timeout=60).read().decode("utf-8"); SRC = "tinyshakespeare"
except Exception as e:
    r = random.Random(13); S = ["轴","齿轮","箱体","检验员","机床"]; V_ = ["加工","检验","装配","送检","返工"]
    O = ["到工位","按图样","按手册","两遍","合格"]; parts = []
    while sum(len(x) for x in parts) < 1_100_000:
        parts.append(f"{r.choice(S)}{r.choice(V_)}{r.choice(O)}。")
    TEXT = "".join(parts)[:1_100_000]; SRC = f"synthetic ({type(e).__name__})"
chars = sorted(set(TEXT)); stoi = {c: i for i, c in enumerate(chars)}
data = torch.tensor([stoi[c] for c in TEXT], dtype=torch.long)
n = int(0.9 * len(data)); train, val = data[:n], data[n:]
V, T, B = len(chars), 128, 64
print(f"{SRC}：{len(TEXT)/1e6:.2f} 百万字符，词表 {V}，上下文 {T}，批量 {B}")
print("校验和", hashlib.sha256(TEXT.encode()).hexdigest()[:8])
# %% [markdown]
# ## 2. 四档模型（任务 2）
# 只改宽度与层数，其他一律不动。**每一档训练同样多的词元**，所以算力随参数线性增长。
# %%
class Block(nn.Module):
    def __init__(s, d, h):
        super().__init__(); s.ln1, s.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        s.att = nn.MultiheadAttention(d, h, batch_first=True)
        s.mlp = nn.Sequential(nn.Linear(d, 4*d), nn.GELU(), nn.Linear(4*d, d))
    def forward(s, x, m):
        y = s.ln1(x); a, _ = s.att(y, y, y, attn_mask=m, need_weights=False)
        x = x + a; return x + s.mlp(s.ln2(x))

class LM(nn.Module):
    def __init__(s, d, layers, heads):
        super().__init__(); s.emb = nn.Embedding(V, d); s.pos = nn.Embedding(T, d)
        s.blocks = nn.ModuleList([Block(d, heads) for _ in range(layers)])
        s.ln = nn.LayerNorm(d); s.head = nn.Linear(d, V, bias=False)
    def forward(s, x):
        m = torch.triu(torch.ones(x.size(1), x.size(1), device=x.device, dtype=torch.bool), 1)
        h = s.emb(x) + s.pos(torch.arange(x.size(1), device=x.device))
        for b in s.blocks: h = b(h, m)
        return s.head(s.ln(h))

def batch(split, bs=B, ctx=T):
    src = train if split == "train" else val
    i = torch.randint(len(src) - ctx - 1, (bs,))
    x = torch.stack([src[j:j+ctx] for j in i]).to(dev)
    y = torch.stack([src[j+1:j+ctx+1] for j in i]).to(dev)
    return x, y

@torch.no_grad()
def evaluate(model, iters=40, ctx=T):
    model.eval(); tot = 0.0
    for _ in range(iters):
        x, y = batch("val", ctx=ctx)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            tot += F.cross_entropy(model(x).view(-1, V), y.view(-1)).item()
    model.train(); return tot / iters

def run(d, layers, heads, tokens=6_000_000, ctx=T, bs=B):
    torch.manual_seed(13)
    model = LM(d, layers, heads).to(dev)
    n_emb = model.emb.weight.numel() + model.pos.weight.numel()
    n_all = sum(p.numel() for p in model.parameters()); n_body = n_all - n_emb
    steps = tokens // (bs * ctx)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.1)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, 1e-3, total_steps=steps, pct_start=0.1)
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(steps):
        x, y = batch("train", bs=bs, ctx=ctx)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            loss = F.cross_entropy(model(x).view(-1, V), y.view(-1))
        opt.zero_grad(set_to_none=True); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sch.step()
    torch.cuda.synchronize(); secs = time.time() - t0
    vl = evaluate(model, ctx=ctx); flops = 6 * n_body * tokens
    del model, opt; torch.cuda.empty_cache()
    return {"body": n_body, "all": n_all, "loss": vl, "ppl": math.exp(vl), "secs": secs,
            "flops": flops, "tflops": flops / secs / 1e12, "steps": steps}

SIZES = [("xs", 64, 2, 2), ("s", 128, 4, 4), ("m", 192, 6, 6), ("l", 256, 8, 8)]
R = {}
for name, d, L_, h in SIZES:
    R[name] = run(d, L_, h)
    r = R[name]
    print(f"{name}: 非嵌入 {r['body']/1e6:.2f}M　损失 {r['loss']:.3f}　困惑度 {r['ppl']:.1f}　"
          f"{r['secs']:.0f}s　{r['tflops']:.1f} TFLOP/s")
# %% [markdown]
# ## 3. 拟合与外推（任务 3）
# 在对数坐标上拟一条直线：斜率的相反数就是指数 α。再只用最小两档拟一条，外推到最大一档，看误差。
# %%
ns = np.array([R[k]["body"] for k, *_ in SIZES], dtype=float)
ls = np.array([R[k]["loss"] for k, *_ in SIZES], dtype=float)
a, b = np.polyfit(np.log(ns), np.log(ls), 1)
a2, b2 = np.polyfit(np.log(ns[:2]), np.log(ls[:2]), 1)
pred = float(np.exp(a2 * np.log(ns[-1]) + b2))
err = abs(pred - ls[-1]) / ls[-1] * 100
print(f"全部四档：α = {-a:.3f}")
print(f"最小两档：α = {-a2:.3f}，外推到最大一档预测 {pred:.3f}，实测 {ls[-1]:.3f}，误差 {err:.1f}%")
print("参数放大 %.0f 倍，损失降了 %.3f" % (ns[-1] / ns[0], ls[0] - ls[-1]))
# %% [markdown]
# ## 4. 同样的算力，两种花法（任务 4）
# 把最大一档的算力（6ND）拿来训一个小一些的模型、喂更多词元：损失谁低？
# 这就是 Kaplan 与 Chinchilla 争论的那件事，只是规模小了几个数量级。
# %%
big = R["l"]
small_d, small_layers, small_heads = 128, 4, 4
probe = run(small_d, small_layers, small_heads, tokens=6_000_000)      # 先量出这一档的非嵌入参数
tokens_eq = int(big["flops"] / (6 * probe["body"]))                   # 同样算力能喂多少词元
alt = run(small_d, small_layers, small_heads, tokens=tokens_eq)
print(f"大模型：非嵌入 {big['body']/1e6:.2f}M × 6.0M 词元 → 损失 {big['loss']:.3f}")
print(f"小模型：非嵌入 {alt['body']/1e6:.2f}M × {tokens_eq/1e6:.1f}M 词元 → 损失 {alt['loss']:.3f}")
print("同样算力下更低的是：" + ("小模型多喂数据" if alt["loss"] < big["loss"] else "大模型少喂数据"))
# %% [markdown]
# ## 5. 回传结果
# %%
wqgpu.submit(xs_loss=R["xs"]["loss"], l_loss=R["l"]["loss"], alpha=float(-a),
             extrap_err_pct=err, l_tflops=R["l"]["tflops"],
             alt_loss=alt["loss"], alt_tokens_M=tokens_eq / 1e6, corpus=SRC)
print(json.dumps({k: R[k]["loss"] for k, *_ in SIZES}, ensure_ascii=False, indent=1))
