"""第 52 轮：整机拆装动画的数据——教材平缝机虚拟样机的三维模型（textbook/web-editions/sewing/models/proto_lockstitch.py，27 个零件编号），
按虚拟样机里主轴转角 0° 的位姿摆好，投影成斜视图，每个零件取外轮廓（多边形），存 data/explode.json（几十 KB，网页直接画）。
拆开的方向和距离照虚拟样机的“拆开”表（EX），零件编号、分组照装配手册。

  python3 tools/explode_data.py
"""
import importlib.util
import json
import math
import subprocess
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SEW = ROOT / "textbook/web-editions/sewing"
spec = importlib.util.spec_from_file_location("proto", SEW / "models/proto_lockstitch.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

# 主轴转角 0° 时各运动零件的位姿：取虚拟样机自己的机构库（lockstitch-kit.js），保证和样机一致
js = r"""
global.window=global; require(process.argv[1]); const K=window.WQLS;
const E=K.machine.evaluate(K.machine.STD);
console.log(JSON.stringify({L:K.takeup.linkPose(0,K.takeup.LK0), PHC:E.hook.fc, dogY:E.feed.Y(0), dogX:E.feed.X(0)}));
"""
pose = json.loads(subprocess.check_output(["node", "-e", js, str(SEW / "src/lib/lockstitch-kit.js")], text=True))
HS, YH, YL, RN, LN = P.HS, P.YH, P.YL, P.RN, P.LN
L = pose["L"]


def rx(t):           # three.js 的 rotation.x：(y, z) 绕 x 轴转
    c, s = math.cos(t), math.sin(t)
    return lambda v: (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)


def tr(off, rot=None):
    def f(v):
        if rot:
            v = rot(v)
        return (v[0] + off[0], v[1] + off[1], v[2] + off[2])
    return f


PLACE = {
    "upper": tr((0, HS, 0)), "lower": tr((0, YL, 0)), "bcase": tr((0, YH, 0)), "bstop": tr((0, YH, 0)),
    "hook": tr((0, YH, 0), rx(2 * (0 - pose["PHC"]) * math.pi / 180)),
    "rod": tr((0, HS + RN, 0)), "nbar": tr((0, HS + RN - LN, 0)),
    "tklever": tr((0, HS + L["P"][1], L["P"][0]), rx(-math.atan2(L["M"][1] - L["P"][1], L["M"][0] - L["P"][0]))),
    "tklink": tr((0, HS + L["Q"][1], L["Q"][0]), rx(-math.atan2(L["M"][1] - L["Q"][1], L["M"][0] - L["Q"][0]))),
    "dog": tr((0, pose["dogY"], -pose["dogX"])),
}
# 拆开：虚拟样机的表 + 其余零件（台板往下、线架往后上……）
EX = {"face": [-110, 0, 0], "top": [0, 110, 0], "rear": [0, 0, -110], "tension": [0, 30, 120], "guide": [0, 30, 120], "presser": [0, 0, -60],
      "rod": [-60, 40, 0], "nbar": [-60, 0, 0], "tklever": [-150, 130, 60], "tklink": [-150, 95, 40], "upper": [0, 90, 0], "lower": [0, -90, 0],
      "hook": [-80, -70, 0], "bcase": [-130, -70, 0], "dog": [0, -40, 90], "belt": [90, 0, 0], "plate": [0, 25, 0], "slide": [0, 25, 0],
      "bstop": [-130, -70, 0], "table": [0, -60, 0], "stand": [60, 0, -90], "spool": [60, 0, -90], "bush": [0, 0, 50], "details": [40, 0, 70],
      "oil": [0, 0, 60], "panes": [0, 0, 0]}
YAW, PITCH = math.radians(28), math.radians(18)


def view(v):
    x, y, z = v
    x, z = x * math.cos(YAW) + z * math.sin(YAW), -x * math.sin(YAW) + z * math.cos(YAW)
    y, z = y * math.cos(PITCH) - z * math.sin(PITCH), y * math.sin(PITCH) + z * math.cos(PITCH)
    return x, y, z


def outline(key, shape):
    vs, ts = P.mesh(shape, 1.2, 0.6)
    place = PLACE.get(key, lambda v: v)
    w = [view(place(v)) for v in vs]
    tris = []
    for a, b, c in ts:
        poly = Polygon([w[a][:2], w[b][:2], w[c][:2]])
        if poly.area > 1e-3:
            tris.append(poly.buffer(0.05))
    U = unary_union(tris).buffer(0.3).buffer(-0.3).simplify(0.6)
    geoms = getattr(U, "geoms", [U])
    rings = [[[round(x, 1), round(-y, 1)] for x, y in g.exterior.coords[:-1]] for g in geoms if g.area > 4]
    depth = sum(p[2] for p in w) / len(w)
    return rings, depth


shapes = P.build()
parts = []
for code, key, zh, en, group, mat, kind in P.PARTS:
    if key == "panes":            # 开窗透明板：只在“开窗”显示时出现，这里不画，表里照列
        parts.append(dict(code=code, key=key, zh=zh, group=group, mat=mat, rings=[], depth=0, ex=[0, 0]))
        continue
    rings, depth = outline(key, shapes[key])
    e3 = view([1.25 * c for c in EX.get(key, [0, 0, 0])])
    parts.append(dict(code=code, key=key, zh=zh, group=group, mat=mat, rings=rings, depth=round(depth, 1), ex=[round(e3[0], 1), round(-e3[1], 1)]))
    print(code, key, len(rings), sum(len(r) for r in rings))
allp = [p for q in parts for r in q["rings"] for p in r]
box = [min(p[0] for p in allp), min(p[1] for p in allp), max(p[0] for p in allp), max(p[1] for p in allp)]
# 画面取景：不算台板和线架（都很大，只露一部分），拆开前后都要装得下
pts = [(x + t * q["ex"][0], y + t * q["ex"][1]) for q in parts if q["key"] not in ("table", "stand", "spool") for r in q["rings"] for x, y in r for t in (0, 1)]
view_box = [min(p[0] for p in pts) - 10, min(p[1] for p in pts) - 10, max(p[0] for p in pts) + 10, max(p[1] for p in pts) + 30]
out = dict(view=[round(b, 1) for b in view_box], source="textbook/web-editions/sewing/models/proto_lockstitch.py", box=[round(b, 1) for b in box], parts=parts)
dest = HERE.parent / "data/explode.json"
dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
print("bytes", dest.stat().st_size, "box", out["box"])
