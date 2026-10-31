"""第 62 轮：电控箱的热与流体——计算核心逐项对上教材第 18 章（18.3、18.4、18.7 节和虚拟实验 18-1），电流接本机设计，改进方案。"""
import pytest

from app.sewcore import ebox as E

TB = E.clean({"src": "manual"})            # 教材算例：3 A / 9 A、40 °C、每分钟起停 30 次、缝纫一半时间


def th(**kw):
    return E.thermal(TB, E.drives_of("lockstitch", {}, TB), **kw)


def test_losses_and_intermittent_load_18_3():
    """3 A 约 20 W、9 A 约 74 W；平均 18 W，起停只占 15% 的时间却贡献约六成热量；40 °C：箱内 56、散热器 83、结温峰值 110 °C"""
    assert E.stage_loss(TB, 3) == pytest.approx(20, abs=0.5) and E.stage_loss(TB, 9) == pytest.approx(74, abs=0.5)
    r = th()
    assert r["Pavg"] == pytest.approx(18, abs=0.3) and r["facc"] == pytest.approx(0.15) and r["acc_share"] == pytest.approx(0.6, abs=0.03)
    assert (round(r["Tin"]), round(r["Ths"]), round(r["Tjpk"])) == (56, 83, 110)
    assert th(Ta=45)["Tjpk"] == pytest.approx(115, abs=0.5)


def test_switching_time_trade_off_18_4():
    """45 °C：t_sw 300 → 600 ns 共模电流减半、结温 115 → 133；100 ns 结温 104、共模电流 1.9 A；窗口约 235–470 ns；300 pF 时 0.6 A"""
    assert th()["icm"] == pytest.approx(0.6, abs=0.03)
    a, b = th(Ta=45, tsw=600), th(Ta=45, tsw=100)
    assert a["Tjpk"] == pytest.approx(133, abs=1) and a["icm"] == pytest.approx(th()["icm"] / 2)
    assert b["Tjpk"] == pytest.approx(104, abs=0.6) and b["icm"] == pytest.approx(1.9, abs=0.05)
    lo, hi = E.tsw_window(TB, E.drives_of("lockstitch", {}, TB))
    assert lo == pytest.approx(235, abs=5) and hi == pytest.approx(470, abs=3)


def test_lint_and_capacitor_case_18_7():
    """38 °C：干净 81 / 108 °C；堵塞 0.3 散热器 97、0.5 散热器 109 结温 136；电容 59 °C 约 10 年、0.5 → 66 °C 6 年、0.8 → 71 °C 4.4 年"""
    c = th(Ta=38)
    assert (round(c["Ths"]), round(c["Tjpk"])) == (81, 108)
    assert th(Ta=38, clog=0.3)["Ths"] == pytest.approx(97, abs=0.5)
    d = th(Ta=38, clog=0.5)
    assert d["Ths"] == pytest.approx(109, abs=0.6) and d["Tjpk"] == pytest.approx(136, abs=0.5)
    assert c["Tcap"] == pytest.approx(59, abs=0.5) and c["life_y"] == pytest.approx(10, abs=0.5)
    assert th(Ta=38, clog=0.5)["life_y"] == pytest.approx(6, abs=0.2) and th(Ta=38, clog=0.8)["life_y"] == pytest.approx(4.4, abs=0.1)


def test_currents_come_from_this_design():
    # 平缝机教材算例：主轴转矩均方根约 3 N·m，K_t = 1 → 3 A（和教材的 3 A 对上）；6000 r/min 时 4.3 A
    d = E.drives_of("lockstitch", {}, E.clean({}))
    assert d[0]["src"] == "design" and d[0]["Irun"] == pytest.approx(3.0, abs=0.05)
    assert E.drives_of("lockstitch", {"n": 6000}, E.clean({}))[0]["Irun"] == pytest.approx(4.3, abs=0.05)
    assert E.drives_of("lockstitch", {}, E.clean({"Kt": 2.0}))[0]["Irun"] == pytest.approx(1.5, abs=0.05)
    assert [x["key"] for x in E.drives_of("pattern", {}, E.clean({}, "pattern"))] == ["spindle", "x", "y"]
    assert [x["key"] for x in E.drives_of("flatknit", {}, E.clean({}))] == ["carriage"]
    # 默认设计六种机型都不亮红灯（平缝、绷缝：飞絮堵塞 0.3 时黄灯，教材说“余量并不大”）
    for m in ("lockstitch", "overlock", "cover", "pattern", "embroid", "flatknit"):
        R = E.analyze({}, m, {})
        assert R["ok"], m
    assert next(c for c in E.analyze({}, "lockstitch", {})["checks"] if c["key"] == "lint")["state"] == "warn"


def test_enclosure_resistance_from_size():
    """默认外壳 260 × 160 × 90 mm 自然对流 + 辐射约 0.58 K/W（教材给 0.6）；加翅片、风扇都降；本色铝（发射率低）升"""
    P = th()["Ptot"]
    R0 = E.box_resistance(TB, P)["R"]
    assert R0 == pytest.approx(0.6, abs=0.05)
    assert E.box_resistance(dict(TB, fins=10), P)["R"] < R0 * 0.9
    assert E.box_resistance(dict(TB, air="fan", vfan=2), P)["R"] < R0
    assert E.box_resistance(dict(TB, eps=0.1), P)["R"] > R0 * 1.3


def test_summer_overheating_case_and_improvements():
    """案例六：平缝机 6000 r/min、38 °C 车间、飞絮堵塞 0.5 → 散热器报过热、结温超限、电容寿命不够；改进方案里有一行全绿"""
    R = E.analyze({"Ta": 38, "clog": 0.5}, "lockstitch", {"n": 6000})
    bad = {c["key"] for c in R["checks"] if c["state"] == "bad"}
    assert {"ths", "tj", "life"} <= bad and not R["ok"]
    rows = R["variants"]["rows"]
    assert rows[0][6] != "0" and any(r[6] == "0" and r[7] == "0" for r in rows[1:])
    clean_row = next(r for r in rows if "清理" in r[0] and "风扇" not in r[0])
    assert clean_row[6] == "0"                      # 只清理飞絮就没有红灯了


def test_cae_resistance_replaces_the_enclosure_step():
    """CAE 复核算出的箱子热阻代进来：散热器温度跟着变，其余不变"""
    a = E.analyze({}, "lockstitch", {})
    b = E.analyze({}, "lockstitch", {}, Rbox=0.4)
    assert b["thermal"]["Rbox"] == 0.4 and b["thermal"]["Ths"] < a["thermal"]["Ths"]
    assert b["thermal"]["icm"] == a["thermal"]["icm"]
    assert a["box"]["p_ipm"] == pytest.approx(a["thermal"]["Pavg"], abs=0.01) and a["box"]["L"] == 260
