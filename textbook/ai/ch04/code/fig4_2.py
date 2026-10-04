"""4.2 节的示意图。

图 4.2.1：一帧 3840×2160 的图像被 240×135 个 16×16 的线程块覆盖（只画左上角 6×4 个块）；放大一个线程块
blockIdx = (3, 2)，其中的线程 threadIdx = (5, 7) 处理第 39 行第 53 列的像素（算例 4.2.1，数据同程序 4.2.2）。
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
runpy.run_path(str(Path(__file__).with_name("ex4_2.py")))
bookout.out = saved

fig, axs = plt.subplots(1, 2, figsize=(11, 4.8), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axs[0]
nb_x, nb_y = 6, 4
for i in range(nb_x):
    for j in range(nb_y):
        hit = (i, j) == (v["bx"], v["by"])
        ax.add_patch(plt.Rectangle((i * 16, j * 16), 16, 16, fill=hit, color=C["z"] if hit else None, alpha=0.25 if hit else 1,
                                   ec=C["ink"], lw=1))
        ax.text(i * 16 + 1.2, j * 16 + 3.2, f"({i},{j})", ha="left", va="center", fontsize=8.5, color=C["ink"])
ax.plot([v["col"] + 0.5], [v["row"] + 0.5], "s", color=C["x"], ms=5)
ax.set_xlim(-2, nb_x * 16 + 2)
ax.set_ylim(nb_y * 16 + 2, -6)
ax.set_aspect("equal")
ax.set_xticks([0, 16, 32, 48, 64, 80, 96])
ax.set_yticks([0, 16, 32, 48, 64])
ax.set_xlabel(T("列 col（x）", "column col (x)"))
ax.set_ylabel(T("行 row（y）", "row (y)"))
ax.xaxis.set_label_position("top")
ax.xaxis.tick_top()
ax.set_title(T(f"（a）图像左上角：线程块 blockIdx = (x, y)，全图 {v['gx']}×{v['gy']} 块",
               f"(a) Top-left of the image: blocks blockIdx = (x, y); {v['gx']}×{v['gy']} in all"), fontsize=10.5, pad=28)
ax = axs[1]
for i in range(16):
    for j in range(16):
        hit = (i, j) == (v["tx"], v["ty"])
        ax.add_patch(plt.Rectangle((i, j), 1, 1, color=C["x"] if hit else C["z"], alpha=0.85 if hit else 0.15, lw=0))
        ax.add_patch(plt.Rectangle((i, j), 1, 1, fill=False, ec=C["muted"], lw=0.4))
ax.set_xlim(-0.5, 16.5)
ax.set_ylim(16.5, -0.5)
ax.set_aspect("equal")
ax.set_xticks([0, 5, 10, 15])
ax.set_yticks([0, 7, 15])
ax.xaxis.tick_top()
ax.text(8, 18.2, T(f"threadIdx = ({v['tx']}, {v['ty']})：col = {v['bx']}·16 + {v['tx']} = {v['col']}，row = {v['by']}·16 + {v['ty']} = {v['row']}",
                   f"threadIdx = ({v['tx']}, {v['ty']}): col = {v['bx']}·16 + {v['tx']} = {v['col']}, row = {v['by']}·16 + {v['ty']} = {v['row']}"),
        ha="center", fontsize=9.5, color=C["ink"])
ax.set_title(T(f"（b）放大线程块 ({v['bx']}, {v['by']})：16×16 个线程", f"(b) Block ({v['bx']}, {v['by']}) enlarged: 16×16 threads"),
             fontsize=10.5, pad=28)
fig.tight_layout()
figure(fig, "fig4_2_1")
plt.close(fig)
