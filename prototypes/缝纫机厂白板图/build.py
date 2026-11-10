# -*- coding: utf-8 -*-
"""第 136 轮：缝纫机厂白板图。

读 factory/plants/wenquest-sewing.yaml（设备、位置、工序、工艺路线、工时、物料清单、测量特性）
和 docs/方案/缝纫机厂工艺方案.md（工步、定位、检验要求），生成单文件网页 index.html。
不另编参数：方案里没写的就不显示。

用法：python3 prototypes/缝纫机厂白板图/build.py
"""
import json
import pathlib
import re
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLANT = ROOT / "factory/plants/wenquest-sewing.yaml"
DOC = ROOT / "docs/方案/缝纫机厂工艺方案.md"

# 车间分区（与生成清单的脚本一致；清单里每台设备的位置都落在这些区里）
ZONES = [
    {"id": "foundry", "no": "①", "name": "机壳铸造车间", "en": "Housing foundry", "rect": [4, 4, 80, 50], "h": 14},
    {"id": "housing", "no": "②", "name": "机壳加工车间", "en": "Housing machining", "rect": [86, 4, 160, 50], "h": 10},
    {"id": "parts", "no": "③", "name": "关键零件加工车间", "en": "Key parts machining", "rect": [86, 58, 160, 106], "h": 9},
    {"id": "ls", "no": "④", "name": "平缝机装配车间", "en": "Lockstitch assembly", "rect": [166, 26, 226, 60], "h": 8},
    {"id": "ol", "no": "⑤", "name": "包缝机装配车间", "en": "Overlock assembly", "rect": [166, 66, 226, 100], "h": 8},
    {"id": "metro", "no": "", "name": "计量室", "en": "Metrology room", "rect": [166, 4, 226, 20], "h": 5},
    {"id": "store", "no": "", "name": "库房", "en": "Stores", "rect": [4, 58, 72, 90], "h": 5},
]

# 工序 → 方案里的哪张表、哪一行（按零件分；同一道工序在平缝、包缝机壳上对应不同的行）
FOUNDRY = {"C10": "C10", "C20": "C20", "C30": "C30", "C40": "C90", "C45": "C90", "C50": "C50", "C55": "C50",
           "C60": "C60", "C65": "C40", "C70": "C70", "C80": "C80", "C90": "C90", "C100": "C100", "C110": "C110",
           "C120": "C120", "C130": "C130", "C140": "C140", "C150": "C150", "C155": "C150", "C158": "C160", "C160": "C160"}
HSG_LS = {"H10": "10", "LS20": "20", "LS30": "30", "H40": "40", "LS50": "50", "LS70": "70", "LS80": "80", "LS90": "90",
          "H100": "100", "H105": "110", "H110": "110", "H115": "115", "H118": "115"}
HSG_OL = {"H10": "10", "OL20": "20", "OL30": "30", "H40": "40", "OL50": "50", "OL70": "70", "OL80": "80", "OL90": "90",
          "H100": "100", "OL110": "110", "H105": "120", "H110": "120", "H115": "125", "H118": "125"}
SHAFT = {"P10": "10", "P20": "20", "P30": "30", "P40": "40", "P50": "50", "P60": "60", "P70": "70", "P80": "80",
         "P90": "90", "P100": "110", "P110": "100"}
ASM_LS = {"LA-S1": "分装 1", "LA-S2": "分装 2", "LA-S3": "分装 3", "LA-S4": "分装 4", "LA-ADJ": "调试", "LA-RUN": "跑合",
          "LA-EOL": "出厂测试", "LA-PK": "清洗包装", **{f"LA-A{i:02d}": f"A{i:02d}" for i in range(1, 13)}}
ASM_OL = {"OA-S1": "分装 1", "OA-S2": "分装 2", "OA-ADJ": "调试", "OA-RUN": "跑合", "OA-EOL": "出厂测试",
          "OA-PK": "清洗包装", **{f"OA-B{i:02d}": f"B{i:02d}" for i in range(1, 7)}}
ROWMAP = {"CAST-LS": ("2.2", FOUNDRY), "CAST-OL": ("2.2", FOUNDRY), "HSG-LS": ("3.2", HSG_LS), "HSG-OL": ("3.3", HSG_OL),
          "LS-101": ("4.2", SHAFT), "LS-102": ("4.2", SHAFT), "OL-101": ("4.2", SHAFT),
          "WQ-LS": ("五", ASM_LS), "WQ-OL": ("六", ASM_OL)}
