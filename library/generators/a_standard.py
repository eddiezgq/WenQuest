# -*- coding: utf-8 -*-
"""A 部分标准件：按条目的 model.engine 调用 bd_warehouse 造型，返回 [(节点名, 形体)]（毫米，Z 向上）。"""
from bd_warehouse import bearing as B
from bd_warehouse.fastener import HexHeadScrew, HexNut, PlainWasher, SocketHeadCapScrew
from bd_warehouse.o_rings import ORing
from bd_warehouse.retaining_ring import ExternalSnapRing
from bd_warehouse.shaft_key import ShaftKey
from build123d import Compound


def _thread(row):
    """(d, P) → bd_warehouse 的规格写法，如 M12-1.75"""
    def s(x):
        return ("%g" % float(x))
    return "M{}-{}".format(s(row["d_mm"]), s(row["P_mm"]))


def _deep_groove(row):
    """GB/T 276 的外形尺寸注入 bd_warehouse 的深沟球轴承造型；滚道挡边直径按外形尺寸取示意值。"""
    d, D, Bw, r = (float(row[k]) for k in ("d_mm", "D_mm", "B_mm", "r_min_mm"))
    t = 0.26 * (D - d)
    key = "M{}-{}-{}".format(row["d_mm"], row["D_mm"], row["B_mm"])
    f = lambda x: "%.4f" % x  # noqa: E731  bd_warehouse 按字符串读数，位数太长会当作非数字
    data = {key: {"WQ:d": f(d), "WQ:D": f(D), "WQ:B": f(Bw), "WQ:r12": f(min(r, 0.12 * (D - d))),
                  "WQ:d1": f(d + t), "WQ:D1": f(D - t)}}
    cls = type("WQDeepGroove", (B.SingleRowDeepGrooveBallBearing,), {"bearing_data": data})
    return cls(key, "WQ")


def _nodes(shape, default="part"):
    """装配体按零件标签分节点（同名的合并成一个，如全部钢球为 Roller），单个零件一个节点。"""
    kids = [c for c in getattr(shape, "children", []) or [] if c.wrapped is not None]
    if not kids:
        return [(default, shape)]
    groups = {}
    for c in kids:
        groups.setdefault(c.label or default, []).append(c)
    return [(name, cs[0] if len(cs) == 1 else Compound(children=[c.moved(c.location) if False else c for c in cs]))
            for name, cs in groups.items()]


def build(entry, row):
    eng = entry["model"]["engine"].split(":")
    kind = eng[1]
    if kind == "HexHeadScrew":
        shape = HexHeadScrew(_thread(row), float(row["l_mm"]), eng[2], simple=True)
    elif kind == "SocketHeadCapScrew":
        shape = SocketHeadCapScrew(_thread(row), float(row["l_mm"]), eng[2], simple=True)
    elif kind == "HexNut":
        shape = HexNut(_thread(row), eng[2], simple=True)
    elif kind == "PlainWasher":
        shape = PlainWasher(row["size"], eng[2])
    elif kind == "ShaftKey":
        shape = ShaftKey(int(row["shaft_max_mm"]), float(row["l_mm"]), key_form=eng[2] if len(eng) > 2 else "A")
    elif kind == "ExternalSnapRing":
        shape = ExternalSnapRing(str(row["size"]))
    elif kind == "ORing":
        shape = ORing(str(row["size"]), eng[2])
    elif kind == "SingleRowDeepGrooveBallBearing":
        shape = _deep_groove(row)
    elif hasattr(B, kind):
        shape = getattr(B, kind)(row["bd_size"])
    else:
        raise ValueError("不认识的造型程序 " + entry["model"]["engine"])
    return _nodes(shape, entry["id"].split("-")[1].lower())
