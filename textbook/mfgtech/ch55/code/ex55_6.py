"""算例 55.6.1–55.6.3：表面完整性与疲劳（hub/surface.py，FKM 指南的做法；材料取 cae/materials.py）。
55.6.1：粗糙度系数 K_R：SH-301 轴承位磨削 Ra 0.8 与精车 Ra 3.2 时，45 钢的 K_R（Rz/Ra 由合成轮廓得到：磨削按细小进给加随机微观不平，
        车削按工序 40 的 f = 0.15、r = 0.4）；
        20CrMnTi（强度高）同样表面的 K_R；
55.6.2：SH-101 轴承位（20CrMnTi 渗碳淬火）的弯曲疲劳极限：正常磨削（表层残余压应力）、磨削烧伤（拉应力）；
55.6.3：同一应力幅下的寿命（Basquin，N_D = 10⁷，k = 9）：正常磨削、烧伤、烧伤后再喷丸。
画图 55.6.1（K_R 与 Rz）、55.6.2（疲劳极限与表层残余应力）、55.6.3（S–N 曲线）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
m45, m20 = S.STEELS["45-QT"], S.STEELS["20CrMnTi-CQ"]
mm = M.mats()
k_sn, n_d = mm.get("45-QT")["k"], mm.get("45-QT")["N_D"]
# Rz/Ra：用 55.2 节同一种合成轮廓（磨削表面按随机轮廓近似）
x, z = S.turned_profile(0.05, 0.8, vc_m_min=200, noise_um=0.5)
rr = S.roughness(x, z)
rz_ra = rr["Rz"] / rr["Ra"]
rz_g = 0.8 * rz_ra
xt, zt = S.turned_profile(0.15, 0.4, vc_m_min=150)
rt = S.roughness(xt, zt)
rz_ra_t = rt["Rz"] / rt["Ra"]
rz_t = 3.2 * rz_ra_t
kr45_g, kr45_t = S.roughness_factor(rz_g, m45["Rm"]), S.roughness_factor(rz_t, m45["Rm"])
kr20_g, kr20_t = S.roughness_factor(rz_g, m20["Rm"]), S.roughness_factor(rz_t, m20["Rm"])
r_ok = float(S.residual_stress("ground", np.array([0.0]))[0])
r_burn = float(S.residual_stress("ground_burn", np.array([0.0]))[0])
r_peen = float(S.residual_stress("shot_peened", np.array([0.0]))[0])
fd_ok = S.fatigue_limit(m20, rz_g, r_ok)
fd_burn = S.fatigue_limit(m20, rz_g, r_burn)
fd_peen = S.fatigue_limit(m20, rz_g * 2.5, r_peen)          # 喷丸后表面变粗（Rz 约增大到 2.5 倍，示意）
sa = 480.0                                                     # 轴承位处的弯曲应力幅（示意：台架试验的加载）
life = {k: S.life(sa, v["sigma_D"], n_d, k_sn) for k, v in (("ok", fd_ok), ("burn", fd_burn), ("peen", fd_peen))}
drop_pct = (1 - fd_burn["sigma_D"] / fd_ok["sigma_D"]) * 100

plt = style()
# ---- 图 55.6.1：粗糙度系数
fig, ax = plt.subplots(figsize=(5.8, 2.9))
rzs = np.logspace(0, 2.3, 80)
for mat, c in ((m45, M.ACCENT), (m20, M.RED)):
    ax.semilogx(rzs, [S.roughness_factor(r, mat["Rm"]) for r in rzs], color=c, lw=1.4, label=T(f"{mat['name']}，Rm = {mat['Rm']} MPa", f"Rm = {mat['Rm']} MPa"))
for rz, lab in ((rz_g, T("磨削 Ra 0.8", "ground Ra 0.8")), (rz_t, T("精车 Ra 3.2", "turned Ra 3.2")), (100, T("锻造毛坯", "forged skin"))):
    ax.axvline(rz, color=M.MUTED, ls=":", lw=0.7)
    ax.text(rz * 1.05, 0.62, lab, fontsize=7, color=M.MUTED, rotation=90, va="bottom")
ax.set_xlabel(T("Rz / µm", "Rz / µm")); ax.set_ylabel(T("粗糙度系数 K_R", "roughness factor K_R")); ax.set_ylim(0.6, 1.02)
ax.grid(lw=0.3, alpha=0.5, which="both"); ax.legend(fontsize=7, loc="upper right")
ax.set_title(T("K_R = 1 − 0.22·lg Rz·lg(2Rm/400)（FKM，钢）", "K_R = 1 − 0.22·lg Rz·lg(2Rm/400) (FKM, steel)"), fontsize=8.5)
figure(fig, "fig55_6_1")

# ---- 图 55.6.2：疲劳极限与表层残余应力
fig, ax = plt.subplots(figsize=(5.8, 2.9))
rs = np.linspace(-700, 700, 50)
ax.plot(rs, [S.fatigue_limit(m20, rz_g, r)["sigma_D"] for r in rs], color=M.RED, lw=1.4, label=T("SH-101 轴承位（20CrMnTi，Ra 0.8）", "SH-101 journal"))
for r, lab, c in ((r_ok, T("正常磨削", "normal"), M.GREEN), (r_burn, T("磨削烧伤", "burn"), M.RED), (r_peen, T("喷丸", "peened"), M.ACCENT)):
    v = S.fatigue_limit(m20, rz_g if lab != T("喷丸", "peened") else rz_g * 2.5, r)["sigma_D"]
    ax.plot(r, v, "o", color=c, ms=5)
    ax.text(r + 25 if r < 300 else r - 30, v + 12, f"{lab} {v:.0f}", fontsize=7.5, color=c, ha="left" if r < 300 else "right")
ax.axvline(0, color=M.INK, lw=0.5)
ax.set_xlabel(T("表层残余应力 / MPa（拉为正）", "surface residual stress / MPa (tension +)")); ax.set_ylabel(T("弯曲疲劳极限 σD / MPa", "bending fatigue limit σD / MPa"))
ax.text(-680, 300, T("喷丸后表面变粗（Rz 约 2.5 倍），点落在线下", "peening roughens the surface: the point lies below the line"), fontsize=7, color=M.ACCENT)
ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="upper right")
ax.set_title(T(f"σD = σ₋₁·K_R − M·σres，M = {fd_ok['M']:.3f}", f"σD = σ₋₁·K_R − M·σres, M = {fd_ok['M']:.3f}"), fontsize=8.5)
figure(fig, "fig55_6_2")

# ---- 图 55.6.3：S–N 曲线
fig, ax = plt.subplots(figsize=(5.8, 3.0))
N = np.logspace(4, 8, 200)
for key, fd, lab, c in (("ok", fd_ok, T("正常磨削", "normal grinding"), M.GREEN), ("burn", fd_burn, T("磨削烧伤", "grinding burn"), M.RED),
                        ("peen", fd_peen, T("烧伤后喷丸", "burn, then shot peened"), M.ACCENT)):
    sd = fd["sigma_D"]
    ax.loglog(N, [sd * (n / n_d) ** (-1 / k_sn) if n < n_d else sd for n in N], color=c, lw=1.4, label=T(f"{lab}：σD = {sd:.0f} MPa", f"{lab}: σD = {sd:.0f} MPa"))
    if math.isfinite(life[key]):
        ax.plot(life[key], sa, "o", color=c, ms=4)
ax.axhline(sa, color=M.MUTED, ls="--", lw=0.8)
ax.text(1.2e4, sa * 1.02, T(f"轴承位的应力幅 {sa:.0f} MPa（示意）", f"stress amplitude {sa:.0f} MPa (illustrative)"), fontsize=7, color=M.MUTED, va="bottom")
ax.set_xlabel(T("循环次数 N", "cycles N")); ax.set_ylabel(T("应力幅 σa / MPa", "stress amplitude σa / MPa"))
ax.set_ylim(250, 1500); ax.grid(lw=0.3, alpha=0.5, which="both"); ax.legend(fontsize=7, loc="upper right")
figure(fig, "fig55_6_3")

out(rz_ra=rz_ra, rz_ra_t=rz_ra_t, rz_g=rz_g, rz_t=rz_t, kr45_g=kr45_g, kr45_t=kr45_t, kr20_g=kr20_g, kr20_t=kr20_t, M20=fd_ok["M"], M45=S.mean_stress_sensitivity(m45["Rm"]),
    s1_20=m20["sigma_1"], s1_45=m45["sigma_1"], Rm20=m20["Rm"], Rm45=m45["Rm"],
    r_ok=r_ok, r_burn=r_burn, r_peen=r_peen, fd_ok=fd_ok["sigma_D"], fd_burn=fd_burn["sigma_D"], fd_peen=fd_peen["sigma_D"], drop_pct=drop_pct,
    sa=sa, life_burn=life["burn"], life_burn_e5=life["burn"] / 1e5, life_ok_inf=not math.isfinite(life["ok"]), life_peen_inf=not math.isfinite(life["peen"]), k_sn=k_sn, n_d=n_d)
