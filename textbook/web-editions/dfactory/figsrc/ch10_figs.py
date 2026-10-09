# -*- coding: utf-8 -*-
"""第 10 章插图（中英两版），数字全由 course/calc/ch10.py 算出（口径取自数字工厂 hub/finance.py）。
python3 figsrc/ch10_figs.py → img/fig10_*.webp、img/en/fig10_*.webp"""
import io
import os
import runpy
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_stdout = sys.stdout
sys.stdout = io.StringIO()
C = runpy.run_path(os.path.join(ROOT, "course", "calc", "ch10.py"))
sys.stdout = _stdout
o = C["out"]

plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"], "font.size": 11, "axes.facecolor": "#faf9f5",
                     "figure.facecolor": "#faf9f5", "savefig.facecolor": "#faf9f5", "axes.edgecolor": "#5a6570",
                     "axes.grid": True, "grid.color": "#d8dde1", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
COL = dict(b="#1d6b86", o="#c27a12", r="#c0392b", g="#1f8a4c", m="#5a6570", k="#1b2430", p="#7444b4", l="#9fb3bf")

T = {
    "zh": dict(
        wf_title="机器人厂这张订单（20 台 WQR-105）：收入被各项成本一块块切掉，剩下毛利",
        wf_lab=["收入", "料", "工\n（折旧+人工）", "电", "废品\n返工", "空转电", "加班\n换供应商", "毛利"],
        wf_y="美元", wf_std="按标准成本的毛利 \\${v:,.0f}（{p:.1f}%）", wf_m="{p:.1f}%",
        ag_t1="(a) 应收账龄：逾期的钱占 {p:.0f}%", ag_t2="(b) 应收周转天数 DSO",
        ag_b=["未到期", "逾期\n1–30 天", "逾期\n31–60 天", "逾期\n60 天以上"], ag_y="应收余额（美元）",
        ag_c={"robot": "机器人厂", "green": "绿谷输送", "summit": "峰顶搅拌", "harbor": "海港起重"},
        ds_lab=["现在", "机器人厂\n付清以后"], ds_y="天", ds_tg="目标 ≤ {v:g} 天",
        cf_title="未来 8 周的现金（期初 \\${c:,.0f}，每周固定开支 \\${w:,.0f}）", cf_x="第几周", cf_y="周末现金（美元）",
        cf_none="不处理：机器人厂不催就不付", cf_dun="催款（或冻结）：{d} 天内收到 \\${a:,.0f}", cf_late="拖到第 {d:g} 天才付",
        cf_zero="现金为零", cf_safe="安全线：一周的固定开支 \\${v:,.0f}", cf_in="收款", cf_out="付款（供应商 + 固定开支）",
        cf_low="第 {w} 周 −\\${v:,.0f}"),
    "en": dict(
        wf_title="The robot plant's order (20 WQR-105): revenue cut block by block by costs, leaving the gross margin",
        wf_lab=["Revenue", "Material", "Labour\n(depr.+wages)", "Energy", "Scrap,\nrework", "Idle\npower", "Overtime,\nalt. supplier", "Margin"],
        wf_y="US dollars", wf_std="Margin at standard cost \\${v:,.0f} ({p:.1f}%)", wf_m="{p:.1f}%",
        ag_t1="(a) Receivables ageing: {p:.0f}% is overdue", ag_t2="(b) Days sales outstanding (DSO)",
        ag_b=["Not due", "1–30 days\noverdue", "31–60 days\noverdue", "Over 60 days\noverdue"], ag_y="Amount outstanding (US dollars)",
        ag_c={"robot": "Robot plant", "green": "GreenValley", "summit": "Summit", "harbor": "Harbor Crane"},
        ds_lab=["Now", "After the robot\nplant pays"], ds_y="days", ds_tg="target ≤ {v:g} days",
        cf_title="Cash over the next 8 weeks (opening \\${c:,.0f}, fixed costs \\${w:,.0f} a week)", cf_x="Week", cf_y="Cash at week end (US dollars)",
        cf_none="Do nothing: the robot plant won't pay unless chased", cf_dun="Dun (or freeze): \\${a:,.0f} within {d} days", cf_late="Paid only on day {d:g}",
        cf_zero="zero cash", cf_safe="Safety line: one week of fixed costs \\${v:,.0f}", cf_in="Cash in", cf_out="Cash out (suppliers + fixed costs)",
        cf_low="week {w}: −\\${v:,.0f}"),
}


