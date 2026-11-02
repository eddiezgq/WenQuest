"""算例 55.5.1–55.5.4：磨削温度与烧伤（hub/surface.py；仿真车间 sim/errors.py 的磨削参数 GRIND）。
55.5.1：SH-301 工序 60（45 钢调质，Ø35，砂轮 Ø400，vs 35 m/s，vw 20 m/min）粗磨 0.01、精磨 0.005 的接触弧长、当量磨削厚度、
        比磨削能、热流密度、磨削区最高温度与接触时间；
55.5.2：烧伤判别——Hollomon–Jaffe 回火参数：45 钢 560 ℃ × 2 h 回火、20CrMnTi 180 ℃ × 2 h 回火，在毫秒级受热下开始软化的温度；
55.5.3：SH-101 轴承位（20CrMnTi 渗碳淬火，Ø25）：同样的砂轮和速度下，精磨 0.002、0.005、0.01 的温度与是否烧伤；不烧伤的最大切深；
        砂轮变钝（磨粒磨平面积 4%）以后；
55.5.4：仿真车间“砂轮修整不锋利”情景：每个修整周期里的磨削温度与烧伤件。
画图 55.5.2（磨削区温度分布）、55.5.3（回火软化温度与受热时间）、55.5.4（三种烧伤的硬度分布，示意）、
55.5.5（烧伤边界）、55.5.7（修整周期内的温度）、55.5.6（SH-101 的几种磨削方案）。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

S = M.surf()
ER = M.errs()
G = ER.GRIND
m45, m20 = S.STEELS["45-QT"], S.STEELS["20CrMnTi-CQ"]
vs, vw = G["vs"], G["vw"]
de301 = S.equivalent_diameter(G["dw"], G["ds"])
de101 = S.equivalent_diameter(25, G["ds"])
g_r = S.grinding_temperature(m45, vs, vw, 0.01, de301)
g_f = S.grinding_temperature(m45, vs, vw, G["ap"], de301)
b_r = S.burn_state(m45, g_r["theta"], g_r["t_ms"])
on45 = S.temper_onset(m45, g_f["t_ms"] / 1000)
on20 = S.temper_onset(m20, 1e-3)
ap45 = S.max_infeed(m45, vs, vw, de301)
# SH-101
cases = {ap: S.grinding_temperature(m20, vs, vw, ap, de101) for ap in (0.002, 0.005, 0.01)}
burns = {ap: S.burn_state(m20, g["theta"], g["t_ms"]) for ap, g in cases.items()}
ap20 = S.max_infeed(m20, vs, vw, de101)
g_dull = S.grinding_temperature(m20, vs, vw, 0.002, de101, wear_flat_pct=4)
b_dull = S.burn_state(m20, g_dull["theta"], g_dull["t_ms"])
ap20_dull = S.max_infeed(m20, vs, vw, de101, wear_flat_pct=4)
vw_slow = 10 / 60
ap20_slow = S.max_infeed(m20, vs, vw_slow, de101)
# 仿真车间：修整不锋利
sim_ok = ER.simulate(40, dress_every=10)["values"]
sim_bad = ER.simulate(40, "wheel_dull", dress_every=10)["values"]
n_burn = sum(sim_bad["burn_bearing"])
first_burn = sim_bad["burn_bearing"].index(1) + 1
ra_bad_max = max(sim_bad["ra_bearing"])


def theta_of(wear, dull):
    A = 0.5 + dull * (1 + 3 * wear) if dull else 0.5 + 3 * wear
    return S.grinding_temperature(m45, vs, vw, G["ap"], de301, A)["theta"]


plt = style()
# ---- 图 55.5.2：磨削区表面温度沿接触区的分布（Jaeger 移动热源）
from scipy.integrate import quad
from scipy.special import k0


def shape(L, X):
    lo, hi = X - L, X + L
    return quad(lambda u: math.exp(-u) * k0(abs(u)) if u else 0.0, lo, hi, points=[0.0] if lo < 0 < hi else None, limit=200)[0]


fig, ax = plt.subplots(figsize=(6.2, 3.0))
for g, ap, c in ((g_r, 0.01, M.RED), (g_f, G["ap"], M.ACCENT)):
    L = g["peclet"]
    Xs = np.linspace(-1.2 / (g["lc"] / 2) * L, 1.2 / (g["lc"] / 2) * L, 200)
    F = np.array([shape(L, X) for X in Xs])
    rise = F / F.max() * g["rise"]
    lc = g["lc"]
    ax.plot(Xs / L * lc / 2, 20 + rise, color=c, lw=1.4, label=T(f"切深 {ap} mm：lc = {lc:.2f} mm，θmax ≈ {g['theta']:.0f} ℃",
                                                              f"ap {ap} mm: lc = {lc:.2f} mm, θmax ≈ {g['theta']:.0f} °C"))
    ax.axvspan(-lc / 2, lc / 2, color=c, alpha=0.07)
ax.axhline(m45["Ac1"], color=M.MUTED, ls="--", lw=0.8)
ax.text(0.7, m45["Ac1"] + 12, T(f"Ac1 = {m45['Ac1']} ℃", f"Ac1 = {m45['Ac1']} °C"), fontsize=7.5, color=M.MUTED)
ax.annotate("", (0.35, 120), (0.95, 120), arrowprops={"arrowstyle": "->", "lw": 0.8, "color": M.INK})
ax.text(0.65, 135, T("工件相对砂轮的运动方向", "work motion relative to the wheel"), fontsize=7.5, ha="center")
ax.text(0.65, 60, T("前方：未受热", "ahead: still cold"), fontsize=7, ha="center", color=M.MUTED)
ax.text(-0.75, 470, T("离开接触区后\n热量向内传开", "after contact the heat\nspreads inwards"), fontsize=7, ha="center", color=M.MUTED)
ax.set_xlabel(T("沿砂轮相对工件运动方向的位置 / mm（0 为接触区中点，阴影为接触区）", "position along the wheel's motion relative to the work / mm (0 = middle of contact)"))
ax.set_ylabel(T("工件表面温度 / ℃", "surface temperature / °C")); ax.set_xlim(-1.2, 1.2); ax.set_ylim(0, 800)
ax.legend(fontsize=7, loc="center right"); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig55_5_2")

# ---- 图 55.5.3：开始回火软化的温度与受热时间（Hollomon–Jaffe）
fig, ax = plt.subplots(figsize=(6.0, 3.0))
ts = np.logspace(-4, 4, 100)
for mat, c in ((m45, M.ACCENT), (m20, M.RED)):
    ax.semilogx(ts, [S.temper_onset(mat, t) for t in ts], color=c, lw=1.4,
                label=T(f"{mat['name']}（原回火 {mat['temper_c']} ℃ × {mat['temper_h']:.0f} h）", f"{mat['name']} (tempered {mat['temper_c']} °C)"))
    ax.axhline(mat["Ac1"], color=c, ls=":", lw=0.7)
ax.text(2e3, m45["Ac1"] + 10, "Ac1", fontsize=7, color=M.MUTED)
ax.axvspan(3e-4, 3e-3, color="#f6e7e5")
ax.text(1e-3, 150, T("磨削：受热约 1 ms", "grinding: ~1 ms"), fontsize=7.5, ha="center", color=M.RED)
ax.axvline(7200, color=M.MUTED, ls="--", lw=0.6); ax.text(6000, 115, T("炉内回火 2 h ", "furnace 2 h "), fontsize=7, color=M.MUTED, ha="right")
ax.set_xlabel(T("受热时间 / s", "heating time / s")); ax.set_ylabel(T("开始回火软化的温度 / ℃", "softening onset / °C"))
ax.set_ylim(100, 1000); ax.grid(lw=0.3, alpha=0.5, which="both"); ax.legend(fontsize=7, loc="upper right")
figure(fig, "fig55_5_3")

# ---- 图 55.5.4：三种烧伤的显微硬度分布（渗碳淬火件，示意）
fig, ax = plt.subplots(figsize=(6.0, 2.9))
z = np.linspace(0, 0.4, 200)
base = 700 - 40 * z / 0.4
ax.plot(z, base, color=M.GREEN, lw=1.3, label=T("正常磨削", "normal grinding"))
temper = base - 180 * np.exp(-z / 0.06)
ax.plot(z, temper, color=M.WARM, lw=1.3, label=T("回火烧伤：表层软化", "tempering burn: softened"))
reh = np.where(z < 0.02, 800, base - 260 * np.exp(-(z - 0.02) / 0.06))
ax.plot(z, reh, color=M.RED, lw=1.3, label=T("二次淬火烧伤：白层 + 下面的回火软带", "re-hardening burn: white layer over a soft band"))
ann = base - 420 * np.exp(-z / 0.08)
ax.plot(z, ann, color=M.MUTED, lw=1.3, ls="--", label=T("退火烧伤（干磨）", "annealing burn (dry)"))
ax.set_xlabel(T("离表面的深度 / mm", "depth below the surface / mm")); ax.set_ylabel(T("显微硬度 HV（示意）", "microhardness HV (illustrative)"))
ax.set_ylim(200, 900); ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="lower right")
figure(fig, "fig55_5_4")

# ---- 图 55.5.5：烧伤边界（SH-101，工件速度–切深）
fig, ax = plt.subplots(figsize=(6.2, 3.2))
vws = [x / 60 for x in (5, 7.5, 10, 15, 20, 25, 30, 40)]
for A, c, lab in ((0.5, M.ACCENT, T("刚修整的砂轮", "freshly dressed")), (4.0, M.RED, T("钝砂轮（磨粒磨平面积 4%）", "dull wheel (4% wear flat)"))):
    bd = S.burn_boundary(m20, vs, de101, vws, A)
    ax.plot([v * 60 for v, _ in bd], [a * 1000 for _, a in bd], color=c, lw=1.4, label=lab)
    if A == 0.5:
        ax.fill_between([v * 60 for v, _ in bd], [a * 1000 for _, a in bd], 30, color="#f6e7e5")
for ap, g in cases.items():
    ok = burns[ap]["kind"] == "none"
    ax.plot(vw * 60, ap * 1000, "o" if ok else "x", color=M.GREEN if ok else M.RED, ms=6, mew=1.6)
    ax.text(vw * 60 + 0.6, ap * 1000, f"{ap}", fontsize=7.5, va="center")
ax.text(32, 22, T("烧伤区", "burn zone"), fontsize=8.5, color=M.RED)
ax.text(30, 1.0, T("不烧伤", "no burn"), fontsize=8.5, color=M.ACCENT)
ax.set_xlabel(T("工件速度 vw / (m/min)", "work speed vw / (m/min)")); ax.set_ylabel(T("切深 ap / µm", "infeed ap / µm"))
ax.set_ylim(0, 30); ax.set_xlim(0, 42); ax.grid(lw=0.3, alpha=0.5); ax.legend(fontsize=7, loc="upper left")
figure(fig, "fig55_5_5")

# ---- 图 55.5.7：仿真车间：修整周期内的温度与烧伤件
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.6, 3.8), sharex=True)
xs = np.arange(1, 41)
wear = [((i % 10) / 30) for i in range(40)]           # 每 10 件修整（与 simulate 的 dress_every=10 一致）
a1.plot(xs, [theta_of(w, 0) for w in wear], "o-", ms=2.5, lw=0.8, color=M.ACCENT, label=T("正常修整", "normal dressing"))
a1.plot(xs, [theta_of(w, ER.PROBLEMS["wheel_dull"]["default"]) for w in wear], "o-", ms=2.5, lw=0.8, color=M.RED,
        label=T("修整不锋利（金刚石笔磨钝）", "blunt dressing diamond"))
a1.axhline(m45["Ac1"], color=M.MUTED, ls="--", lw=0.8); a1.text(41, m45["Ac1"], "Ac1", fontsize=7, va="center", color=M.MUTED)
a1.set_ylabel(T("精磨区最高温度 / ℃", "max. temperature / °C")); a1.set_ylim(280, 920); a1.legend(fontsize=7, loc="upper left", ncol=2); a1.grid(lw=0.3, alpha=0.5)
a2.plot(xs, sim_ok["ra_bearing"], "o", ms=2.8, color=M.ACCENT)
a2.plot(xs, sim_bad["ra_bearing"], "o", ms=2.8, color=M.RED)
for i, bflag in enumerate(sim_bad["burn_bearing"]):
    if bflag:
        a2.plot(i + 1, sim_bad["ra_bearing"][i], "s", ms=6, mfc="none", mec=M.RED, mew=1.0)
a2.axhline(0.8, color=M.RED, ls="--", lw=0.7)
a2.text(1, 0.84, T("Ra 0.8：烧伤件（方框）的粗糙度照样合格", "Ra 0.8: the burnt parts (squares) still pass"), fontsize=7, color=M.RED)
a2.set_ylabel("Ra / µm"); a2.set_ylim(0.3, 1.0); a2.grid(lw=0.3, alpha=0.5)
for k in (10, 20, 30):
    for a in (a1, a2):
        a.axvline(k + 0.5, color=M.MUTED, ls=":", lw=0.6)
a2.set_xlabel(T("零件序号（点线：修整砂轮）", "part number (dotted: dressing)"))
figure(fig, "fig55_5_7")

# ---- 图 55.5.6：SH-101 几种精磨方案的温度
opts = [(T("0.01，20 m/min", "0.01, 20 m/min"), m20, vw, 0.01, 0.5), (T("0.005，20 m/min", "0.005, 20 m/min"), m20, vw, 0.005, 0.5),
        (T("0.002，20 m/min", "0.002, 20 m/min"), m20, vw, 0.002, 0.5), (T("0.002，钝砂轮", "0.002, dull wheel"), m20, vw, 0.002, 4.0),
        (T("0.004，10 m/min", "0.004, 10 m/min"), m20, vw_slow, 0.004, 0.5)]
fig, ax = plt.subplots(figsize=(6.4, 2.9))
for i, (lab, mat, v, ap, A) in enumerate(opts):
    g = S.grinding_temperature(mat, vs, v, ap, de101, A)
    b = S.burn_state(mat, g["theta"], g["t_ms"])
    c = {"none": M.GREEN, "tempering": M.WARM}.get(b["kind"], M.RED)
    ax.bar(i, g["theta"], color=c, width=0.6)
    ax.text(i, g["theta"] + 15, T(f"{g['theta']:.0f} ℃\n{b['name']}", f"{g['theta']:.0f} °C\n{b['kind']}"), ha="center", fontsize=7)
ax.axhline(on20, color=M.WARM, ls="--", lw=0.8); ax.text(4.45, on20, T(f"回火软化\n{on20:.0f} ℃", f"softening\n{on20:.0f} °C"), fontsize=7, va="center", color=M.WARM)
ax.axhline(m20["Ac1"], color=M.RED, ls="--", lw=0.8); ax.text(4.45, m20["Ac1"], "Ac1", fontsize=7, va="center", color=M.RED)
ax.set_xticks(range(len(opts))); ax.set_xticklabels([o[0] for o in opts], fontsize=7.5)
ax.set_ylabel(T("磨削区最高温度 / ℃", "max. temperature / °C")); ax.set_ylim(0, 950); ax.set_xlim(-0.6, 5.1); ax.grid(lw=0.3, alpha=0.5, axis="y")
ax.set_title(T("SH-101 轴承位 Ø25（20CrMnTi 渗碳淬火）的精磨方案：切深 mm，工件速度", "SH-101 journal: infeed mm, work speed"), fontsize=8.5)
figure(fig, "fig55_5_6")

out(de301=de301, lc_r=g_r["lc"], lc_f=g_f["lc"], heq_r=g_r["heq"], heq_f=g_f["heq"], u_r=g_r["u"], u_f=g_f["u"], q_r=g_r["q"], q_f=g_f["q"],
    th_r=g_r["theta"], th_f=g_f["theta"], t_r=g_r["t_ms"], t_f=g_f["t_ms"], pe_r=g_r["peclet"], approx_ratio=g_r["rise"] / g_r["rise_approx"],
    on45=on45, on20=on20, Ac1_45=m45["Ac1"], Ac1_20=m20["Ac1"], ap45=ap45, ap45_um=ap45 * 1000,
    de101=de101, th101_2=cases[0.002]["theta"], th101_5=cases[0.005]["theta"], th101_10=cases[0.01]["theta"],
    b101_5=burns[0.005]["name"], b101_10=burns[0.01]["name"], ap20=ap20, ap20_um=ap20 * 1000, th_dull=g_dull["theta"], b_dull=b_dull["name"],
    ap20_dull_um=ap20_dull * 1000, ap20_slow_um=ap20_slow * 1000, eps=S.EPS_WET,
    n_burn=n_burn, first_burn=first_burn, ra_bad_max=ra_bad_max, dull_m=ER.PROBLEMS["wheel_dull"]["default"])
