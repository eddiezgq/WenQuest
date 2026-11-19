"""23.7 节的图：为什么这种数字不能横向比（**全部是合成数据**）。

图 23.7.1：三家虚构的运营方，**同一套上报事件数**，换四种口径算出来就是四种结论：
raw 计数 → 按里程归一 → 再按“知悉比例”修正 → 再按运行设计域难度归一，
排名两次整个翻过来。（b）把其中一个没人公布的数（知悉比例）扫一遍，
名次随它上下移动——**结论取决于一个你拿不到的数**。

**本图不使用任何真实厂家的数据，也不代表任何真实运营方。** 它配合的是监管方自己写下的
三句局限：数据“未按任何暴露量归一”、“不应被当作全部事故的统计代表”、
“比较各方的事故数据时要当心”。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---- 三家虚构运营方的“真实”情况（合成，仅用于演示口径）
OPS = [
    # 名称, 里程（百万英里）, 每百万英里的真实事件数（按它实际跑的路算）, 知悉比例, 运行设计域难度
    ("A", 12.0, 6.0, 0.95, 0.6),
    ("B", 3.0, 9.0, 0.60, 1.0),
    ("C", 0.6, 14.0, 0.25, 1.8),
]
names = [o[0] for o in OPS]
miles = np.array([o[1] for o in OPS])
true_rate = np.array([o[2] for o in OPS])
known = np.array([o[3] for o in OPS])
odd = np.array([o[4] for o in OPS])

reported = np.round(true_rate * miles * known)            # 上报的事件数：唯一公开的那一列
per_mile = reported / miles                               # 口径二：按里程归一
corrected = per_mile / known                              # 口径三：再按知悉比例修正
odd_norm = corrected / odd                                # 口径四：再按运行设计域难度归一

cols = [reported, per_mile, corrected, odd_norm]
titles = [T("上报事件数\n（唯一公开的一列）", "reported\ncount"),
          T("每百万英里\n（按里程归一）", "per million\nmiles"),
          T("再按知悉比例修正\n（没人公布这个数）", "÷ share\nknown"),
          T("再按运行设计域难度归一\n（也没人公布）", "÷ ODD\ndifficulty")]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.5))

# ---------------- (a) 同一套数，四种口径，四个结论
xs = np.arange(len(cols))
bar_c = [C["x"], C["z"], C["y"]]
width = 0.26
for i, nm in enumerate(names):
    vals = np.array([c[i] / c.max() for c in cols])       # 每一列各自归一，只看相对高低
    a.bar(xs + (i - 1) * width, vals, width, color=bar_c[i],
          label=T(f"运营方 {nm}", f"operator {nm}"))
    for j, vv in enumerate(vals):
        a.annotate(f"{cols[j][i]:.1f}" if j else f"{cols[j][i]:.0f}",
                   xy=(j + (i - 1) * width, vv), xytext=(0, 3),
                   textcoords="offset points", ha="center", fontsize=7.8, color=bar_c[i])
for j, c in enumerate(cols):
    worst = names[int(np.argmax(c))]
    a.annotate(T(f"看上去最差：{worst}", f"looks worst: {worst}"),
               xy=(j, 1.14), ha="center", fontsize=8.5, color=C["accent"])
a.set_xticks(xs)
a.set_xticklabels(titles, fontsize=8.2)
a.set_ylabel(T("该列内的相对高低（各列各自归一）", "relative height in each column"))
a.set_ylim(0, 1.32)
a.set_title(T("(a) 同一套上报数，四种口径，三个不同的“最差”",
              "(a) one set of reports, four conventions, three different “worst”"),
            fontsize=10)
a.legend(fontsize=8.5, loc="upper left", framealpha=0.92, ncol=3)
a.grid(alpha=0.25, lw=0.5, axis="y")

# ---------------- (b) 名次取决于一个拿不到的数
share = np.linspace(0.15, 1.0, 120)
for i, nm in enumerate(names):
    if nm == "C":
        est = (reported[i] / miles[i]) / share / odd[i]
        b.plot(share, est, color=bar_c[i], lw=2.4,
               label=T(f"运营方 {nm}（知悉比例未知）",
                       f"operator {nm} (share known is unknown)"))
    else:
        est = (reported[i] / miles[i]) / known[i] / odd[i]
        b.axhline(est, color=bar_c[i], lw=1.9, ls="--",
                  label=T(f"运营方 {nm}（按各自已知口径）",
                          f"operator {nm} (its own stated convention)"))
for i in (0, 1):
    line = (reported[i] / miles[i]) / known[i] / odd[i]
    cross = (reported[2] / miles[2]) / odd[2] / line
    if share.min() < cross < share.max():
        b.plot([cross], [line], "o", color=C["ink"], ms=7)
        b.annotate(T(f"在这里与 {names[i]} 打平：{cross:.0%}",
                     f"ties with {names[i]} at {cross:.0%}"),
                   xy=(cross, line), xytext=(16, 22) if i == 0 else (16, -26),
                   textcoords="offset points",
                   fontsize=8.5, color=C["ink"],
                   arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1.0))
b.set_xlabel(T("运营方 C 到底知道自己多少起事故（没人公布这个数）",
               "share of C’s own crashes it knows about (never published)"))
b.set_ylabel(T("折算后的事件率（每百万英里，已按难度归一）",
               "adjusted rate (per million miles)"))
b.set_title(T("(b) 名次随一个拿不到的数上下移动",
              "(b) the ranking slides with a number you cannot obtain"), fontsize=10)
b.set_ylim(0, 30)
b.legend(fontsize=8, loc="upper right", framealpha=0.92)
b.annotate(T("同一套公开数字，换一个没人公布的假设，\n"
             "“谁更安全”的答案就变了——所以这类数不作横向比较",
             "the same public numbers plus one unpublished assumption\n"
             "change who is “safer”; so these numbers are not compared across entities"),
           xy=(0.56, 0.63), xycoords="axes fraction", ha="center", va="center",
           fontsize=8.2, color=C["accent"])
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig23_7_1")
