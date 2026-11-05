"""Checking a maker's catalogue (round 64, plan section 十七): every rule fires on a row made to break it and stays
quiet on a clean one. The tables here are made up (a fictional "88" series and fictional inch numbers), not a
maker's data."""

import copy
import math

from bearingkit import catalog as K


def series():
    rows = []
    for i in range(10):
        d = 20 + 5 * i
        D = 2 * d + 12
        T = round(0.3 * (D - d) + 4, 2)
        B, C = round(0.92 * T, 2), round(0.78 * T, 2)
        Cr = round(0.9 * ((D - d) * T) ** 0.8, 1)
        mass = round(6.0e-6 * math.pi / 4 * (D**2 - d**2) * T, 3)
        rows.append(
            {
                "table": "metric",
                "page": 1,
                "model": f"880{i:02d}",
                "old": "",
                "d": str(d),
                "D": f"{D:.2f}",
                "T": f"{T:.2f}",
                "B": f"{B:.2f}",
                "C": f"{C:.2f}",
                "R": "1.0",
                "r": "1.0",
                "Cr": str(Cr),
                "Cor": str(round(1.4 * Cr, 1)),
                "n_grease": "5000",
                "n_oil": "7000",
                "da_max": str(d + 6),
                "db_min": str(d + 5),
                "Da_min": str(round(D - 10)),
                "Da_max": str(round(D - 8)),
                "Db_min": str(round(D - 4)),
                "mass": f"{mass:.3f}",
            }
        )
    return rows


def inch():
    def row(cone, cup, d_in, D_in, T_in, B_in, C_in, Cr, Cor):
        mm = lambda x: f"{x * 25.4:.3f}"  # noqa: E731
        return {
            "table": "inch",
            "page": 2,
            "model": cone,
            "cup": cup,
            "d": mm(d_in),
            "D": mm(D_in),
            "T": mm(T_in),
            "B": mm(B_in),
            "C": mm(C_in),
            "R": "1.5",
            "r": "1.5",
            "Cr": str(Cr),
            "Cor": str(Cor),
            "n_grease": "5000",
            "n_oil": "6500",
        }

    out = []
    for k in range(6):
        d = 1.0 + 0.25 * k
        out.append(row(f"X{k}10", f"X{k}20", d, d + 1.5, 0.75, 0.8, 0.6, 40 + 8 * k, 52 + 10 * k))
    out.append(row("X010", "X920", 1.0, 2.75, 0.75, 0.8, 0.6, 50, 64))  # cone X010 again with another cup
    return out


def rules(rows):
    return {(f["rule"], f["model"], f["level"]) for f in K.check(rows)}


def test_a_clean_table_gives_nothing_but_the_standard_line():
    f = K.check(series() + inch())
    assert [x["rule"] for x in f] == ["std"] and f[0]["level"] == K.UNKNOWN


def test_each_rule_fires():
    rows = series() + inch()
    r = {x["model"]: x for x in rows}
    r["88003"]["C"] = "90.00"  # shape: C > T (a typo)
    r["88004"]["n_oil"] = "4000"  # speed: oil below grease
    r["88005"]["Cr"] = "1.5"  # outlier: the rating against the trend, and C0r/Cr
    r["88006"]["D"] = "70.00"  # D not growing with d, and Da max ≥ D
    r["88007"]["Cor"] = r["88007"]["Cr"]  # Cr = C0r
    r["88008"]["mass"] = "9.000"  # mass against volume
    r["88002"]["B"] = "2.10"  # a ring narrower than half of T
    r["X310"]["C"] = "15.241"  # inch: not a whole 0.0001 in (15.240 = 0.6 in)
    r["X410"]["n_oil"] = None
    rows.append(dict(r["88001"]))  # the same row twice: a repeat
    twin = dict(r["88009"])
    twin["Cr"] = "999"
    rows.append(twin)  # the same model with other data
    k = next(x for x in rows if x["model"] == "X010" and x["cup"] == "X920")
    k["B"] = "20.000"  # one cone, two widths
    got = rules(rows)
    for want in [
        ("shape", "88003", "疑似"),
        ("speed", "88004", "疑似"),
        ("outlier", "88005", "疑似"),
        ("outlier", "88006", "疑似"),
        ("shape", "88006", "疑似"),
        ("outlier", "88007", "请确认"),
        ("outlier", "88008", "疑似"),
        ("shape", "88002", "疑似"),
        ("inch", "X310 / X320", "请确认"),
        ("dup", "88009", "疑似"),
        ("dup", "88001", "请确认"),
    ]:
        assert want in got, want
    assert any(x[0] == "part" and x[1].startswith("X010") for x in got)
    # nothing else of the clean rows is touched
    assert not any(m in ("88000",) for _r, m, _l in got)
    # a blank cell is listed, never filled
    r2 = series()
    r2[0]["Da_max"] = None
    f = [x for x in K.check(r2) if x["rule"] == "blank"]
    assert f and f[0]["level"] == "请确认" and "Da max" in f[0]["why"] and r2[0]["Da_max"] is None


