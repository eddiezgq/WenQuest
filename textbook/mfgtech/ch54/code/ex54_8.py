"""算例 54.8.1–54.8.3：从误差的形态推断误差来源（hub/accuracy.py 的 harmonics、sequence、diagnose；数据来自仿真车间的误差模型）。
54.8.1：圆度仪测得的一个截面（二阶 3 µm + 三阶 1 µm + 随机 0.3 µm）的谐波分析；
54.8.2：五种逐件序列——正常（磨损锯齿）、砂轮磨损加快、未预热、调整后跳变、中心孔质量差（圆跳动分散变大），各自的判别结果；
54.8.3：图 54.0.1 的那一批：左右轴承位、圆跳动逐件数据交给 diagnose，得到形态和可能原因。
画图 54.8.2（圆度谐波）、54.8.3（五种序列）、54.8.4（本章提要那一批的诊断）。"""
import math
import random
import statistics as st

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
ER = M.errs()
# 54.8.1
rng = random.Random(548)
m = 180
r = [0.003 * math.cos(2 * (2 * math.pi * i / m) - 0.4) + 0.001 * math.cos(3 * (2 * math.pi * i / m) + 1.0) + 0.0015 * math.cos(2 * math.pi * i / m)
     + rng.gauss(0, 0.0003) for i in range(m)]
h = A.harmonics(r)
assert h["label"] == "ellipse"
rd = max(r) - min(r)
# 54.8.2
SIG = 0.0012


def seq(problem, seed, n=40, jump=None):
    rr = ER.simulate(n, problem, seed=seed, dress_every=10)
    resets = [i + 1 for i in rr["dress_after"]]
    v = list(rr["values"]["bearing_seat_d35"])
    if jump:
        v = [x + (jump if i >= 20 else 0) for i, x in enumerate(v)]
    return v, resets, rr


base_v, base_rs, _ = seq(None, 560)
q_base = A.sequence(base_v, resets=base_rs, sigma=SIG)
drs_v, drs_rs, _ = seq("dressing_interval", 561)
q_drs = A.sequence(drs_v, resets=drs_rs, sigma=SIG)
wu_v, wu_rs, _ = seq("thermal_warmup", 562)
q_wu = A.sequence(wu_v, resets=wu_rs, sigma=SIG)
rj = ER.simulate(40, None, seed=563, dress_every=10)         # 第 16 件起尺寸跳 5 µm（换班后重新调刀的调整误差）
jv = [x + (0.005 if i >= 15 else 0) for i, x in enumerate(rj["values"]["bearing_seat_d35"])]
j_rs = [i + 1 for i in rj["dress_after"]]
q_j = A.sequence(jv, resets=j_rs, sigma=SIG)
_, _, ch = seq("center_hole", 564)
_, _, nm = seq(None, 564)
ro = ch["values"]["runout_bearing"]
ro0 = nm["values"]["runout_bearing"]
q_ro = A.sequence(ro, sigma=SIG, baseline=(st.fmean(ro0), st.stdev(ro0)))
for q, want in ((q_base, "drift_saw"), (q_drs, "drift_saw"), (q_wu, "warmup"), (q_j, "jump"), (q_ro, "spread")):
    assert want in q["labels"], (want, q["labels"])
# 54.8.3
s = M.shift()
v = s["values"]
k0 = s["start"]
L1, R1 = st.fmean(v["bearing_seat_d35"][k0:]), st.fmean(v["bearing_seat_d35_r"][k0:])
L0, R0 = st.fmean(v["bearing_seat_d35"][:k0]), st.fmean(v["bearing_seat_d35_r"][:k0])
G1, G0 = st.fmean(v["gear_seat_d40"][k0:]), st.fmean(v["gear_seat_d40"][:k0])
zs = [ER.Z_LEFT, ER.Z_GEAR, ER.Z_RIGHT]
chg = [L1 - L0, G1 - G0, R1 - R0]
dg_along = A.diagnose(along=(zs, chg), tol=0.016)
k_lin = sum(z * c for z, c in zip(zs, chg)) / sum(z * z for z in zs)          # 过原点（头架顶尖）的直线：变化 = k·z
e_est = k_lin * ER.LENGTH / 2
dg_left = A.diagnose(seq=v["bearing_seat_d35"], resets=s["resets"], sigma=SIG)
dg_run = A.diagnose(seq=v["runout_bearing"], sigma=SIG, baseline=(st.fmean(v["runout_bearing"][:k0]), st.stdev(v["runout_bearing"][:k0])))
diff = [b - a for a, b in zip(v["bearing_seat_d35"], v["bearing_seat_d35_r"])]
dg_diff = A.diagnose(seq=diff, sigma=SIG * math.sqrt(2))
assert dg_along and dg_along[0]["label"] == "taper" and any(d["label"] == "jump" for d in dg_diff)
assert {d["label"] for d in dg_left} == {"drift_saw", "jump"} and not dg_run
jump_at = next(A.sequence(diff, sigma=SIG * math.sqrt(2))["jump"]["at"] for _ in [0]) + 1

