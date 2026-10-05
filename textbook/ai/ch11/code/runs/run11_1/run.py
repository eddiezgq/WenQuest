"""程序 11.1.1（实测）：迁移学习训练零件分类器（11.1.4 节）。A10，半精度自动混合精度。
数据由 data.py 按固定种子合成（与书中算例 11.8.1 同一个生成器：训练 2000 张、验证 500 张，四类：合格、划痕、压痕、锈斑）。
三种训练方式各训练同样的步数，比较正确率与用时：
  scratch ：ResNet-18 从随机初始化开始训练；
  linear  ：用在 ImageNet 上预训练的权重，冻住主干，只训练最后一层（线性探测）；
  finetune：用预训练的权重，整个网络一起训练（微调），学习率小一些。
结果写进 out.json（第 14 轮附 4.4 节）。"""
import json
import time

import torch
import torchvision
from torch import nn

import data

dev = "cuda"
torch.manual_seed(0)
train_x, train_y = data.tensors(2000, 0)
val_x, val_y = data.tensors(500, 4000)
train_x, train_y = train_x.to(dev), train_y.to(dev)
val_x, val_y = val_x.to(dev), val_y.to(dev)
out = {"torch": torch.__version__, "n_train": int(train_x.shape[0]), "n_val": int(val_x.shape[0]),
       "n_class": data.N_CLASS}


def build(mode):
    w = None if mode == "scratch" else torchvision.models.ResNet18_Weights.IMAGENET1K_V1
    m = torchvision.models.resnet18(weights=w)
    if mode == "linear":
        for p in m.parameters():
            p.requires_grad = False
    m.fc = nn.Linear(512, data.N_CLASS)
    return m.to(dev)


def run(mode, steps=400, batch=64):
    m = build(mode)
    lr = {"scratch": 1e-3, "linear": 3e-3, "finetune": 2e-4}[mode]
    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=lr)
    scaler = torch.amp.GradScaler("cuda")
    g = torch.Generator(device=dev).manual_seed(1)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    m.train()
    for _ in range(steps):
        idx = torch.randint(0, train_x.shape[0], (batch,), device=dev, generator=g)
        with torch.autocast("cuda", dtype=torch.float16):
            loss = nn.functional.cross_entropy(m(train_x[idx]), train_y[idx])
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
    torch.cuda.synchronize()
    secs = time.perf_counter() - t0
    m.eval()
    correct = 0
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.float16):
        for i in range(0, val_x.shape[0], 128):
            correct += (m(val_x[i:i + 128]).argmax(1) == val_y[i:i + 128]).sum().item()
    return correct / val_x.shape[0] * 100, secs, float(loss.item())


for mode in ("scratch", "linear", "finetune"):
    acc, secs, loss = run(mode)
    out[mode + "_acc"] = acc
    out[mode + "_s"] = secs
    out[mode + "_loss"] = loss
    print(mode, acc, secs)
out["gain_linear"] = out["linear_acc"] - out["scratch_acc"]
out["gain_finetune"] = out["finetune_acc"] - out["scratch_acc"]
out["speed_linear"] = out["scratch_s"] / out["linear_s"]
out["_gpu_name"] = torch.cuda.get_device_name(0)
json.dump(out, open("out.json", "w"), ensure_ascii=False)
print(out)
if out["finetune_acc"] < out["scratch_acc"]:            # 实测之前不下断言：任务太容易时三者都可能满分
    print("提醒：微调没有胜过从头训练——多半是这个合成任务太容易，减少训练步数或加大难度再看")
