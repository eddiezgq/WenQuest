# -*- coding: utf-8 -*-
"""WQ-LS G8.0 第 7 步：SM 螺纹表（JIS B 0226 基本尺寸）和本厂三种螺钉（Q/WQ 001）。"""
import csv

import pytest
import yaml

import wqlib


def rows(eid):
    with open(wqlib.CATALOG / "A" / eid / "specs.csv", encoding="utf-8") as f:
        return {r["size"]: r for r in csv.DictReader(f)}


def test_regenerates_identically(tmp_path, monkeypatch):
    monkeypatch.setenv("WQLIB_SPECS_OUT", str(tmp_path))
    import import_bd
    import import_sm
    for eid in import_sm.FAM:
        header, rs = import_sm.rows_of(eid)
        import_bd.write(eid, header, rs)
        assert (tmp_path / "A" / eid / "specs.csv").read_text() == (wqlib.CATALOG / "A" / eid / "specs.csv").read_text()
    t = yaml.safe_load((wqlib.ROOT / "std_tables" / "thr_sm.yaml").read_text(encoding="utf-8"))
    assert t["rows"] == import_sm.table()


def test_thread_basic_dimensions():
    t = {r["size"]: r for r in yaml.safe_load((wqlib.ROOT / "std_tables" / "thr_sm.yaml").read_text(encoding="utf-8"))["rows"]}
    r = t["SM9/64-40"]                                              # 9/64 in = 3.5719 mm，40 牙/英寸 → P 0.635
    assert r["d_mm"] == pytest.approx(3.5719, abs=1e-4) and r["P_mm"] == pytest.approx(0.635, abs=1e-4)
    assert r["drill_mm"] == 2.95
    assert t["SM1/8-44"]["d_mm"] == pytest.approx(3.175, abs=1e-4) and t["SM1/8-44"]["P_mm"] == pytest.approx(0.5773, abs=1e-4)
    for x in t.values():                                            # 60° 基本牙型
        P = x["P_mm"]
        assert x["d_mm"] - x["d2_mm"] == pytest.approx(0.649519 * P, abs=2e-4)
        assert x["d_mm"] - x["D1_mm"] == pytest.approx(1.082532 * P, abs=2e-4)
        assert x["D1_mm"] < x["drill_mm"] < x["d2_mm"], x["size"]    # 底孔在小径与中径之间
    ds = [x["d_mm"] for x in t.values()]
    assert ds == sorted(ds)


@pytest.mark.parametrize("eid", ["A-SCR-SMP", "A-SCR-SML"])
def test_pan_head_proportions(eid):
    for s, x in rows(eid).items():
        d, L = float(x["d_mm"]), float(x["l_mm"])
        assert float(x["dk_mm"]) > 1.8 * d and float(x["k_mm"]) < d, s
        assert float(x["t_mm"]) < float(x["k_mm"]) and d <= L <= 6 * d, s
        assert s == "{}x{}".format(x["thread"], x["l_mm"])
    if eid == "A-SCR-SML":
        assert {x["thread"] for x in rows(eid).values()} == {"SM9/64-40", "SM11/64-40", "SM15/64-28"}


def test_set_screw():
    for s, x in rows("A-SCR-SMS").items():
        d = float(x["d_mm"])
        assert float(x["dp_mm"]) < d and float(x["s_mm"]) < 0.6 * d and float(x["t_mm"]) < float(x["l_mm"]), s


def test_entries_cite_standard_and_sources():
    for eid in ("A-SCR-SMP", "A-SCR-SMS", "A-SCR-SML"):
        e = next(x for x in wqlib.entries([eid]) if x["id"] == eid)
        codes = [s["code"] for s in e["standards"]]
        assert "Q/WQ 001—2026" in codes and "JIS B 0226" in codes
        assert all(s["url"].startswith("https://") for s in e["source"]["data_sources"])
