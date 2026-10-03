"""3.7 节的示意图（GPU 执行模拟器部分 ①）。

图 3.7.1：一个调度器的逐周期甘特图。为了看得清，把显存延迟缩短为 60 个周期，每次读显存后做 k = 4 条算术指令；
线程束数分别为 2、6、13（按式 (3.7.1)，13 个正好能藏住延迟）。
图 3.7.2：延迟 L = 700 个周期时，每个调度器的发射利用率随线程束数的变化：点为模拟，线为式 (3.7.1) 的估计；
竖线是 H100 每个调度器最多的 16 个线程束。
"""
import numpy as np

from _gpusim import little, schedule
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
COL = {"I": C["z"], "M": "#f2d7a6", "R": "#d9e6f2", "B": "#e8c4c4"}

# ---------------------------------------------------------------- 图 3.7.1
Ls, k, span = 60, 4, 200
cases = [2, 6, 13]
fig, axs = plt.subplots(len(cases), 1, figsize=(10.4, 6.4), gridspec_kw={"height_ratios": [2, 6, 13]})
for ax, n in zip(axs, cases):
    r = schedule(warps=n, latency=Ls, k=k, cycles=2000, trace=span)
    for w, row in enumerate(r["trace"]):
        c = 0
        while c < span:
            st = row[c]
            e = c
            while e < span and row[e] == st:
                e += 1
            ax.add_patch(plt.Rectangle((c, w), e - c, 0.85, color=COL[st], lw=0))
            c = e
    busy = sum(1 for c in range(span) if any(row[c] == "I" for row in r["trace"]))
    ax.set_xlim(0, span)
    ax.set_ylim(n, -0.15)
    ax.set_yticks([0, n - 1] if n > 2 else [0, 1])
    ax.set_ylabel(T(f"{n} 个\n线程束", f"{n}\nwarps"), rotation=0, ha="right", va="center", fontsize=9.5)
    ax.text(span + 2, n / 2, T(f"稳态\n利用率\n{100 * r['util']:.0f}%", f"steady\nutil.\n{100 * r['util']:.0f}%"), va="center", fontsize=9.5, color=C["ink"])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[-1].set_xlabel(T("周期", "cycle"))
handles = [plt.Rectangle((0, 0), 1, 1, color=COL[s]) for s in ("I", "M", "R")]
fig.legend(handles, [T("发射指令", "issue"), T("等显存数据", "waiting for memory"), T("准备好但没轮到", "ready, not picked")],
           loc="lower center", ncol=3, frameon=False, fontsize=9)
fig.tight_layout(rect=(0, 0.05, 0.95, 1))
figure(fig, "fig3_7_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.7.2
L = 700
fig, ax = plt.subplots(figsize=(8.4, 4.4))
ns = np.arange(1, 65)
for k, col in ((4, C["x"]), (16, C["accent"]), (46, C["z"])):
    ax.plot(ns, [100 * little(n, k, L) for n in ns], color=col, lw=1.6, label=f"k = {k}")
    pts = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64]
    ax.plot(pts, [100 * schedule(warps=n, latency=L, k=k, cycles=60000)["util"] for n in pts], "o", color=col, ms=4.5)
ax.axvline(16, color=C["muted"], lw=1, ls="--")
ax.text(16.8, 6, T("H100：每个调度器\n最多 16 个线程束", "H100: at most\n16 warps per scheduler"), fontsize=8.8, color=C["muted"])
ax.set_xlabel(T("每个调度器的线程束数 n", "warps per scheduler n"))
ax.set_ylabel(T("发射利用率（%）", "issue utilization (%)"))
ax.set_ylim(0, 105)
ax.legend(fontsize=9, frameon=False, title=T("每次读后的算术指令", "arithmetic per load"), title_fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig3_7_2")
plt.close(fig)
