"""算例 54.5.1–54.5.3：工艺系统的热变形（hub/accuracy.py）。
54.5.1：磨床开机后砂轮架热伸长按一阶模型 δ(t) = δ∞(1 − e^(−t/τ))（warmup）：δ∞（直径上）0.010 mm、τ = 6 件（仿真车间“未预热”情景的参数），
        预热多久剩余不超过 1 µm；工艺规程工序 60 的单件工时折算成分钟；
54.5.2：仿真车间“磨床未预热”情景磨 40 件，从逐件数据拟合预热段（sequence：磨损锯齿与指数段一起拟合）；
54.5.3：工件磨后马上测量：Ø35 比量具高 10 °C 时读数大多少（thermal_size、measure_temp_error），同温时（钢件钢量具，都是 25 °C）多少。
画图 54.5.2（热伸长与预热）、54.5.3（仿真车间数据与拟合）、54.5.4（工件温度与测量误差）。"""
import math

import _mfg as M
from bookout import T, figure, out, style

A = M.acc()
ER = M.errs()
p = M.plan()
o60 = M.op(p, 60)
cyc = float(o60["minutes"])
dinf, tau = 0.010, 6.0                       # 直径上的热伸长（使直径变小）、时间常数（件），与 sim/errors.py 的 thermal_warmup 相同
n_res = -tau * math.log(0.001 / dinf)        # 剩余热变形 ≤ 1 µm 要磨（或空转）多少件的时间
t_res_min = n_res * cyc
r = ER.simulate(40, "thermal_warmup", seed=545, dress_every=10)
v = r["values"]["bearing_seat_d35"]
resets = [i + 1 for i in r["dress_after"]]
q = A.sequence(v, resets=resets, sigma=0.0012)
assert "warmup" in q["labels"], q["labels"]
wu = q["warmup"]
d = 35.0
e10 = A.thermal_size(d, 10.0)
e_same = A.measure_temp_error(d, 25.0, 25.0)
e_mix = A.measure_temp_error(d, 30.0, 22.0)
n_fail = sum(1 for x in v if x < 35.002)

plt = style()
# ---- 图 54.5.2：砂轮架热伸长与预热
fig, ax = plt.subplots(figsize=(5.8, 3.0))
ts = [0.25 * i for i in range(0, 161)]
ax.plot(ts, [A.warmup(dinf, tau, t) * 1000 for t in ts], color=M.RED, lw=1.6, label=T("砂轮架热伸长（直径上）", "wheelhead growth (on diameter)"))
ax.axhline(dinf * 1000, color=M.MUTED, ls="--", lw=0.8)
ax.text(2, dinf * 1000 + 0.3, T("热平衡 δ∞", "equilibrium δ∞"), fontsize=7.5, color=M.MUTED)
ax.axvspan(0, n_res, color="#f6e7e5")
ax.text(n_res * 0.5, 2.0, T(f"约 {n_res:.0f} 件的时间\n（剩余 ≤ 1 µm）", f"about {n_res:.0f} parts\n(≤ 1 µm left)"), fontsize=7.5, ha="center", color=M.RED)
ax.plot([tau], [A.warmup(dinf, tau, tau) * 1000], "o", color=M.ACCENT, ms=4)
ax.text(tau + 0.4, A.warmup(dinf, tau, tau) * 1000 - 1.2, "t = τ：63%", fontsize=7.5, color=M.ACCENT)
ax.set_xlabel(T("开机后的时间（折算成磨削的件数）", "time after start-up (in parts ground)")); ax.set_ylabel(T("热伸长 / µm", "growth / µm"))
ax.set_xlim(0, ts[-1]); ax.set_ylim(0, 12); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_5_2")

# ---- 图 54.5.3：仿真车间“磨床未预热”：逐件测得值与拟合
fig, ax = plt.subplots(figsize=(6.4, 3.1))
xs = list(range(1, 41))
ax.plot(xs, v, "o", ms=3.5, color=M.ACCENT, label=T("左轴承位测得值", "left bearing seat measured"))
fit = []
pos = [0] * 40
cuts = [0] + resets + [40]
for k in range(len(cuts) - 1):
    for i in range(cuts[k], cuts[k + 1]):
        pos[i] = i - cuts[k]
c0 = sum(v[i] - wu["slope"] * pos[i] - wu["delta_inf"] * (1 - math.exp(-i / wu["tau"])) for i in range(40)) / 40
fit = [c0 + wu["slope"] * pos[i] + wu["delta_inf"] * (1 - math.exp(-i / wu["tau"])) for i in range(40)]
ax.plot(xs, fit, color=M.RED, lw=1.2, label=T(f"拟合：预热段 τ = {wu['tau']:.1f} 件，δ∞ = {wu['delta_inf'] * 1000:.1f} µm；磨损锯齿", f"fit: τ = {wu['tau']:.1f} parts, δ∞ = {wu['delta_inf'] * 1000:.1f} µm; wear saw"))
for y in (35.002, 35.018):
    ax.axhline(y, color=M.RED, ls="--", lw=0.7)
for rr in resets:
    ax.axvline(rr + 0.5, color=M.MUTED, ls=":", lw=0.6)
ax.set_xlabel(T("零件序号（开机后）", "part number (after start-up)")); ax.set_ylabel(T("直径 / mm", "diameter / mm"))
ax.set_ylim(34.99, 35.02); ax.legend(fontsize=7.2, loc="upper right"); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_5_3")

# ---- 图 54.5.4：工件温度与测量误差
fig, ax = plt.subplots(figsize=(5.8, 3.0))
dTs = [0.5 * i for i in range(0, 41)]
for dd, col in ((35.0, M.ACCENT), (80.0, M.WARM), (200.0, M.RED)):
    ax.plot(dTs, [A.thermal_size(dd, x) * 1000 for x in dTs], color=col, label=f"Ø{dd:g}")
ax.axhline(16, color=M.MUTED, ls="--", lw=0.8)
ax.text(0.5, 16.5, T("k6 公差 16 µm（Ø35）", "k6 tolerance 16 µm (Ø35)"), fontsize=7.5, color=M.MUTED)
ax.plot([10], [e10 * 1000], "o", color=M.ACCENT, ms=5)
ax.text(10.5, e10 * 1000 - 2, f"{e10 * 1000:.1f} µm", fontsize=7.5, color=M.ACCENT)
ax.set_xlabel(T("工件比量具高的温度 ΔT / °C", "work warmer than the gauge ΔT / °C")); ax.set_ylabel(T("读数偏大 / µm", "reading too large / µm"))
ax.set_ylim(0, 40); ax.legend(fontsize=7.5); ax.grid(lw=0.3, alpha=0.5)
figure(fig, "fig54_5_4")

out(cyc=cyc, dinf_um=dinf * 1000, tau=tau, tau_min=tau * cyc, n_res=n_res, t_res_min=t_res_min, wu_tau=wu["tau"], wu_dinf_um=wu["delta_inf"] * 1000,
    wu_slope_um=wu["slope"] * 1000, e10_um=e10 * 1000, e_same_um=e_same * 1000, e_mix_um=e_mix * 1000, n_fail=n_fail, first=v[0], last10=sum(v[-10:]) / 10)
