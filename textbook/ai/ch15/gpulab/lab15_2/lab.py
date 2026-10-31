# GPU 实验 15.2 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 15.2　深度 Q 网络：那两条技巧各值多少
# 15.2 节用 Baird 的反例说明了"价值会飞"。这里在一个真的（虽然小的）环境上训一个 DQN，
# 把经验回放与目标网络各关掉一次，看学习曲线与 Q 值各变成什么样。
# %%
import sys; sys.path.insert(0, "..")
import time
import numpy as np
import torch
import torch.nn as nn
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q 'gymnasium[classic-control]'", timeout=1800)
import gymnasium as gym
dev = "cuda"
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 环境与网络（任务 1）
# 用经典控制里的 CartPole：状态 4 个数、动作 2 个，回报上限 500。它小到能在几分钟内训完，
# 又足够让两条技巧的差别显出来。
# %%
ENV_ID, GAMMA, LR = "CartPole-v1", 0.99, 1e-3
STEPS, WARMUP, BATCH = 60_000, 1_000, 64


def make_net():
    return nn.Sequential(nn.Linear(4, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU(), nn.Linear(128, 2)).to(dev)


def evaluate(net, episodes=10, seed=0):
    e = gym.make(ENV_ID)
    rets = []
    for k in range(episodes):
        s, _ = e.reset(seed=seed + k)
        done, total = False, 0.0
        while not done:
            with torch.no_grad():
                a = int(net(torch.tensor(s, dtype=torch.float32, device=dev)).argmax())
            s, r, term, trunc, _ = e.step(a)
            total += r
            done = term or trunc
        rets.append(total)
    return float(np.mean(rets))


# %% [markdown]
# ## 2、3. 四种设置各训一遍（任务 2、3）
# replay=False 时只拿刚刚那一步学（前后高度相关）；target=False 时自举用的是当前权重（目标跟着自己跑）。
# %%
def train(replay=True, target=True, seed=0, steps=STEPS):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    e = gym.make(ENV_ID)
    net, tgt = make_net(), make_net()
    tgt.load_state_dict(net.state_dict())
    opt = torch.optim.Adam(net.parameters(), lr=LR)
    buf, curve, qmax = [], [], 0.0
    s, _ = e.reset(seed=seed)
    t0 = time.time()
    for t in range(steps):
        eps = max(0.05, 1.0 - t / (steps * 0.3))
        if rng.random() < eps:
            a = int(rng.integers(2))
        else:
            with torch.no_grad():
                a = int(net(torch.tensor(s, dtype=torch.float32, device=dev)).argmax())
        s2, r, term, trunc, _ = e.step(a)
        buf.append((s, a, r, s2, float(term)))
        if len(buf) > 50_000:
            buf.pop(0)
        s = s2
        if term or trunc:
            s, _ = e.reset()
        if t > WARMUP:
            idx = rng.integers(0, len(buf), BATCH) if replay else np.array([len(buf) - 1] * BATCH)
            bs, ba, br, bs2, bd = (np.array([buf[i][k] for i in idx]) for k in range(5))
            bs_t = torch.tensor(np.stack(bs), dtype=torch.float32, device=dev)
            bs2_t = torch.tensor(np.stack(bs2), dtype=torch.float32, device=dev)
            ba_t = torch.tensor(ba, dtype=torch.int64, device=dev)
            br_t = torch.tensor(br, dtype=torch.float32, device=dev)
            bd_t = torch.tensor(bd, dtype=torch.float32, device=dev)
            with torch.no_grad():
                nxt = (tgt if target else net)(bs2_t).max(1).values
                y = br_t + GAMMA * (1 - bd_t) * nxt
            q = net(bs_t).gather(1, ba_t[:, None]).squeeze(1)
            loss = nn.functional.smooth_l1_loss(q, y)
            opt.zero_grad(); loss.backward(); opt.step()
            qmax = max(qmax, float(q.abs().max()))
        if target and (t + 1) % 500 == 0:
            tgt.load_state_dict(net.state_dict())
        if (t + 1) % 5000 == 0:
            curve.append((t + 1, evaluate(net, 5)))
    return {"curve": curve, "final": evaluate(net, 20), "qmax": qmax,
            "sec": time.time() - t0, "steps_per_s": steps / (time.time() - t0)}


runs = {}
for name, kw in (("回放+目标网络", {}), ("去掉回放", {"replay": False}),
                 ("去掉目标网络", {"target": False}), ("两个都去掉", {"replay": False, "target": False})):
    runs[name] = train(**kw)
    r = runs[name]
    print(f"{name}: 最终回报 {r['final']:.0f}，最大 |Q| {r['qmax']:.1f}，用时 {r['sec']:.0f} s")

# %% [markdown]
# ## 4. 吞吐（任务 4）
# CartPole 跑在 CPU 上、网络在 GPU 上，每一步都要来回搬一次——这正是 15.7 节说的那笔搬运开销。
# %%
sps = runs["回放+目标网络"]["steps_per_s"]
print(f"每秒 {sps:.0f} 个环境步；跑十亿步要 {1e9 / sps / 86400:.0f} 天")
print("对照：Isaac Gym 论文在一块 A100 上给出约 70 万步/秒（8192 个环境并行）")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(ret_full=runs["回放+目标网络"]["final"], ret_noreplay=runs["去掉回放"]["final"],
             ret_notarget=runs["去掉目标网络"]["final"], qmax_full=runs["回放+目标网络"]["qmax"],
             qmax_notarget=runs["去掉目标网络"]["qmax"], steps_per_s=sps)
