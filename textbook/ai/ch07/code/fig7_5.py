"""7.5 节的示意图（规则同程序 7.5.1）。

图 7.5.1：一行 y = x @ w（x、w 在 GPU 上、要记录梯度）的调用链：Python 绑定 → 组合算子 matmul 分解成 mm → 分派器按分派键依次经过自动微分层（记录反向要用的节点）
与 CUDA 层（ATen 的 mm） → cuBLAS 选核函数 → CUDA 运行时与驱动发出启动 → GPU 执行。主机这一路要花几到十几微秒，
发出启动后立即返回，Python 拿到的结果张量此时可能还没算完（异步）。动画 7.5.1 演示这一过程。

图 7.5.2：（a）步长视图：3×4 的张量存放在 12 个数的存储里，形状 (3, 4)、步长 (4, 1)；转置只把形状与步长对调成 (4, 3)、(1, 4)，
切片 x[:, 1:3] 改形状为 (3, 2)、起点为 1，都不搬数据，但都不再连续。
（b）缓存分配器：向驱动要来的一段 20 MB 显存，被切成几块分给张量；张量释放后块回到池里（与相邻的空闲块合并），
下一次同样大小的请求直接取用，不再调用 cudaMalloc。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
steps = [(T("Python：y = x @ w", "Python: y = x @ w"), T("Tensor.__matmul__ → C++ 绑定", "Tensor.__matmul__ → C++ binding"), C["muted"]),
         (T("aten::matmul（组合算子）", "aten::matmul (composite)"), T("按维数分解成 aten::mm（三维以上为 bmm）", "decomposed into aten::mm (bmm for 3-D and up)"), C["z"]),
         (T("分派器：自动微分键", "dispatcher: Autograd key"), T("记录反向节点 MmBackward0，保存 x、w", "record MmBackward0, save x and w"), C["z"]),
         (T("分派器：CUDA 键 → ATen 的 mm", "dispatcher: CUDA key → ATen mm"), T("分配输出（缓存分配器），检查步长", "allocate output (caching allocator), check strides"), C["z"]),
         (T("cuBLAS：cublasSgemm", "cuBLAS: cublasSgemm"), T("按形状挑选核函数（启发式）", "choose a kernel for the shape (heuristics)"), C["y"]),
         (T("CUDA 运行时与驱动", "CUDA runtime and driver"), T("cudaLaunchKernel：命令写进流的队列，立即返回", "cudaLaunchKernel: queue the command, return at once"), C["accent"]),
         (T("GPU", "GPU"), T("核函数在 SM 上执行（异步，稍后）", "the kernel runs on the SMs (asynchronously, later)"), C["x"])]
fig, ax = plt.subplots(figsize=(10, 5.4))
for i, (who, what, col) in enumerate(steps):
    ax.add_patch(plt.Rectangle((0, i), 4.0, 0.72, fc=col, alpha=0.3, ec=col))
    ax.text(2.0, i + 0.36, who, ha="center", va="center", fontsize=10)
    ax.text(4.25, i + 0.36, what, va="center", fontsize=9)
    if i:
        ax.annotate("", xy=(2.0, i - 0.02), xytext=(2.0, i - 0.27), arrowprops=dict(arrowstyle="->", color=C["ink"]))
ax.annotate("", xy=(-0.25, 5.72), xytext=(-0.25, 0.0), arrowprops=dict(arrowstyle="<->", color=C["muted"]))
ax.text(-0.4, 2.86, T("主机：几到十几 μs", "host: a few to tens of μs"), rotation=90, ha="center", va="center", fontsize=9, color=C["muted"])
ax.set_xlim(-0.7, 10.2)
ax.set_ylim(-0.2, 6.9)
ax.invert_yaxis()
ax.axis("off")
fig.tight_layout()
figure(fig, "fig7_5_1")
plt.close(fig)

fig, (a, b) = plt.subplots(2, 1, figsize=(11, 6.2), gridspec_kw={"height_ratios": [1.15, 1]})


def strip(ax, y, hl, col, label):
    for k in range(12):
        on = k in hl
        ax.add_patch(plt.Rectangle((k * 0.7, y), 0.7, 0.55, fc=col if on else "white", alpha=0.55 if on else 1, ec=C["ink"], lw=0.7))
        ax.text(k * 0.7 + 0.35, y + 0.27, str(k), ha="center", va="center", fontsize=9)
    ax.text(-0.2, y + 0.27, label, ha="right", va="center", fontsize=9)


strip(a, 0.0, set(range(12)), C["z"], T("x：形状 (3, 4)，步长 (4, 1)", "x: shape (3, 4), stride (4, 1)"))
strip(a, 0.9, {0, 4, 8}, C["y"], T("x.T 的第 0 行：形状 (4, 3)，步长 (1, 4)", "row 0 of x.T: shape (4, 3), stride (1, 4)"))
strip(a, 1.8, {1, 2, 5, 6, 9, 10}, C["x"], T("x[:, 1:3]：形状 (3, 2)，步长 (4, 1)，起点 1", "x[:, 1:3]: shape (3, 2), stride (4, 1), offset 1"))
a.text(4.2, 2.75, T("同一块存储（12 个数）；位置 = 起点 + Σ 下标 × 步长", "one storage of 12 numbers; position = offset + Σ index × stride"), ha="center", fontsize=9)
a.set_xlim(-6.2, 8.6)
a.set_ylim(-0.2, 3.0)
a.invert_yaxis()
a.axis("off")
a.set_title(T("（a）视图只改形状、步长与起点", "(a) A view changes only shape, stride and offset"), fontsize=10)

segs = [(0, 6, T("张量 A（6 MB）", "tensor A (6 MB)"), C["z"]), (6, 4, T("张量 B（4 MB）", "tensor B (4 MB)"), C["y"]),
        (10, 10, T("空闲（留在池里）", "free (kept in the pool)"), None)]
for row, (title, items) in enumerate([(T("一段 20 MB（一次 cudaMalloc）", "one 20 MB segment (one cudaMalloc)"), segs),
                                      (T("A 释放后：块回到池里，下一个 6 MB 的请求直接用它", "after A is freed: its block returns to the pool for the next 6 MB request"),
                                       [(0, 6, T("空闲", "free"), None)] + segs[1:])]):
    y = row * 1.3
    for x0, w, s, col in items:
        b.add_patch(plt.Rectangle((x0 * 0.42, y), w * 0.42, 0.6, fc=col or "#eeeeee", alpha=0.5 if col else 1, ec=C["ink"], lw=0.8))
        b.text((x0 + w / 2) * 0.42, y + 0.3, s, ha="center", va="center", fontsize=8.5)
    b.text(8.7, y + 0.3, title, va="center", fontsize=9)
b.set_xlim(-0.2, 15.5)
b.set_ylim(-0.2, 2.1)
b.invert_yaxis()
b.axis("off")
b.set_title(T("（b）缓存分配器：显存要来以后不还给驱动，反复使用", "(b) Caching allocator: memory is kept and reused, not returned to the driver"), fontsize=10)
fig.tight_layout()
figure(fig, "fig7_5_2")
plt.close(fig)