def save(fig, name, lang):
    d = os.path.join(ROOT, "img") if lang == "zh" else os.path.join(ROOT, "img", "en")
    os.makedirs(d, exist_ok=True)
    buf = io.BytesIO()
    fig.savefig(buf, dpi=200, format="png")
    plt.close(fig)
    p = os.path.join(d, name + ".webp")
    Image.open(buf).save(p, "WEBP", quality=88, method=6)
    print("wrote", p)


def waterfall(lang):
    t = T[lang]
    steps = [o["o_mat"], o["o_lab"], o["o_en"], o["x_scrap"], o["x_idle"], o["x_act"]]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(0, o["rev"], color=COL["b"], width=0.66)
    ax.text(0, o["rev"] + 500, "\\${:,.0f}".format(o["rev"]), ha="center", fontsize=9.5, color=COL["k"])
    top = o["rev"]
    for i, v in enumerate(steps, start=1):
        ax.bar(i, v, bottom=top - v, color=COL["r"] if i <= 3 else COL["o"], width=0.66)
        ax.plot([i - 1 + 0.33, i - 0.33], [top, top], color=COL["m"], lw=0.8)
        small = v < 1500
        ax.text(i, top - v - 1300 if small else top + 500, "−\\${:,.0f}".format(v), ha="center", fontsize=9.5, color=COL["r"] if i <= 3 else COL["o"])
        top -= v
    n = len(steps) + 1
    ax.plot([n - 1 + 0.33, n - 0.33], [top, top], color=COL["m"], lw=0.8)
    ax.bar(n, o["margin"], color=COL["g"], width=0.66)
    ax.text(n, o["margin"] / 2, "\\${:,.0f}\n".format(o["margin"]) + t["wf_m"].format(p=o["m_pct"]), ha="center", va="center", fontsize=10, color="white",
            fontweight="bold", linespacing=1.6)
    ax.axhline(o["std_margin"], color=COL["g"], lw=1.1, ls="--")
    ax.text(0.45, o["std_margin"] - 1500, t["wf_std"].format(v=o["std_margin"], p=o["std_pct"]), ha="left", fontsize=9, color=COL["g"])
    ax.set_xticks(range(n + 1)); ax.set_xticklabels(t["wf_lab"], fontsize=9.5)
    ax.set_ylim(0, o["rev"] * 1.1); ax.set_xlim(-0.6, n + 0.6)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: "{:,.0f}".format(v)))
    ax.set_ylabel(t["wf_y"]); ax.set_title(t["wf_title"], loc="left", fontsize=11)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "fig10_waterfall", lang)


