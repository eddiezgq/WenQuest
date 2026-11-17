# -*- coding: utf-8 -*-
"""WQ-LS G8.0 第 7 步：缝纫机螺纹（SM，JIS B 0226）和本厂三种螺钉（Q/WQ 001—2026）。

螺纹只按定义算基本尺寸，不编公差：
- 大径 d = 英寸数 × 25.4，螺距 P = 25.4 / 每英寸牙数，牙型角 60°（JIS B 0226）；
- 基本中径 d2 = d − 0.649519 P，基本小径 D1 = d − 1.082532 P（60° 基本牙型，与 ISO 68-1、ASME B1.1 相同）；
- 攻丝底孔按 75% 牙高的通用公式 d − 0.974 P（Machinery's Handbook），取到 0.05 mm；
- 公差在 JIS B 0226 正文核对之前不列，螺纹按 SM 2 级螺纹量规（通 / 止）验收（OSG 有售，SM 3/32-56 ～ 1/4-40）。
螺钉头部是本厂规定（比例参照 ISO 1580 盘头、ISO 4026 平端紧定），写在 Q/WQ 001。

用法：python3 tools/import_sm.py     → std_tables/thr_sm.yaml 和 A-SCR-SMP / A-SCR-SMS / A-SCR-SML 三个条目
核对：tests/test_sm.py
"""
import math
import sys
from fractions import Fraction
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from import_bd import mm, write  # noqa: E402
from wqlib import CATALOG, ROOT  # noqa: E402

ON = "2026-11-16"
STD = {"code": "Q/WQ 001—2026", "title": "缝纫机螺纹与螺钉（问渠企业标准；螺纹按 JIS B 0226）"}
JIS = {"code": "JIS B 0226", "title": "ミシン用ねじ（缝纫机螺纹）"}

# (公称英寸, 每英寸牙数)。3/32-56 ～ 1/4-40 是 OSG 螺纹量规覆盖的范围；其余是 JUKI DDL-8700 零件表里用到的
THREADS = [("3/32", 56), ("1/8", 44), ("9/64", 40), ("5/32", 32), ("11/64", 40), ("15/64", 28), ("1/4", 40)]
LENGTHS = [3, 4, 5, 6, 8, 10, 12, 16, 20]
SOCKET = {"3/32": 0.9, "1/8": 1.5, "9/64": 1.5, "5/32": 2.0, "11/64": 2.0, "15/64": 3.0, "1/4": 3.0}   # 紧定螺钉内六角对边（ISO 4026 同径档）
LEFT = ["9/64", "11/64", "15/64"]                                                                     # 左旋只收这三档


def r05(x):
    return round(round(x / 0.05) * 0.05, 2)


def r01(x):
    return round(x, 1)


def thread(inch, tpi):
    d = float(Fraction(inch)) * 25.4
    P = 25.4 / tpi
    return {"size": "SM{}-{}".format(inch, tpi), "inch": inch, "tpi": tpi, "d_mm": round(d, 4), "P_mm": round(P, 4),
            "d2_mm": round(d - 0.649519 * P, 4), "D1_mm": round(d - 1.082532 * P, 4),
            "H1_mm": round(0.541266 * P, 4), "drill_mm": r05(d - 0.974 * P)}


def table():
    return [thread(i, n) for i, n in THREADS]


def pan(t, L):
    d = t["d_mm"]
    k = r01(0.6 * d)
    return {"thread": t["size"], "d_mm": t["d_mm"], "P_mm": t["P_mm"], "l_mm": L, "dk_mm": r01(1.9 * d), "k_mm": k,
            "n_mm": r05(0.2 * d), "t_mm": r05(0.5 * k), "b_mm": L, "drill_mm": t["drill_mm"]}


