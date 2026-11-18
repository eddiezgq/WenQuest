# GPU 实验 21.3 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 21.3　故障诊断模型，以及用三种口径验收它
# 训练只是这个实验的一半。另一半——**也是更要紧的一半**——是把同一个模型用三种划分口径
# 各验收一遍：按窗口随机、按工况（负载/转速）、按时间顺序。
#
# **先把口径说清楚**：
#
# * 三个准确率回答三个不同的问题，**不能平均、不能只报一个**；
# * 公开数据里的故障是**电火花加工出来的单点缺陷**，与现场的分布式剥落不是一回事；
# * 本实验**不排名算法**：模型故意取小，要量的是三个数之间的**差距**。
# %%
import sys; sys.path.insert(0, "..")
import time

import numpy as np
import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
print(torch.cuda.get_device_name(0), torch.__version__)
wqgpu.sh(f"{sys.executable} -m pip install -q scipy requests", timeout=1800)

# %% [markdown]
# ## 1. 数据（任务 2）
# 公开的滚动轴承振动数据：几种状态（正常、外圈、内圈、滚动体故障），每种在几个负载下
# 各有一段连续采集。下载之后按固定长度切窗口，**每个窗口记住它来自哪一段采集、哪个负载、
# 在那段里的第几个位置**——这三样是后面做划分用的，缺一样就只能做随机划分。
# %%
import io
import requests
from scipy.io import loadmat

# 这些是公开数据集的记录编号；若源站暂时取不到，实验会退回到合成信号（并在结果里注明）
RECORDS = {"normal": [97, 98, 99, 100], "outer": [130, 131, 132, 133],
           "inner": [105, 106, 107, 108], "ball": [118, 119, 120, 121]}
LOADS = [0, 1, 2, 3]          # 马力；与上面每组四条记录一一对应
RPMS = [1797, 1772, 1750, 1730]
WIN, STRIDE, FS = 2048, 1024, 12000.0
BASE = "https://engineering.case.edu/sites/default/files/"

raw, synthetic = {}, False
for cls, ids in RECORDS.items():
    for rec, load, rpm in zip(ids, LOADS, RPMS):
        try:
            r = requests.get(f"{BASE}{rec}.mat", timeout=60)
            r.raise_for_status()
            m = loadmat(io.BytesIO(r.content))
            key = [k for k in m if k.endswith("DE_time")][0]
            raw[(cls, load)] = (np.asarray(m[key]).ravel().astype(np.float32), rpm)
        except Exception as e:                      # 取不到就合成，实验照样能做
            synthetic = True
            print(f"  取 {cls}/{load} 失败（{type(e).__name__}），用合成信号代替")
            n = int(FS * 10)
            t = np.arange(n) / FS
            g = np.random.default_rng(rec)
            x = 0.35 * g.normal(0, 1, n) + 0.25 * np.sin(2 * np.pi * rpm / 60 * t)
            if cls != "normal":
                hz = {"outer": 3.585, "inner": 5.415, "ball": 2.357}[cls] * rpm / 60
                k = 0
                while k / hz < 10:
                    i0 = int(k / hz * FS); mm = min(n - i0, int(0.004 * FS))
                    if mm > 0:
                        tt = np.arange(mm) / FS
                        x[i0:i0 + mm] += np.exp(-900 * tt) * np.sin(2 * np.pi * 3200 * tt)
                    k += 1
            raw[(cls, load)] = (x.astype(np.float32), rpm)

X, y, meta = [], [], []
classes = list(RECORDS)
for (cls, load), (sig, rpm) in raw.items():
    for pos, i in enumerate(range(0, len(sig) - WIN, STRIDE)):
        X.append(sig[i:i + WIN]); y.append(classes.index(cls))
        meta.append({"load": load, "rpm": rpm, "pos": pos, "cls": cls})
X = np.stack(X); y = np.array(y)
print(f"\n样本 {len(X)} 个，每个 {WIN} 点；"
      f"各类：{ {c: int((y == i).sum()) for i, c in enumerate(classes)} }")
print("数据来源：" + ("**合成信号**（源站取不到，结论只作演示）" if synthetic else "公开数据集"))

# %% [markdown]
# ## 2. 特征频率：算出来的与找出来的（任务 3）
# 先按几何算，再去包络谱上找。两者必须对得上——**对不上先查窗口长度与转速，不要先怪模型**。
# %%
N_BALLS, D_BALL, D_PITCH = 9, 7.94, 39.04


def freqs(rpm):
    fr = rpm / 60.0
    ratio = D_BALL / D_PITCH
    return {"fr": fr, "BPFO": N_BALLS / 2 * fr * (1 - ratio),
            "BPFI": N_BALLS / 2 * fr * (1 + ratio)}


