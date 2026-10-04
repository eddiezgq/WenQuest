"""1.4 设计的约束：SH-301 外伸段（装联轴器的一段）直径 d 的可行范围（算例 1.4.1，图 1.4.1）。
下限来自强度（起动峰值转矩下不屈服，计入键槽），上限来自几何（右轴承 6207 的内径与定位轴肩），零件库的联轴器
LM 系列给出一个范围，标准直径系列给出可选的值。各约束的数据都取自数字工厂与零件库。"""
import _ch1 as H
from bookout import T, figure, out, style

from _con import *  # noqa: F401,F403  约束的计算（与 1.5 节共用）
from _con import WT_key, rec  # noqa: F401

# ---------------------------------------------------------------- 图 1.4.1
plt = style()
fig, ax = plt.subplots(figsize=(6.8, 2.7))
rowsY = [(3, T("强度：起动峰值下不屈服（含键槽）", "strength: no yield at the start peak (with keyway)"), d_strength, 46, "#2c6fbb"),
         (2, T("联轴器 {} 的孔径范围".format(cpl["size"]), "bore range of coupling {}".format(cpl["size"])), cpl_lo, cpl_hi, "#8e44ad"),
         (1, T("轴承 6207 与定位轴肩", "bearing 6207 and its locating shoulder"), 19, d_geom, "#b8860b")]
for y, lab, a, b, col in rowsY:
    ax.barh(y, b - a, left=a, height=0.45, color=col, alpha=0.35, lw=0)
    ax.text(19.6, y + 0.32, lab, fontsize=7.5, color=col, va="bottom")
ax.axvspan(lo, hi, color="#2ca02c", alpha=0.15, lw=0)
ax.text((lo + hi) / 2, 0.15, T("可行", "feasible"), ha="center", fontsize=8, color="#2ca02c")
for x in R40:
    ax.plot([x, x], [-0.35, -0.1], color=H.INK, lw=0.8)
ax.text(19.6, -0.75, T("标准直径（R40）", "standard diameters (R40)"), fontsize=7.5, color=H.MUTED)
if d_pick:
    ax.plot([d_pick], [-0.22], "v", color="#c0392b", ms=8)
    ax.text(d_pick, -0.75, "Ø{:g}".format(d_pick), ha="center", fontsize=8, color="#c0392b")
ax.set_xlim(19.5, 46)
ax.set_ylim(-1.0, 3.9)
ax.set_yticks([])
ax.set_xlabel(T("外伸段直径 d / mm", "extension diameter d / mm"))
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig1_4_1")

out(T_R=T_R, K_peak=K_PEAK, T_peak=T_PEAK, sigma_s=mat["sigma_s"], tau_s=tau_s, S_req=S_REQ, d_strength=d_strength,
    cpl=cpl["size"], cpl_T=float(cpl["Tn_a_Nm"]), cpl_lo=cpl_lo, cpl_hi=cpl_hi, brg_d=brg["d"], d_geom=d_geom, lo=lo, hi=hi,
    d_pick=d_pick, S_pick=S_pick, m_ext=m_ext, n_choices=len(choices), width=hi - lo)