def setscrew(t, L):
    d = t["d_mm"]
    return {"thread": t["size"], "d_mm": t["d_mm"], "P_mm": t["P_mm"], "l_mm": L, "dp_mm": r01(0.65 * d),
            "s_mm": SOCKET[t["inch"]], "t_mm": r05(min(0.5 * d, 0.6 * L)), "drill_mm": t["drill_mm"]}


def P_(key, zh, en, role, unit=None):
    return {"key": key, "zh": zh, "en": en, "role": role, **({"unit": unit} if unit else {})}


COMMON = [P_("thread", "螺纹规格", "Thread", "key"), P_("l_mm", "公称长度", "Nominal length", "key", "mm"),
          P_("d_mm", "螺纹大径", "Major diameter", "dim", "mm"), P_("P_mm", "螺距", "Pitch", "dim", "mm")]
FAM = {
    "A-SCR-SMP": {"zh": "缝纫机盘头一字螺钉（SM 螺纹）", "en": "Slotted pan head screw, sewing-machine thread (SM)",
                  "params": COMMON + [P_("dk_mm", "头部直径", "Head diameter", "dim", "mm"), P_("k_mm", "头高", "Head height", "dim", "mm"),
                                      P_("n_mm", "槽宽", "Slot width", "dim", "mm"), P_("t_mm", "槽深", "Slot depth", "dim", "mm"),
                                      P_("b_mm", "螺纹长度（全螺纹）", "Thread length (full)", "dim", "mm"),
                                      P_("drill_mm", "攻丝底孔", "Tap drill", "info", "mm")],
                  "row": pan, "threads": [x[0] for x in THREADS], "default": "SM9/64-40x8", "engine": "wenquest:sm_pan",
                  "lh": False},
    "A-SCR-SMS": {"zh": "缝纫机内六角平端紧定螺钉（SM 螺纹）", "en": "Hexagon socket set screw, flat point, sewing-machine thread (SM)",
                  "params": COMMON + [P_("dp_mm", "平端直径", "Point diameter", "dim", "mm"), P_("s_mm", "内六角对边", "Socket size", "dim", "mm"),
                                      P_("t_mm", "内六角深", "Socket depth", "dim", "mm"), P_("drill_mm", "攻丝底孔", "Tap drill", "info", "mm")],
                  "row": setscrew, "threads": [x[0] for x in THREADS], "default": "SM11/64-40x5", "engine": "wenquest:sm_set",
                  "lh": False},
    "A-SCR-SML": {"zh": "缝纫机盘头一字螺钉，左旋（SM 螺纹）", "en": "Slotted pan head screw, left-hand, sewing-machine thread (SM)",
                  "params": None, "row": pan, "threads": LEFT, "default": "SM9/64-40x6", "engine": "wenquest:sm_pan", "lh": True},
}
FAM["A-SCR-SML"]["params"] = FAM["A-SCR-SMP"]["params"]


def rows_of(eid):
    f = FAM[eid]
    keys = [p["key"] for p in f["params"]]
    out = []
    for t in table():
        if t["inch"] not in f["threads"]:
            continue
        lo, hi = (1.0 if eid != "A-SCR-SMS" else 0.8) * t["d_mm"], 6 * t["d_mm"]
        for L in LENGTHS:
            if lo <= L <= hi and (eid != "A-SCR-SML" or 4 <= L <= 12):
                r = f["row"](t, L)
                out.append(["{}x{}".format(t["size"], L)] + [mm(r[k]) if isinstance(r[k], (int, float)) else r[k] for k in keys])
    return ["size"] + keys, out


