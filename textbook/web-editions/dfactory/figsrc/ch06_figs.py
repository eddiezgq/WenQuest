# -*- coding: utf-8 -*-
"""第 6 章插图（中英两版），数字全由 course/calc/ch06.py 的模型算出。
python3 figsrc/ch06_figs.py → img/fig06_*.webp、img/en/fig06_*.webp"""
import io
import math
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
C = runpy.run_path(os.path.join(ROOT, "course", "calc", "ch06.py"))
sys.stdout = _stdout
o = C["out"]

plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"], "font.size": 11, "axes.facecolor": "#faf9f5",
                     "figure.facecolor": "#faf9f5", "savefig.facecolor": "#faf9f5", "axes.edgecolor": "#5a6570",
                     "axes.grid": True, "grid.color": "#d8dde1", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
COL = dict(b="#1d6b86", o="#c27a12", r="#c0392b", g="#1f8a4c", m="#5a6570", k="#1b2430", p="#7444b4")

T = {
    "zh": dict(
        bt_title="浴盆曲线：失效率随时间的三个阶段（示意）", bt_x="运行时间", bt_y="失效率 h(t)",
        bt_a="早期失效\nβ < 1\n装配、材料缺陷", bt_b="偶然失效\nβ ≈ 1\n外因、冲击", bt_c="磨损失效\nβ > 1\n轴承、导轨、密封",
        bt_note="保养能对付的是这一段", w_title1="(a) 累计故障概率 F(t)", w_title2="(b) 失效率 h(t)",
        w_x="自上次保养以来的运行小时 t", w_y1="F(t)（%）", w_y2="h(t)（次 / 千小时）",
        w_lab="外圆磨床 GRD-01：β = {b:g}，η = {e:g} h", w_pm="保养周期 {v:g} h", w_now="现在 t = {v:g} h",
        w_win="未来 {h:g} h：{p:.1f}%", w_eta="t = η：F = 63.2%",
        c_title="按龄保养：每运行小时的平均花费（GRD-01）", c_x="保养周期 T（运行小时）", c_y="平均花费（\\$ / 运行小时）",
        c_a="下班后保养：只花 \\${cp:.0f}", c_b="生产时间里停机保养：\\${cp:.0f} + 少挣 \\${pl:.0f}", c_run="不保养、坏了再修：\\${r:.2f}/h",
        c_opt="最优 T* = {t:d} h，\\${r:.2f}/h", c_cur="现行周期 {t:g} h"),
    "en": dict(
        bt_title="The bathtub curve: three phases of the failure rate (illustrative)", bt_x="Operating time", bt_y="Failure rate h(t)",
        bt_a="Infant mortality\nβ < 1\nassembly, material defects", bt_b="Random failures\nβ ≈ 1\nexternal causes, shocks", bt_c="Wear-out\nβ > 1\nbearings, guides, seals",
        bt_note="this is the part maintenance can fight", w_title1="(a) Cumulative failure probability F(t)", w_title2="(b) Failure rate h(t)",
        w_x="Operating hours since the last service t", w_y1="F(t) (%)", w_y2="h(t) (failures per 1000 h)",
        w_lab="Grinder GRD-01: β = {b:g}, η = {e:g} h", w_pm="Service interval {v:g} h", w_now="Now t = {v:g} h",
        w_win="Next {h:g} h: {p:.1f}%", w_eta="t = η: F = 63.2%",
        c_title="Age-based maintenance: average cost per operating hour (GRD-01)", c_x="Service interval T (operating hours)", c_y="Average cost (\\$ per operating hour)",
        c_a="Service after the shift: \\${cp:.0f} only", c_b="Stop during production: \\${cp:.0f} + \\${pl:.0f} lost margin", c_run="No service, repair on failure: \\${r:.2f}/h",
        c_opt="Optimum T* = {t:d} h, \\${r:.2f}/h", c_cur="Current interval {t:g} h"),
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


def bathtub(lang):
    t = T[lang]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    xs = [i / 10 for i in range(1, 1001)]
    h = [0.32 * x ** -0.55 + 0.28 + (0.95 * ((x - 58) / 42) ** 2.4 if x > 58 else 0) for x in xs]
    ax.plot(xs, h, color=COL["b"], lw=2.4)
    ax.set_ylim(0, 2.0); ax.set_xlim(0, 100)
    for x0, x1, c in ((0, 12, COL["p"]), (12, 62, COL["m"]), (62, 100, COL["o"])):
        ax.axvspan(x0, x1, color=c, alpha=0.07, lw=0)
    ax.text(1.5, 1.7, t["bt_a"], ha="left", va="center", fontsize=9.5, color=COL["p"])
    ax.text(37, 1.7, t["bt_b"], ha="center", va="center", fontsize=9.5, color=COL["m"])
    ax.text(81, 1.7, t["bt_c"], ha="center", va="center", fontsize=9.5, color=COL["o"])
    ax.annotate(t["bt_note"], (88, 0.74), (62, 1.25), fontsize=9.5, color=COL["o"], arrowprops=dict(arrowstyle="->", color=COL["o"]))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(t["bt_x"]); ax.set_ylabel(t["bt_y"]); ax.set_title(t["bt_title"], loc="left", fontsize=11)
    fig.tight_layout()
    save(fig, "fig06_bathtub", lang)


def weibull(lang):
    t = T[lang]
    b, e, pm, t0, H = o["beta"], o["eta"], o["pm_h"], o["t0"], o["H"]
    F, hz = C["F"], C["hz"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
    xs = list(range(0, 1601, 5))
    a1.plot(xs, [F(x) * 100 for x in xs], color=COL["b"], lw=2.2, label=t["w_lab"].format(b=b, e=e))
    a1.axvspan(t0, t0 + H, color=COL["o"], alpha=0.18, lw=0)
    a1.plot([t0, t0], [0, F(t0) * 100], color=COL["o"], lw=1.2, ls="--")
    a1.plot([t0 + H, t0 + H], [0, F(t0 + H) * 100], color=COL["o"], lw=1.2, ls="--")
    a1.text(t0 + H + 20, F(t0 + H / 2) * 100 - 6, t["w_win"].format(h=H, p=o["p"]), color=COL["o"], fontsize=9.5)
    a1.axvline(pm, color=COL["g"], lw=1.2, ls=":"); a1.text(pm - 10, 76, t["w_pm"].format(v=pm), color=COL["g"], fontsize=9, ha="right")
    a1.plot([e], [63.2], "o", color=COL["k"], ms=5); a1.text(e + 30, 60, t["w_eta"], fontsize=9)
    a1.set_xlim(0, 1600); a1.set_ylim(0, 100)
    a1.set_xlabel(t["w_x"]); a1.set_ylabel(t["w_y1"]); a1.set_title(t["w_title1"], loc="left", fontsize=10.5)
    a1.legend(frameon=False, fontsize=9, loc="upper left")
    a2.plot(xs, [hz(x) * 1000 for x in xs], color=COL["r"], lw=2.2)
    a2.axvline(pm, color=COL["g"], lw=1.2, ls=":"); a2.text(pm - 10, 7.2, t["w_pm"].format(v=pm), color=COL["g"], fontsize=9, ha="right")
    a2.plot([t0], [hz(t0) * 1000], "o", color=COL["o"], ms=6)
    a2.text(t0 + 30, hz(t0) * 1000 - 0.3, t["w_now"].format(v=t0) + f"：{hz(t0)*1000:.2f}" if lang == "zh" else t["w_now"].format(v=t0) + f": {hz(t0)*1000:.2f}",
            color=COL["o"], fontsize=9.5)
    a2.set_xlim(0, 1600); a2.set_ylim(0, 8.5)
    a2.set_xlabel(t["w_x"]); a2.set_ylabel(t["w_y2"]); a2.set_title(t["w_title2"], loc="left", fontsize=10.5)
    fig.tight_layout()
    save(fig, "fig06_weibull", lang)


def cost(lang):
    t = T[lang]
    rate, Cp, pl = C["rate"], o["Cp"], o["pm_lost"]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    Ts = list(range(60, 1601, 10))
    ya = [rate(x, Cp) for x in Ts]
    yb = [rate(x, Cp + pl) for x in Ts]
    ax.plot(Ts, ya, color=COL["b"], lw=2.2, label=t["c_a"].format(cp=Cp))
    ax.plot(Ts, yb, color=COL["o"], lw=2.2, label=t["c_b"].format(cp=Cp, pl=pl))
    ax.axhline(o["r_run"], color=COL["r"], lw=1.2, ls="--"); ax.text(1580, o["r_run"] + 0.12, t["c_run"].format(r=o["r_run"]), color=COL["r"], fontsize=9.5, ha="right")
    ax.plot([o["T_opt"]], [o["r_opt"]], "o", color=COL["b"], ms=7)
    ax.annotate(t["c_opt"].format(t=o["T_opt"], r=o["r_opt"]), (o["T_opt"], o["r_opt"]), (o["T_opt"] + 260, o["r_opt"] - 0.6), fontsize=9.5, color=COL["b"],
                arrowprops=dict(arrowstyle="->", color=COL["b"]))
    ax.plot([o["T_opt2"]], [o["r_opt2"]], "o", color=COL["o"], ms=7)
    ax.annotate(t["c_opt"].format(t=o["T_opt2"], r=o["r_opt2"]), (o["T_opt2"], o["r_opt2"]), (o["T_opt2"] + 200, o["r_opt2"] + 1.3), fontsize=9.5, color=COL["o"],
                arrowprops=dict(arrowstyle="->", color=COL["o"]))
    ax.axvline(o["pm_h"], color=COL["g"], lw=1.2, ls=":"); ax.text(o["pm_h"] + 12, 5.6, t["c_cur"].format(t=o["pm_h"]), color=COL["g"], fontsize=9)
    ax.set_xlim(0, 1600); ax.set_ylim(0, 6)
    ax.set_xlabel(t["c_x"]); ax.set_ylabel(t["c_y"]); ax.set_title(t["c_title"], loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=9.5, loc="upper right", bbox_to_anchor=(1.0, 0.9))
    fig.tight_layout()
    save(fig, "fig06_cost", lang)


if __name__ == "__main__":
    for lang in ("zh", "en"):
        bathtub(lang); weibull(lang); cost(lang)
