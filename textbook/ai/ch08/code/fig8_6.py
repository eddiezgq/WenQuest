"""8.6 节的示意图。

图 8.6.1：同一个向量加法的两种写法。（a）CUDA：网格由线程块组成，程序员写“一个线程做什么”——算出自己的下标 i，处理一个元素；
线程块里的线程怎样合并访问、怎样用共享内存，都要自己安排。（b）Triton：网格由程序实例组成，程序员写“一个程序实例处理一块（BLOCK 个）
元素做什么”，下标 offs 是一个向量；块内怎样分给线程束与线程、怎样合并访问与向量化、要不要用共享内存，由编译器决定。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.4))
for ax, title, unit, code, col in (
        (a, T("（a）CUDA：写一个线程", "(a) CUDA: write one thread"), T("线程", "thread"),
         "i = blockIdx.x * blockDim.x + threadIdx.x\nif (i < n) z[i] = x[i] + y[i];", C["z"]),
        (b, T("（b）Triton：写一个程序实例（一块数据）", "(b) Triton: write one program instance (a block)"), T("程序实例", "program"),
         "offs = pid * BLOCK + tl.arange(0, BLOCK)\nmask = offs < n\nx = tl.load(x_ptr + offs, mask=mask)\ny = tl.load(y_ptr + offs, mask=mask)\ntl.store(z_ptr + offs, x + y, mask=mask)", C["y"])):
    for k in range(4):
        ax.add_patch(plt.Rectangle((k * 2.6, 2.2), 2.4, 1.3, fc=col, alpha=0.18, ec=col))
        ax.text(k * 2.6 + 1.2, 3.75, (T("线程块 ", "block ") if ax is a else T("实例 ", "pid ")) + str(k), ha="center", fontsize=9)
        if ax is a:
            for j in range(8):
                ax.add_patch(plt.Rectangle((k * 2.6 + 0.12 + j * 0.27, 2.5), 0.22, 0.7, fc=col, alpha=0.6, ec="none"))
        else:
            ax.add_patch(plt.Rectangle((k * 2.6 + 0.12, 2.5), 2.16, 0.7, fc=col, alpha=0.6, ec="none"))
            ax.text(k * 2.6 + 1.2, 2.85, "BLOCK", ha="center", va="center", fontsize=8, color="white")
    ax.text(0.0, 1.65, T("程序员写的：", "you write:"), fontsize=9, color=C["muted"])
    ax.text(0.0, 1.35, code, fontsize=8.5, family="monospace", va="top")
    ax.text(10.4, 2.85, ("← " + unit), fontsize=9, va="center", color=C["muted"])
    ax.set_xlim(-0.2, 12.2)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.set_title(title, fontsize=10)
fig.tight_layout()
figure(fig, "fig8_6_1")
plt.close(fig)
