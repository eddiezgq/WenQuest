"""50.4 节：SH-301 的机械加工工艺过程卡片（图 50.4.1），由数字工厂的工艺数据生成；工时合计与 ERPNext 一致。"""
import _mfg as M
from bookout import out

p = M.plan()
ops = M.cards.machining_ops(p)
pages = 1 + len(ops) + 3
M.card_figure(M.cards.process_card(p, 1, pages), "fig50_4_1")
tot = sum(o["minutes"] for o in p["operations"])
setup = sum(o.get("setup_min", 0) for o in p["operations"])
batch = p["doc"]["batch"]
out(total=tot, setup=setup, batch=batch, per_piece_with_setup=tot + setup / batch, pages=pages, n_op_cards=len(ops),
    doc_no=p["doc"]["number"], rev=p["doc"]["revision"], drawing_no=p["doc"]["drawing_no"])
