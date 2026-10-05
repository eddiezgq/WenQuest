"""10.5 节的示意图（事实依各家官方文档，截至 2026 年 10 月）。

图 10.5.1：写一段算子，有几种写法，各能跑在哪里。越往上越可移植、越不费人力，也越难榨干硬件；
越往下越接近硬件，也越被一家厂商绑住。格子的颜色表示现状：
上游直接支持（绿）、要装厂商的扩展或独立的后端（黄）、要自己改写或没有（灰）。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, ax = plt.subplots(figsize=(10.2, 4.6))

rows = [  # 由上到下：越来越贴近硬件
    (T("框架（PyTorch 等）", "Framework (PyTorch…)"), [2, 2, 1, 1]),
    (T("编译器与图优化（torch.compile）", "Compiler (torch.compile)"), [2, 2, 1, 0]),
    (T("Triton（Python 写核函数）", "Triton (kernels in Python)"), [2, 2, 1, 0]),
    (T("SYCL / OpenCL", "SYCL / OpenCL"), [1, 1, 0, 0]),
    (T("厂商自己的语言与库", "Vendor language and libraries"), [2, 2, 2, 2]),
]
cols = [T("NVIDIA", "NVIDIA"), T("AMD", "AMD"), T("昇腾", "Ascend"), T("其他国产", "Other CN")]
note = {2: T("上游支持", "upstream"), 1: T("扩展/独立后端", "extension"), 0: T("要改写或没有", "rewrite / none")}
fill = {2: C["y"], 1: C["accent"], 0: C["muted"]}
alpha = {2: 0.55, 1: 0.45, 0: 0.25}
vendor_lang = [T("CUDA C++", "CUDA C++"), "HIP", "Ascend C", T("BANG C / MUSA…", "BANG C / MUSA…")]

for i, (name, cells) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.text(-0.15, y + 0.42, name, ha="right", va="center", fontsize=9)
    for j, s in enumerate(cells):
        ax.add_patch(plt.Rectangle((j, y), 0.9, 0.84, fc=fill[s], alpha=alpha[s], ec="none"))
        txt = vendor_lang[j] if i == len(rows) - 1 else note[s]
        ax.text(j + 0.45, y + 0.42, txt, ha="center", va="center", fontsize=7.5, color=C["ink"])
for j, c in enumerate(cols):
    ax.text(j + 0.45, len(rows) + 0.05, c, ha="center", fontsize=9.5, color=C["ink"])
ax.annotate("", (-0.05, 0.1), (-0.05, len(rows) - 0.1), arrowprops=dict(arrowstyle="-|>", lw=1.0, color=C["muted"]))
ax.text(4.05, len(rows) - 0.6, T("可移植", "portable"), fontsize=8.5, color=C["muted"])
ax.text(4.05, 0.3, T("贴近硬件", "close to the metal"), fontsize=8.5, color=C["muted"])
ax.set_xlim(-3.1, 5.4)
ax.set_ylim(-0.3, len(rows) + 0.45)
ax.axis("off")
fig.tight_layout()
figure(fig, "fig10_5_1")
