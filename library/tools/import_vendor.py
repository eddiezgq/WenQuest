# -*- coding: utf-8 -*-
"""厂商目录（第 5 轮 P1–P6）：把 library/vendors/<厂商>.yaml 转成零件库条目。

- products → D 部分条目（kind: product）：entry.yaml + specs.csv（每行带出处页码 src_page）；外形代用模型 proxy:<外形>
- robots   → B 部分：Menagerie 已有同型号的，写 vendor.yaml 叠加（技术参数、DH、出处）；没有的新建条目，按 DH 生成模型
用法：python3 tools/import_vendor.py [厂商文件名…]      # 默认全部
"""
import csv

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wqlib import CATALOG, ROOT  # noqa: E402

VENDORS = ROOT / "vendors"
LICENSE = "Apache-2.0"
DATASHEET_LABELS = {
    "payload_kg": ("额定负载", "Payload", "kg"), "reach_mm": ("工作半径", "Reach", "mm"), "dof": ("自由度", "DOF", ""),
    "repeatability_mm": ("重复定位精度 ±", "Pose repeatability ±", "mm"), "tcp_speed_m_s": ("末端最大速度", "TCP speed", "m/s"),
    "footprint_mm": ("底座直径", "Footprint Ø", "mm"), "weight_kg": ("重量", "Weight", "kg"), "ip": ("防护等级", "IP rating", ""),
    "power_typical_w": ("典型功耗", "Typical power", "W"), "power_max_w": ("最大功耗", "Max power", "W"),
}


def _src(v, key, page=None):
    s = v["sources"][key]
    return {"title": s["title"], "url": s["url"], "retrieved": str(v["retrieved"]), **({"note": "第 {} 页".format(page)} if page else {})}


