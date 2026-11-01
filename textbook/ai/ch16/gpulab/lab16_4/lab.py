# GPU 实验 16.4 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 16.4　引导强度：把分布推偏到什么程度
# 16.4 节在一个一维玩具上把这件事算了出来：引导一调强，单张更"像这一类"，分布却明显偏了，
# 两类共用的那个峰直接被挤掉。那里的最优噪声预测器有解析式，所以结论是算出来的。
#
# 这里换成真模型：训一个条件扩散模型生成 32×32 的缺陷图（四类），实现无分类器引导，
# 把强度从 0 扫到 8，量三件事——像不像这一类、同一类里还剩多少花样、整批与真图差多远。
# 训练数据是程序现画的，不下载任何权重，也没有真实照片。
# %%
import sys; sys.path.insert(0, "..")
import math
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import wqgpu
env = wqgpu.check(("gpu", "torch"))
dev = "cuda"
torch.manual_seed(0)
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 训练数据：四类缺陷图（任务 1）
# 与 16.8 节的案例同一套画法，只是放到 32×32：磨削底纹（朝向、疏密、照明每张都不一样）
# 加上划痕、压痕、锈斑。严重度在 0.3—1.0 之间——比书里的案例重一些，
# 因为这里要看的是"生成得像不像"，不是"检测难不难"。
# %%
N, KINDS = 32, ("无缺陷", "划痕", "压痕", "锈斑")


def draw(kind, sev, g):
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    ang, lam = g.uniform(0, np.pi), g.uniform(2.6, 5.0)
    u = x * np.cos(ang) + y * np.sin(ang)
    img = (0.50 + 0.085 * np.sin(2 * np.pi * u / lam + g.uniform(0, 2 * np.pi))
           + 0.030 * np.sin(2 * np.pi * u / (lam * 2.3) + g.uniform(0, 2 * np.pi))
           + 0.060 * np.cos((x / N - 0.5) * 2.0 + g.uniform(-0.4, 0.4))
           + 0.040 * (y / N - 0.5) + g.normal(0, 0.012, (N, N)))
    if kind == 1:
        x0, y0 = g.uniform(5, N - 5), g.uniform(5, N - 5)
        a, ln = g.uniform(0, np.pi), g.uniform(7, 17)
        t = np.clip(((x - x0) * np.cos(a) + (y - y0) * np.sin(a)) / ln, 0, 1)
        d = np.hypot(x - (x0 + t * ln * np.cos(a)), y - (y0 + t * ln * np.sin(a)))
        img -= 0.45 * sev * np.exp(-(d / 0.8) ** 2)
    elif kind == 2:
        x0, y0, r = g.uniform(6, N - 6), g.uniform(6, N - 6), g.uniform(2, 4)
        d = np.hypot(x - x0, y - y0)
        img += -0.40 * sev * np.exp(-(d / r) ** 2) + 0.20 * sev * np.exp(-((d - r) / 0.9) ** 2)
    elif kind == 3:
        x0, y0, r = g.uniform(6, N - 6), g.uniform(6, N - 6), g.uniform(3, 5)
        d = np.hypot(x - x0, y - y0)
        img += 0.35 * sev * np.exp(-(d / r) ** 2) * (1 + 0.5 * g.normal(0, 1, (N, N)))
    return np.clip(img, 0, 1).astype(np.float32)


def dataset(n, seed=0, sev=(0.3, 1.0)):
    g = np.random.default_rng(seed)
    X = np.empty((n, 1, N, N), np.float32)
    y = np.empty(n, np.int64)
    for i in range(n):
        k = int(g.integers(4))
        X[i, 0] = draw(k, float(g.uniform(*sev)), g)
        y[i] = k
    return torch.tensor(X), torch.tensor(y)


t0 = time.time()
Xtr, ytr = dataset(8000, 0)
Xte, yte = dataset(2000, 99)
print(f"训练 {len(Xtr)} 张，测试 {len(Xte)} 张，画图用了 {time.time() - t0:.0f} s")
print("各类张数：", [int((ytr == k).sum()) for k in range(4)])

# %% [markdown]
# ## 2. 条件扩散模型与评价用的分类器（任务 2）
# 噪声预测器是一个小的 U 形网络：输入 (x_t, t, c)，输出 ε̂。类别 c 有五个取值——四类加一个"空"，
# 训练时按 10% 的概率换成"空"，这样同一个网络既会有条件预测，也会无条件预测（16.4 节）。
# %%
T, BETA = 400, None
beta = torch.linspace(1e-4, 0.02, T, device=dev)
alpha = 1 - beta
abar = torch.cumprod(alpha, 0)
NULL = 4                                     # "空"类别


def temb(t, dim=64):
    half = dim // 2
    f = torch.exp(-math.log(10000) * torch.arange(half, device=t.device) / half)
    a = t.float()[:, None] * f[None]
    return torch.cat([a.sin(), a.cos()], 1)


