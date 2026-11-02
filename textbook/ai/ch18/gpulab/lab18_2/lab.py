# GPU 实验 18.2 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 18.2　预测一个蛋白质，并读懂它的可信度
# 18.1 节讲了四个指标各测什么，18.2 节讲了接触信息值多少，18.7 节讲了自评分数该怎么读。
# 这个实验把三件事放到真模型上做一遍：
#
# 1. 用 ESMFold（公开权重、单序列、不用搜数据库）预测几条小蛋白；
# 2. 与实验结构逐条比 GDT_TS、lDDT、TM-score——看三个指标会不会给出不同的结论；
# 3. 把自评分数与真实误差按残基画在一起，亲眼看"分数高到底意味着什么"。
#
# **口径先说清楚**：本实验的数**不能**与论文里的 CAMEO / CASP 分数比（蛋白不同、数量少得多、
# 叠合与指标的实现也不完全一样）。能比的是三个指标之间的关系，以及自评分数与真实误差的关系。
# %%
import sys; sys.path.insert(0, "..")
import time

import numpy as np
import torch
import wqgpu
env = wqgpu.check(("gpu", "torch"))
wqgpu.sh(f"{sys.executable} -m pip install -q transformers accelerate biotite", timeout=2400)
print(torch.cuda.get_device_name(0), torch.__version__)

# %% [markdown]
# ## 1. 模型（任务 1）
# 官方模型卡：`facebook/esmfold_v1`，MIT 许可，"It does not require any lookup or MSA step"。
# 第一次下载权重要几分钟。
# %%
from transformers import AutoTokenizer, EsmForProteinFolding

MODEL = "facebook/esmfold_v1"
tok = AutoTokenizer.from_pretrained(MODEL)
model = EsmForProteinFolding.from_pretrained(MODEL, low_cpu_mem_usage=True).cuda().eval()
model.trunk.set_chunk_size(64)          # 省显存：注意力分块
print("参数量 %.0f M" % (sum(p.numel() for p in model.parameters()) / 1e6))

# %% [markdown]
# ## 2. 取几条小蛋白（任务 2）
# 序列与实验结构都从公开数据库现取，**仓库里不放任何结构文件**。
# 挑的是 80—250 残基的单链球状蛋白：太长的显存不够，多聚体用单链预测对不上实验结构。
#
# 想换自己的蛋白，把下面的 PDB 编号改掉就行（要挑单链的）。
# %%
import urllib.request

PDB_IDS = ["1UBQ", "1CRN", "5PTI", "1LYZ"]      # 换成你自己的（单链、80—250 残基最省事）
AA3 = {"ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q", "GLU": "E",
       "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F",
       "PRO": "P", "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V"}


def fetch(pdb_id):
    """从 RCSB 取一个结构，返回 (序列, Cα 坐标)。只取第一条链、只取有坐标的标准残基。"""
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    text = urllib.request.urlopen(url, timeout=60).read().decode()
    chain, seq, xyz = None, [], []
    for line in text.splitlines():
        if line.startswith("ENDMDL"):
            break
        if not line.startswith("ATOM") or line[12:16].strip() != "CA":
            continue
        if line[16] not in (" ", "A"):                  # 只要主构象
            continue
        res = line[17:20].strip()
        if res not in AA3:
            continue
        if chain is None:
            chain = line[21]
        if line[21] != chain:
            continue
        seq.append(AA3[res])
        xyz.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    return "".join(seq), np.array(xyz)


data = {}
for pid in PDB_IDS:
    s, c = fetch(pid)
    data[pid] = (s, c)
    print(f"{pid}: {len(s)} 残基")
print("长度中位数", int(np.median([len(s) for s, _ in data.values()])))

# %% [markdown]
# ## 3. 预测并比对（任务 3）
# 三个指标按 18.1 节的定义实现：
# - **GDT_TS**：四个距离截断（1/2/4/8 Å）下落在截断内的残基百分比的平均，要先叠合；
# - **lDDT**：参考结构里 15 Å 之内的距离对，在模型里被"保持"的比例（四个容差取平均），**不叠合**；
# - **TM-score**：d₀ 随长度归一，所以随机结构对恒在 0.17 附近。
#
# CASP 用 LGA 做序列无关叠合，这里用一次整体最优叠合近似，所以**本实验的 GDT_TS 不与 CASP 的数直接比**。
# %%
def kabsch(p, q):
    pc, qc = p - p.mean(0), q - q.mean(0)
    u, _, vt = np.linalg.svd(pc.T @ qc)
    d = np.sign(np.linalg.det(vt.T @ u.T))
    r = vt.T @ np.diag([1.0, 1.0, d]) @ u.T
    return pc @ r.T + q.mean(0)


def per_residue_error(model_xyz, ref):
    return np.sqrt(((kabsch(model_xyz, ref) - ref) ** 2).sum(1))


def gdt_ts(model_xyz, ref):
    d = per_residue_error(model_xyz, ref)
    return float(np.mean([100.0 * (d <= c).mean() for c in (1.0, 2.0, 4.0, 8.0)]))


def tm_score(model_xyz, ref):
    n = len(ref)
    d0 = 1.24 * (n - 15) ** (1 / 3) - 1.8 if n > 15 else 0.5
    d = per_residue_error(model_xyz, ref)
    return float(np.mean(1.0 / (1.0 + (d / d0) ** 2)))


