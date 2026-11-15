"""第 167b 轮：软件公司案例 B——云平台对象存储：三副本还是纠删码。
64 台存储节点（4 个整机柜、每台 12 块 16 TB 盘）：比较三副本、RS(6,3)、RS(10,4)；手算可用容量、修复流量与修复时间、数据持久性（马尔可夫链）；
蒙特卡洛模拟坏盘与修复（固定修复时间，加速故障率下对照马尔可夫链）；读延迟 p99 仿真（纠删码要等最慢的一块，降级读更慢）；
选“热数据三副本 + 温冷数据 RS(6,3)”；软件公司做 10 次云平台版本构建、开通 24 份云订阅验收。

    python3 tools/cases/software_b.py

盘的年故障率、延迟分布、带宽、容量需求都是示例值（量级按常见的机械盘对象存储）。输出到 factory/cases/software/B/。
"""
from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ["WQ_PLANT_FILE"] = str(ROOT / "factory" / "plants" / "wenquest-software.yaml")
sys.path[:0] = [str(HERE), str(ROOT / "factory" / "digital"), str(ROOT / "factory")]

import numpy as np  # noqa: E402

import caselib as L  # noqa: E402
from caselib import plt  # noqa: E402

TOOLS = {
    "softops": ("发布与服务", "Releases & services", "/software-ops"),
    "engineer": ("设计与工艺", "Design & process", "/work/engineer"),
    "planner": ("订单与计划", "Orders & planning", "/work/planner"),
    "quality": ("质量", "Quality", "/work/quality"),
}
tools = lambda *k: [TOOLS[x] for x in k]  # noqa: E731

case = L.Case("software", "B", "中等", "云平台对象存储：三副本还是纠删码", "Cloud object storage: replicas or erasure coding", "REL-CLOUD 存储层",
              "64 台存储节点、768 块 16 TB 盘：比较三副本、RS(6,3)、RS(10,4) 的可用容量、修复时间、数据持久性和读延迟；马尔可夫链算几个 9，"
              "蒙特卡洛（固定修复时间）对照；读延迟仿真看出纠删码小文件尾延迟高、大文件反而快；选热数据三副本 + 温冷数据 RS(6,3)；"
              "云平台版本构建 10 次、云订阅开通 24 份验收。",
              "64 storage nodes with 768 × 16 TB disks: 3-way replication, RS(6,3) and RS(10,4) compared on usable capacity, repair time, durability and read latency; "
              "Markov-chain durability cross-checked by Monte Carlo with fixed repair times; latency simulation shows erasure coding has a worse tail for small objects "
              "but is faster for large ones; hot data on replicas, warm and cold data on RS(6,3); 10 platform builds and 24 cloud subscriptions accepted.",
              "tools/cases/software_b.py")

# ---------------------------------------------------------------- 任务（示例值）
N_RACK, NODE_PER = 4, 16
N_NODE = N_RACK * NODE_PER
DISK_PER, DISK_TB = 12, 16.0
N_DISK = N_NODE * DISK_PER
RAW_TB = N_DISK * DISK_TB
FILL = 0.80                 # 最多装到 80 %（留修复空间）
NEED_TB = 4000.0            # 三年后要存的数据（可用容量）
HOT = 0.15                  # 热数据比例（最近 30 天常读的小文件）
AFR = 0.012                 # 盘的年故障率
LAM = AFR / 8760            # 每小时
REPAIR_BW = 2.0             # 修复限速：全集群 GB/s（给用户读写留带宽）
DETECT = 0.5                # 发现坏盘、标记下线的时间 h
DUR_REQ = 11                # 持久性要求：一年丢一个对象的概率 ≤ 1e-11（“11 个 9”）
P99_SMALL = 30.0            # 小文件（64 KB）读 p99 要求 ms
P99_LARGE = 250.0           # 大文件（16 MB）读 p99 要求 ms
GROUPS = 4096               # 放置组数
SCHEMES = [("三副本", "3-way replication", 3, 1), ("RS(6,3)", "RS(6,3)", 6, 3), ("RS(10,4)", "RS(10,4)", 10, 4)]   # (名, 英文, k, m)；副本记作 k = 1 份数据 + m = 2 份副本 → n = 3


def nfm(k, m, name):
    if name == "三副本":
        return 3, 2, 3.0            # n 盘、能坏 f 块、存储倍数
    return k + m, m, (k + m) / k


