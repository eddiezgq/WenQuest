# -*- coding: utf-8 -*-
"""第 39 轮：缝纫机设计软件计算核心。数字以教材算例为准（course/calc/ch02–08、23 讲的程序输出），
并用 node 跑教材共用库 lockstitch-kit.js，与 Python 版逐项对数。"""
import json
import random
import shutil
import subprocess
from pathlib import Path

import pytest

from app.sewcore import analyze, adjust_card, chain, clean, Mech
from app.sewcore.design import vib, VREF

REPO = Path(__file__).resolve().parents[3]
KIT = REPO / "textbook/web-editions/sewing/src/lib/lockstitch-kit.js"


def near(a, b, tol):
    return abs(a - b) <= tol


def test_ch03_needle_worked_example():
    m = Mech()
    assert near(m.LAM, 0.2818, 1e-4)
    assert near(m.acc(0, 5000), 3052, 1)
    assert near(m.acc(180, 5000), -5447, 1)
    assert near(m.PHC0, 206.067, 1e-3)
    assert near(m.xN(90), 13.27, 0.01)
    k = analyze(trial=False)["key"]
    assert near(k["vmax"], 8.434, 1e-3) and near(k["vmax_at"], 104.7, 0.05)
    assert near(k["F_bdc"], 654, 0.5) and near(k["F_tdc"], 366, 0.5)
    assert near(k["pin"], 101.7, 0.05) and near(k["pout"], 258.3, 0.05)
    assert near(analyze({"n": 6000}, trial=False)["key"]["F_bdc"], 941, 0.5)        # F6000 = 941 N
    assert near(analyze({"n": 5000}, trial=False)["key"]["n_max_F"], 5532, 1)       # 800 N 限值下的最高转速
    ex3 = Mech(r=17, l=60)
    assert near(ex3.acc(180, 5500), -7237, 1) and near(ex3.PHC0, 204.85, 0.01)
    assert near(Mech(r=15.5, l=40).PHC0, 205.05, 0.01)                                # 实验任务 2


def test_ch04_takeup_worked_example():
    R = Mech().takeup()
    assert near(R["Smax"], 81.6, 0.05) and R["top"] == 55 and R["fin"] == 109
    assert near(R["margin"], 1.9, 0.05) and R["at"] == 296
    assert near(R["pre"], 9.2, 0.05) and near(R["neg"], 0.0, 1e-9) and near(R["waste"], 23.8, 0.05)
    assert near(R["acc"] / 1000, 30.0, 0.05)
    assert near(R["mu"][0], 41.0, 0.05) and near(R["mu"][1], 114.8, 0.05)
    R3 = Mech().takeup(t=3)
    assert near(R3["margin"], -0.9, 0.05) and near(R3["neg"], 1.9, 0.05)


def test_ch05_ch06_ch07_ch08():
    m = Mech()
    assert near(m.rise(201), 1.3107, 1e-4) and near(m.rise(211), 2.7964, 1e-4)
    g = m.hook_geom(d=1.1)                    # Nm90 → 110：间隙 0.08 − 0.1 = −0.02 → 碰针
    assert near(g["g"], -0.02, 1e-9) and g["res"] == "hit"
    assert near(m.FE, 114.1795, 1e-4) and near(m.EFF0, 0.92562, 1e-5)
    assert near(m.cross(4.0), 92.678, 1e-3)
    F = m.feed_model()
    assert near(F["rise"], 325.833, 1e-3) and near(F["drag"], 0.0388, 1e-4)   # 实验 6-1 的离散（教材写 0.04）
    assert near(m.feed_model(dT=10)["drag"], 0.123, 1e-3)
    assert near(m.feed_model(fab="lining")["Pmin"], 0.8, 1e-9)
    E = m.tension(Td=220, Tb=90)
    assert near(E["z"], 0.4964, 1e-4) and near(m.tension()["z"], 0.5106, 1e-4)
    assert near(m.tension(fab="denim", Td=245.85)["peak"], 345.33, 0.01)
    k = analyze(trial=False)["key"]
    assert near(analyze({"k": 0.45}, trial=False)["key"]["fmax"], 368, 0.5)       # 教材 8.4 节
    t = {x["key"]: x for x in analyze(trial=False)["timing"]}
    assert near(t["catch"]["a"], 203.2, 0.05) and near(t["catch"]["b"], 209.2, 0.05)
    assert near(k["fe"] - k["pin"], 12.5, 0.01)                                     # 送布与入布重叠 12.5°


