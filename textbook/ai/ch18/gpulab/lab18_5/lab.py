# GPU 实验 18.5 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 18.5　随机划分与骨架划分：同一个模型，两个成绩
# 18.5 节在玩具数据上算过这件事，这里在真分子上做一遍。
#
# 要比的是**同一批分子、同一个模型**，只换数据划分：
# - **随机划分**：样本随机分进训练／测试；
# - **骨架划分**：按分子的二维结构骨架（Murcko 骨架）分，结构不同的分子进不同子集。
#
# 另外放一个故意"只会找类似物"的最近邻基线当对照。看两种划分把两个模型的名次排成什么样。
#
# **口径先说清楚**：本实验的绝对分数不与任何论文比（数据集版本、特征、模型、训练轮数都不同）。
# 能比的是**同一次实验里两种划分之间的差**，以及两个模型的名次。
# %%
import sys; sys.path.insert(0, "..")
import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q rdkit torch-geometric", timeout=2400)
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 取数据（任务 1）
# 用 BBBP（血脑屏障通透性，二分类）。数据从公开来源现取，**仓库里不放分子数据**。
# MoleculeNet Table 1 给的分子数是 2039（正文另有一组数，见 18.5 节的口径说明）。
# %%
import urllib.request
import io
import csv

URL = ("https://deepchemdata.s3.us-west-1.amazonaws.com/datasets/BBBP.csv")
raw = urllib.request.urlopen(URL, timeout=120).read().decode("utf-8", "ignore")
rows = list(csv.DictReader(io.StringIO(raw)))
print("原始行数", len(rows))

from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold
RDLogger.DisableLog("rdApp.*")

mols, ys = [], []
for r in rows:
    m = Chem.MolFromSmiles(r["smiles"])
    if m is None:
        continue
    mols.append(m); ys.append(int(r["p_np"]))
y = np.array(ys)
print(f"能解析的分子 {len(mols)} 个，阳性比例 {y.mean() * 100:.1f}%")

# %% [markdown]
# ## 2. Murcko 骨架（任务 2）
# 骨架划分的原文做法：按 Murcko 骨架分箱，大于目标测试集一半的箱全部进训练集，
# 其余的箱**随机**分进训练／测试。注意最后这一句——**骨架划分不是唯一确定的划分**。
# %%
import collections

scaf = [MurckoScaffold.MurckoScaffoldSmiles(mol=m, includeChirality=False) for m in mols]
cnt = collections.Counter(scaf)
print(f"不同骨架 {len(cnt)} 个")
print(f"最大的骨架有 {cnt.most_common(1)[0][1]} 个分子")
only_one = sum(1 for v in cnt.values() if v == 1)
print(f"只有一个分子的骨架 {only_one} 个（占 {only_one / len(cnt) * 100:.1f}%）")
print("最大的五个骨架各有多少分子：", [v for _, v in cnt.most_common(5)])

# %% [markdown]
# ## 3. 两个模型（任务 3）
# - **图神经网络**：三层消息传递 + 全局平均池化，原子特征只用最朴素的几维；
# - **最近邻基线**：Morgan 指纹上的 5 近邻投票——它**只会找类似物**，不会别的。
# %%
from rdkit.Chem import rdFingerprintGenerator
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GCNConv, global_mean_pool

gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
FP = np.array([gen.GetFingerprintAsNumPy(m) for m in mols], dtype=np.float32)


def to_graph(m, label):
    x = torch.tensor([[a.GetAtomicNum(), a.GetDegree(), a.GetFormalCharge(),
                       int(a.GetIsAromatic()), a.GetTotalNumHs()] for a in m.GetAtoms()],
                     dtype=torch.float)
    ei = [[], []]
    for b in m.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
        ei[0] += [i, j]; ei[1] += [j, i]
    if not ei[0]:
        ei = [[0], [0]]
    return Data(x=x, edge_index=torch.tensor(ei, dtype=torch.long),
                y=torch.tensor([float(label)]))


GRAPHS = [to_graph(m, t) for m, t in zip(mols, y)]


class GNN(torch.nn.Module):
    def __init__(self, hid=64):
        super().__init__()
        self.c1, self.c2, self.c3 = GCNConv(5, hid), GCNConv(hid, hid), GCNConv(hid, hid)
        self.out = torch.nn.Linear(hid, 1)

    def forward(self, d):
        h = torch.relu(self.c1(d.x, d.edge_index))
        h = torch.relu(self.c2(h, d.edge_index))
        h = torch.relu(self.c3(h, d.edge_index))
        return self.out(global_mean_pool(h, d.batch)).squeeze(-1)


def auc(labels, scores):
    order = np.argsort(scores)
    ranks = np.empty(len(scores), float); ranks[order] = np.arange(1, len(scores) + 1)
    pos, neg = labels.sum(), (1 - labels).sum()
    return float((ranks[labels == 1].sum() - pos * (pos + 1) / 2) / (pos * neg))


