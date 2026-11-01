"""8.2 拉压、剪切与挤压：WQR-105 齿轮键（SH-301 B 版，Ø40 齿轮位，平键 12 × 8 × 45，GB/T 1096）在额定转矩、跑合试验台的
起动峰值和矿山现场一年中的最大转矩下的剪切应力和挤压应力（挤压高度按 h/2 和按 h − t 两种算法，第 33 章）；
地脚螺栓（M12，第 7 章的力）的拉应力（算例 8.2.1、8.2.2，图 8.2.1）。
键：A 型（圆头），工作长度 l = L − b；剪切面积 b·l，挤压面积 k·l。"""
import math
import sys
from pathlib import Path

import _ch8 as H
import _shaft as S
import mdstd
from bookout import T, figure, out, style

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ch07" / "code"))
import _ch7 as C7                     # noqa: E402  跑合试验台记录、数字孪生现场、减速器模型

d = 40.0
K = mdstd.key_for(d)
b, h, t = K["b"], K["h"], K["t"]
L = S.L_KEY_GEAR
l = L - b
_, yb, _ = C7.bench()
mine = C7.site_year("mine")
TQ = [(T("额定", "rated"), C7.RATED), (T("试验台起动峰值", "bench start peak"), max(yb)),
      (T("矿山现场一年最大", "mine site, yearly max"), max(x.get("torque_max_nm", 0) for x in mine))]
P_ALLOW = S.SIGMA_P_ALLOW
rows = []
for name, Tq in TQ:
    Tn = Tq * 1e3
    tau = 2 * Tn / (d * b * l)
    sp_half = 4 * Tn / (d * h * l)                   # k = h/2
    sp_exact = 2 * Tn / (d * (h - t) * l)            # k = h − t（毂一侧实际的挤压高度）
    rows.append((name, Tq, tau, sp_half, sp_exact))
# 地脚螺栓：第 7 章的反力偶 / (2 × 450 mm)，M12 的应力截面积 84.3 mm²（ISO 898-1）
Tq = C7.TM.torques(C7.RATED)
F_bolt = (Tq["out"] - Tq["in"]) * 1e3 / (2 * 450.0)
AS_M12 = 84.3
sig_bolt = F_bolt / AS_M12

plt = style()
fig, ax = plt.subplots(figsize=(6.4, 3.0))
import numpy as np
x = np.arange(len(rows))
w = 0.26
ax.bar(x - w, [r[2] for r in rows], w, color="#1f77b4", label=T("键的剪切应力 τ", "key shear stress τ"))
ax.bar(x, [r[3] for r in rows], w, color="#ff7f0e", label=T("挤压应力（k = h/2）", "bearing stress (k = h/2)"))
ax.bar(x + w, [r[4] for r in rows], w, color="#d62728", label=T("挤压应力（k = h − t）", "bearing stress (k = h − t)"))
ax.axhline(P_ALLOW, color=H.MUTED, lw=0.8, ls="--")
ax.text(x[0] - 0.45, P_ALLOW + 6, T(f"许用挤压应力 {P_ALLOW:.0f} MPa", f"allowable bearing {P_ALLOW:.0f} MPa"), fontsize=6.4, color=H.MUTED, ha="left")
ax.set_xticks(x)
ax.set_xticklabels([f"{r[0]}\n{r[1]:.0f} N·m" for r in rows], fontsize=6.6)
ax.set_ylabel(T("应力 / MPa", "Stress / MPa"), fontsize=7.4)
ax.legend(fontsize=6.4, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.98))
ax.set_ylim(0, max(r[4] for r in rows) * 1.15)
ax.tick_params(labelsize=6.4)
ax.set_title(T(f"齿轮键 {b}×{h}×{L:.0f}（Ø{d:.0f}）的剪切与挤压", f"Shear and bearing of the gear key {b}×{h}×{L:.0f} (Ø{d:.0f})"), fontsize=7.6)
fig.tight_layout()
figure(fig, "fig8_2_1")

o = {}
for k, r in zip(("rated", "bench", "mine"), rows):
    o.update({f"T_{k}": r[1], f"tau_{k}": r[2], f"sph_{k}": r[3], f"spe_{k}": r[4]})
out(d=d, b=b, h=h, t=t, L=L, l=l, p_allow=P_ALLOW, F_bolt=F_bolt, As=AS_M12, sig_bolt=sig_bolt, ratio_k=h / 2 / (h - t), **o)
