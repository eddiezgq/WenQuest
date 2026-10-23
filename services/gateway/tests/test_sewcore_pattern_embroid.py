"""第 42 轮：电子花样机、多头刺绣机计算核心——逐项对上教材第 15、16 章的算例和习题答案。"""
import math

import pytest

from app import sewcore
from app.sewcore import embroid as E
from app.sewcore import pattern as P


# ---------------- 花样机（第 15 章） ----------------
def test_window_table_15_3():
    for t, f1, f2, W in ((1.5, 101.7, 258.3, 203.4), (3, 96.3, 263.7, 192.6), (6, 85.2, 274.8, 170.5)):
        a, b, w = P.window(t)
        assert a == pytest.approx(f1, abs=0.1) and b == pytest.approx(f2, abs=0.1) and w == pytest.approx(W, abs=0.15)


def test_speed_limit_and_exercises():
    W = P.window(1.5)[2]
    tm = P.t_axis(3, 50, 1)
    assert tm * 1000 == pytest.approx(15.5, abs=0.05)
    assert P.n_max(W, tm) == pytest.approx(2190, abs=5)                       # 15.3 节：约 2190 r/min
    assert P.n_max(P.window(3)[2], P.t_axis(5, 50, 1)) == pytest.approx(1600, abs=10)   # 习题 1
    # 习题 2：针距 8 mm、布厚 1.5 mm 仍要 2000 r/min，每轴加速度约 111 m/s²
    a = 4 * 0.008 / ((W / (6 * 2000)) ** 2)
    assert a == pytest.approx(111, abs=1.5)
    # 斜向 45°：每轴 s/√2，时间 × 0.84，转速约高 19%
    assert P.t_axis(3 / math.sqrt(2), 50, 1) / tm == pytest.approx(2 ** -0.25, abs=1e-6)
    # 摆线规律：Δt × 1.25，转速 × 0.80
    assert P.t_axis(3, 50, 1, 6.28) / tm == pytest.approx(1.253, abs=0.002)


def test_lookahead_example_15_4_3():
    W = P.window(1.5)[2]
    caps = [2680] * 4 + [P.n_max(W, P.t_axis(10, 50, 1))] + [2680] * 3
    assert caps[4] == pytest.approx(1198, abs=1)
    n = P.lookahead([2680] + caps, 300, n0=2680)[1:]
    assert [round(x) for x in n] == [2398, 2098, 1798, 1498, 1198, 1498, 1798, 2098]
    n2 = P.lookahead([2680] + caps, 200, n0=2680)[1:]                       # 习题 4：Δn = 200，提前更多针减速
    assert round(n2[4]) == 1198 and round(n2[0]) == 1998


def test_x_axis_motor_15_8_and_belt():
    duty = 203.4 / 360
    M = P.axis_motor(3, 50, 15, 0.3, 1.27, 3.8, 0.05, 1, 3000, duty)
    assert M["F"] == pytest.approx(151.5, abs=0.1) and M["Tpk"] == pytest.approx(2.37, abs=0.01)
    assert M["Trms"] == pytest.approx(1.79, abs=0.02) and not M["ok_rms"] and M["rpm"] == pytest.approx(637, abs=1)
    M2 = P.axis_motor(3, 50, 10, 0.3, 1.27, 3.8, 0.05, 1, 3000, duty)       # 第二条路：带轮半径 10 mm
    assert M2["Tpk"] == pytest.approx(1.67, abs=0.02) and M2["Trms"] == pytest.approx(1.26, abs=0.02) and M2["ok_rms"]
    assert M2["r_opt"] == pytest.approx(3.2, abs=0.05)
    k, fn = P.belt(150, 0.3, 0.5, 3)
    assert k == pytest.approx(800e3) and fn == pytest.approx(82, abs=0.5)
    assert P.belt(250, 0.3, 0.5, 3)[1] == pytest.approx(106, abs=0.5)


def test_defaults_green_and_red_cases():
    R = P.analyze({})
    assert R["ok"] and all(c["state"] == "ok" for c in R["checks"]), [c for c in R["checks"] if c["state"] != "ok"]
    R = P.analyze({"rx": 15})                                                 # 教材原来的 400 W 电机 + 15 mm 带轮：发热超
    assert {c["key"] for c in R["checks"] if c["state"] == "bad"} == {"x_rms"}
    R = P.analyze({"n": 2600})
    assert "speed" in {c["key"] for c in R["checks"] if c["state"] == "bad"}
    R = P.analyze({"EA": 100, "nyb": 1})
    assert {c["key"]: c["state"] for c in R["checks"]}["belt_x"] in ("warn", "bad")


