# -*- coding: utf-8 -*-
"""第 3 章插图（中英两版），数字全由 course/calc/ch03.py 的模型算出。
python3 figsrc/ch03_figs.py → img/fig03_*.webp、img/en/fig03_*.webp"""
import io
import os
import runpy
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_stdout = sys.stdout
sys.stdout = io.StringIO()
C = runpy.run_path(os.path.join(ROOT, "course", "calc", "ch03.py"))
sys.stdout = _stdout
o = C["out"]

plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"], "font.size": 11, "axes.facecolor": "#faf9f5",
                     "figure.facecolor": "#faf9f5", "savefig.facecolor": "#faf9f5", "axes.edgecolor": "#5a6570",
                     "axes.grid": True, "grid.color": "#d8dde1", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
COL = dict(b="#1d6b86", o="#c27a12", r="#c0392b", g="#1f8a4c", m="#5a6570", k="#1b2430", p="#7444b4", l="#e9edf0")
ORD = {"F": COL["p"], "R": COL["b"], "H": COL["m"]}

T = {
    "zh": dict(
        ch_title="一次停机的因果链：往上找原因，往下算影响（周一 10:00 GRD-01 停 {d:g} 小时）",
        layers=["原因", "设备", "工序", "工单", "订单", "客户"],
        cause="主轴故障\n等备件", dev="外圆磨床 GRD-01\n停 {d:g} h，丢 {L:g} 个生产小时",
        op="磨外圆\n排着 {n} 根轴", wo_f="峰顶的轴工单\n{q} 台 × 3 根", wo_r="机器人厂的轴工单\n{q} 台 × 3 根", wo_h="海港的轴工单\n{q} 台 × 3 根",
        so_f="峰顶 {q} 台\n周三交：按时", so_r="机器人厂 {q} 台（急单）\n周四交：晚 {l} 天", so_h="海港 {q} 台\n{w} 个工作日后交：按时",
        cu_f="峰顶搅拌机\n违约金 \\$0", cu_r="机器人厂\n违约金 \\${p:,.0f}", cu_h="海港起重\n不受影响",
        g_title="磨床 GRD-01 的排程：四个方案（停机周一 10:00 起 {d:g} 小时）", g_y=["A 不处理", "B 恢复后加班", "C 维修加急", "D 外协 {n} 台"],
        g_down="停机", g_ot="加班", g_out="外协件 {h:g} 小时后回厂", g_dead="机器人订单的轴最晚做完（周三当天，含加班）", g_lab={"F": "峰顶", "R": "机器人厂", "H": "海港"},
        g_res=["晚 {l} 天，违约金 \\${p:,.0f}", "按时，加班 {h:.1f} h = \\${c:,.2f}", "仍晚 {l} 天：\\${c:,.0f} + 违约金 \\${p:,.0f}", "按时，外协 \\${c:,.2f}"],
        c_title="停机越久，各方案多花的钱（加班费、加急费、外协费 + 违约金）", c_x="停机时长（小时，周一 10:00 开始）", c_y="多花的钱（\\$）",
        c_names=["A 不处理", "B 恢复后加班（每天加到够为止，最多 4 h）", "C 维修加急", "D 外协（保机器人订单的最少台数）"],
        c_late="空心点：有订单晚交", c_now="本章：{d:g} h", c_flat="停机在夜里：再多也不丢生产时间"),
    "en": dict(
        ch_title="The causal chain of one breakdown: up to the cause, down to the impact (GRD-01 stops at 10:00 Monday for {d:g} h)",
        layers=["Cause", "Machine", "Operation", "Work orders", "Sales orders", "Customers"],
        cause="Spindle fault\nwaiting for parts", dev="Grinder GRD-01\ndown {d:g} h, {L:g} production h lost",
        op="Cylindrical grinding\n{n} shafts queued", wo_f="Summit's shaft WOs\n{q} units × 3", wo_r="Robot plant's shaft WOs\n{q} units × 3", wo_h="Harbor's shaft WOs\n{q} units × 3",
        so_f="Summit, {q} units\ndue Wed: on time", so_r="Robot plant, {q} units (rush)\ndue Thu: {l} day late", so_h="Harbor, {q} units\ndue in {w} working days: on time",
        cu_f="Summit Mixers\npenalty \\$0", cu_r="Robot plant\npenalty \\${p:,.0f}", cu_h="Harbor Crane\nnot affected",
        g_title="Schedule of grinder GRD-01 under four options (down from 10:00 Monday for {d:g} h)",
        g_y=["A Do nothing", "B Overtime after repair", "C Expedite repair", "D Outsource {n} units"],
        g_down="down", g_ot="overtime", g_out="outsourced parts back after {h:g} h", g_dead="latest finish for the robot order (Wednesday, overtime included)", g_lab={"F": "Summit", "R": "Robot plant", "H": "Harbor"},
        g_res=["{l} day late, penalty \\${p:,.0f}", "on time, {h:.1f} h overtime = \\${c:,.2f}", "still {l} day late: \\${c:,.0f} + \\${p:,.0f} penalty", "on time, outsourcing \\${c:,.2f}"],
        c_title="The longer the stop, the more each option costs (overtime, expediting, outsourcing + penalties)", c_x="Downtime (hours, starting 10:00 Monday)", c_y="Extra cost (\\$)",
        c_names=["A Do nothing", "B Overtime after repair (as needed, up to 4 h a day)", "C Expedite the repair", "D Outsource (fewest units that save the robot order)"],
        c_late="hollow: some order is late", c_now="this chapter: {d:g} h", c_flat="the stop runs through the night: no production lost"),
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


def box(ax, x, y, text, fc, ec, w=1.55, h=0.78, fs=8.6, tc=None):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.4))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, color=tc or COL["k"], linespacing=1.35)