def aging(lang):
    t = T[lang]
    inv = C["inv"]
    who = {C["ROBOT"]: "robot", C["GREEN"]: "green", C["SUMMIT"]: "summit", C["HARBOR"]: "harbor"}
    cols = {"robot": COL["r"], "green": COL["b"], "summit": COL["o"], "harbor": COL["p"]}
    keys = ["current", "d30", "d60", "d60p"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.7, 1]})
    base = [0.0] * 4
    done = set()
    for x in inv:
        k = keys.index(C["bucket"](x["over"]))
        c = who[x["party"]]
        a1.bar(k, x["amount"], bottom=base[k], color=cols[c], width=0.6, label=None if c in done else t["ag_c"][c])
        a1.text(k, base[k] + x["amount"] / 2, "\\${:,.0f}".format(x["amount"]), ha="center", va="center", fontsize=9, color="white")
        base[k] += x["amount"]
        done.add(c)
    for k, v in enumerate(base):
        a1.text(k, v + 700, "\\${:,.0f}".format(v), ha="center", fontsize=9.5, color=COL["k"])
    a1.set_xticks(range(4)); a1.set_xticklabels(t["ag_b"], fontsize=9.5)
    a1.set_ylim(0, max(base) * 1.18)
    a1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: "{:,.0f}".format(v)))
    a1.set_ylabel(t["ag_y"]); a1.set_title(t["ag_t1"].format(p=o["overdue_share"]), loc="left", fontsize=10.5)
    a1.legend(frameon=False, fontsize=9, loc="upper right")
    a1.grid(axis="x", visible=False)
    vals = [o["dso"], o["dso_after"]]
    a2.bar([0, 1], vals, color=[COL["r"], COL["g"]], width=0.55)
    for i, v in enumerate(vals):
        a2.text(i, v + 2, "{:.1f}".format(v), ha="center", fontsize=10, color=COL["k"])
    a2.axhline(o["dso_target"], color=COL["m"], ls="--", lw=1.1)
    a2.text(1.45, o["dso_target"] + 2, t["ds_tg"].format(v=o["dso_target"]), ha="right", fontsize=9, color=COL["m"])
    a2.set_xticks([0, 1]); a2.set_xticklabels(t["ds_lab"], fontsize=9.5); a2.set_xlim(-0.6, 1.6)
    a2.set_ylim(0, 100); a2.set_ylabel(t["ds_y"]); a2.set_title(t["ag_t2"], loc="left", fontsize=10.5)
    a2.grid(axis="x", visible=False)
    fig.tight_layout()
    save(fig, "fig10_aging", lang)


def cash(lang):
    t = T[lang]
    fc = C["forecast"]
    none, dun, late = fc(None)[0], fc(float(o["dun"]))[0], fc(o["late_day"])[0]
    wks = [0] + [r["week"] for r in none]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar([r["week"] - 0.17 for r in none], [r["in"] for r in none], width=0.32, color=COL["g"], alpha=0.35, label=t["cf_in"])
    ax.bar([r["week"] + 0.17 for r in none], [-r["out"] for r in none], width=0.32, color=COL["r"], alpha=0.30, label=t["cf_out"])
    ax.plot(wks, [o["cash0"]] + [r["balance"] for r in dun], color=COL["b"], lw=2.4, marker="o", ms=4, label=t["cf_dun"].format(d=o["dun"], a=o["robot_amt"]))
    ax.plot(wks, [o["cash0"]] + [r["balance"] for r in late], color=COL["o"], lw=1.8, ls="-.", marker="o", ms=3, label=t["cf_late"].format(d=o["late_day"]))
    ax.plot(wks, [o["cash0"]] + [r["balance"] for r in none], color=COL["r"], lw=2.4, marker="o", ms=4, label=t["cf_none"])
    ax.axhline(0, color=COL["k"], lw=1.0)
    ax.axhline(o["safety"], color=COL["m"], lw=1.0, ls="--")
    ax.text(0.15, o["safety"] + 1500, t["cf_safe"].format(v=o["safety"]), fontsize=8.5, color=COL["m"])
    ax.annotate(t["cf_low"].format(w=o["none_low_wk"], v=abs(o["none_low"])), (o["none_low_wk"], o["none_low"]), (o["none_low_wk"] - 2.2, o["none_low"] - 9000),
                fontsize=9.5, color=COL["r"], arrowprops=dict(arrowstyle="->", color=COL["r"]))
    ax.set_xticks(wks); ax.set_xlim(-0.3, 8.6); ax.set_ylim(-30000, 105000)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: "{:,.0f}".format(v)))
    ax.set_xlabel(t["cf_x"]); ax.set_ylabel(t["cf_y"]); ax.set_title(t["cf_title"].format(c=o["cash0"], w=o["wk"]), loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8.8, loc="upper right", ncol=2)
    fig.tight_layout()
    save(fig, "fig10_cash", lang)


if __name__ == "__main__":
    for lang in ("zh", "en"):
        waterfall(lang); aging(lang); cash(lang)
