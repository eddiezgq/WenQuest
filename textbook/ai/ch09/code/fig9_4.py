"""9.4 节的示意图（调度规则同程序 9.4.1）。

图 9.4.1：4 段流水线、8 个微批的调度（横轴是时间，每格一个单位；前向 1、反向 2）。（a）GPipe：全部前向做完再做反向；
（b）1F1B：稳定以后每段交替做一个前向、一个反向。空白是气泡，两者的气泡一样多，但 1F1B 每段同时存着的微批最多 4 个。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
p, m = 4, 8


def gpipe():
    ev = []
    for s in range(p):
        for i in range(m):
            ev.append((s, s + i, 1, "F", i))
    t0 = p - 1 + m
    for s in reversed(range(p)):
        for i in range(m):
            ev.append((s, t0 + (p - 1 - s) * 2 + i * 2, 2, "B", i))
    return ev


def one_f_one_b():
    """逐个时刻模拟：每段先做 p − s 个前向（预热），然后在能做反向时优先做反向。"""
    ready_f = {(0, i): 0 for i in range(m)}
    done_f, done_b, free, ev = {}, {}, [0] * p, []
    nf, nb = [0] * p, [0] * p
    t = 0
    while any(n < m for n in nb):
        for s in range(p):
            if free[s] > t:
                continue
            i = nb[s]
            back_ready = i < m and (s, i) in done_f and done_f[(s, i)] <= t and (s == p - 1 or ((s + 1, i) in done_b and done_b[(s + 1, i)] <= t))
            warm = nf[s] - nb[s] < p - s
            j = nf[s]
            fwd_ready = j < m and (s == 0 or ((s - 1, j) in done_f and done_f[(s - 1, j)] <= t))
            if back_ready and not (warm and fwd_ready):
                ev.append((s, t, 2, "B", i)); done_b[(s, i)] = t + 2; free[s] = t + 2; nb[s] += 1
            elif fwd_ready and nf[s] - nb[s] < p - s:
                ev.append((s, t, 1, "F", j)); done_f[(s, j)] = t + 1; free[s] = t + 1; nf[s] += 1
        t += 1
    return ev


fig, axes = plt.subplots(2, 1, figsize=(12, 4.6), sharex=True)
for ax, ev, title in ((axes[0], gpipe(), T("（a）GPipe", "(a) GPipe")), (axes[1], one_f_one_b(), T("（b）1F1B", "(b) 1F1B"))):
    end = max(t + d for _, t, d, _, _ in ev)
    for s, t, d, k, i in ev:
        ax.add_patch(plt.Rectangle((t, p - 1 - s), d, 0.8, fc=C["z"] if k == "F" else C["y"], alpha=0.35 + 0.05 * i, ec="white"))
        ax.text(t + d / 2, p - 1 - s + 0.4, str(i + 1), ha="center", va="center", fontsize=7)
    ax.set_yticks([p - 1 - s + 0.4 for s in range(p)])
    ax.set_yticklabels([T(f"第 {s + 1} 段", f"stage {s + 1}") for s in range(p)], fontsize=8)
    ax.set_xlim(0, 34)
    ax.set_ylim(-0.2, p)
    ax.set_title(title + T(f"：共 {end} 个单位，气泡占 {100 * (1 - m * 3 / end):.0f}%", f": {end} units, bubble {100 * (1 - m * 3 / end):.0f}%"), fontsize=10, loc="left")
axes[1].set_xlabel(T("时间（前向 1，反向 2；蓝：前向，绿：反向，数字是第几个微批）", "time (forward 1, backward 2; blue forward, green backward, numbers are micro-batches)"))
fig.tight_layout()
figure(fig, "fig9_4_1")
plt.close(fig)