brief = f"""# 设计任务书：云平台对象存储的冗余方案

**用在哪**　软件公司的云平台（REL-CLOUD、订阅 SUB-CLOUD）建在计算机厂案例 C 的 20 柜机房里，其中 **{N_RACK} 柜是存储柜**：
{N_NODE} 台存储节点，每台 {DISK_PER} 块 {DISK_TB:g} TB 机械盘，共 {N_DISK} 块、裸容量 {RAW_TB / 1000:.2f} PB。

| 项目 | 要求 | 出处 |
|---|---|---|
| 三年后可用容量 | ≥ {NEED_TB / 1000:g} PB（盘最多装到 {FILL * 100:.0f} %） | 订阅增长预测（案例 C） |
| 数据持久性 | 一个对象一年丢失的概率 ≤ 10⁻¹¹（“11 个 9”） | 对象存储常见承诺 |
| 整柜断电 / 断网 | 数据不丢、仍可读 | 机房只有 2 路供电，柜级故障要扛住 |
| 小文件（64 KB）读延迟 p99 | ≤ {P99_SMALL:g} ms | 网页、缩略图、配置；云服务 p99 ≤ 50 ms 的一部分 |
| 大文件（16 MB）读延迟 p99 | ≤ {P99_LARGE:g} ms | 模型文件、日志包、备份 |
| 坏盘修复 | ≤ 12 小时修回完整冗余；修复限速 {REPAIR_BW:g} GB/s（不挤占用户带宽） | 运维规程 |

盘的年故障率取 {AFR * 100:.1f} %（大规模机房统计的常见量级，示例值）。数据里约 {HOT * 100:.0f} % 是“热数据”。
"""
case.step("brief", f"{N_NODE} 台节点 {N_DISK} 块盘（{RAW_TB / 1000:.1f} PB 裸）：三年 ≥ {NEED_TB / 1000:g} PB 可用、11 个 9、扛整柜故障、小文件 p99 ≤ {P99_SMALL:g} ms。",
          f"{N_NODE} nodes, {N_DISK} disks ({RAW_TB / 1000:.1f} PB raw): ≥ {NEED_TB / 1000:g} PB usable in three years, 11 nines, survive a rack failure, small-object p99 ≤ {P99_SMALL:g} ms.",
          md=case.text("1_任务书.md", brief),
          facts=[("裸容量", "Raw capacity", round(RAW_TB / 1000, 2), "PB"), ("可用容量要求", "Usable capacity needed", NEED_TB / 1000, "PB"),
                 ("持久性", "Durability", "11 × 9", "")])


# ================================================================ 2–3 方案与计算
def repair_h(name, k):
    """坏一块盘：它上面的数据（{DISK_TB} TB × 装满率）由全集群并行重建；副本读 1 份，纠删码要读 k 块才能算出丢的那块"""
    data = DISK_TB * FILL * 1000                       # GB
    reads = 1 if name == "三副本" else k
    return DETECT + data * reads / REPAIR_BW / 3600


def mttdl_exact(n, f, lam, mu):
    """生灭马尔可夫链：状态 i = 组里坏了 i 块（0…f），坏到 f+1 块丢数据（吸收态）。
    i → i+1 速率 λ_i = (n−i)λ，i → i−1 速率 μ_i = iμ（各块并行修）。从 0 到 f+1 的平均首达时间（精确，全是正项相加，数值稳定）：
    T = Σ_{i=0..f} Σ_{j=0..i} (1/λ_j) Π_{k=j+1..i} (μ_k / λ_k)"""
    la = [(n - i) * lam for i in range(f + 1)]
    mk = [i * mu for i in range(f + 1)]
    T = 0.0
    for i in range(f + 1):
        for j in range(i + 1):
            T += math.prod(mk[k] / la[k] for k in range(j + 1, i + 1)) / la[j]
    return T


def mttdl_approx(n, f, lam, mu):
    """近似公式（λ ≪ μ）：MTTDL ≈ f! μ^f / (n(n−1)…(n−f) λ^(f+1))"""
    prod = math.prod(n - i for i in range(f + 1))
    return math.factorial(f) * mu ** f / (prod * lam ** (f + 1))


