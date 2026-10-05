"""7.1 节的示意图。

图 7.1.1：深度学习的软件栈。从上到下：用户的 Python 程序；框架（PyTorch：Python 接口、分派器、ATen 算子库、自动微分、缓存分配器；
torch.compile 生成的 Triton 核函数）；CUDA 库（cuBLAS/cuBLASLt、cuDNN、NCCL、CUTLASS、CUB、cuFFT、cuRAND 等）；CUDA 运行时与驱动；GPU。
右侧标出本书哪一章讲哪一层。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, ax = plt.subplots(figsize=(10, 5.6))
layers = [
    (T("用户程序（Python）：model(x)、loss.backward()、optimizer.step()", "User program (Python): model(x), loss.backward(), optimizer.step()"), C["muted"], 0.25, [], T("第 2 章", "Ch. 2")),
    (T("框架：PyTorch", "Framework: PyTorch"), C["z"], 0.35,
     [T("Python 接口", "Python API"), T("分派器", "dispatcher"), T("ATen 算子", "ATen ops"), T("自动微分", "autograd"),
      T("缓存分配器", "caching allocator"), "torch.compile"], T("7.5—7.8 节", "7.5–7.8")),
    (T("CUDA 库", "CUDA libraries"), C["y"], 0.4,
     ["cuBLAS / cuBLASLt", "cuDNN", "NCCL", "CUTLASS", "CUB / Thrust", "cuFFT · cuRAND · …"], T("7.1—7.4 节、第 6 章", "7.1–7.4, Ch. 6")),
    (T("CUDA 运行时与驱动：内存管理、流、启动核函数", "CUDA runtime and driver: memory, streams, kernel launch"), C["accent"], 0.35, [], T("第 4、6 章", "Ch. 4, 6")),
    (T("GPU：SM、张量核心、显存、NVLink", "GPU: SMs, tensor cores, memory, NVLink"), C["x"], 0.3, [], T("第 3 章", "Ch. 3")),
]
y = 0
for name, col, alpha, boxes, ch in layers:
    h = 1.1 if boxes else 0.7
    ax.add_patch(plt.Rectangle((0, y), 8.4, h, fc=col, alpha=alpha, ec="none"))
    ax.text(0.15, y + (0.27 if boxes else h / 2), name, va="center", fontsize=10)
    for i, b in enumerate(boxes):
        bx = 0.15 + i * 1.37
        ax.add_patch(plt.Rectangle((bx, y + 0.5), 1.27, 0.5, fc="white", ec=col, lw=1))
        ax.text(bx + 0.635, y + 0.75, b, ha="center", va="center", fontsize=7.5)
    ax.text(8.6, y + h / 2, ch, va="center", fontsize=9, color=C["muted"])
    y += h + 0.15
ax.annotate("", xy=(-0.3, y - 0.2), xytext=(-0.3, 0.1), arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1.2))
ax.text(-0.45, y / 2, T("一行代码向下走到核函数", "one line of code travels down to a kernel"), rotation=90, ha="center", va="center", fontsize=9)
ax.set_xlim(-0.8, 10.0)
ax.set_ylim(-0.1, y)
ax.invert_yaxis()
ax.axis("off")
fig.tight_layout()
figure(fig, "fig7_1_1")
plt.close(fig)
