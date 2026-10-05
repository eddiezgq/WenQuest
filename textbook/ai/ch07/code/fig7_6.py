"""7.6 节的示意图（数据同程序 7.6.1，按保存的张量逐项估算；实测见程序 7.6.2）。

图 7.6.1：小型 Transformer（B = 32，T = 256，单精度，AdamW）训练时的显存：参数、梯度与优化器状态，
加上为反向保存的激活（按类别）。上：不重计算；下：重计算（每层只存残差流，反向时重计算一层）。
"""
from _ch7 import B, D, L, PARAMS, T as TT, saved_activations, saved_head
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
MB = 1e6
per = dict(saved_activations())
P = per["softmax 的输出 P"]
ff = per["ff1 的输出（GELU 的输入）"] + per["GELU 的输出（ff2 的输入）"]
layer = sum(per.values())
head = sum(v for _, v in saved_head())
resid = B * TT * D
rows = [
    (T("不重计算", "no recomputation"), [(T("参数、梯度、AdamW 状态", "params, grads, AdamW"), PARAMS * 16, C["muted"]),
                                     (T("注意力权重 P", "attention weights P"), L * P * 4, C["x"]),
                                     (T("前馈网络中间结果", "FFN intermediates"), L * ff * 4, C["accent"]),
                                     (T("其余激活", "other activations"), L * (layer - P - ff) * 4, C["z"]),
                                     (T("输出层", "output head"), head * 4, C["y"])]),
    (T("重计算", "recomputation"), [(T("参数、梯度、AdamW 状态", "params, grads, AdamW"), PARAMS * 16, C["muted"]),
                                  (T("每层的残差流", "residual stream per layer"), L * resid * 4, "#9467bd"),
                                  (T("正在重计算的一层", "the layer being recomputed"), layer * 4, "#8c564b"),
                                  (T("输出层", "output head"), head * 4, C["y"])]),
]
fig, ax = plt.subplots(figsize=(11, 3.4))
seen = set()
for i, (name, parts) in enumerate(rows):
    left = 0
    for lab, v, col in parts:
        ax.barh(i, v / MB, left=left, color=col, alpha=0.6, ec="white", label=None if lab in seen else lab)
        seen.add(lab)
        if v / MB > 90:
            ax.text(left + v / MB / 2, i, f"{v / MB:.0f}", ha="center", va="center", fontsize=8)
        left += v / MB
    ax.text(left + 20, i, f"{left:.0f} MB", va="center", fontsize=9)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows])
ax.invert_yaxis()
ax.set_xlim(0, 2100)
ax.set_xlabel(T("显存（MB，估算）", "memory (MB, estimated)"))
ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower right", bbox_to_anchor=(1.0, 1.0))
fig.tight_layout()
figure(fig, "fig7_6_1")
plt.close(fig)