def per_rack(n):
    """n 块分到 {N_RACK} 柜，尽量平均：最多的一柜几块"""
    return -(-n // N_RACK)


S = []
for name, en, k, m in SCHEMES:
    n, f, over = nfm(k, m, name)
    tr = repair_h(name, k)
    mu = 1 / tr
    T = mttdl_exact(n, f, LAM, mu)
    p_year = 8760 / T                                   # 一个放置组一年丢数据的概率（≪ 1 时）
    S.append(dict(name=name, en=en, k=k, m=m, n=n, f=f, over=over, usable=RAW_TB * FILL / over, tr=tr, mttdl=T, approx=mttdl_approx(n, f, LAM, mu),
                  p=p_year, nines=-math.log10(p_year), rack=per_rack(n)))
mix_over = HOT * 3.0 + (1 - HOT) * S[1]["over"]
mix_usable = RAW_TB * FILL / mix_over

rows = [[s["name"], f"{s['over']:.2f} ×", f"{s['usable'] / 1000:.2f} PB", f"{s['tr']:.1f} h", f"{s['f']}", f"{s['rack']} / {s['f']}",
         f"{s['p']:.1e}", f"{s['nines']:.1f}"] for s in S]
calcmd = """# 方案与计算

## 三个方案

| 方案 | 存储倍数 | 可用容量 | 坏盘修复时间 | 能同时坏几块 | 一柜最多几块 / 能坏几块 | 一组一年丢数据概率 | 几个 9 |
|---|---|---|---|---|---|---|---|
""" + "\n".join("| " + " | ".join(map(str, r)) + " |" for r in rows) + f"""

- **可用容量** = 裸容量 × {FILL * 100:.0f} % ÷ 存储倍数。三副本只有 {S[0]['usable'] / 1000:.2f} PB **< {NEED_TB / 1000:g} PB，装不下**。
- **修复时间** = 发现 {DETECT:g} h + 盘上数据 {DISK_TB * FILL:g} TB × 要读的份数 ÷ 修复限速 {REPAIR_BW:g} GB/s。纠删码修一块要读 k 块，修复流量是副本的 k 倍。
- **整柜故障**：每个对象的 n 块分到 {N_RACK} 个柜，最多的一柜 ⌈n / {N_RACK}⌉ 块；不超过能坏的块数 f，整柜断电也不丢。三个方案都满足（RS(10,4) 正好卡在边上）。

## 数据持久性：马尔可夫链

一个放置组（一个对象的 n 块所在的那 n 块盘）：状态 i = 坏了 i 块。坏盘速率 (n − i)λ，修复速率 iμ（μ = 1 / 修复时间），坏到 f + 1 块就丢数据。
用生灭过程首达时间的精确公式算平均丢数据时间（MTTDL），一年丢数据的概率 ≈ 8760 h ÷ MTTDL。近似公式 MTTDL ≈ f! μ^f / (n(n−1)…(n−f) λ^(f+1)) 和精确解相差都小于 0.1 %（λ ≪ μ）。

- 三副本 {S[0]['nines']:.1f} 个 9，RS(6,3) {S[1]['nines']:.1f} 个，RS(10,4) {S[2]['nines']:.1f} 个——都过 11 个 9。纠删码能坏的块多，持久性反而更高，尽管修得慢。
- 整个集群 {GROUPS} 个放置组，一年**任何一个对象**丢的概率：三副本 {S[0]['p'] * GROUPS:.1e}，RS(6,3) {S[1]['p'] * GROUPS:.1e}。

## 选：热数据三副本 + 温冷数据 RS(6,3)

- 容量：{HOT * 100:.0f} % × 3 + {(1 - HOT) * 100:.0f} % × 1.5 = {mix_over:.3f} 倍，可用 **{mix_usable / 1000:.2f} PB ≥ {NEED_TB / 1000:g} PB**；
- 为什么热数据不用纠删码：小文件读要等 6 块里最慢的一块，尾延迟高（第 4 步仿真；三副本加“对冲读”才过 p99 要求）；
- 为什么不选 RS(10,4)：容量只多 {(S[2]['usable'] - S[1]['usable']) / 1000:.2f} PB，修复慢 {S[2]['tr'] - S[1]['tr']:.1f} h、修复流量多 2/3，整柜故障时没有余量。
- 对象写入时是热数据（三副本），30 天没人读就由后台迁到 RS(6,3)。
"""
case.step("concept", f"三副本只有 {S[0]['usable'] / 1000:.2f} PB 装不下；选热数据三副本 + 温冷 RS(6,3)：可用 {mix_usable / 1000:.2f} PB，持久性都过 11 个 9，整柜故障不丢。",
          f"Replication alone gives only {S[0]['usable'] / 1000:.2f} PB; hot data on replicas plus warm/cold on RS(6,3) gives {mix_usable / 1000:.2f} PB, all above 11 nines, rack-failure safe.",
          md=case.text("2_方案.md", "# 方案\n\n见第 3 步“方案与计算”：三个方案的容量、修复、持久性、整柜故障对比，以及为什么选热三副本 + 温冷 RS(6,3)。\n\n"
                       + "\n".join(f"- {s['name']}：存储 {s['over']:.2f} 倍、可用 {s['usable'] / 1000:.2f} PB、{s['nines']:.1f} 个 9" for s in S)
                       + f"\n- **选**：热 {HOT * 100:.0f} % 三副本 + 温冷 RS(6,3)，可用 {mix_usable / 1000:.2f} PB\n"),
          facts=[("可用容量（选定）", "Usable (chosen)", round(mix_usable / 1000, 2), "PB"), ("三副本可用", "Replicas only", round(S[0]["usable"] / 1000, 2), "PB")])
case.check("concept", "可用容量（热三副本 + 温冷 RS(6,3)）", "Usable capacity (hot replicas + warm/cold RS(6,3))", round(mix_usable / 1000, 2), ">=", NEED_TB / 1000, "PB", "任务书")
case.step("calc", f"修复：三副本 {S[0]['tr']:.1f} h、RS(6,3) {S[1]['tr']:.1f} h；持久性 {S[0]['nines']:.1f} / {S[1]['nines']:.1f} 个 9；一柜最多 {S[1]['rack']} 块 ≤ 能坏 {S[1]['f']} 块。",
          f"Repair: replicas {S[0]['tr']:.1f} h, RS(6,3) {S[1]['tr']:.1f} h; durability {S[0]['nines']:.1f} / {S[1]['nines']:.1f} nines; at most {S[1]['rack']} chunks per rack ≤ {S[1]['f']} tolerated.",
          md=case.text("3_方案与计算.md", calcmd),
          facts=[("RS(6,3) 修复", "RS(6,3) repair", round(S[1]["tr"], 1), "h"), ("三副本几个 9", "Replica nines", round(S[0]["nines"], 1), ""),
                 ("RS(6,3) 几个 9", "RS(6,3) nines", round(S[1]["nines"], 1), "")])
for s in S[:2]:
    case.check("calc", f"{s['name']} 持久性（几个 9）", f"{s['en']} durability (nines)", round(s["nines"], 1), ">=", DUR_REQ, "", "任务书")
    case.check("calc", f"{s['name']} 整柜故障：一柜最多块数 ≤ 能坏块数", f"{s['en']} rack failure: max chunks per rack ≤ tolerated", s["rack"], "<=", s["f"], "块", "任务书")
case.check("calc", "RS(6,3) 坏盘修复时间", "RS(6,3) disk repair time", round(S[1]["tr"], 1), "<=", 12.0, "h", "运维规程")
case.check("calc", "马尔可夫近似公式与精确解相差（最大）", "Markov approximation vs exact (max)", round(max(abs(s["approx"] / s["mttdl"] - 1) for s in S) * 100, 3), "<=", 1.0, "%", "核对公式")


# ================================================================ 4 仿真：坏盘蒙特卡洛 + 读延迟
def mc_group(n, f, lam, t_rep, n_loss, seed):
    """一个放置组的蒙特卡洛：坏盘按指数分布来（每块盘 λ），每块坏盘**固定**修复时间 t_rep 后修好（不是指数分布——和马尔可夫链的假设不同），
    坏的块数到 f+1 就丢数据、记下时间、整组换新重来。→ 平均丢数据时间（小时）"""
    rng = random.Random(seed)
    total, losses = 0.0, 0
    t, fixing = 0.0, []                                 # fixing：各坏盘修好的时刻
    while losses < n_loss:
        rate = (n - len(fixing)) * lam
        dt = rng.expovariate(rate)
        nxt_fix = min(fixing) if fixing else math.inf
        if t + dt < nxt_fix:
            t += dt
            fixing.append(t + t_rep)
            if len(fixing) > f:
                total += t
                losses += 1
                t, fixing = 0.0, []
        else:
            t = nxt_fix
            fixing.remove(nxt_fix)
    return total / losses


# 正常故障率下丢数据太罕见，蒙特卡洛跑不出来：把故障率放大到 λ·t_rep ≈ 0.02（加速），两种方法在同一组参数下对照，确认马尔可夫链模型可信，
# 再用马尔可夫链算正常故障率（持久性按 λ^(f+1) 缩放，近似公式里看得出来）
mc_rows = []
for s in S:
    lam_acc = 0.02 / s["tr"]
    T_mc = mc_group(s["n"], s["f"], lam_acc, s["tr"], 3000, seed=1672 + s["n"])
    T_mk = mttdl_exact(s["n"], s["f"], lam_acc, 1 / s["tr"])
    s.update(acc=lam_acc / LAM, T_mc=T_mc, T_mk=T_mk, d_mc=(T_mc / T_mk - 1) * 100)
    mc_rows.append([s["name"], f"{lam_acc / LAM:,.0f} ×", f"{T_mk:,.0f} h", f"{T_mc:,.0f} h", f"{s['d_mc']:+.1f} %"])


def read_lat(rng, size_kb, k, degraded=False, load=0.5, hedge=None):
    """读一个对象的延迟 ms。每块盘：寻道 + 旋转等待（对数正态，中位 6 ms）× 排队放大 1/(1 − 负载)^0.5 + 传输（180 MB/s）+ 网络 0.3 ms。
    副本 k = 1：读一块。纠删码：并行读 k 块（每块 size/k）等最慢的；降级读（缺一块）要多读一块校验块、再解码 2 ms。"""
    def disk(sz_kb):
        return rng.lognormvariate(math.log(6.0), 0.55) / (1 - load) ** 0.5 + sz_kb / 1024 / 180 * 1000 + 0.3
    if k == 1:
        a = disk(size_kb)
        if hedge is not None and a > hedge:                 # 对冲读：hedge ms 还没回，就向另一个副本再发一次，谁先回用谁
            return min(a, hedge + disk(size_kb))
        return a
    lat = max(disk(size_kb / k) for _ in range(k))
    return lat + (2.0 if degraded else 0.0)


rng = random.Random(1673)
N_READ = 40000
lat = {}
for s in S:
    k = 1 if s["name"] == "三副本" else s["k"]
    for size, tag in ((64, "small"), (16384, "large")):
        v = sorted(read_lat(rng, size, k) for _ in range(N_READ))
        lat[(s["name"], tag)] = v[int(0.99 * N_READ)]
    if k > 1:
        v = sorted(read_lat(rng, 64, k, degraded=True) for _ in range(N_READ))
        lat[(s["name"], "deg")] = v[int(0.99 * N_READ)]
HEDGE = 20.0                       # 对冲读的等待时间 ms（约单块延迟的 93 分位：约 7 % 的读会多发一次）
v = sorted(read_lat(rng, 64, 1, hedge=HEDGE) for _ in range(N_READ))
lat[("三副本", "hedge")] = v[int(0.99 * N_READ)]
extra = sum(1 for _ in range(N_READ) if read_lat(rng, 64, 1) > HEDGE) / N_READ * 100
# 解析对照：k 块里最慢的一块的 p99 = 单块的 0.99^(1/k) 分位（各块独立）
z = {k: float(np.quantile(np.random.default_rng(5).standard_normal(400000), 0.99 ** (1 / k))) for k in (1, 6, 10)}
p99_formula = {k: math.exp(math.log(6.0) + 0.55 * z[k]) / 0.5 ** 0.5 + 64 / k / 1024 / 180 * 1000 + 0.3 for k in (1, 6, 10)}
d_lat = max(abs(lat[(s["name"], "small")] / p99_formula[1 if s["name"] == "三副本" else s["k"]] - 1) * 100 for s in S)

fig, axs = plt.subplots(1, 2, figsize=(12, 4))
xs = np.arange(len(S))
axs[0].bar(xs - 0.2, [lat[(s["name"], "small")] for s in S], 0.4, label="64 KB 小文件")
axs[0].bar(xs + 0.2, [lat[(s["name"], "large")] / 10 for s in S], 0.4, label="16 MB 大文件（÷10）")
axs[0].scatter([-0.2], [lat[("三副本", "hedge")]], marker="v", s=60, color="#2f9e44", zorder=5, label="三副本 + 对冲读（64 KB）")
axs[0].axhline(P99_SMALL, color="#c92a2a", lw=1, label=f"小文件要求 {P99_SMALL:g} ms")
axs[0].set_xticks(xs, [s["name"] for s in S])
axs[0].set_ylabel("读延迟 p99 / ms")
axs[0].legend(fontsize=8, loc="upper left", bbox_to_anchor=(0, 1.0))
axs[0].set_ylim(0, 60)
axs[0].set_title("读延迟 p99：纠删码小文件慢、大文件快", fontsize=10)
lams = np.logspace(-3, 0.5, 30)
for s in S:
    axs[1].loglog(lams * 100, [8760 / mttdl_exact(s["n"], s["f"], a / 8760, 1 / s["tr"]) for a in lams], label=s["name"])
axs[1].axhline(10 ** -DUR_REQ, color="#c92a2a", lw=1)
axs[1].axvline(AFR * 100, color="k", lw=0.6, ls="--")
axs[1].set_xlabel("盘年故障率 / %（虚线 = 设计取值）")
axs[1].set_ylabel("一组一年丢数据概率")
axs[1].legend(fontsize=8)
axs[1].set_title("持久性随盘故障率（马尔可夫链）", fontsize=10)
case.fig(fig, "4_延迟与持久性.png")
simmd = f"""# 仿真

## 1. 坏盘与修复的蒙特卡洛

马尔可夫链假设修复时间是指数分布；实际修复时间差不多是固定的。蒙特卡洛按**固定修复时间**模拟一个放置组坏盘、修复，直到丢数据，各跑 3 000 次。
正常故障率下丢数据太罕见（要模拟几十亿年），所以把故障率放大到 λ × 修复时间 ≈ 0.02，两种方法在同一组参数下比：

{L.md_table(["方案", "故障率放大", "马尔可夫链", "蒙特卡洛（固定修复）", "相差"], mc_rows)}

相差都在 ±{max(abs(s['d_mc']) for s in S):.0f} % 以内（3 000 次的统计误差约 ±2 %，差别基本就是统计误差——修复时间是固定还是指数分布，对平均丢数据时间影响很小）。马尔可夫链模型可信，第 3 步的几个 9 用它算。

## 2. 读延迟

每块盘的延迟：寻道 + 旋转等待（对数正态，中位 6 ms）、负载 50 % 的排队放大、传输 180 MB/s、网络 0.3 ms；每种情况 {N_READ:,} 次读。

{L.md_table(["方案", "64 KB p99", "16 MB p99", "64 KB 降级读 p99"],
            [[s["name"], f"{lat[(s['name'], 'small')]:.1f} ms", f"{lat[(s['name'], 'large')]:.0f} ms", f"{lat.get((s['name'], 'deg'), float('nan')):.1f} ms" if s["name"] != "三副本" else "—"] for s in S])}

- **小文件**：纠删码要并行读 k 块、等最慢的一块——最慢一块的 p99 是单块的 0.99^(1/k) 分位，比单块的 p99 大得多。仿真和这个公式相差 {d_lat:.1f} %。
  RS(6,3) 小文件 p99 {lat[('RS(6,3)', 'small')]:.1f} ms **超过 {P99_SMALL:g} ms**——所以热的小文件放三副本。
- **三副本也差一点**：只读一个副本，p99 {lat[('三副本', 'small')]:.1f} ms，比 {P99_SMALL:g} ms 多一点。**改设计：对冲读**——{HEDGE:g} ms 还没回（约单块延迟的 {100 - extra:.0f} 分位），
  就向另一个副本再发一次，谁先回用谁。p99 降到 **{lat[('三副本', 'hedge')]:.1f} ms**，只多发 {extra:.1f} % 的读（盘负载 50 %，有余量）。
  纠删码也能对冲（多读一块校验块），但小文件仍要等多块，热数据还是放三副本。
- **大文件**：传输时间占大头，纠删码 k 块并行传、每块只有 1/k，反而**比副本快**（16 MB：三副本 {lat[('三副本', 'large')]:.0f} ms，RS(6,3) {lat[('RS(6,3)', 'large')]:.0f} ms）。
- 右图：盘的故障率翻几倍，三副本最先掉到 11 个 9 以下——遇到一批坏盘（同批次缺陷）时，RS(6,3) 更扛得住。
"""
case.step("sim", f"蒙特卡洛（固定修复）与马尔可夫链相差 ≤ {max(abs(s['d_mc']) for s in S):.0f} %；小文件 p99：三副本 {lat[('三副本', 'small')]:.1f} ms，加对冲读 {lat[('三副本', 'hedge')]:.1f} ms，RS(6,3) {lat[('RS(6,3)', 'small')]:.1f} ms；大文件 RS(6,3) 更快。",
          f"Monte Carlo (fixed repair) within {max(abs(s['d_mc']) for s in S):.0f} % of the Markov chain; small-object p99 {lat[('三副本', 'small')]:.1f} ms replicas, "
          f"{lat[('三副本', 'hedge')]:.1f} ms with hedged reads, vs "
          f"{lat[('RS(6,3)', 'small')]:.1f} ms RS(6,3); RS(6,3) is faster for large objects.",
          md=case.text("4_仿真.md", simmd), figs=[("4_延迟与持久性.png", "读延迟 p99 与持久性", "Read p99 and durability")],
          facts=[("小文件 p99（三副本 + 对冲）", "Small p99 (replicas, hedged)", round(lat[("三副本", "hedge")], 1), "ms"),
                 ("小文件 p99（RS(6,3)）", "Small p99 (RS(6,3))", round(lat[("RS(6,3)", "small")], 1), "ms"),
                 ("大文件 p99（RS(6,3)）", "Large p99 (RS(6,3))", round(lat[("RS(6,3)", "large")]), "ms")])
case.check("sim", "蒙特卡洛与马尔可夫链相差（最大）", "Monte Carlo vs Markov chain (max)", round(max(abs(s["d_mc"]) for s in S), 1), "<=", 15.0, "%",
           "固定 vs 指数修复时间 + 统计误差")
case.check("sim", "读延迟仿真与最慢一块公式相差（小文件，最大）", "Latency sim vs slowest-of-k formula (small, max)", round(d_lat, 1), "<=", 5.0, "%", "核对公式")
case.check("sim", "热数据（三副本 + 对冲读）小文件读 p99", "Hot data (replicas + hedged reads) small-object p99", round(lat[("三副本", "hedge")], 1), "<=", P99_SMALL, "ms", "任务书")
case.check("sim", "对冲读多发的读请求", "Extra reads from hedging", round(extra, 1), "<=", 10.0, "%", "盘的余量（负载 50 %）")
case.check("sim", "温冷数据（RS(6,3)）大文件读 p99", "Warm/cold (RS(6,3)) large-object p99", round(lat[("RS(6,3)", "large")], 1), "<=", P99_LARGE, "ms", "任务书")
case.check("sim", "RS(6,3) 降级读小文件 p99（温冷数据可接受 2 倍）", "RS(6,3) degraded small-object p99 (2× allowed for warm/cold)", round(lat[("RS(6,3)", "deg")], 1), "<=",
           2 * P99_SMALL, "ms", "运维规程")

# ================================================================ 5 图纸：放置与架构
fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.6), gridspec_kw=dict(width_ratios=[1.25, 1]))
ax = axs[0]
ax.set_axis_off()
ax.set_xlim(0, N_RACK * 2.6)
ax.set_ylim(-1.2, NODE_PER + 1.2)
rs = random.Random(9)
stripe = []                                     # RS(6,3) 一个条带：9 块按 3/2/2/2 分到 4 柜、每柜不同节点
for r, cnt in enumerate([3, 2, 2, 2]):
    stripe += [(r, nd) for nd in rs.sample(range(NODE_PER), cnt)]