def train_gnn(tr, te, epochs=40, seed=0):
    torch.manual_seed(seed)
    net = GNN().cuda()
    opt = torch.optim.Adam(net.parameters(), lr=3e-3)
    loader = DataLoader([GRAPHS[i] for i in tr], batch_size=64, shuffle=True)
    lossf = torch.nn.BCEWithLogitsLoss()
    net.train()
    for _ in range(epochs):
        for batch in loader:
            batch = batch.cuda()
            opt.zero_grad()
            lossf(net(batch), batch.y).backward()
            opt.step()
    net.eval()
    sc = []
    with torch.no_grad():
        for batch in DataLoader([GRAPHS[i] for i in te], batch_size=256):
            sc.append(net(batch.cuda()).cpu().numpy())
    return auc(y[te], np.concatenate(sc))


def knn_baseline(tr, te, k=5):
    """只会找类似物：在 Morgan 指纹上找最近的 k 个训练分子，看它们的标签。"""
    a, b = FP[te], FP[tr]
    inter = a @ b.T
    sim = inter / (a.sum(1)[:, None] + b.sum(1)[None, :] - inter + 1e-9)   # Tanimoto
    nn = np.argsort(-sim, axis=1)[:, :k]
    return auc(y[te], y[tr][nn].mean(1))


def split_random(n, seed, test_frac=0.2):
    g = np.random.default_rng(seed)
    idx = g.permutation(n); cut = int(n * test_frac)
    return idx[cut:], idx[:cut]


def split_scaffold(scaf, seed, test_frac=0.2):
    """原文做法：大箱全进训练集，其余箱随机分——所以同一数据集有多个骨架划分。"""
    g = np.random.default_rng(seed)
    groups = collections.defaultdict(list)
    for i, s in enumerate(scaf):
        groups[s].append(i)
    need = int(len(scaf) * test_frac)
    big = [v for v in groups.values() if len(v) > need / 2]
    rest = [v for v in groups.values() if len(v) <= need / 2]
    g.shuffle(rest)
    test = []
    for v in rest:
        if len(test) >= need:
            break
        test.extend(v)
    test_set = set(test)
    train = [i for i in range(len(scaf)) if i not in test_set]
    return np.array(train), np.array(sorted(test_set))


tr, te = split_random(len(mols), seed=0)
gnn_rand = train_gnn(tr, te, seed=0)
knn_rand = knn_baseline(tr, te)
print(f"随机划分：图神经网络 {gnn_rand:.3f}　最近邻基线 {knn_rand:.3f}")

# %% [markdown]
# ## 4. 换成骨架划分（任务 4）
# 同一批分子、同一个模型、同样的训练轮数，只换划分。
# %%
tr, te = split_scaffold(scaf, seed=0)
gnn_scaf = train_gnn(tr, te, seed=0)
knn_scaf = knn_baseline(tr, te)
print(f"骨架划分：图神经网络 {gnn_scaf:.3f}　最近邻基线 {knn_scaf:.3f}")
print(f"\n掉了几个点：图神经网络 {(gnn_rand - gnn_scaf) * 100:5.1f}　"
      f"最近邻基线 {(knn_rand - knn_scaf) * 100:5.1f}")
flipped = (knn_rand > gnn_rand) != (knn_scaf > gnn_scaf)
print(f"两种划分把名次排反了吗：{'是' if flipped else '否'}")
if flipped:
    print("→ 随机划分选出来的那个'更好的模型'，在骨架划分上更差。"
          "这与第 17.1 节'换一套测试排名会翻'是同一件事")

# %% [markdown]
# ## 5. 骨架划分不是唯一的（任务 5）
# 剩下的骨架箱是随机分配的，所以同一个数据集可以有多个骨架划分。只跑一组就下结论，
# 和只跑一个随机种子一样不可靠。
# %%
gs, ks = [], []
for sd in range(5):
    tr, te = split_scaffold(scaf, seed=sd)
    gs.append(train_gnn(tr, te, seed=sd)); ks.append(knn_baseline(tr, te))
    print(f"第 {sd + 1} 组：图神经网络 {gs[-1]:.3f}　最近邻基线 {ks[-1]:.3f}")
print(f"\n图神经网络 {np.mean(gs):.3f} ± {np.std(gs):.3f}　"
      f"最近邻基线 {np.mean(ks):.3f} ± {np.std(ks):.3f}")
print("对照：随机划分上这两个数的抖动要小得多——骨架划分多出来的那部分抖动，"
      "来自'哪几个骨架被分进测试集'")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_molecules=len(mols), n_scaffolds=len(cnt),
             auc_gnn_random=gnn_rand, auc_gnn_scaffold=gnn_scaf,
             auc_knn_random=knn_rand, auc_knn_scaffold=knn_scaf,
             gnn_drop_pts=(gnn_rand - gnn_scaf) * 100,
             knn_drop_pts=(knn_rand - knn_scaf) * 100,
             scaffold_sd=float(np.std(gs)), rank_flipped="是" if flipped else "否")
