# -*- coding: utf-8 -*-
"""E 部分“工装夹具”的造型程序（第 13 轮 8.7）：直接调用数字工厂的三维模型 factory/digital/models3d，
书中的三维图、动画、工程图、数字工厂和零件库用的是同一个函数、同一组参数。

engine 写成 wqfix:<模块>.<函数>，模块是 elements、locating、machines、typical、jj30150、workpiece，
另有本文件里的几个组合（wqfix:local.<名称>）。条目的 defaults 是函数参数（书中所用的那一个规格），
model.args 是不在参数表里显示的固定参数（列表按元组传）。

返回 [(节点名, 形体)]（毫米，Z 向上）。每个形体带属性 _wq：{rgba, meta, mesh}——rgba 是节点颜色，
meta 是零件表的一行（零件名、序号、作用、爆炸方向），mesh 是按面着色时（工件的本工序加工面）给出网格的函数。
"""
from __future__ import annotations

import sys
from pathlib import Path

DIGITAL = Path(__file__).resolve().parents[2] / "factory" / "digital"
if str(DIGITAL) not in sys.path:
    sys.path.insert(0, str(DIGITAL))

ROLES = [   # 按零件名判断作用（零件表“作用”一栏；顺序有讲究：先认工件、标准件）
    ("工件", ("工件", "毛坯", "SH-301")),
    ("刀具", ("铣刀", "钻头", "镗刀")),
    ("标准件", ("螺栓", "螺钉", "螺母", "垫圈", "弹簧", "T 形槽", "T形槽")),
    ("操作件", ("手柄", "把手", "手轮", "丝杠")),
    ("夹具体", ("定位键", "夹具体")),
    ("对刀导向", ("对刀", "钻套", "镗套", "钻模板", "塞尺", "衬套", "镗杆", "导向")),
    ("夹紧", ("缸体", "活塞", "杠杆")),
    ("定位", ("V 形块", "V形块", "拉钉", "分度", "支承", "定位", "销", "心轴", "顶尖", "挡块", "挡板", "挡销", "止推", "定心", "锥", "卡爪", "钳口")),
    ("夹紧", ("压板", "夹紧", "偏心", "斜楔", "压块", "夹头", "铰链", "气缸", "活塞", "拉杆", "摆杆", "压头")),
    ("夹具体", ("夹具体", "底板", "滑柱", "钳身", "主轴", "平衡块", "底座", "立柱", "角铁", "定位键", "基础板", "本体", "盘", "台", "塔", "座", "架", "体")),
]


def role_of(name: str, color: str = "") -> str:
    if color == "work":
        return "工件"
    for role, keys in ROLES:
        if any(k in name for k in keys):
            return role
    return "其他"


def _rgba(hexcolor: str, opacity: float = 1.0):
    h = hexcolor.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [int(255 * opacity)]


def _mods():
    from models3d import elements, jj30150, locating, machines, typical, workpiece
    return {"elements": elements, "locating": locating, "machines": machines, "typical": typical,
            "jj30150": jj30150, "workpiece": workpiece, "local": sys.modules[__name__]}


def _tuples(v):
    if isinstance(v, list):
        return tuple(_tuples(x) for x in v)
    return v


def kwargs_of(entry, row) -> dict:
    keys = [p["key"] for p in entry.get("params", [])]
    kw = {k: row[k] for k in keys if k in row and row[k] not in (None, "")}
    for k, v in kw.items():
        if isinstance(v, str):
            try:
                kw[k] = float(v) if "." in v or "e" in v.lower() else int(v)
            except ValueError:
                pass
    kw.update({k: _tuples(v) for k, v in (entry["model"].get("args") or {}).items()})
    return kw


def call(entry, row):
    mod, fn = entry["model"]["engine"].split(":", 1)[1].split(".")
    return getattr(_mods()[mod], fn)(**kwargs_of(entry, row))


