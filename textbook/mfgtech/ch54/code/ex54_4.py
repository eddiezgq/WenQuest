"""算例 54.4.1–54.4.4：工艺系统的受力变形（hub/accuracy.py）。
54.4.1：SH-301 工序 40 精车（两顶尖，L = 167），切深 0.3、进给 0.15，主切削力与背向力（kienzle_turning，45 钢的单位切削力按第 35 章取）；
        头架、尾座刚度各 20000 N/mm、刀架 50000 N/mm，工件 Ø40：沿轴向的让刀量与车出的形状（profile_between_centers）；
54.4.2：同一台车床车 Ø20 × 500 的细长轴：鼓形；改用跟刀架；尾座刚度只有头架的一半：锥形；
54.4.3：误差复映——毛坯有 0.5 mm 的偏心（直径上的径向跳动 1 mm），粗车、半精车、精车三次走刀各自的复映系数与车后的误差（reflection、passes_needed）；
54.4.4：生产法（误差复映法）测刚度——毛坯上车出切深差 1 mm 的台阶，一次走刀后工件上剩下的台阶（stiffness_from_steps）。
画图 54.4.2（让刀量沿轴向的组成）、54.4.4（误差复映）。"""
import math

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
L = 167.0
kh, kt, kk = 20000.0, 20000.0, 50000.0
f40 = A.kienzle_turning(0.3, 0.15)
Fp = f40["Fp"]
sh = A.profile_between_centers(Fp, L, 40.0, kh, kt, kk)
c_mid = A.compliance_between_centers(L / 2, L, 40.0, kh, kt, kk)
c_end = A.compliance_between_centers(0.0, L, 40.0, kh, kt, kk)
assert sh["label"] == "saddle"
# 54.4.2：细长轴、跟刀架、尾座软
Ls = 500.0
f2 = A.kienzle_turning(0.5, 0.2)
slender = A.profile_between_centers(f2["Fp"], Ls, 20.0, kh, kt, kk)
rest = A.profile_between_centers(f2["Fp"], Ls, 20.0, kh, kt, kk, rest=True)
soft = A.profile_between_centers(Fp, L, 40.0, kh, kh / 4, kk)
assert slender["label"] == "drum" and soft["label"] == "taper" and soft["dd"][-1] > soft["dd"][0]
# 54.4.3：误差复映
k_sys = 1 / c_mid["total"]
passes = [("粗车", 2.0, 0.4), ("半精车", 0.8, 0.25), ("精车", 0.3, 0.15)]
eps, e_now, rows = [], 1.0, []                  # 毛坯直径上的跳动 1 mm（偏心 0.5）
for name, ap, f in passes:
    C = A.kienzle_turning(ap, f)["C"]
    ep = A.reflection(C, k_sys)
    e_now *= ep
    eps.append(ep)
    rows.append((name, ap, f, C, ep, e_now))
n_need = A.passes_needed(1.0, 0.01, eps)
# 54.4.4：生产法测刚度
C1 = A.kienzle_turning(1.0, 0.2)["C"]
d_work = 0.0125                                  # 一次走刀后工件上剩下的台阶（半径，实测示例）
k_meas = A.stiffness_from_steps(C1, 1.0, d_work)

plt = style()
# ---- 图 54.4.2：让刀量沿轴向的组成（两种情况）
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.2))
for ax, (LL, d, FF, ttl) in zip(axs, ((L, 40.0, Fp, T("(a) SH-301 精车：Ø40 × 167（工件刚，头尾架软）", "(a) SH-301 finish turning: Ø40 × 167")),
                                     (Ls, 20.0, f2["Fp"], T("(b) 细长轴：Ø20 × 500（工件软）", "(b) slender shaft: Ø20 × 500")))):
    xs = [LL * i / 60 for i in range(61)]
    cc = [A.compliance_between_centers(x, LL, d, kh, kt, kk) for x in xs]
    for key, col, lab in (("head", M.ACCENT, T("头架", "headstock")), ("tail", M.WARM, T("尾座", "tailstock")),
                          ("work", M.GREEN, T("工件弯曲", "work bending")), ("tool", M.MUTED, T("刀架", "tool post")), ("total", M.RED, T("合计", "total"))):
        ax.plot(xs, [FF * c[key] * 1000 for c in cc], color=col, lw=2.0 if key == "total" else 1.0, label=lab)
    ax.set_xlabel(T("刀具位置 x（距头架）/ mm", "tool position x (from headstock) / mm"))
    ax.set_ylabel(T("让刀量 y / µm", "deflection y / µm"))
    ax.set_title(ttl, fontsize=8.2); ax.grid(lw=0.3, alpha=0.5)
