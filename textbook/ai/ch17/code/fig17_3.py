"""17.3 节的示意图。

图 17.3.1（动画 17.3.1 的静态版）：智能体的一轮循环，以及每步出错率怎样把成功率压下去。
图 17.3.2：（a）三种救法各买回多少；（b）末端校验的误判率一高就开始帮倒忙。
"""
import numpy as np

from _ch17 import plain, steps_for, with_check, with_retry, with_verifier
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 17.3.1
fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.4))

# （a）一轮循环的四步
steps = [(T("规划", "plan"), T("下一步做什么", "what to do next")),
         (T("调工具", "act"), T("取数、改文件、跑测试", "fetch, edit, run tests")),
         (T("读结果", "observe"), T("工具回了什么", "what came back")),
         (T("修正", "revise"), T("对不对，要不要重来", "right? retry?"))]
pos = [(0.18, 0.72), (0.72, 0.72), (0.72, 0.26), (0.18, 0.26)]
for (name, desc), (x, y) in zip(steps, pos):
    a.add_patch(plt.Rectangle((x - 0.15, y - 0.09), 0.30, 0.18, facecolor="white",
                              edgecolor=C["z"], lw=1.6, zorder=3))
    a.text(x, y + 0.03, name, ha="center", fontsize=11, zorder=4)
    a.text(x, y - 0.045, desc, ha="center", fontsize=7.5, color=C["muted"], zorder=4)
for i in range(4):
    x1, y1 = pos[i]
    x2, y2 = pos[(i + 1) % 4]
    a.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=2,
               arrowprops=dict(arrowstyle="-|>", color=C["muted"], lw=1.6,
                               shrinkA=34, shrinkB=34,
                               connectionstyle="arc3,rad=0.22"))
a.text(0.45, 0.50, T("每转一圈\n都可能出错", "every lap\ncan go wrong"), ha="center",
       fontsize=10, color=C["x"])
a.set_xlim(0, 1)
a.set_ylim(0.08, 0.92)
a.axis("off")
a.set_title(T("(a) 智能体的一轮循环", "(a) One lap of the agent loop"), fontsize=10)

ns = np.arange(1, 61)
for p, col in ((0.01, C["z"]), (0.02, C["y"]), (0.05, C["accent"]), (0.10, C["x"])):
    b.plot(ns, [plain(p, int(n)) for n in ns], color=col, lw=1.9,
           label=T(f"每步出错 {p * 100:.0f}%", f"{p * 100:.0f}% error per step"))
    nmax = steps_for(p, 0.8)
    if nmax <= 60:
        b.plot([nmax], [0.8], "o", color=col, ms=6)
b.axhline(0.8, color=C["muted"], ls="--", lw=1.0)
b.text(42, 0.82, T("保住 80%", "80% success"), fontsize=8, color=C["muted"])
b.set_xlabel(T("一共走几步 n", "number of steps n"))
b.set_ylabel(T("整件事做成的概率 (1−p)ⁿ", "probability the whole task succeeds"))
b.set_ylim(0, 1.02)
b.set_title(T("(b) 每一步的小毛病会乘起来", "(b) Small per-step errors multiply"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig17_3_1")

# ---------------------------------------------------------------- 图 17.3.2
P, N = 0.05, 20
fig2, (c, d) = plt.subplots(1, 2, figsize=(11.4, 4.2))

names = [T("什么都不做", "nothing"), T("整件事重试 3 次", "retry the whole task ×3"),
         T("每步自检（查出率 0.8）", "per-step check (detect 0.8)"),
         T("末端校验（0.95 / 0.05）", "final verifier (0.95 / 0.05)")]
vals = [plain(P, N), with_retry(P, N, 3), with_check(P, N, 0.8), with_verifier(P, N, 0.95, 0.05)]
cols = [C["muted"], C["z"], C["y"], C["accent"]]
bars = c.barh(names, vals, color=cols)
for bar, val in zip(bars, vals):
    c.text(bar.get_width() + 0.012, bar.get_y() + bar.get_height() / 2, f"{val:.3f}",
           va="center", fontsize=9)
c.set_xlim(0, 1.05)
c.set_xlabel(T(f"整件事做成的概率（每步出错 {P * 100:.0f}%，走 {N} 步）",
                f"success probability ({P * 100:.0f}% per-step error, {N} steps)"))
c.set_title(T("(a) 三种救法各买回多少", "(a) What each remedy buys"), fontsize=10)
c.grid(alpha=0.25, lw=0.5, axis="x")
c.invert_yaxis()

fprs = np.linspace(0, 0.8, 41)
for tpr, col in ((1.0, C["z"]), (0.95, C["y"]), (0.8, C["x"])):
    d.plot(fprs, [with_verifier(P, N, tpr, float(f)) for f in fprs], color=col, lw=1.9,
           label=T(f"查错能力 {tpr:.2f}", f"detection rate {tpr:.2f}"))
d.axhline(plain(P, N), color=C["muted"], ls="--", lw=1.2,
          label=T("不校验", "no verifier"))
d.set_xlabel(T("把对的误判成错的概率", "probability of rejecting a correct result"))
d.set_ylabel(T("交付出去的结果是对的概率", "probability the delivered result is right"))
d.set_title(T("(b) 误判率一高，校验器开始帮倒忙",
              "(b) Too many false rejections and the verifier backfires"), fontsize=10)
d.legend(fontsize=8)
d.grid(alpha=0.25, lw=0.5)

fig2.tight_layout()
figure(fig2, "fig17_3_2")
