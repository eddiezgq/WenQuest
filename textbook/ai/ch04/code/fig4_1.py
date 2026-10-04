"""4.1 节的示意图。

图 4.1.1：（a）一个 CUDA 程序的编译：nvcc 把 .cu 文件分成主机代码与设备代码，设备代码编译成 PTX 与机器码（SASS），
合在一个可执行文件里；（b）主机与设备：CPU 与内存、GPU 与显存，经 PCIe 相连，核函数在 GPU 上由成千上万个线程执行。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS


def box(ax, x, y, w, h, text, col, fs=9.5, alpha=0.18):
    ax.add_patch(plt.Rectangle((x, y), w, h, color=col, alpha=alpha, lw=0))
    ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, ec=col, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=C["ink"])


def arr(ax, x1, y1, x2, y2, col=None):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=col or C["muted"], lw=1.2))


fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.05, 1]})
ax = axs[0]
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")
box(ax, 0.3, 2.5, 2.0, 1.0, "vadd.cu", C["accent"])
box(ax, 3.2, 4.0, 2.6, 1.0, T("主机代码\n（main 等）", "host code\n(main etc.)"), C["y"])
box(ax, 3.2, 1.0, 2.6, 1.0, T("设备代码\n（__global__ 核函数）", "device code\n(__global__ kernels)"), C["z"])
box(ax, 6.6, 4.0, 2.2, 1.0, T("C++ 编译器\n（gcc 等）", "C++ compiler\n(gcc etc.)"), C["y"])
box(ax, 6.6, 1.6, 2.2, 0.8, "PTX", C["z"])
box(ax, 6.6, 0.4, 2.2, 0.8, T("机器码 SASS", "machine code SASS"), C["z"])
box(ax, 3.6, 2.6, 5.0, 0.8, T("可执行文件（主机程序 + 嵌入的设备代码）", "executable (host program + embedded device code)"), C["ink"], fs=9, alpha=0.06)
arr(ax, 2.3, 3.2, 3.2, 4.4)
arr(ax, 2.3, 2.8, 3.2, 1.5)
arr(ax, 5.8, 4.5, 6.6, 4.5)
arr(ax, 5.8, 1.5, 6.6, 2.0)
arr(ax, 7.7, 1.6, 7.7, 1.2)
ax.text(1.3, 4.2, "nvcc", fontsize=11, weight="bold", color=C["ink"], ha="center")
ax.set_title(T("（a）nvcc 的编译过程", "(a) What nvcc does"), fontsize=11)
ax = axs[1]
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")
box(ax, 0.3, 3.3, 3.0, 1.4, T("CPU\n运行 main()", "CPU\nruns main()"), C["accent"])
box(ax, 0.3, 0.8, 3.0, 1.6, T("主机内存\nha, hb, hc", "host memory\nha, hb, hc"), C["accent"], alpha=0.08)
box(ax, 6.4, 3.3, 3.4, 1.4, T("GPU：成千上万个\n线程执行核函数", "GPU: thousands of\nthreads run the kernel"), C["z"])
box(ax, 6.2, 0.8, 3.5, 1.6, T("显存（全局内存）\nda, db, dc", "device memory (global)\nda, db, dc"), C["z"], alpha=0.08)
ax.annotate("", xy=(6.2, 1.6), xytext=(3.3, 1.6), arrowprops=dict(arrowstyle="<|-|>", color=C["x"], lw=2))
ax.text(4.75, 1.85, T("PCIe：cudaMemcpy", "PCIe: cudaMemcpy"), ha="center", fontsize=9, color=C["x"])
arr(ax, 3.3, 4.0, 6.4, 4.0, C["ink"])
ax.text(4.85, 4.75, T("启动：vadd<<<g, b>>>(…)", "launch: vadd<<<g, b>>>(…)"), ha="center", fontsize=9, color=C["ink"])
ax.plot([1.8, 1.8], [3.3, 2.4], color=C["muted"], lw=1)
ax.plot([7.95, 7.95], [3.3, 2.4], color=C["muted"], lw=1)
ax.text(1.8, 5.3, T("主机（host）", "host"), ha="center", fontsize=10.5, weight="bold", color=C["ink"])
ax.text(7.95, 5.3, T("设备（device）", "device"), ha="center", fontsize=10.5, weight="bold", color=C["ink"])
ax.set_title(T("（b）主机与设备", "(b) Host and device"), fontsize=11)
figure(fig, "fig4_1_1")
plt.close(fig)
