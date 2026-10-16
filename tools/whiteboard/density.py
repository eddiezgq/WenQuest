"""动画密度检查（每日科普交付前必跑）：density.py <课目录> [--min 3x]
数的是“东西在动”——角色、物体、箭头、曲线、液面的动作（shift、rotate、grow、spin、wiggle、bob、pulse、flow、signal），
以及图形（非文字）的蹦出；文字蹦出单独列出，不算动画。基准：《会飞的特斯拉》快节奏版（2026-10-16）每分钟 30 个物体动作、
每分钟 10.7 张画板。Eddie 2026-10-16 13:26 定：每日科普的动画至少是它的 3 倍 → 每分钟 ≥ 90 个物体动作，画板每分钟 ≥ 16 张（1.5 倍，再多就看不清）。
先跑 wb.py <课目录>（生成 data.json），再跑本脚本；不达标退出码 1。"""
import json
import sys
from pathlib import Path

BASE_MOVES, BASE_BOARDS = 30.0, 10.7          # 特斯拉快节奏版，每分钟
d = Path(sys.argv[1])
x = float(sys.argv[sys.argv.index("--min") + 1].rstrip("x")) if "--min" in sys.argv else 3.0
data = json.loads((d / "data.json").read_text())
kinds = {}
for it in data["items"]:
    if it.get("eid"):
        kinds.setdefault(it["eid"], set()).add(it["k"])
texts = {e for e, ks in kinds.items() if ks == {"path"}}       # 文字画成字形轮廓（k = path），图形是 rough
mins = data["total"] / 60
obj, txt_pops = 0, 0
for m in data["moves"]:
    if m["kind"] == "pop" and all(t in texts for t in m["targets"]):
        txt_pops += 1
    else:
        obj += 1
per_min, boards = obj / mins, len(data["boards"]) / mins
print(f"时长 {data['total']:.0f} 秒；物体动作 {obj} 个 = 每分钟 {per_min:.0f}（要求 ≥ {BASE_MOVES * x:.0f}）；"
      f"画板 {len(data['boards'])} 张 = 每分钟 {boards:.1f}（要求 ≥ {BASE_BOARDS * x / 2:.0f}）；文字蹦出 {txt_pops} 个（不算动画）")
ok = per_min >= BASE_MOVES * x and boards >= BASE_BOARDS * x / 2
print("达标" if ok else "不达标：加动作（每张画板至少 3 样东西在动，持续动作贯穿整张），或把画板拆细")
sys.exit(0 if ok else 1)