plt = style()
# ---- 图 54.8.2：圆度谐波
fig = plt.figure(figsize=(7.4, 3.0))
ax = fig.add_subplot(1, 2, 1, projection="polar")
kk = 1 / 0.01
th = [2 * math.pi * i / m for i in range(m)] + [0]
ax.plot(th, [1 + kk * x for x in r] + [1 + kk * r[0]], color=M.RED, lw=1.2)
ax.plot(th, [1.0] * len(th), color=M.MUTED, lw=0.6, ls="--")
ax.set_ylim(0, 1.6); ax.set_yticks([]); ax.set_xticks([])
ax.set_title(T(f"(a) 测得的截面（误差放大），圆度 {rd * 1000:.1f} µm（含偏心）", f"(a) measured section (exaggerated), {rd * 1000:.1f} µm incl. eccentricity"), fontsize=8)
ax = fig.add_subplot(1, 2, 2)
ks = list(range(1, 13))
cols = [M.MUTED if k == 1 else (M.RED if k == h["dominant"] else M.ACCENT) for k in ks]
ax.bar(ks, [2 * h["amp"][k] * 1000 for k in ks], color=cols)
ax.set_xticks(ks); ax.set_xlabel(T("谐波阶次 k", "harmonic order k")); ax.set_ylabel(T("峰谷值 2Aₖ / µm", "peak-to-valley 2Aₖ / µm"))
ax.text(1, 2 * h["amp"][1] * 1000 + 0.2, T("偏心", "ecc."), ha="center", fontsize=7, color=M.MUTED)
ax.text(2, 2 * h["amp"][2] * 1000 + 0.2, T("椭圆", "oval"), ha="center", fontsize=7, color=M.RED)
ax.set_title(T("(b) 谐波分析：二阶为主 → 椭圆", "(b) harmonics: order 2 dominates → oval"), fontsize=8); ax.grid(lw=0.3, alpha=0.5, axis="y")
figure(fig, "fig54_8_2")

# ---- 图 54.8.3：五种逐件序列
fig, axs = plt.subplots(1, 5, figsize=(8.0, 2.5), sharey=False)
items = [(base_v, base_rs, q_base, T("(a) 正常：锯齿", "(a) normal: saw"), T(f"斜率 {q_base['saw_slope'] * 1000:.2f} µm/件", f"{q_base['saw_slope'] * 1000:.2f} µm/part")),
         (drs_v, drs_rs, q_drs, T("(b) 砂轮磨损加快", "(b) faster wheel wear"), T(f"斜率 {q_drs['saw_slope'] * 1000:.2f} µm/件", f"{q_drs['saw_slope'] * 1000:.2f} µm/part")),
         (wu_v, wu_rs, q_wu, T("(c) 未预热", "(c) not warmed up"), T(f"τ = {q_wu['warmup']['tau']:.1f} 件", f"τ = {q_wu['warmup']['tau']:.1f} parts")),
         (jv, j_rs, q_j, T("(d) 重新调整后跳变", "(d) jump after resetting"), T(f"第 {q_j['jump']['at'] + 1} 件起 {q_j['jump']['size'] * 1000:+.1f} µm", f"from part {q_j['jump']['at'] + 1}: {q_j['jump']['size'] * 1000:+.1f} µm")),
         (ro, [], q_ro, T("(e) 中心孔差：圆跳动", "(e) poor centre holes: runout"), T(f"分散为正常的 {q_ro['sigma_ratio']:.1f} 倍", f"spread × {q_ro['sigma_ratio']:.1f}"))]
