"""3.6 节的示意图。

图 3.6.1：线程束分化（GPU 执行模拟器部分 ②，数据同程序 3.6.1）。横轴是线程束依次发射的指令，纵轴是 32 个线程；
有色格子是在这条指令上活动的线程，白格是空转的线程。（a）按线程号奇偶分支：两条路径依次执行，各有一半线程空转；
（b）按线程束编号分支：每个线程束内部一致，只执行一条路径。
"""
import numpy as np

from _gpusim import diverge
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
base = dict(pre=2, then=4, other=4, post=2)
COL = {"pre": C["muted"], "post": C["muted"], "then": C["z"], "else": C["accent"]}


def draw(ax, res, w, x0):
    mask = [c == "1" for c in res["warps"][w]["mask"]]
    for i, kind in enumerate(res["steps"][w]):
        for lane in range(32):
            on = kind in ("pre", "post") or (kind == "then" and mask[lane]) or (kind == "else" and not mask[lane])
            ax.add_patch(plt.Rectangle((x0 + i, lane), 0.9, 0.9, color=COL[kind] if on else "white",
                                       ec=C["muted"] if not on else None, lw=0.3, alpha=0.85 if on else 1))
    return len(res["steps"][w])


fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.8), gridspec_kw={"width_ratios": [12, 17.5]})
ax = axs[0]
r = diverge("odd", warps=1, **base)
n = draw(ax, r, 0, 0)
ax.set_xlim(-0.3, n + 0.2)
ax.set_title(T(f"（a）if (t % 2 == 1)：发射 {n} 条，效率 {100 * r['eff']:.0f}%", f"(a) if (t % 2 == 1): {n} issued, {100 * r['eff']:.0f}% efficient"), fontsize=10.5)
ax = axs[1]
r = diverge("warp", warps=2, **base)
n0 = draw(ax, r, 0, 0)
n1 = draw(ax, r, 1, n0 + 1.5)
ax.set_xlim(-0.3, n0 + n1 + 1.7)
ax.text(n0 / 2, -2.2, T("线程束 0：全走 else", "warp 0: all take else"), ha="center", fontsize=9, color=C["ink"])
ax.text(n0 + 1.5 + n1 / 2, -2.2, T("线程束 1：全走 then", "warp 1: all take then"), ha="center", fontsize=9, color=C["ink"])
ax.set_title(T(f"（b）if (线程束编号为奇数)：每个线程束 {n0} 条，效率 100%", f"(b) if (warp id odd): {n0} per warp, 100% efficient"), fontsize=10.5)
for a in axs:
    a.set_ylim(-3.2, 32.2)
    a.invert_yaxis()
    a.set_yticks([0, 8, 16, 24, 31])
    a.set_xticks([])
    a.set_ylabel(T("线程（通道）", "thread (lane)"))
    for s in ("top", "right", "bottom"):
        a.spines[s].set_visible(False)
axs[0].set_xlabel(T("依次发射的指令 →", "instructions in issue order →"))
axs[1].set_xlabel(T("依次发射的指令 →", "instructions in issue order →"))
handles = [plt.Rectangle((0, 0), 1, 1, color=COL[k]) for k in ("pre", "then", "else")]
fig.legend(handles, [T("分支前后（全部活动）", "before/after the branch"), "then", "else"], loc="lower center", ncol=3, frameon=False, fontsize=9)
fig.tight_layout(rect=(0, 0.06, 1, 1))
figure(fig, "fig3_6_1")
plt.close(fig)