def entry(eid):
    f = FAM[eid]
    lh = "左旋" if f["lh"] else ""
    return {
        "schema": 1, "id": eid, "kind": "family", "name": {"zh": f["zh"], "en": f["en"]}, "category": "SCR",
        "tags": ["螺钉", "缝纫机螺钉", "SM 螺纹", "英制细牙", "sewing machine screw", "SM thread"] + (["左旋", "left-hand"] if f["lh"] else []),
        "standards": [STD, JIS], "params": f["params"], "specs": "specs.csv", "default": f["default"],
        "model": {"engine": f["engine"], "formats": ["step", "stl", "glb"],
                  "origin": "螺钉末端在 z=0，轴线沿 Z，头部朝 +Z（紧定螺钉内六角朝 +Z）；不画螺纹" + ("；左旋只在标记里体现" if f["lh"] else "")},
        "source": {"origin": "wenquest", "license": "Apache-2.0",
                   "attribution": "问渠零件库；螺纹基本尺寸按 JIS B 0226 的定义计算，头部尺寸为问渠企业标准 Q/WQ 001",
                   "checked": {"by": "Claude", "on": ON, "note": "螺纹按定义计算（大径、螺距、60° 基本牙型）；测试核对公式与单调性。公差未列，按 SM 2 级螺纹量规验收"},
                   "data_sources": [
                       {"title": "improwis 螺纹表：Japanese and Korean threads for sewing machines（SM，60°，JIS B 0226 / KS B 0225）",
                        "url": "https://www.improwis.com/tables/threads2.webt", "retrieved": ON},
                       {"title": "OSG 螺纹量规样本：ミシン（SM）ねじ 2 级，SM3/32-56 ～ SM1/4-40",
                        "url": "https://osg.co.jp/media_dl/flier/file/p_9.pdf", "retrieved": ON},
                       {"title": "JUKI DDL-8700 零件表（各规格的用法）",
                        "url": "https://www.juki.co.jp/industrial_j/download_j/manual_j/ddl8700/menu/ddl8700/pdf/partslist.pdf", "retrieved": ON}],
                   "notes": "SM 螺纹是日本缝纫机行业的英制细牙螺纹（名义尺寸用英寸分数，牙数比 UNC/UNF 更细），国内外缝纫机零件普遍沿用。"
                            "公差待买到 JIS B 0226 正文后补进规格表。"},
        "teaching": {"principle": lh + "SM 螺纹牙型与公制、统一螺纹同为 60°，但直径按英寸分数、牙更细，小直径下牙数多、自锁好，适合缝纫机这类高速振动、零件小的机构。"
                     + ("左旋螺钉用在转动件上：选成转动和振动时越拧越紧的旋向。" if f["lh"] else ""),
                     "uses": ["WQ-LS 平缝机：紧针螺钉、针杆连接块、针杆导轨、线钩、曲柄销"],
                     "courses": [{"course": "机械设计基础", "chapter": "螺纹连接"}], "labs": []},
        "factory": {"erp_items": [], "suppliers": []},
    }


def main():
    tdoc = {"standard": JIS, "note": "基本尺寸按定义计算（见 tools/import_sm.py 开头）；公差未列，按 SM 2 级螺纹量规验收",
            "columns": [["d_mm", "大径", "major diameter", "mm"], ["P_mm", "螺距", "pitch", "mm"], ["d2_mm", "基本中径", "basic pitch diameter", "mm"],
                        ["D1_mm", "基本小径（内螺纹）", "basic minor diameter", "mm"], ["H1_mm", "基本牙高", "basic thread depth", "mm"],
                        ["drill_mm", "攻丝底孔（75% 牙高）", "tap drill (75 % thread)", "mm"]],
            "rows": table()}
    (ROOT / "std_tables" / "thr_sm.yaml").write_text("# 缝纫机螺纹 SM（JIS B 0226）基本尺寸——由 tools/import_sm.py 生成，勿手改\n"
                                                     + yaml.safe_dump(tdoc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for eid in FAM:
        header, rs = rows_of(eid)
        write(eid, header, rs)
        (CATALOG / "A" / eid / "entry.yaml").write_text("# {} · {}（WQ-LS G8.0 第 7 步）\n".format(eid, FAM[eid]["zh"])
                                                        + yaml.safe_dump(entry(eid), allow_unicode=True, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main()
