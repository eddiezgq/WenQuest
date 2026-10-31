# GPU 实验 15.7 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 15.7　并行仿真：吞吐与瓶颈
# 强化学习的数据是自己跑出来的。这一节把"每秒能跑多少环境步"量出来，并把时间拆成
# 仿真、网络前向、搬数据三段，看瓶颈卡在哪。
# %%
import sys; sys.path.insert(0, "..")
import time
import numpy as np
import torch
import torch.nn as nn
import wqgpu
env = wqgpu.check(("gpu", "torch"))
dev = "cuda"
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 一个向量化的环境（任务 1）
# 为了把"仿真"这一段也放到显卡上，这里写一个最简单的向量化环境：N 个独立的二维质点，
# 每一步按动作加速、按阻尼衰减。它不是物理仿真器，但"一批一起走"这件事是一样的。
# %%
class VecPoints:
    def __init__(self, n, device=dev):
        self.n, self.device = n, device
        self.x = torch.zeros(n, 4, device=device)

    def reset(self):
        self.x = torch.randn(self.n, 4, device=self.device) * 0.1
        return self.x

    def step(self, a):
        acc = torch.nn.functional.one_hot(a, 4).float() @ torch.tensor(
            [[1.0, 0], [-1, 0], [0, 1], [0, -1]], device=self.device)
        self.x[:, 2:] = self.x[:, 2:] * 0.98 + 0.02 * acc
        self.x[:, :2] = self.x[:, :2] + self.x[:, 2:]
        r = -(self.x[:, :2] ** 2).sum(1)
        done = (self.x[:, :2].abs() > 3).any(1)
        self.x[done] = torch.randn(int(done.sum()), 4, device=self.device) * 0.1
        return self.x, r, done


net = nn.Sequential(nn.Linear(4, 128), nn.ReLU(), nn.Linear(128, 4)).to(dev)

# %% [markdown]
# ## 2. 环境数与吞吐（任务 2）
# %%
def bench(n_env, iters=200, cpu_env=False):
    e = VecPoints(n_env, "cpu" if cpu_env else dev)
    s = e.reset()
    torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(iters):
        inp = s.to(dev) if cpu_env else s
        with torch.no_grad():
            a = net(inp).argmax(1)
        s, r, d = e.step(a.cpu() if cpu_env else a)
    torch.cuda.synchronize()
    dt = time.time() - t0
    return n_env * iters / dt


rows = []
for n in (1, 16, 256, 1024, 4096, 16384):
    fps = bench(n)
    rows.append((n, fps))
    print(f"{n:6d} 个环境：{fps:12,.0f} 步/秒")
base = rows[0][1]
best = max(rows, key=lambda r: r[1])
print(f"最好的一档：{best[0]} 个环境，{best[1]:,.0f} 步/秒，比单环境快 {best[1] / base:,.0f} 倍")

# %% [markdown]
# ## 3. 时间花在哪（任务 3）
# 把三段分别计时：环境自己走一步、网络前向、以及（环境在 CPU 上时）来回搬数据。
# %%
def split(n_env, iters=200):
    e = VecPoints(n_env, dev)
    s = e.reset()
    a = torch.zeros(n_env, dtype=torch.long, device=dev)
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(iters):
        s, r, d = e.step(a)
    torch.cuda.synchronize(); t_sim = time.time() - t0
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(iters):
        with torch.no_grad():
            a = net(s).argmax(1)
    torch.cuda.synchronize(); t_net = time.time() - t0
    cpu_s = s.cpu()
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(iters):
        tmp = cpu_s.to(dev)
        _ = tmp.cpu()
    torch.cuda.synchronize(); t_move = time.time() - t0
    tot = t_sim + t_net + t_move
    return t_sim / tot * 100, t_net / tot * 100, t_move / tot * 100


shares = {}
for n in (16, 256, 4096):
    shares[n] = split(n)
    print(f"{n:5d} 个环境：仿真 {shares[n][0]:.0f}%、网络 {shares[n][1]:.0f}%、搬数据 {shares[n][2]:.0f}%")

# %% [markdown]
# ## 4. 一次训练要多久（任务 4）
# %%
for steps in (1e8, 1e9):
    print(f"{steps:.0e} 个环境步：按 {best[1]:,.0f} 步/秒要 {steps / best[1] / 3600:.1f} 小时")
print("对照（论文正文）：Isaac Gym 一块 A100 上 Ant 约 70 万步/秒；EnvPool 在 256 核上 Atari 约 107 万帧/秒")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(fps_1=rows[0][1], fps_best=best[1], envs_best=best[0], speedup=best[1] / base,
             share_sim=shares[4096][0], days_1e9=1e9 / best[1] / 86400)
