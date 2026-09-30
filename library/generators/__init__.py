# -*- coding: utf-8 -*-
"""按条目的 model.engine 选造型程序。每个程序 build(entry, row) → [(节点名, 形体或网格)]。"""


def get_builder(entry):
    eng = entry["model"]["engine"]
    if eng.startswith("bd_warehouse:"):
        from generators import a_standard
        return a_standard.build
    raise ValueError("没有造型程序：" + eng)