# 方案 4.1 节零件表里的哪一行（没有逐道工序的工艺规程，只有路线和关键特性）
PARTROW = {"LS-101": "平缝上轴", "LS-102": "平缝下轴", "OL-101": "包缝主轴", "LS-201": "针杆", "OL-201": "针杆",
           "LS-301": "旋梭", "LS-401": "偏心", "OL-401": "偏心"}
# 铸造检验规程（2.3）里和各工序相关的检验点
FOUNDRY_QC = {"C10": ["炉料"], "C20": ["铁水"], "C30": ["铁水"], "C65": ["铁水"], "C40": ["型砂"], "C45": ["型砂"],
              "C60": ["型砂"], "C90": ["型砂"], "C50": ["砂芯"], "C55": ["砂芯"], "C140": ["时效"], "C158": ["试棒", "金相", "内部", "铸件"],
              "C160": ["铸件", "试棒", "金相", "内部"]}


def split_name(s):
    code, rest = s.split(" ", 1)
    m = re.search(r"[A-Za-z]", rest)
    zh, en = (rest[:m.start()].strip(), rest[m.start():].strip()) if m else (rest, "")
    return code, zh, en


def parse_doc(text):
    """把方案拆成 {小节号: {"title", "tables": [[表头, 行...]], "lines": [...] }}"""
    secs, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^(#{2,3}) (.+)$", line)
        if m:
            title = m.group(2).strip()
            k = re.match(r"([0-9]+\.[0-9]+|[一二三四五六七八九〇])", title)
            key = k.group(1) if k else title
            cur = secs.setdefault(key, {"title": title, "tables": [], "lines": []})
            continue
        if cur is None:
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                continue
            if cur["tables"] and cur.get("_in_table"):
                cur["tables"][-1].append(cells)
            else:
                cur["tables"].append([cells])
            cur["_in_table"] = True
        else:
            cur["_in_table"] = False
            if line.strip():
                cur["lines"].append(line.rstrip())
    for s in secs.values():
        s.pop("_in_table", None)
    return secs


def table_rows(sec):
    head, *rows = sec["tables"][0]
    return head, rows


def md_inline(s):
    s = s.replace("<br>", "\n")
    return s


def main():
    plant = yaml.safe_load(PLANT.read_text(encoding="utf-8"))
    secs = parse_doc(DOC.read_text(encoding="utf-8"))

    # 设备
    units = {}
    for u in plant["units"]:
        lay = u.get("layout")
        z = None
        if lay:
            cx, cy = lay[0] + lay[2] / 2, lay[1] + lay[3] / 2
            for zz in ZONES:
                x0, y0, x1, y1 = zz["rect"]
                if x0 <= cx <= x1 and y0 <= cy <= y1:
                    z = zz["id"]
                    break
        units[u["id"]] = {"name": u["name"], "en": u.get("name_en", ""), "ws": u.get("workstation", ""),
                          "lay": lay, "h": u.get("height_m", 2), "zone": z, "area": u["area"],
                          "cap": u.get("capacity", 1), "home": u.get("home")}
    for zz in ZONES:
        zz["units"] = [k for k, v in units.items() if v["zone"] == zz["id"]]

    # 工序
    ops = {}
    for o in plant["operations"]:
        code, zh, en = split_name(o["name"])
        ops[code] = {"full": o["name"], "zh": zh, "en": en, "ws": o["workstation"], "units": o["units"],
                     "stage": o["stage"], "insp": bool(o.get("inspection"))}
    wsinfo = {w["name"]: {"count": w["count"]} for w in plant["workstations"]}

    # 物料、工艺路线、物料清单
    items = {i["code"]: {"name": i["name"], "kind": i["kind"], "uom": i["uom"], "note": i.get("note", "")} for i in plant["items"]}
    routings = {r["name"]: [[split_name(s[0])[0], s[1]] for s in r["steps"]] for r in plant["routings"]}
    meas = {}
    for m in plant["measurements"]:
        meas.setdefault(m["item"], {})[split_name(m["operation"])[0]] = m["chars"]
    made = {}
    for b in plant["boms"]:
        made[b["item"]] = {"routing": b["routing"], "bom": [[c[0], items.get(c[0], {}).get("name", c[0]), c[1],
                                                              items.get(c[0], {}).get("uom", "")] for c in b["components"]]}

    # 方案的行：(零件, 工序) → {title, fields}
    def find_row(sec_key, key):
        head, rows = table_rows(secs[sec_key])
        for r in rows:
            first = r[0].replace("**", "")
            if first == key or first.startswith(key + "（") or first.startswith(key + " ") or (key in ("调试", "跑合", "出厂测试", "清洗包装") and first.startswith(key)):
                return head, r
        return None

    docrows, missing = {}, []
    for item, (sk, mp) in ROWMAP.items():
        steps = routings[made[item]["routing"]]
        for code, _ in steps:
            key = mp.get(code)
            hit = find_row(sk, key) if key else None
            if not hit:
                missing.append((item, code))
                continue
            head, r = hit
            docrows[f"{item}|{code}"] = {"src": f"《缝纫机厂工艺方案》{secs[sk]['title']}，{head[0]} {r[0]}",
                                         "fields": [[h, md_inline(v)] for h, v in zip(head, r)]}
    # 零件表 4.1
    head41, rows41 = table_rows(secs["4.1"])
    partrows = {}
    for item, kw in PARTROW.items():
        for r in rows41:
            if kw in r[0]:
                partrows[item] = {"src": f"《缝纫机厂工艺方案》{secs['4.1']['title']}", "fields": [[h, v] for h, v in zip(head41, r)]}
                break
    # 铸件（2.1）
    head21, rows21 = table_rows(secs["2.1"])
    castrows = {"CAST-LS": rows21[0], "CAST-OL": rows21[1]}
    castrows = {k: {"src": f"《缝纫机厂工艺方案》{secs['2.1']['title']}", "fields": [[h, v] for h, v in zip(head21, r)]} for k, r in castrows.items()}
    # 铸造检验规程 2.3
    head23, rows23 = table_rows(secs["2.3"])
    fqc = {}
    for code, kws in FOUNDRY_QC.items():
        fqc[code] = [r for r in rows23 if any(r[0].startswith(k) for k in kws)]
    defects = secs["2.3"]["tables"][1] if len(secs["2.3"]["tables"]) > 1 else []

    # 每个工位做哪些（零件, 工序）
    unit_jobs = {}
    for item, mk in made.items():
        for code, _ in routings[mk["routing"]]:
            for u in ops[code]["units"]:
                unit_jobs.setdefault(u, []).append([item, code])

    unused_ops = [c for c in ops if not any(c == s[0] for st in routings.values() for s in st)]
    if missing or unused_ops:
        print("对不上方案的（零件, 工序）：", missing, file=sys.stderr)
        print("没进工艺路线的工序：", unused_ops, file=sys.stderr)

    data = {
        "plant": {"name": plant["company"]["name"], "floor": plant["floor"]},
        "zones": ZONES, "units": units, "ops": ops, "ws": wsinfo, "items": items, "made": made,
        "routings": routings, "meas": meas, "docrows": docrows, "partrows": partrows, "castrows": castrows,
        "fqc": {"head": head23, "rows": fqc}, "defects": defects, "unitJobs": unit_jobs,
        "principles": secs["3.1"]["lines"],
        "holes": {"HSG-LS": [l for l in secs["3.2"]["lines"] if l.startswith("- ")],
                  "HSG-OL": [l for l in secs["3.3"]["lines"] if l.startswith("- ")]},
        "asmNote": {"WQ-LS": secs["五"]["lines"][:1], "WQ-OL": secs["六"]["lines"][:1]},
        "general": secs["八"]["lines"],
    }
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    out = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    (HERE / "index.html").write_text(out, encoding="utf-8")
    n = sum(len(v) for v in unit_jobs.values())
    print(f"工位 {len(units)}，工序 {len(ops)}，（零件, 工序）{sum(len(routings[m['routing']]) for m in made.values())}，"
          f"对上方案的行 {len(docrows)}，工位-工序 {n}，输出 {len(out) // 1024} KB")


if __name__ == "__main__":
    main()
