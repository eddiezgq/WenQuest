"""7.4 载荷谱：从运行记录到设计载荷（算例 7.4.1、7.4.2，图 7.4.1）。
1. 雨流计数（ASTM E1049-85，_ch7.rainflow）先用标准里的例子核对，再处理跑合试验台“工况模拟”段的转矩记录（三次起停）；
   与数字孪生客户现场的边缘端做法对照——边缘端把每次起停记成一个 0 → 峰值 → 0 的大循环，把运行中的波动记成幅值约 8% 额定的小循环。
2. 矿山皮带机一年的雨流结果（数字孪生）画成累积频次图（载荷谱），外推到设计寿命 20 000 运行小时；
   按输出轴 S-N 曲线的斜率 m = 9 求“与起停次数等效”的当量转矩幅值，作为第 11 章疲劳校核的设计载荷。"""
import numpy as np

import _ch7 as H
from bookout import T, figure, out, style

LIFE_H = 20000.0
M_SH = H.TM.SHAFT_MAT["k"]
# 1. 核对：ASTM E1049-85 图 6 的例子 −2, 1, −3, 5, −1, 3, −4, 4, −2（单位任意）
astm = H.rainflow([-2, 1, -3, 5, -1, 3, -4, 4, -2])
by_range = {}
for r_, m_, n_ in astm:
    by_range[r_] = by_range.get(r_, 0) + n_
ASTM_EXPECT = {3: 0.5, 4: 1.5, 6: 0.5, 8: 1.0, 9: 0.5}                 # 标准表 4 的结果
astm_ok = by_range == ASTM_EXPECT
# 跑合试验台记录
tb, yb, rec = H.bench()
cyc = H.rainflow(yb)
big = [c for c in cyc if c[0] > 0.5 * H.RATED]
small = [c for c in cyc if c[0] <= 0.5 * H.RATED]
n_big = sum(c[2] for c in big)
n_small = sum(c[2] for c in small)
run_s = 3 * 20.0                                                     # 三段稳定运行，每段约 20 s（记录的 2–22 s）
amp_small = np.array([c[0] / 2 for c in small for _ in range(int(round(c[2] * 2)))])
a95 = float(np.percentile(amp_small, 95))
peaks = [max(yb[k * 250:(k + 1) * 250]) for k in range(3)]
# 2. 矿山皮带机一年 → 20 000 h
days = H.site_year("mine")
run_h = sum(d["run_h"] for d in days)
spec = {}
for d in days:
    for a, m, n in d["rainflow"]:
        spec[a] = spec.get(a, 0) + n
scale = LIFE_H / run_h
amps = np.array(sorted(spec, reverse=True), dtype=float)
counts = np.array([spec[a] for a in sorted(spec, reverse=True)]) * scale
cum = np.cumsum(counts)
n_starts = sum(n for d in days for a, m, n in d["rainflow"] if a == m) * scale
a_eq = (np.sum(counts * amps ** M_SH) / n_starts) ** (1 / M_SH)      # 与起停次数等效的当量幅值
a_max = float(amps.max())
damage_share_run = 100 * float(np.sum([c * a ** M_SH for a, c in zip(amps, counts) if a < 0.25 * H.RATED]) / np.sum(counts * amps ** M_SH))

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.1))
t = np.array(tb)
a0.plot(t, yb, color=H.INK, lw=0.6)
for k, p in enumerate(peaks):
    i = int(np.argmax(yb[k * 250:(k + 1) * 250])) + k * 250
    a0.annotate("", xy=(t[i] + 0.5, p), xytext=(t[i] + 0.5, 0), arrowprops=dict(arrowstyle="<->", color="#d62728", lw=0.8))
a0.text(26, 560, T(f"大循环 {n_big:g} 次（起停）", f"{n_big:g} large cycles (start–stop)"), fontsize=6.4, color="#d62728")
a0.text(28, 60, T(f"小循环 {n_small:g} 次（运行波动）", f"{n_small:g} small cycles (running ripple)"), fontsize=6.4, color="#1f77b4")
a0.set_xlabel(T("时间 / s", "Time / s"), fontsize=7.2)
a0.set_ylabel(T("输出转矩 / N·m", "Output torque / N·m"), fontsize=7.2)
a0.tick_params(labelsize=6.3)
a0.set_title(T("(a) 跑合试验台记录的雨流计数", "(a) Rainflow count of the run-in bench record"), fontsize=7.6)
a1.step(cum, amps, where="post", color="#d62728", lw=1.3, label=T("矿山皮带机，外推到 20 000 h", "mine conveyor, extrapolated to 20 000 h"))
a1.axhline(a_eq, color="#1f77b4", lw=0.9, ls="--", label=T(f"当量幅值 {a_eq:.0f} N·m（m = {M_SH:.0f}）", f"equivalent amplitude {a_eq:.0f} N·m (m = {M_SH:.0f})"))
a1.set_xscale("log")
a1.set_xlabel(T("累积循环次数（幅值 ≥ 纵坐标）", "Cumulative cycles (amplitude ≥ ordinate)"), fontsize=7.2)
a1.set_ylabel(T("转矩幅值 / N·m", "Torque amplitude / N·m"), fontsize=7.2)
a1.legend(fontsize=6.2, frameon=False, loc="upper right")
a1.tick_params(labelsize=6.3)
a1.set_title(T("(b) 载荷谱（累积频次图）", "(b) Load spectrum (cumulative frequency)"), fontsize=7.6)
fig.tight_layout()
figure(fig, "fig7_4_1")

out(astm_ok=T("一致", "agrees") if astm_ok else T("不一致", "differs"), n_big=n_big, n_small=n_small, small_per_s=n_small / run_s, a95=a95,
    twin_ripple=round(0.08 * H.RATED / 5) * 5, peak_lo=min(peaks), peak_hi=max(peaks), big_range_lo=min(c[0] for c in big),
    big_range_hi=max(c[0] for c in big), run_h=run_h, life_h=LIFE_H, years=LIFE_H / run_h, scale=scale, n_starts=n_starts,
    n_total=float(cum[-1]), n_total_m=float(cum[-1]) / 1e4, a_eq=a_eq, a_max=a_max, peak_eq=2 * a_eq, m_sh=M_SH, damage_share_run=damage_share_run)