axs[0].legend(fontsize=7, loc="upper center", ncol=2)
figure(fig, "fig54_4_2")

# ---- 图 54.4.4：误差复映
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1, 1.3]})
ax = axs[0]
th = [2 * math.pi * i / 200 for i in range(201)]
e0 = 0.35
ax.plot([math.cos(t) + e0 for t in th], [math.sin(t) for t in th], color=M.MUTED, lw=1.2, ls="--")
ax.plot([0.7 * math.cos(t) for t in th], [0.7 * math.sin(t) for t in th], color=M.INK, lw=0.6, ls=":")
ax.plot([0.75 * math.cos(t) + e0 * 0.3 for t in th], [0.75 * math.sin(t) for t in th], color=M.RED, lw=1.3)
ax.plot([0], [0], "k+", ms=8)
ax.annotate("", xy=(1.0 + e0, 0), xytext=(-1.0 + e0, 0), arrowprops=dict(arrowstyle="-", color=M.MUTED, lw=0.4))
ax.text(-0.95, 1.05, T("毛坯（偏心）", "blank (eccentric)"), fontsize=7.5, color=M.MUTED)
ax.text(0.05, -0.32, T("车后：偏心变小，\n但没有消失", "after: smaller,\nbut not gone"), fontsize=7.5, color=M.RED)
ax.text(-1.05, -1.25, T("切深大处背向力大、让刀多", "deeper cut → larger force → more deflection"), fontsize=7, color=M.INK)
ax.set_aspect("equal"); ax.set_xlim(-1.1, 1.5); ax.set_ylim(-1.35, 1.25); ax.axis("off")
ax.set_title(T("(a) 毛坯误差复映到工件上（示意）", "(a) the blank's error reflected (schematic)"), fontsize=8.5)
ax = axs[1]
names = [T("毛坯", "blank")] + [T(r[0], {"粗车": "rough", "半精车": "semi-finish", "精车": "finish"}[r[0]]) for r in rows]
vals = [1.0] + [r[5] for r in rows]
ax.semilogy(range(4), [v * 1000 for v in vals], "o-", color=M.RED)
for i, v in enumerate(vals):
    ax.text(i, v * 1000 * 2.2, (f"{v * 1000:.0f}" if v * 1000 >= 10 else f"{v * 1000:.2g}") + " µm", ha="center", fontsize=7.5)
for i, r in enumerate(rows):
    ax.text(i + 0.5, math.sqrt(vals[i] * vals[i + 1]) * 1000, f"ε = {r[4]:.3f}", fontsize=7, color=M.ACCENT, ha="center")
ax.axhline(10, color=M.MUTED, ls="--", lw=0.8)
ax.text(3.3, 12, T("10 µm", "10 µm"), fontsize=7, color=M.MUTED)
ax.set_xticks(range(4)); ax.set_xticklabels(names)
ax.set_ylabel(T("直径上的跳动 / µm", "runout on diameter / µm")); ax.set_ylim(1e-3, 1e4); ax.grid(lw=0.3, alpha=0.5, which="both")
ax.set_title(T("(b) 三次走刀后的误差（k = {:.0f} N/mm）".format(k_sys), "(b) error after three passes (k = {:.0f} N/mm)".format(k_sys)), fontsize=8.5)
figure(fig, "fig54_4_4")

out(Fc=f40["Fc"], Fp=Fp, kh=kh, kt=kt, kk=kk, y_mid_um=Fp * c_mid["total"] * 1000, y_end_um=Fp * c_end["total"] * 1000,
    sh_crown_um=sh["crown"] * 1000, sh_range_um=sh["range"] * 1000, sl_crown_um=(slender["dd"][20] - slender["dd"][0]) * 1000, sl_Fp=f2["Fp"],
    rest_range_um=rest["range"] * 1000, soft_taper_um=soft["taper"] * 1000, k_sys=k_sys,
    C_r=rows[0][3], C_s=rows[1][3], C_f=rows[2][3], eps_r=rows[0][4], eps_s=rows[1][4], eps_f=rows[2][4],
    e_r_um=rows[0][5] * 1000, e_s_um=rows[1][5] * 1000, e_f_um=rows[2][5] * 1000, eps_total=rows[2][5], n_need=n_need,
    C1=C1, d_work=d_work, k_meas=k_meas, work_mid_um=Fp * c_mid["work"] * 1000, head_mid_um=Fp * c_mid["head"] * 1000)