def test_patterns_csv_and_plan():
    for k in ("flap", "circle", "star", "rect", "bartack", "zig"):
        R = P.analyze({"pat": k})
        assert R["plan"]["n"] > 5 and R["plan"]["t_sew"] > 0, k
        sp = R["charts"][0]["series"][1]["y"]
        lim = R["charts"][0]["series"][0]["y"]
        assert all(a <= b + 0.5 for a, b in zip(sp, lim)), k                # 前瞻后每针都不超过自身上限
    csv = "x,y\n0,0\n3,0\n6,0\n9,0\n19,0\n22,0\n25,0\n28,0\n"
    R = P.analyze({"pat": "csv", "pts": csv})
    assert R["params"]["pts"][4] == [19.0, 0.0] and R["plan"]["n"] == 8
    sp = R["charts"][0]["series"][1]["y"]
    assert sp[4] < sp[3] or sp[4] < 1500                                    # 10 mm 的长针前已减速
    assert P.analyze({"pat": "csv"})["params"]["pat"] == "flap"               # 没传针位表就回到口袋盖
    assert P.parse_pts("a,b\n1,2\nbad\n3;4") == [[1.0, 2.0], [3.0, 4.0]]
    big = P.analyze({"pat": "csv", "pts": [[0, 0], [400, 0]]})
    assert {c["key"]: c["state"] for c in big["checks"]}["travel"] == "bad"


# ---------------- 刺绣机（第 16 章） ----------------
def test_frame_acceleration_and_speed_16_3():
    assert E.a_req(3, 800) == pytest.approx(10.4, abs=0.05) and E.a_req(7, 800) == pytest.approx(24.4, abs=0.05)
    assert E.mass(8) == 42 and E.a_max(8) == pytest.approx(17.9, abs=0.05) and E.a_max(15) == pytest.approx(10.7, abs=0.05)
    assert [round(E.n_max(s, E.a_max(8)), -1) for s in (3, 5, 7)] == [1050, 810, 690]
    assert [round(E.n_max(7, E.a_max(h)), -1) for h in (4, 15, 20)] == [870, 530, 470]
    assert E.force_req(7, 850, 8) == pytest.approx(1200, abs=10)


def test_exercises_16():
    assert E.n_max(5, E.a_max(12, 1000)) == pytest.approx(776, abs=1)        # 习题 1
    assert E.a_req(6, 900) == pytest.approx(26.4, abs=0.1) and E.force_req(6, 900, 6) == pytest.approx(950, abs=5)   # 习题 2
    assert E.dst_records(30, 0) == 3 and E.dst_records(30 / 2 ** 0.5, 30 / 2 ** 0.5) == 2                           # 习题 3
    p = E.clean({"N": 15000, "lam": 0.4, "t_fix": 45, "t_back": 0, "colors": 5, "t_color": 6})
    assert E.production(p, 12, 750)["eff"] == pytest.approx(0.77, abs=0.005)                                        # 习题 4


def test_efficiency_16_6():
    p = E.clean({"n": 800})
    eff = {h: E.production(p, h, 800) for h in (4, 8, 15, 20)}
    assert [round(eff[h]["eff"] * 100) for h in (4, 8, 15, 20)] == [88, 80, 69, 63]
    assert eff[4]["pph"] == pytest.approx(8.5, abs=0.1) and eff[8]["pph"] == pytest.approx(15.4, abs=0.1) and eff[20]["pph"] == pytest.approx(30, abs=0.5)


def test_embroid_defaults_and_red():
    R = E.analyze({})
    assert R["ok"] and all(c["state"] == "ok" for c in R["checks"])
    R = E.analyze({"n": 800})                                                 # 8 头、7 mm、800 r/min：24.4 > 17.9
    assert [c["key"] for c in R["checks"] if c["state"] == "bad"] == ["accel"]
    assert E.analyze({"b": 6})["checks"][3]["state"] == "bad"                 # 回退少于检测延迟
    assert R["view"] == {"page": "embroid", "sync": "A", "cfg": {"H": 8, "F": 800, "s": 7.0, "n": 800}}


def test_registry_and_common_fields():
    for k in ("pattern", "embroid"):
        M = sewcore.get(k)
        R = M.analyze({})
        assert M.MACHINE == k and k in sewcore.ORDER
        for f in ("params", "checks", "ok", "results", "charts", "timing", "parts", "card", "view"):
            assert f in R, (k, f)
        for c in R["charts"]:
            if c["kind"] == "line" and c.get("xr"):
                assert c["xl"]["zh"] and len(c["x"]) == len(c["series"][0]["y"])
