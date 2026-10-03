"""50.2 节：SH-301 工艺过程的组成——每道工序有几次安装、几个工步、几次走刀（由工艺规程的工步数据数出来）。"""
import _mfg as M
from bookout import out

p = M.plan()
rows = []
for o in p["operations"]:
    st = o.get("steps") or []
    rows.append((o["seq"], o["operation"].split(" ")[0], M.setups(o) if st else None, len(st) or None, M.passes(o) or None))
r = M.op(p, 20)
out(table=rows, n_steps=sum(x[3] or 0 for x in rows), n_setups=sum(x[2] or 0 for x in rows),
    rough_setups=M.setups(r), rough_steps=len(r["steps"]), rough_passes=M.passes(r),
    fin_setups=M.setups(M.op(p, 40)), grind_setups=M.setups(M.op(p, 60)),
    rough_turn_passes=sum(len(s.get("passes_detail") or []) for s in r["steps"] if s.get("op") == "turn"),
    rough_ap=r["steps"][2]["passes_detail"][0][1], rough_stock=(50 - 41.5) / 2,
    fin_steps=len(M.op(p, 40)["steps"]), fin_passes=M.passes(M.op(p, 40)), key_steps=len(M.op(p, 50)["steps"]),
    key_passes=M.passes(M.op(p, 50)), grind_steps=len(M.op(p, 60)["steps"]),
    N_year=1000 * 1 * (1 + 0.05) * (1 + 0.01),
    fin2_passes=len(M.op(p, 40)["steps"][1]["passes_detail"]))
