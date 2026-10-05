"""程序 2.3.1 的测试：正反转电路（双重互锁）在虚拟正反转电动机上的 7 个测试；
再比较三种互锁做法在“运行中直接按反转”时会不会相间短路（各 200 次，接触器断开时的电弧长短随机），
画出换向时的触点时序（图 2.3.3）和反接时的电流、转速。

扫描周期取 1 ms：继电器电路里各支路是同时通电的，1 ms 的扫描足以近似（比接触器动作快一个数量级）。"""
from bookout import figure, out, T, style
from plcbook import read, run
from _draw02 import timing_ms, ACCENT, GREEN, RED, WARM, MUTED, INK

F = [{"set": {"S1_Fwd": True}}, {"wait": 300}, {"set": {"S1_Fwd": False}}]
R = [{"set": {"S3_Rev": True}}, {"wait": 300}, {"set": {"S3_Rev": False}}]
STOP = [{"set": {"S2_Stop": False}}, {"wait": 300}, {"set": {"S2_Stop": True}}]
tests = [
    {"id": "fwd", "steps": [*F, {"wait": 3000}, {"expect": {"KM1_Closed": True, "KM2_Closed": False}}]},
    {"id": "stop", "steps": [*F, {"wait": 3000}, {"set": {"S2_Stop": False}}, {"wait": 40}, {"expect": {"KM1_Closed": False}},
                             {"set": {"S2_Stop": True}}, {"never": {"KM1_Fwd": True}, "during": 2000}]},
    {"id": "rev", "steps": [*F, {"wait": 3000}, *STOP, {"wait": 3000}, *R, {"wait": 3000}, {"expect": {"KM2_Closed": True, "short": False}}]},
    {"id": "direct", "steps": [*F, {"wait": 3000}, *R, {"wait": 3000}, {"expect": {"KM2_Closed": True, "KM1_Closed": False, "short": False}}]},
    {"id": "both", "steps": [{"set": {"S1_Fwd": True, "S3_Rev": True}}, {"wait": 500}, {"set": {"S1_Fwd": False, "S3_Rev": False}}, {"wait": 500},
                             {"expect": {"KM1_Closed": False, "KM2_Closed": False, "short": False}}]},
    # KM1 welds on its second closing: first prove the reverse works, then weld KM1 and try to reverse
    {"id": "weld", "faults": {"weld1": True}, "steps": [*F, {"wait": 2000}, *STOP, {"wait": 2000}, *R, {"wait": 2000}, {"expect": {"KM2_Closed": True}},
                                                        *STOP, {"wait": 2000}, *F, {"wait": 2000}, *R, {"wait": 2000},
                                                        {"expect": {"KM1_Closed": True, "KM2_Closed": False, "short": False}}]},
    {"id": "overload", "faults": {"heavy": True}, "steps": [*F, {"until": {"tripped": True}, "within": 20000}, {"wait": 40}, {"expect": {"KM1_Closed": False}}]},
]
TRACE = ["S3_Rev", "KM1_Fwd", "KM1_Main", "KM1_Aux", "KM2_Rev", "KM2_Main", "KM2_Aux"]





SEED = 8           # a typical opening: the arc lasts about 6 ms
prog = read("p2_3_1.st")
r = run(prog, plant="reversing", tests=tests, review=True, cycle=1,
        scenario={"steps": [*F, {"wait": 3000}, *R, {"wait": 400}], "trace": TRACE, "seed": SEED})
assert not [x for x in r["review"] if x["level"] == "error"], r["review"]
trip_s = next(t for t in r["tests"] if t["id"] == "overload")["time"] / 1000

# the same circuit with only the button interlock, and with no interlock at all
BUTTON = prog.replace(" AND NOT KM2_Aux", "").replace(" AND NOT KM1_Aux", "")
NONE = BUTTON.replace(" AND NOT S3_Rev", "").replace(" AND NOT S1_Fwd", "")
N = 200


def shorts(text):
    ts = [{"id": f"s{i}", "seed": 1000 + i, "steps": [*F, {"wait": 2000}, *R, {"wait": 500}, {"expect": {"short": False}}]} for i in range(N)]
    res = run(text, plant="reversing", tests=ts, cycle=1, must_pass=False)
    bad = [int(t["id"][1:]) for t in res["tests"] if not t["ok"]]
    return len(bad), bad


n_double, _ = shorts(prog)
n_button, bad_button = shorts(BUTTON)
n_none, _ = shorts(NONE)
assert n_double == 0 and n_none == N and 0 < n_button < N // 2, (n_double, n_button, n_none)

# a direct reversal with only the button interlock where the arc lasts long enough to short-circuit
rb = run(BUTTON, plant="reversing", cycle=1, must_pass=False,
         scenario={"steps": [*F, {"wait": 2000}, *R, {"wait": 400}], "trace": TRACE + ["short"], "seed": 1000 + bad_button[0]})

tr = r["scenario"]["trace"]


def edge(trace, name, rising, after):
    k = trace["names"].index(name)
    return next(t for t, v in zip(trace["t"], trace["v"][k]) if bool(v) == rising and t >= after)


