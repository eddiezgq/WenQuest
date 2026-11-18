# GPU 实验 21.8 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 21.8　剩余寿命预测，以及把它变成维护决策
# 训练一个剩余寿命模型不难，难的是**把预测变成决策**，并且把决策的好坏算成钱。
#
# 本实验分两半：
# * 前半：常印的误差指标（均方根误差、平均绝对误差）——外加一个常常不印、却更要紧的数：
#   **预测偏晚（乐观）的比例**；
# * 后半：按阈值报警，算**提前期、漏报数、总代价**，再扫一遍阈值。
#
# 口径：数据是**仿真**生成的，单位是**循环不是小时**；代价参数是示例值，要换成你们自己的。
# %%
import sys; sys.path.insert(0, "..")
import io
import zipfile

import numpy as np
import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
print(torch.cuda.get_device_name(0), torch.__version__)
wqgpu.sh(f"{sys.executable} -m pip install -q requests", timeout=1800)

# %% [markdown]
# ## 2. 数据（任务 1）
# 公开的涡扇发动机退化数据，取最简单的那个子集（一个工况、一种故障模式）。
# 取不到就用合成退化数据，并在结果里注明。
# %%
import requests

URL = "https://data.nasa.gov/download/ff5v-kuh6/application%2Fzip"
SUBSET = "FD001"
synthetic = False
train_raw = test_raw = None
try:
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = {n.split("/")[-1]: n for n in z.namelist()}
    train_raw = np.loadtxt(z.open(names[f"train_{SUBSET}.txt"]))
    test_raw = np.loadtxt(z.open(names[f"test_{SUBSET}.txt"]))
    rul_raw = np.loadtxt(z.open(names[f"RUL_{SUBSET}.txt"]))
except Exception as e:
    synthetic = True
    print(f"源站取不到（{type(e).__name__}），用合成退化数据代替——结论只作演示")

    def synth(n_units, seed):
        g = np.random.default_rng(seed)
        rows = []
        for u in range(1, n_units + 1):
            life = int(g.integers(130, 320))
            for c in range(1, life + 1):
                frac = c / life
                s = [0.4 * frac + 0.02 * g.normal(),
                     1.0 - 0.5 * frac + 0.03 * g.normal(),
                     0.2 * frac ** 2 + 0.02 * g.normal(),
                     0.1 + 0.3 * frac + 0.02 * g.normal()]
                rows.append([u, c, 0.0, 0.0, 0.0] + s)
        return np.array(rows)

    train_raw = synth(100, 1)
    test_raw = synth(100, 2)
    rul_raw = None

units_tr = np.unique(train_raw[:, 0])
units_te = np.unique(test_raw[:, 0])
print(f"子集 {SUBSET}：训练 {len(units_tr)} 台、测试 {len(units_te)} 台，"
      f"列数 {train_raw.shape[1]}（前两列是台号与循环号）")
print("数据来源：" + ("**合成**" if synthetic else "公开数据集（仿真生成，单位是循环）"))

# %% [markdown]
# ## 3. 训练与误差指标（任务 2）
# 剩余寿命的标签按惯例封顶（超过 125 个循环一律记作 125）：**太早的时候传感器看不出区别**，
# 不封顶会让模型把力气花在没有信息的那一段上。
# %%
import torch.nn as nn

CAP = 125
SENSORS = list(range(5, train_raw.shape[1]))


def windows(raw, win=30, cap=CAP, with_label=True):
    X, y, keys = [], [], []
    for u in np.unique(raw[:, 0]):
        d = raw[raw[:, 0] == u]
        s = d[:, SENSORS]
        life = len(d)
        for i in range(win, life + 1):
            X.append(s[i - win:i])
            y.append(min(cap, life - i))
            keys.append((int(u), i))
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32), keys


Xtr, ytr, _ = windows(train_raw)
mu, sd = Xtr.reshape(-1, Xtr.shape[-1]).mean(0), Xtr.reshape(-1, Xtr.shape[-1]).std(0) + 1e-6
Xtr = (Xtr - mu) / sd
Xte, yte, keys_te = windows(test_raw)
Xte = (Xte - mu) / sd
print(f"训练窗口 {len(Xtr)}，测试窗口 {len(Xte)}，每个窗口 {Xtr.shape[1]} 个循环 × "
      f"{Xtr.shape[2]} 个传感器")

