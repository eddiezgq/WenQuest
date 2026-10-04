"""15.7 节：回程中途断电 0.5 s。状态保持（程序 15.7.1）与上电进 INIT（程序 15.5.1）的对比（图 15.7.1）。"""
from bookout import T, figure, out, style
from plcbook import read, run
from _press import HANDS, HOME, LOAD
from _draw15 import ACCENT, GREEN, MUTED, RED

steps = [{"set": {"S_Auto": True}}] + HOME + [LOAD, {"wait": 200}, HANDS, {"until": {"B_PressDown": True}, "within": 5000},
                                              {"wait": 600}, {"power": 500}, {"wait": 2500}]
names = ["ram", "Y_PressUp", "H_Ready"]
runs = {}
for key, prog in (("good", "p15_5_1.st"), ("bad", "p15_7_1.st")):
    r = run(read(prog), plant="press", scenario={"steps": steps, "trace": ["Y_PressUp", "H_Ready", "B_PressUp"]}, must_pass=False)
    runs[key] = r["scenario"]
plt = style()
fig, axes = plt.subplots(2, 1, figsize=(9, 4.6), sharex=True)
for ax, key, title in ((axes[0], "bad", T("程序 15.7.1：状态保持，来电后压头自己上行", "Program 15.7.1: state retained, the ram moves up by itself")),
                       (axes[1], "good", T("程序 15.5.1：上电进 INIT，等人复位", "Program 15.5.1: power-up into INIT, waits for reset"))):
    sc = runs[key]
    t = [x / 1000 for x in sc["trace"]["t"]]
    on = next(x for x, k, _ in sc["log"] if k == "power") / 1000
    for k, (name, col, y0) in enumerate((("Y_PressUp", ACCENT, 1.2), ("B_PressUp", GREEN, 0.0))):
        v = sc["trace"]["v"][sc["trace"]["names"].index(name)]
        ax.step(t, [y0 + (0.8 if x else 0) for x in v], where="post", color=col, lw=1.5)
        ax.text(on - 1.25, y0 + 0.35, name, ha="right", fontsize=9, family="monospace")
    ax.axvspan(on - 0.5, on, color="#f3d0cd", lw=0)
    ax.text(on - 0.25, 2.15, T("断电", "power off"), ha="center", fontsize=9, color=RED)
    ax.set_title(title, fontsize=10, loc="left")
    ax.set_yticks([]); ax.set_ylim(-0.2, 2.4); ax.set_xlim(on - 1.2, on + 2.5)
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
axes[1].set_xlabel(T("时间 / s", "time / s"))
figure(fig, "fig15_7_1")
out(power_at_s=round(next(x for x, k, _ in runs["good"]["log"] if k == "power") / 1000 - 0.5, 2))