t_press = edge(tr, "S3_Rev", True, 1000)
t1_off = edge(tr, "KM1_Main", False, t_press)          # the arc on KM1's main contacts is out
t1_aux = edge(tr, "KM1_Aux", False, t_press)
t2_on = edge(tr, "KM2_Main", True, t_press)
margin = t2_on - t1_off
trb = rb["scenario"]["trace"]
tb_press = edge(trb, "S3_Rev", True, 1000)
tb2_on = edge(trb, "KM2_Main", True, tb_press)
tb1_off = edge(trb, "KM1_Main", False, tb_press) if any(not v for t, v in zip(trb["t"], trb["v"][trb["names"].index("KM1_Main")]) if t > tb_press) else None

# plugging: speed and current through a direct reversal (10 ms samples)
rs = run(prog, plant="reversing", cycle=1,
         scenario={"steps": [*F, {"wait": 2500}, *R, {"wait": 2500}], "trace": ["speed", "current"], "every": 10})
ts = rs["scenario"]["trace"]
spd, cur = ts["v"][0], ts["v"][1]
t_s = [x / 1000 for x in ts["t"]]
t_rev_press = 300 + 2500                                                          # S3 pressed 2.5 s after S1 was released
i_start = max(cur[: int(1500 / 10)])
i_plug = max(cur[int(t_rev_press / 10):])
t_zero = next(t for t, v in zip(ts["t"], spd) if t > t_rev_press and v <= 0) - t_rev_press
t_full = next(t for t, v in zip(ts["t"], spd) if t > t_rev_press and v <= -0.95 * max(spd)) - t_rev_press


def draw():
    plt = style()
    fig = plt.figure(figsize=(10.5, 7.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], hspace=0.45, wspace=0.32)
    a1, a2, a3 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, :])
    rows = [("S3_Rev", "S3", GREEN), ("KM1_Fwd", T("KM1 线圈", "KM1 coil")), ("KM1_Main", T("KM1 主触点", "KM1 main"), WARM),
            ("KM1_Aux", T("KM1 辅助", "KM1 aux"), GREEN), ("KM2_Rev", T("KM2 线圈", "KM2 coil")), ("KM2_Main", T("KM2 主触点", "KM2 main"), WARM)]
    timing_ms(a1, tr, rows, -5, 55, zero=t_press, marks=[(t1_off, T("电弧熄灭", "arc out")), (t2_on, "")],
              title=T("（a）双重互锁：先断后通", "(a) double interlock: break before make"))
    a1.annotate("", xy=(t2_on - t_press, 1.2 * 0.5 + 0.35), xytext=(t1_off - t_press, 1.2 * 0.5 + 0.35),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.0))
    a1.text((t1_off + t2_on) / 2 - t_press, 1.2 * 0.5 + 0.5, f"{margin:.0f} ms", ha="center", fontsize=8.5, color=RED)
    timing_ms(a2, trb, rows, -5, 55, zero=tb_press, marks=[(tb2_on, T("相间短路", "phase short"))],
              title=T("（b）只有按钮互锁：电弧还没熄灭，KM2 已经闭合", "(b) button interlock only: KM2 closes into the arc"))
    a3.plot(t_s, spd, color=ACCENT, lw=1.5, label=T("转速 / (r/min)", "speed / (r/min)"))
    a3.set_ylabel(T("转速 / (r/min)", "speed / (r/min)"), color=ACCENT, fontsize=9)
    a3.axhline(0, color=MUTED, lw=0.6)
    b3 = a3.twinx()
    b3.plot(t_s, cur, color=WARM, lw=1.3)
    b3.set_ylabel(T("电流 / A", "current / A"), color=WARM, fontsize=9)
    a3.axvline(t_rev_press / 1000, color=MUTED, lw=0.8, ls=(0, (4, 3)))
    a3.text(t_rev_press / 1000 + 0.6, -0.45 * max(spd), T("按 S3：反接制动，再反向加速", "S3: plug braking, then reverse"), fontsize=8.5, color=MUTED)
    a3.text(0.6, -0.45 * max(spd), T("按 S1：直接启动", "S1: direct start"), fontsize=8.5, color=MUTED)
    a3.set_xlabel(T("时间 / s", "time / s"), fontsize=9)
    a3.set_title(T("（c）运行中直接换向：转速与电流", "(c) direct reversal while running: speed and current"), fontsize=10)
    for s in ("top",):
        a3.spines[s].set_visible(False); b3.spines[s].set_visible(False)
    return fig


figure(draw(), "fig2_3_3")
out(passed=r["passed"], total=r["total"], margin_ms=margin, aux_ms=t1_aux - t_press, km1_off_ms=t1_off - t_press, km2_on_ms=t2_on - t_press,
    n=N, n_double=n_double, n_button=n_button, n_none=n_none, pct_button=round(100 * n_button / N),
    i_start=round(i_start, 1), i_plug=round(i_plug, 1), i_ratio=round(i_plug / 1.9, 1), t_zero=round(t_zero / 1000, 2),
    t_full=round(t_full / 1000, 1), trip_s=round(trip_s, 1))
