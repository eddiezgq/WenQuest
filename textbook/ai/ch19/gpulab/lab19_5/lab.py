# GPU 实验 19.5 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 19.5　同一份卫星影像，两种划分，两个分数
# 19.5 节用一张造出来的"卫星图"说明了一件事：地表是成片的，**按像素随机划分时测试集里的每个
# 像素在训练集里都有一个紧挨着的孪生兄弟**，于是一个只会"找最像的像素"的模型就能考高分。
#
# 这个实验在真影像上把同一件事量出来：同一个模型、同一套超参数、同一批特征，
# 按像素随机划分一次、按区块划分一次，看差出几十分；再把空间自相关量出来，
# 弄清楚这几十分是从哪里漏过来的。
#
# **口径先说清楚**：本实验量的是**方法上的差距**（两种划分差多少分），不是某个数据集的绝对分数。
# 也**不要**把"随机划分会泄漏"安在某个具体公开数据集头上——泄漏是使用者怎么划分的问题。
# %%
import sys; sys.path.insert(0, "..")
import time

import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q rasterio scikit-learn matplotlib", timeout=1800)
print(torch.cuda.get_device_name(0), torch.__version__)
DEV = "cuda"

# %% [markdown]
# ## 1—2. 取一景影像与它的标注（任务 1、2）
# 影像与标注都从公开来源现取，**仓库里不放任何影像文件**。
#
# 这里用的是一景多波段影像加一张同范围的地物标注栅格。换成你自己那一景，
# 只要改下面两个地址与 `CLASSES`：后面各节都按"特征矩阵 + 类别 + 行列号"这三样来跑，
# 与影像从哪里来无关。
#
# 没有自己的影像时，把 `USE_SYNTH` 改成 True：会按 19.5 节那套玩具造一景，
# 结论的方向一样，只是绝对分数没有意义。
# %%
import rasterio

USE_SYNTH = False
IMG_URL = "https://example.invalid/scene.tif"       # ← 改成你那一景的地址（多波段反射率）
LBL_URL = "https://example.invalid/labels.tif"      # ← 改成同范围的地物标注栅格
PIX_M = 10.0                                        # 一个像素多少米（哨兵二号是 10 m）
MAX_PIX = 120_000                                   # 像素数：两两距离那一节是平方级开销


def load_real():
    with rasterio.open(IMG_URL) as src:
        img = src.read().astype(np.float32)                      # (波段, 行, 列)
        px = abs(src.transform.a)
    with rasterio.open(LBL_URL) as src:
        lbl = src.read(1).astype(np.int32)
    return img, lbl, px


def load_synth(n=384, patch=24, seed=0):
    """19.5 节那套玩具：类别成片，每一片还有自己的局地条件。"""
    g = np.random.default_rng(seed)
    nb = n // patch
    n = nb * patch                      # 边长取成块的整数倍，免得几个数组对不齐
    block_class = g.integers(0, 3, (nb, nb))
    cls = np.repeat(np.repeat(block_class, patch, 0), patch, 1)
    centers = g.normal(0, 0.45, (3, 4))
    local = np.repeat(np.repeat(g.normal(0, 1.6, (nb, nb, 4)), patch, 0), patch, 1)
    img = (centers[cls] + local + g.normal(0, 0.5, (n, n, 4))).transpose(2, 0, 1)
    return img.astype(np.float32), cls.astype(np.int32), 10.0


img, lbl, PIX_M = load_synth() if USE_SYNTH else load_real()
H, W = lbl.shape
rr, cc = np.mgrid[0:H, 0:W]
good = lbl >= 0
X = img.reshape(img.shape[0], -1).T[good.reshape(-1)]
y = lbl.reshape(-1)[good.reshape(-1)]
row = rr.reshape(-1)[good.reshape(-1)]
col = cc.reshape(-1)[good.reshape(-1)]
if len(y) > MAX_PIX:                                 # 均匀抽样，不改变空间结构
    sel = np.random.default_rng(0).choice(len(y), MAX_PIX, replace=False)
    X, y, row, col = X[sel], y[sel], row[sel], col[sel]
