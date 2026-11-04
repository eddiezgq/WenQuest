"""算例 57.1.1、57.1.2：SH-101 的最小余量（分析计算法，式 57.1.3）与棒料直径。
57.1.1 三次切削的最小余量各由什么组成：热轧圆钢 → 粗车、粗车 → 半精车、半精车 + 渗碳淬火 → 磨削（企业工艺标准 WQ-PS-01，示意值）；
57.1.2 由齿顶圆 Ø52 推出需要的棒料直径，与工厂现用的 Ø60 比较（多用的材料与粗车工时）。画图 57.1.2、57.1.5。"""
import math

import _calc57 as C
import _mfg as M
from bookout import T, figure, out, style

KEYS = [("热轧圆钢", T("棒料 → 粗车", "bar → rough"), C.EPS_CHUCK), ("粗车", T("粗车 → 半精车", "rough → semi"), 0.0),
        ("半精车后渗碳淬火", T("半精车、渗碳淬火 → 磨", "semi + hardening → grind"), 0.0)]
comp = []
for k, lab, eps in KEYS:
    rz, ha, rho, _ = C.WQ_PS_01[k]
    comp.append({"lab": lab, "rz": 2 * rz, "ha": 2 * ha, "geo": 2 * math.sqrt(rho ** 2 + eps ** 2), "z": C.zmin(rz, ha, rho, eps)})
bar = C.bar_diameter()
P = M.plan101()
rho_steel = 7.85e-6
L = P["blank"]["length_mm"]
m60 = math.pi / 4 * 60 ** 2 * L * rho_steel
m_pick = math.pi / 4 * bar["pick"] ** 2 * L * rho_steel
price = M.F.ITEMS["RM-20CR-D60"][3]

plt = style()
fig, ax = plt.subplots(figsize=(6.2, 2.4))
ys = range(len(comp))[::-1]
for y, c in zip(ys, comp):
    l = 0
    for key, col, nm in (("rz", M.MUTED, T("2Rz", "2Rz")), ("ha", M.WARM, T("2Hₐ 缺陷层", "2Hₐ defect layer")), ("geo", M.ACCENT, T("2√(ρ²+ε²) 空间偏差与装夹", "2√(ρ²+ε²) form & set-up"))):
        ax.barh(y, c[key], left=l, color=col, height=0.55, label=nm if y == ys[0] else None)
        l += c[key]
    ax.text(l + 0.03, y, f"2Z_min = {c['z']:.3f} mm", va="center", fontsize=7.5)
ax.set_yticks(list(ys)); ax.set_yticklabels([c["lab"] for c in comp], fontsize=7.5)
ax.set_xlim(0, 2.4); ax.set_xlabel(T("直径上的最小余量 / mm", "minimum stock on diameter / mm"))
ax.legend(fontsize=6.8, loc="lower right"); ax.grid(lw=0.3, alpha=0.5, axis="x")
figure(fig, "fig57_1_2")

fig, ax = plt.subplots(figsize=(6.2, 2.3))
parts = [(52.0, T("齿顶圆 Ø52", "tip Ø52"), M.INK), (1.5, T("精车余量 1.5", "finish 1.5"), M.ACCENT),
         (bar["z1"], T(f"毛坯最小余量 {bar['z1']:.2f}", f"bar min stock {bar['z1']:.2f}"), M.WARM)]
l = 0
POS = {1: (52.75, 1.36, "center"), 2: (53.6, 1.58, "center")}
for k, (w, lab, col) in enumerate(parts):
    ax.barh(1, w, left=l, color=col, height=0.5, clip_on=True)
    if k:
        x, y, ha = POS[k]
        ax.text(x, y, lab, ha=ha, fontsize=6.8, color=col)
    l += w
ax.text(50, 1, T("齿顶圆 Ø52", "tip Ø52"), ha="center", va="center", fontsize=7.5, color="white")
for d, col, lab in ((bar["pick"], M.GREEN, T(f"够用的圆钢 Ø{bar['pick']}", f"enough: Ø{bar['pick']}")), (60, M.RED, T("工厂现用 Ø60", "in stock: Ø60"))):
    ax.barh(0 if d == 60 else 0.45, d, color=col, height=0.3, alpha=0.35)
    ax.text(d + 0.3, 0 if d == 60 else 0.45, lab, va="center", fontsize=7, color=col)
ax.barh(0.45, -bar["bar_ei"], left=bar["pick_min"], color=M.GREEN, height=0.3, alpha=0.7)
ax.text(bar["pick_min"] - 0.35, 0.45, T(f"下偏差 −{-bar['bar_ei']:g} → 最小 {bar['pick_min']:g}", f"lower dev. {bar['bar_ei']:g} → min {bar['pick_min']:g}"),
        ha="right", va="center", fontsize=6.5, color=M.INK)
ax.set_xlim(48, 64); ax.set_ylim(-0.3, 1.8); ax.set_yticks([]); ax.set_xlabel(T("直径 / mm", "diameter / mm"))
ax.axvline(bar["need"], color=M.INK, ls="--", lw=0.7); ax.text(bar["need"] + 0.15, 0.72, f"≥ {bar['need']:.2f}", ha="left", fontsize=7)
figure(fig, "fig57_1_5")

out(**{f"z_{i}": c["z"] for i, c in enumerate(comp)}, **{f"geo_{i}": c["geo"] for i, c in enumerate(comp)},
    rz_rough=C.WQ_PS_01["粗车"][0], ha_rough=C.WQ_PS_01["粗车"][1], rho_rough=C.WQ_PS_01["粗车"][2],
    rz_semi=C.WQ_PS_01["半精车后渗碳淬火"][0], ha_semi=C.WQ_PS_01["半精车后渗碳淬火"][1], rho_semi=C.WQ_PS_01["半精车后渗碳淬火"][2],
    rz_bar=C.WQ_PS_01["热轧圆钢"][0], ha_bar=C.WQ_PS_01["热轧圆钢"][1], rho_bar=C.WQ_PS_01["热轧圆钢"][2], eps_chuck=C.EPS_CHUCK,
    bar_need=bar["need"], bar_pick=bar["pick"], bar_ei=bar["bar_ei"], bar_pick_min=bar["pick_min"], bar_z1=bar["z1"], m60=m60, m_pick=m_pick, save_kg=m60 - m_pick,
    save_cny=(m60 - m_pick) * price, save_year=(m60 - m_pick) * price * 6000, price=price)
