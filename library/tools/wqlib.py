# -*- coding: utf-8 -*-
"""零件库公共函数：读条目、读规格表、规格代号转文件名。"""
import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
ALLOWED_LICENSES = {"Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSD-3-Clause-Clear", "MIT", "Zlib", "ISC",
                    "CC0-1.0", "CC-BY-3.0", "CC-BY-4.0"}


def entry_dirs():
    return sorted(p.parent for p in CATALOG.glob("*/*/entry.yaml"))


def load(d):
    d = Path(d)
    e = yaml.safe_load(open(d / "entry.yaml", encoding="utf-8"))
    e["_dir"] = d
    return e


def entries(only=None):
    out = [load(d) for d in entry_dirs()]
    if only:
        out = [e for e in out if e["id"] in only or any(e["id"].startswith(o) for o in only)]
    return out


def _num(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
    except ValueError:
        return v
    return int(f) if f == int(f) else f


def specs(e):
    """规格表的每一行（数值已转成数）；robot/mechanism/case 只有一行 default。"""
    if e.get("specs"):
        with open(e["_dir"] / e["specs"], encoding="utf-8") as f:
            return [{k: (_num(v) if k != "size" else v) for k, v in r.items()} for r in csv.DictReader(f)]
    return [dict({"size": "default"}, **(e.get("defaults") or {}))]


def file_code(size):
    return str(size).replace("/", "_").replace("×", "x").replace(" ", "")


def ref(e, size):
    return "{}/{}".format(e["id"], size)