def arrow(ax, x0, y0, x1, y1, c):
    ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="-|>", color=c, lw=1.2, shrinkA=2, shrinkB=2))


def chain(lang):
    t = T[lang]
    fig, ax = plt.subplots(figsize=(11.5, 4.9))
    ax.set_xlim(-0.2, 11.4); ax.set_ylim(-0.2, 4.35); ax.axis("off")
    xs = [0.75, 2.75, 4.7, 6.65, 8.6, 10.5]
    for x, name in zip(xs, t["layers"]):
        ax.text(x, 4.15, name, ha="center", va="center", fontsize=10, color=COL["m"], fontweight="bold")
    late = C["O"]["none"]["late"]
    red, redf, grn, grnf, gry = COL["r"], "#f7e1de", COL["g"], "#ddefe4", "#eef1f3"
    w0 = 1.75
    box(ax, xs[0], 2.0, t["cause"], "#efe6f7", COL["p"], w=1.3)
    box(ax, xs[1], 2.0, t["dev"].format(d=o["D"], L=o["L"]), redf, red, w=w0, fs=8.3)
    box(ax, xs[2], 2.0, t["op"].format(n=o["queue_n"]), "#fbeedd", COL["o"], w=w0)
    arrow(ax, xs[0] + 0.65, 2.0, xs[1] - w0 / 2, 2.0, COL["p"])
    arrow(ax, xs[1] + w0 / 2, 2.0, xs[2] - w0 / 2, 2.0, red)
    ys = {"F": 3.25, "R": 2.0, "H": 0.75}
    for k in "FRH":
        y = ys[k]
        bad = late[k] > 0
        fc, ec = (redf, red) if bad else ((grnf, grn) if k == "F" else (gry, COL["m"]))
        box(ax, xs[3], y, t["wo_" + k.lower()].format(q=o["qty_" + k.lower()]), "#fbeedd", COL["o"], w=w0)
        box(ax, xs[4], y, t["so_" + k.lower()].format(q=o["qty_" + k.lower()], l=late[k], w=o["due_h_wd"]), fc, ec, w=w0 + 0.1, fs=8.2)
        box(ax, xs[5], y, t["cu_" + k.lower()].format(p=o["pen_r"] * late["R"]), fc, ec, w=1.6)
        arrow(ax, xs[2] + w0 / 2, 2.0, xs[3] - w0 / 2, y, COL["o"])
        arrow(ax, xs[3] + w0 / 2, y, xs[4] - (w0 + 0.1) / 2, y, ec)
        arrow(ax, xs[4] + (w0 + 0.1) / 2, y, xs[5] - 0.8, y, ec)
    ax.set_title(t["ch_title"].format(d=o["D"]), loc="left", fontsize=11)
    fig.tight_layout()
    save(fig, "fig03_chain", lang)


