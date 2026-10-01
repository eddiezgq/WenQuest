# -*- coding: utf-8 -*-
"""按条目的 model.engine 选造型程序。每个程序 build(entry, row) → [(节点名, 形体或网格)]。"""


def get_builder(entry):
    eng = entry["model"]["engine"]
    if eng.startswith("bd_warehouse:"):
        from generators import a_standard
        return a_standard.build
    if eng.startswith("wenquest:"):
        from generators import a_wenquest
        return a_wenquest.build
    if eng.startswith("proxy:"):
        from generators import d_proxy
        return d_proxy.build
    if eng.startswith("wqrobot:"):
        from generators import b_wq
        return b_wq.build
    if eng.startswith("dh:"):
        from generators import b_dh
        return b_dh.build
    if eng.startswith("menagerie:"):
        from generators import b_robot
        return b_robot.build
    raise ValueError("没有造型程序：" + eng)