X = (X - X.mean(0)) / (X.std(0) + 1e-6)
CLASSES = int(y.max()) + 1
print(f"像素 {len(y):,} 个，波段 {X.shape[1]} 个，类别 {CLASSES} 类，"
      f"一个像素 {PIX_M:.0f} m，瞎猜的水平 {1 / CLASSES:.3f}")

# %% [markdown]
# ## 3. 空间自相关有多远（任务 3）
# 块要多大才够？看**自相关降到接近零的那个距离**。这里按距离分档，
# 统计每一档里"特征的相关"与"同类的比例"——两条都降下来，才算真的隔开了。
#
# 两两距离在显卡上算，分块做，免得显存炸。
# %%
Xg = torch.as_tensor(X, device=DEV)
Pg = torch.as_tensor(np.stack([row, col], 1).astype(np.float32), device=DEV)
yg = torch.as_tensor(y.astype(np.int64), device=DEV)

EDGES_PIX = np.array([1, 2, 4, 8, 16, 32, 64, 128, 256], dtype=float)
SAMPLE = min(6000, len(y))
idx = torch.as_tensor(np.random.default_rng(1).choice(len(y), SAMPLE, replace=False), device=DEV)
d = torch.cdist(Pg[idx], Pg[idx])
xs = Xg[idx]
xs = (xs - xs.mean(0)) / (xs.std(0) + 1e-6)
fcorr = (xs @ xs.T) / xs.shape[1]                    # 特征向量之间的相关
same = (yg[idx][:, None] == yg[idx][None, :]).float()

auto_rows = []
for lo, hi in zip(np.r_[0.0, EDGES_PIX[:-1]], EDGES_PIX):
    m = (d > lo) & (d <= hi)
    if m.sum() < 100:
        continue
    auto_rows.append((hi * PIX_M / 1000, float(fcorr[m].mean()), float(same[m].mean())))
    print(f"≤ {hi * PIX_M / 1000:7.2f} km　特征自相关 {auto_rows[-1][1]:+.3f}　"
          f"同类比例 {auto_rows[-1][2]:.3f}")

base_same = float(same.mean())
rng_km = next((r[0] for r in auto_rows if r[1] < 0.05 and r[2] < base_same + 0.05),
              auto_rows[-1][0])
BLOCK_PIX = int(max(8, round(rng_km * 1000 / PIX_M)))
print(f"\n自相关降到接近零大约在 {rng_km:.2f} km —— 区块边长取 {BLOCK_PIX} 像素"
      f"（{BLOCK_PIX * PIX_M / 1000:.2f} km）")

# %% [markdown]
# ## 4—5. 同一个模型，两种划分（任务 4、5）
# **三样东西写死在这一处：模型、超参数、特征。** 两种划分唯一的差别是"哪些像素进测试集"。
# 模型用最近邻——它正是"按类似物记忆"的那一类，泄漏在它身上看得最清楚。
# %%
K = 5


def knn_acc(tr, te, chunk=4096):
    """K 近邻分类的准确率，分块算距离。"""
    hit = 0
    xt, yt = Xg[tr], yg[tr]
    for s in range(0, len(te), chunk):
        q = Xg[te[s:s + chunk]]
        nn = torch.cdist(q, xt).topk(K, largest=False).indices
        votes = torch.zeros(len(q), CLASSES, device=DEV)
        votes.scatter_add_(1, yt[nn], torch.ones_like(yt[nn], dtype=torch.float))
        hit += int((votes.argmax(1) == yg[te[s:s + chunk]]).sum())
    return hit / len(te)


def split_pixels(fold, n_fold=5):
    g = np.random.default_rng(100 + fold)
    p = g.permutation(len(y)); cut = len(y) // n_fold
    return torch.as_tensor(p[cut:], device=DEV), torch.as_tensor(p[:cut], device=DEV)


