"""第 69 轮：刺绣机第二期——读花样文件（DST、CSV）、按每针调速算产能、主轴转矩、设计优化“达到订单交期”。
公式的数对教材第 16 章（16.3 节转速上限、16.5 节 DST 记录、16.6 节效率）；网关一侧见文件末尾。"""
import base64

import pytest

from app.sewcore import ebox as EB
from app.sewcore import emb_samples as SMP
from app.sewcore import embroid as E
from app.sewcore import optimize as OPT
from app.sewcore import stitchfile as SF
from tests.test_course_pack import client  # noqa: F401
from tests.test_sewing_cae import cae  # noqa: F401

LOGO = base64.b64encode(SMP.logo_dst()).decode()


def dst_of(recs):
    return base64.b64encode(SF.write_dst(recs)).decode()


def test_dst_record_bits_16_5():
    """+1、+1：字节 0 的位 0（Δx +1）和位 7（Δy +1）；字节 2 的位 0、1 总是 1；跳步位 7，换色位 7 + 6，结束 0xF3"""
    assert SF._encode(1, 1) == bytes([0x81, 0x00, 0x03])
    assert SF._decode(bytes([0x81, 0x00, 0x03])) == (1, 1)
    assert SF._decode(SF._encode(121, -121)) == (121, -121) and SF._decode(SF._encode(-40, 67)) == (-40, 67)
    head = SF.write_dst([])[:512]
    rec = bytes([0x81, 0, 0x03]) + bytes([0, 0, 0x83]) + bytes([0, 0, 0xC3]) + bytes([0, 0, 0xF3]) + bytes([0x81, 0, 0x03])
    assert SF.read_dst(head + rec) == [(0.1, 0.1, "s"), (0, 0, "j"), (0, 0, "c")]          # 结束记录之后不读


def test_dst_round_trip_and_long_moves_split():
    recs = [(2.5, 0, "s"), (-2.5, 0.4, "s"), (30.0, -5.0, "j"), (0, 0, "c"), (8.0, 0.35, "s")]
    back = SF.read_dst(SF.write_dst(recs))
    # 30 mm 的跳步拆成 3 条记录（每条单方向不超过 12.1 mm），总位移不变
    assert [k for *_, k in back] == ["s", "s", "j", "j", "j", "c", "s"]
    assert sum(r[0] for r in back) == pytest.approx(sum(r[0] for r in recs))
    st = SF.stats(back)
    assert (st["stitches"], st["jumps"], st["colors"], st["s_max"]) == (3, 3, 1, 8.0)


def test_bad_files_and_csv_flags():
    with pytest.raises(SF.StitchFileError):
        SF.read_dst(b"PK\x03\x04" + b"0" * 600)            # 别的格式（压缩包、家用机格式……）
    with pytest.raises(SF.StitchFileError):
        SF.read_dst(b"LA:x")
    recs = SF.read_csv("x,y,flag\n0,0\n3,0\n6,0,0\n40,0,j\n40,0,c\n43,0\n")
    assert [k for *_, k in recs] == ["s", "s", "j", "c", "s"]
    st = SF.stats(recs)
    assert (st["stitches"], st["jumps"], st["colors"], st["w"]) == (3, 1, 1, 43)
    # 文件坏了：照手填算，红灯说明
    R = E.analyze({"src": "file", "dst": base64.b64encode(b"junk" * 200).decode()})
    bad = [c["key"] for c in R["checks"] if c["state"] == "bad"]
    assert bad == ["file"] and "design" not in R and R["params"]["src"] == "manual"


def test_robustness():
    """推力不大于摩擦力：绷架走不动，红灯，不报错；太大的文件、坏记录：红灯；选手填时不存文件"""
    R = E.analyze({"src": "file", "dst": LOGO, "F": 100, "Ff": 200})
    assert next(c for c in R["checks"] if c["key"] == "accel")["state"] == "bad"
    R = E.analyze({"src": "file", "dst": "A" * (SF.MAX_TEXT + 1)})
    assert [c["key"] for c in R["checks"] if c["state"] == "bad"] == ["file"]
    raw = bytearray(SF.write_dst([(1, 1, "s")] * 5))
    raw[512 + 3 * 2 + 2] = 0x00                                       # 第 3 条记录的标志位坏了
    with pytest.raises(SF.StitchFileError):
        SF.read_dst(bytes(raw))
    assert "dst" not in E.clean({"src": "manual", "dst": LOGO})
    with pytest.raises(SF.StitchFileError):
        SF.read_csv("0,0\n50,0,j\n")                                 # 全是跳步


def test_manual_mode_unchanged():
    """不上传文件时和第 42 轮一样（教材算例）：8 头机 7 mm 缎纹转速上限约 690，默认参数全部合格"""
    R = E.analyze({})
    assert R["ok"] and "design" not in R and R["params"]["src"] == "manual"
    lim = next(r for r in R["results"] if r["zh"] == "最长针的转速上限")
    assert float(lim["value"]) == pytest.approx(690, abs=5)
    assert E.analyze({"src": "file"})["params"]["src"] == "manual"            # 选了文件却没传：退回手填


