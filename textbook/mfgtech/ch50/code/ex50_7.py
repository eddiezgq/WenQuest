"""50.7 节：刀具卡片与量检具清单（图 50.7.1）。"""
import _mfg as M
from bookout import out

p = M.plan()
ops = M.cards.machining_ops(p)
pages = 1 + len(ops) + 3
M.card_figure(M.cards.tool_card(p, pages, pages), "fig50_7_1")
out(n_tools=len(p["tool_list"]), n_gauges=len(p["gauges"]))