def test_inch_values_and_marks():
    assert K.inch_ok("28.575") and K.inch_ok("30.162") and K.inch_ok("30.163") and K.inch_ok("69.85")
    assert not K.inch_ok("28.576") and not K.inch_ok("25.645")
    rows = inch()
    rows[0]["D"] = "62.000"  # a whole millimetre: a metric size, not checked
    rows[1]["R"] = "(Sp*)"
    rows[2]["D"] = "68*"
    got = K.check(rows)
    assert not any(x["rule"] == "inch" for x in got)
    why = " ".join(x["why"] for x in got if x["rule"] == "blank")
    assert "(Sp*)" in why and "68*" in why


def test_nonstandard_series_and_input_untouched():
    rows = series()
    for x in rows:
        x["nonstandard"] = True
    rows[6]["D"] = "70.00"
    before = copy.deepcopy(rows)
    got = K.check(rows)
    assert not any(x["rule"] == "outlier" and "外径" in x["why"] for x in got)
    assert rows == before  # check() only reads


def test_the_workbook_round_trip_and_the_service():
    """The company's workbook (made-up rows here) is read as written, checked, and nothing else is kept."""
    import io

    from fastapi.testclient import TestClient
    from openpyxl import load_workbook

    import app as service

    c = TestClient(service.app)
    r = c.get("/api/catalog/template.xlsx")
    assert r.status_code == 200 and r.content[:2] == b"PK"
    wb = load_workbook(io.BytesIO(r.content))
    assert wb.sheetnames == list(K.SHEETS)
    m, i = wb["公制圆锥"], wb["英制圆锥"]
    head = [x.value for x in m[1]]
    for row in series()[:6]:
        m.append([row.get(K.SHEETS["公制圆锥"][1][h]) for h in head])
    m.append([None] * len(head))  # an empty line is skipped
    ih = [x.value for x in i[1]]
    for row in inch()[:3]:
        i.append([row.get(K.SHEETS["英制圆锥"][1][h]) for h in ih])
    i.append(["2", "X999", "X998", 25.4, "50.800", 15, 15, 12, None, None, None, None, None, None])
    buf = io.BytesIO()
    wb.save(buf)
    got = c.post("/api/catalog/read", content=buf.getvalue())
    assert got.status_code == 200, got.text
    j = got.json()
    rows = j["rows"]
    assert [x["model"] for x in rows if x["table"] == "metric"] == [f"880{k:02d}" for k in range(6)]
    assert len([x for x in rows if x["table"] == "inch"]) == 4
    last = rows[-1]
    assert (
        last["d"] == "25.4"
        and last["D"] == "50.800"
        and last["T"] == "15"
        and "Cr" not in {k for k, v in last.items() if v}
    )
    assert j["opens_as"]["metric"] == "tapered" and any(
        f["rule"] == "blank" and f["model"] == "X999 / X998" for f in j["findings"]
    )
    bad = c.post("/api/catalog/read", content=b"not a workbook")
    assert bad.status_code == 422 and bad.json()["detail"]["zh"].startswith("不是 Excel")
    empty = io.BytesIO()
    from openpyxl import Workbook

    Workbook().save(empty)
    e = c.post("/api/catalog/read", content=empty.getvalue())
    assert e.status_code == 422 and "公制圆锥" in e.json()["detail"]["zh"]


def test_a_design_from_a_catalogue_row():
    """Picking a model (the web panel and the FreeCAD form share fields.from_catalog): outside sizes from the row, a
    tapered bearing's width is T, the inner sizes cleared, the application kept, the row noted; the checks then wait
    for the inner sizes (an error asking for them, never a pass)."""
    import json
    from pathlib import Path

    import pytest

    from bearingkit import fields as FL
    from bearingkit.analyze import ProjectError, analyse

    ex = json.loads((Path(__file__).resolve().parents[1] / "examples" / "scene-tapered.json").read_text("utf-8"))
    cat = {"name": "示范厂目录（虚构）", "version": 3, "rows": series() + inch()}
    assert all(r["table"] in ("metric", "inch") for r in FL.catalog_rows(cat))
    row = series()[3]
    p = FL.from_catalog(ex, cat, row)
    assert p["type"] == "tapered" and p["size"] == {
        "d": 35.0,
        "D": 82.0,
        "B": float(row["T"]),  # overall T; the cone and cup widths too (plan section 二十)
        "Bi": float(row["B"]),
        "Co": float(row["C"]),
    }
    assert p["inner"]["Dw"] is None and p["inner"]["Z"] is None and p["scenario"] == ex["scenario"]
    assert (
        p["catalog"]["model"] == "88003"
        and p["catalog"]["maker"] == "示范厂目录（虚构）"
        and p["catalog"]["version"] == 3
    )
    assert p["title"]["zh"] == "88003" and "厂家目录值" in FL.catalog_note(p) and FL.catalog_note(ex) == ""
    with pytest.raises(ProjectError, match="roller diameter"):
        analyse(p)
    q = FL.from_catalog(ex, cat, inch()[0])
    assert q["catalog"]["cup"] == "X020" and q["title"]["zh"] == "X010 / X020"
    with pytest.raises(ValueError):
        FL.from_catalog(ex, cat, {"table": "double", "model": "T1", "d": "40", "D": "80", "T": "40"})