class Block(nn.Module):
    def __init__(self, cin, cout, emb=128):
        super().__init__()
        self.c1 = nn.Conv2d(cin, cout, 3, padding=1)
        self.c2 = nn.Conv2d(cout, cout, 3, padding=1)
        self.e = nn.Linear(emb, cout)
        self.n1, self.n2 = nn.GroupNorm(8, cout), nn.GroupNorm(8, cout)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()

    def forward(self, x, e):
        h = F.silu(self.n1(self.c1(x)))
        h = h + self.e(e)[:, :, None, None]
        h = F.silu(self.n2(self.c2(h)))
        return h + self.skip(x)


class UNet(nn.Module):
    def __init__(self, ch=64, emb=128):
        super().__init__()
        self.tp = nn.Sequential(nn.Linear(64, emb), nn.SiLU(), nn.Linear(emb, emb))
        self.cls = nn.Embedding(5, emb)
        self.inp = nn.Conv2d(1, ch, 3, padding=1)
        self.d1, self.d2 = Block(ch, ch, emb), Block(ch, 2 * ch, emb)
        self.mid = Block(2 * ch, 2 * ch, emb)
        self.u2, self.u1 = Block(4 * ch, ch, emb), Block(2 * ch, ch, emb)
        self.out = nn.Conv2d(ch, 1, 3, padding=1)

    def forward(self, x, t, c):
        e = self.tp(temb(t)) + self.cls(c)
        h0 = self.inp(x)
        h1 = self.d1(h0, e)
        h2 = self.d2(F.avg_pool2d(h1, 2), e)
        m = self.mid(h2, e)
        u2 = self.u2(torch.cat([m, h2], 1), e)
        u2 = F.interpolate(u2, scale_factor=2, mode="nearest")
        u1 = self.u1(torch.cat([u2, h1], 1), e)
        return self.out(u1)


def train_diffusion(epochs=18, bs=128, lr=2e-4, p_drop=0.1):
    net = UNet().to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    X = (Xtr * 2 - 1).to(dev)                 # 归一到 [-1, 1]
    y = ytr.to(dev)
    n = len(X)
    t0 = time.time()
    for ep in range(epochs):
        perm = torch.randperm(n, device=dev)
        tot = 0.0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            x0, c = X[idx], y[idx].clone()
            c[torch.rand(len(c), device=dev) < p_drop] = NULL      # 按概率换成"空"
            t = torch.randint(0, T, (len(x0),), device=dev)
            eps = torch.randn_like(x0)
            a = abar[t][:, None, None, None]
            xt = a.sqrt() * x0 + (1 - a).sqrt() * eps
            loss = F.mse_loss(net(xt, t, c), eps)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += float(loss) * len(x0)
        if ep % 3 == 0 or ep == epochs - 1:
            print(f"  第 {ep + 1} 轮，损失 {tot / n:.4f}，已用 {time.time() - t0:.0f} s")
    return net, time.time() - t0


net, sec_train = train_diffusion()
print(f"扩散模型训好了，用时 {sec_train:.0f} s")


