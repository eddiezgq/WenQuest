# GPU 实验 9.2 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 9.2　用 FSDP 训练约 8 亿参数的模型
# %%
import sys; sys.path.insert(0, "..")
import json
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
P = torch.cuda.device_count()
print(f"这台机器有 {P} 块 GPU" + ("" if P >= 2 else "：只能用 1 个进程跑 FSDP（能学接口，看不到切分的效果），多卡的效果用书中表 9.2.1 的实测"))
# %% [markdown]
# ## 1. 三种方式训练同一个模型（任务 1）
# 打开 `train.py`：`single` 不包装，`ddp` 每块 GPU 一份完整的模型，`fsdp` 把参数、梯度、优化器状态切成 P 份（相当于 ZeRO-3）。
# `mid` 是约 8 亿参数的模型（d = 2048、16 层）。每种方式由 torchrun（`python -m torch.distributed.run`）启动，每块 GPU 一个进程。
# %%
res = {}
for mode, n in (("single", 1), ("ddp", P), ("fsdp", P)):
    wqgpu.sh(f"{sys.executable} -m torch.distributed.run --standalone --nproc_per_node={n} train.py {mode} mid", timeout=1800)
    res[mode] = json.load(open(f"result_{mode}_mid_{n}.json"))
    r = res[mode]
    print(f"{mode:6s} {n} 块：每步 {r['ms']:.0f} ms，每块 GPU 显存峰值 {r['peak_MB'] / 1e3:.1f} GB，每秒 {r['tok_s']:.0f} 个词元")
# %% [markdown]
# ## 2. 显存为什么省了（任务 2）
# 按 9.2 节：单精度参数与 AdamW 每个参数约 16 字节（参数 4、梯度 4、两份状态 8）。算出 single 时的模型状态，与实测的峰值对照；
# FSDP 时每块 GPU 应约为它的 1/P，加上激活值与正在使用的那一层的完整参数。
# %%
n_params = res["single"]["params"]
print(f"参数 {n_params / 1e6:.0f} M，模型状态约 {16 * n_params / 1e9:.1f} GB，FSDP 时每块约 {16 * n_params / P / 1e9:.2f} GB")
# %% [markdown]
# ## 3. 回传结果
# %%
wqgpu.submit(gpus=P, params=n_params, single_ms=res["single"]["ms"], ddp_ms=res["ddp"]["ms"], fsdp_ms=res["fsdp"]["ms"],
             single_GB=res["single"]["peak_MB"] / 1e3, ddp_GB=res["ddp"]["peak_MB"] / 1e3, fsdp_GB=res["fsdp"]["peak_MB"] / 1e3)