rep = [(r, rs.randrange(NODE_PER)) for r in rs.sample(range(N_RACK), 3)]
for r in range(N_RACK):
    x0 = r * 2.6 + 0.2
    ax.add_patch(plt.Rectangle((x0, -0.2), 2.2, NODE_PER + 0.4, fc="none", ec="#7b8794", lw=1))
    ax.text(x0 + 1.1, NODE_PER + 0.6, f"存储柜 S{r + 1}", ha="center", fontsize=9)
    for nd in range(NODE_PER):
        fc = "#eef3f8"
        lab = ""
        if (r, nd) in stripe:
            j = stripe.index((r, nd))
            fc, lab = ("#2c6fbb" if j < 6 else "#e8590c"), (f"D{j + 1}" if j < 6 else f"P{j - 5}")
        if (r, nd) in rep:
            fc, lab = "#2f9e44", f"副本{rep.index((r, nd)) + 1}"
        ax.add_patch(plt.Rectangle((x0 + 0.1, nd + 0.05), 2.0, 0.8, fc=fc, ec="white"))
        ax.text(x0 + 1.1, nd + 0.45, lab or f"节点 {nd + 1:02d}", ha="center", va="center", fontsize=6.5, color="white" if lab else "#7b8794")
ax.text(0.2, -1.0, "蓝 = RS(6,3) 数据块，橙 = 校验块（3/2/2/2 分到 4 柜）；绿 = 三副本（3 个柜各一份）", fontsize=8)
ax.set_title("放置规则：同一对象的块分到不同柜、不同节点", fontsize=10)
ax = axs[1]
ax.set_axis_off()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
for (x, y, w, h, t, c) in [(0.3, 8.2, 9.4, 1.2, "对象接口网关（S3 兼容）× 6　无状态，负载均衡", "#eef3f8"),
                           (0.3, 6.2, 4.4, 1.4, "元数据服务（3 副本 + 共识）\n对象名 → 放置组", "#f3f0ff"),
                           (5.3, 6.2, 4.4, 1.4, "放置计算（按柜、节点分）\n放置组 → 盘", "#f3f0ff"),
                           (0.3, 3.6, 4.4, 1.8, f"热池：三副本 + 对冲读（{HEDGE:g} ms）\n新写入、30 天内常读", "#ebfbee"),
                           (5.3, 3.6, 4.4, 1.8, "温冷池：RS(6,3)\n30 天没读的对象后台迁入", "#e7f5ff"),
                           (0.3, 0.6, 9.4, 2.2, f"盘服务（每块盘一个进程）× {N_DISK}\n坏盘：标记下线 → 全集群并行重建（限速 {REPAIR_BW:g} GB/s）→ 回到完整冗余", "#fff4e6")]:
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=c, ec="#2c6fbb"))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=8.5)
ax.annotate("", xy=(7.5, 5.4), xytext=(2.5, 5.4), arrowprops=dict(arrowstyle="->", color="#7b8794"))
ax.text(5.0, 5.55, "分层迁移", ha="center", fontsize=8)
ax.set_title("存储层架构", fontsize=10)
case.fig(fig, "5_放置与架构.png")
cadmd = f"""# 图纸：放置规则与存储层架构

软件没有三维零件，这一步出的是**放置规则**（写进云平台的集群配置）和**存储层架构图**：

| 规则 | 内容 |
|---|---|
| 故障域 | 柜 → 节点 → 盘三级；同一对象的块不放同一节点 |
| 三副本 | 3 份分到 3 个不同的柜 |
| RS(6,3) | 9 块按 3/2/2/2 分到 4 个柜（一柜最多 3 块 = 能坏的块数，整柜断电不丢） |
| 放置组 | {GROUPS} 个，每块盘约 {GROUPS * (HOT * 3 + (1 - HOT) * 9) / N_DISK:.0f} 个组的块 |
| 对冲读 | 热池读 {HEDGE:g} ms 没回，向另一个副本再发一次 |
| 分层 | 写入进热池；30 天没读的对象后台迁到温冷池（每天限 50 TB） |
| 修复 | 坏盘 {DETECT:g} h 内标记下线，全集群并行重建，限速 {REPAIR_BW:g} GB/s |
"""
case.step("cad", "柜 → 节点 → 盘三级故障域；三副本分 3 柜，RS(6,3) 按 3/2/2/2 分 4 柜；热池、温冷池、元数据、网关的架构图。",
          "Rack → node → disk failure domains; replicas across 3 racks, RS(6,3) split 3/2/2/2 over 4 racks; architecture with hot and warm/cold pools, metadata and gateways.",
          md=case.text("5_放置与架构.md", cadmd), figs=[("5_放置与架构.png", "放置规则与存储层架构", "Placement rules and storage architecture")])

