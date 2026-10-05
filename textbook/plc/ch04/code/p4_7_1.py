"""程序 4.7.1：现场故障案例。输送线从 2 m/s 提速到 5 m/s 后，计件少了。扫描时间约 10 ms（模型同程序 4.3.1），
分别跑 2 m/s 与 5 m/s 约 6 s，比较实际件数、CTU 的计数、高速计数器的计数；中途按一次清零，检查两种计数都从 0 重来。"""
from bookout import out
from plcbook import read, run

SM = {"base": 0.5, "perStep": 1}
prog = read("p4_7_1.st")


def go(fast2, ms=6010):   # reset released and run ended between part edges at both speeds, so both counts are settled
    r = run(prog, plant="counter", cycle=1, scan_model=SM, cycle_mode="free", watchdog=150, must_pass=False,
            scenario={"steps": [{"set": {"Fast": not fast2, "VeryFast": fast2}}, {"wait": 500}, {"set": {"S1_Reset": True}}, {"wait": 65},
                                {"set": {"S1_Reset": False}}, {"wait": ms}],
                      "final": ["cnt.CV", "countHsc", "since", "$maxScan", "pulseMs"]})
    return r["scenario"]["final"]


a, b = go(False), go(True)
# the reference is the plant's own count of parts since S1 was pressed ('since'); the image lags the plant by at most one scan
lost = 1 - b["cnt.CV"] / b["since"]
assert abs(a["cnt.CV"] - a["since"]) <= 1, a
assert abs(b["countHsc"] - b["since"]) <= 1, b
assert lost > 0.05, b
out(scan=round(b["$maxScan"], 1), n2=a["since"], c2=a["cnt.CV"], n5=b["since"], c5=b["cnt.CV"], h5=b["countHsc"], lost=round(100 * lost),
    pulse5=round(b["pulseMs"]), pulse2=round(a["pulseMs"]), rate5=round(5 / 0.1), rate2=round(2 / 0.1))
