"""52.8 节：算例 52.8.1——SH-301 铣键槽用找正装夹、组合夹具还是专用夹具：每件的装夹成本随年产量变化，求分界点。图 52.8.4。
费用与时间是教学示意值（机床加人工按每分钟 1.5 元计）。"""
import numpy as np

import _mfg as M
from bookout import T, figure, out, style

rate = 1.5                     # 元/min
batch = 50                     # 每批件数
opts = {
    # 名称: (夹具一次性费用 元, 每批的准备费用 元, 每批准备时间 min, 每件装夹找正时间 min)
    "find": (0.0, 0.0, 10.0, 8.0),          # 平口钳 + 千分表找正，每件找正
    "modular": (0.0, 200.0, 120.0, 2.5),    # 组合夹具：每批组装 2 h，元件折旧与管理 200 元/批
    "special": (6000.0, 0.0, 20.0, 1.5),    # 专用夹具 JJ-301-50：设计制造 6000 元，按 3 年摊销
}
years = 3


def per_part(key, N):
    C, Cb, tb, tp = opts[key]
    batches = np.ceil(N / batch)
    return (C / years + batches * (Cb + tb * rate)) / N + tp * rate


N = np.unique(np.round(np.logspace(0.7, 4.3, 600)))
cost = {k: per_part(k, N) for k in opts}


def cross(a, b):
    d = cost[a] - cost[b]
    i = np.where(np.diff(np.sign(d)) != 0)[0]
    return float(N[i[0] + 1]) if len(i) else None


N1 = cross("find", "modular")
N2 = cross("modular", "special")
N3 = cross("find", "special")
plt = style()
fig, ax = plt.subplots(figsize=(5.6, 2.8))
for k, col, lab in (("find", M.MUTED, T("找正装夹", "indicator set-up")), ("modular", M.ACCENT, T("组合夹具", "modular fixture")),
                    ("special", M.RED, T("专用夹具", "dedicated fixture"))):
    ax.plot(N, cost[k], color=col, lw=1.4, label=lab)
ax.set_xscale("log"); ax.set_ylim(0, 40)
ax.set_xlabel(T("年产量 / 件", "annual quantity / parts"), fontsize=8.5)
ax.set_ylabel(T("每件装夹成本 / 元", "fixturing cost per part / yuan"), fontsize=8.5)
ax.legend(fontsize=7.5, frameon=False)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
figure(fig, "fig52_8_4")
at = {k: float(per_part(k, np.array([2000]))[0]) for k in opts}
out(rate=rate, batch=batch, years=years, N1=N1, N2=N2, N3=N3, c_find=at["find"], c_mod=at["modular"], c_spec=at["special"],
    C_spec=opts["special"][0])
