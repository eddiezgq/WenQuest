# -*- coding: utf-8 -*-
"""第 5 轮第 1 步：4 个自写标准件族的规格表核对（出处抽查值、单调性、自洽），以及 WQR-105 标准外购件全部对上库编号。"""
import csv
import importlib.util


import pytest

import wqlib


def rows(eid):
    with open(wqlib.CATALOG / "A" / eid / "specs.csv", encoding="utf-8") as f:
        return {r["size"]: r for r in csv.DictReader(f)}


def test_tables_regenerate_identically(tmp_path, monkeypatch):
    monkeypatch.setenv("WQLIB_SPECS_OUT", str(tmp_path))
    import import_std
    for eid in import_std.ENTRIES:
        header, rs = import_std.rows_of(eid)
        import_bd = importlib.import_module("import_bd")
        import_bd.write(eid, header, rs)
        assert (tmp_path / "A" / eid / "specs.csv").read_text() == (wqlib.CATALOG / "A" / eid / "specs.csv").read_text()


def test_spring_washer_gbt93():
    r = rows("A-WSH-SPR")
    assert len(r) == 23
    assert (r["12"]["d_min_mm"], r["12"]["s_mm"], r["12"]["H_max_mm"]) == ("12.2", "3.1", "7.75")
    assert (r["30"]["d_min_mm"], r["30"]["s_mm"]) == ("30.5", "7.5")
    for x in r.values():                                    # 自由高度 = 2s ~ 2.5s
        s = float(x["s_mm"])
        assert abs(float(x["H_min_mm"]) - 2 * s) < 1e-6 and abs(float(x["H_max_mm"]) - 2.5 * s) < 0.011


def test_taper_pin_gbt117():
    r = rows("A-PIN-TAPER")
    assert r["8x35"]["a_mm"] == "1" and float(r["8x35"]["D_mm"]) == 8.7
    for x in r.values():
        assert abs(float(x["D_mm"]) - (float(x["d_mm"]) + float(x["l_mm"]) / 50)) < 1e-6      # 锥度 1:50


def test_lip_seal_gbt13871():
    r = rows("A-SEL-LIP")
    assert {"20x35x7", "30x47x7", "35x52x8"} <= set(r)
    for x in r.values():
        assert float(x["D_mm"]) > float(x["d1_mm"]) and float(x["b_mm"]) in (7, 8, 10, 12, 15, 20)


def test_hex_plug_din910_self_consistent():
    r = rows("A-PLG-HEX")
    assert r["M16x1.5"]["s_mm"] == "17" and r["M16x1.5"]["d2_mm"] == "21"
    for x in r.values():                                    # 总长 = 螺纹长 + 肩厚 + 头高
        assert float(x["l_mm"]) == float(x["i_mm"]) + float(x["c_mm"]) + float(x["m_mm"]), x["size"]
        assert float(x["d2_mm"]) > float(x["d_mm"])


def test_every_new_entry_names_its_sources():
    for eid in ("A-WSH-SPR", "A-PIN-TAPER", "A-SEL-LIP", "A-PLG-HEX"):
        e = next(x for x in wqlib.entries(eid) if x["id"] == eid)
        ds = e["source"]["data_sources"]
        assert ds and all(d["url"].startswith("http") and d["retrieved"] for d in ds)


FACTORY_DATA = wqlib.ROOT.parent / "factory" / "factory" / "data.py"
STANDARD = ("BRG-", "KEY-", "BOLT-", "NUT-", "WASHER-", "PIN-", "PLUG-", "SEAL-")


@pytest.mark.skipif(not FACTORY_DATA.exists(), reason="没有工厂数据")
def test_wqr105_standard_parts_all_in_library():
    spec = importlib.util.spec_from_file_location("fdata", FACTORY_DATA)
    F = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(F)
    need = {c for c, v in F.ITEMS.items() if v[1] == "buy" and c.startswith(STANDARD)}
    mapped = {}
    for e in wqlib.entries():
        sizes = {str(s["size"]) for s in wqlib.specs(e)}
        for x in (e.get("factory") or {}).get("erp_items") or []:
            assert str(x.get("size", "default")) in sizes, (e["id"], x)
            mapped[x["item_code"]] = "{}/{}".format(e["id"], x.get("size"))
    assert need - set(mapped) == set(), "WQR-105 的标准外购件还没有库编号：{}".format(sorted(need - set(mapped)))
    assert mapped["PLUG-M16"] == "A-PLG-HEX/M16x1.5" and mapped["PIN-8x35"] == "A-PIN-TAPER/8x35"



@pytest.mark.skipif(not FACTORY_DATA.exists(), reason="没有工厂数据")
def test_factory_library_refs_match_catalog():
    """工厂数据里的 LIBRARY_REFS（ERPNext 物料上的零件库编号）与零件库条目的 erp_items 一致"""
    spec = importlib.util.spec_from_file_location("fdata", FACTORY_DATA)
    F = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(F)
    cat = {}
    for e in wqlib.entries():
        for x in (e.get("factory") or {}).get("erp_items") or []:
            cat[x["item_code"]] = "{}/{}".format(e["id"], x.get("size"))
    assert F.LIBRARY_REFS == cat