def _dump(path, head, doc):
    path.write_text(head + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def product(v, p):
    eid = p["id"]
    d = CATALOG / "D" / eid
    d.mkdir(parents=True, exist_ok=True)
    keys = [x[0] for x in p["params"]]
    pages = sorted({x[6] for x in p["params"] if len(x) > 6})
    params = [{"key": k, "zh": zh, "en": en, "role": role, **({"unit": u} if u else {})}
              for k, zh, en, role, u, *_ in p["params"] if k not in ("size",)]
    # 规格表：尺寸-减速比；外形按尺寸
    rows = []
    for r in p["rows"]:
        size, ratio, *vals = r
        od, length, mass = p["sizes"][size]
        rec = dict(zip(["T_rated_Nm", "T_repeat_Nm", "T_avg_Nm", "T_momentary_Nm", "n_max_oil_rpm", "n_max_grease_rpm",
                        "n_avg_oil_rpm", "n_avg_grease_rpm", "J_1e4_kgm2"], vals))
        rec.update(size_code=size, ratio=ratio, OD_mm=od, L_mm=length, mass_kg=mass)
        rows.append(rec)
    header = ["size", "size_code", "ratio"] + [k for k in keys if k not in ("size", "ratio")] + ["src_page"]
    with open(d / "specs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for rec in rows:
            w.writerow(["{}-{}".format(rec["size_code"], rec["ratio"]), rec["size_code"], rec["ratio"]]
                       + [rec[k] for k in header[3:-1]] + ["/".join(str(x) for x in pages)])
    params = [{"key": "size_code", "zh": "型号尺寸", "en": "Size", "role": "key"}] + [x for x in params if x["key"] != "size_code"]
    doc = {
        "schema": 1, "id": eid, "kind": "product", "name": p["name"], "category": p["category"],
        "tags": p.get("tags", []) + [v["vendor"]["name"]["zh"], v["vendor"]["name"]["en"]],
        "standards": [], "params": params, "specs": "specs.csv", "default": p["default"],
        "model": {"engine": "proxy:" + p["proxy"], "formats": ["step", "stl", "glb"],
                  "origin": "输出端在 z<0，轴线沿 Z", "note": "外形示意：按样本外形尺寸生成，非厂商模型；厂商 CAD 请到厂商网站下载"},
        "source": {"origin": "vendor", "vendor": v["vendor"]["name"]["en"], "catalog": v["sources"]["csf"]["title"],
                   "license": LICENSE, "attribution": "问渠零件库（规格表整理与外形示意模型）；参数摘自 {} 公开样本，商标归厂商所有".format(
                       v["vendor"]["name"]["en"]),
                   "checked": {"by": "Claude", "on": str(v["retrieved"]), "note": "两次独立读取样本表格，结果一致"},
                   "data_sources": [_src(v, "csf", "、".join(str(x) for x in pages))]},
        "vendor": {"id": v["vendor"]["id"], "name": v["vendor"]["name"], "site": v["vendor"]["site"], "series": p.get("series")},
        "teaching": {"principle": p["principle"], "uses": p["uses"],
                     "courses": [{"course": "机器人技术", "chapter": "关节驱动与减速器"}], "labs": []},
        "factory": {"erp_items": [], "suppliers": [v["vendor"]["name"]["en"]]},
    }
    _dump(d / "entry.yaml", "# {} · {}（厂商目录，第 5 轮第 2 步）\n".format(eid, p["name"]["zh"]), doc)
    return eid


def robot(v, r):
    eid = r["id"]
    d = CATALOG / "B" / eid
    ds = dict(r["datasheet"])
    dh = {"params": r["dh"], "convention": "standard DH (a, d, alpha)", "range_deg": r["joint_range_deg"],
          "speed_deg_s": r["joint_speed_deg_s"], "reach_mm": ds["reach_mm"]}
    sheet = {"vendor": v["vendor"]["name"]["en"], "model": r["model"], "values": ds,
             "labels": {k: {"zh": DATASHEET_LABELS[k][0], "en": DATASHEET_LABELS[k][1], "unit": DATASHEET_LABELS[k][2]}
                        for k in ds},
             "src": v["sources"][r["src"]]["url"], **({"note": r["note"]} if r.get("note") else {})}
    sources = [_src(v, r["src"]), _src(v, "dh")]
    vend = {"id": v["vendor"]["id"], "name": v["vendor"]["name"], "site": v["vendor"]["site"], "model": r["model"]}
    if (d / "entry.yaml").exists() and "menagerie:" in (d / "entry.yaml").read_text(encoding="utf-8"):
        _dump(d / "vendor.yaml", "# {} 的厂商参数（第 5 轮 P4，叠加在 Menagerie 条目上）\n".format(eid),
              {"vendor": vend, "datasheet": sheet, "dh": dh, "data_sources": sources,
               "tags": [v["vendor"]["name"]["zh"], v["vendor"]["name"]["en"], r["model"]]})
        return eid
    d.mkdir(parents=True, exist_ok=True)
    doc = {
        "schema": 1, "id": eid, "kind": "robot",
        "name": {"zh": "{} {} 协作机械臂".format(v["vendor"]["name"]["en"], r["model"]),
                 "en": "{} {}".format(v["vendor"]["name"]["en"], r["model"])},
        "category": "ARM", "tags": ["机械臂", "协作机器人", "arm", "cobot", v["vendor"]["name"]["zh"], r["model"]],
        "standards": [], "params": [], "defaults": {},
        "model": {"engine": "dh:", "formats": ["glb"], "origin": "基座坐标系 = DH 坐标系 {0}（Z 向上）；每个连杆一个节点",
                  "note": "按厂商公布的 DH 参数生成的示意模型（关节位置、连杆长度准确，外形简化）；厂商 CAD 请到厂商网站下载"},
        "robot": {"type": "arm", "payload_kg": ds["payload_kg"], "reach_mm": ds["reach_mm"]},
        "source": {"origin": "vendor", "vendor": v["vendor"]["name"]["en"], "catalog": v["sources"][r["src"]]["title"],
                   "license": LICENSE, "attribution": "问渠零件库（示意模型）；参数摘自 {} 官方技术参数表与 DH 参数，商标归厂商所有".format(
                       v["vendor"]["name"]["en"]),
                   "checked": {"by": "Claude", "on": str(v["retrieved"]), "note": "照官方表录入"},
                   "data_sources": sources},
        "vendor": vend, "datasheet": sheet, "dh": dh,
        "teaching": {"principle": "六个转动关节串联：前三个关节主要决定末端位置，后三个（腕部）决定姿态；协作机器人带力矩感知，可与人同区工作。",
                     "uses": ["装配", "上下料", "打磨", "码垛"],
                     "courses": [{"course": "机器人技术", "chapter": "串联机械臂运动学（DH 参数）"}], "labs": []},
        "factory": {"erp_items": [], "suppliers": [v["vendor"]["name"]["en"]]},
    }
    _dump(d / "entry.yaml", "# {} · {}（厂商目录，第 5 轮第 2 步）\n".format(eid, doc["name"]["zh"]), doc)
    return eid


def main(names=None):
    files = [VENDORS / n for n in names] if names else sorted(VENDORS.glob("*.yaml"))
    for f in files:
        v = yaml.safe_load(open(f, encoding="utf-8"))
        done = [product(v, p) for p in v.get("products") or []] + [robot(v, r) for r in v.get("robots") or []]
        print("{}：{}".format(v["vendor"]["name"]["zh"], "、".join(done)))



if __name__ == "__main__":
    main(sys.argv[1:])
