# -*- coding: utf-8 -*-
"""第 5 轮第 1 步：WQR-105 还缺的 4 个标准件族（P7），尺寸表按公开资料录入，逐族注明出处（P6）。

用法：python3 tools/import_std.py      # 重写这 4 族的 entry.yaml 与 specs.csv
尺寸表的核对：tests/test_std_tables.py（行数、单调性、与出处一致的抽查值、螺塞长度 = 螺纹长 + 肩厚 + 头高）。
"""
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from import_bd import mm, write  # noqa: E402
from wqlib import CATALOG  # noqa: E402

RETRIEVED = "2026-09-30"
CHECKED = {"by": "Claude", "on": RETRIEVED, "note": "尺寸按下列出处录入；测试逐行核对单调性与抽查值"}
LICENSE = "Apache-2.0"
ATTR = "问渠零件库（造型程序与规格表）；尺寸取自所列标准的公开尺寸表"

# ---------------------------------------------------------------- GB/T 93-1987 标准型弹簧垫圈
# 规格 d, d_min, d_max, s(b) 公称, H_min, H_max, m≤
SPRING_WASHER = [
    (2, 2.1, 2.35, 0.5, 1, 1.25, 0.25), (2.5, 2.6, 2.85, 0.65, 1.3, 1.63, 0.33), (3, 3.1, 3.4, 0.8, 1.6, 2, 0.4),
    (4, 4.1, 4.4, 1.1, 2.2, 2.75, 0.55), (5, 5.1, 5.4, 1.3, 2.6, 3.25, 0.65), (6, 6.1, 6.68, 1.6, 3.2, 4, 0.8),
    (8, 8.1, 8.68, 2.1, 4.2, 5.25, 1.05), (10, 10.2, 10.9, 2.6, 5.2, 6.5, 1.3), (12, 12.2, 12.9, 3.1, 6.2, 7.75, 1.55),
    (14, 14.2, 14.9, 3.6, 7.2, 9, 1.8), (16, 16.2, 16.9, 4.1, 8.2, 10.25, 2.05), (18, 18.2, 19.04, 4.5, 9, 11.25, 2.25),
    (20, 20.2, 21.04, 5, 10, 12.5, 2.5), (22, 22.5, 23.34, 5.5, 11, 13.75, 2.75), (24, 24.5, 25.5, 6, 12, 15, 3),
    (27, 27.5, 28.5, 6.8, 13.6, 17, 3.4), (30, 30.5, 31.5, 7.5, 15, 18.75, 3.75), (33, 33.5, 34.7, 8.5, 17, 21.25, 4.25),
    (36, 36.5, 37.7, 9, 18, 22.5, 4.5), (39, 39.5, 40.7, 10, 20, 25, 5), (42, 42.5, 43.7, 10.5, 21, 26.25, 5.25),
    (45, 45.5, 46.7, 11, 22, 27.5, 5.5), (48, 48.5, 49.7, 12, 24, 30, 6)]

# ---------------------------------------------------------------- GB/T 117-2000 圆锥销（A 型，= ISO 2339）
PIN_A = {1: 0.12, 1.5: 0.2, 2: 0.25, 2.5: 0.3, 3: 0.4, 4: 0.5, 5: 0.63, 6: 0.8, 8: 1, 10: 1.2, 12: 1.6, 16: 2}
PIN_L_RANGE = {1: (8, 16), 1.5: (10, 20), 2: (12, 30), 2.5: (12, 40), 3: (14, 50), 4: (16, 60), 5: (20, 70),
               6: (30, 100), 8: (30, 120), 10: (40, 140), 12: (40, 140), 16: (40, 140)}
PIN_L_SERIES = [4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85,
                90, 95, 100, 120, 140, 160, 180, 200]

