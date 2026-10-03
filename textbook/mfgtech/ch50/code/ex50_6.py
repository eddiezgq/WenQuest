"""50.6 节：SH-301 的检验卡片（图 50.6.1 终检，图 50.6.2 工序检验）；统计图纸特性、关键特性和录入质量系统的项目。"""
import _mfg as M
from bookout import out

p = M.plan()
ops = M.cards.machining_ops(p)
pages = 1 + len(ops) + 3
html = M.cards.inspection_card(p, pages - 2, pages)
first, second = html.split("</section>", 1)
M.card_figure(first + "</section>", "fig50_6_1")
M.card_figure(second, "fig50_6_2")
chars = p["characteristics"]
fin = next(o for o in p["operations"] if o.get("final_inspection"))
qms = [i["char"] for i in fin["inspect"] if i.get("record") == "QMS"]
tmpl = [x["parameter"] for x in M.F.inspection_templates()["零件检验-输出轴"]]
inproc = sum(len(o.get("inspect") or []) for o in p["operations"] if not o.get("final_inspection"))
every = [i["char"] for i in fin["inspect"] if i.get("freq") == "每件"]
out(n_chars=len(chars), n_key=sum(1 for c in chars if c.get("key")), n_qms=len(qms), n_tmpl=len(tmpl), n_inproc=inproc,
    n_every=len(every), keys="、".join(c["id"] for c in chars if c.get("key")))
