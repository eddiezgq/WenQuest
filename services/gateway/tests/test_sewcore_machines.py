# -*- coding: utf-8 -*-
"""第 40 轮：包缝机、绷缝机计算核心。数字以教材算例为准（course/calc/ch09.py、ch10.py 的输出、第 9、10 讲正文）。"""
from app.sewcore import MACHINES, cover, overlock


def near(a, b, tol):
    return abs(a - b) <= tol


def test_overlock_textbook_example():
    p = overlock.clean({})
    pin, pout = overlock.crossings(p, 1.5)
    assert near(pin, 80.8, 0.05) and near(pout, 279.2, 0.05)                       # 9.5：80.8° 入布、279.2° 出布
    assert near(overlock.needle_h(p, 180), -13.52, 0.01)                           # 最低点在针板下 13.52 mm
    p3 = overlock.clean({"t": 3.0})
    a, b = overlock.crossings(p3, 3.0)
    assert near(a, 72.5, 0.05) and near(b, 287.5, 0.05)
    L = overlock.rssr(4.3619, 22.4789, 22, overlock.LL, 7000)
    assert near(L["swing"], 25.74, 0.01) and near(L["gmin"], 49.5, 0.05) and near(L["wmax"], 182.46, 0.05)   # 9.6 算例
    assert near(overlock.r_critical(22.4789, 22, overlock.LL, lo=4.4), 10.63, 0.01)                         # 临界偏心半径
    U = overlock.rssr(7.3801, 29.47, 20, overlock.UL, 7000)
    assert near(U["swing"], 50.5, 0.1) and near(U["gmin"], 39.0, 0.1)                                       # 上弯针：50.5°、39°
    J = overlock.diff_feed("jersey", 1.0, 1.0, 2.5)
    assert near(J["dstar"], 1.212, 0.001) and near(J["amp"], 4.05, 0.01)                                    # 9.10
    assert near(overlock.diff_feed("rib", 1.0, 1.0, 2.5)["dstar"], 1.375, 0.001)
    assert near(overlock.diff_feed("rib", 1.0, 1.0, 2.5)["amp"], 4.53, 0.01)
    assert near(overlock.diff_feed("jersey", 1.3, 1.0, 2.5)["eps"], -0.0598, 0.0001)
    F = overlock.diff_feed("fleece", 1.0, 1.0, 2.5)
    assert near(F["eps"], 0.10, 1e-9) and near(F["amp"], 3.62, 0.01)


def test_overlock_checks():
    r = overlock.analyze()
    st = {c["key"]: c["state"] for c in r["checks"]}
    assert st["feed_window"] == "ok" and st["ll_swing"] == "ok" and st["ll_gamma"] == "ok" and st["diff"] == "ok"
    assert st["ul_gamma"] == "warn"                      # 教材：上弯针 39°，略低于 40° 的经验值
    assert r["ok"] and len(r["charts"]) == 4 and r["view"]["page"] == "model-overlock"
    bad = {c["key"]: c["state"] for c in overlock.analyze({"D": 1.0, "ll_r": 11, "kn_ph": 300, "f_on": 270})["checks"]}
    assert bad["diff"] == "bad" and bad["ll_turn"] == "bad" and bad["knife_time"] == "bad" and bad["feed_window"] == "bad"


def test_cover_textbook_example():
    assert near(cover.RW[0], 0.98, 0.005) and near(cover.RW[1], 4.17, 0.005)
    E = cover.evaluate(dict(dphi=0, dz=0, e=1.0, gap=0.03, rr=3.2))
    assert near(E["fc"], 214.1, 0.05) and near(E["h"], 3.36, 0.005) and near(E["fd"], 129.9, 0.05) and near(E["fr"], 137.9, 0.05)
    assert all(E["ok"])
    assert not cover.evaluate(dict(dphi=5, dz=0, e=1.0, gap=0.03, rr=3.2))["ok"][0]       # 推迟 5°：回升 4.35 mm 超窗
    r = cover.analyze()
    res = {x["zh"]: x["value"] for x in r["results"]}
    assert res["弯针定时窗口"] == "-3.5 … +4.0" and res["窗口时间（最高转速）"] == "0.192"
    pl = r["plan"]                                                                             # T 恤 406：1000 件
    assert [round(x["meters"]) for x in pl] == [4623, 4623, 23117] and sum(x["cones"] for x in pl) == 7
    pl = cover.analyze({"stitch": "602"})["plan"]
    assert sum(x["cones"] for x in pl) == 10 and near(sum(x["ratio"] for x in pl), 23.24, 0.005)
    pl = cover.analyze({"stitch": "605", "g": 5.6, "Lcm": 80, "Q": 2000, "W": 0.10})["plan"]
    assert sum(x["cones"] for x in pl) == 13
    pl = cover.analyze({"stitch": "401", "spc": 4, "t": 2.4, "nr": 2, "Lcm": 60})["plan"]
    assert [round(x["meters"]) for x in pl] == [2231, 2285, 2231, 2285]
    assert r["ok"] and r["view"]["sync"] == "ST"


def test_every_machine_gives_the_common_fields():
    for k, M in MACHINES.items():
        r = M.analyze()
        for f in ("params", "checks", "ok", "results", "charts", "timing", "parts", "card", "view", "machine"):
            assert f in r, (k, f)
        assert r["machine"] == k and M.clean({"zz": 1}) == M.DEFAULTS