class Clf(nn.Module):
    """评价用的小分类器：它同时给出类别打分和一组特征（弗雷歇距离就在这组特征上算）。"""
    def __init__(self, ch=32):
        super().__init__()
        self.f = nn.Sequential(nn.Conv2d(1, ch, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                               nn.Conv2d(ch, 2 * ch, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                               nn.Conv2d(2 * ch, 2 * ch, 3, padding=1), nn.ReLU(),
                               nn.AdaptiveAvgPool2d(1), nn.Flatten())
        self.head = nn.Linear(2 * ch, 4)

    def forward(self, x, feat=False):
        z = self.f(x)
        return z if feat else self.head(z)


def train_clf(epochs=12, bs=128):
    c = Clf().to(dev)
    opt = torch.optim.Adam(c.parameters(), lr=1e-3)
    X, y = Xtr.to(dev), ytr.to(dev)
    for _ in range(epochs):
        perm = torch.randperm(len(X), device=dev)
        for i in range(0, len(X), bs):
            idx = perm[i:i + bs]
            loss = F.cross_entropy(c(X[idx]), y[idx])
            opt.zero_grad(); loss.backward(); opt.step()
    c.eval()
    with torch.no_grad():
        acc = float((c(Xte.to(dev)).argmax(1) == yte.to(dev)).float().mean())
    return c, acc


clf, clf_acc = train_clf()
print(f"评价用的分类器在真图上的准确率 {clf_acc * 100:.1f}%——它本身也会错，读数时要记得这一点")

# %% [markdown]
# ## 3. 引导强度扫描（任务 3）
# ε̃ = (1+w)·ε(x,c) − w·ε(x)。w = 0 就是不引导。每一档采 256 张，量三件事：
# 与真图的弗雷歇距离（整批像不像）、类别一致率（单张像不像这一类）、同类两两平均距离（还剩多少花样）。
# %%
@torch.no_grad()
def sample(n, cls, w, steps=100):
    x = torch.randn(n, 1, N, N, device=dev)
    c = torch.full((n,), cls, device=dev, dtype=torch.long)
    cn = torch.full((n,), NULL, device=dev, dtype=torch.long)
    ts = torch.linspace(T - 1, 0, steps).long().to(dev)
    for i in range(len(ts)):
        t = ts[i].expand(n)
        e = net(x, t, c)
        if w > 0:
            e = (1 + w) * e - w * net(x, t, cn)
        a = abar[ts[i]]
        x0 = ((x - (1 - a).sqrt() * e) / a.sqrt()).clamp(-1, 1)
        ap = abar[ts[i + 1]] if i + 1 < len(ts) else torch.tensor(1.0, device=dev)
        if i + 1 == len(ts):
            x = x0
            break
        sig = ((1 - ap) / (1 - a) * (1 - a / ap)).clamp(min=0).sqrt()
        x = ap.sqrt() * x0 + (1 - ap - sig ** 2).clamp(min=0).sqrt() * e + sig * torch.randn_like(x)
    return (x + 1) / 2


@torch.no_grad()
def feats(x):
    return clf(x.to(dev), feat=True)


def frechet(a, b):
    a, b = a.double().cpu().numpy(), b.double().cpu().numpy()
    m1, m2 = a.mean(0), b.mean(0)
    c1 = np.cov(a, rowvar=False) + 1e-6 * np.eye(a.shape[1])
    c2 = np.cov(b, rowvar=False) + 1e-6 * np.eye(b.shape[1])
    vals, vecs = np.linalg.eig(c1 @ c2)
    s = np.real(vecs @ np.diag(np.sqrt(np.maximum(np.real(vals), 0))) @ np.linalg.inv(vecs))
    return float(((m1 - m2) ** 2).sum() + np.trace(c1 + c2 - 2 * s))


real_f = feats(Xte)
WS = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0]
rows, gen_cache = [], {}
for w in WS:
    t0 = time.time()
    batch = torch.cat([sample(64, k, w) for k in range(4)])
    labels = torch.arange(4, device=dev).repeat_interleave(64)
    sec = time.time() - t0
    f = feats(batch)
    with torch.no_grad():
        acc = float((clf(batch.to(dev)).argmax(1) == labels).float().mean()) * 100
    div = float(torch.cdist(f[64:128], f[64:128]).mean())        # 同一类（划痕）里两两的平均距离
    fid = frechet(f, real_f)
    rows.append((w, fid, acc, div, sec))
    gen_cache[w] = (batch.cpu(), f.cpu())
    print(f"  w = {w:>3}：弗雷歇距离 {fid:7.2f}，类别一致率 {acc:5.1f}%，同类两两距离 {div:6.3f}，{sec:.0f} s")

best = min(rows, key=lambda r: r[1])
print(f"\n弗雷歇距离最小的是 w = {best[0]}（{best[1]:.2f}）；"
      f"类别一致率最高的是 w = {max(rows, key=lambda r: r[2])[0]}")

# %% [markdown]
# ## 4. 会不会把训练图背出来；采样要多久（任务 4）
# 引导调得很大时，分布被挤到一个很窄的地方——会不会窄到干脆复制训练图？
# 量一下生成图与训练集最近邻的距离，和"真图之间的典型距离"对照就知道了。
# %%
train_f = feats(Xtr[:4000])
real_nn = float(torch.cdist(real_f[:256], train_f).min(1).values.mean())
nn_rows = []
for w in (0.0, 4.0, 8.0):
    g_f = gen_cache[w][1].to(dev)
    d = float(torch.cdist(g_f, train_f).min(1).values.mean())
    nn_rows.append((w, d))
    print(f"  w = {w}：离训练集最近的平均距离 {d:.3f}（真图之间是 {real_nn:.3f}）")
if nn_rows[-1][1] < 0.3 * real_nn:
    print("  注意：引导到 8 时已经非常接近训练图了，要当心记忆")
else:
    print("  还没有记忆训练图的迹象")
sec_per_batch = rows[0][4]
print(f"\n采一批 256 张要 {sec_per_batch:.0f} s（100 步采样）；"
      f"走满 {T} 步大约要 {sec_per_batch * T / 100:.0f} s")

# %% [markdown]
# ## 回传结果
# %%
w_best_fid = best[0]
fid_w0, fid_best, fid_w8 = rows[0][1], best[1], rows[-1][1]
acc_w0, acc_w8 = rows[0][2], rows[-1][2]
div_w0, div_w8 = rows[0][3], rows[-1][3]
nn_w8 = nn_rows[-1][1]
wqgpu.submit(w_best_fid=w_best_fid, fid_w0=fid_w0, fid_best=fid_best, fid_w8=fid_w8,
             acc_w0=acc_w0, acc_w8=acc_w8, div_w0=div_w0, div_w8=div_w8,
             nn_w8=nn_w8, sec_per_batch=sec_per_batch)
