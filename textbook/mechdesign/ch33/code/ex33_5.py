"""33.5 节：疲劳强度安全系数校核。

算例 33.5.1  截面 I–IV 的应力集中系数（轴肩：有限元；键槽：[SHI] 首轮估计）、缺口敏感系数、有效应力集中系数、
             尺寸系数、表面系数、综合影响系数；
算例 33.5.2  安全系数法（国内写法）与 [SHI] 修正古德曼法（冯·米塞斯合成）的结果；
算例 33.5.3  截面 IV 不够时的三种改法：换 40Cr 调质、加大外伸段直径、改为盘铣键槽；
图 33.5.2    截面 IV 的极限应力线图（τ_a–τ_m 平面）与工作点；图 33.5.3  各截面的安全系数。
"""
import math

import numpy as np

import _draw as D
import _fea
import _shaft as S
from bookout import T, figure, out, style
import mdstd

S_req = 1.5                               # 许用安全系数 [S]：材料均匀、载荷与应力计算较准确时取 1.3–1.5，本章取 1.5
mat = mdstd.material(S.MAT)
mat40 = mdstd.material("40Cr-QT")

alpha = {}
for k in ("II", "III"):
    sec = S.SECTIONS[k]
    r = _fea.stepped_bar_kt(sec["d"], sec["D"], sec["r"], fine=4)
    alpha[k] = (r["alpha_sigma"], r["alpha_tau"])

res = {}
for k, sec in S.SECTIONS.items():
    f = S.fatigue_factors(sec, mat, "ground", alpha.get(k))
    M, Tq = S.M_total(sec["z"]), S.torque_at(sec["z"])
    cn = S.safety(sec, mat, f, M, Tq)
    sg = S.shigley_goodman(sec, mat, f, M, Tq)
    res[k] = (f, cn, sg)

# ---- 算例 33.5.3：截面 IV 的改法
sec4 = S.SECTIONS["IV"]
T4 = S.torque_at(sec4["z"])
f40 = S.fatigue_factors(sec4, mat40, "ground")
c40 = S.safety(sec4, mat40, f40, 0.0, T4)
sec32 = dict(sec4, d=32)
f32 = S.fatigue_factors(sec32, mat, "ground")
c32 = S.safety(sec32, mat, f32, 0.0, T4)
sled = mdstd.kt_estimate("keyseat_sled")
# 起动冲击：跑合试验台记录的最大转矩按脉动循环作用时，截面 IV 的安全系数（说明为什么要做有限寿命计算）
series, _, rated = S.torque_series()
K_peak = float(series.max()) / rated
c_peak = S.safety(sec4, mat, res["IV"][0], 0.0, T4 * K_peak)
# 盘铣（滑橇形）键槽：[SHI] 只给弯曲的 1.7，扭转按端铣值的比例估计不可靠，这里只说明方向，不作定量结论

# ---- 图 33.5.2：截面 IV 的 τ_a–τ_m 极限线
f4, c4, _ = res["IV"]
plt = style()
fig, ax = plt.subplots(figsize=(6.4, 3.8))
for m_, f_, c_, col, name in ((mat, f4, c4, D.FORCE, T("45 钢调质", "45 steel, Q&T")),
                              (mat40, f40, c40, D.MOMENT, T("40Cr 调质", "40Cr, Q&T"))):
    tb = m_["sigma_b"] / math.sqrt(3)
    tA = m_["tau_1"] / f_["K_t"]                           # 零件的对称循环疲劳极限
    ax.plot([0, tb], [tA, 0], color=col, lw=1.6, label=name + T("：零件极限线", ": component limit"))
    ax.plot([0, tb / S_req], [tA / S_req, 0], color=col, lw=1.0, ls="--")   # 许用线：极限线按原点缩小 1/[S]
tm = c4["tau_a"]
ax.plot([0, 80], [0, 80], color=D.MUTED, lw=0.8, ls=":")
ax.text(84, 74, T("脉动循环 τ_a = τ_m", "repeated cycle τ_a = τ_m"), fontsize=8.5, color=D.MUTED, ha="left")
ax.plot([tm], [tm], "o", color=D.INK, ms=7)
ax.annotate(T(f"工作点（{tm:.0f}, {tm:.0f}）MPa", f"operating point ({tm:.0f}, {tm:.0f}) MPa"), (tm, tm), (tm + 30, tm + 22),
            fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.text(8, 8, T("虚线：除以 [S] = 1.5", "dashed: divided by [S] = 1.5"), fontsize=8.5, color=D.MUTED)
ax.set_xlabel(T("平均切应力 τ_m / MPa", "mean shear stress τ_m / MPa"))
ax.set_ylabel(T("切应力幅 τ_a / MPa", "shear stress amplitude τ_a / MPa"))
ax.set_xlim(0, 440)
ax.set_ylim(0, 80)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_5_2")

# ---- 图 33.5.3：各截面安全系数
fig, ax = plt.subplots(figsize=(6.0, 3.0))
ks = list(res)
x = np.arange(len(ks))
ax.bar(x - 0.18, [res[k][1]["S_ca"] for k in ks], 0.34, color=D.MOMENT, label=T("安全系数法 S_ca", "safety-factor method S_ca"))
ax.bar(x + 0.18, [res[k][2]["n"] for k in ks], 0.34, color=D.GEAR, label=T("[SHI] 修正古德曼 n", "[SHI] modified Goodman n"))
ax.axhline(S_req, color=D.FORCE, lw=1.2, ls="--")
ax.text(len(ks) - 0.5, S_req + 0.1, "[S] = 1.5", color=D.FORCE, fontsize=9, ha="right")
ax.set_xticks(x)
ax.set_xticklabels([f"{k}\n{T(S.SECTIONS[k]['what'][0], S.SECTIONS[k]['what'][1])}" for k in ks], fontsize=8)
ax.set_ylabel(T("安全系数", "factor of safety"))
ax.legend(fontsize=8.5, frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig33_5_3")

o = dict(S_req=S_req, sigma_1=mat["sigma_1"], tau_1=mat["tau_1"], sigma_b=mat["sigma_b"], tau_1_40=mat40["tau_1"],
         sigma_b_40=mat40["sigma_b"])
for k, (f, cn, sg) in res.items():
    for kk, vv in f.items():
        o[f"{kk}_{k}"] = vv
    for kk, vv in cn.items():
        if math.isfinite(vv):
            o[f"{kk}_{k}"] = vv
    for kk, vv in sg.items():
        o[f"{kk}_sg_{k}"] = vv
o.update(S40_IV=c40["S_ca"], K_t_40=f40["K_t"], q_t_40=f40["q_t"], S32_IV=c32["S_ca"], tau_32=c32["tau"],
         kt_sled=sled["Kt"], S_peak_IV=c_peak["S_ca"], K_peak=K_peak, T_peak=float(series.max()), worst=min(res, key=lambda k: res[k][1]["S_ca"]))
out(**o)
