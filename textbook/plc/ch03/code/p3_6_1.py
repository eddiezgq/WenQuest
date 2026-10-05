"""程序 3.6.1：用普通数字量输入数脉冲。扫描周期 10 ms 和 1 ms 时，1 s 内各频率的脉冲数到几个（图 3.6.1）。"""
from bookout import figure, out, T, style
from plcbook import read, run
from _draw03 import ACCENT, WARM, MUTED, INK

prog = read("p3_6_1.st")
FREQS = [5, 10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200, 300, 400, 500]


def counted(f, cycle):
    r = run(prog, plant="pulser", plant_opts={"f": f}, cycle=cycle, scenario={"steps": [{"wait": 1000}], "final": ["cnt.CV", "pulses"]})
    fin = r["scenario"]["final"]
    return fin["cnt.CV"], fin["pulses"]


c10 = {f: counted(f, 10) for f in FREQS}
c1 = {f: counted(f, 1) for f in FREQS}
ok10 = max(f for f in FREQS if c10[f][0] == c10[f][1])
ok1 = max(f for f in FREQS if c1[f][0] == c1[f][1])


def draw():
    plt = style()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(FREQS, [c10[f][0] for f in FREQS], "o-", color=WARM, lw=1.5, ms=4, label=T("扫描周期 10 ms", "scan 10 ms"))
    ax.plot(FREQS, [c1[f][0] for f in FREQS], "s-", color=ACCENT, lw=1.5, ms=4, label=T("扫描周期 1 ms", "scan 1 ms"))
    ax.plot(FREQS, [c10[f][1] for f in FREQS], color=INK, lw=0.9, ls=(0, (2, 2)), label=T("实际脉冲数", "actual pulses"), zorder=5)
    ax.set_xscale("log")
    ax.set_xticks([5, 10, 20, 50, 100, 200, 500]); ax.set_xticklabels(["5", "10", "20", "50", "100", "200", "500"])
    ax.set_xlabel(T("脉冲频率 / Hz", "pulse frequency / Hz"), fontsize=9.5)
    ax.set_ylabel(T("1 s 内数到的脉冲数", "pulses counted in 1 s"), fontsize=9.5)
    ax.legend(frameon=False, fontsize=8.6)
    ax.grid(True, which="both", color="#e6ebee", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return fig


figure(draw(), "fig3_6_1")
out(ok10=ok10, ok1=ok1, c10_60=c10[60][0], c10_100=c10[100][0], c10_200=c10[200][0], c1_500=c1[500][0])