def nodes_of(obj, entry=None, color="hardened"):
    """模型函数的返回值（形体、{名称: 形体}、Part、Assembly）→ [(节点名, 形体)]，节点名 p01、p02……"""
    from models3d.core import COLORS, Assembly, Part, tessellate
    colors = (entry or {}).get("model", {}).get("colors") or {}
    parts = []
    if isinstance(obj, Assembly):
        parts = list(obj.parts)
    elif isinstance(obj, Part):
        parts = [obj]
    elif isinstance(obj, dict):
        names = (entry or {}).get("model", {}).get("names") or {}
        parts = [Part(names.get(n, n), s, colors.get(n, color)) for n, s in obj.items()]
    elif isinstance(obj, (tuple, list)):
        names = (entry or {}).get("model", {}).get("names") or []
        parts = [Part(names[i] if i < len(names) else f"零件{i + 1}", s, color) for i, s in enumerate(obj)]
    else:
        parts = [Part((entry or {}).get("name", {}).get("zh", "零件"), obj, colors.get("*", color))]
    out = []
    from models3d import shapes as S
    for i, p in enumerate(parts):
        shape0 = p.shape
        off = next((t[1] for t in (p.tags or ()) if isinstance(t, tuple) and len(t) == 2 and t[0] == "offset_mm"), None)
        shape = S.move(shape0, *off) if off else shape0
        hexc = COLORS.get(p.color, p.color)
        roles = (entry or {}).get("model", {}).get("roles") or {}
        role = next((r for k, r in roles.items() if k in p.name), None) or role_of(p.name, p.color)
        w = {"rgba": _rgba(hexc, p.opacity),
             "meta": {"node": f"p{i + 1:02d}", "name": p.name, "number": p.number, "role": role,
                      "color": hexc, "explode_mm": [round(float(x), 3) for x in p.explode]}}
        if off:                               # 排开摆放的节点：加上 home_mm 回到原位（实验页逐个切换用）
            w["meta"]["home_mm"] = [round(-float(x), 3) + 0.0 for x in off]
        if p.face_color is not None:          # 按面着色（橙色为本工序加工面）：在原位网格化、判断面，再平移
            fc = p.face_color

            def mesh(shape0=shape0, fc=fc, base=w["rgba"], off=off or (0.0, 0.0, 0.0)):
                v, t, _, cols = tessellate(shape0, 0.05, face_color=fc)
                v = [[a + off[0], b + off[1], c + off[2]] for a, b, c in v]
                return v, t, [(_rgba(COLORS.get(c, c)) if c else base) for c in cols]
            w["mesh"] = mesh
        try:
            shape._wq = w
        except AttributeError:               # 个别形体类不能加属性：包一层 Compound
            from build123d import Compound
            shape = Compound(children=[shape])
            shape._wq = w
        out.append((w["meta"]["node"], shape))
    return out


def build(entry, row):
    return nodes_of(call(entry, row), entry)


# ---------------------------------------------------------------- 本文件里的组合（wqfix:local.*）
def sh301_states(spacing=70.0):
    """SH-301 的毛坯与五个工序状态，每个状态一个节点，沿 y 排开（间距 spacing）；本工序加工面着橙色。"""
    from models3d.core import Assembly
    from models3d import workpiece as W
    names = [("blank", "毛坯（工序 10 下料后）"), ("op20", "工序 20 粗车后"), ("op40", "工序 40 精车后"),
             ("op50", "工序 50 铣键槽后"), ("op60", "工序 60 磨外圆后（成品）")]
    a = Assembly("SH-301 各工序状态")
    for k, (st, zh) in enumerate(names):
        p = W.sh301(st, highlight=st != "blank")
        p.name = "工件 SH-301 " + zh
        p.tags = (("offset_mm", (0.0, (k - 2) * spacing, 0.0)),)   # 沿 y 排开；本工序加工面按原位判断
        a.add(p)
    return a


def jj30150_full(work_state="op40"):
    """JJ-301-50 键槽铣夹具总成：夹具、工件（工序 50 铣键槽前的状态）、对刀用的铣刀不画。"""
    from models3d import jj30150 as J
    return J.assembly(work_state, with_work=True, with_cutter=False, with_table=False)
