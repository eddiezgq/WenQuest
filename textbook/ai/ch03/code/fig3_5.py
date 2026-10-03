"""3.5 节的示意图。

图 3.5.1：H100 一个流多处理器（SM）的组成（示意，按 H100 架构白皮书图 7 简化）：4 个处理块，各有线程束调度器、
分发单元、64 KB 寄存器堆、32 条 FP32 通道、1 个张量核心、加载/存储单元与特殊函数单元；4 块共用 256 KB 的 L1 缓存/共享内存。
图 3.5.2：H100 的存储层次：容量与带宽（数据同程序 3.5.1；寄存器堆与共享内存的带宽是按最高频率的理想上限）。
"""
import runpy
from pathlib import Path

import bookout
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
saved = bookout.out
v = {}
bookout.out = lambda **kw: v.update(kw)
runpy.run_path(str(Path(__file__).with_name("ex3_5.py")))
bookout.out = saved

# ---------------------------------------------------------------- 图 3.5.1
fig, ax = plt.subplots(figsize=(9.6, 6.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.6)
ax.axis("off")
ax.add_patch(plt.Rectangle((0.1, 0.1), 9.8, 6.3, fill=False, ec=C["ink"], lw=1.4))
ax.text(5, 6.15, T("流多处理器（SM）", "Streaming multiprocessor (SM)"), ha="center", fontsize=12, weight="bold", color=C["ink"])
for p in range(4):
    x0 = 0.3 + p * 2.4
    ax.add_patch(plt.Rectangle((x0, 1.5), 2.2, 4.4, fill=False, ec=C["muted"], lw=1))
    ax.add_patch(plt.Rectangle((x0 + 0.1, 5.25), 2.0, 0.5, color=C["accent"], alpha=0.45))
    ax.text(x0 + 1.1, 5.5, T("线程束调度器", "warp scheduler"), ha="center", va="center", fontsize=8.6, color=C["ink"])
    ax.add_patch(plt.Rectangle((x0 + 0.1, 4.65), 2.0, 0.5, color=C["accent"], alpha=0.25))
    ax.text(x0 + 1.1, 4.9, T("分发单元", "dispatch unit"), ha="center", va="center", fontsize=8.6, color=C["ink"])
    ax.add_patch(plt.Rectangle((x0 + 0.1, 3.95), 2.0, 0.6, color=C["y"], alpha=0.4))
    ax.text(x0 + 1.1, 4.25, T("寄存器堆 64 KB", "register file 64 KB"), ha="center", va="center", fontsize=8.6, color=C["ink"])
    for r in range(4):
        for c in range(8):
            ax.add_patch(plt.Rectangle((x0 + 0.12 + c * 0.25, 3.0 + r * 0.22), 0.2, 0.17, color=C["z"], alpha=0.8))
    ax.text(x0 + 1.1, 2.82, T("32 条 FP32 通道", "32 FP32 lanes"), ha="center", va="top", fontsize=8.2, color=C["ink"])
    ax.add_patch(plt.Rectangle((x0 + 0.1, 1.95), 1.2, 0.5, color=C["x"], alpha=0.55))
    ax.text(x0 + 0.7, 2.2, T("张量核心", "tensor core"), ha="center", va="center", fontsize=8.2, color="white")
    ax.add_patch(plt.Rectangle((x0 + 1.4, 1.95), 0.7, 0.5, color=C["muted"], alpha=0.35))
    ax.text(x0 + 1.75, 2.2, "LD/ST\nSFU", ha="center", va="center", fontsize=7.2, color=C["ink"])
    ax.text(x0 + 1.1, 1.65, T(f"处理块 {p + 1}", f"partition {p + 1}"), ha="center", fontsize=8.2, color=C["muted"])
ax.add_patch(plt.Rectangle((0.3, 0.3), 9.4, 0.95, color=C["y"], alpha=0.25))
ax.text(5, 0.78, T("L1 数据缓存 / 共享内存 共 256 KB（共享内存最多 228 KB）", "L1 data cache / shared memory, 256 KB in all (up to 228 KB shared)"),
        ha="center", va="center", fontsize=9.5, color=C["ink"])
figure(fig, "fig3_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.5.2
fig, ax = plt.subplots(figsize=(8.4, 4.4))
levels = [
    (T("寄存器堆", "registers"), v["reg_total_MB"] * 2 ** 20, v["bw_reg_T"] * 1e12, C["y"]),
    (T("共享内存", "shared memory"), v["smem_total_MB"] * 2 ** 20, v["bw_smem_T"] * 1e12, C["z"]),
    (T("L2 缓存", "L2 cache"), v["l2_MB"] * 2 ** 20, None, C["accent"]),
    (T("显存（HBM3）", "HBM3"), v["mem_GB"] * 1e9, v["bw_hbm_T"] * 1e12, C["x"]),
]
for i, (name, cap, bw, col) in enumerate(levels):
    ax.barh(i, cap, color=col, alpha=0.75, height=0.55)
    cap_txt = f"{cap / 2 ** 20:.0f} MB" if cap < 1e9 else f"{cap / 1e9:.0f} GB"
    bw_txt = T(f"，约 {bw / 1e12:.0f} TB/s", f", ≈ {bw / 1e12:.0f} TB/s") if bw and bw > 1e13 else (T(f"，{bw / 1e12:.2f} TB/s", f", {bw / 1e12:.2f} TB/s") if bw else "")
    ax.text(cap * 1.3, i, cap_txt + bw_txt, va="center", fontsize=9.5, color=C["ink"])
ax.set_xscale("log")
ax.set_yticks(range(len(levels)))
ax.set_yticklabels([lv[0] for lv in levels])
ax.invert_yaxis()
ax.set_xlim(1e7, 3e12)
ax.set_xlabel(T("全卡合计容量（字节，对数坐标）", "total capacity on the GPU (bytes, log scale)"))
ax.set_title(T("越往上越快、越小，离运算单元越近", "Faster, smaller and closer to the ALUs towards the top"), fontsize=10.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig3_5_2")
plt.close(fig)
