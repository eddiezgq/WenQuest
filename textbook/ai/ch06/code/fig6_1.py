"""6.1 节的示意图（数据同程序 6.1.2）。

图 6.1.1：6 帧图像的时间线。上：一个流，每帧“上传 → 处理 → 传回”依次进行；下：三个流，复制引擎（上传）、计算单元、复制引擎（传回）
各自忙着不同的帧。按 PCIe 4.0 ×16 的理论带宽算，处理的计算量取与上传相当。
"""
from _ch6 import A10, FRAME_GRAY, FRAME_RGB
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
th = FRAME_RGB / A10["pcie"] * 1e3
td = FRAME_GRAY / A10["pcie"] * 1e3
tk = th
F = 6
col = {"h": C["z"], "k": C["accent"], "d": C["y"]}
fig, ax = plt.subplots(figsize=(11, 3.6))


def bar(lane, t0, dt, kind, f):
    ax.barh(lane, dt, left=t0, height=0.6, color=col[kind], alpha=0.85, edgecolor="white")
    ax.text(t0 + dt / 2, lane, str(f + 1), ha="center", va="center", fontsize=8, color="white")


t = 0.0
for f in range(F):                                          # 串行：一条时间线
    bar(5, t, th, "h", f)
    bar(5, t + th, tk, "k", f)
    bar(5, t + th + tk, td, "d", f)
    t += th + tk + td
serial_end = t
h_free = k_free = d_free = 0.0
for f in range(F):                                          # 流水线：三个硬件各管一段，同一帧的三段有先后
    a = h_free
    h_free = a + th
    b = max(h_free, k_free)
    k_free = b + tk
    c = max(k_free, d_free)
    d_free = c + td
    bar(2, a, th, "h", f)
    bar(1, b, tk, "k", f)
    bar(0, c, td, "d", f)
ax.set_yticks([5, 2, 1, 0])
ax.set_yticklabels([T("一个流", "one stream"), T("复制引擎：上传", "copy engine: upload"), T("计算单元：处理", "SMs: process"),
                    T("复制引擎：传回", "copy engine: download")])
ax.axvline(serial_end, color=C["muted"], ls=":", lw=1)
ax.axvline(d_free, color=C["muted"], ls=":", lw=1)
ax.text(serial_end, 5.55, T(f"{serial_end:.1f} ms", f"{serial_end:.1f} ms"), ha="right", fontsize=9)
ax.text(d_free, 2.55, T(f"三个流：{d_free:.1f} ms", f"three streams: {d_free:.1f} ms"), ha="right", fontsize=9)
for k, (name, c) in enumerate([(T("上传", "upload"), col["h"]), (T("处理", "process"), col["k"]), (T("传回", "download"), col["d"])]):
    ax.barh(-1.2, 0.3, left=0.2 + k * 1.6, height=0.35, color=c)
    ax.text(0.6 + k * 1.6, -1.2, name, va="center", fontsize=9)
ax.set_ylim(-1.7, 6)
ax.set_xlabel(T("时间（ms）", "time (ms)"))
ax.set_title(T("6 帧图像：一个流与三个流的时间线（数字是帧号）", "Six frames: one stream vs three streams (numbers are frames)"), fontsize=10)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig6_1_1")
plt.close(fig)
