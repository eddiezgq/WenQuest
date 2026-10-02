# -*- coding: utf-8 -*-
"""第 22 章数据图（中英两版）：python3 figsrc/ch22_figs.py
输出 img/fig_c22_{intro,stats,case}.png 和 img/en/ 下同名英文版。模型见 ch22_model.py。"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import ch22_model as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = "#faf9f5"; INK = "#1b2430"; MUT = "#5a6570"; RULE = "#d8dde1"
BLUE = "#2a6fdb"; RED = "#c0392b"; ORG = "#e0662f"; GRN = "#2e9e5b"; PUR = "#8a5cc7"; TEAL = "#14797f"
plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "DejaVu Sans"], "font.size": 11, "axes.edgecolor": RULE,
                     "axes.labelcolor": INK, "xtick.color": MUT, "ytick.color": MUT, "axes.grid": True,
                     "grid.color": RULE, "grid.linewidth": .8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12.5, "axes.titlelocation": "left",
                     "figure.facecolor": BG, "axes.facecolor": "white", "savefig.facecolor": BG, "legend.frameon": False})

T = {
 "zh": dict(
  i_title="只在高速时出现的剪线失败", i_sub="算例：固件 v1.4.0“快速剪线”优化前后，停车剪线失败概率与起始转速的关系（HIL 电机模型；κ 为电网电压使电机基速变化的系数，示意值）",
  i_a="一次剪线失败的概率", i_x="松开脚踏时的主轴转速（r/min）", i_y="失败概率（%，对数刻度）",
  i_hand="手工试缝常用的转速", i_l1="v1.3.2（减速按 60% 能力）", i_l2="v1.4.0（HIL：电机有恒功率区）",
  i_l3="v1.4.0（SIL：理想电机）", i_l4="v1.4.1（修复后）",
  i_b="剪线电磁铁发令时（290°）的主轴转速", i_y2="发令时转速（r/min）", i_lim="进刀晚于 330° 的风险区（延迟 10 ms 时 > 667 r/min）",
  s_title="要测多少次才算数", s_sub="零失效验证、有失效时的置信下限、停针误差的过程能力（算例，示意值）",
  s_a="零失效验证需要的试验次数", s_ax="要验证的可靠度 R（%）", s_ay="试验次数 n",
  s_b="1000 次剪线、x 次失败时的置信下限（C = 95%）", s_bx="失败次数 x", s_by="可靠度下限（%）", s_req="要求 99.5%",
  s_c="停针误差：50 次停车（HIL）", s_cx="停针误差（°）", s_cy="次数", s_usl="上限 1°",
  c_title="案例：HIL 当晚发现、二分定位、修复、回归", c_sub="算例：从 5000 r/min 停车剪线（示意值）",
  c_a="每晚 HIL：5000 r/min 剪线 250 次的失败数", c_ay="失败次数", c_night="夜",
  c_b="二分：23 个提交，5 轮", c_bx="提交序号", c_good="通过", c_bad="失败",
  c_c="剪线针里的转速（从 5000 r/min 停车）", c_cx="剪线针内的主轴转角（°）", c_cy="主轴转速（r/min）",
  c_cmd="发令 290°", c_v13="v1.3.2", c_v140="v1.4.0", c_v141="v1.4.1",
  zero="零失效", ),
 "en": dict(
  i_title="A trimming failure that appears only at high speed", i_sub="Worked example: probability of a failed trim versus the speed at which the stop begins, before and after the v1.4.0 \"fast trim\" change (HIL motor model; κ scales the motor base speed with mains voltage; illustrative)",
  i_a="Probability that one trim fails", i_x="Spindle speed when the pedal is released (r/min)", i_y="Failure probability (%, log scale)",
  i_hand="Speeds used in hand trials", i_l1="v1.3.2 (deceleration at 60 % capability)", i_l2="v1.4.0 (HIL: motor has a constant-power region)",
  i_l3="v1.4.0 (SIL: ideal motor)", i_l4="v1.4.1 (fixed)",
  i_b="Spindle speed when the trimmer solenoid is fired (290°)", i_y2="Speed at firing (r/min)", i_lim="Risk of knife entry after 330° (> 667 r/min at 10 ms delay)",
  s_title="How many tests are enough", s_sub="Zero-failure demonstration, the lower confidence bound with failures, and process capability of the stop error (worked example; illustrative)",
  s_a="Trials needed for a zero-failure demonstration", s_ax="Reliability to demonstrate, R (%)", s_ay="Number of trials n",
  s_b="1000 trims with x failures: lower bound (C = 95 %)", s_bx="Failures x", s_by="Lower bound on reliability (%)", s_req="Required 99.5 %",
  s_c="Stop error: 50 stops on the HIL rig", s_cx="Stop error (°)", s_cy="Count", s_usl="Limit 1°",
  c_title="Case: caught by the nightly HIL run, bisected, fixed, regression-tested", c_sub="Worked example: trimming from 5000 r/min (illustrative)",
  c_a="Nightly HIL: failures in 250 trims from 5000 r/min", c_ay="Failures", c_night="Night",
  c_b="Bisection: 23 commits, 5 rounds", c_bx="Commit index", c_good="pass", c_bad="fail",
  c_c="Speed during the trimming stitch (stop from 5000 r/min)", c_cx="Spindle angle within the trimming stitch (°)", c_cy="Spindle speed (r/min)",
  c_cmd="fire at 290°", c_v13="v1.3.2", c_v140="v1.4.0", c_v141="v1.4.1",
  zero="zero failures", ),
}


def head(fig, t, title, sub):
    fig.text(0.012, 0.975, title, fontsize=17, fontweight="bold", color=INK, va="top")
    fig.text(0.012, 0.915, sub, fontsize=11.5, color=MUT, va="top")


def save(fig, lang, name):
    out = os.path.join(ROOT, "img", ("en/" if lang == "en" else "") + f"fig_c22_{name}.png")
    fig.savefig(out, dpi=118)
    plt.close(fig)
    print(out)


SPEEDS = np.arange(3000, 5251, 125)
P = {k: np.array([M.p_trim(n, v, mo) for n in SPEEDS]) for k, v, mo in
     (("v132", "v1.3.2", "hil"), ("v140", "v1.4.0", "hil"), ("v140s", "v1.4.0", "sil"), ("v141", "v1.4.1", "hil"))}
NC = {}
for v in ("v1.3.2", "v1.4.0", "v1.4.1"):
    NC[v] = [M.n_at_cmd(n, M.FW[v]["plan"], M.NB0)[0] for n in SPEEDS]
    NC[v + "lo"] = [M.n_at_cmd(n, M.FW[v]["plan"], M.NB0 * 0.9)[0] for n in SPEEDS]

stops = {kp: M.stop_sample(kp, 50, seed=7) for kp in (200, 300)}

traces = {}
for v in ("v1.3.2", "v1.4.0", "v1.4.1"):
    tr = []
    M.n_at_cmd(5000, M.FW[v]["plan"], M.NB0, trace=tr)
    traces[v] = np.array(tr)

for lang in ("zh", "en"):
    t = T[lang]
    # ---------- intro ----------
    fig = plt.figure(figsize=(17, 7.2))
    head(fig, t, t["i_title"], t["i_sub"])
    ax = fig.add_axes([0.06, 0.12, 0.42, 0.68]); ax2 = fig.add_axes([0.56, 0.12, 0.42, 0.68])
    ax.axvspan(3000, 4000, color=GRN, alpha=.08); ax.text(3500, 60, t["i_hand"], ha="center", color=GRN, fontsize=10.5)
    ax.semilogy(SPEEDS, P["v132"] * 100, color=MUT, lw=2.2, label=t["i_l1"])
    ax.semilogy(SPEEDS, P["v140"] * 100, color=RED, lw=2.6, label=t["i_l2"])
    ax.semilogy(SPEEDS, P["v140s"] * 100, color=BLUE, lw=1.8, ls="--", label=t["i_l3"])
    ax.semilogy(SPEEDS, P["v141"] * 100, color=GRN, lw=1.8, ls=":", label=t["i_l4"])
    ax.axhline(0.5, color=ORG, lw=1.2, ls="--"); ax.text(3020, 0.6, "0.5 %", color=ORG, fontsize=10)
    ax.set_ylim(0.005, 100); ax.set_xlim(3000, 5250)
    ax.set_title(t["i_a"]); ax.set_xlabel(t["i_x"]); ax.set_ylabel(t["i_y"])
    ax.legend(loc="upper left", fontsize=9.8, bbox_to_anchor=(0.0, 0.93))
    for n0 in (4750, 5000):
        p = M.p_trim(n0, "v1.4.0")
        ax.annotate(f"{p*100:.1f} %", (n0, p * 100), xytext=(-48, 8), textcoords="offset points", color=RED, fontsize=10.5, fontweight="bold")
    ax2.fill_between([3000, 5250], 667, 1600, color=RED, alpha=.07); ax2.text(3050, 1450, t["i_lim"], color=RED, fontsize=10)
    ax2.plot(SPEEDS, NC["v1.3.2"], color=MUT, lw=2.2, label=t["i_l1"])
    ax2.plot(SPEEDS, NC["v1.4.0"], color=RED, lw=2.6, label=t["i_l2"] + " κ=1")
    ax2.plot(SPEEDS, NC["v1.4.0lo"], color=RED, lw=1.4, ls="--", label=t["i_l2"] + " κ=0.9")
    ax2.plot(SPEEDS, NC["v1.4.1lo"], color=GRN, lw=1.8, ls=":", label=t["i_l4"] + " κ=0.9")
    ax2.set_ylim(0, 1600); ax2.set_xlim(3000, 5250)
    ax2.set_title(t["i_b"]); ax2.set_xlabel(t["i_x"]); ax2.set_ylabel(t["i_y2"])
    ax2.legend(loc="center left", fontsize=9.8, bbox_to_anchor=(0, 0.62))
    save(fig, lang, "intro")

    # ---------- stats ----------
    fig = plt.figure(figsize=(17, 6.8))
    head(fig, t, t["s_title"], t["s_sub"])
    a1 = fig.add_axes([0.05, 0.12, 0.27, 0.66]); a2 = fig.add_axes([0.385, 0.12, 0.27, 0.66]); a3 = fig.add_axes([0.715, 0.12, 0.27, 0.66])
    Rs = np.linspace(0.98, 0.999, 200)
    for C, col in ((0.90, TEAL), (0.95, BLUE), (0.99, PUR)):
        a1.plot(Rs * 100, np.log(1 - C) / np.log(Rs), color=col, lw=2.2, label=f"C = {C*100:.0f} %")
    a1.plot([99.5], [598], "o", color=RED); a1.annotate("R = 99.5 %, C = 95 %\nn = 598", (99.5, 598), xytext=(-150, 60), textcoords="offset points",
                                                      color=RED, fontsize=10.5, arrowprops=dict(arrowstyle="->", color=RED))
    a1.set_yscale("log"); a1.set_xlim(98, 99.9); a1.set_title(t["s_a"]); a1.set_xlabel(t["s_ax"]); a1.set_ylabel(t["s_ay"]); a1.legend(loc="upper left")
    xs = np.arange(0, 7)
    rl = [M.r_lower(1000, x) * 100 for x in xs]
    cols = [GRN if r >= 99.5 else RED for r in rl]
    a2.bar(xs, [r - 98.5 for r in rl], bottom=98.5, color=cols, width=.6)
    for x, r in zip(xs, rl):
        a2.text(x, r + 0.02, f"{r:.2f}", ha="center", fontsize=10, color=INK)
    a2.axhline(99.5, color=ORG, ls="--", lw=1.4); a2.text(4.2, 99.53, t["s_req"], color=ORG, fontsize=10.5)
    a2.set_ylim(98.5, 100); a2.set_title(t["s_b"]); a2.set_xlabel(t["s_bx"]); a2.set_ylabel(t["s_by"])
    bins = np.linspace(0, 1.3, 40)
    for kp, col in ((200, GRN), (300, RED)):
        x = stops[kp]
        a3.hist(x, bins=bins, color=col, alpha=.75, label=f"Kp = {kp} s⁻¹: μ = {x.mean():.2f}°, σ = {x.std(ddof=1):.3f}°, Cpk = {M.cpu(x):.2f}")
    a3.axvline(1.0, ymax=0.84, color=ORG, ls="--", lw=1.6); a3.text(1.02, 14, t["s_usl"], color=ORG, fontsize=10.5)
    a3.set_title(t["s_c"]); a3.set_xlabel(t["s_cx"]); a3.set_ylabel(t["s_cy"]); a3.set_ylim(0, 34); a3.legend(loc="upper left", bbox_to_anchor=(0.2, 1.0), fontsize=9.3)
    save(fig, lang, "stats")

    # ---------- case ----------
    fig = plt.figure(figsize=(17, 6.8))
    head(fig, t, t["c_title"], t["c_sub"])
    b1 = fig.add_axes([0.05, 0.12, 0.27, 0.66]); b2 = fig.add_axes([0.385, 0.12, 0.27, 0.66]); b3 = fig.add_axes([0.715, 0.12, 0.27, 0.66])
    nights = ["v1.3.2", "v1.3.2", "v1.3.2", "v1.4.0", "v1.4.1", "v1.4.1"]
    labels = ["N1", "N2", "N3", "N4", "N5", "N6"]
    rng = np.random.default_rng(22)
    p5 = {v: M.p_trim(5000, v) for v in set(nights)}
    fails = [rng.binomial(250, p5[v]) for v in nights]
    fails[3] = 43  # 与正文一致（期望约 43）
    b1.bar(range(6), fails, color=[RED if f > 1 else GRN for f in fails], width=.6)
    for i, (f, v) in enumerate(zip(fails, nights)):
        b1.text(i, f + 1, f"{f}\n{v}", ha="center", fontsize=10, color=INK)
    b1.set_xticks(range(6)); b1.set_xticklabels([f"{t['c_night']} {i+1}" if lang == "zh" else f"{t['c_night']} {i+1}" for i in range(6)])
    b1.set_ylim(0, 58); b1.set_title(t["c_a"]); b1.set_ylabel(t["c_ay"])
    # bisect: 23 commits, first bad = 14
    bad0 = 14; lo, hi = 0, 23; steps = []
    while hi - lo > 1:
        mid = (lo + hi) // 2
        steps.append((mid, mid >= bad0))
        if mid >= bad0: hi = mid
        else: lo = mid
    b2.set_xlim(-0.5, 23.5); b2.set_ylim(len(steps) + 0.6, -0.8)
    for k in range(24):
        b2.plot([k, k], [-0.6, len(steps) + 0.4], color=RULE, lw=.6, zorder=0)
    b2.scatter([0], [-0.3], color=GRN, s=60, marker="s"); b2.text(0.4, -0.3, "v1.3.2 (N3) " + t["c_good"], fontsize=9.5, va="center", color=GRN)
    b2.scatter([23], [-0.3], color=RED, s=60, marker="s"); b2.text(22.6, -0.3, "HEAD (N4) " + t["c_bad"], fontsize=9.5, va="center", ha="right", color=RED)
    for i, (m, bad) in enumerate(steps, 1):
        b2.scatter([m], [i], color=RED if bad else GRN, s=90, zorder=3)
        b2.text(m + 0.5, i, f"#{m} {t['c_bad'] if bad else t['c_good']}", va="center", fontsize=10, color=RED if bad else GRN)
    b2.axvline(bad0, color=RED, ls="--", lw=1.2); b2.text(bad0 - 0.3, len(steps) + 0.45, "#14 a3f9c1e", color=RED, fontsize=10.5, ha="right", fontweight="bold")
    b2.set_yticks(range(1, len(steps) + 1)); b2.set_yticklabels([str(i) for i in range(1, len(steps) + 1)])
    b2.set_title(t["c_b"]); b2.set_xlabel(t["c_bx"]); b2.grid(False)
    for v, col, lab in (("v1.3.2", MUT, t["c_v13"]), ("v1.4.0", RED, t["c_v140"]), ("v1.4.1", GRN, t["c_v141"])):
        tr = traces[v]
        m = tr[:, 0] > -360
        b3.plot(tr[m, 0], tr[m, 1], color=col, lw=2.2, label=lab)
    b3.axvline(290, color=ORG, ls="--"); b3.text(285, 1700, t["c_cmd"], color=ORG, ha="right", fontsize=10.5)
    b3.axhspan(0, 300, color=GRN, alpha=.05)
    b3.set_xlim(-360, 300); b3.set_ylim(0, 2400); b3.set_title(t["c_c"]); b3.set_xlabel(t["c_cx"]); b3.set_ylabel(t["c_cy"]); b3.legend(loc="upper right")
    save(fig, lang, "case")
print("nightly fails", fails, "bisect", steps)
