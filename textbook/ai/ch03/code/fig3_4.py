"""3.4 节的示意图。

图 3.4.1：历代 NVIDIA 数据中心 GPU（2010 年为 GeForce GTX 580）的（a）FP32 峰值、FP16 张量核心峰值（稠密）与显存带宽，
对数坐标；（b）平衡点 P/β（AI 常用精度的峰值除以带宽；没有张量核心的取 FP32）。数据见 conventions/gpus.py。
"""
from bookout import COLORS, T, figure, style
from gpus import GPUS

plt = style()
C = COLORS
order = ["gtx580", "k40", "p100", "v100", "a100", "h100", "b200"]
G = [GPUS[k] for k in order]
yr = [g["year"] for g in G]
fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.3))
ax = axs[0]
ax.semilogy(yr, [g["fp32"] / 1e12 for g in G], "o-", color=C["z"], label=T("FP32 峰值（TFLOP/s）", "FP32 peak (TFLOP/s)"))
tc = [(g["year"], g["fp16t"] / 1e12) for g in G if g["fp16t"]]
ax.semilogy([a for a, _ in tc], [b for _, b in tc], "s-", color=C["x"], label=T("FP16 张量核心（TFLOP/s，稠密）", "FP16 tensor (TFLOP/s, dense)"))
ax.semilogy(yr, [g["bw"] / 1e12 for g in G], "^-", color=C["accent"], label=T("显存带宽（TB/s）", "memory bandwidth (TB/s)"))
for g in G:
    ax.text(g["year"], g["fp32"] / 1e12 * 0.55, g["name"], ha="center", fontsize=7.8, color=C["muted"], va="top")
ax.set_xlabel(T("年份", "year"))
ax.set_xlim(2009, 2025)
ax.set_ylim(0.05, 6000)
ax.legend(fontsize=8.6, frameon=False, loc="upper left")
ax.set_title(T("（a）算力与带宽", "(a) Compute and bandwidth"), fontsize=11)
ax = axs[1]
bal = [(g["fp16t"] or g["fp32"]) / g["bw"] for g in G]
bars = ax.bar(range(len(G)), bal, color=[C["muted"] if not g["fp16t"] else C["x"] for g in G], width=0.6)
for bb, val in zip(bars, bal):
    ax.text(bb.get_x() + bb.get_width() / 2, val + 5, f"{val:.0f}", ha="center", fontsize=8.6, color=C["ink"])
ax.set_xticks(range(len(G)))
ax.set_xticklabels([f"{g['name']}\n{g['year']}" for g in G], fontsize=8.4)
ax.set_ylabel(T("平衡点 P/β（FLOP/B）", "balance point P/β (FLOP/B)"))
ax.text(0, 270, T("灰：FP32（无张量核心）\n红：FP16 张量核心", "grey: FP32 (no tensor cores)\nred: FP16 tensor cores"), fontsize=8.6, color=C["muted"])
ax.set_title(T("（b）每读一个字节要做多少次运算", "(b) FLOPs needed per byte"), fontsize=11)
for a in axs:
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig3_4_1")
plt.close(fig)
