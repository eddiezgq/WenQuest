"""程序 4.3.1：扫描时间随程序长度变化（扫描时间模型：固定开销 0.5 ms + 每条语句 1 µs，自由循环），看门狗 150 ms；
计件输送线带速 5 m/s（工件挡光 8 ms）时，扫描时间多长开始漏计（图 4.3.1 的数据）。"""
from bookout import figure, out, T, style
from plcbook import read, run
from _draw04 import ACCENT, WARM, RED, MUTED, GREEN, INK

SM = {"base": 0.5, "perStep": 1}
prog = read("p4_3_1.st")


def go(n, fast=False, fast2=False, ms=3000):
    text = prog.replace("n : DINT := 1000;", f"n : DINT := {n};")
    r = run(text, plant="counter", cycle=1, scan_model=SM, cycle_mode="free", watchdog=150, budget=10000000, must_pass=False,
            scenario={"steps": [{"set": {"Fast": fast, "VeryFast": fast2}}, {"wait": ms}], "final": ["cnt.CV", "parts", "$maxScan", "$scans"]})
    sc = r["scenario"]
    return sc["final"], sc["failures"]


NS = [0, 500, 1000, 2000, 3000, 4000, 5000, 7500, 10000, 15000, 20000, 30000]
rows = []
for n in NS:
    f2, _ = go(n, fast2=True)
    f1, _ = go(n, fast=True)
    rows.append((n, f2["$maxScan"], f2["cnt.CV"] / f2["parts"], f1["cnt.CV"] / f1["parts"]))
scan_1000 = next(s for n, s, _, _ in rows if n == 1000)
scan_5000 = next(s for n, s, _, _ in rows if n == 5000)
ok5 = max(s for n, s, a, b in rows if a >= 0.999)
miss5 = min(s for n, s, a, b in rows if a < 0.999)
ok2 = max(s for n, s, a, b in rows if b >= 0.999)
# the watchdog: a scan longer than 150 ms stops the PLC
WD_N = 100000
fw, fail = go(WD_N, ms=500)
wd_scan = 0.5 + WD_N * 2 / 1000
assert fail and "扫描时间" in fail[0], fail      # the time watchdog, not the step budget


def draw():
    plt = style()
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    xs = [s for _, s, _, _ in rows]
    ax.plot(xs, [100 * a for _, _, a, _ in rows], "o-", color=RED, lw=1.5, ms=4, label=T("带速 5 m/s（挡光 8 ms）", "belt 5 m/s (8 ms pulse)"))
    ax.plot(xs, [100 * b for _, _, _, b in rows], "s-", color=ACCENT, lw=1.5, ms=4, label=T("带速 2 m/s（挡光 20 ms）", "belt 2 m/s (20 ms pulse)"))
    ax.axvline(8, color=RED, lw=0.8, ls=(0, (4, 3))); ax.axvline(20, color=ACCENT, lw=0.8, ls=(0, (4, 3)))
    ax.set_xscale("log")
    ax.set_xticks([0.5, 1, 2, 5, 10, 20, 50]); ax.set_xticklabels(["0.5", "1", "2", "5", "10", "20", "50"])
    ax.set_xlabel(T("扫描时间 / ms", "scan time / ms"), fontsize=9.5)
    ax.set_ylabel(T("数到的工件 / %", "parts counted / %"), fontsize=9.5)
    ax.legend(frameon=False, fontsize=8.8, loc="lower left")
    ax.grid(True, which="both", color="#e6ebee", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return fig


figure(draw(), "fig4_3_1")
out(scan_1000=round(scan_1000, 1), scan_5000=round(scan_5000, 1), ok5=round(ok5, 1), miss5=round(miss5, 1), ok2=round(ok2, 1),
    wd_n=WD_N, wd_scan=round(wd_scan), per_iter_us=2)
