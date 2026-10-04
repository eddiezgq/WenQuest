"""5.8 节的示意图（数据同程序 5.8.1，GPU 执行模拟器部分 ⑤）。

图 5.8.1：（a）共享内存分块：线程块负责 C 的一个 T×T 块（橙色），沿 K 方向一步步把 A 的 T×T 块（红）与 B 的 T×T 块（蓝）读进共享内存，
图中是第 3 步；（b）n = 4096 时，块边长 T 与计算强度（不计缓存）：T 每翻一番，显存读量减半，计算强度翻一番；虚线是 A10 单精度的屋脊。
"""
from _ch5 import A10
from bookout import COLORS, T, figure, style
from gpusim import gemm_tiles

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.35, 1]})
nb = 6                                                     # 6×6 个块
st = gemm_tiles(M=nb * 32, N=nb * 32, K=nb * 32, bm=32, bn=32, bk=32, block=(2, 4))["steps"]


def grid(x0, y0, name):
    for i in range(nb):
        for j in range(nb):
            a.add_patch(plt.Rectangle((x0 + j, y0 + i), 1, 1, fc="#f2f4f6", ec="white", lw=1))
    a.text(x0 + nb / 2, y0 - 0.5, name, ha="center", fontsize=12)


grid(0, 7.5, "A")
grid(7.5, 0, "B")
grid(7.5, 7.5, "C")
s = st[3]
for kk in range(nb):                                       # 这一行块与这一列块：整个 K 方向
    a.add_patch(plt.Rectangle((kk, 7.5 + 2), 1, 1, fc=C["x"], alpha=0.15, ec="white"))
    a.add_patch(plt.Rectangle((7.5 + 4, kk), 1, 1, fc=C["z"], alpha=0.15, ec="white"))
a.add_patch(plt.Rectangle((s["a"][2] // 32, 7.5 + s["a"][0] // 32), 1, 1, fc=C["x"], alpha=0.8, ec="white"))
a.add_patch(plt.Rectangle((7.5 + s["b"][2] // 32, s["b"][0] // 32), 1, 1, fc=C["z"], alpha=0.8, ec="white"))
a.add_patch(plt.Rectangle((7.5 + 4, 7.5 + 2), 1, 1, fc=C["accent"], alpha=0.9, ec="white"))
a.text(0, 14.6, T("线程块 (2, 4) 的第 3 步：深色两块在共享内存里", "block (2, 4), step 3: the two dark tiles are in shared memory"), fontsize=9)
a.set_xlim(-0.5, 14)
a.set_ylim(15.2, -1.2)
a.set_aspect("equal")
a.axis("off")
a.set_title(T("（a）C 的一块由 A 的一行块与 B 的一列块算出", "(a) A C tile from a row of A tiles and a column of B tiles"), fontsize=10)
ts = [1, 2, 4, 8, 16, 32, 64, 128]
Is = [gemm_tiles(M=4096, N=4096, K=4096, bm=t, bn=t, bk=t)["intensity"] for t in ts]
b.plot(ts, Is, "o-", color=C["z"])
for t, v in zip(ts, Is):
    b.annotate(f"{v:.2g}", (t, v), textcoords="offset points", xytext=(-4, 7), fontsize=8)
ridge = A10["fp32"] / A10["bw"]
b.axhline(ridge, color=C["x"], ls="--", lw=1.2, label=T(f"A10 单精度屋脊 {ridge:.0f} FLOP/B", f"A10 FP32 ridge, {ridge:.0f} FLOP/B"))
b.set_xscale("log", base=2)
b.set_yscale("log")
b.set_xticks(ts)
b.set_xticklabels([str(t) for t in ts])
b.set_xlabel(T("块边长 T（T = 1 即不分块）", "tile size T (T = 1: no tiling)"))
b.set_ylabel(T("计算强度（FLOP/B，不计缓存）", "intensity (FLOP/B, no caches)"))
b.set_title(T("（b）分块越大，计算强度越高", "(b) Bigger tiles, higher intensity"), fontsize=10)
b.legend(fontsize=9, frameon=False, loc="lower right")
fig.tight_layout()
figure(fig, "fig5_8_1")
plt.close(fig)