for ax, (vv, rs, q, ttl, note) in zip(axs, items):
    ax.plot(range(1, len(vv) + 1), [x * 1000 - (35000 if x > 1 else 0) for x in vv], "o-", ms=2, lw=0.6, color=M.ACCENT)
    for rr_ in rs:
        ax.axvline(rr_ + 0.5, color=M.MUTED, ls=":", lw=0.5)
    ax.set_title(ttl, fontsize=7.2)
    ax.text(0.03, 0.04, note, transform=ax.transAxes, fontsize=6.8, color=M.RED)
    ax.tick_params(labelsize=6.5)
axs[0].set_ylabel(T("直径 − 35 / µm", "diameter − 35 / µm"), fontsize=7.5)
axs[4].set_ylabel(T("圆跳动 / µm", "runout / µm"), fontsize=7.5)
fig.subplots_adjust(wspace=0.5)
figure(fig, "fig54_8_3")

# ---- 图 54.8.4：本章提要那一批的诊断
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.0), gridspec_kw={"width_ratios": [1.6, 1]})
ax = axs[0]
xs = list(range(1, len(diff) + 1))
ax.plot(xs, [d * 1000 for d in diff], "o-", ms=2.5, lw=0.7, color=M.WARM)
ax.axvline(jump_at - 0.5, color=M.RED, ls="--", lw=0.8)
ax.plot([1, k0], [(R0 - L0) * 1000] * 2, color=M.INK, lw=1.4); ax.plot([k0 + 1, len(diff)], [(R1 - L1) * 1000] * 2, color=M.INK, lw=1.4)
ax.set_xlabel(T("零件序号", "part number")); ax.set_ylabel(T("右减左轴承位直径 / µm", "right − left / µm")); ax.grid(lw=0.3, alpha=0.5)
ax.set_title(T(f"(a) 两轴承位之差：第 {jump_at} 件起跳变（砂轮磨损两处一样，相减后消掉）", f"(a) right − left: a jump from part {jump_at} (wear cancels)"), fontsize=7.8)
ax = axs[1]
ax.plot(zs, [c * 1000 for c in chg], "s", color=M.RED, ms=6)
for z, c, lab in zip(zs, chg, (T("左轴承位", "left"), T("齿轮位", "gear seat"), T("右轴承位", "right"))):
    ax.text(z, c * 1000 + 0.8, lab, ha="center", fontsize=7)
ax.plot([0, ER.LENGTH], [0, k_lin * ER.LENGTH * 1000], color=M.ACCENT, lw=1, ls="--")
ax.axhline(0, color=M.MUTED, lw=0.6)
ax.set_xlabel(T("距左端（头架顶尖）/ mm", "from the left end (head centre) / mm")); ax.set_ylabel(T("比注入前变化 / µm", "change vs before / µm"))
ax.set_xlim(0, 175); ax.set_ylim(-1, 17); ax.grid(lw=0.3, alpha=0.5)
ax.set_title(T("(b) 沿轴向：变化与到头架的距离成正比 → 锥度", "(b) along the axis: change ∝ distance from the head → taper"), fontsize=7.8)
figure(fig, "fig54_8_4")

out(h2_um=2 * h["amp"][2] * 1000, h3_um=2 * h["amp"][3] * 1000, h1_um=2 * h["amp"][1] * 1000, rd_um=rd * 1000, dom=h["dominant"],
    slope_base=q_base["saw_slope"] * 1000, slope_drs=q_drs["saw_slope"] * 1000, wu_tau=q_wu["warmup"]["tau"], wu_dinf=q_wu["warmup"]["delta_inf"] * 1000,
    j_at=q_j["jump"]["at"] + 1, j_size=q_j["jump"]["size"] * 1000, ro_ratio=q_ro["sigma_ratio"], ro_shift=q_ro.get("shift", 0) * 1000,
    dL=(L1 - L0) * 1000, dR=(R1 - R0) * 1000, dG=(G1 - G0) * 1000, e_est_um=e_est * 1000, taper_um=dg_along[0]["value"] * 1000, cause0=dg_along[0]["causes"][0], jump_at=jump_at,
    labels_left="、".join(A.SHAPES[d["label"]]["name"] for d in dg_left))
