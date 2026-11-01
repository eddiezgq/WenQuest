"""算例 54.7.1–54.7.3：加工误差的统计分析（hub/spc.py，与数字工厂质量页同一个库）。
54.7.1：仿真车间正常状态磨 100 件 SH-301，左轴承位的分布图：均值、标准差、Cp、Cpk、超差率的估计（capability）；
54.7.2：按一个修整周期（10 件）一组的均值–极差图（xbar_r）：前 100 件正常、后 100 件注入“尾座偏移”时右轴承位的均值–极差图与判异（special_causes）；
54.7.3：四种常见的分布（正态；不修整、磨损贯穿全批时的“平顶”；圆跳动这类只有上限的偏态；两次调整混在一起的双峰）。
画图 54.7.1（直方图与正态曲线）、54.7.2（四种分布）、54.7.3（Cp 与 Cpk）、54.7.4（均值–极差图）、54.7.5（判异规则）。"""
import math
import random
import statistics as st

import _mfg as M
from bookout import T, figure, out, style

SPC = M.spc()
ER = M.errs()
lo, hi = 35.002, 35.018
s100 = M.shift(n_ok=100, n_bad=0, seeds=(547, 0))
v = s100["values"]["bearing_seat_d35"]
cap = SPC.capability(v, lo, hi)
xr = SPC.xbar_r(v, 10)                 # 子组 = 一个修整周期（10 件）
cap_w = SPC.capability(v, lo, hi, xr["sigma_within"])
ACC = M.acc()
rep = ACC.sequence(v, resets=s100["resets"])          # 去掉磨损锯齿以后的移动极差：加工的重复性 σ
sig_rep = rep["sigma_mr"]
z_lo, z_hi = (cap["mean"] - lo) / cap["s"], (hi - cap["mean"]) / cap["s"]
phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))       # noqa: E731
p_out = (1 - phi(z_lo)) + (1 - phi(z_hi))
# 54.7.2：前 50 件正常、后 50 件尾座偏移
s2 = M.shift(n_ok=100, n_bad=100, seeds=(548, 549))
vr = s2["values"]["bearing_seat_d35_r"]
ph1 = SPC.xbar_r(vr[:100], 10)
g = SPC.subgroups(vr, 10)
xb = [st.fmean(x) for x in g]
rr = [max(x) - min(x) for x in g]
sig_x = (ph1["UCL"] - ph1["center"]) / 3
hits = SPC.special_causes(xb, ph1["center"], sig_x)
first = min(h["index"] for h in hits) + 1 if hits else None
assert first and first > 10, "判异应在第 10 组（第 100 件）以后"
# 54.7.3：四种分布
rng = random.Random(54)
d_norm = [rng.gauss(35.010, 0.0012) for _ in range(400)]
nd = ER.simulate(400, None, seed=550, dress_every=None)          # 不按 10 件修整：寿命用到 8% 才修整，磨损贯穿整段
d_flat = nd["values"]["bearing_seat_d35"]
d_skew = [math.hypot(rng.gauss(0, 0.002), rng.gauss(0, 0.002)) for _ in range(400)]   # 圆跳动 ≈ 偏心矢量的长度（瑞利分布）
d_bi = [rng.gauss(35.0075, 0.0011) for _ in range(200)] + [rng.gauss(35.0125, 0.0011) for _ in range(200)]

plt = style()
# ---- 图 54.7.1
fig, ax = plt.subplots(figsize=(5.8, 3.2))
bins = [lo - 0.002 + 0.001 * i for i in range(21)]
ax.hist(v, bins=bins, color="#c9d8ea", edgecolor=M.ACCENT)
xs = [lo - 0.002 + 0.0002 * i for i in range(101)]
ax.plot(xs, [100 * 0.001 / (cap["s"] * math.sqrt(2 * math.pi)) * math.exp(-(x - cap["mean"]) ** 2 / (2 * cap["s"] ** 2)) for x in xs], color=M.RED)
for y, lab in ((lo, T("下限", "LSL")), (hi, T("上限", "USL"))):
    ax.axvline(y, color=M.RED, ls="--", lw=0.8); ax.text(y, ax.get_ylim()[1] * 0.92, lab, color=M.RED, fontsize=7.5, ha="center")
