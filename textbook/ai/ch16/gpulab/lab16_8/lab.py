# GPU 实验 16.8 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 16.8　用生成的图扩充训练集，在真图上评
# 16.8 节的案例里，"合成器"只是画真图那个程序改了几个设置——那是为了把"分布偏了多少"
# 一样一样拆开看。这里换成真的：**只拿那几十张真图**训一个条件扩散模型，用它生成几百张，
# 补进训练集，再到真图上评。
#
# 要量四件事：补对了能补回多少、引导调过头会掉多少、第二代生成器（拿合成图训的）会不会更窄、
# 以及这些成绩离"全用真图"的参照线还差多远。
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
T0 = time.time()
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 真图：少量训练集与测试集（任务 1）
# 车间口径：七成的件合格，缺陷大多轻微。手上只有 N_REAL 张标注过的真图；
# 测试集 3000 张，与训练集严格分开。
# %%
N, KINDS = 32, ("无缺陷", "划痕", "压痕", "锈斑")
N_REAL, N_FULL, N_TEST, N_SYN = 64, 1024, 3000, 768
SEV = (0.25, 0.8)
PK = np.array([0.7, 0.1, 0.1, 0.1])


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


def real_set(n, seed):
    g = np.random.default_rng(seed)
    X = np.empty((n, 1, N, N), np.float32)
    y = np.empty(n, np.int64)
    for i in range(n):
        k = int(g.choice(4, p=PK))
        X[i, 0] = draw(k, float(g.uniform(*SEV)), g)
        y[i] = k
    return torch.tensor(X), torch.tensor(y)


Xr, yr = real_set(N_REAL, 11)             # 手上只有这几十张
Xf, yf = real_set(N_FULL, 22)             # 参照：如果真能标这么多
Xt, yt = real_set(N_TEST, 99)
print(f"少量真图 {N_REAL} 张，其中有缺陷的 {int((yr > 0).sum())} 张")
print(f"各类张数：{[int((yr == k).sum()) for k in range(4)]}（最少的那一类只有几张，这就是难处）")

# %% [markdown]
# ## 2. 条件扩散模型：只拿那几十张真图训（任务 2）
# 结构与 GPU 实验 16.4 的一样。训练数据只有 N_REAL 张，所以要多跑几轮、加上翻转增广。
# 然后用两档引导各生成一批：w = 1（合适）与 w = 8（调过头）。
# %%
T = 400
beta = torch.linspace(1e-4, 0.02, T, device=dev)
abar = torch.cumprod(1 - beta, 0)
NULL = 4


def temb(t, dim=64):
    half = dim // 2
    f = torch.exp(-math.log(10000) * torch.arange(half, device=t.device) / half)
    a = t.float()[:, None] * f[None]
    return torch.cat([a.sin(), a.cos()], 1)


class Block(nn.Module):
    def __init__(self, cin, cout, emb=128):
        super().__init__()
        self.c1, self.c2 = nn.Conv2d(cin, cout, 3, padding=1), nn.Conv2d(cout, cout, 3, padding=1)
        self.e = nn.Linear(emb, cout)
        self.n1, self.n2 = nn.GroupNorm(8, cout), nn.GroupNorm(8, cout)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()

    def forward(self, x, e):
        h = F.silu(self.n1(self.c1(x))) + self.e(e)[:, :, None, None]
        return F.silu(self.n2(self.c2(h))) + self.skip(x)


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
        h1 = self.d1(self.inp(x), e)
        h2 = self.d2(F.avg_pool2d(h1, 2), e)
        u2 = F.interpolate(self.u2(torch.cat([self.mid(h2, e), h2], 1), e), scale_factor=2, mode="nearest")
        return self.out(self.u1(torch.cat([u2, h1], 1), e))


def train_diffusion(X, y, epochs=400, bs=64, lr=2e-4, p_drop=0.1):
    net = UNet().to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    X = (X * 2 - 1).to(dev)
    y = y.to(dev)
    t0 = time.time()
    for ep in range(epochs):
        perm = torch.randperm(len(X), device=dev)
        for i in range(0, len(X), bs):
            idx = perm[i:i + bs]
            x0, c = X[idx], y[idx].clone()
            if torch.rand(1).item() < 0.5:                 # 左右翻转增广
                x0 = torch.flip(x0, [3])
            c[torch.rand(len(c), device=dev) < p_drop] = NULL
            t = torch.randint(0, T, (len(x0),), device=dev)
            eps = torch.randn_like(x0)
            a = abar[t][:, None, None, None]
            loss = F.mse_loss(net(a.sqrt() * x0 + (1 - a).sqrt() * eps, t, c), eps)
            opt.zero_grad(); loss.backward(); opt.step()
    print(f"  训完，用时 {time.time() - t0:.0f} s")
    return net


@torch.no_grad()
def sample(net, n, cls, w, steps=100):
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
        if i + 1 == len(ts):
            x = x0
            break
        ap = abar[ts[i + 1]]
        sig = ((1 - ap) / (1 - a) * (1 - a / ap)).clamp(min=0).sqrt()
        x = ap.sqrt() * x0 + (1 - ap - sig ** 2).clamp(min=0).sqrt() * e + sig * torch.randn_like(x)
    return ((x + 1) / 2).cpu()


def synth(net, n, w):
    """按真实的类别比例生成一批带标签的合成图。"""
    g = np.random.default_rng(5)
    cnt = np.bincount(g.choice(4, size=n, p=PK), minlength=4)
    Xs, ys = [], []
    for k in range(4):
        if cnt[k] == 0:
            continue
        Xs.append(sample(net, int(cnt[k]), k, w))
        ys.append(torch.full((int(cnt[k]),), k, dtype=torch.long))
    return torch.cat(Xs), torch.cat(ys)


