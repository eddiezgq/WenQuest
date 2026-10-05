"""程序 2.3.2 的测试：星三角启动电路在虚拟 7.5 kW 电动机上的 5 个测试；
与直接启动、过早切换（KT1 只等 1 s）比较启动电流和转速（图 2.3.5）。"""
from bookout import figure, out, T, style
from plcbook import read, run
from _draw02 import ACCENT, WARM, MUTED, RED, INK

S = [{"set": {"S1_Start": True}}, {"wait": 300}, {"set": {"S1_Start": False}}]
tests = [
    {"id": "star", "steps": [*S, {"wait": 1000}, {"expect": {"KM1_Closed": True, "KM2_Closed": True, "KM3_Closed": False}}]},
    {"id": "delta", "steps": [*S, {"until": {"KM3_Closed": True}, "within": 6000}, {"wait": 100},
                              {"expect": {"KM1_Closed": True, "KM2_Closed": False, "short": False}}]},
    {"id": "never-both", "steps": [*S, {"never": {"short": True}, "during": 8000}]},
    {"id": "stop", "steps": [*S, {"wait": 7000}, {"set": {"S2_Stop": False}}, {"wait": 40},
                             {"expect": {"KM1_Closed": False, "KM3_Closed": False}}, {"set": {"S2_Stop": True}}, {"never": {"KM1_Main": True}, "during": 2000}]},
    {"id": "weld", "faults": {"weld2": True}, "steps": [*S, {"wait": 8000}, {"expect": {"KM3_Closed": False, "short": False}}]},
]
prog = read("p2_3_2.st")
SC = {"steps": [*S, {"wait": 9000}], "trace": ["current", "speed", "KM3_Closed"], "every": 5}
r = run(prog, plant="stardelta", tests=tests, review=True, cycle=1, scenario=SC)
assert not [x for x in r["review"] if x["level"] == "error"], r["review"]
DOL = """PROGRAM Main
  KM1_Main := (S1_Start OR KM1_Aux) AND S2_Stop AND F1_OL;
  KM3_Delta := KM1_Main;
  KM2_Star := FALSE;
END_PROGRAM
"""
rd = run(DOL, plant="stardelta", cycle=1, scenario=SC)
re = run(prog.replace("T#5s", "T#1s"), plant="stardelta", cycle=1, scenario=SC)


def series(res):
    tr = res["scenario"]["trace"]
    return [t / 1000 for t in tr["t"]], tr["v"][0], tr["v"][1], tr["v"][2]


t, i_sd, n_sd, k3 = series(r)
_, i_dol, n_dol, _ = series(rd)
_, i_early, n_early, k3e = series(re)
sw = next(k for k, v in enumerate(k3) if v)                 # first sample with KM3 closed
swe = next(k for k, v in enumerate(k3e) if v)
i_star = max(i_sd[:sw])
i_switch = max(i_sd[sw:sw + 40])
i_direct = max(i_dol)
i_early_sw = max(i_early[swe:swe + 40])
n_switch = n_sd[sw - 10]                                     # speed just before the change-over
n_switch_e = n_early[swe - 10]
t_rated = next(tt for tt, n in zip(t, n_sd) if tt > t[sw] and n >= 0.98 * max(n_sd))
t_rated_dol = next(tt for tt, n in zip(t, n_dol) if n >= 0.98 * max(n_dol))
i_rated = i_sd[-1]


def draw():
    plt = style()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.4, 6.6), sharex=True)
    for ax, ys, unit in ((a1, (i_dol, i_sd, i_early), T("电流 / A", "current / A")), (a2, (n_dol, n_sd, n_early), T("转速 / (r/min)", "speed / (r/min)"))):
        ax.plot(t, ys[0], color=MUTED, lw=1.3, ls=(0, (5, 2)), label=T("直接启动", "direct on line"))
        ax.plot(t, ys[1], color=ACCENT, lw=1.7, label=T("星三角，KT1 = 5 s", "star–delta, KT1 = 5 s"))
        ax.plot(t, ys[2], color=WARM, lw=1.2, label=T("星三角，KT1 = 1 s（切换过早）", "star–delta, KT1 = 1 s (too early)"))
        ax.set_ylabel(unit, fontsize=9.5)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
    a1.legend(frameon=False, fontsize=8.6, loc="upper right")
    a1.annotate(T(f"星形：约 {i_star:.0f} A", f"star: about {i_star:.0f} A"), xy=(1.0, i_sd[int(1000 / 5)]), xytext=(1.6, 60), fontsize=8.6,
                color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    a1.annotate(T(f"切到三角形：约 {i_switch:.0f} A", f"to delta: about {i_switch:.0f} A"), xy=(t[sw], i_switch), xytext=(t[sw] + 0.6, 55), fontsize=8.6,
                color=ACCENT, arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    a2.set_xlabel(T("时间 / s", "time / s"), fontsize=9.5)
    return fig


figure(draw(), "fig2_3_5")
out(passed=r["passed"], total=r["total"], i_star=round(i_star), i_switch=round(i_switch), i_direct=round(i_direct), i_early=round(i_early_sw),
    ratio=round(i_direct / i_star, 1), n_switch=round(n_switch), n_switch_e=round(n_switch_e), t_switch=round(t[sw], 2),
    t_rated=round(t_rated, 1), t_rated_dol=round(t_rated_dol, 1), i_rated=round(i_rated, 1), pct_switch=round(100 * n_switch / 1500))
