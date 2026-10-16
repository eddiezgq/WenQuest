"""动画与信息密度检查（每日科普交付前必跑）：density.py <课目录> [--min 3x]
先跑 wb.py <课目录>（生成 data.json），再跑本脚本；不达标退出码 1。

两条标准（Eddie 2026-10-16）：
1. 动画（13:26“动画要多，要是现在的三倍以上”）：数的是“东西在动”——角色、物体、箭头、曲线、液面的动作（shift、rotate、
   grow、spin、wiggle、bob、pulse、flow、signal）和图形（非文字）的蹦出；文字蹦出单独列出，不算动画。
   基准：《会飞的特斯拉》快节奏版每分钟 30 个 → 要求每分钟 ≥ 90 个。
2. 信息（14:47 参考《物理学导论》，14:50 定“知识图”做法）：画面上每分钟要新出现 ≥ 20 样东西（字、图标、图形各算一样，
   同一个编号算一样），且每张知识图（停留 ≥ 20 秒的画板）上至少 6 处标注。不再要求每分钟换多少张画板。"""
import json
import sys
from pathlib import Path

BASE_MOVES = 30.0                              # 特斯拉快节奏版，每分钟物体动作
d = Path(sys.argv[1])
x = float(sys.argv[sys.argv.index("--min") + 1].rstrip("x")) if "--min" in sys.argv else 3.0
data = json.loads((d / "data.json").read_text())
lesson = json.loads((d / "lesson.json").read_text())
etype = {}
for b in lesson["boards"]:
    for e in b["elements"]:
        if e.get("id") is not None:
            etype.setdefault(str(e["id"]), set()).add(e.get("t"))
texts = {i for i, ts in etype.items() if ts <= {"text"}}
mins = data["total"] / 60
obj = txt_pops = 0
for m in data["moves"]:
    if m["kind"] == "pop" and all(t in texts for t in m["targets"]):
        txt_pops += 1
    else:
        obj += 1
things = 0                                     # 新出现的东西：有编号的按编号算一样，没编号的每个元素算一样
for b in lesson["boards"]:
    seen = set()
    for e in b["elements"]:
        if e.get("t") == "move":
            continue
        k = e.get("id")
        if k is None or k not in seen:
            things += 1
        if k is not None:
            seen.add(k)
segs = lesson["segments"]
maps = []
for b in lesson["boards"]:
    ats = [e["at"] for e in b["elements"]]
    stay = segs[max(ats)]["t1"] - segs[min(ats)]["t0"]
    if stay >= 20:
        maps.append(sum(1 for e in b["elements"] if e.get("t") in ("text", "box")))
per_min, things_min = obj / mins, things / mins
print(f"时长 {data['total']:.0f} 秒，画板 {len(data['boards'])} 张，其中知识图 {len(maps)} 张（标注数 {maps}）")
print(f"动画：物体动作 {obj} 个 = 每分钟 {per_min:.0f}（要求 ≥ {BASE_MOVES * x:.0f}）；文字蹦出 {txt_pops} 个不算")
print(f"信息：新出现的东西 {things} 样 = 每分钟 {things_min:.0f}（要求 ≥ 20）")
ok = per_min >= BASE_MOVES * x and things_min >= 20 and all(n >= 6 for n in maps)
print("达标" if ok else "不达标：加动作（每样新加的东西都动起来，持续动作贯穿整张），或往知识图上加要点")
sys.exit(0 if ok else 1)
