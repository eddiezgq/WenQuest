"""3.1 节的示意图。

图 3.1.1：弗林分类：按指令流与数据流的个数分成四类。
图 3.1.2：16 个数的树形归约：每层的加法互不依赖，共 log₂16 = 4 层。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 3.1.1
fig, ax = plt.subplots(figsize=(8.6, 5.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6.2)
ax.axis("off")
cells = [
    (1.0, 3.2, "SISD", T("单指令流单数据流", "single instruction, single data"), T("早期的单核 CPU", "early single-core CPUs"), 1, 1),
    (5.4, 3.2, "SIMD", T("单指令流多数据流", "single instruction, multiple data"), T("CPU 的向量指令；GPU 的线程束（SIMT）", "CPU vector units; GPU warps (SIMT)"), 1, 4),
    (1.0, 0.2, "MISD", T("多指令流单数据流", "multiple instruction, single data"), T("少见（容错系统）", "rare (fault-tolerant systems)"), 3, 1),
    (5.4, 0.2, "MIMD", T("多指令流多数据流", "multiple instruction, multiple data"), T("多核 CPU；多个 SM；多台机器", "multicore CPUs; many SMs; clusters"), 3, 4),
]
for x, y, name, zh, ex, ni, nd in cells:
    ax.add_patch(plt.Rectangle((x, y), 4.0, 2.7, fill=False, ec=C["muted"], lw=1))
    ax.text(x + 0.15, y + 2.4, name, fontsize=13, weight="bold", color=C["ink"], va="top")
    ax.text(x + 1.45, y + 2.36, zh, fontsize=9.5, color=C["ink"], va="top")
    for i in range(ni):                                   # 指令流（橙）
        ax.annotate("", xy=(x + 1.2 + i * 0.35, y + 0.95), xytext=(x + 1.2 + i * 0.35, y + 1.85),
                    arrowprops=dict(arrowstyle="-|>", color=C["accent"], lw=1.6))
    for j in range(nd):                                   # 处理单元与数据流（蓝）
        ax.add_patch(plt.Rectangle((x + 2.2 + j * 0.42, y + 1.1), 0.32, 0.6, color=C["z"], alpha=0.85))
    ax.plot([x + 1.2, x + 1.2 + (ni - 1) * 0.35 + 0.01], [y + 1.4, y + 1.4], color=C["accent"], lw=0)
    ax.text(x + 0.15, y + 0.35, ex, fontsize=9, color=C["muted"])
ax.text(3.0, 6.05, T("单数据流", "single data"), ha="center", fontsize=10.5, color=C["ink"])
ax.text(7.4, 6.05, T("多数据流", "multiple data"), ha="center", fontsize=10.5, color=C["ink"])
ax.text(0.75, 4.55, T("单指令流", "single\ninstruction"), ha="right", va="center", fontsize=10.5, color=C["ink"])
ax.text(0.75, 1.55, T("多指令流", "multiple\ninstruction"), ha="right", va="center", fontsize=10.5, color=C["ink"])
ax.set_xlim(-0.9, 10)
figure(fig, "fig3_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.1.2
fig, ax = plt.subplots(figsize=(8.6, 4.0))
ax.axis("off")
n = 16
xs = [i + 0.5 for i in range(n)]
level = [(x, 4.0) for x in xs]
vals = list(range(1, n + 1))
for x, v in zip(xs, vals):
    ax.add_patch(plt.Rectangle((x - 0.38, 3.75), 0.76, 0.5, color=C["z"], alpha=0.18))
    ax.text(x, 4.0, str(v), ha="center", va="center", fontsize=9, color=C["ink"])
y = 4.0
k = 0
while len(level) > 1:
    k += 1
    ny = y - 0.95
    new, nv = [], []
    for i in range(0, len(level), 2):
        (x1, _), (x2, _) = level[i], level[i + 1]
        xm = (x1 + x2) / 2
        ax.plot([x1, xm], [y - 0.27, ny + 0.27], color=C["muted"], lw=0.9)
        ax.plot([x2, xm], [y - 0.27, ny + 0.27], color=C["muted"], lw=0.9)
        s = vals[i] + vals[i + 1]
        ax.add_patch(plt.Rectangle((xm - 0.38, ny - 0.25), 0.76, 0.5, color=C["accent"], alpha=0.25))
        ax.text(xm, ny, str(s), ha="center", va="center", fontsize=8.5, color=C["ink"])
        new.append((xm, ny))
        nv.append(s)
    ax.text(n + 0.4, ny, T(f"第 {k} 层：{len(new)} 次加法", f"level {k}: {len(new)} additions"), va="center", fontsize=9.5, color=C["ink"])
    level, vals, y = new, nv, ny
ax.text(n + 0.4, 4.0, T("16 个数", "16 numbers"), va="center", fontsize=9.5, color=C["ink"])
ax.set_xlim(-0.2, n + 4.6)
ax.set_ylim(-0.1, 4.4)
figure(fig, "fig3_1_2")
plt.close(fig)