dev = "cuda"
torch.manual_seed(0)
net = nn.Sequential(nn.Flatten(), nn.Linear(Xtr.shape[1] * Xtr.shape[2], 96), nn.ReLU(),
                    nn.Linear(96, 32), nn.ReLU(), nn.Linear(32, 1)).to(dev)
opt = torch.optim.Adam(net.parameters(), lr=1e-3)
Xt = torch.tensor(Xtr, device=dev); yt = torch.tensor(ytr, device=dev)[:, None]
for ep in range(20):
    perm = torch.randperm(len(Xt), device=dev)
    for i in range(0, len(perm), 256):
        b = perm[i:i + 256]
        opt.zero_grad(); nn.functional.mse_loss(net(Xt[b]), yt[b]).backward(); opt.step()

with torch.no_grad():
    pred = net(torch.tensor(Xte, device=dev)).cpu().numpy().ravel()
err = pred - yte
rmse = float(np.sqrt(np.mean(err ** 2)))
mae = float(np.mean(np.abs(err)))
late = float(np.mean(err > 0)) * 100
print(f"\n均方根误差 {rmse:.1f} 个循环，平均绝对误差 {mae:.1f} 个循环")
print(f"**预测偏晚（比真值乐观）的比例 {late:.1f}%** —— 这个数常常不印，"
      f"可它决定了报警会不会来不及")

# %% [markdown]
# ## 4. 把预测变成决策：扫一遍阈值（任务 3）
# 规则：某台设备的预测剩余寿命第一次低于阈值，就报警、安排停机。
# 三种代价：计划停机、意外失效、提前浪费（每提前一个循环）。
# %%
C_PLAN, C_FAIL, C_EARLY = 1.0, 12.0, 0.02

by_unit = {}
for (u, i), p, truth in zip(keys_te, pred, yte):
    by_unit.setdefault(u, []).append((i, float(p), float(truth)))
for u in by_unit:
    by_unit[u].sort()


def decide(thr):
    plan = fail = 0
    waste = 0.0
    leads = []
    for u, rows in by_unit.items():
        life = max(i for i, _, _ in rows) + int(rows[-1][2])
        alarm = None
        for i, p, _ in rows:
            if p <= thr:
                alarm = i
                break
        if alarm is None:
            fail += 1
            leads.append(0)
        else:
            lead = life - alarm
            if lead <= 0:
                fail += 1
                leads.append(0)
            else:
                plan += 1
                leads.append(lead)
                waste += C_EARLY * lead
    total = plan * C_PLAN + fail * C_FAIL + waste
    return {"thr": thr, "planned": plan, "failed": fail, "total": total,
            "lead_mean": float(np.mean(leads)), "lead_min": int(np.min(leads))}


rows = [decide(t) for t in range(5, 85, 5)]
for r in rows:
    print(f"阈值 {r['thr']:>3d}：平均提前 {r['lead_mean']:6.1f}、最短 {r['lead_min']:>3d} 个循环，"
          f"漏报 {r['failed']:>2d} 台，总代价 {r['total']:8.1f}")
best = min(rows, key=lambda r: r["total"])
worst = max(rows, key=lambda r: r["total"])
print(f"\n最省的阈值 {best['thr']}（代价 {best['total']:.1f}），"
      f"最贵的 {worst['thr']}（{worst['total']:.1f}）——**同一个模型差 "
      f"{worst['total'] / best['total']:.1f} 倍**")

# %% [markdown]
# ## 5. 加一条验收约束（任务 4）
# 条款：**每一台都至少提前 N 个循环报警，且不许漏报。** 看满足它的最省阈值贵多少。
# %%
for need in (10, 20, 30):
    ok = [r for r in rows if r["lead_min"] >= need and r["failed"] == 0]
    if ok:
        cheap = min(ok, key=lambda r: r["total"])
        print(f"要求最短提前 {need:>2d} 个循环：最省的合规阈值 {cheap['thr']}，"
              f"代价 {cheap['total']:.1f}（比不加约束贵 "
              f"{(cheap['total'] / best['total'] - 1) * 100:.0f}%）")
    else:
        print(f"要求最短提前 {need:>2d} 个循环：**没有阈值能满足**——"
              f"要么换模型，要么改条款，两条路都要拿数据说话")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_train_units=len(units_tr), n_test_units=len(units_te),
             rmse=rmse, mae=mae, late_share=late,
             best_thr=best["thr"], cost_best=best["total"],
             cost_ratio=worst["total"] / best["total"],
             lead_min=best["lead_min"], missed=best["failed"])
