# -*- coding: utf-8 -*-
"""第 27 章数据图（中英两版）：fig_27_spc、fig_27_field、fig_27_roi。
python3 figsrc/ch27_figs.py  → img/fig_27_*.png 与 img/en/fig_27_*.png"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import ch27_model as M  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = "#faf9f5"
INK, MUTED, RULE = "#1b2430", "#5a6570", "#d8dde1"
BLUE, ORANGE, GREEN, RED, PURPLE, TEAL, YEL = "#2a6fdb", "#e0662f", "#2e9e5b", "#c0392b", "#8a5cc7", "#14797f", "#c48a17"
plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "DejaVu Sans"], "font.size": 11, "axes.edgecolor": RULE,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.titleweight": "bold",
                     "axes.titlesize": 12.5, "axes.titlecolor": INK, "axes.unicode_minus": False})

T = {
 "zh": dict(
  spc_title="梭尖间隙的质量闭环：漂移、报警与受影响整机",
  spc_sub="算例（示意）：平均 22.5 台/h，σ = 6 µm，公差 0.04–0.10 mm；第 2 h（#46）起换用旋梭批次 H2610-07，间隙以 4 µm/h 漂移；子组 n = 5；报警后 0.5 h 隔离",
  ind="逐台测量值（调试工位 ADJ）", sn="序列号", gap="梭尖间隙 (mm)", lim="公差限", lotb="旋梭批次 H2610-07",
  ff="首台超差 #174", xbar="X̄ 控制图（连续 5 台一组）", sg="子组号", xbm="子组均值 (mm)",
  r2="R2 报警 #70", r1="R1 报警 #100", bars="晚发现的代价（起点：R1–R4 在 #70 报警）",
  late="比 SPC 报警晚发现的时间 (h)", cnt="台数", aff="受影响整机（须复检）", rw="超差返工", sh="已发货（8 h 发运）",
  tol="只按超差", note="控制限按基准 μ₀ = 0.070 mm、σ/√5 计算。只用 R1 时在 #100 报警；加上 R2–R4 后在 #70 报警。只靠逐台判超差，要到 #174 才开出第一张 NCR。"),
 "en": dict(
  spc_title="Quality loop for hook-point clearance: drift, alarm and affected machines",
  spc_sub="Illustrative: 22.5 machines/h, σ = 6 µm, tol. 0.04–0.10 mm; from hour 2 (#46) hook lot H2610-07, drift 4 µm/h; n = 5; lot withdrawn 0.5 h after an alarm",
  ind="Individual readings (adjustment station ADJ)", sn="Serial no.", gap="Hook-point clearance (mm)", lim="Tolerance limits", lotb="Hook lot H2610-07",
  ff="first out-of-spec #174", xbar="X̄ chart (5 consecutive machines per subgroup)", sg="Subgroup", xbm="Subgroup mean (mm)",
  r2="R2 alarm #70", r1="R1 alarm #100", bars="The cost of finding out late (from the R1–R4 alarm at #70)",
  late="Hours later than the SPC alarm", cnt="Machines", aff="Affected machines (re-check)", rw="Out of spec (rework)", sh="Already shipped (8 h despatch)",
  tol="Tolerance only", note="Limits from baseline μ₀ = 0.070 mm and σ/√5. With R1 alone the alarm comes at #100; adding R2–R4 brings it to #70. Relying on per-machine tolerance checks, the first NCR opens only at #174."),
}


def save(fig, name, lang):
    d = os.path.join(ROOT, "img") if lang == "zh" else os.path.join(ROOT, "img", "en")
    os.makedirs(d, exist_ok=True)
    fig.savefig(os.path.join(d, name), dpi=2000 / fig.get_figwidth(), facecolor=BG)
    plt.close(fig)


def header(fig, title, sub):
    fig.text(0.025, 0.965, title, fontsize=18, fontweight="bold", color=INK, va="top")
    fig.text(0.025, 0.915, sub, fontsize=11.5, color=MUTED, va="top")


def style(ax):
    ax.set_facecolor("white")
    ax.grid(True, color="#e7eaec", lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- 图 27-5 SPC
def fig_spc(lang):
    L = T[lang]
    p = dict(M.Q)
    vals, lots = M.values(p)                     # 不隔离时的完整漂移（显示用）
    N = len(vals)
    n0 = round(p["t0"] * p["rate"])
    fig = plt.figure(figsize=(14, 8.2))
    header(fig, L["spc_title"], L["spc_sub"])
    ax1 = fig.add_axes([0.065, 0.53, 0.52, 0.30]); style(ax1)
    ax2 = fig.add_axes([0.065, 0.13, 0.52, 0.30]); style(ax2)
    ax3 = fig.add_axes([0.665, 0.13, 0.31, 0.70]); style(ax3)
    xs = list(range(1, 201))
    ax1.axvspan(n0 + 0.5, 200, color="#fbf4e3", lw=0)
    ax1.plot(xs, vals[:200], ".", ms=3.2, color=BLUE)
    for y in (p["lsl"], p["usl"]):
        ax1.axhline(y, color=RED, lw=1.2, ls="--")
    ff = M.first_fail(vals, p)
    ax1.plot([ff], [vals[ff - 1]], "o", mfc="none", mec=RED, ms=9, mew=1.6)
    ax1.annotate(L["ff"], (ff, vals[ff - 1]), xytext=(ff - 75, 0.106), color=RED, fontsize=9.5,
                 arrowprops=dict(arrowstyle="-", color=RED, lw=0.8))
    ax1.text(n0 + 3, 0.1105, L["lotb"] + " →", color=YEL, fontsize=10, va="top")
    ax1.set_ylim(0.03, 0.115); ax1.set_xlim(0, 201)
    ax1.set_title(L["ind"], loc="left"); ax1.set_ylabel(L["gap"], fontsize=9.5)
    # X̄
    k = p["sub"]; s = p["sigma"] / math.sqrt(k); c = p["mu0"]
    xb = [sum(vals[i - k:i]) / k for i in range(k, 201, k)]
    sg = list(range(1, len(xb) + 1))
    ax2.axvspan(n0 / k + 0.5, len(xb) + 0.5, color="#fbf4e3", lw=0)
    for m, ls, col in ((0, "-", MUTED), (1, ":", "#9aa4ae"), (-1, ":", "#9aa4ae"), (2, "--", "#9aa4ae"), (-2, "--", "#9aa4ae"),
                       (3, "-", RED), (-3, "-", RED)):
        ax2.axhline(c + m * s, color=col, lw=1 if abs(m) < 3 else 1.3, ls=ls)
    ax2.plot(sg, xb, "-o", ms=3.5, color=BLUE, lw=1)
    for n, lab in ((70, L["r2"]), (100, L["r1"])):
        g = n // k
        ax2.plot([g], [xb[g - 1]], "o", mfc="none", mec=ORANGE, ms=10, mew=1.8)
        ax2.annotate(lab, (g, xb[g - 1]), xytext=(g - 13 if n == 70 else g + 2, xb[g - 1] + 0.006),
                     color=ORANGE, fontsize=9.5, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
    for m, lab in ((3, "UCL"), (-3, "LCL"), (0, "CL")):
        ax2.text(len(xb) + 0.8, c + m * s, lab, fontsize=8.5, color=MUTED, va="center")
    ax2.set_xlim(0, len(xb) + 3); ax2.xaxis.set_label_coords(0.5, -0.12)
    ax2.set_title(L["xbar"], loc="left"); ax2.set_xlabel(L["sg"]); ax2.set_ylabel(L["xbm"], fontsize=9.5)
    # 晚发现
    lates = [0, 1, 2, 3, 4, 5, 6]
    aff, rw, sh = [], [], []
    for lt in lates:
        o = M.outcome(p, M.RULES, late_h=lt)
        aff.append(o["affected"]); rw.append(o["rework"]); sh.append(o["shipped"])
    xx = list(range(len(lates)))
    ax3.bar([x - 0.27 for x in xx], aff, 0.27, color=YEL, label=L["aff"])
    ax3.bar(xx, rw, 0.27, color=RED, label=L["rw"])
    ax3.bar([x + 0.27 for x in xx], sh, 0.27, color=PURPLE, label=L["sh"])
    for x, a in zip(xx, aff):
        ax3.text(x - 0.27, a + 3, str(a), ha="center", fontsize=8.5, color=INK)
    for x, a in zip(xx, rw):
        if a:
            ax3.text(x, a + 3, str(a), ha="center", fontsize=8.5, color=RED)
    ax3.set_xticks(xx); ax3.set_xticklabels([str(v) for v in lates])
    ax3.set_xlabel(L["late"]); ax3.set_ylabel(L["cnt"])
    ax3.set_ylim(0, 215)
    ax3.legend(loc="upper left", fontsize=9, frameon=False)
    ax3.set_title(L["bars"], loc="left", fontsize=10.5, wrap=True)
    fig.text(0.025, 0.02, L["note"], fontsize=10, color=MUTED)
    save(fig, "fig_27_spc.png", lang)


# ---------------------------------------------------------------- 图 27-7 服务数据
FAULTS = [  # 故障码, 中文, 英文, FW 1.4.x 每千运转小时, FW 1.5.0（示意数据）
    ("E-31", "剪线电磁铁过流", "Trim solenoid overcurrent", 0.62, 0.18),
    ("E-12", "编码器信号丢失", "Encoder signal lost", 0.21, 0.20),
    ("E-07", "主轴过载", "Spindle overload", 0.17, 0.16),
    ("E-44", "停针超时", "Needle-positioning timeout", 0.14, 0.05),
    ("E-52", "电控箱过热", "Control box overheat", 0.11, 0.10),
]


def fig_field(lang):
    zh = lang == "zh"
    fig = plt.figure(figsize=(14, 6.4))
    header(fig, "服务数据回流：故障码按固件版本比较，旋梭备件按运转小时预测" if zh else
           "Field data coming back: fault codes by firmware version, spare hooks forecast from running hours",
           "示意：联网机群 6000 台（客户同意回传）；故障率 = 次数 / 千运转小时；旋梭寿命按韦布尔分布 β = 2.2、η = 5000 h（示意值）" if zh else
           "Illustrative: 6000 connected machines (customers consented); fault rate = events per 1000 running hours; hook life Weibull β = 2.2, η = 5000 h")
    ax1 = fig.add_axes([0.19, 0.14, 0.33, 0.66]); style(ax1)
    ax2 = fig.add_axes([0.62, 0.14, 0.35, 0.66]); style(ax2)
    ys = list(range(len(FAULTS)))[::-1]
    a = [f[3] for f in FAULTS]; b = [f[4] for f in FAULTS]
    ax1.barh([y + 0.2 for y in ys], a, 0.38, color="#9aa4ae", label="FW 1.4.x")
    ax1.barh([y - 0.2 for y in ys], b, 0.38, color=TEAL, label="FW 1.5.0")
    ax1.set_yticks(ys); ax1.set_yticklabels(["{} {}".format(f[0], f[1] if zh else f[2]) for f in FAULTS], fontsize=9.5)
    ax1.set_xlabel("次 / 千运转小时" if zh else "events per 1000 running h")
    ax1.legend(frameon=False, fontsize=9.5, loc="lower right")
    ax1.set_title("故障码（每千运转小时）" if zh else "Fault codes per 1000 running hours", loc="left")
    # 旋梭预测：8 个季度
    fl = M.fleet()
    use, cal = [], []
    for q in range(8):
        f2 = [(h, ch + h * 0.25 * q) for h, ch in fl]
        u, c_, _ = M.hook_forecast(f2)
        use.append(u); cal.append(c_)
    xs = list(range(1, 9))
    ax2.plot(xs, cal, "--o", color="#9aa4ae", ms=4, label="按平均寿命（日历平均）" if zh else "From mean life (calendar average)")
    ax2.plot(xs, use, "-o", color=ORANGE, ms=4, label="按每台累计运转小时" if zh else "From each machine's running hours")
    for x, v in ((1, use[0]), (1, cal[0])):
        ax2.text(x + 0.15, v + 4, "{:.0f}".format(v), fontsize=9, color=INK)
    ax2.set_xlabel("未来季度" if zh else "Quarter ahead"); ax2.set_ylabel("旋梭需求（只）" if zh else "Hooks needed")
    ax2.set_ylim(0, max(cal) * 1.35)
    ax2.legend(frameon=False, fontsize=9.5, loc="lower right")
    ax2.set_title("旋梭备件需求预测" if zh else "Spare-hook demand forecast", loc="left")
    save(fig, "fig_27_field.png", lang)
    return use, cal


# ---------------------------------------------------------------- 图 27-9 回收
def fig_roi(lang):
    zh = lang == "zh"
    sav = [sum(s.values()) for s in M.savings()]
    cum, pay = M.cashflow(M.PH, sav)
    c1, p1 = M.cashflow(M.PH[:1], sav[:1])
    fig = plt.figure(figsize=(14, 6.4))
    header(fig, "分期实施的累计现金流（算例）" if zh else "Cumulative cash flow of the phased roll-out (worked example)",
           "示意值（万元）：投资 150 / 120 / 80，年节省 {:.0f} / {:.0f} / {:.0f}；上线后 6 个月爬升到全额；运行费为投资的 15%/年".format(*sav) if zh else
           "Illustrative (10k CNY): investment 150 / 120 / 80, annual savings {:.0f} / {:.0f} / {:.0f}; 6-month ramp after go-live; running cost 15 %/yr of investment".format(*sav))
    ax = fig.add_axes([0.08, 0.14, 0.88, 0.66]); style(ax)
    ms = list(range(1, len(cum) + 1))
    cols = [BLUE, GREEN, PURPLE]
    for ph, col in zip(M.PH, cols):
        ax.axvspan(ph["start"] + 0.5, ph["start"] + ph["build"] + 0.5, color=col, alpha=0.07, lw=0)
        ax.text(ph["start"] + ph["build"] / 2 + 0.5, 470, (ph["name"] + "建设" if zh else
                {"第一期": "Phase 1", "第二期": "Phase 2", "第三期": "Phase 3"}[ph["name"]] + " build"),
                ha="center", fontsize=9.5, color=col)
    ax.axhline(0, color=INK, lw=1)
    ax.plot(ms, c1, "--", color="#9aa4ae", lw=1.5, label="只做第一期" if zh else "Phase 1 only")
    ax.plot(ms, cum, "-", color=ORANGE, lw=2.2, label="三期全做" if zh else "All three phases")
    ax.plot([pay], [cum[pay - 1]], "o", color=ORANGE, ms=7)
    ax.annotate(("回收：第 {} 月" if zh else "Payback: month {}").format(pay), (pay, cum[pay - 1]),
                xytext=(pay + 2, -150), fontsize=10, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE))
    ax.plot([p1], [c1[p1 - 1]], "o", color="#9aa4ae", ms=6)
    ax.annotate(("第 {} 月" if zh else "month {}").format(p1), (p1, c1[p1 - 1]), xytext=(p1 - 6, 110), fontsize=9.5,
                color=MUTED, arrowprops=dict(arrowstyle="-", color="#9aa4ae"))
    mn = min(cum); im = cum.index(mn) + 1
    ax.annotate(("最低 {:.0f}" if zh else "low point {:.0f}").format(mn), (im, mn), xytext=(im + 3, mn - 10), fontsize=9.5, color=INK)
    ax.text(len(cum), cum[-1] + 15, "{:.0f}".format(cum[-1]), ha="right", fontsize=9.5, color=ORANGE)
    ax.set_xlim(0, len(cum) + 1); ax.set_ylim(-260, 620)
    ax.set_xlabel("月" if zh else "Month"); ax.set_ylabel("累计现金流（万元）" if zh else "Cumulative cash flow (10k CNY)")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    save(fig, "fig_27_roi.png", lang)


if __name__ == "__main__":
    for lg in ("zh", "en"):
        fig_spc(lg)
        u, c = fig_field(lg)
        fig_roi(lg)
    print("hook use", [round(x) for x in u], "cal", [round(x) for x in c])
