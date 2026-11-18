# GPU 实验 21.7 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 21.7　给视觉检测模型写验证方案，并真的验一遍
# 这个实验的顺序是**故意**的：先写判据，再造数据，最后才训练。倒过来做，这份记录就没有意义。
#
# 四步：
# 1. 写下**预期用途**与**验收判据**；
# 2. 按判据**反算要测多少件**（置信下限）；
# 3. **按批次留出**验证集，实测并算置信界；
# 4. 换批次、重训一版，做**变更影响评估**。
#
# 口径：本实验只做技术记录，**不讨论怎么通过审核**；图像是合成的，数字不要外引。
# %%
import sys; sys.path.insert(0, "..")
import numpy as np
import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
print(torch.cuda.get_device_name(0), torch.__version__)
wqgpu.sh(f"{sys.executable} -m pip install -q scipy", timeout=1800)

# %% [markdown]
# ## 2. 预期用途与判据（任务 1）
# 把这几行改成你们自己的数。**先写在这里，后面一个字都不许改。**
# %%
INTENDED_USE = ("在减速器壳体精加工后、装配前，对密封面做在线外观检测，"
                "判出划伤与磕碰；判为不良的零件进入人工复检，不直接报废。")
RECALL_TARGET = 0.95      # 查全率判据（对缺陷件）
FPR_TARGET = 0.05         # 误判率判据（对好件）
CONF = 0.95               # 置信水平
UNIT = "按零件（同一零件的 3 张图任一报警即判不良）"

from scipy.stats import beta


def lcb(k, n, conf=CONF):
    """二项比例的精确置信下限（Clopper–Pearson）。"""
    if n == 0:
        return 0.0
    if k == n:
        return float((1 - conf) ** (1 / n))
    return float(beta.ppf(1 - conf, k, n - k + 1))


def ucb(k, n, conf=CONF):
    if n == 0:
        return 1.0
    if k == 0:
        return float(1 - (1 - conf) ** (1 / n))
    return float(beta.ppf(conf, k + 1, n - k))


n_def = 1
while lcb(n_def, n_def) < RECALL_TARGET:     # 全对的情况下至少要多少件
    n_def += 1
n_good = 1
while ucb(0, n_good) > FPR_TARGET:           # 一个都不误判的情况下至少要多少件
    n_good += 1
print(f"预期用途：{INTENDED_USE}")
print(f"判据：查全率的 {CONF:.0%} 置信下限 ≥ {RECALL_TARGET:.0%}；"
      f"误判率的 {CONF:.0%} 置信上限 ≤ {FPR_TARGET:.0%}；{UNIT}")
print(f"\n**反算样本量**：缺陷件至少 {n_def} 件（且必须全部判对），"
      f"好件至少 {n_good} 件（且一件都不许误判）")
print("注意这是**最理想情况**下的下限：只要错一件，需要的件数立刻涨上去——")
for miss in (1, 2, 3):
    n = n_def
    while lcb(n - miss, n) < RECALL_TARGET:
        n += 1
    print(f"  允许错 {miss} 件时，缺陷件要 {n} 件")

# %% [markdown]
# ## 3. 数据：按批次留出（任务 2）
# 合成图像：灰底 + 加工纹理 + 随机光照，缺陷是细划痕或小凹坑。
# **三个批次**：批次 0、1 用来训练，批次 2 完全留出；批次 3 模拟“换了供应商”（纹理与光照不同）。
# %%
H = W = 64


def make_batch(n, batch, defect_rate=0.3, seed=0):
    g = np.random.default_rng(seed + batch * 1000)
    tone = 0.45 + 0.08 * batch                     # 每个批次的底色不同
    grain = 0.05 + 0.02 * (batch % 3)
    imgs, labels = [], []
    for i in range(n):
        im = tone + grain * g.normal(0, 1, (H, W))
        im += 0.06 * np.sin(np.linspace(0, 8 * np.pi, W))[None, :]   # 加工纹理
        bad = g.random() < defect_rate
        if bad:
            if g.random() < 0.5:                   # 划痕
                r0, c0 = g.integers(8, H - 8), g.integers(8, W - 24)
                im[r0:r0 + 1, c0:c0 + int(g.integers(10, 20))] -= 0.22
            else:                                  # 凹坑
                r0, c0 = g.integers(6, H - 6), g.integers(6, W - 6)
                rr, cc = np.ogrid[:H, :W]
                im -= 0.3 * np.exp(-(((rr - r0) ** 2 + (cc - c0) ** 2) / 6.0))
        imgs.append(im.astype(np.float32)); labels.append(int(bad))
    return np.stack(imgs), np.array(labels)


train_X, train_y = [], []
for b in (0, 1):
    x, y = make_batch(1500, b, seed=1)
    train_X.append(x); train_y.append(y)
train_X = np.concatenate(train_X); train_y = np.concatenate(train_y)
val_X, val_y = make_batch(max(2000, n_def * 4), 2, seed=7)          # 留出批次
new_X, new_y = make_batch(2000, 3, seed=11)                        # 新供应商批次
print(f"训练 {len(train_X)} 件（批次 0、1），验证 {len(val_X)} 件（批次 2，完全留出），"
      f"新批次 {len(new_X)} 件")