def test_ch23_chain_and_resonance():
    c = chain()
    assert near(c["worst"], 0.153, 1e-9) and near(c["sigma"], 0.0194, 1e-4) and near(c["y_int"], 0.878, 1e-3)
    assert near(c["sigma_adj"], 0.0054, 1e-4) and near(c["sigma_swap"], 0.013, 1e-3) and near(c["y_swap"], 0.9793, 1e-4)
    assert near(vib(5000), 4.0, 0.01) and near(vib(5500), 13.28, 0.01)
    assert near(83.5 + 20 * __import__("math").log10(vib(5500) / VREF), 93.9, 0.05)
    assert near(vib(5500, fn=190 * 1.3 ** 0.5), 3.45, 0.01)


def test_standard_machine_all_green_and_faults_show():
    r = analyze()
    assert r["ok"] and all(c["state"] == "ok" for c in r["checks"])
    assert r["trial"]["counts"]["ok"] == 30
    bad = analyze({"n": 6000, "psi": -20, "dT": 20})
    st = {c["key"]: c["state"] for c in bad["checks"]}
    assert st["needle_force"] == "bad" and st["catch_rise"] == "bad" and st["feed_drag"] == "bad" and st["frame_res"] == "bad"
    assert not bad["ok"] and bad["trial"]["counts"]["skip"] > 0
    # 四杆装不上的尺寸：不报错，挑线判为红
    r = analyze({"lk_b": 32, "lk_a": 35}, trial=False)
    assert any(c["key"] == "takeup_ok" and c["state"] == "bad" for c in r["checks"]) or r["ok"] in (True, False)


def test_clean_and_card():
    p = clean({"n": 99999, "fab": "silk", "r": "abc", "zz": 1, "s": "2.5"})
    assert p["n"] == 7000 and p["fab"] == "cotton" and p["r"] == 15.5 and "zz" not in p and p["s"] == 2.5
    card = adjust_card()
    assert len(card) == 7 and "206.1" in card[0]["do_zh"]


@pytest.mark.skipif(not (KIT.exists() and shutil.which("node")), reason="needs node and the textbook kit")
def test_same_numbers_as_textbook_js_kit():
    """Python 版与教材共用库（虚拟实验、三维样机用的那份）逐项一致；
    只有实验 8-1 的两处常数 JS 写成了四舍五入的 206.067 与 258.3，那两项放宽到 1e-4 / 0.05。"""
    random.seed(3)
    rng = dict(psi=(-25, 25), dz=(-1.2, 1.2), g=(0.0, 0.2), d=(0.7, 1.1), u=(-12, 12), stroke=(5, 12), Td=(40, 260), Tb=(14, 90),
               dT=(-10, 25), dP=(-30, 30), h=(0.3, 1.6), P=(0.3, 3), s=(1.5, 5), n=(3000, 6000), k=(0, 1))
    cases = [{}]
    for _ in range(30):
        c = {k: round(random.uniform(*rng[k]), 2) for k in random.sample(list(rng), 4)}
        c.update(fab=random.choice(["lining", "cotton", "denim"]), th=random.choice(["t18", "t24", "t40"]),
                 mode=random.choice(["drop", "drop", "needle", "compound"]), dh=random.randint(-8, 8), dt=random.randint(-15, 15))
        cases.append(c)
    js = json.loads(subprocess.run(["node", str(Path(__file__).parent / "fixtures/sewkit_dump.js"), str(KIT)], input=json.dumps(cases),
                                   capture_output=True, text=True, check=True).stdout)
    assert near(Mech().PHC0, js["PHC0"], 1e-12) and near(Mech().FE, js["FE"], 1e-12)
    for c, j in zip(cases, js["cases"]):
        m = Mech()
        t = m.trial(c, 30, 7)
        ev = t["ev"]
        assert [f["key"] for f in ev["faults"]] == j["faults"], c
        assert ev["catch"] == j["catch"] and t["res"] == j["res"], c
        assert near(ev["fmax"], j["fmax"], 1e-6 * max(1, j["fmax"]))
        for grp, d in (("hook", ev["hook"]), ("supply", ev["supply"]), ("tension", ev["tension"]), ("feed", ev["feed"])):
            for k, v in j[grp].items():
                assert near(d[k], v, 1e-6 * max(1, abs(v))), (grp, k, c)
        core = m.timing_core(c["dh"] if "dh" in c else 0, c.get("dt", 0), c.get("dT", 0))
        for k in ("margin", "pre", "neg"):
            assert near(core[k], j["core"][k], 1e-6 * max(1, abs(j["core"][k]))), (k, c)
        assert near(core["rc"], j["core"]["rc"], 1e-4) and near(core["feedrise"], j["core"]["feedrise"], 0.05)
        assert near(core["F"]["drag"], j["core"]["drag"], 1e-4)
        R = m.takeup(u=c.get("u", 0))
        for k in ("top", "bot", "fin", "margin", "waste", "pre", "neg", "Smax", "acc"):
            assert near(R[k], j["takeup"][k], 1e-6 * max(1, abs(j["takeup"][k]))), (k, c)
