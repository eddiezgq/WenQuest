"""7.8 节的示意图。

图 7.8.1：torch.compile 的三个阶段。TorchDynamo 在 Python 执行字节码之前截住它，把其中的张量运算记录成 FX 图，并写下“守卫”
（输入的形状、类型等条件，下次调用时先检查，满足就直接用编译好的代码）；遇到它处理不了的 Python 代码就“图中断”，
那一段照常由 Python 执行，前后各成一张图。AOTAutograd 事先追踪出反向图，把前向与反向分开，并决定哪些中间结果保存、哪些在反向时重计算。
TorchInductor 把图中的运算融合、调度，生成 Triton 核函数，矩阵乘法调用 cuBLAS（或生成模板核函数）；mode="reduce-overhead" 时再用 CUDA 图提交。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, ax = plt.subplots(figsize=(12.5, 3.3))


def box(x, y, w, h, title, body, col):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=col, alpha=0.25, ec=col, lw=1.2))
    ax.text(x + w / 2, y + 0.28, title, ha="center", va="center", fontsize=10, weight="bold")
    ax.text(x + w / 2, y + 0.55, body, ha="center", va="top", fontsize=8.5, linespacing=1.5)


def data(x, y, s):
    ax.text(x, y, s, ha="center", va="center", fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=C["muted"]))


data(0.6, 0.97, T("Python 函数\nmodel(x)", "Python function\nmodel(x)"))
box(1.4, 0.3, 2.6, 1.35, "TorchDynamo", T("截住字节码\n张量运算记成 FX 图\n写下守卫（形状、类型…）\n处理不了的代码：图中断",
                                           "intercept bytecode\nrecord tensor ops as an FX graph\nwrite guards (shapes, dtypes…)\nunsupported code: graph break"), C["z"])
data(4.55, 0.97, T("FX 图\n（前向）", "FX graph\n(forward)"))
box(5.1, 0.3, 2.6, 1.35, "AOTAutograd", T("事先追踪出反向图\n切分前向与反向\n决定保存什么、重计算什么",
                                         "trace the backward ahead of time\nsplit forward and backward\nchoose what to save or recompute"), C["y"])
data(8.25, 0.97, T("前向图\n反向图", "forward graph\nbackward graph"))
box(8.8, 0.3, 2.6, 1.35, "TorchInductor", T("融合逐元素运算与归约\n生成 Triton 核函数\n矩阵乘法调 cuBLAS\n（可选）CUDA 图",
                                           "fuse pointwise ops and reductions\ngenerate Triton kernels\ncall cuBLAS for GEMMs\n(optional) CUDA graphs"), C["x"])
data(12.0, 0.97, T("GPU 上的\n核函数", "kernels\non the GPU"))
for x0, x1 in [(1.05, 1.38), (4.02, 4.15), (4.95, 5.08), (7.72, 7.8), (8.7, 8.78), (11.42, 11.6)]:
    ax.annotate("", xy=(x1, 0.97), xytext=(x0, 0.97), arrowprops=dict(arrowstyle="->", color=C["ink"]))
ax.text(6.4, 1.95, T("下次调用：守卫都满足 → 直接运行编译好的代码；不满足（例如形状变了）→ 重新编译",
                     "next call: guards hold → run the compiled code; a guard fails (e.g. new shape) → recompile"), ha="center", fontsize=9, color=C["muted"])
ax.set_xlim(0, 12.8)
ax.set_ylim(0.1, 2.15)
ax.invert_yaxis()
ax.axis("off")
fig.tight_layout()
figure(fig, "fig7_8_1")
plt.close(fig)