print(f"验证集里缺陷件 {int(val_y.sum())} 件——判据要求至少 {n_def} 件，"
      f"{'够' if val_y.sum() >= n_def else '**不够，要补样品**'}")

# %% [markdown]
# ## 4. 训练与实测（任务 3）
# %%
import torch.nn as nn

dev = "cuda"


def train(X, y, seed=0, epochs=12):
    torch.manual_seed(seed)
    net = nn.Sequential(nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                        nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                        nn.Flatten(), nn.Linear(16 * 16 * 16, 32), nn.ReLU(),
                        nn.Linear(32, 2)).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    lossf = nn.CrossEntropyLoss()
    Xt = torch.tensor(X[:, None], device=dev)
    yt = torch.tensor(y, device=dev)
    for _ in range(epochs):
        perm = torch.randperm(len(Xt), device=dev)
        for i in range(0, len(perm), 128):
            b = perm[i:i + 128]
            opt.zero_grad(); lossf(net(Xt[b]), yt[b]).backward(); opt.step()
    return net


def measure(net, X, y, thr=0.5):
    with torch.no_grad():
        p = torch.softmax(net(torch.tensor(X[:, None], device=dev)), 1)[:, 1].cpu().numpy()
    pred = (p >= thr).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
    return {"tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "recall": tp / max(tp + fn, 1), "fpr": fp / max(fp + tn, 1),
            "recall_lcb": lcb(tp, tp + fn), "fpr_ucb": ucb(fp, fp + tn)}


net = train(train_X, train_y, seed=0)
m = measure(net, val_X, val_y)
ok = (m["recall_lcb"] >= RECALL_TARGET) and (m["fpr_ucb"] <= FPR_TARGET)
print(f"验证集（批次 2，{len(val_X)} 件）：")
print(f"  查全率 {m['recall']:.3%}（95% 下限 {m['recall_lcb']:.3%}，判据 ≥ {RECALL_TARGET:.0%}）")
print(f"  误判率 {m['fpr']:.3%}（95% 上限 {m['fpr_ucb']:.3%}，判据 ≤ {FPR_TARGET:.0%}）")
print(f"  **结论：{'通过' if ok else '不通过'}**")
print("注意点估计与置信界的差：件数越少，两者差得越远——这正是样本量判据存在的理由")

# %% [markdown]
# ## 5. 换一个批次（任务 4）
# 来料换供应商、换模具、换班次，都属于“实际使用条件变了”。
# %%
mn = measure(net, new_X, new_y)
drift = (m["recall"] - mn["recall"]) * 100
print(f"新批次（批次 3）：查全率 {mn['recall']:.3%}（原批次 {m['recall']:.3%}，"
      f"掉了 {drift:.1f} 个百分点），误判率 {mn['fpr']:.3%}")
print(f"按判据算：{'仍然通过' if mn['recall_lcb'] >= RECALL_TARGET and mn['fpr_ucb'] <= FPR_TARGET else '**不通过——这就是要重新验证的信号**'}")

# %% [markdown]
# ## 6. 重训一版：变更影响评估（任务 5）
# 把新批次的一半并进训练集重训，然后回答三个问题：改了什么、怎么验证、影响多大。
# %%
half = len(new_X) // 2
X2 = np.concatenate([train_X, new_X[:half]])
y2 = np.concatenate([train_y, new_y[:half]])
net2 = train(X2, y2, seed=0)
m2_old = measure(net2, val_X, val_y)
m2_new = measure(net2, new_X[half:], new_y[half:])
retrain_gap = (m2_old["recall"] - m["recall"]) * 100
print("变更影响评估：")
print(f"  改了什么：训练集加入新批次的 {half} 件（分布变了，网络结构与超参数没变）")
print(f"  怎么验证：同一份验证集（批次 2）+ 新批次留出的另一半，判据不变")
print(f"  影响多大：原批次查全率 {m['recall']:.3%} → {m2_old['recall']:.3%}"
      f"（{retrain_gap:+.1f} 个百分点）；新批次 {mn['recall']:.3%} → {m2_new['recall']:.3%}")
print(f"  原判据在重训版上：{'仍然成立' if m2_old['recall_lcb'] >= RECALL_TARGET and m2_old['fpr_ucb'] <= FPR_TARGET else '不成立'}")
print("\n**这三行就是一份变更影响评估的骨架**：改什么、怎么验证、影响多大。"
      "把它事先写好，就是“预定变更控制计划”要求的那三件事")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_train=len(train_X), n_test=len(val_X), n_required=n_def,
             recall_point=m["recall"] * 100, recall_lcb=m["recall_lcb"] * 100,
             fpr_point=m["fpr"] * 100, fpr_ucb=m["fpr_ucb"] * 100,
             pass_criteria=1 if ok else 0,
             drift_gap=drift, retrain_gap=retrain_gap)
