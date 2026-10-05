"""9.3 节的示意图。

图 9.3.1：三种并行怎样切分同一个模型（4 层，4 块 GPU）。（a）数据并行：每块 GPU 一份完整的模型，数据分成 4 份；
（b）张量并行：每一层的矩阵按列 / 按行切成 4 份，每块 GPU 拿每一层的四分之一，层内要通信；
（c）流水线并行：按层切，每块 GPU 拿一层，层与层之间传激活值。颜色表示 GPU。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
cols = [C["z"], C["x"], C["y"], C["accent"]]
fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))
titles = [T("（a）数据并行", "(a) Data parallel"), T("（b）张量并行", "(b) Tensor parallel"), T("（c）流水线并行", "(c) Pipeline parallel")]
for k, ax in enumerate(axes):
    for layer in range(4):
        y = 3 - layer
        for g in range(4):
            if k == 0:
                ax.add_patch(plt.Rectangle((g * 1.05, y), 0.95, 0.8, fc=cols[g], alpha=0.55, ec="white"))
                ax.text(g * 1.05 + 0.47, y + 0.4, T("整层", "full"), ha="center", va="center", fontsize=8)
            elif k == 1:
                ax.add_patch(plt.Rectangle((g * 1.05, y), 0.95, 0.8, fc=cols[g], alpha=0.55, ec="white"))
                ax.text(g * 1.05 + 0.47, y + 0.4, "¼", ha="center", va="center", fontsize=9)
            else:
                if g == layer:
                    ax.add_patch(plt.Rectangle((g * 1.05, y), 0.95, 0.8, fc=cols[g], alpha=0.55, ec="white"))
        ax.text(-0.15, y + 0.4, T(f"第 {layer + 1} 层", f"layer {layer + 1}"), ha="right", va="center", fontsize=8)
    for g in range(4):
        ax.text(g * 1.05 + 0.47, -0.35, f"GPU {g}", ha="center", fontsize=8)
    note = [T("每块一份完整模型；反向后全归约梯度", "full model each; all-reduce gradients"),
            T("每层切成 4 份；每层前向、反向各要全归约", "each layer split 4 ways; all-reduce inside layers"),
            T("每块一层；相邻两块之间传激活值", "one layer each; activations passed between GPUs")][k]
    ax.text(2.1, 4.25, note, ha="center", fontsize=8.5, color=C["muted"])
    ax.set_xlim(-1.2, 4.3)
    ax.set_ylim(-0.6, 4.6)
    ax.axis("off")
    ax.set_title(titles[k], fontsize=10)
fig.tight_layout()
figure(fig, "fig9_3_1")
plt.close(fig)