# ---------------------------------------------------------------- GB/T 13871.1 旋转轴唇形密封圈（d1×D×b）
LIP_SEAL = [
    (6, 16, 7), (6, 22, 7), (7, 22, 7), (8, 22, 7), (8, 24, 7), (9, 22, 7), (10, 22, 7), (10, 25, 7), (12, 24, 7),
    (12, 25, 7), (12, 30, 7), (15, 26, 7), (15, 30, 7), (15, 35, 7), (16, 30, 7), (16, 35, 7), (18, 30, 7), (18, 35, 7),
    (20, 35, 7), (20, 40, 7), (20, 45, 7), (22, 35, 7), (22, 40, 7), (22, 47, 7), (25, 40, 7), (25, 47, 7), (25, 52, 7),
    (28, 40, 7), (28, 47, 7), (28, 52, 7), (30, 42, 7), (30, 47, 7), (30, 50, 7), (30, 52, 7), (32, 45, 8), (32, 47, 8),
    (32, 52, 8), (35, 50, 8), (35, 52, 8), (35, 55, 8), (38, 55, 8), (38, 58, 8), (38, 62, 8), (40, 55, 8), (40, 60, 8),
    (40, 62, 8), (42, 55, 8), (42, 62, 8), (45, 62, 8), (45, 65, 8), (50, 68, 8), (50, 70, 8), (50, 72, 8), (55, 72, 8),
    (55, 75, 8), (55, 80, 8), (60, 80, 8), (60, 85, 8), (65, 85, 10), (65, 90, 10), (70, 90, 10), (70, 95, 10),
    (75, 95, 10), (75, 100, 10), (80, 100, 10), (80, 110, 10), (85, 110, 12), (85, 120, 12), (90, 115, 12),
    (90, 120, 12), (95, 120, 12), (100, 125, 12), (105, 130, 12), (110, 140, 12), (120, 150, 12), (130, 160, 12),
    (140, 170, 15), (150, 180, 15), (160, 190, 15), (170, 200, 15), (180, 210, 15), (190, 220, 15), (200, 230, 15),
    (220, 250, 15), (240, 270, 15), (250, 290, 15), (260, 300, 20), (280, 320, 20), (300, 340, 20), (320, 360, 20),
    (340, 380, 20), (360, 400, 20), (380, 420, 20), (400, 440, 20)]

# ---------------------------------------------------------------- DIN 910 外六角带肩螺塞（重型，圆柱螺纹）
# d×P, 肩径 d2, 总长 l, 肩厚 c, 螺纹长 i, 头高 m, 对边 s, 千件重 kg
# M26×1.5（l 30 ≠ i+c+m 28）与 M36×1.5（33 ≠ 32）两行出处数值自相矛盾，暂不收
HEX_PLUG = [
    ("M10x1", 10, 1, 14, 17, 3, 8, 6, 10, 12), ("M12x1.5", 12, 1.5, 17, 21, 3, 12, 6, 13, 20.3),
    ("M14x1.5", 14, 1.5, 19, 21, 3, 12, 6, 13, 25), ("M16x1.5", 16, 1.5, 21, 21, 3, 12, 6, 17, 35.2),
    ("M18x1.5", 18, 1.5, 23, 24, 4, 12, 8, 17, 48.6), ("M20x1.5", 20, 1.5, 25, 26, 4, 14, 8, 19, 64.5),
    ("M22x1.5", 22, 1.5, 27, 26, 4, 14, 8, 19, 73.4), ("M24x1.5", 24, 1.5, 29, 27, 4, 14, 9, 22, 93.5),
    ("M30x1.5", 30, 1.5, 36, 30, 4, 16, 10, 24, 148), ("M38x1.5", 38, 1.5, 44, 32, 5, 16, 11, 27, 238),
    ("M42x1.5", 42, 1.5, 49, 33, 5, 16, 12, 30, 300), ("M45x1.5", 45, 1.5, 52, 33, 5, 16, 12, 30, 340),
    ("M48x1.5", 48, 1.5, 55, 33, 5, 16, 12, 30, 375)]


def P(key, zh, en, role):
    return {"key": key, "zh": zh, "en": en, "role": role}