def lddt(model_xyz, ref, radius=15.0):
    dr = np.linalg.norm(ref[:, None] - ref[None, :], axis=-1)
    dm = np.linalg.norm(model_xyz[:, None] - model_xyz[None, :], axis=-1)
    i, j = np.triu_indices(len(ref), k=2)
    sel = dr[i, j] < radius
    diff = np.abs(dm[i, j][sel] - dr[i, j][sel])
    return float(np.mean([(diff < t).mean() for t in (0.5, 1.0, 2.0, 4.0)]))


rows, all_score, all_err = [], [], []
for pid, (seq, ref) in data.items():
    t0 = time.perf_counter()
    with torch.no_grad():
        out = model.infer([seq])
    torch.cuda.synchronize()
    dt = time.perf_counter() - t0
    pos = out["positions"][-1, 0]                    # 最后一轮、第一条序列
    ca = pos[:, 1].cpu().numpy().astype(float)       # 原子顺序 N, CA, C, ...
    plddt = out["plddt"][0, :, 1].cpu().numpy().astype(float)
    n = min(len(ca), len(ref))
    ca, ref_n, plddt = ca[:n], ref[:n], plddt[:n]
    err = per_residue_error(ca, ref_n)
    rows.append((pid, n, dt, tm_score(ca, ref_n), lddt(ca, ref_n), gdt_ts(ca, ref_n),
                 float(np.median(plddt))))
    all_score.append(plddt); all_err.append(err)
    print(f"{pid}: {n} 残基　{dt:5.1f} s　TM {rows[-1][3]:.3f}　lDDT {rows[-1][4]:.3f}　"
          f"GDT_TS {rows[-1][5]:5.1f}　自评中位 {rows[-1][6]:.0f}")

score = np.concatenate(all_score); err = np.concatenate(all_err)
tm_med = float(np.median([r[3] for r in rows]))
lddt_med = float(np.median([r[4] for r in rows]))
gdt_med = float(np.median([r[5] for r in rows]))
print(f"\n中位数：TM {tm_med:.3f}　lDDT {lddt_med:.3f}　GDT_TS {gdt_med:.1f}")
print(f"对照论文（口径不同，不可直接比）：CAMEO 194 个结构 TM 0.83，CASP14 51 个 0.68")

# %% [markdown]
# ## 4. 自评分数到底意味着什么（任务 4）
# 论文给的拟合是 lDDT-Cα = 0.997·pLDDT − 1.17，**相关系数 0.76**。
# 0.76 听着很高，可它允许"分数很高、误差却很大"的那一撮存在。下面把这一撮量出来。
# %%
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

corr = float(np.corrcoef(score, -np.log(np.maximum(err, 1e-3)))[0, 1])
print(f"自评分数与 −log(真实误差) 的相关系数：{corr:.3f}（论文那条拟合给的是 0.76）")

BAD = 2.0
print(f"\n{'档位':>8}  {'残基数':>6}  {'误差中位':>8}  {'错超过 2 Å 占':>12}")
bands = []
for lo, hi, name in ((90, 101, "90 以上"), (70, 90, "70—90"), (50, 70, "50—70"), (0, 50, "50 以下")):
    sel = (score >= lo) & (score < hi)
    if sel.sum() == 0:
        bands.append((name, 0, float("nan"), float("nan"))); continue
    med, bad = float(np.median(err[sel])), float((err[sel] > BAD).mean() * 100)
    bands.append((name, int(sel.sum()), med, bad))
    print(f"{name:>8}  {int(sel.sum()):6d}  {med:8.2f}  {bad:11.1f}%")
top_bad = bands[0][3]
print(f"\n**自评 90 分以上却错超过 {BAD:.0f} Å 的残基占 {top_bad:.1f}%** —— 这就是 r = 0.76 的含义")

fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4))
a.scatter(score, err, s=4, alpha=0.3)
a.axhline(BAD, color="r", ls="--")
a.axvline(90, color="k", ls=":")
a.set_yscale("log"); a.set_xlabel("自评分数 pLDDT"); a.set_ylabel("真实误差 (Å)")
a.set_title(f"逐残基：r = {corr:.2f}")
b.bar(range(4), [x[2] for x in bands])
b.set_xticks(range(4)); b.set_xticklabels([x[0] for x in bands])
b.set_ylabel("误差中位数 (Å)"); b.set_title("四档各是什么样")
fig.tight_layout(); fig.savefig("plddt.png", dpi=120)
print("图已存成 plddt.png")

# %% [markdown]
# ## 5. 最差的那一条，差在哪（任务 5）
# 两种"差"要分开：
# - **整体折叠就错了**：TM 低、lDDT 也低；
# - **只是域摆了**：lDDT 高、TM 低——这时结构本身是对的，只是两段的相对取向不对。
# %%
worst = min(rows, key=lambda r: r[3])
print(f"最差的是 {worst[0]}：TM {worst[3]:.3f}，lDDT {worst[4]:.3f}，GDT_TS {worst[5]:.1f}")
if worst[4] > 0.7 and worst[3] < 0.6:
    print("→ lDDT 高而 TM 低：像是**域摆了**，局部结构其实是对的")
elif worst[4] < 0.5:
    print("→ 两个都低：整体折叠就没对，这个预测不能用")
else:
    print("→ 介于两者之间，把每个域单独算一次 lDDT 再判断")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_proteins=len(rows), median_len=int(np.median([r[1] for r in rows])),
             sec_per_protein=float(np.mean([r[2] for r in rows])),
             tm_median=tm_med, lddt_median=lddt_med, gdt_median=gdt_med,
             plddt_median=float(np.median(score)), corr_plddt_err=corr,
             top_band_bad_pct=top_bad, worst_name=worst[0])
