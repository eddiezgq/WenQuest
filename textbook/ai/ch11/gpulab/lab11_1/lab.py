# GPU 实验 11.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 11.1　用迁移学习训练零件分类器
# %%
import sys; sys.path.insert(0, "..")
import time
import torch
import torchvision
from torch import nn
import wqgpu
import data
env = wqgpu.check(("gpu", "torch"))
dev = "cuda"
print(torch.cuda.get_device_name(0))
# %% [markdown]
# ## 1. 数据（任务 1）
# 四类：合格、划痕、压痕、锈斑。图像由 `data.py` 按固定种子合成——同一个种子永远得到同一张图，
# 实验可复现。先看看每类长什么样，再数一数类别分布。
# %%
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 4, figsize=(11, 3))
shown = set()
for seed in range(400):
    img, cls = data.sample(seed)
    if cls not in shown:
        shown.add(cls)
        axes[cls].imshow(img, cmap="gray"); axes[cls].set_title(data.CLASSES[cls]); axes[cls].axis("off")
    if len(shown) == 4: break
plt.show()
train_x, train_y = data.tensors(2000, 0)
val_x, val_y = data.tensors(500, 4000)
print("训练", train_x.shape, "验证", val_x.shape, "各类数量", torch.bincount(train_y).tolist())
train_x, train_y, val_x, val_y = train_x.to(dev), train_y.to(dev), val_x.to(dev), val_y.to(dev)
# %% [markdown]
# ## 2. 三种训练方式（任务 2）
# `scratch` 从随机初始化开始；`linear` 冻住在 ImageNet 上预训练的主干、只训练最后一层；`finetune` 整个网络一起训练。
# 三者训练同样的步数，比较验证集正确率与用时。
# %%
def build(mode):
    w = None if mode == "scratch" else torchvision.models.ResNet18_Weights.IMAGENET1K_V1
    m = torchvision.models.resnet18(weights=w)
    if mode == "linear":
        for p in m.parameters(): p.requires_grad = False
    m.fc = nn.Linear(512, data.N_CLASS)
    return m.to(dev)

def run(mode, steps=400, batch=64):
    m, lr = build(mode), {"scratch": 1e-3, "linear": 3e-3, "finetune": 2e-4}[mode]
    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=lr)
    scaler = torch.amp.GradScaler("cuda")
    g = torch.Generator(device=dev).manual_seed(1)
    torch.cuda.synchronize(); t0 = time.perf_counter(); m.train()
    for _ in range(steps):
        idx = torch.randint(0, train_x.shape[0], (batch,), device=dev, generator=g)
        with torch.autocast("cuda", dtype=torch.float16):
            loss = nn.functional.cross_entropy(m(train_x[idx]), train_y[idx])
        opt.zero_grad(set_to_none=True); scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
    torch.cuda.synchronize(); secs = time.perf_counter() - t0
    m.eval(); correct = 0
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
        for i in range(0, val_x.shape[0], 128):
            correct += (m(val_x[i:i+128]).argmax(1) == val_y[i:i+128]).sum().item()
    return correct / val_x.shape[0] * 100, secs

res = {}
for mode in ("scratch", "linear", "finetune"):
    acc, secs = res[mode] = run(mode)
    print(f"{mode:9s} 正确率 {acc:5.1f}%　用时 {secs:5.1f} s")
# %% [markdown]
# ## 3. 改一改（任务 3）
# 把训练步数减到 100 步：三种方式的差距变大还是变小？为什么预训练的权重在数据少、步数少时更占便宜？
# %%
# 在这里把 steps 改小后重跑上一格
# %% [markdown]
# ## 4. 回传结果
# %%
wqgpu.submit(scratch_acc=res["scratch"][0], linear_acc=res["linear"][0], finetune_acc=res["finetune"][0],
             scratch_s=res["scratch"][1], linear_s=res["linear"][1], finetune_s=res["finetune"][1])
