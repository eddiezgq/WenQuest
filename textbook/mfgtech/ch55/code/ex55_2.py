"""算例 55.2.1–55.2.4：表面粗糙度的形成与控制（hub/surface.py）。
55.2.1：SH-301 工序 40 精车（DNMG 110404，r = 0.4，f = 0.15 mm/r）的理论残留高度和 Ra，与图纸 Ra 3.2 比较；
        要车到 Ra 0.8 时进给量最大多少（只按几何残留）；r = 0.8 时呢；
55.2.2：尖刀（κr = 93°、κr′ = 32°）同样进给量的残留高度；
55.2.3：积屑瘤：同一刀具、同一进给，vc = 25 m/min 与 150 m/min 合成轮廓的 Ra、Rz（三条轮廓平均）；
55.2.4：工序 60 磨削：粗磨（横进给 0.01）、精磨（0.005）的当量磨削厚度和 Ra，光磨 0、1、2、3 次的 Ra。
画图 55.2.2（h、Ra 与 f、r）、55.2.4（积屑瘤区）、55.2.5（三条轮廓）、55.2.7（磨削的 Ra 与光磨次数）、55.2.8（SH-301 各工序的 Ra）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
p = M.plan()
o40 = M.op(p, 40)
f40 = float(o40["cut"]["f_mm_r"])
vc40 = float(o40["cut"]["vc_m_min"])
r40 = 0.4                                   # DNMG 110404：刀尖圆弧 0.4（刀片型号最后两位 04）
h40 = S.residual_height(f40, r40) * 1000
ra40 = S.ra_theory(f40, r40)
f_08 = S.feed_for_ra(0.8, r40)
f_08_r8 = S.feed_for_ra(0.8, 0.8)
h_sharp = S.residual_height_sharp(f40, 93, 32) * 1000


def mean_rough(f, r, vc, wave=0.0, n=3):
    rs = [S.roughness(*S.turned_profile(f, r, vc_m_min=vc, wave_um=wave, wave_mm=0.5, seed=s)) for s in range(n)]
    return float(np.mean([x["Ra"] for x in rs])), float(np.mean([x["Rz"] for x in rs]))


ra_bue, rz_bue = mean_rough(f40, r40, 25)
ra_hi, rz_hi = mean_rough(f40, r40, vc40)
ra_wave, rz_wave = mean_rough(f40, r40, vc40, wave=3.0)
# 磨削（工序 60）
G = M.errs().GRIND
vs, vw = G["vs"], G["vw"]
heq_r = S.heq(vw, 0.01, vs)
heq_f = S.heq(vw, G["ap"], vs)
ra_rough = S.grinding_ra(heq_r, 0)
ra_fine = [S.grinding_ra(heq_f, k) for k in range(4)]

plt = style()
# ---- 图 55.2.2：残留高度、理论 Ra 与进给量、刀尖圆弧
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.0))
fs = np.linspace(0.02, 0.4, 80)
for r, c in ((0.4, M.RED), (0.8, M.ACCENT), (1.2, M.GREEN)):
    a1.plot(fs, [S.residual_height(f, r) * 1000 for f in fs], color=c, lw=1.4, label=f"r = {r}")
    a2.plot(fs, [S.ra_theory(f, r) for f in fs], color=c, lw=1.4, label=f"r = {r}")
for y in (0.8, 1.6, 3.2):
    a2.axhline(y, color=M.MUTED, ls="--", lw=0.7)
    a2.text(0.30, y + 0.08, f"Ra {y}", fontsize=7, va="bottom", color=M.MUTED)
a2.plot([f40], [ra40], "o", color=M.RED, ms=4)
a2.annotate(T(f"工序 40 精车\nf = {f40}，r = {r40}", f"op 40 finishing\nf = {f40}, r = {r40}"), (f40, ra40), (0.05, 4.2), fontsize=7,
            arrowprops={"arrowstyle": "->", "lw": 0.6}, color=M.RED)
a1.set_title(T("(a) 理论残留高度 h = r − √(r² − f²/4)", "(a) theoretical peak-to-valley h"), fontsize=8.5)
a2.set_title(T("(b) 理论 Ra ≈ 0.0321 f²/r", "(b) theoretical Ra ≈ 0.0321 f²/r"), fontsize=8.5)
for a, yl in ((a1, T("h / µm", "h / µm")), (a2, T("Ra / µm", "Ra / µm"))):
    a.set_xlabel(T("进给量 f / (mm/r)", "feed f / (mm/r)")); a.set_ylabel(yl); a.grid(lw=0.3, alpha=0.5); a.legend(fontsize=7, loc="upper left")
a1.set_ylim(0, 45); a2.set_ylim(0, 6); a2.set_xlim(0, 0.43)
figure(fig, "fig55_2_2")

# ---- 图 55.2.4：积屑瘤区：Ra 随切削速度
fig, ax = plt.subplots(figsize=(6.0, 2.9))
vcs = [3, 6, 10, 15, 20, 25, 30, 40, 50, 70, 100, 150, 200]
ras = [mean_rough(f40, r40, v, n=2)[0] for v in vcs]
ax.semilogx(vcs, ras, "o-", color=M.RED, ms=3.5, lw=1.2, label=T("合成轮廓的 Ra（f = 0.15，r = 0.4）", "Ra of the synthetic profile (f = 0.15, r = 0.4)"))
ax.axhline(ra40, color=M.ACCENT, ls="--", lw=0.8)
ax.text(160, ra40 + 0.05, T("只有几何残留", "geometry only"), fontsize=7, color=M.ACCENT, ha="right", va="bottom")
ax.axvspan(10, 60, color="#f6e7e5")
ax.text(25, 0.6, T("积屑瘤、鳞刺区（中碳钢，示意）", "built-up edge zone (medium-carbon steel, illustrative)"), fontsize=7.5, ha="center", color=M.RED)
ax.set_xlabel(T("切削速度 vc / (m/min)", "cutting speed vc / (m/min)")); ax.set_ylabel(T("Ra / µm", "Ra / µm"))
ax.set_ylim(0, max(ras) * 1.1); ax.grid(lw=0.3, alpha=0.5, which="both"); ax.legend(fontsize=7, loc="center right")
figure(fig, "fig55_2_4")

# ---- 图 55.2.5：三条轮廓：几何残留、积屑瘤、振动
fig, axs = plt.subplots(3, 1, figsize=(7.2, 5.0), sharex=True, gridspec_kw={"hspace": 0.55})
cases = [(T(f"(a) vc = {vc40:.0f} m/min：刀尖圆弧的残留", f"(a) vc = {vc40:.0f} m/min: nose-radius scallops"), vc40, 0.0),
         (T("(b) vc = 25 m/min：积屑瘤、鳞刺", "(b) vc = 25 m/min: built-up edge"), 25, 0.0),
         (T(f"(c) vc = {vc40:.0f} m/min，振动留下的振纹（幅值 3 µm、间距 0.5 mm）", f"(c) vc = {vc40:.0f} m/min with chatter marks (3 µm, 0.5 mm apart)"), vc40, 3.0)]
for a, (title, vc, wave) in zip(axs, cases):
    x, z = S.turned_profile(f40, r40, vc_m_min=vc, wave_um=wave, wave_mm=0.5, seed=2)
    k = (x >= 0.8) & (x < 2.0)
    rr = S.roughness(x, z)
    a.plot(x[k] - 0.8, (z[k] - z[k].mean()) * 1000, color=M.INK, lw=0.6)
    a.set_title(title + T(f"（Ra {rr['Ra']:.2f}，Rz {rr['Rz']:.1f} µm）", f" (Ra {rr['Ra']:.2f}, Rz {rr['Rz']:.1f} µm)"), fontsize=8, loc="left")
    a.set_ylim(-9, 9); a.grid(lw=0.3, alpha=0.4); a.set_ylabel("µm", fontsize=7)
axs[-1].set_xlabel(T("沿进给方向的距离 / mm（纵向放大约 100 倍）", "distance along the feed / mm (vertical scale about ×100)"))
figure(fig, "fig55_2_5")

# ---- 图 55.2.7：磨削：Ra 与当量磨削厚度、光磨次数
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 2.9))
hs = np.linspace(0.02, 0.3, 60)
for k, c in ((0, M.RED), (1, M.WARM), (2, M.ACCENT)):
    a1.plot(hs, [S.grinding_ra(h, k) for h in hs], color=c, lw=1.3, label=T(f"光磨 {k} 次", f"{k} spark-out passes"))
a1.axvline(heq_f, color=M.MUTED, ls=":", lw=0.8); a1.axvline(heq_r, color=M.MUTED, ls=":", lw=0.8)
a1.text(heq_f, 1.35, T(" 精磨", " finish"), fontsize=7, color=M.MUTED); a1.text(heq_r, 1.35, T(" 粗磨", " rough"), fontsize=7, color=M.MUTED)
a1.axhline(0.8, color=M.RED, ls="--", lw=0.7)
a1.set_xlabel(T("当量磨削厚度 heq / µm", "equivalent chip thickness heq / µm")); a1.set_ylabel("Ra / µm"); a1.set_ylim(0, 1.5)
a1.set_title(T("(a) heq = vw·ap/vs 越小越光", "(a) the smaller heq, the finer"), fontsize=8.5); a1.legend(fontsize=7); a1.grid(lw=0.3, alpha=0.5)
a2.bar(range(4), ra_fine, color=[M.RED, M.WARM, M.ACCENT, M.GREEN], width=0.6)
for i, v in enumerate(ra_fine):
    a2.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=7.5)
a2.axhline(0.8, color=M.RED, ls="--", lw=0.7); a2.text(3.4, 0.82, "Ra 0.8", fontsize=7, color=M.RED, ha="left")
a2.axhline(0.4, color=M.MUTED, ls=":", lw=0.7); a2.text(3.4, 0.36, T("砂轮形貌\n决定的下限", "limit set\nby the wheel"), fontsize=7, color=M.MUTED, ha="left", va="top"); a2.set_xlim(-0.5, 4.4)
a2.set_xticks(range(4)); a2.set_xticklabels([T(f"{k} 次", f"{k}") for k in range(4)])
a2.set_xlabel(T("精磨后的光磨次数", "spark-out passes after finishing")); a2.set_ylabel("Ra / µm"); a2.set_ylim(0, 1.0)
a2.set_title(T("(b) 工序 60 精磨（横进给 0.005）后光磨", "(b) spark-out after finishing (op 60)"), fontsize=8.5)
figure(fig, "fig55_2_7")

# ---- 图 55.2.8：SH-301 各工序后的 Ra
o20 = M.op(p, 20)
f20 = float(o20["cut"]["f_mm_r"]) if o20.get("cut") else 0.2
ra20 = S.ra_theory(f20, 0.8)
steps = [(T(f"工序 20 粗车\nf {f20}，r 0.8", "op 20 rough turn"), ra20, 12.5),
         (T("工序 40 精车\nf 0.15，r 0.4", "op 40 finish turn"), ra40, 3.2),
         (T("工序 60 粗磨\n0.01/行程", "op 60 rough grind"), ra_rough, None),
         (T("工序 60 精磨\n0.005，光磨 2 次", "op 60 finish + 2 spark-out"), ra_fine[2], 0.8)]
fig, ax = plt.subplots(figsize=(6.4, 2.9))
ax.bar(range(4), [s[1] for s in steps], color=[M.MUTED, M.WARM, M.ACCENT, M.GREEN], width=0.55, label=T("计算的 Ra（几何残留或磨削经验式）", "computed Ra"))
for i, (_, v, req) in enumerate(steps):
    ax.text(i, v * 1.12, f"{v:.2f}", ha="center", fontsize=7.5)
    if req:
        ax.plot([i - 0.35, i + 0.35], [req, req], color=M.RED, lw=1.2)
        ax.text(i + 0.37, req, T(f"要求 {req}", f"req. {req}"), fontsize=7, color=M.RED, va="center")
ax.set_yscale("log"); ax.set_ylim(0.2, 30); ax.set_xlim(-0.5, 4.1)
ax.set_xticks(range(4)); ax.set_xticklabels([s[0] for s in steps], fontsize=7.5)
ax.set_ylabel(T("Ra / µm（对数坐标）", "Ra / µm (log)")); ax.grid(lw=0.3, alpha=0.5, axis="y")
figure(fig, "fig55_2_8")

out(f40=f40, r40=r40, vc40=vc40, h40_um=h40, ra40=ra40, f_08=f_08, f_08_r8=f_08_r8, h_sharp_um=h_sharp,
    ra_bue=ra_bue, rz_bue=rz_bue, ra_hi=ra_hi, rz_hi=rz_hi, ra_wave=ra_wave, bue_ratio=ra_bue / ra_hi,
    heq_r=heq_r, heq_f=heq_f, ra_rough=ra_rough, ra_f0=ra_fine[0], ra_f1=ra_fine[1], ra_f2=ra_fine[2], ra_f3=ra_fine[3],
    ra20=ra20, f20=f20, vs=vs, vw_m_min=vw * 60)
