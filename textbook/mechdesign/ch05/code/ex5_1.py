"""5.1 力学性能：几种材料的拉伸曲线（按国标最小值或材料库的值拟合的模型曲线），疲劳极限与抗拉强度之比（数字工厂材料库）。
算例 5.1.1、5.1.2，图 5.1.1。

拉伸曲线的模型：弹性段 σ = Eε；屈服后真应力按斯威夫特（Swift）式 σ = K(ε₀ + εp)ⁿ 强化，ε₀ 使曲线在屈服点连续；
n、K 由两个条件定出：工程应力的最大值等于抗拉强度 Rm，最大值处的工程应变（均匀伸长）取断后伸长率 A 的六成（本书设定）。
颈缩以后工程应力下降，到断后伸长率处断开（画成直线，示意）。低碳钢 Q235 另画一段约 1.5% 的屈服平台。"""
import math

import numpy as np
from scipy.optimize import brentq

import _ch5 as H
from bookout import T, figure, out, style

AG_RATIO = 0.6                       # 均匀伸长 / 断后伸长率（本书设定，示意用）
# (名称, E GPa, ReL, Rm, A%, 屈服平台, 来源)
CURVES = []
for g in H.steel_grades():
    E = H.lib(g["lib_id"])["E"]
    state = {"Q235": T("热轧", "hot rolled"), "45": T("正火", "normalized"), "40Cr": T("调质", "Q&T"), "20CrMnTi": T("淬火回火", "Q&T")}[g["grade"]]
    CURVES.append((T(f"{g['grade']}（{state}）", f"{g['grade']} ({state})"), E, g["ReL"], g["Rm"], g["A"], 0.015 if g["grade"] == "Q235" else 0.0, "GB"))
al = H.lib("6061-T6")
ss = H.lib("304")
CURVES.append(("6061-T6", al["E"], al["sy"], al["sb"], 10, 0.0, T("材料库；A 为典型值", "library; A typical")))
CURVES.append(("304", ss["E"], ss["sy"], ss["sb"], 40, 0.0, T("材料库；A 按 GB/T 1220", "library; A per GB/T 1220")))
CURVES = [c for c in CURVES if not c[0].startswith("20CrMnTi")]   # 渗碳钢的试样性能不代表零件表层，不画


def fit(E, sy, Rm, A, plateau):
    eu = AG_RATIO * A / 100                                  # 均匀伸长（工程应变）
    eps_u = math.log(1 + eu)                                 # 对应的真应变

    def resid(n):
        # 颈缩点：dσ/dε = σ → ε₀ + εp = n；真应变 = εp + σ/E + 平台
        K = Rm * math.exp(eps_u) / n ** n
        e0 = (sy / K) ** (1 / n)
        return (n - e0) + Rm * math.exp(eps_u) / (E * 1000) + plateau - eps_u

    n = brentq(resid, 0.02, 0.6)
    K = Rm * math.exp(eps_u) / n ** n
    return n, K, (sy / K) ** (1 / n), eu


def curve(E, sy, Rm, A, plateau):
    n, K, e0, eu = fit(E, sy, Rm, A, plateau)
    Em = E * 1000
    pts = [(0.0, 0.0), (sy / Em, sy)]
    if plateau:
        pts.append((sy / Em + plateau, sy))
    for ep in np.linspace(0, n - e0, 60)[1:]:
        st = K * (e0 + ep) ** n
        et = ep + st / Em + plateau
        e = math.exp(et) - 1
        pts.append((e, st / (1 + e)))
    eA = A / 100
    pts.append((eA, 0.82 * Rm))                              # 颈缩后到断裂（示意）
    return np.array(pts), n


plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.35, 1.0]})
cols = ["#7f7f7f", "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"]
ns = {}
for (name, E, sy, Rm, A, pl, src), c in zip(CURVES, cols):
    p, n = curve(E, sy, Rm, A, pl)
    ns[name] = n
    a0.plot(100 * p[:, 0], p[:, 1], color=c, lw=1.1, label=name)
    a0.plot(100 * p[-1, 0], p[-1, 1], "x", color=c, ms=4)
a0.set_xlabel(T("工程应变 / %", "Engineering strain / %"), fontsize=7.5)
a0.set_ylabel(T("工程应力 / MPa", "Engineering stress / MPa"), fontsize=7.5)
a0.set_xlim(0, 45)
a0.set_ylim(0, 1100)
a0.legend(fontsize=6.5, frameon=False)
a0.tick_params(labelsize=6.5)
a0.set_title(T("(a) 拉伸曲线（模型，按最小值拟合；× 为断裂）", "(a) Tensile curves (model fitted to minimum values; × = fracture)"), fontsize=7.8)

libs = ["Q235", "45-QT", "40Cr-QT", "20CrMnTi-CQ", "HT200", "QT500-7", "304", "6061-T6", "7075-T6", "ABS", "PA66"]
rat = [(H.lib(m)["name"].split("（")[0].split(" ")[0], H.lib(m)["s1"] / H.lib(m)["sb"], m) for m in libs]
y = range(len(rat))
KIND = {"Q235": "#1f77b4", "45-QT": "#1f77b4", "40Cr-QT": "#1f77b4", "20CrMnTi-CQ": "#1f77b4", "304": "#1f77b4",
        "HT200": "#8c564b", "QT500-7": "#8c564b", "6061-T6": "#2ca02c", "7075-T6": "#2ca02c", "ABS": "#ff7f0e", "PA66": "#ff7f0e"}
a1.barh(list(y), [r[1] for r in rat], color=[KIND[r[2]] for r in rat])
a1.set_yticks(list(y))
a1.set_yticklabels([r[0] for r in rat], fontsize=6.4)
a1.invert_yaxis()
a1.set_xlabel("σ₋₁ / σb", fontsize=7.5)
a1.axvline(0.45, color=H.MUTED, lw=0.6, ls="--")
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) σ₋₁/σb（材料库；蓝 钢，棕 铸铁，绿 铝，橙 塑料）", "(b) σ₋₁/σb (library; blue steel, brown iron,\ngreen Al, orange plastics)"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig5_1_1")

steel_r = [r[1] for r in rat if r[2] in ("Q235", "45-QT", "40Cr-QT", "20CrMnTi-CQ")]
al_r = [r[1] for r in rat if r[2] in ("6061-T6", "7075-T6")]
g45 = next(g for g in H.steel_grades() if g["grade"] == "45")
out(n_curves=len(CURVES), ag_ratio=AG_RATIO, n45=ns[[k for k in ns if k.startswith("45")][0]], n304=ns["304"], n40=ns[[k for k in ns if k.startswith("40Cr")][0]],
    r_steel_lo=min(steel_r), r_steel_hi=max(steel_r), r_al_lo=min(al_r), r_al_hi=max(al_r),
    r_ht=H.lib("HT200")["s1"] / H.lib("HT200")["sb"], r_pa=H.lib("PA66")["s1"] / H.lib("PA66")["sb"],
    E45=H.lib("45-QT")["E"], E_al=al["E"], E_ratio=H.lib("45-QT")["E"] / al["E"],
    Rm45=g45["Rm"], ReL45=g45["ReL"], A45=g45["A"], Z45=g45["Z"], KU45=g45["KU2"])
