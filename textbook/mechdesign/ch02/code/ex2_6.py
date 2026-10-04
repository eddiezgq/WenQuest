"""2.6 参数化产品族：WQR-105 两级中心距不变、换齿数组合得到 16 种传动比；用数字工厂参数配置器的同一个函数，
算出每种传动比在 1450 r/min、工况系数 1.25 下允许的最大输入功率（算例 2.6.1，图 2.6.1）。"""
import math

import numpy as np

import _ch2 as H
from bookout import T, figure, out, style

C = H.C
R20 = [1.00, 1.12, 1.25, 1.40, 1.60, 1.80, 2.00, 2.24, 2.50, 2.80, 3.15, 3.55, 4.00, 4.50, 5.00, 5.60, 6.30, 7.10, 8.00, 9.00,
       10.0, 11.2, 12.5, 14.0, 16.0, 18.0, 20.0]       # 优先数系 R20 的常用值（GB/T 321，圆整后）
powers = np.round(np.arange(0.37, 11.0001, 0.01), 2)
rows = []
for r in C.ratios():
    best, why = None, ""
    for p in powers:
        ev = C._wqr_eval({"ratio": r["key"], "power_kw": float(p), "n1": 1450, "ka": 1.25, "life_h": 10000}, 1)
        if ev["ok"]:                                   # 与配置器相同：错误才不可用，轴承寿命不足只是警告
            best = float(p)
        else:
            why = ev["errors"][0]
            break
    near = min(R20, key=lambda x: abs(math.log(x / r["i"])))
    rows.append({"key": r["key"], "i": r["i"], "z": r["z"], "p_max": best, "limit": "转矩" if "转矩" in why else ("键" if "键" in why else "寿命"),
                 "r20": near, "dev": (r["i"] / near - 1) * 100})
rows.sort(key=lambda x: x["i"])
std = next(x for x in rows if x["z"] == [24, 72, 20, 70])
dev_max = max(abs(x["dev"]) for x in rows)
k3 = min(range(len(rows) - 2), key=lambda k: rows[k + 2]["i"] / rows[k]["i"])   # 挤得最紧的三个相邻传动比
crowd = "、".join("{:g}".format(x["i"]) for x in rows[k3:k3 + 3])

plt = style()
fig, ax = plt.subplots(figsize=(6.8, 3.2))
for k, x in enumerate(rows):
    ax.bar(k, x["p_max"], color="#2c6fbb", width=0.7, edgecolor="#1d2327" if x is std else "none", lw=1.4)
ax2 = ax.twinx()
ax2.plot(range(len(rows)), [1450 / x["i"] for x in rows], "o-", color="#b8860b", ms=3.5, lw=1.2)
ax2.set_ylabel(T("输出转速 / (r/min)", "output speed / (r/min)"), color="#b8860b", fontsize=9)
ax.set_xticks(range(len(rows)))
ax.set_xticklabels(["{:g}".format(x["i"]) for x in rows], rotation=60, fontsize=7.5)
ax.set_xlabel(T("传动比 i（加框的为标准型 10.5）", "ratio i (framed: standard 10.5)"))
ax.set_ylabel(T("允许的最大输入功率 / kW", "max input power / kW"), color="#2c6fbb")
lim = {"转矩": T("额定输出转矩", "the rated output torque"), "键": T("平键", "the key"), "寿命": T("轴承寿命", "bearing life")}
ax.text(len(rows) - 0.5, max(x["p_max"] for x in rows) * 0.97, T("全部受", "all limited by ") + "、".join(sorted({lim[x["limit"]] for x in rows})) + T("限制", ""),
        ha="right", va="top", fontsize=8)
for a_ in (ax, ax2):
    a_.spines["top"].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_6_1")

out(n_ratio=len(rows), i_min=rows[0]["i"], i_max=rows[-1]["i"], p_std=std["p_max"], i_std=std["i"], p_lo=rows[0]["p_max"], p_hi=rows[-1]["p_max"],
    n_torque=sum(x["limit"] == "转矩" for x in rows), n_life_warn=sum(1 for x in rows if C._wqr_eval({"ratio": x["key"], "power_kw": x["p_max"], "n1": 1450, "ka": 1.25, "life_h": 10000}, 1)["warnings"]),
    key_util=4000 * C.T_RATED / (C.KEY["d"] * C.KEY["h"] * (C.KEY["l"] - C.KEY["b"])) / C.KEY["sigma"] * 100, dev_max=dev_max, crowd=crowd, a1=C.A1, a2=C.A2, m1=C.M1, m2=C.M2, T_rated=C.T_RATED,
    sum1=sum(C.STAGE1[0]), sum2=sum(C.STAGE2[0]))