def envelope_spectrum(x, fs=FS):
    n = len(x)
    Xf = np.fft.fft(x)
    h = np.zeros(n); h[0] = 1
    if n % 2 == 0:
        h[n // 2] = 1; h[1:n // 2] = 2
    else:
        h[1:(n + 1) // 2] = 2
    env = np.abs(np.fft.ifft(Xf * h))
    env = env - env.mean()
    w = np.hanning(n)
    return np.fft.rfftfreq(n, 1 / fs), np.abs(np.fft.rfft(env * w)) / n * 2


sig, rpm = raw[("outer", 0)]
seg = sig[:WIN * 8]
f_th = freqs(rpm)
fe, E = envelope_spectrum(seg)
m = (fe > f_th["BPFO"] - 6) & (fe < f_th["BPFO"] + 6)
found = float(fe[m][int(np.argmax(E[m]))])
err = abs(found - f_th["BPFO"]) / f_th["BPFO"] * 100
print(f"转速 {rpm} r/min：轴频 {f_th['fr']:.2f} Hz，算出的 BPFO {f_th['BPFO']:.2f} Hz，"
      f"包络谱上找到 {found:.2f} Hz，差 {err:.2f}%")
print(f"换一个转速（{RPMS[-1]} r/min）：BPFO 变成 {freqs(RPMS[-1])['BPFO']:.2f} Hz —— "
      f"差 {abs(freqs(RPMS[-1])['BPFO'] - f_th['BPFO']):.2f} Hz，**所以转速必须进模型**")

# %% [markdown]
# ## 3. 三种划分，各训一遍（任务 4）
# 模型故意取小：对数频谱 + 两层全连接。**要量的是三个数之间的差距，不是哪个模型更好。**
# %%
import torch.nn as nn


def features(batch):
    w = np.hanning(WIN)
    S = np.abs(np.fft.rfft(batch * w, axis=1)) / WIN * 2
    return np.log1p(S[:, :512]).astype(np.float32)


F = features(X)
dev = "cuda"


def split(how):
    idx = np.arange(len(X))
    if how == "random":
        g = np.random.default_rng(0); g.shuffle(idx)
        cut = int(len(idx) * 0.75)
        return idx[:cut], idx[cut:]
    if how == "load":                         # 留出一个负载完全不参加训练
        held = 3
        tr = np.array([i for i in idx if meta[i]["load"] != held])
        te = np.array([i for i in idx if meta[i]["load"] == held])
        return tr, te
    if how == "time":                         # 每段采集的前 75% 训练、后 25% 测试
        tr, te = [], []
        for i in idx:
            top = max(m2["pos"] for m2 in meta if m2["load"] == meta[i]["load"]
                      and m2["cls"] == meta[i]["cls"])
            (tr if meta[i]["pos"] <= top * 0.75 else te).append(i)
        return np.array(tr), np.array(te)
    raise ValueError(how)


def run(how, epochs=25):
    tr, te = split(how)
    mu, sd = F[tr].mean(0), F[tr].std(0) + 1e-6      # 用训练集的统计量
    Xtr = torch.tensor((F[tr] - mu) / sd, device=dev)
    Xte = torch.tensor((F[te] - mu) / sd, device=dev)
    ytr = torch.tensor(y[tr], device=dev)
    yte = torch.tensor(y[te], device=dev)
    torch.manual_seed(0)
    net = nn.Sequential(nn.Linear(Xtr.shape[1], 64), nn.ReLU(),
                        nn.Linear(64, len(classes))).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=3e-3)
    lossf = nn.CrossEntropyLoss()
    t0 = time.perf_counter()
    for _ in range(epochs):
        perm = torch.randperm(len(Xtr), device=dev)
        for i in range(0, len(perm), 256):
            b = perm[i:i + 256]
            opt.zero_grad(); loss = lossf(net(Xtr[b]), ytr[b]); loss.backward(); opt.step()
    wall = time.perf_counter() - t0
    with torch.no_grad():
        pred = net(Xte).argmax(1)
        acc = float((pred == yte).float().mean()) * 100
    return acc, wall, pred.cpu().numpy(), y[te]


res = {}
for how, name in (("random", "按窗口随机"), ("load", "按工况（留出一个负载）"),
                  ("time", "按时间顺序（前 75% 训、后 25% 测）")):
    acc, wall, pred, truth = run(how)
    res[how] = (acc, wall, pred, truth)
    print(f"{name:>28}：准确率 {acc:6.2f}%　训练 {wall:5.1f} 秒")

gap = res["random"][0] - res["load"][0]
print(f"\n**随机划分比按工况高 {gap:.1f} 个百分点**——"
      f"前者回答“见过的工况里认不认得出来”，后者回答“换个负载还准不准”")
print("这两个问题的答案差这么多，而报告里常常只印前一个")

# %% [markdown]
# ## 4. 按工况划分时，错的是哪几类（任务 5）
# %%
acc, wall, pred, truth = res["load"]
cm = np.zeros((len(classes), len(classes)), dtype=int)
for t, p in zip(truth, pred):
    cm[t, p] += 1
print("行 = 真实，列 = 预测　" + "  ".join(f"{c:>6}" for c in classes))
for i, c in enumerate(classes):
    print(f"{c:>8} " + "  ".join(f"{n:6d}" for n in cm[i]))
print("\n看混淆矩阵比看一个准确率有用得多：错在哪两类之间，就知道该补哪一类数据")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_samples=len(X), win_len=WIN,
             acc_random=res["random"][0], acc_load=res["load"][0],
             acc_time=res["time"][0], gap_random_load=gap,
             bpfo_hz=f_th["BPFO"], bpfo_found_hz=found, bpfo_err_pct=err,
             train_s=res["random"][1])
