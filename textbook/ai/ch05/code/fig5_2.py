"""5.2 节的示意图（与动画 5.2.1 对应）。

图 5.2.1：16 个数在一个线程块的共享内存中树形归约，每层之间同步一次。（a）交错寻址（版本 1、2）：第 s 层由位置 2s·k 加上 2s·k + s；
（b）顺序寻址（版本 3）：第 s 层由前 s 个位置加上后 s 个位置。两者都是 4 层、15 次加法；区别在于每层干活的是哪些线程、读哪些位置。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N = 16
fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
for ax, mode in zip(axs, ("inter", "seq")):
    vals = list(range(N))
    for lvl in range(5):
        y = -lvl
        for i in range(N):
            live = (i % (2 ** lvl) == 0) if mode == "inter" else (i < N >> lvl)
            ax.add_patch(plt.Rectangle((i, y - 0.35), 0.9, 0.7, fc=C["z"] if live else "#e6e9ec", alpha=0.6 if live else 1, ec="white"))
        if lvl == 4:
            break
        s = 2 ** lvl if mode == "inter" else N >> (lvl + 1)
        targets = range(0, N, 2 * s) if mode == "inter" else range(s)
        for k, t in enumerate(targets):
            src = t + s
            for frm in (t, src):
                ax.annotate("", xy=(t + 0.45, y - 1 + 0.35), xytext=(frm + 0.45, y - 0.35),
                            arrowprops=dict(arrowstyle="-|>", color=C["accent"] if frm == src else C["muted"], lw=1.1))
        ax.text(N + 0.3, y - 0.5, T(f"s = {s}：{len(targets)} 次加法", f"s = {s}: {len(targets)} adds"), fontsize=9, va="center")
    ax.set_xlim(-0.3, N + 4.2)
    ax.set_ylim(-4.6, 0.6)
    ax.axis("off")
    ax.set_title(T("（a）交错寻址：位置 2s·k ← 2s·k + s" if mode == "inter" else "（b）顺序寻址：位置 k ← k + s（k < s）",
                   "(a) Interleaved: slot 2s·k ← 2s·k + s" if mode == "inter" else "(b) Sequential: slot k ← k + s (k < s)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig5_2_1")
plt.close(fig)
