"""9.1 节的示意图（数据同程序 9.1.1、9.2.1）。

图 9.1.1：70 亿参数的模型（Llama 2 7B 的结构）训练时每块 GPU 的显存，混合精度 + AdamW，序列长 4096、每块 GPU 一条：
模型状态（BF16 参数与梯度、FP32 主权重与两份 AdamW 状态）与激活值（标准注意力 / FlashAttention）。左：一块 GPU 全都放下；
右：64 块 GPU 用 ZeRO-3 切分模型状态。虚线是 A100 80 GB 的显存。
"""
from _ch9 import BIG, params
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N = params(BIG)
s, h, a, L = 4096, BIG["d"], BIG["h"], BIG["L"]
act_std = L * s * h * (34 + 5 * a * s / h) / 1e9
act_fl = L * s * h * 34 / 1e9
fig, ax = plt.subplots(figsize=(10, 4.4))
rows = [(T("1 块 GPU，标准注意力", "1 GPU, standard attention"), 1, act_std), (T("1 块 GPU，FlashAttention", "1 GPU, FlashAttention"), 1, act_fl),
        (T("ZeRO-3，64 块，FlashAttention", "ZeRO-3, 64 GPUs, FlashAttention"), 64, act_fl)]
for i, (lab, p, act) in enumerate(rows):
    parts = [(T("BF16 参数与梯度", "BF16 params & grads"), 4 * N / p / 1e9, C["z"]), (T("FP32 主权重与 AdamW 状态", "FP32 master & AdamW"), 12 * N / p / 1e9, C["accent"]),
             (T("激活值", "activations"), act, C["x"])]
    left = 0
    for name, v, col in parts:
        ax.barh(i, v, left=left, color=col, alpha=0.65, label=name if i == 0 else None)
        if v > 8:
            ax.text(left + v / 2, i, f"{v:.0f}", ha="center", va="center", fontsize=8)
        left += v
    ax.text(left + 3, i, f"{left:.0f} GB", va="center", fontsize=9)
ax.axvline(80, color=C["ink"], ls="--", lw=1)
ax.text(81, 2.45, T("A100 80 GB", "A100 80 GB"), fontsize=9)
ax.set_yticks(range(3))
ax.set_yticklabels([r[0] for r in rows], fontsize=9)
ax.invert_yaxis()
ax.set_xlabel(T("每块 GPU 的显存（GB，估算）", "memory per GPU (GB, estimated)"))
ax.legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout()
figure(fig, "fig9_1_1")
plt.close(fig)