# ================================================================ 6 工艺
from factory import data as F  # noqa: E402

rt = F.ROUTINGS[F.BOMS["REL-CLOUD"][0]]
rts = F.ROUTINGS[F.BOMS["SUB-CLOUD"][0]]
procmd = f"""# 工艺：云平台版本发布与订阅开通

**版本（REL-CLOUD）**

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rt)])}

- **集成测试**加三条存储测试：拔一块盘看修复时间（≤ 12 h 按比例缩短的小集群）、断一个柜看能不能读、热 → 温冷迁移后对象校验和不变；
- **长稳压测** 12 小时，量内存增长速率；**发布门禁**量接口延迟 p99（压测，≤ 80 ms）。

**订阅（SUB-CLOUD）**

{L.md_table(["工序", "名称", "设备", "工时 / min"], [[i + 1, op, F.OPERATIONS[op], m] for i, (op, m) in enumerate(rts)])}

服务验收 24 小时：每分钟的延迟 p99、错误率、可用性；存储层的小文件读是服务延迟的一部分。
"""
case.step("process", f"版本 {len(rt)} 道（集成测试加拔盘、断柜、迁移校验）；订阅 {len(rts)} 道（开通 + 24 小时服务验收）。",
          f"Release {len(rt)} steps (integration tests add disk pull, rack cut, migration checksum); subscription {len(rts)} steps (provisioning + 24 h acceptance).",
          md=case.text("6_工艺.md", procmd), tools=tools("engineer"), facts=[("版本工序", "Release steps", len(rt), ""), ("订阅工序", "Subscription steps", len(rts), "")])