def segments(kind, n_out=None):
    """把推演再跑一遍，记下磨床每一段在做谁的活（给甘特图用）"""
    import copy
    D, tb = C["D_H"], C["TB"]
    factor = C["EXP_F"] if kind == "expedite" else 1.0
    ot = C["OT_DEF"] if kind == "overtime" else 0
    n = n_out or 0
    up = tb + D * 60
    if factor < 1:
        up = tb + (up - tb) * factor
    SET, QTY, SH0, SH1 = C["SET_MIN"], copy.copy(C["QTY"]), C["SH0"], C["SH1"]
    items = [[k, QTY[k] * SET - (n * SET if k == "R" else 0)] for k in C["FIFO"]]
    segs, ots = [], []
    r_done = False
    up_day = int(up // 1440)
    for d in range(0, 5):
        s, e = d * 1440 + SH0, d * 1440 + SH1
        t = max(s, up, tb)
        while items:
            lim = e + (ot if (ot and d >= up_day and not r_done) else 0)
            if t >= lim:
                break
            take = min(items[0][1], lim - t)
            segs.append((items[0][0], t, t + take))
            if t + take > e:
                ots.append((max(t, e), t + take))
            t += take
            items[0][1] -= take
            if items[0][1] <= 1e-9:
                if items.pop(0)[0] == "R":
                    r_done = True
    return segs, ots, (tb, up)


def gantt(lang):
    t = T[lang]
    O = C["O"]
    fig, ax = plt.subplots(figsize=(11.5, 5.0))
    X = lambda m: (m - 0) / 60.0          # 小时，从周一 00:00 起
    t0, t1 = 8, 3 * 24 + 21               # 周一 08:00 到周四 21:00
    kinds = ["none", "overtime", "expedite", "outsource"]
    for d in range(0, 4):
        ax.axvspan(X(d * 1440 + C["SH0"]), X(d * 1440 + C["SH1"]), color="#e7edf1", lw=0, zorder=0)
        ax.text(X(d * 1440 + 12.5 * 60), 4.42, ["周一", "周二", "周三", "周四"][d] if lang == "zh" else ["Mon", "Tue", "Wed", "Thu"][d],
                ha="center", fontsize=9.5, color=COL["m"])
    for i, k in enumerate(kinds):
        y = 3 - i
        segs, ots, (a, b) = segments(k, o["n_min"] if k == "outsource" else None)
        ax.barh(y, X(b) - X(a), left=X(a), height=0.5, color="#f3d2cd", edgecolor=COL["r"], hatch="///", lw=0.8, zorder=2)
        for who, s, e in segs:
            if s >= (t1 + 0.0) * 60:
                continue
            e = min(e, t1 * 60)
            ax.barh(y, X(e) - X(s), left=X(s), height=0.5, color=ORD[who], alpha=0.85, lw=0, zorder=3)
        for s, e in ots:
            ax.barh(y, X(e) - X(s), left=X(s), height=0.62, fill=False, edgecolor=COL["o"], lw=2.0, zorder=4)
        if k == "outsource":
            back = C["TB"] + C["OUT_DAYS"] * 1440
            ax.annotate("", (X(back), y + 0.34), (X(C["TB"]), y + 0.34), arrowprops=dict(arrowstyle="->", color=COL["b"], lw=1.1, ls="--"))
            ax.text(X(C["TB"]) + 1, y + 0.42, t["g_out"].format(h=o["out_h"]), fontsize=8, color=COL["b"])
        res = O[k]
        txt = t["g_res"][i].format(l=res["late"]["R"], p=res["pen"], h=res["ot_h"], c=res["extra"])
        ax.text(t1 + 1.0, y, txt, va="center", fontsize=8.6, color=COL["r"] if res["worst"] else COL["g"])
    dead = C["dead_R"] + C["OT_MAX"]          # 周三当天做完都算（加班到 21:00）
    ax.axvline(X(dead), color=COL["k"], lw=1.2, ls="--", zorder=5)
    ax.text(X(dead) + 0.6, -0.72, t["g_dead"], ha="left", fontsize=8.5, color=COL["k"])
    ax.set_yticks([3, 2, 1, 0]); ax.set_yticklabels([t["g_y"][0], t["g_y"][1], t["g_y"][2], t["g_y"][3].format(n=o["n_min"])])
    ax.set_ylim(-1.0, 4.65); ax.set_xlim(t0, t1 + 36)
    ticks = [d * 24 + h for d in range(4) for h in (8, 17)]
    ax.set_xticks(ticks); ax.set_xticklabels([f"{h % 24:02d}:00" for h in ticks], fontsize=8)
    ax.grid(axis="y", visible=False)
    hs = [plt.Rectangle((0, 0), 1, 1, color=ORD[k], alpha=.85) for k in "FRH"] + \
         [plt.Rectangle((0, 0), 1, 1, fc="#f3d2cd", ec=COL["r"], hatch="///"), plt.Rectangle((0, 0), 1, 1, fill=False, ec=COL["o"], lw=2)]
    ax.legend(hs, [t["g_lab"][k] for k in "FRH"] + [t["g_down"], t["g_ot"]], ncol=5, frameon=False, fontsize=8.6, loc="upper left", bbox_to_anchor=(0.0, -0.1))
    ax.set_title(t["g_title"].format(d=o["D"]), loc="left", fontsize=11)
    fig.tight_layout()
    save(fig, "fig03_gantt", lang)


def cost(lang):
    t = T[lang]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    Ds = list(range(2, 49))
    cols = [COL["m"], COL["o"], COL["r"], COL["b"]]
    for k, c, nm in zip(["none", "overtime", "expedite", "outsource"], cols, t["c_names"]):
        ys = [C["option"](k, D=d) for d in Ds]
        ax.plot(Ds, [y["total"] for y in ys], color=c, lw=2, label=nm)
        late = [(d, y["total"]) for d, y in zip(Ds, ys) if y["worst"] > 0]
        ok = [(d, y["total"]) for d, y in zip(Ds, ys) if y["worst"] == 0]
        if ok:
            ax.plot(*zip(*ok), "o", color=c, ms=4)
        if late:
            ax.plot(*zip(*late), "o", mfc="#faf9f5", mec=c, ms=4.5)
    ax.axvline(o["D"], color=COL["k"], lw=1, ls=":")
    ax.text(o["D"] + 0.4, 1130, t["c_now"].format(d=o["D"]), fontsize=9)
    ax.annotate(t["c_flat"], (16, 205), (33, 120), fontsize=8.8, color=COL["m"],
                arrowprops=dict(arrowstyle="->", color=COL["m"]))
    ax.set_xlim(0, 49); ax.set_ylim(0, 1200)
    ax.set_xlabel(t["c_x"]); ax.set_ylabel(t["c_y"]); ax.set_title(t["c_title"], loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8.8, loc="upper left", title=t["c_late"], title_fontsize=8.8, alignment="left")
    fig.tight_layout()
    save(fig, "fig03_cost", lang)


if __name__ == "__main__":
    for lang in ("zh", "en"):
        chain(lang); gantt(lang); cost(lang)