def split_blocks(fold, block_pix, n_fold=5):
    """整块要么全在训练集、要么全在测试集。"""
    bid = (row // block_pix) * 10_000 + (col // block_pix)
    ub = np.unique(bid)
    g = np.random.default_rng(200 + fold)
    gb = g.permutation(ub)
    need, test_blocks, got = len(y) // n_fold, [], 0
    for b in gb:
        if got >= need:
            break
        test_blocks.append(b); got += int((bid == b).sum())
    mask = np.isin(bid, test_blocks)
    return (torch.as_tensor(np.where(~mask)[0], device=DEV),
            torch.as_tensor(np.where(mask)[0], device=DEV))


res = {}
for name, fn in (("pixel", lambda f: split_pixels(f)),
                 ("block", lambda f: split_blocks(f, BLOCK_PIX))):
    accs = []
    t0 = time.perf_counter()
    for f in range(5):
        tr, te = fn(f)
        accs.append(knn_acc(tr, te))
    res[name] = (float(np.mean(accs)), float(np.std(accs)), float(np.min(accs)))
    print(f"{name:>6}：5 折平均 {res[name][0]:.4f}　抖动 {res[name][1]:.4f}　"
          f"最差一折 {res[name][2]:.4f}　（{time.perf_counter() - t0:.1f} s）")

gap = (res["pixel"][0] - res["block"][0]) * 100
over = (res["pixel"][0] / max(res["block"][0], 1e-6) - 1) * 100
print(f"\n**两种划分差 {gap:.1f} 分，按像素划分高估了 {over:.1f}%**")
print("公开文献的量级：一项研究报告按空间划分低约 28%；一项综述给出高估 5% 到 54% 的范围，"
      "并统计 99% 的相关论文在模型选择时没有做空间校验")

# %% [markdown]
# ## 6. 块越大，分数掉到哪（任务 6）
# 块比自相关的距离尺度小，训练集里仍然有"隔壁"；块足够大，测试集才真的是"另一个地方"。
# 这条曲线的拐点在哪，决定了验收条款该写多大的块。
# %%
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sizes = [s for s in (4, 8, 16, 32, 64, 128) if s <= min(H, W) // 4]
sweep = []
for s in sizes:
    a = float(np.mean([knn_acc(*split_blocks(f, s)) for f in range(3)]))
    sweep.append((s * PIX_M / 1000, a, (res["pixel"][0] - a) * 100))
    print(f"块边长 {s:4d} 像素（{s * PIX_M / 1000:6.2f} km）　准确率 {a:.4f}　"
          f"比像素划分低 {sweep[-1][2]:5.1f} 分")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
a1.semilogx([r[0] for r in auto_rows], [r[1] for r in auto_rows], "o-", label="特征自相关")
a1.semilogx([r[0] for r in auto_rows], [r[2] for r in auto_rows], "s-", label="同类比例")
a1.axhline(base_same, ls="--", color="grey")
a1.axvline(rng_km, ls=":", color="k")
a1.set_xlabel("距离 (km)"); a1.legend(); a1.set_title("空间自相关有多远")
a2.semilogx([r[0] for r in sweep], [r[1] for r in sweep], "o-", label="按区块划分")
a2.axhline(res["pixel"][0], ls="--", color="r", label="按像素随机划分")
a2.axhline(1 / CLASSES, ls=":", color="grey", label="瞎猜")
a2.set_xlabel("块的边长 (km)"); a2.set_ylabel("准确率"); a2.legend()
a2.set_title("块越大，分数掉到哪")
fig.tight_layout(); fig.savefig("split.png", dpi=120)
print("图已存成 split.png")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_pixels=int(len(y)), n_classes=CLASSES,
             acc_pixel=res["pixel"][0], acc_block=res["block"][0],
             gap_pts=gap, overestimate_pct=over, sd_block=res["block"][1],
             range_km=float(rng_km), block_km=BLOCK_PIX * PIX_M / 1000,
             chance=1 / CLASSES)