ax.axvline(cap["mean"], color=M.INK, lw=0.8)
ax.text(cap["mean"] + 0.0003, ax.get_ylim()[1] * 0.75, T(f"x̄ = {cap['mean']:.4f}\ns = {cap['s'] * 1000:.2f} µm", f"x̄ = {cap['mean']:.4f}\ns = {cap['s'] * 1000:.2f} µm"), fontsize=7.5)
ax.set_xlabel(T("左轴承位直径 / mm", "left bearing seat diameter / mm")); ax.set_ylabel(T("件数", "count"))
ax.ticklabel_format(useOffset=False)
figure(fig, "fig54_7_1")

# ---- 图 54.7.2：四种分布
fig, axs = plt.subplots(1, 4, figsize=(7.8, 2.4))
for ax, data, ttl in ((axs[0], d_norm, T("(a) 正态：随机误差为主", "(a) normal: random")), (axs[1], d_flat, T("(b) 平顶：磨损贯穿全批", "(b) flat: wear over the batch")),
                      (axs[2], d_skew, T("(c) 偏态：圆跳动（偏心的大小）", "(c) skewed: runout")), (axs[3], d_bi, T("(d) 双峰：两次调整混在一起", "(d) bimodal: two settings"))):
    ax.hist(data, bins=18, color="#c9d8ea", edgecolor=M.ACCENT)
    ax.set_title(ttl, fontsize=7.5); ax.set_yticks([]); ax.tick_params(labelsize=6.5)
    ax.ticklabel_format(useOffset=False)
    for lab in ax.get_xticklabels():
        lab.set_rotation(35)
figure(fig, "fig54_7_2")

# ---- 图 54.7.3：Cp 与 Cpk
fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.4))
for ax, (mu, sg, ttl) in zip(axs, ((0.0, 1 / 6, "Cp = 1, Cpk = 1"), (0.0, 1 / 8, "Cp = 1.33, Cpk = 1.33"), (0.2, 1 / 8, "Cp = 1.33, Cpk = 0.8"))):
    xs = [-0.8 + 0.01 * i for i in range(161)]
    ax.fill_between(xs, [math.exp(-(x - mu) ** 2 / (2 * sg * sg)) for x in xs], color="#c9d8ea")
    ax.plot(xs, [math.exp(-(x - mu) ** 2 / (2 * sg * sg)) for x in xs], color=M.ACCENT)
    for b in (-0.5, 0.5):
        ax.axvline(b, color=M.RED, ls="--", lw=0.8)
    ax.axvline(0, color=M.MUTED, lw=0.6)
    ax.set_title(ttl, fontsize=8); ax.set_yticks([]); ax.set_xticks([-0.5, 0, 0.5]); ax.set_xticklabels([T("下限", "LSL"), T("中值", "mid"), T("上限", "USL")], fontsize=7)
figure(fig, "fig54_7_3")

# ---- 图 54.7.4：均值–极差图（右轴承位：前 100 件正常求控制限，后 100 件尾座偏移）
fig, axs = plt.subplots(2, 1, figsize=(6.6, 4.2), sharex=True)
ks = list(range(1, len(xb) + 1))
ax = axs[0]
ax.plot(ks, xb, "o-", ms=3.5, color=M.ACCENT)
for y, ls_ in ((ph1["center"], "-"), (ph1["UCL"], "--"), (ph1["LCL"], "--")):
    ax.axhline(y, color=M.RED if ls_ == "--" else M.MUTED, ls=ls_, lw=0.8)
for h in hits:
    ax.plot([h["index"] + 1], [xb[h["index"]]], "o", ms=8, mfc="none", mec=M.RED)
