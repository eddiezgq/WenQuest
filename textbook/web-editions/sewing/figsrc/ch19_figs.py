# -*- coding: utf-8 -*-
"""第 19 章数据图（中英两版）：fig_19_sizing（主轴与电磁铁选型）、fig_19_evtable（事件表与时刻表）。
python3 figsrc/ch19_figs.py → img/fig_19_*.png、img/en/fig_19_*.png"""
import os, sys, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, os.path.dirname(__file__))
import ch19_calc as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams.update({"font.family": ["Noto Sans CJK SC", "DejaVu Sans"], "font.size": 11, "axes.facecolor": "#faf9f5",
                     "figure.facecolor": "#faf9f5", "savefig.facecolor": "#faf9f5", "axes.edgecolor": "#5a6570",
                     "axes.grid": True, "grid.color": "#d8dde1", "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False})
COL = dict(g="#1f8a4c", b="#2a5fb8", o="#c4531d", p="#7444b4", t="#0f6e74", y="#a8740c", k="#1b2430", m="#5a6570", r="#c0392b")

T = {
 "zh": dict(
   s_title="(a) 主轴：0→最高转速所需转矩\n（平缝机原型，J_load = 5×10⁻⁴ kg·m²）",
   s_x="加速时间 t_acc（s）", s_y="所需转矩（N·m）", mot="电机 {s}：所需转矩", lim="0.8 × 峰值 = {v:.2f}",
   s_pick="算例：400 W，0.15 s → 2.24 N·m", s_lim25="驱动器转矩限幅 2.5 N·m（第 13 章整定）",
   b_title="(b) 电磁铁：吸合折算主轴转角 = 6·n·t\n（D-DRV-SOL 驱动，24 V 强激磁）", b_x="动作时的主轴转速 n（r/min）", b_y="折算转角（°）",
   sol="{s}（吸合 {t} ms）", b_lim="剪线判据 20°", b_trim="剪线转速 300 r/min", b_win="倒缝：空闲角 201.6°", b_bt="回针转速 1800 r/min",
   e_title="平缝机原型 WQ-SC/LS 的事件表（初值，示意）对准第 8、14 章的时刻表：剪线那一针（第 0 转）和下一转（第 1 转）",
   e_x="主轴转角（°，0° = 针杆上止点）", rows=["针尖在布中", "挑线杆最高点 / 钩线", "剪线电磁铁（凸轮式动刀）", "动刀进刀窗口（直接驱动，第 14 章）", "拨线电磁铁", "倒缝电磁铁（只在回针针内）", "停针定位"],
   lab=dict(needle="101.7°–258.3°", take="55°", hook="梭尖钩线 206°", trim="通电 205.0°–330.0°", knife="300°–330°", wipe="15.0°–60.0°",
            bt="114.2° 切换（送布牙沉下）", engage="25° 切入位置环", stop="停在 70°（上针位）"),
   rev0="第 0 转（剪线那一针）", rev1="第 1 转",
   note="角度单位在固件里是 0.1°（0–3599）。凸轮式剪线：电磁铁 205° 通电，按 300 r/min、6.9 ms 吸合折算 12.4°，217° 前到位，赶在凸轮槽入口之前；直接驱动的动刀按第 14 章在 290°–300° 发令。"),
 "en": dict(
   s_title="(a) Spindle: torque needed to reach top speed\n(lockstitch prototype, J_load = 5×10⁻⁴ kg·m²)",
   s_x="Acceleration time t_acc (s)", s_y="Required torque (N·m)", mot="Motor {s}: required torque", lim="0.8 × peak = {v:.2f}",
   s_pick="Worked example: 400 W, 0.15 s → 2.24 N·m", s_lim25="Drive torque limit 2.5 N·m (Ch. 13 tuning)",
   b_title="(b) Solenoids: pull-in as spindle angle = 6·n·t\n(D-DRV-SOL driver, 24 V boost)", b_x="Spindle speed during the action n (r/min)", b_y="Equivalent angle (°)",
   sol="{s} (pull-in {t} ms)", b_lim="Trim criterion 20°", b_trim="Trim speed 300 r/min", b_win="Backtack: idle angle 201.6°", b_bt="Backtack speed 1800 r/min",
   e_title="Event table of the WQ-SC/LS lockstitch prototype (initial values, illustrative) against the timing charts of Ch. 8 and 14: the trim stitch (rev 0) and the next revolution (rev 1)",
   e_x="Spindle angle (°, 0° = needle-bar top dead centre)", rows=["Needle point in fabric", "Take-up top / loop catch", "Trim solenoid (cam-driven knife)", "Knife-entry window (direct drive, Ch. 14)", "Wiper solenoid", "Backtack solenoid (backtack stitches only)", "Needle positioning"],
   lab=dict(needle="101.7°–258.3°", take="55°", hook="hook catches 206°", trim="on 205.0°–330.0°", knife="300°–330°", wipe="15.0°–60.0°",
            bt="switch at 114.2° (feed dog down)", engage="position loop at 25°", stop="stop at 70° (needle up)"),
   rev0="Rev 0 (trim stitch)", rev1="Rev 1",
   note="Firmware angles are in 0.1° (0–3599). Cam-driven trimmer: the solenoid is energised at 205°; at 300 r/min its 6.9 ms pull-in is 12.4°, so it is home by 217°, ahead of the cam-groove entry. A directly driven knife is commanded at 290°–300° as in Ch. 14."),
}

def save(fig, name, lang):
    d = os.path.join(ROOT, "img") if lang == "zh" else os.path.join(ROOT, "img", "en")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    fig.savefig(p, dpi=200)
    plt.close(fig)
    print("wrote", p)

def sizing(lang):
    t = T[lang]; r = C.REQ["LS"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.6))
    ts = [0.08+0.005*i for i in range(45)]
    cols = {"250": COL["m"], "400": COL["b"], "550": COL["g"]}
    for s, c in cols.items():
        m = C.item("D-MOT-PMSM", s)
        ys = []
        for ta in ts:
            rr = dict(r, t_acc=ta)
            ys.append(C.spindle_need(rr, m)["T_acc"])
        a1.plot(ts, ys, color=c, lw=2, label=t["mot"].format(s=s))
        a1.axhline(0.8*m["peak_torque_Nm"], color=c, lw=1.1, ls="--")
        a1.text(0.302, 0.8*m["peak_torque_Nm"]+0.04, t["lim"].format(v=0.8*m["peak_torque_Nm"]), color=c, fontsize=9, ha="right")
    a1.axhline(2.5, color=COL["o"], lw=1.1, ls=":")
    a1.text(0.302, 2.5-0.17, t["s_lim25"], color=COL["o"], fontsize=9, ha="right")
    T0 = C.spindle_need(r, C.item("D-MOT-PMSM", "400"))["T_acc"]
    a1.plot([0.15], [T0], "o", color=COL["b"], ms=7)
    a1.annotate(t["s_pick"], (0.15, T0), (0.185, 3.05), fontsize=9, color=COL["k"], arrowprops=dict(arrowstyle="->", color=COL["k"], lw=0.8))
    a1.set_xlim(0.08, 0.30); a1.set_ylim(0, 5)
    a1.set_xlabel(t["s_x"]); a1.set_ylabel(t["s_y"]); a1.set_title(t["s_title"], fontsize=10.5, loc="left")
    a1.legend(fontsize=8.5, loc="upper right", frameon=False, bbox_to_anchor=(1.0, 1.0))
    ns = list(range(0, 2201, 20))
    for s, c in (("S8", COL["m"]), ("M15", COL["b"]), ("L30", COL["g"]), ("XL60", COL["p"])):
        sol = C.item("D-SOL-PUSH", s)
        a2.plot(ns, [6*n*sol["t_on_ms"]/1000 for n in ns], color=c, lw=2, label=t["sol"].format(s=s, t=sol["t_on_ms"]))
    a2.axhline(20, color=COL["r"], lw=1.2, ls="--"); a2.text(2190, 6, t["b_lim"], color=COL["r"], fontsize=9, ha="right")
    a2.axhline(201.6, color=COL["o"], lw=1.2, ls="--"); a2.text(420, 188, t["b_win"], color=COL["o"], fontsize=9)
    a2.axvline(300, color=COL["k"], lw=0.9, ls=":"); a2.text(325, 140, t["b_trim"], fontsize=9, rotation=90, va="center")
    a2.axvline(1800, color=COL["k"], lw=0.9, ls=":"); a2.text(1830, 228, t["b_bt"], fontsize=9, rotation=90, va="center")
    a2.plot([300], [12.42], "o", color=COL["b"], ms=6); a2.plot([1800], [118.8], "o", color=COL["g"], ms=6)
    a2.set_xlim(0, 2200); a2.set_ylim(0, 300)
    a2.set_xlabel(t["b_x"]); a2.set_ylabel(t["b_y"]); a2.set_title(t["b_title"], fontsize=10.5, loc="left")
    a2.legend(fontsize=8.5, loc="upper left", frameon=False, bbox_to_anchor=(0.0, 1.0))
    fig.tight_layout()
    save(fig, "fig_19_sizing.png", lang)

def evtable(lang):
    t = T[lang]
    fig, ax = plt.subplots(figsize=(10, 4.9))
    rows = t["rows"]; nr = len(rows)
    y = lambda i: nr-1-i
    def bar(i, a0, a1, col, txt=None, alpha=0.85, hatch=None, tc="white"):
        ax.add_patch(Rectangle((a0, y(i)-0.32), a1-a0, 0.64, color=col, alpha=alpha, hatch=hatch, lw=0))
        if txt:
            ax.text((a0+a1)/2, y(i), txt, ha="center", va="center", fontsize=8.5, color=tc)
    for r0 in (0, 360):
        bar(0, r0+101.7, r0+258.3, "#9aa4ae", t["lab"]["needle"])
    for r0 in (0, 360):
        ax.plot([r0+55, r0+55], [y(1)-0.32, y(1)+0.32], color=COL["o"], lw=3)
        ax.text(r0+59, y(1)+0.05, t["lab"]["take"], fontsize=8.5, color=COL["o"], va="center")
    ax.plot([206, 206], [y(1)-0.32, y(1)+0.32], color=COL["t"], lw=3); ax.text(210, y(1), t["lab"]["hook"], fontsize=8.5, color=COL["t"], va="center")
    bar(2, 205, 330, COL["b"], t["lab"]["trim"])
    ax.add_patch(Rectangle((205, y(2)-0.32), 12.4, 0.64, color="#0b2f6b", alpha=0.55, lw=0))
    bar(3, 300, 330, COL["y"], alpha=0.7); ax.text(336, y(3), t["lab"]["knife"], fontsize=8.5, color=COL["y"], va="center")
    bar(4, 360+15, 360+60, COL["g"]); ax.text(426, y(4), t["lab"]["wipe"], fontsize=8.5, color=COL["g"], va="center")
    for r0 in (0, 360):
        ax.plot([r0+114.2]*2, [y(5)-0.32, y(5)+0.32], color=COL["p"], lw=3)
    ax.text(114.2+6, y(5), t["lab"]["bt"], fontsize=8.5, color=COL["p"], va="center")
    ax.add_patch(Rectangle((360+25, y(6)-0.32), 45, 0.64, color=COL["o"], alpha=0.25, lw=0))
    ax.plot([360+25]*2, [y(6)-0.32, y(6)+0.32], color=COL["o"], lw=1.5, ls="--")
    ax.plot([360+70]*2, [y(6)-0.4, y(6)+0.4], color=COL["o"], lw=3)
    ax.text(360+20, y(6), t["lab"]["engage"], fontsize=8.5, color=COL["o"], va="center", ha="right")
    ax.text(360+75, y(6), t["lab"]["stop"], fontsize=8.5, color=COL["o"], va="center")
    ax.axvline(360, color=COL["k"], lw=1)
    ax.text(180, nr-0.35, t["rev0"], ha="center", fontsize=9.5, color=COL["k"], weight="bold")
    ax.text(540, nr-0.35, t["rev1"], ha="center", fontsize=9.5, color=COL["k"], weight="bold")
    ax.set_yticks([y(i) for i in range(nr)]); ax.set_yticklabels(rows, fontsize=9)
    ax.set_xticks(range(0, 721, 30)); ax.set_xticklabels([str(v % 360) for v in range(0, 721, 30)], fontsize=8.5)
    ax.set_xlim(0, 720); ax.set_ylim(-0.6, nr-0.1); ax.grid(axis="y", visible=False)
    ax.set_xlabel(t["e_x"])
    ax.set_title(t["e_title"], fontsize=10, loc="left", wrap=True)
    fig.text(0.01, 0.01, t["note"], fontsize=8, color=COL["m"], wrap=True)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig_19_evtable.png", lang)

if __name__ == "__main__":
    for lg in ("zh", "en"):
        sizing(lg); evtable(lg)