# ================================================================ 7 制造
shr = L.run_shop("REL-CLOUD", 10, "WO-CASE-SW-B1", seed=1674)
rows_r, cpk_r, fails_r, _ = L.shop_table(shr["measurements"])
shs = L.run_shop("SUB-CLOUD", 24, "WO-CASE-SW-B2", seed=1675)
rows_s, cpk_s, fails_s, st_s = L.shop_table(shs["measurements"])
makemd = f"""# 制造：10 次云平台构建、24 份云订阅

**云平台版本 REL-CLOUD**（{shr['hours']:.1f} 小时，长稳压测平台一台、每次 12 小时）：

{L.md_table(["特性", "规格", "次数", "均值", "标准差", "Cpk"], rows_r)}

不合格 **{fails_r}**（10 次太少，Cpk 只作参考）。

**云订阅 SUB-CLOUD**（{shs['hours']:.1f} 小时）：

{L.md_table(["特性", "规格", "份数", "均值", "标准差", "Cpk"], rows_s)}

不合格 **{fails_s}**，最低 Cpk {cpk_s:.2f}。服务延迟 p99 平均 {st_s['cl_p99']['mean']:.1f} ms，比 50 ms 的规格低得多——存储层小文件读 p99 {lat[('三副本', 'hedge')]:.1f} ms
是请求里最慢的一段，但大多数请求命中缓存，不到盘。
"""
case.step("make", f"10 次构建不合格 {fails_r}；24 份订阅不合格 {fails_s}、最低 Cpk {cpk_s:.2f}，服务延迟 p99 平均 {st_s['cl_p99']['mean']:.1f} ms。",
          f"10 builds, {fails_r} failures; 24 subscriptions, {fails_s} failures, lowest Cpk {cpk_s:.2f}, mean service p99 {st_s['cl_p99']['mean']:.1f} ms.",
          md=case.text("7_构建与订阅验收.md", makemd), tools=tools("softops", "planner", "quality"),
          facts=[("构建不合格", "Build failures", fails_r, ""), ("订阅不合格", "Subscription failures", fails_s, ""), ("订阅最低 Cpk", "Lowest subscription Cpk", round(cpk_s, 2), "")])