ENTRIES = {
    "A-WSH-SPR": {
        "name": {"zh": "标准型弹簧垫圈", "en": "Spring lock washer"}, "category": "WSH",
        "tags": ["垫圈", "弹簧垫圈", "防松", "紧固件", "spring washer"],
        "standards": [{"code": "GB/T 93-1987", "title": "标准型弹簧垫圈"}],
        "params": [P("d_mm", "规格（螺纹大径）", "For thread", "key"), P("d_min_mm", "内径最小", "Inside diameter min", "dim"),
                   P("d_max_mm", "内径最大", "Inside diameter max", "dim"), P("s_mm", "厚度 s（= 宽度 b）", "Thickness s (= width b)", "dim"),
                   P("H_min_mm", "自由高度最小", "Free height min", "dim"), P("H_max_mm", "自由高度最大", "Free height max", "dim"),
                   P("m_max_mm", "开口搭接 m 最大", "Overlap m max", "dim")],
        "default": "12", "engine": "wenquest:spring_washer", "origin": "垫圈中心，轴线沿 Z，底面在 z=0",
        "principle": "开口处扭起的弹性圈被螺母压平后产生持续弹力和开口刃口的咬入，增大螺纹副摩擦，防止振动下松脱。",
        "uses": ["箱体联接螺栓下面（WQR-105）", "有振动的一般联接"], "chapter": "螺纹联接的防松",
        "erp": [("WASHER-12", "12")],
        "sources": [{"title": "嘉立创 FA 机械设计手册：标准型弹簧垫圈（GB/T 93—1987）", "url": "https://www.jlc-jdgf.com/mcbook/GBT93-1987.htm",
                     "retrieved": RETRIEVED}]},
    "A-PIN-TAPER": {
        "name": {"zh": "圆锥销（A 型）", "en": "Taper pin, type A"}, "category": "PIN",
        "tags": ["销", "定位销", "圆锥销", "taper pin"],
        "standards": [{"code": "GB/T 117-2000", "title": "圆锥销"}, {"code": "ISO 2339:1986", "title": "Taper pins, unhardened"}],
        "params": [P("d_mm", "公称直径（小端）", "Nominal diameter (small end)", "key"), P("l_mm", "长度", "Length", "key"),
                   P("a_mm", "端部倒圆 a≈", "End radius a≈", "dim"), P("D_mm", "大端直径（锥度 1:50）", "Large-end diameter (taper 1:50)", "dim")],
        "default": "8x35", "engine": "wenquest:taper_pin", "origin": "大端在 z=0，轴线沿 Z",
        "principle": "1:50 的锥度靠楔紧定位，可多次拆装而定位精度不变，常用于需要反复拆装的两零件定位。",
        "uses": ["箱座与箱盖合箱定位（WQR-105）", "端盖、法兰定位"], "chapter": "销联接",
        "erp": [("PIN-8x35", "8x35")],
        "sources": [
            {"title": "ISO 2339:1986 样本（iTeh）：公称直径 d 与 a", "url": "https://cdn.standards.iteh.ai/samples/7174/6d3e6dec32224d188b9d378f45e19cf7/ISO-2339-1986.pdf", "retrieved": RETRIEVED},
            {"title": "易紧通 GB/T 117-2000 圆锥销：长度系列", "url": "https://www.164580.com/info_19244.html?pc=1", "retrieved": RETRIEVED},
            {"title": "Boltport ISO 2339 重量表：各直径的常用长度范围", "url": "https://www.boltport.com/weights/iso-2339/", "retrieved": RETRIEVED,
             "note": "长度取长度系列中落在该范围内的值；标准本身允许的范围更宽"}]},
    "A-SEL-LIP": {
        "name": {"zh": "旋转轴唇形密封圈（骨架油封）", "en": "Rotary shaft lip seal"}, "category": "SEL",
        "tags": ["密封件", "油封", "骨架油封", "oil seal", "lip seal"],
        "standards": [{"code": "GB/T 13871.1-2007", "title": "密封元件为弹性体材料的旋转轴唇形密封圈 第1部分：基本尺寸和公差"}],
        "params": [P("d1_mm", "轴径", "Shaft diameter", "key"), P("D_mm", "外径（座孔）", "Outside diameter (bore)", "key"),
                   P("b_mm", "宽度", "Width", "key")],
        "default": "20x35x7", "engine": "wenquest:lip_seal", "origin": "油封中心，轴线沿 Z，底面在 z=0",
        "principle": "橡胶唇口在弹簧箍紧下贴住旋转轴表面，形成很窄的密封带，把润滑油封在箱内、把灰尘挡在外面。",
        "uses": ["减速器输入、输出轴伸出端（WQR-105）", "电机、泵的旋转轴"], "chapter": "密封装置",
        "erp": [("SEAL-20", "20x35x7"), ("SEAL-30", "30x47x7")],
        "sources": [{"title": "易紧通 GB/T 13871.1-2007 旋转轴唇形密封圈：基本尺寸表", "url": "https://www.164580.com/info_399381.html?pc=1",
                     "retrieved": RETRIEVED}]},
    "A-PLG-HEX": {
        "name": {"zh": "外六角带肩螺塞（重型）", "en": "Hexagon head screw plug with collar, heavy"}, "category": "PLG",
        "tags": ["螺塞", "放油螺塞", "油塞", "screw plug", "drain plug"],
        "standards": [{"code": "DIN 910:1992", "title": "Heavy-duty hexagon head screw plugs, cylindrical thread"}],
        "params": [P("d_mm", "螺纹大径", "Thread diameter", "key"), P("P_mm", "螺距", "Pitch", "dim"),
                   P("d2_mm", "肩径", "Collar diameter", "dim"), P("l_mm", "总长", "Overall length", "dim"),
                   P("c_mm", "肩厚", "Collar thickness", "dim"), P("i_mm", "螺纹长度", "Thread length", "dim"),
                   P("m_mm", "头高", "Head height", "dim"), P("s_mm", "对边宽度", "Width across flats", "dim"),
                   P("mass_kg_per_1000", "千件重（kg）", "Mass per 1000 (kg)", "info")],
        "default": "M16x1.5", "engine": "wenquest:hex_plug", "origin": "螺纹端在 z=0，轴线沿 Z",
        "principle": "细牙螺纹拧入箱体油孔，肩部压紧密封垫圈，放油时拧下；细牙自锁性好，不易振松。",
        "uses": ["减速器箱座最低处放油孔（WQR-105）", "液压、润滑系统的工艺孔"], "chapter": "减速器附件",
        "erp": [("PLUG-M16", "M16x1.5")],
        "sources": [{"title": "Aspen Fasteners：Metric DIN 910 spec", "url": "https://www.aspenfasteners.com/v/vspfiles/files/docs/Metric_DIN_910_spec.pdf",
                     "retrieved": RETRIEVED, "note": "M26、M36 两行总长与分段之和不符，未收；e 值有误印，不收（可由 s 算出）"}]},
}


