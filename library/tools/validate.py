# -*- coding: utf-8 -*-
"""校验全部条目：格式（schema）、许可、规格表与参数定义一致、默认规格与 ERPNext 对应的规格存在。

    python3 tools/validate.py       # 有问题时列出并返回 1
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jsonschema  # noqa: E402
import wqlib  # noqa: E402

CATEGORIES = {k: set(v) for k, v in wqlib.CATEGORY_NAMES.items()}


def problems():
    schema = json.load(open(wqlib.ROOT / "schema" / "entry.v1.json", encoding="utf-8"))
    out, seen = [], set()
    for d in wqlib.entry_dirs():
        e = wqlib.load(d)
        doc = {k: v for k, v in e.items() if not k.startswith("_")}
        where = e.get("id", d.name)
        for err in jsonschema.Draft202012Validator(schema).iter_errors(doc):
            out.append("{}：格式 {} {}".format(where, "/".join(map(str, err.path)), err.message[:120]))
        if e.get("id") != d.name or d.parent.name != str(e.get("id", "?"))[0]:
            out.append("{}：文件夹名应为 {}/{}".format(where, str(e.get("id", "?"))[0], e.get("id")))
        if e.get("id") in seen:
            out.append("{}：编号重复".format(where))
        seen.add(e.get("id"))
        part = str(e.get("id", "?"))[0]
        if e.get("category") not in CATEGORIES.get(part, set()):
            out.append("{}：类别 {} 不在 {} 部分的词表里".format(where, e.get("category"), part))
        lic = (e.get("source") or {}).get("license")
        if lic not in wqlib.ALLOWED_LICENSES:
            out.append("{}：许可 {} 不在可收名单（B.6）".format(where, lic))
        try:
            rows = wqlib.specs(e)
        except Exception as ex:  # noqa: BLE001
            out.append("{}：读不了规格表（{}）".format(where, ex))
            continue
        if e.get("specs"):
            cols = set(rows[0].keys()) - {"size"} if rows else set()
            keys = {p["key"] for p in e.get("params", [])}
            if cols != keys:
                out.append("{}：规格表列 {} 与参数定义 {} 不一致".format(where, sorted(cols), sorted(keys)))
            sizes = [str(r["size"]) for r in rows]
            if len(set(sizes)) != len(sizes):
                out.append("{}：规格代号重复".format(where))
            codes = [wqlib.file_code(s) for s in sizes]
            if len(set(codes)) != len(codes):
                out.append("{}：规格代号转成文件名后重复".format(where))
            if str(e.get("default")) not in sizes:
                out.append("{}：默认规格 {} 不在规格表里".format(where, e.get("default")))
            for x in (e.get("factory") or {}).get("erp_items") or []:
                if str(x.get("size")) not in sizes:
                    out.append("{}：ERPNext 物料 {} 对应的规格 {} 不在规格表里".format(where, x.get("item_code"), x.get("size")))
    return out


if __name__ == "__main__":
    p = problems()
    for x in p:
        print(x)
    print("条目校验：{} 个问题".format(len(p)))
    sys.exit(1 if p else 0)