ax.axvspan(10.5, len(xb) + 0.5, color="#f6e7e5", zorder=0)
ax.set_ylim(ph1["LCL"] - 0.0012, max(xb) + 0.001); ax.set_ylabel(T("子组均值 / mm", "subgroup mean / mm")); ax.ticklabel_format(useOffset=False); ax.grid(lw=0.3, alpha=0.5)
ax.text(1, ph1["UCL"], "UCL", fontsize=7, color=M.RED, va="bottom"); ax.text(1, ph1["LCL"], "LCL", fontsize=7, color=M.RED, va="top")
ax = axs[1]
ax.plot(ks, rr, "s-", ms=3, color=M.WARM)
ax.axhline(ph1["Rbar"], color=M.MUTED, lw=0.8); ax.axhline(ph1["UCL_R"], color=M.RED, ls="--", lw=0.8)
ax.axvspan(10.5, len(xb) + 0.5, color="#f6e7e5", zorder=0)
ax.set_ylabel(T("子组极差 / mm", "subgroup range / mm")); ax.set_xlabel(T("子组（每组 10 件，一个修整周期）", "subgroup (10 parts, one dressing cycle)")); ax.grid(lw=0.3, alpha=0.5)
ax.set_xticks(ks[::2])
figure(fig, "fig54_7_4")

# ---- 图 54.7.5：四条判异规则（示意数据）
fig, axs = plt.subplots(1, 4, figsize=(7.8, 2.2), sharey=True)
pat = {1: [0.2, -0.5, 0.8, -0.3, 0.1, 3.4, 0.2, -0.4, 0.5, 0.0],
       2: [0.2, -0.5, 0.3, 2.3, 0.6, 2.4, 0.1, -0.2, 0.4, -0.6],
       3: [0.1, -0.4, 1.3, 1.6, 0.4, 1.2, 1.5, -0.1, 0.2, -0.3],
       4: [-0.3, 0.4, 0.6, 0.2, 0.9, 0.5, 0.3, 0.7, 0.4, 0.8]}
txt = {1: T("规则 1：1 点出 3σ", "rule 1: beyond 3σ"), 2: T("规则 2：3 点中 2 点出 2σ", "rule 2: 2 of 3 beyond 2σ"),
       3: T("规则 3：5 点中 4 点出 1σ", "rule 3: 4 of 5 beyond 1σ"), 4: T("规则 4：连续 8 点在一侧", "rule 4: 8 in a row on one side")}
for ax, r in zip(axs, (1, 2, 3, 4)):
    z = pat[r]
    hs = [h for h in SPC.special_causes(z, 0.0, 1.0) if h["rule"] == r]
    assert hs, f"示意数据应触发规则 {r}"
    ax.plot(range(1, 11), z, "o-", ms=3, color=M.ACCENT)
    for y in (3, 2, 1, 0, -1, -2, -3):
        ax.axhline(y, color=M.RED if abs(y) == 3 else M.MUTED, lw=0.8 if abs(y) == 3 else 0.4, ls="--" if y else "-")
    ax.plot([hs[0]["index"] + 1], [z[hs[0]["index"]]], "o", ms=8, mfc="none", mec=M.RED)
    ax.set_title(txt[r], fontsize=7.2); ax.set_xticks([])
axs[0].set_yticks([-3, -2, -1, 0, 1, 2, 3]); axs[0].set_yticklabels(["−3σ", "−2σ", "−σ", T("中心", "CL"), "σ", "2σ", "3σ"], fontsize=6.5)
figure(fig, "fig54_7_5")

out(p3s=(phi(3) - phi(-3)) * 100, sig_rep_um=sig_rep * 1000, n=len(v), mean=cap["mean"], s_um=cap["s"] * 1000, sw_um=xr["sigma_within"] * 1000, Cp=cap_w["Cp"], Cpk=cap_w["Cpk"], Pp=cap["Pp"], Ppk=cap["Ppk"],
    p_out_ppm=p_out * 1e6, n_fail=sum(1 for x in v if not lo <= x <= hi), A2=SPC.A2[10], D4=SPC.D4[10], D3=SPC.D3[10], d2=SPC.D2[10],
    xbb=xr["center"], Rbar_um=xr["Rbar"] * 1000, UCL=xr["UCL"], LCL=xr["LCL"], UCLR_um=xr["UCL_R"] * 1000,
    ph1_c=ph1["center"], ph1_ucl=ph1["UCL"], first=first, first_rule=min(hits, key=lambda h: h["index"])["rule"], n_hits=len(hits))