def rows_of(eid):
    if eid == "A-WSH-SPR":
        return (["size", "d_mm", "d_min_mm", "d_max_mm", "s_mm", "H_min_mm", "H_max_mm", "m_max_mm"],
                [[mm(r[0])] + [mm(x) for x in r] for r in SPRING_WASHER])
    if eid == "A-PIN-TAPER":
        rows = []
        for d, a in PIN_A.items():
            lo, hi = PIN_L_RANGE[d]
            for ln in PIN_L_SERIES:
                if lo <= ln <= hi:
                    rows.append(["{}x{}".format(mm(d), ln), mm(d), ln, mm(a), mm(round(d + ln / 50, 3))])
        return ["size", "d_mm", "l_mm", "a_mm", "D_mm"], rows
    if eid == "A-SEL-LIP":
        return ["size", "d1_mm", "D_mm", "b_mm"], [["{}x{}x{}".format(*r), *r] for r in LIP_SEAL]
    if eid == "A-PLG-HEX":
        return (["size", "d_mm", "P_mm", "d2_mm", "l_mm", "c_mm", "i_mm", "m_mm", "s_mm", "mass_kg_per_1000"],
                [[r[0]] + [mm(x) for x in r[1:]] for r in HEX_PLUG])
    raise KeyError(eid)


def entry_yaml(eid):
    e = ENTRIES[eid]
    return {
        "schema": 1, "id": eid, "kind": "family", "name": e["name"], "category": e["category"], "tags": e["tags"],
        "standards": e["standards"], "params": e["params"], "specs": "specs.csv", "default": e["default"],
        "model": {"engine": e["engine"], "formats": ["step", "stl", "glb"], "origin": e["origin"]},
        "source": {"origin": "wenquest", "license": LICENSE, "attribution": ATTR, "checked": CHECKED,
                   "data_sources": e["sources"]},
        "teaching": {"principle": e["principle"], "uses": e["uses"],
                     "courses": [{"course": "机械设计基础", "chapter": e["chapter"]}], "labs": []},
        "factory": {"erp_items": [{"item_code": c, "size": s} for c, s in e["erp"]], "suppliers": []},
    }


def main():
    for eid in ENTRIES:
        header, rows = rows_of(eid)
        write(eid, header, rows)
        d = CATALOG / "A" / eid
        head = "# {} · {}（第 5 轮第 1 步，P7）\n".format(eid, ENTRIES[eid]["name"]["zh"])
        (d / "entry.yaml").write_text(head + yaml.safe_dump(entry_yaml(eid), allow_unicode=True, sort_keys=False),
                                      encoding="utf-8")


if __name__ == "__main__":
    main()