print("训第一代生成器（只用那几十张真图）……")
gen1 = train_diffusion(Xr, yr)
t0 = time.time()
Xs1, ys1 = synth(gen1, N_SYN, 1.0)
Xs8, ys8 = synth(gen1, N_SYN, 8.0)
print(f"两批合成图各 {N_SYN} 张，采样用时 {time.time() - t0:.0f} s")

# %% [markdown]
# ## 3. 四种训练集，都在真图上评（任务 3）
# 检测器是一个小卷积网络（第 5 章那一类）。成绩看两个数：曲线下面积，以及
# 把误报压到 5% 时能查出多少缺陷——后者才是车间定门限时看的。
# %%
class Det(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.f = nn.Sequential(nn.Conv2d(1, ch, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                               nn.Conv2d(ch, 2 * ch, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                               nn.Conv2d(2 * ch, 2 * ch, 3, padding=1), nn.ReLU(),
                               nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(2 * ch, 1))

    def forward(self, x):
        return self.f(x)[:, 0]


def auc(score, y):
    order = np.argsort(-score)
    y = y[order]
    P, Nn = int(y.sum()), int((1 - y).sum())
    tp = np.cumsum(y)
    fp = np.cumsum(1 - y)
    return float(np.sum(tp * (1 - y)) / (P * Nn)), fp / Nn, tp / P


def recall_at(fpr, tpr, f=0.05):
    ok = tpr[fpr <= f]
    return float(ok.max()) if len(ok) else 0.0


def train_det(X, y, epochs=40, bs=64, seeds=3):
    """几个种子取平均：少样本时单次结果很不稳。"""
    aucs, recs = [], []
    Xt_d, yt_np = Xt.to(dev), (yt > 0).numpy().astype(int)
    for sd in range(seeds):
        torch.manual_seed(sd)
        det = Det().to(dev)
        opt = torch.optim.Adam(det.parameters(), lr=1e-3)
        Xd, yd = X.to(dev), (y > 0).float().to(dev)
        for _ in range(epochs):
            perm = torch.randperm(len(Xd), device=dev)
            for i in range(0, len(Xd), bs):
                idx = perm[i:i + bs]
                loss = F.binary_cross_entropy_with_logits(det(Xd[idx]), yd[idx])
                opt.zero_grad(); loss.backward(); opt.step()
        det.eval()
        with torch.no_grad():
            s = det(Xt_d).cpu().numpy()
        a, fpr, tpr = auc(s, yt_np)
        aucs.append(a)
        recs.append(recall_at(fpr, tpr))
    return float(np.mean(aucs)), float(np.mean(recs)), float(np.std(aucs))


sets = [("少量真图", Xr, yr),
        ("少量真图 + 合成（引导 1）", torch.cat([Xr, Xs1]), torch.cat([yr, ys1])),
        ("少量真图 + 合成（引导 8）", torch.cat([Xr, Xs8]), torch.cat([yr, ys8])),
        ("全用真图（参照）", Xf, yf)]
res = {}
for name, X, y in sets:
    a, r, sd = train_det(X, y)
    res[name] = (a, r, sd, len(X))
    print(f"{name:<26} {len(X):>5} 张  曲线下面积 {a:.3f} (±{sd:.3f})  误报 5% 处查出 {r * 100:5.1f}%")

a_real, a_syn = res["少量真图"][0], res["少量真图 + 合成（引导 1）"][0]
a_full, a_hi = res["全用真图（参照）"][0], res["少量真图 + 合成（引导 8）"][0]
recovered = (a_syn - a_real) / max(a_full - a_real, 1e-9) * 100
print(f"\n合成图把“再标 {N_FULL - N_REAL} 张真图”的收益补回了 {recovered:.0f}%；"
      f"引导调到 8 的那一批只补回 {(a_hi - a_real) / max(a_full - a_real, 1e-9) * 100:.0f}%")

# %% [markdown]
# ## 4. 第二代：拿合成图再训一个生成器（任务 4）
# 每一代只学到上一代的一部分花样。训第二代，看它生成的图多样性少了多少、
# 用它补出来的训练集又差多少。
# %%
print("训第二代生成器（训练数据是第一代的合成图）……")
gen2 = train_diffusion(Xs1, ys1, epochs=120)      # 数据多了，轮数相应减少
Xs2, ys2 = synth(gen2, N_SYN, 1.0)


def diversity(X):
    """多样性的一个简单代理：两两像素距离的平均值。"""
    v = X[:256].reshape(min(len(X), 256), -1)
    return float(torch.cdist(v, v).mean())


div_real, div1, div2 = diversity(Xr), diversity(Xs1), diversity(Xs2)
a2, r2, _ = train_det(torch.cat([Xr, Xs2]), torch.cat([yr, ys2]))
print(f"多样性：真图 {div_real:.2f}，第一代 {div1:.2f}，第二代 {div2:.2f}"
      f"（第二代比第一代少了 {(1 - div2 / div1) * 100:.0f}%）")
print(f"用第二代的图补出来：曲线下面积 {a2:.3f}（第一代是 {a_syn:.3f}）")
if div2 < div1:
    print("一代一代往下传，分布确实在收窄——这就是只拿模型自己的输出继续训的代价")

# %% [markdown]
# ## 回传结果
# %%
sec_total = time.time() - T0
wqgpu.submit(auc_real=a_real, auc_syn=a_syn, auc_syn_hi=a_hi, auc_full=a_full,
             rec_real=res["少量真图"][1] * 100, rec_syn=res["少量真图 + 合成（引导 1）"][1] * 100,
             recovered=recovered, auc_gen2=a2, n_real=N_REAL, sec_total=sec_total)
