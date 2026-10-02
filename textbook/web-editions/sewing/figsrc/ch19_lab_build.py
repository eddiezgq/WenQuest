# -*- coding: utf-8 -*-
"""生成虚拟实验 19-1（labs/config.html，中英两版）：把 ch19_calc.py 写出的 ch19_lib.json 内嵌进模板。
python3 figsrc/ch19_calc.py && python3 figsrc/ch19_lab_build.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
data = json.load(open(os.path.join(HERE, "ch19_lib.json"), encoding="utf-8"))
data = {k: data[k] for k in ("LIB", "K", "BELT_FOR")}
tpl = open(os.path.join(HERE, "ch19_lab_template.html"), encoding="utf-8").read()
L = {"zh": dict(HTMLLANG="zh-CN", TITLE="零件库快速配套器", BACK="返回教材",
                SUB="《缝纫机设计与制造》第 19 章 · 虚拟实验 19-1 · 选机种、填需求，从示意零件库里自动挑出满足判据的最便宜组合，生成 BOM、接线表和固件配置"),
     "en": dict(HTMLLANG="en", TITLE="Parts-library configurator", BACK="Back to the book",
                SUB="Sewing Machine Design and Manufacturing · Chapter 19 · Virtual lab 19-1 · pick a machine, enter the requirements, and pick the cheapest set of modules that meets every criterion from an illustrative library; BOM, I/O map and firmware configuration are generated")}
for lang, d in L.items():
    s = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False)).replace("__LANG__", lang)
    for k, v in d.items():
        s = s.replace("__%s__" % k, v)
    p = os.path.join(ROOT, "src", lang, "labs", "config.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(s)
    print("wrote", p, len(s))