def test_stitch_by_stitch_speed_16_3():
    """一个花样全是 7 mm 的针：每针都降到 8 头机 7 mm 的上限（约 690）；全是 3 mm：约 1050（教材 16.3 节）"""
    for s, n_lim in ((7.0, 690), (3.0, 1050)):
        recs = [(s if i % 2 else -s, 0.0, "s") for i in range(400)]
        R = E.analyze({"src": "file", "dst": dst_of(recs), "n": 1100})
        PL = E.plan(R["params"] | {"dst": dst_of(recs)})
        assert sum(PL["sp"]) / len(PL["sp"]) == pytest.approx(n_lim, abs=10)
    # 有文件时，只有长针的那一段降速：比整个花样都按最长针一个转速算要快
    p = {"src": "file", "dst": LOGO, "H": 12}
    R = E.analyze(p)
    d = R["design"]
    assert d["stitches"] > 9000 and d["colors"] == 5 and d["s_max"] == pytest.approx(8.0)
    one = E.analyze({"H": 12, "N": d["stitches"], "s": 8, "colors": 5})
    assert R["production"]["t_sew"] < 0.9 * one["production"]["t_sew"]
    assert not any(c["state"] == "bad" for c in R["checks"])            # 手填时 12 头 650 r/min 是红灯；有文件时长针自动降速
    assert any(c["state"] == "bad" for c in one["checks"])
    kinds = [c["kind"] for c in R["charts"]]
    assert kinds[:2] == ["line", "stitch"] and R["tables"][0]["key"] == "bins_table"


def test_frame_travel_and_csv_over_record_limit():
    recs = [(5.0, 0, "s")] * 100                                   # 500 mm 宽
    R = E.analyze({"src": "file", "dst": dst_of(recs)})
    assert next(c for c in R["checks"] if c["key"] == "travel")["state"] == "bad"
    R = E.analyze({"src": "file", "pts": "0,0\n15,0\n15,3\n"})       # 15 mm 的一针超过 DST 一条记录
    assert next(c for c in R["checks"] if c["key"] == "dst")["state"] == "bad"


def test_spindle_and_servo_follow_the_design():
    """主轴（示例模型）：0.5 + 0.3 × 头数；电控箱里主轴电流跟着变（K_t = 1）。有文件时绷架伺服的有效转矩按每针加权，比最坏情况小"""
    assert E.spindle(E.clean({}))["Trun"] == pytest.approx(2.9)
    assert E.spindle(E.clean({"H": 12}))["Trun"] == pytest.approx(4.1)
    d = EB.drives_of("embroid", {"H": 12}, EB.clean({}, "embroid"))
    assert d[0]["src"] == "design" and d[0]["Irun"] == pytest.approx(4.1)
    assert EB.drives_of("embroid", {"H": 12}, EB.clean({"src": "manual"}, "embroid"))[0]["Irun"] == 3.0
    a = E.servo(E.clean({"H": 12, "s": 8, "n": 545}))
    b = E.servo(E.clean({"H": 12, "src": "file", "dst": LOGO}))
    assert b["Tpk"] == pytest.approx(a["Tpk"], rel=0.02) and b["Trms"] < 0.6 * a["Trms"]
    assert EB.analyze({}, "embroid", {"H": 12, "src": "file", "dst": LOGO})["ok"]


def test_optimize_order_delivery():
    """达到订单交期：头数从少到多；每个头数下至少要的推力（再少 10 N 就赶不上），现有推力够就不动；都不出红灯、都赶上交期"""
    p = {"src": "file", "dst": LOGO, "Q": 20000, "days": 45}
    r = OPT.run("embroid", p, "order")
    cs = r["candidates"]
    H0 = cs[0]["value"]
    assert [c["value"] for c in cs] == [H0, H0 + 1, H0 + 2]
    for c in cs:
        Fm = c["note"]["F_min"]
        assert c["bad"] == 0 and c["note"]["days"] <= 45 and c["params"]["n"] == 650 and c["params"]["F"] == max(800, Fm)
        assert E.run_production(E.clean(p | c["params"]), F=Fm)[0]["days"] <= 45
        assert E.run_production(E.clean(p | c["params"]), F=Fm - 10)[0]["days"] > 45
    assert E.run_production(E.clean(p | {"H": H0 - 1, "F": 5000}))[0]["days"] > 45      # 少一个头，推力到上限也赶不上
    assert OPT.run("embroid", {}, "order")["candidates"] == [] and "交期" in OPT.run("embroid", {}, "order")["why"]["zh"]
    R = E.analyze(p | {"H": 8})
    assert next(c for c in R["checks"] if c["key"] == "order")["state"] == "bad"


def test_gateway_sample_analyze_export(cae):  # noqa: F811
    c, h, _ = cae
    s = c.get("/api/v1/sewing/embroid/sample").json()
    assert s["name"].endswith(".dst") and base64.b64decode(s["dst"])[:3] == b"LA:"
    r = c.post("/api/v1/sewing/analyze", json={"machine": "embroid", "params": {"src": "file", "dst": s["dst"], "fname": s["name"], "H": 12}}).json()
    assert r["design"]["fname"] == "wq-logo.dst" and "dst" not in r["params"]          # 回给网页的结果里不带文件本身
    keys = {p["key"] for g in c.get("/api/v1/sewing/schema?machine=embroid").json()["groups"] for p in g["params"]}
    assert {"src", "dn", "stx", "Q", "days", "T0", "Th"} <= keys
    j = c.post("/api/v1/sewing/export/json", json={"machine": "embroid", "params": {"src": "file", "dst": s["dst"]}}, headers=h).json()
    assert j["params"]["dst"] == s["dst"]                                                # 参数文件带上花样，FreeCAD 导入能接着算
    for kind in ("report", "params"):
        assert c.post(f"/api/v1/sewing/export/{kind}", json={"machine": "embroid", "params": {"src": "file", "dst": s["dst"]}}, headers=h).status_code == 200
    o = c.post("/api/v1/sewing/optimize", json={"machine": "embroid", "goal": "order",
                                               "params": {"src": "file", "dst": s["dst"], "Q": 20000, "days": 45}}, headers=h).json()
    assert o["candidates"] and o["candidates"][0]["bad"] == 0
