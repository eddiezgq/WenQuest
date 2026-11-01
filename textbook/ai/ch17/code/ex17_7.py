"""算例 17.7.1—17.7.4：案例——产线日报智能体（17.7 节）。

（1）先把标准答案算出来：哪条线掉了产能、掉了多少。这件事数据里有定论，所以结论对不对可判。
（2）三种工具毛病，每一种都**不报错**，但都会让日报给出一个确信无疑的错结论。
（3）三道检查各挡掉哪一种。单开一道挡不住全部，三道一起才行。
（4）把检查装上要花多少——以及它们带来的误报。
"""
import numpy as np

from _ch17 import agent_report, factory_data, report_ok, truth, DAYS, LINES
from bookout import out

v = {}
data = factory_data()
tru = truth(data)

# ---------- （1）标准答案
v["lines"] = list(LINES)
v["days"] = DAYS
v["worst_line"] = tru["worst_line"]
v["worst_drop"] = tru["worst_drop_pct"]
v["drop_rows"] = [(k, round(val, 1)) for k, val in tru["drop"].items()]
for i, (k, val) in enumerate(tru["drop"].items(), start=1):
    v[f"drop_l{i}"] = round(val, 1)
v["most_downtime"], v["most_defect"] = tru["most_downtime"], tru["most_defect"]
v["defect_rows"] = [(k, round(val, 2)) for k, val in tru["defect_rate"].items()]
for i, (k, val) in enumerate(tru["defect_rate"].items(), start=1):
    v[f"defect_l{i}"] = round(val, 2)
assert v["worst_drop"] < -5, "第 25 天起二号线确实掉了产能，这是数据里有的"

# ---------- （2）（3）三种毛病、三道检查
FAULTS = (("一切正常", None),
          ("取数取成了上一周", {"fetch": "stale"}),
          ("分页没翻完，只取回四天", {"fetch": "partial"}),
          ("一条线的数来自另一个系统，单位是箱", {"fetch": "mixed"}))
CHECKS = (("全不开", ()),
          ("只查天数", ("length",)),
          ("只查量级", ("range",)),
          ("只做交叉核对", ("cross",)),
          ("三道全开", ("length", "range", "cross")))

v["matrix"] = []
grid = {}
for fname, faults in FAULTS:
    for cname, checks in CHECKS:
        rep, warn = agent_report(data, faults, checks)
        ok = report_ok(rep, tru)
        grid[(fname, cname)] = (ok, warn, rep["worst_line"], rep["worst_drop_pct"])
        v["matrix"].append((fname, cname, "对" if ok else "错", warn,
                            rep["worst_line"], round(rep["worst_drop_pct"], 1)))

# 什么都不查时，三种毛病各给出什么结论
for tag, fname in (("stale", "取数取成了上一周"), ("partial", "分页没翻完，只取回四天"),
                   ("mixed", "一条线的数来自另一个系统，单位是箱")):
    ok, warn, line, drop = grid[(fname, "全不开")]
    v[f"raw_{tag}_line"], v[f"raw_{tag}_drop"], v[f"raw_{tag}_warn"] = line, round(drop, 1), warn
    assert not ok, f"{fname}：不查的时候给出的是个错结论"
    assert warn == 0, f"{fname}：而且一个警都不报——这才是最要命的地方"

v["n_wrong_without_checks"] = sum(1 for (f, c), (ok, *_) in grid.items()
                                  if c == "全不开" and not ok)
v["n_wrong_with_checks"] = sum(1 for (f, c), (ok, *_) in grid.items()
                               if c == "三道全开" and not ok)
assert v["n_wrong_without_checks"] == 3 and v["n_wrong_with_checks"] == 0, \
    "三道检查全开，三种毛病都挡住了"

# 单开一道各挡住几种
v["single_rows"] = []
for cname, _ in CHECKS[1:-1]:
    caught = sum(1 for fname, _ in FAULTS[1:] if grid[(fname, cname)][0])
    v["single_rows"].append((cname, caught, 3))
    v[f"caught_{ {'只查天数': 'len', '只查量级': 'rng', '只做交叉核对': 'cross'}[cname] }"] = caught
v["best_single"] = max(c for _, c, _ in v["single_rows"])
assert v["best_single"] < 3, "没有哪一道检查能单独挡住全部三种毛病"

# ---------- （4）检查的代价与误报
ok_clean, warn_clean, _, _ = grid[("一切正常", "三道全开")]
v["clean_ok"], v["clean_warn"] = ok_clean, warn_clean
assert ok_clean, "一切正常时，开了检查也不该把对的结论改坏"
v["false_alarm_clean"] = warn_clean
# 换 20 批数据，看误报有多少
fa, wrong = 0, 0
for s in range(20):
    d = factory_data(seed=s)
    t = truth(d)
    rep, warn = agent_report(d, None, ("length", "range", "cross"))
    fa += warn
    wrong += 0 if report_ok(rep, t) else 1
v["n_runs"] = 20
v["false_alarms_20"] = fa
v["wrong_20"] = wrong
assert wrong == 0, "二十批数据上，开着检查一次都没答错"
v["false_alarm_rate"] = fa / 20

out(**v)
