# -*- coding: utf-8 -*-
"""从 bd_warehouse 自带的标准数据生成第一期标准件族的规格表（specs.csv）。

规格表进仓库（L5）；这个脚本保证它们能从 bd_warehouse 的数据重新生成、逐行核对（tests/test_specs.py）。
用法：python3 tools/import_bd.py            # 重写 catalog/A/*/specs.csv（只写 bd 数据的那几族）
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wqlib import CATALOG  # noqa: E402

# 第一期的尺寸范围（常用段；bd_warehouse 的表更大，需要时放宽即可）
BOLT_SIZES = ["M5-0.8", "M6-1", "M8-1.25", "M10-1.5", "M12-1.75", "M14-2", "M16-2", "M20-2.5", "M24-3"]
SHCS_SIZES = ["M3-0.5", "M4-0.7", "M5-0.8", "M6-1", "M8-1.25", "M10-1.5", "M12-1.75", "M16-2", "M20-2.5"]
NUT_SIZES = ["M3-0.5", "M4-0.7", "M5-0.8", "M6-1", "M8-1.25", "M10-1.5", "M12-1.75", "M14-2", "M16-2", "M20-2.5",
             "M24-3", "M30-3.5", "M36-4"]
WASHER_SIZES = ["M3", "M4", "M5", "M6", "M8", "M10", "M12", "M14", "M16", "M20", "M24", "M30", "M36"]
RING_SIZES = [str(d) for d in (8, 10, 12, 14, 15, 16, 17, 18, 20, 22, 24, 25, 28, 30, 32, 35, 40, 45, 50, 55, 60)]
# GB/T 1096 普通平键的长度系列与各规格的长度范围（b×h：L 最小、最大）
KEY_L_SERIES = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56, 63, 70, 80, 90, 100, 110, 125, 140,
                160, 180, 200]
KEY_L_RANGE = {(2, 2): (6, 20), (3, 3): (6, 36), (4, 4): (8, 45), (5, 5): (10, 56), (6, 6): (14, 70),
               (8, 7): (18, 90), (10, 8): (22, 110), (12, 8): (28, 140), (14, 9): (36, 160)}


def mm(x):
    x = float(x)
    return int(x) if x == int(x) else round(x, 4)


def write(entry_id, header, rows):
    import os
    base = Path(os.environ.get("WQLIB_SPECS_OUT") or CATALOG)       # 测试时写到临时目录再比对
    d = base / entry_id.split("-")[0] / entry_id
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "specs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print("{}: {} 个规格".format(entry_id, len(rows)))


def thread(size):
    d, p = size[1:].split("-")
    return mm(d), mm(p)


def bolts():
    from bd_warehouse.fastener import HexHeadScrew
    rows = []
    for size in BOLT_SIZES:
        probe = HexHeadScrew(size, 50, "iso4014", simple=True)
        d, p = thread(size)
        for L in probe.nominal_lengths:
            k, s = probe.screw_data["k"], probe.screw_data["s"]
            rows.append(["M{}x{}".format(d, mm(L)), d, p, mm(L), mm(k), mm(s)])
    write("A-BLT-HEX", ["size", "d_mm", "P_mm", "l_mm", "k_mm", "s_mm"], rows)


def socket_screws():
    from bd_warehouse.fastener import SocketHeadCapScrew
    rows = []
    for size in SHCS_SIZES:
        probe = SocketHeadCapScrew(size, 20, "iso4762", simple=True)
        d, p = thread(size)
        sd = probe.screw_data
        for L in probe.nominal_lengths:
            rows.append(["M{}x{}".format(d, mm(L)), d, p, mm(L), mm(sd["dk"]), mm(sd["k"]), mm(sd["s"]), mm(sd["t"])])
    write("A-SCR-SHC", ["size", "d_mm", "P_mm", "l_mm", "dk_mm", "k_mm", "s_mm", "t_mm"], rows)


def nuts():
    from bd_warehouse.fastener import HexNut
    rows = []
    for size in NUT_SIZES:
        n = HexNut(size, "iso4032", simple=True)
        d, p = thread(size)
        rows.append(["M{}".format(d), d, p, mm(n.nut_data["m"]), mm(n.nut_data["s"])])
    write("A-NUT-HEX", ["size", "d_mm", "P_mm", "m_mm", "s_mm"], rows)


def washers():
    from bd_warehouse.fastener import PlainWasher
    rows = []
    for size in WASHER_SIZES:
        w = PlainWasher(size, "iso7089")
        dd = w.washer_data
        rows.append([size, mm(size[1:]), mm(dd["d1"]), mm(dd["d2"]), mm(dd["h"])])
    write("A-WSH-PLN", ["size", "d_mm", "d1_mm", "d2_mm", "h_mm"], rows)


def keys():
    from bd_warehouse.shaft_key import ShaftKey
    by_bh = {}
    for shaft in ShaftKey.sizes():
        p = ShaftKey.parameters(shaft) if hasattr(ShaftKey, "parameters") else ShaftKey.key_data[shaft]
        b, h = mm(p["b"]), mm(p["h"])
        rec = by_bh.setdefault((b, h), {"lo": shaft, "hi": shaft, "t1": mm(p["t4"]), "t2": mm(p["t2"])})  # DIN 6885: t4 轴槽深, t2 轮毂槽深
        rec["lo"], rec["hi"] = min(rec["lo"], shaft), max(rec["hi"], shaft)
    # 适用轴径按 GB/T 1095 的写法“大于 shaft_min 至 shaft_max”：上限 = 本规格最大轴径，下限 = 上一规格的上限
    #（第一个规格的下限就是它自己的起点，即“自 6 至 8”）
    order = sorted(by_bh, key=lambda bh: by_bh[bh]["lo"])
    for i, bh in enumerate(order):
        by_bh[bh]["min"] = by_bh[order[i - 1]]["hi"] if i else by_bh[bh]["lo"]
    rows = []
    for (b, h), r in sorted(by_bh.items()):
        lo, hi = KEY_L_RANGE[(b, h)]
        for L in KEY_L_SERIES:
            if lo <= L <= hi:
                rows.append(["{}x{}x{}".format(b, h, L), b, h, L, r["min"], r["hi"], r["t1"], r["t2"]])
    write("A-KEY-FLAT", ["size", "b_mm", "h_mm", "l_mm", "shaft_min_mm", "shaft_max_mm", "t1_mm", "t2_mm"], rows)


def rings():
    from bd_warehouse.retaining_ring import ExternalSnapRing
    rows = []
    for size in RING_SIZES:
        p = ExternalSnapRing.parameters(size)
        rows.append([size, mm(size), mm(p["s"]), mm(p["d3"]), mm(p["d2"]), mm(p["a"]), mm(p["m"])])
    write("A-RNG-SHAFT", ["size", "d1_mm", "s_mm", "d3_mm", "d2_mm", "a_mm", "m_mm"], rows)


def orings():
    import csv as _c
    import bd_warehouse
    f = Path(bd_warehouse.__file__).parent / "data" / "o-ring_parameters.csv"
    rows = []
    for r in _c.DictReader(open(f, encoding="utf-8")):
        idd, w = float(r["iso3601:id"]), float(r["iso3601:w"])
        if 2 <= idd <= 120:
            rows.append([r["Size"], mm(idd), mm(w), mm(idd + 2 * w)])
    write("A-SEL-ORING", ["size", "id_mm", "w_mm", "od_mm"], rows)


def bd_bearings(entry_id, cls, extra):
    rows = []
    for size in cls.sizes("SKT"):
        try:
            b = cls(size)          # bd_warehouse 自己造不出来的规格（少数圆锥滚子轴承）不收
        except Exception as ex:  # noqa: BLE001
            print("  {} {}：bd_warehouse 造型失败，不收（{}）".format(entry_id, size, str(ex)[:60]))
            continue
        dd = b.bearing_dict
        width = dd.get("T", dd.get("B"))
        desig = str(cls.bearing_data[size].get("SKT:Designation", "")).replace("*", "").strip()
        # 圆锥滚子轴承的数据里 C 是外圈宽度，额定载荷在 Cl、Cl0
        cr, c0 = ("Cl", "Cl0") if "T" in dd else ("C", "C0")
        rows.append([desig.replace(" ", "") or size, mm(dd["d"]), mm(dd["D"]), mm(width),
                     mm(dd[cr]) if cr in dd else "", mm(dd[c0]) if c0 in dd else "", size] + extra)
    write(entry_id, ["size", "d_mm", "D_mm", "B_mm", "Cr_kN", "C0r_kN", "bd_size"], rows)


# GB/T 276-2013 深沟球轴承外形尺寸（60、62、63 系列，内径 10–50 mm）：代号、d、D、B、r_min
GB276 = """6000 10 26 8 0.3|6001 12 28 8 0.3|6002 15 32 9 0.3|6003 17 35 10 0.3|6004 20 42 12 0.6|6005 25 47 12 0.6|
6006 30 55 13 1|6007 35 62 14 1|6008 40 68 15 1|6009 45 75 16 1|6010 50 80 16 1|
6200 10 30 9 0.6|6201 12 32 10 0.6|6202 15 35 11 0.6|6203 17 40 12 0.6|6204 20 47 14 1|6205 25 52 15 1|
6206 30 62 16 1|6207 35 72 17 1.1|6208 40 80 18 1.1|6209 45 85 19 1.1|6210 50 90 20 1.1|
6300 10 35 11 0.6|6301 12 37 12 1|6302 15 42 13 1|6303 17 47 14 1|6304 20 52 15 1.1|6305 25 62 17 1.1|
6306 30 72 19 1.1|6307 35 80 21 1.5|6308 40 90 23 1.5|6309 45 100 25 1.5|6310 50 110 27 2"""


def deep_groove():
    """GB/T 276 的 60/62/63 系列（外形尺寸按标准）+ bd_warehouse 的微型轴承（内径 < 10 mm，SKF 数据）。"""
    from bd_warehouse.bearing import SingleRowDeepGrooveBallBearing as DG
    rows = []
    for rec in GB276.replace("\n", "").split("|"):
        c, d, D, B, r = rec.split()
        rows.append([c, mm(d), mm(D), mm(B), mm(r), "", "", "GB/T 276"])
    for size in DG.sizes("SKT"):
        dd = DG(size).bearing_dict
        if dd["d"] >= 10:
            continue
        desig = str(DG.bearing_data[size].get("SKT:Designation", "")).replace("*", "").strip()
        rows.append([desig.replace(" ", ""), mm(dd["d"]), mm(dd["D"]), mm(dd["B"]), mm(dd["r12"]),
                     mm(dd["C"]), mm(dd["C0"]), "bd_warehouse（SKF）"])
    write("A-BRG-DG", ["size", "d_mm", "D_mm", "B_mm", "r_min_mm", "Cr_kN", "C0r_kN", "data_source"], rows)


if __name__ == "__main__":
    deep_groove()
    from bd_warehouse.bearing import (SingleRowAngularContactBallBearing, SingleRowCylindricalRollerBearing,
                                      SingleRowTaperedRollerBearing)
    bolts(); socket_screws(); nuts(); washers(); keys(); rings(); orings()
    bd_bearings("A-BRG-AC", SingleRowAngularContactBallBearing, [])
    bd_bearings("A-BRG-CR", SingleRowCylindricalRollerBearing, [])
    bd_bearings("A-BRG-TR", SingleRowTaperedRollerBearing, [])