case.check("make", "云平台构建不合格", "Platform build failures", fails_r, "==", 0, "", "发布门禁")
case.check("make", "云订阅不合格", "Subscription failures", fails_s, "==", 0, "", "服务验收")
case.check("make", "云订阅最低 Cpk", "Lowest subscription Cpk", round(cpk_s, 2), ">=", 1.33, "", "常用要求")

# ================================================================ 8 总结
ok_rows = [[("✓" if c["ok"] else "✗"), c["what"], f"{c['value']} {c['unit']}", f"{c['op']} {c['limit']}", c["src"]] for c in case.checks]
review = f"""# 总结

{L.md_table(["", "项目", "结果", "要求", "出处"], ok_rows)}

1. **三副本简单、快，但贵**：存储 3 倍，{N_DISK} 块盘只装得下 {S[0]['usable'] / 1000:.2f} PB；纠删码 1.5 倍，同样的盘装两倍。
2. **纠删码持久性更高，代价是修复流量和尾延迟**：修一块读 6 块；小文件读要等 6 块里最慢的——尾延迟是“最大值的分布”，不是平均值的问题。
3. **分层最划算**：{HOT * 100:.0f} % 热数据三副本（加对冲读）保延迟，其余纠删码省盘；放置规则按柜分，整柜断电也不丢。
4. **几个 9 是模型算出来的**：马尔可夫链（指数修复）和蒙特卡洛（固定修复）在加速条件下对上了，再用模型推到正常故障率。

## 留给学生的问题

1. 盘换成 24 TB：修复时间、持久性怎么变？（修复时间和盘容量成正比，持久性按 μ^f 变。）
2. 只有 3 个存储柜时，RS(6,3) 还能扛整柜故障吗？要改成什么编码？
3. 修复限速从 {REPAIR_BW:g} GB/s 提到 4 GB/s，几个 9 多几个？代价是什么？

相关：软件公司帮助“云平台”；计算机厂案例 C（20 柜机房）；本厂案例 C（容量规划）。
"""
case.step("review", f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} 项校核通过；热三副本 + 温冷 RS(6,3)：{mix_usable / 1000:.2f} PB、≥ {min(S[0]['nines'], S[1]['nines']):.0f} 个 9。",
          f"{sum(c['ok'] for c in case.checks)} / {len(case.checks)} checks pass; hot replicas + warm/cold RS(6,3): {mix_usable / 1000:.2f} PB, ≥ {min(S[0]['nines'], S[1]['nines']):.0f} nines.",
          md=case.text("8_总结.md", review), tools=tools("softops", "quality"))
case.write()
print("ok", [(s["name"], round(s["usable"]), round(s["tr"], 2), round(s["nines"], 2), round(s["d_mc"], 1)) for s in S], round(mix_usable),
      {k: round(v, 1) for k, v in lat.items()}, round(d_lat, 2), fails_r, fails_s, cpk_s)
