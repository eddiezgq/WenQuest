"""本章提要：本章的问题——仿真车间一个班次磨 60 件 SH-301，第 31 件起老师注入“磨床尾座偏移”（学生不知道）。
图 54.0.1：左、右轴承位直径逐件的测得值与公差带；超差件标红。数据来自仿真车间的误差模型（factory/digital/sim/errors.py），
与数字工厂质量页的数据（第 54.8 节的截图）是同一个模型。"""
import statistics as st

import _mfg as M
from bookout import T, figure, out, style

s = M.shift()
v = s["values"]
L, Rr = v["bearing_seat_d35"], v["bearing_seat_d35_r"]
n, k = len(L), s["start"]
lo, hi = 35.002, 35.018
fails = [i for i, x in enumerate(Rr) if x > hi or x < lo]
fails_l = [i for i, x in enumerate(L) if x > hi or x < lo]
assert not fails_l and fails and min(fails) >= k, "左轴承位应全部合格、右轴承位的超差件都在注入问题以后"

plt = style()
fig, ax = plt.subplots(figsize=(7.4, 3.3))
xs = list(range(1, n + 1))
ax.axvspan(k + 0.5, n + 0.5, color="#f6e7e5", zorder=0)
ax.text(k + 1, hi + 0.0026, T("第 31 件起（这时还不知道原因）", "from part 31 (cause not yet known)"), fontsize=8, color=M.RED)
for y in (lo, hi):
    ax.axhline(y, color=M.RED, lw=0.8, ls="--")
ax.axhline((lo + hi) / 2, color=M.MUTED, lw=0.6)
ax.plot(xs, L, "o-", ms=3, lw=0.9, color=M.ACCENT, label=T("左轴承位 Ø35 k6", "left bearing seat Ø35 k6"))
ax.plot(xs, Rr, "s-", ms=3, lw=0.9, color=M.WARM, label=T("右轴承位 Ø35 k6", "right bearing seat Ø35 k6"))
ax.plot([i + 1 for i in fails], [Rr[i] for i in fails], "s", ms=6, mfc="none", mec=M.RED, mew=1.4, label=T("超差", "out of tolerance"))
for r in s["resets"]:
    if r != k:
        ax.axvline(r + 0.5, color=M.MUTED, lw=0.5, ls=":")
ax.text(10.6, lo + 0.0008, T("点线：修整砂轮", "dotted: wheel dressed"), fontsize=7.5, color=M.MUTED)
ax.set_xlabel(T("零件序号（加工顺序）", "part number (in order)"))
ax.set_ylabel(T("直径 / mm", "diameter / mm"))
ax.set_ylim(lo - 0.002, hi + 0.004)
ax.set_xlim(0, n + 1)
ax.legend(fontsize=7.5, ncol=3, loc="lower left", bbox_to_anchor=(0.0, 1.0), frameon=False)
figure(fig, "fig54_0_1")

out(n=n, start=k + 1, n_fail=len(fails),
    dl_um=1000 * (st.fmean(L[k:]) - st.fmean(L[:k])), dr_um=1000 * (st.fmean(Rr[k:]) - st.fmean(Rr[:k])),
    gap_um=1000 * (st.fmean(Rr[k:]) - st.fmean(L[k:])))
