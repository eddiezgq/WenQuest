"""57.8 节：SH-101 的全套工艺文件——数字工厂的工艺文件生成器（hub/cards.py）由 std/SH-101_process.yaml 生成的过程卡、
工序卡（工序 30 精车、工序 50 铣键槽、工序 70 磨外圆）、检验卡和刀具卡（图 57.8.1–57.8.6）。卡片上的转速、机动时间都由切削用量算出；
同时核对生成前的完整性检查（cards.check）没有问题。"""
import _mfg as M
from bookout import out

P = M.plan101()
C = M.cards
assert C.check(P) == []
ops = C.machining_ops(P)
pages = 1 + len(ops) + 2
idx = {o["seq"]: i for i, o in enumerate(ops)}
M.card_figure(C.process_card(P, 1, pages), "fig57_8_1")
M.card_figure(C.op_card(P, M.op(P, 30), idx[30] + 2, pages), "fig57_8_2")
M.card_figure(C.op_card(P, M.op(P, 50), idx[50] + 2, pages), "fig57_8_3")
M.card_figure(C.op_card(P, M.op(P, 70), idx[70] + 2, pages), "fig57_8_4")
M.card_figure(C.inspection_card(P, pages - 1, pages), "fig57_8_5")
M.card_figure(C.tool_card(P, pages, pages), "fig57_8_6")
v30 = [C.step_values(s) for s in M.op(P, 30)["steps"]]
out(n_ops=len(P["operations"]), n_mach=len(ops), n_pages=pages, n_chars=len(P["characteristics"]), n_tools=len(P["tool_list"]),
    n_gauges=len(P["gauges"]), n30_lo=v30[0]["n"][0], n30_hi=v30[0]["n"][1], tb30=sum(x["tb"] for x in v30),
    n_steps=sum(len(o.get("steps") or []) for o in P["operations"]))
